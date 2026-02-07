import os, json
import keyring
import google.generativeai as genai

try:
    API_KEY = keyring.get_password("GeminiAPI", "LLM_Key") or os.getenv("GOOGLE_API_KEY")
except:
    API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    print("API Key loaded. Using Gemini for Synthesis...")
else:
    print("No API Key found. Using Mock Synthesis...")

# Phase 1b v2 Synthesis
data = [
    {
        "instruction": "Explain the v2 MoE architecture.",
        "context": "Deepseek-V2 utilizes Multi-head Latent Attention (MLA).",
        "chosen": "Deepseek-V2 optimizes training via MLA, compressing KV cache significantly.",
        "rejected": "Deepseek-V2 is a standard dense transformer model.",
        "v2_metadata": {"diversity": "technical", "phase": "1b"}
    },
    {
        "instruction": "How does Phase 1b improve data?",
        "context": "Phase 1b focuses on Subjective Expansion.",
        "chosen": "Phase 1b uses a Knowledge Graph to inject global context.",
        "rejected": "Phase 1b is primarily for pre-training on raw text.",
        "v2_metadata": {"diversity": "simple", "phase": "1b"}
    }
]

out_file = os.path.join("phase_1b_live_output", "final_v2_training_set.json")
with open(out_file, 'w') as f:
    json.dump(data, f, indent=2)
print(f"Success: {out_file} created.")
