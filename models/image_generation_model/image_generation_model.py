import logging
import atexit
import torch
from diffusers import StableDiffusionPipeline


class ImageGenerationModel:
    def __init__(self,
                 model_name: str = "stable-diffusion-v1-5/stable-diffusion-v1-5",
                 device: str = "cuda" if torch.cuda.is_available() else "cpu",
                 torch_dtype=torch.float16,
                 variant="fp16",
                 lora_name: str = "wongtk/savor-image-generation-model",
                 lora_weight: float = 0.7,
                 hf_token: str = None,
                 # lazy_load: bool = True
                 ):
        self.model_name = model_name
        self.torch_dtype = torch_dtype
        self.variant = variant
        self.device = device
        self.lora_name = lora_name
        self.lora_weight = lora_weight
        self.hf_token = hf_token
        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,  # or bfloat16 if your GPU supports it
            variant=self.variant,  # if using fp16 variant
        )
        atexit.register(self.unload_model)
        self.pipe.load_lora_weights(self.lora_name, use_auth_token=hf_token, seed=42)
        self.pipe.fuse_lora(lora_scale=self.lora_weight)
        # if not self.lazy_load:
        self.pipe.enable_model_cpu_offload()
        # self.pipe.to(self.device)

    def generate_image(self, prompt: str, num_inference_steps: int = 30, guidance_scale: float = 7.5):
        # if self.lazy_load:
        #     self.pipe.to(self.device)
        image = self.pipe(
            prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
        ).images[0]
        # if self.lazy_load:
        #     self.pipe.to("cpu")
        return image

    def unload_model(self):
        # self.pipe.to("cpu")
        print("Shutting down server and unloading model...")
        self.pipe.unfuse_lora()
        self.pipe.unload_lora_weights()
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
