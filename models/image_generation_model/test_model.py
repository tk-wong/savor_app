import glob
import torch
from torchmetrics.functional.multimodal import clip_score
from functools import partial
from PIL import Image
import numpy as np
import os
from tqdm import tqdm
from transformers import CLIPModel, CLIPProcessor
from diffusers import StableDiffusionPipeline
from dotenv import load_dotenv


def load_captions(caption_paths):
    captions = []
    for caption_path in caption_paths:
        with open(caption_path, "r") as f:
            caption = f.read().strip()
            captions.append(caption)
    return captions


def main():
    load_dotenv()
    clip_model_name = "openai/clip-vit-base-patch16"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLIPModel.from_pretrained(clip_model_name).to(device)
    processor = CLIPProcessor.from_pretrained(clip_model_name)
    model.eval()

    original_pipe = StableDiffusionPipeline.from_pretrained(
        "stable-diffusion-v1-5/stable-diffusion-v1-5",
        torch_dtype=torch.float16,  # or bfloat16 if your GPU supports it
        variant="fp16",  # if using fp16 variant
        safety_checker=None,
        requires_safety_checker=False,
        use_fast=True
    )
    original_pipe.to(device)
    original_pipe.enable_attention_slicing()
    original_pipe.set_progress_bar_config(disable=True)
    lora_pipe = StableDiffusionPipeline.from_pretrained(
        "stable-diffusion-v1-5/stable-diffusion-v1-5",
        torch_dtype=torch.float16,  # or bfloat16 if your GPU supports it
        variant="fp16",  # if using fp16 variant
        safety_checker=None,
        requires_safety_checker=False,
        use_fast=True

    )
    lora_pipe.load_lora_weights("wongtk/savor-image-generation-model",
                                # or folder if multiple files
                                use_auth_token=os.getenv("HF_TOKEN"),
                                prefix=None,)
    # lora_pipe.fuse_lora(lora_scale=0.7)  # Adjust scale 0.6-1.0 based on strength needed
    lora_pipe.to(device)
    lora_pipe.enable_attention_slicing()
    lora_pipe.set_progress_bar_config(disable=True)
    generator = torch.Generator(device).manual_seed(42)

    validation_images_dir = "../dataset/testing/verified"
    image_path_list = sorted(glob.glob(os.path.join(
        validation_images_dir, "*.jpg"), recursive=True))
    caption_path_list = sorted(glob.glob(os.path.join(
        validation_images_dir, "*.txt"), recursive=True))

    image_list = [Image.open(image_path).convert("RGB")
                  for image_path in image_path_list]

    captions = load_captions(caption_path_list)
    image_caption_pairs = list(zip(image_list, captions))
    print(f"{image_caption_pairs[0]=}")


    original_text_score_list = np.zeros(shape=(len(image_caption_pairs),))
    original_image_score_list = np.zeros(shape=(len(image_caption_pairs),))
    lora_text_score_list = np.zeros(shape=(len(image_caption_pairs),))
    lora_image_score_list = np.zeros(shape=(len(image_caption_pairs),))
    for i, (image, caption) in enumerate(tqdm(image_caption_pairs)):
        # Generate with original model
        with torch.no_grad():
            original_output = original_pipe(
                caption,
                num_inference_steps=30,
                guidance_scale=7.5,
                generator=generator,
            ).images[0]
        # Compute CLIP scores
        current_text_score, current_image_score = calculate_clip_similarity(device, model, processor, caption, original_output, image)
        original_text_score_list[i] = current_text_score
        original_image_score_list[i] = current_image_score
    # for image, caption in tqdm(image_caption_pairs):
        # Generate with original model

    # Generate with LoRA model
        with torch.no_grad():
            lora_output = lora_pipe(
                caption,
                num_inference_steps=30,
                guidance_scale=7.5,
                generator=generator,
            ).images[0]

        # Compute CLIP scores
        current_text_score, current_image_score = calculate_clip_similarity(device, model, processor, caption, lora_output, image)
        lora_text_score_list[i] = current_text_score
        lora_image_score_list[i] = current_image_score
    print(
    f"Original CLIP Score: {original_text_score_list.mean():.4f} ± {original_text_score_list.std():.4f}")
    print(f"Original Image CLIP Score: {original_image_score_list.mean():.4f} ± {original_image_score_list.std():.4f}")
    print(f"Original Hybrid CLIP Score: {hybrid_score(original_text_score_list, original_image_score_list).mean():.4f} ± {hybrid_score(original_text_score_list, original_image_score_list).std():.4f}")
    print("--------------------------------")
    print(f"LoRA CLIP Score: {lora_text_score_list.mean():.4f} ± {lora_text_score_list.std():.4f}")
    print(f"LoRA Image CLIP Score: {lora_image_score_list.mean():.4f} ± {lora_image_score_list.std():.4f}")
    print(f"LoRA Hybrid CLIP Score: {hybrid_score(lora_text_score_list, lora_image_score_list).mean():.4f} ± {hybrid_score(lora_text_score_list, lora_image_score_list).std():.4f}")
def calculate_clip_similarity(device, model, processor, caption, generated_image , original_image):
    original_input = processor(
            text=[caption], images=[generated_image,original_image], return_tensors="pt",
            padding=True
            ).to(device)
    with torch.no_grad():
        model_output = model(**original_input)
        generated_image_embeds = model_output.image_embeds[0:1]
        original_image_embeds = model_output.image_embeds[1:2]
        text_embeds = model_output.text_embeds
        text_score = max(0, torch.nn.functional.cosine_similarity(
                generated_image_embeds, text_embeds).item())*100.0
        image_score = max(0, torch.nn.functional.cosine_similarity(
                generated_image_embeds, original_image_embeds).item())*100.0
            
    return text_score,image_score

def hybrid_score(text_score, image_score, alpha=0.5):
    return alpha * image_score + (1 - alpha) * text_score

if __name__ == "__main__":
    main()
