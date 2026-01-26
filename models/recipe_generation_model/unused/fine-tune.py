from unsloth import FastModel, FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig
from transformers import TextStreamer


def fine_tune_model():
    model, tokenizer = FastModel.from_pretrained(
        model_name="unsloth/Qwen3-4B-unsloth-bnb-4bit",
        max_seq_length=2048,  # Choose any for long context!
        load_in_4bit=True,  # 4 bit quantization to reduce memory
        load_in_8bit=False,  # [NEW!] A bit more accurate, uses 2x memory
        full_finetuning=False,  # [NEW!] We have full finetuning now!
        # token = "hf_...", # use one if using gated models
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=32,  # Choose any number > 0! Suggested 8, 16, 32, 64, 128
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj", ],
        lora_alpha=32,  # Best to choose alpha = rank or rank*2
        lora_dropout=0,  # Supports any, but = 0 is optimized
        bias="none",  # Supports any, but = "none" is optimized
        # [NEW] "unsloth" uses 30% less VRAM, fits 2x larger batch sizes!
        use_gradient_checkpointing="unsloth",  # True or "unsloth" for very long context
        random_state=3407,
        use_rslora=False,  # We support rank stabilized LoRA
        loftq_config=None,  # And LoftQ
    )
    data = load_dataset("json", data_files="sample_recipes.jsonl", split="train")
    print(data)
    conversions = data.map(lambda x: {"messages": tokenizer.apply_chat_template(x["messages"], tokenize=False)})
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=conversions,
        eval_dataset=None,
        args=SFTConfig(
            dataset_text_field="messages",
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,  # Use GA to mimic batch size!
            warmup_steps=5,
            num_train_epochs=1,  # Set this for 1 full training run.
            # max_steps = None,
            learning_rate=2e-4,  # Reduce to 2e-5 for long training runs
            logging_steps=1,
            optim="adamw_8bit",
            weight_decay=0.001,
            lr_scheduler_type="linear",
            seed=3407,
            report_to="none",  # Use TrackIO/WandB etc
        ),
    )
    trainer_stat = trainer.train()
    print("Training completed:", trainer_stat)
    with open("../trainer_stat.txt", "w") as f:
        f.write(str(trainer_stat))
    messages = [
        {"role": "user",
         "content": "You are a professional chef and trying to teach a beginner to cook. "
                    "Please create a recipe using eggs, milk, and flour"},
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=1024,
        temperature=0.7,
        top_p=0.8,
        top_k=40,
        streamer=TextStreamer(tokenizer, skip_prompt=True),
    )
    model.save_pretrained("qwen3-4b-finetuned-recipes")
    tokenizer.save_pretrained("qwen3-4b-finetuned-recipes")


if __name__ == '__main__':
    fine_tune_model()
