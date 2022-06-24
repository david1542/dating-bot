import os
import argparse
import shutil
from bs4 import BeautifulSoup

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, required=True, help='Path to dataset')
    parser.add_argument('--aligned', type=str, required=True, help='Path to aligned images')
    parser.add_argument('--output', type=str, required=True, help='Path to output folder')
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.mkdir(args.output)
        os.mkdir(os.path.join(args.output, 'images'))

    actual_images = os.listdir(args.aligned)

    with open(os.path.join(args.dataset, 'annotations.xml'), 'rb') as f:
        annotations = BeautifulSoup(f.read(), 'xml')

    labeled_images = annotations.find_all('image')
    images_to_ignore = []

    for image in labeled_images:
        image_file_name = image.get('name')

        if image_file_name not in actual_images:
            images_to_ignore.append(image_file_name)
            image.decompose()
    
    # Save annotations
    with open(os.path.join(args.output, 'annotations.xml'), 'w') as f_out:
        print(annotations, file=f_out)

    for file_name in os.listdir(os.path.join(args.dataset, 'images')):
        if file_name not in images_to_ignore:
            shutil.copy(os.path.join(args.dataset, 'images', file_name), os.path.join(args.output, 'images'))
