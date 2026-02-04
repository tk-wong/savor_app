from diffusers import StableDiffusionPipeline
import torch
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env file

pipe = StableDiffusionPipeline.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5",
    torch_dtype=torch.float16,  # or bfloat16 if your GPU supports it
    variant="fp16",  # if using fp16 variant
)

# Load your Kohya LoRA directly
pipe.load_lora_weights("wongtk/savor-image-generation-model",use_auth_token=os.getenv("HF_TOKEN"),seed=42,)  # or folder if multiple files

# Optional: Fuse for faster inference (recommended after loading)
pipe.fuse_lora(lora_scale=0.7)  # Adjust scale 0.6-1.0 based on strength needed
pipe.to("cuda")  # Move to GPU
# Generate
image = pipe(
    "chicken curry on a plate with ice cream, high resolution, professional food photography, vibrant colors, detailed, sharp focus",
    num_inference_steps=30,
    guidance_scale=7.5,
).images[0]

# image.save("output_lora_scale_0.8.png")
image.save("output_lora_scale_0.7.png")

# Unfuse/unload if switching LoRAs
pipe.unfuse_lora()
pipe.unload_lora_weights()
