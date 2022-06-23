from io import BytesIO

from PIL import Image


def to_jpeg(image_bytes):
    img_io = BytesIO(image_bytes)
    out_io = BytesIO()
    img = Image.open(img_io).convert("RGB")
    img.save(out_io, format="jpeg", quality=95, optimize=True)

    return out_io.getvalue()
