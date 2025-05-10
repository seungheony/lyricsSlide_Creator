# image_processor.py

from PIL import Image, ImageOps
import os
import io

def invert_image_colors(image_path):
    """
    이미지 색상을 반전시키고 BytesIO 객체로 반환합니다.
    
    Args:
        image_path (str): 이미지 파일 경로
    
    Returns:
        BytesIO: 변환된 이미지가 포함된 BytesIO 객체
    """
    try:
        # 이미지 열기
        image = Image.open(image_path)
        
        # RGBA 이미지인 경우 RGB로 변환 (투명도가 있는 경우 처리)
        if image.mode == 'RGBA':
            # 흰색 배경으로 투명부분 채우기
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])  # 알파 채널을 마스크로 사용
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 색상 반전
        inverted_image = ImageOps.invert(image)
        
        # BytesIO 객체로 변환
        output = io.BytesIO()
        inverted_image.save(output, format='PNG')
        output.seek(0)  # 읽기 위치 초기화
        
        print(f"이미지 색상을 반전시켰습니다: {image_path}")
        return output
    except Exception as e:
        print(f"이미지 색상 반전 중 오류 발생: {e}")
        # 오류 발생 시 원본 이미지 반환
        try:
            with open(image_path, 'rb') as f:
                return io.BytesIO(f.read())
        except:
            return None

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