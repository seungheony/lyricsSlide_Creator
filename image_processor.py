# image_processor.py

from PIL import Image, ImageOps

def invert_image_colors(image_path):
    with Image.open(image_path) as img:
        inverted_image = ImageOps.invert(img.convert('RGB'))
        inverted_image.save(image_path)
        print(f"이미지 색상을 반전시켰습니다: {image_path}")