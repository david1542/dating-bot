import os
import numpy as np
import pandas as pd
import tensorflow as tf

from PIL import Image
from bs4 import BeautifulSoup

from constants import DATASET_PATH
from src.utils.augs import augmentor

IMAGE_SIZE = (256, 256, 3)
IMAGE_WIDTH = IMAGE_SIZE[0]
IMAGE_HEIGHT = IMAGE_SIZE[1]
BATCH_SIZE = 32

def xml_to_dataframe(xml: BeautifulSoup):
    labels = xml.find_all('image')
    dataset = {}

    for label in labels:
        image_name = label.get('name')
        image_label = label.find('tag').get('label') == 'True'

        dataset[image_name] = image_label
    
    df = pd.DataFrame(dataset, index=['label']).T
    df = df.reset_index().rename(columns={'index': 'file_name'})
    return df

def load_metadata():
    annotations_path = os.path.join(DATASET_PATH, 'annotations.xml')
    images_path = os.path.join(DATASET_PATH, 'images')

    with open(annotations_path, 'rb') as f:
        annotations = BeautifulSoup(f.read(), 'xml')

    df = xml_to_dataframe(annotations)
    df['file_path'] = images_path + '/' + df['file_name']

    return df

def split_metadata(df: pd.DataFrame, train_frac: float = 0.7, valid_frac: float = 0.15, random_state=42):
    people_ids = df['file_name'].str.split('_').str[0].unique()
    people_ids = pd.Series(people_ids).sample(frac=1., random_state=random_state)

    train_amount = int(train_frac * len(people_ids))
    valid_amount = int(valid_frac * len(people_ids))

    people_ids_train = people_ids[:train_amount]
    people_ids_valid = people_ids[train_amount:train_amount + valid_amount]
    people_ids_test = people_ids[train_amount + valid_amount:]

    train_images = df[df['file_name'].str.split('_').str[0].isin(people_ids_train)]
    valid_images = df[df['file_name'].str.split('_').str[0].isin(people_ids_valid)]
    test_images = df[df['file_name'].str.split('_').str[0].isin(people_ids_test)]

    return train_images, valid_images, test_images

def load_image(image_path, label):
    image = tf.io.decode_image(tf.io.read_file(image_path), expand_animations=False)
    return image, label

def resize_image(image, label):
    image_resized = tf.image.resize(image, [IMAGE_WIDTH, IMAGE_HEIGHT], method='nearest')
    return image_resized, label

def cast_float32(image, label):
    image = tf.cast(image, dtype=tf.float32)
    image = image * (1. / 255)
    return image, label

def augment_image(image, label):
    image_aug = tf.numpy_function(
        func=augmentor, inp=(image,), Tout=tf.float32)
    return image_aug, label

def set_shapes(image, label):
    image.set_shape(IMAGE_SIZE)
    return image, label

def create_dataset(df: pd.DataFrame, batch_size: int = BATCH_SIZE):
    image_paths, labels = df['file_path'].values, df['label'].values
    image_paths = tf.convert_to_tensor(image_paths, dtype=tf.string)
    labels = tf.convert_to_tensor(labels)

    dataset = tf.data.Dataset.from_tensor_slices((image_paths, labels))
    dataset = dataset.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
    dataset = dataset.map(resize_image, num_parallel_calls=tf.data.AUTOTUNE)
    dataset = dataset.map(augment_image, num_parallel_calls=tf.data.AUTOTUNE)
    dataset = dataset.map(set_shapes, num_parallel_calls=tf.data.AUTOTUNE)

    dataset = dataset.batch(min(batch_size, len(image_paths)))
    return dataset