import os
def create_folder(folder_path, base_path):
    for _, subdirs, _ in os.walk(folder_path):
        for subdir in subdirs:
            
            full_path = os.path.join(base_path, f"100_{subdir.replace("_"," ")}")
            try:
                os.makedirs(full_path, exist_ok=True)
                print(f"Folder created: {full_path}")
            except Exception as e:
                print(f"Error creating folder {full_path}: {e}")

if __name__ == "__main__":
    create_folder('../dataset/archive/food-101/food-101/images_processed', '../dataset/testing/APPLE PIE LORA/image')