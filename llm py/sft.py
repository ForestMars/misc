# sft.py - Basic Supervised Fine Tuning script
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset

# Load model and tokenizer
model_name = "distilgpt2"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token  # Set padding token

# Load dataset
dataset = load_dataset("json", data_files="data.jsonl")

# Preprocess dataset: Combine prompt and output for training
def preprocess_function(examples):
    inputs = [f"{prompt} ### {output}" for prompt, output in zip(examples["prompt"], examples["output"])]
    model_inputs = tokenizer(inputs, max_length=256, truncation=True, padding="max_length")
    model_inputs["labels"] = model_inputs["input_ids"].copy()  # Autoregressive training
    return model_inputs

tokenized_dataset = dataset.map(preprocess_function, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir="./finetuned_model",
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    save_steps=500,
    save_total_limit=2,
    logging_steps=100,
    learning_rate=2e-5,
    fp16=True,  # Mixed precision for efficiency
)

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
)

# Fine-tune the model
trainer.train()

# Save the model
model.save_pretrained("./finetuned_model")
tokenizer.save_pretrained("./finetuned_model")