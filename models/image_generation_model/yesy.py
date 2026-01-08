from safetensors.torch import load_file

state_dict = load_file(
    "D:\\savor_app\\models\\dataset\\testing\\APPLE PIE LORA\\model\\apple_pie.safetensors")
keys = list(state_dict.keys())
print("Sample keys:", keys[:10])  # Show first 10 keys
print("All keys contain 'lora':", all("lora" in k for k in keys))
print("Any alpha keys:", any("alpha" in k for k in keys))
