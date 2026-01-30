import os
import shutil
import numpy as np
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
import tqdm

# Load CLIP model (downloads on first run)
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")
model.to(device)


def compute_score(batch_images, positive_prompt, negative_prompt):
    '''
    compute food fit scores for a batch of images
    :param batch_images: list of PIL Images
    :param positive_prompt: list of positive prompts
    :param negative_prompt: list of negative prompts
    :return: numpy array of food fit scores
    '''
    # Prepare inputs
    inputs = processor(text=positive_prompt * len(batch_images) + negative_prompt * len(batch_images), images=batch_images,
                       return_tensors="pt", padding=True).to(device)
    output_scores = model(**inputs)
    logits_per_image = output_scores.logits_per_image
    # Compute food fit scores using softmax over positive prompts
    food_fit_scores = logits_per_image.softmax(dim=1)[:, :len(positive_prompt)].mean(dim=1).detach(
    ).cpu().numpy()  # Probability for the prompt
    return food_fit_scores


def compute_clarity_score(image):
    '''
    compute clarity score for a single image using Laplacian variance
    :param image: PIL Image
    :return: clarity score (float)
    '''
    # Convert to grayscale
    gray = np.array(image.convert("L"))
    # compute Laplacian variance (higher = sharper)
    laplacian = np.abs(np.gradient(gray.astype(float), axis=(0, 1)))
    variance = np.var(laplacian)
    # Normalize roughly to 0-1 scale (adjust based on your images)
    return variance


def process_images(food_name, image_dir, batch_size=16, top_k=20):
    '''
    process images in the given directory to find top K clearest food photos
    :param food_name: Name of the food to focus on (e.g., "pizza")
    :param image_dir: Directory containing images
    :param batch_size: Number of images to process in a batch (default 16)
    :param top_k: Number of top images to return based on combined score (default 20)
    :return: List of tuples (image_path, combined_score, food_score, clarity_score)
    '''
    image_paths = [os.path.join(image_dir, f) for f in os.listdir(
        image_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    scores = []

    for i in range(0, len(image_paths), batch_size):
        batch_paths = image_paths[i:i+batch_size]
        batch_images = [Image.open(path).convert("RGB")
                        for path in batch_paths]

        # Define food-related prompts, some
        positive_food_prompt = [f"a clear photo of a {food_name}", f"a delicious {food_name}", f"a close-up photo of a {food_name}",
                                f"a high-resolution image of a {food_name}", f"a photo of a pepperoni {food_name}"]
        negative_food_prompt = [f"a photo of not a {food_name}", f"a blurry photo of a {food_name}",
                                f"a photo of a name of {food_name} restaurant", f"a photo of a staff serving {food_name}",
                                f"a photo of a {food_name} packaging",
                                f"a photo of a {food_name} text"]
        # food scores
        food_score = compute_score(
            batch_images, positive_food_prompt, negative_food_prompt)

        # Clarity scores
        clarity_scores = np.array([compute_clarity_score(img)
                                  for img in batch_images])
        # Combined score (multiply to emphasize both)
        normalized_food_scores = (food_score - food_score.min()) / \
            (food_score.max() - food_score.min() + 1e-8)
        normalized_clarity_scores = (clarity_scores - clarity_scores.min()) / \
            (clarity_scores.max() - clarity_scores.min() + 1e-8)
        combined_scores = normalized_food_scores * normalized_clarity_scores
        # Store results
        for path, food_s, clarity_s, combined_s in zip(batch_paths, normalized_food_scores, normalized_clarity_scores, combined_scores):
            scores.append((path, combined_s, food_s, clarity_s))

    # Sort by combined score descending and pick top K
    scores.sort(key=lambda x: x[1], reverse=True)
    top_20 = scores[:top_k]

    # Output results
    # print(f"Top 20 clearest {food_name} photos:")
    # for rank, (path, combined, food, clarity) in enumerate(top_20, 1):
    #     print(
    #         f"{rank}. {path} (Combined: {combined:.4f}, food Fit: {food:.4f}, Clarity: {clarity:.4f})")

    # Returns list of (path, combined_score, food_score, clarity_score)
    return top_20


def copy_top_images(top_images, dest_dir="./top_food_photos/", keep_dir_file=False):
    '''
    Copy top images to a destination directory
    :param top_images: List of tuples (image_path, combined_score, food_score, clarity_score)
    :param dest_dir: Destination directory to copy images
    '''
    if not keep_dir_file:
        shutil.rmtree(dest_dir, ignore_errors=True)
    os.makedirs(dest_dir, exist_ok=True)
    for path, _, _, _ in top_images:
        filename = os.path.basename(path)
        dest_path = os.path.join(dest_dir, filename)
        Image.open(path).save(dest_path)


if __name__ == "__main__":
    input_base_dir = os.path.normpath("../dataset/testing/processed_images")
    output_base_dir = os.path.normpath("../dataset/testing/verified")
    pbar = tqdm.tqdm(os.listdir(input_base_dir))
    for food_folder in pbar:
        food_image_dir = os.path.join(input_base_dir, food_folder)
        if os.path.isdir(food_image_dir):
            food_name = food_folder.replace("_", " ")
            pbar.set_description(f"Processing {food_name}")
            top_images = process_images(food_name, food_image_dir,batch_size=32,top_k=22)
            food_output_dir = os.path.join(output_base_dir, f"100_{food_name}")
            copy_top_images(top_images[20:], dest_dir=output_base_dir, keep_dir_file=True)
    # image_dir = "./pizza/"
    # top_20 = process_images("pizza",image_dir)
    # copy_top_images(top_20)
