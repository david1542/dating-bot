
import tensorflow as tf
import albumentations as A

transform = A.Compose([
    A.ShiftScaleRotate(shift_limit=0, rotate_limit=20, border_mode=1),
    A.RandomBrightnessContrast(p=0.2),
    A.GaussianBlur(),
    A.HorizontalFlip(),
    A.Blur()
])

def augmentor(image):
    aug_data = transform(image=image)
    aug_image = aug_data['image']
    aug_image = tf.cast(aug_image / 255.0, tf.float32)
    return aug_image