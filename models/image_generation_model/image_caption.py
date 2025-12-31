import glob
import os
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import tqdm
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
# Load BLIP processor and model
def generate_image_caption(path,prefix=""):
# Load an image
    image = Image.open(path).convert("RGB")

# Process the image
    inputs = processor(images=image, return_tensors="pt").to(device)

# Generate captions
    outputs = model.generate(**inputs)
    caption = processor.decode(outputs[0], skip_special_tokens=True)
    file_name = os.path.basename(path).split('.')[0]
    caption_file = os.path.join(os.path.dirname(path), f"{file_name}.txt")
    with open(caption_file, "w") as f:
        if prefix:
            f.write(f"{prefix}, {caption}")
        else:
            f.write(caption)
    return caption

def generate_caption_from_directory(image_dir):
    captions = {}
    image_path = glob.glob(os.path.join(image_dir, "**", "*.jpg"), recursive=True)
    # for filename in tqdm.tqdm(os.listdir(image_dir)):
    #     if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
    #         path = os.path.join(image_dir, filename)
    #         caption = generate_image_caption(path)
    #         captions[filename] = caption
    for path in tqdm.tqdm(image_path):
        filename = os.path.basename(path)
        food_name = os.path.basename(os.path.dirname(path)).split('_')[1]
        caption = generate_image_caption(path, prefix=food_name)
        captions[filename] = caption
    return captions

# print((glob.glob("/home/user/project/savor_app/models/dataset/testing/APPLE PIE LORA/image/**/*.jpg")))
# caption = generate_image_caption("pizza/2965.jpg")
# print("Generated Caption:", caption)

captions = generate_caption_from_directory("/home/user/project/savor_app/models/dataset/testing/APPLE PIE LORA/image")
