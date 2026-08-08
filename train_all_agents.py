import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig

MODEL_ID = 'Qwen/Qwen2.5-0.5B-Instruct'

agents = [
    ('Planner', 'planner_data.jsonl', './fine_tuned_planner'),
    ('Decomposer', 'decomposer_data.jsonl', './fine_tuned_decomposer'),
    ('Evaluator', 'evaluator_data.jsonl', './fine_tuned_evaluator'),
]

for name, datafile, outdir in agents:
    print(f'=== Fine-tuning {name} Agent ===')
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float32,
        device_map='cpu',
        trust_remote_code=True,
    )

    peft_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'],
        lora_dropout=0.05,
        bias='none',
        task_type='CAUSAL_LM',
    )

    dataset = load_dataset('json', data_files=datafile, split='train')

    training_args = SFTConfig(
        output_dir=f'./local_{name.lower()}_model',
        num_train_epochs=2,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=2,
        learning_rate=2e-4,
        fp16=False,
        use_cpu=True,
        logging_steps=1,
        save_strategy='no',
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        args=training_args,
    )

    trainer.train()
    trainer.model.save_pretrained(outdir)
    tokenizer.save_pretrained(outdir)
    print(f'Successfully fine-tuned {name} Agent -> {outdir}\n')
