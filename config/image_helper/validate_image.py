from io import BytesIO
from PIL import Image
from .base64_image_conversion import base64_to_image


def is_image_valid(image_data) -> bool:
    try:
        img = Image.open(BytesIO(image_data.read()), formats=['JPEG'])
        img.verify()
    except Exception:
        return False

    return True
