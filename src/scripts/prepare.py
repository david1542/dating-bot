import os
import argparse
import shutil
import numpy as np
import cv2

from tqdm.auto import tqdm
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

def get_files_recursive(path):
    """
    Get all files in a directory and its subdirectories.
    """
    files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('jpeg') or file.endswith('png') or file.endswith('jpg'):
                files.append(os.path.join(root, file))
    return files

def flatten(folder: str, output: str):
    for root, dirs, files in os.walk(folder, topdown=False):
        for name in files:
            shutil.copy(os.path.join(root, name), output)

def mse(image_a, image_b):
    err = np.sum((image_a.astype("float") - image_b.astype("float")) ** 2)
    err /= float(image_a.shape[0] * image_a.shape[1])
    return err

def load_image_as_array(file_path):
    image = Image.open(file_path)
    image = np.array(image)
    return image

def load_images_matrix(path, image_files):
    N = len(image_files)
    width, height = 256, 256
    images = np.zeros((N, width * height * 3))
    for i, f in enumerate(image_files):
        arr = load_image_as_array(os.path.join(path, f))
        arr = cv2.resize(arr, (width, height))
        images[i] = arr.flatten()

    return images

def remove_duplicates(folder: str):
    image_files = os.listdir(folder)
    image_files = [file for file in image_files if file != '.DS_Store']
    
    images = load_images_matrix(folder, image_files)

    print('Starting to find duplicates')
    for i in tqdm(range(len(images))):
        image = images[i]

        err = np.sum((images - image) ** 2, axis=1)
        err /= float(image.shape[0])

        duplicates = np.where(err < 200)[0]
        duplicates = [j for j in duplicates if j != i]

        # Delete duplicate images
        for duplicate in duplicates:
            file_name = image_files[duplicate]
            file_path = os.path.join(folder, file_name)
            try:
                os.remove(file_path)
            except Exception as e:
                print(e)
                pass

if __name__ == '__main__':
    """
    This script takes a folder of scraped images (in categories) and prepares them.
    For example, this is the expected folder structure:
    - bumble/
      - 123.jpg
    - okcupid
      - 456.jpg
    - tinder
      - 789.png
    
    Afterwards, the script flattens the hierarchy and remove duplicate images by
    computing relative MSE between images.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', type=str, required=True, help='Path to scraped images')
    parser.add_argument('--output', type=str, required=True, help='Output path')
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.mkdir(args.output)

    # Flatten the hierarchy
    flatten(args.folder, args.output)

    # Remove duplicates
    remove_duplicates(args.output)
