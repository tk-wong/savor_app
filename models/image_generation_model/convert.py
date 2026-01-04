import torch
from safetensors.torch import load_file, save_file

input_path = "D:\\savor_app\\models\\image_generation_model\\model\\food\\food.safetensors"   # Change this
output_path = "D:\\savor_app\\models\\image_generation_model\\model\\food\\merged\\food.safetensors"  # Change this

state_dict = load_file(input_path)

new_state_dict = {}
alpha_dict = {}  # To collect alphas if present

for key, value in state_dict.items():
    if "alpha" in key:
        # Collect alpha (usually a scalar tensor)
        module_key = key.replace(".alpha", "")
        alpha_dict[module_key] = value.item() if value.numel() == 1 else value
        continue
    
    if "lora_down" in key:
        new_key = key.replace("lora_down.weight", "lora_A.weight")
    elif "lora_up" in key:
        new_key = key.replace("lora_up.weight", "lora_B.weight")
    else:
        continue  # Skip non-LoRA keys if any
    
    # Prefix for Diffusers/PEFT format
    new_key = new_key.replace("lora_", "base_model.model.lora_")
    
    new_state_dict[new_key] = value

# If alphas exist, add them as needed (PEFT often uses a single alpha per module)
for module, alpha in alpha_dict.items():
    peft_key = module.replace("lora_", "base_model.model.lora_") + ".alpha"
    new_state_dict[peft_key] = torch.tensor(alpha)

save_file(new_state_dict, output_path)
print(f"Converted LoRA saved to {output_path}")
print(f"Converted {len(new_state_dict)} keys")