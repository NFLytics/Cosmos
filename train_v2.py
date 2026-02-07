import sys
from types import ModuleType

def mock_flash_attn():
    for name in ["flash_attn", "flash_attn.flash_attn_interface", "flash_attn.bert_padding"]:
        mod = ModuleType(name)
        mod.__spec__ = ModuleType("__spec__")
        sys.modules[name] = mod

mock_flash_attn()

import os, json, torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import DPOTrainer, DPOConfig

MODEL_ID = "deepseek-ai/DeepSeek-V2-Lite-Chat" 
DATA_PATH = "./phase_1b_live_output/final_v2_training_set.json"
OUTPUT_DIR = "./v2_finetuned_model"

def train():
    print(f"--- Starting Training Pipeline ---")
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} missing.")
        return

    data = json.load(open(DATA_PATH, encoding='utf-8'))
    ds = Dataset.from_list(data)
    
    def dpo_format(example):
        return {
            "prompt": f"User: {example['instruction']}<|end_of_turn|>Assistant:",
            "chosen": example["chosen"] + "<|end_of_turn|>",
            "rejected": example["rejected"] + "<|end_of_turn|>"
        }
    
    train_ds = ds.map(dpo_format)
    
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        llm_int8_enable_fp32_cpu_offload=True
    )

    try:
        print(f"Loading Model: {MODEL_ID}...")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID, 
            quantization_config=bnb_config, 
            trust_remote_code=True, 
            device_map="auto",
            offload_folder="offload",
            attn_implementation="eager"
        )
        model = prepare_model_for_kbit_training(model)

        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
        tokenizer.pad_token = tokenizer.eos_token
        
        peft_config = LoraConfig(
            r=8, 
            lora_alpha=16, 
            target_modules=["q_proj", "v_proj", "gate_proj", "up_proj", "down_proj"], 
            task_type="CAUSAL_LM"
        )
        
        # Use DPOConfig instead of TrainingArguments
        args = DPOConfig(
            output_dir=OUTPUT_DIR,
            max_steps=10, 
            per_device_train_batch_size=1,
            gradient_accumulation_steps=4,
            learning_rate=1e-4,
            fp16=True,
            logging_steps=1,
            report_to="none",
            optim="paged_adamw_32bit",
            remove_unused_columns=False,
            beta=0.1,
            max_length=512,
            max_prompt_length=256
        )
        
        trainer = DPOTrainer(
            model=model,
            train_dataset=train_ds,
            tokenizer=tokenizer,
            peft_config=peft_config,
            args=args
        )
        
        print("Executing DPO Training...")
        trainer.train()
        trainer.save_model(OUTPUT_DIR)
        print(f"Success! Model saved to {OUTPUT_DIR}")

    except Exception as e:
        print(f"Training Error: {e}")

if __name__ == "__main__":
    train()
