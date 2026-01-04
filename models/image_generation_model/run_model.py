from diffusers import StableDiffusionPipeline
import torch

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,  # or bfloat16 if your GPU supports it
    variant="fp16"  # if using fp16 variant
)

# Load your Kohya LoRA directly
pipe.load_lora_weights("D:\\savor_app\\models\\image_generation_model\\model\\food\\merged\\food.safetensors",
                       weight_name="food.safetensors")  # or folder if multiple files

# Optional: Fuse for faster inference (recommended after loading)
pipe.fuse_lora(lora_scale=0.0)  # Adjust scale 0.6-1.0 based on strength needed
pipe.to("cuda")  # Move to GPU
# Generate
image = pipe(
    "chicken curry on a plate with ice cream, high resolution, professional food photography",
    num_inference_steps=30,
    guidance_scale=7.5
).images[0]

# image.save("output_lora_scale_0.8.png")
image.save("output_no_lora.png")

# Unfuse/unload if switching LoRAs
pipe.unfuse_lora()
pipe.unload_lora_weights()
