from PIL import Image
import os


def process_image(input_path, output_path):
    os.makedirs(output_path, exist_ok=True)
    for root, _, files in os.walk(input_path):
        file_num = len(files)
        file_processed = 0
        for file in files:
            if file.endswith(('.jpg', '.jpeg', '.png')):
                path_in_subfolder = os.path.join(os.path.split(root)[1], file)
                print(f"Processing {path_in_subfolder} ({file_processed}/{file_num})\r",end="")
                output_path_file = os.path.join(output_path, path_in_subfolder)
                os.makedirs(os.path.dirname(output_path_file), exist_ok=True)
                image = Image.open(os.path.join(root, file)).convert('RGB')
                image = image.resize((512,512))
                image.save(output_path_file)
                # shutil.copy(os.path.join(root, file), output_path_file)
            # Process the image here
            file_processed += 1
        
    print("\033[AProcessing complete.")


if __name__ == "__main__":
    process_image('/home/user/project/savor_app/models/dataset/archive/food-101/food-101/images', '../dataset/testing/processed_images')