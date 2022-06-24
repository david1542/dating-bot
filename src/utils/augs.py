
import albumentations as A

transform = A.Compose([
    A.ShiftScaleRotate(shift_limit=0, rotate_limit=20, border_mode=1, p=1),
    A.HorizontalFlip(p=1)
])

def augmentor(image):
    aug_data = transform(image=image)
    aug_image = aug_data['image']
    return aug_image