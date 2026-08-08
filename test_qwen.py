import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"


print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("GPU:", torch.cuda.get_device_name(0))


print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)


print("Loading model...")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)


print("\nModel loaded successfully")


prompt = "Explain what a neural network is in simple terms."

inputs = tokenizer(
    prompt,
    return_tensors="pt"
).to("cuda")


print("\nGenerating response...")


with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=100
    )


response = tokenizer.decode(
    outputs[0],
    skip_special_tokens=True
)


print("\nResponse:")
print(response)


print("\nGPU Memory Used:")
print(
    torch.cuda.memory_allocated()/1024**3,
    "GB"
)