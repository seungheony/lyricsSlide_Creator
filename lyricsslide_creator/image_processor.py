# image_processor.py

from PIL import Image, ImageOps
import os

def invert_image_colors(image_path):
    """이미지의 색상을 반전시킵니다."""
    try:
        with Image.open(image_path) as img:
            # RGB 모드로 변환 (투명도가 있는 이미지도 처리)
            if img.mode == 'RGBA':
                # 알파 채널 분리
                r, g, b, a = img.split()
                rgb_img = Image.merge('RGB', (r, g, b))
                inverted_rgb = ImageOps.invert(rgb_img)
                
                # 알파 채널 다시 합치기
                r2, g2, b2 = inverted_rgb.split()
                inverted_image = Image.merge('RGBA', (r2, g2, b2, a))
            else:
                inverted_image = ImageOps.invert(img.convert('RGB'))
            
            inverted_image.save(image_path)
            print(f"이미지 색상을 반전시켰습니다: {image_path}")
    except Exception as e:
        print(f"이미지 색상 반전 중 오류 발생: {e}")
        return False
    return True

def resize_image(image_path, width=None, height=None, max_size=None):
    """이미지의 크기를 조정합니다."""
    try:
        with Image.open(image_path) as img:
            orig_width, orig_height = img.size
            
            # 최대 크기 제한이 있는 경우
            if max_size:
                if orig_width > max_size or orig_height > max_size:
                    ratio = min(max_size / orig_width, max_size / orig_height)
                    new_width = int(orig_width * ratio)
                    new_height = int(orig_height * ratio)
                    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                    resized_img.save(image_path)
                    print(f"이미지 크기를 조정했습니다: {image_path} ({new_width}x{new_height})")
                    return True
            
            # 특정 폭이나 높이로 조정하는 경우
            elif width or height:
                if width and height:
                    new_size = (width, height)
                elif width:
                    ratio = width / orig_width
                    new_size = (width, int(orig_height * ratio))
                else:  # height
                    ratio = height / orig_height
                    new_size = (int(orig_width * ratio), height)
                
                resized_img = img.resize(new_size, Image.LANCZOS)
                resized_img.save(image_path)
                print(f"이미지 크기를 조정했습니다: {image_path} ({new_size[0]}x{new_size[1]})")
                return True
                
    except Exception as e:
        print(f"이미지 크기 조정 중 오류 발생: {e}")
        return False
    
    return False  # 크기 조정이 필요 없거나 실패한 경우