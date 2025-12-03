#!/usr/bin/env python3
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import BitsAndBytesConfig
from datasets import Dataset
import os

print(f"GPU: {torch.cuda.is_available()}")
print(f"Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")

# Load TinyLlama
print("\nLoading TinyLlama...")
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto"
)

tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token

print("Model loaded!")

# Prepare LoRA
print("\nPreparing LoRA...")
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Load personality data
print("\nLoading training data...")
personality_data = []
if os.path.exists("ml_training/datasets/sisi_lola_personality.txt"):
    with open("ml_training/datasets/sisi_lola_personality.txt") as f:
        for line in f:
            if line.strip():
                personality_data.append({"text": line.strip()})

dataset = Dataset.from_list(personality_data)

def tokenize(example):
    return tokenizer(example["text"], truncation=True, max_length=256, padding="max_length")

dataset = dataset.map(tokenize, batched=False)

# Train
print(f"\nTraining on {len(dataset)} examples...")
training_args = TrainingArguments(
    output_dir="ml_training/checkpoints/sisi_lola_brain",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=5,
    save_steps=50,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer
)

print("\n🚀 Starting training...")
trainer.train()

print("\n💾 Saving model...")
model.save_pretrained("ml_training/checkpoints/sisi_lola_brain")
tokenizer.save_pretrained("ml_training/checkpoints/sisi_lola_brain")

print("\n✅ Training complete!")
