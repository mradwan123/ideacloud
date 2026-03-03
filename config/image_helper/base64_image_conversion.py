import base64
import uuid
from django.core.files.base import ContentFile
from io import BytesIO

def base64_to_image(b64: bytes):

    # # Default to jpg
    # format = 'jpg'

    # Decode
    decoded = base64.b64decode(b64)

    # # Generate unique filename
    # filename = f"image_{uuid.uuid4().hex[:10]}.{format}"

    # return ContentFile(decoded, name=filename)

    return BytesIO(decoded)


def image_to_base64(file: bytes):
    """please only put only jpg files in here :)"""
    b64 = base64.b64encode(file)

    return b64
