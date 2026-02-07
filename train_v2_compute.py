import sys
from types import ModuleType
from unittest.mock import MagicMock

# 1. PEFT/Torch Distributed Patch for Windows
import torch
import torch.distributed
if not hasattr(torch.distributed, "tensor"):
    class MockTensorMod:
        DTensor = MagicMock()
    torch.distributed.tensor = MockTensorMod

# 2. FlashAttn Mocking for Windows
def mock_flash_attn():
    for name in ["flash_attn", "flash_attn.flash_attn_interface", "flash_attn.bert_padding"]:
        mod = ModuleType(name)
        mod.__spec__ = ModuleType("__spec__")
        sys.modules[name] = mod
mock_flash_attn()

import os, json
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import DPOTrainer, DPOConfig

MODEL_ID = "deepseek-ai/DeepSeek-V2-Lite-Chat"
DATA_PATH = "./phase_1b_live_output/final_v2_training_set.json"
OUTPUT_DIR = "./v2_compute_optimized_model"

def train():
    print("--- HP Z440 Optimized Pipeline (8GB VRAM Constraint) ---")
    
    # 1. Load Data
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    train_ds = Dataset.from_list(data).map(lambda x: {
        "prompt": f"User: {x['instruction']}<|end_of_turn|>Assistant:",
        "chosen": x["chosen"] + "<|end_of_turn|>",
        "rejected": x["rejected"] + "<|end_of_turn|>"
    })

    # 2. Aggressive 4-bit Config for 8GB VRAM
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        llm_int8_enable_fp32_cpu_offload=True
    )

    print("Loading Model Shards (Priority: GPU Compute)...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        trust_remote_code=True,
        device_map="auto",
        max_memory={0: "7.2GiB", "cpu": "24GiB"}, # Strict limit for 8GB card
        offload_folder="offload",
        attn_implementation="eager"
    )
    
    # 3. Enable Gradient Checkpointing (REQUIRED for 8GB)
    model.gradient_checkpointing_enable()
    model = prepare_model_for_kbit_training(model)
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token

    # 4. Minimal LoRA Rank to save compute/memory
    peft_config = LoraConfig(
        r=4, 
        lora_alpha=8,
        target_modules=["q_proj", "v_proj", "gate_proj"], 
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, peft_config)

    # 5. DPO Config optimized for 8GB throughput
    training_args = DPOConfig(
        output_dir=OUTPUT_DIR,
        max_steps=5,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=16, # High accumulation to saturate compute
        learning_rate=1e-5,
        fp16=True,
        optim="paged_adamw_32bit", # Use paged optimizer for offload stability
        beta=0.1,
        max_length=256,        # Keep sequences short for 8GB
        max_prompt_length=128,
        remove_unused_columns=False,
        report_to="none"
    )

    trainer = DPOTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        tokenizer=tokenizer,
        peft_config=peft_config,
    )

    print("\n=== INITIATING HP Z440 COMPUTE PASS ===")
    trainer.train()
    trainer.save_model(OUTPUT_DIR)
    print(f"Success! Final Model: {OUTPUT_DIR}")

if __name__ == "__main__":
    train()
