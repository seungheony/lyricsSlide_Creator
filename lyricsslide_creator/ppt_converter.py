"""
PPT 파일을 이미지로 변환하는 모듈
"""

import os
import sys
import subprocess
import tempfile

# 상대 경로와 절대 경로 모두 지원하도록 임포트 처리
try:
    # 패키지로 설치된 경우
    from .utils import convert_ppt_to_pptx, set_slide_background_to_white, get_libreoffice_path
    from .image_processor import invert_image_colors
except (ImportError, ValueError):
    # 개발 중 직접 실행 시
    from lyricsslide_creator.utils import convert_ppt_to_pptx, set_slide_background_to_white, get_libreoffice_path
    from lyricsslide_creator.image_processor import invert_image_colors

def convert_ppt_to_images(ppt_file, output_dir):
    """PPT 파일을 이미지로 변환합니다."""
    # PPT 파일 이름 (한글 처리를 위해 수정)
    ppt_name = os.path.splitext(os.path.basename(ppt_file))[0]
    
    # 안전한 임시 파일명 생성 (한글 제거)
    safe_name = f"slide_{abs(hash(ppt_name)) % 10000}"  # 해시값으로 고유 ID 생성
    
    try:
        # 1. .ppt 파일을 .pptx로 변환 (필요한 경우)
        if ppt_file.lower().endswith('.ppt'):
            # .ppt를 .pptx로 변환하고 변환된 파일의 경로를 얻습니다.
            pptx_file = convert_ppt_to_pptx(ppt_file)
        else:
            pptx_file = ppt_file

        # 2. 슬라이드 배경을 흰색으로 변경하여 임시 파일에 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx') as tmp_pptx:
            modified_pptx_file = tmp_pptx.name

        set_slide_background_to_white(pptx_file, modified_pptx_file)
        
        # 3. 슬라이드를 PDF로 변환 (안전한 파일명 사용)
        pdf_file = os.path.join(tempfile.gettempdir(), f"{safe_name}_slides.pdf")
        
        libreoffice_path = get_libreoffice_path()
        if libreoffice_path is None:
            raise ValueError("LibreOffice가 설치되어 있지 않습니다.")
            
        # LibreOffice 실행 명령
        cmd = [
            libreoffice_path, 
            '--headless', 
            '--convert-to', 'pdf', 
            '--outdir', os.path.dirname(pdf_file),
            modified_pptx_file
        ]
        
        # 사용자 프롬프트 없이 실행
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # PDF 파일명 확인 (LibreOffice에서 생성한 실제 파일명)
        created_pdf = os.path.join(os.path.dirname(pdf_file), 
                                  os.path.splitext(os.path.basename(modified_pptx_file))[0] + ".pdf")
        
        if os.path.exists(created_pdf):
            pdf_file = created_pdf
        else:
            print(f"생성된 PDF 파일을 찾을 수 없습니다: {created_pdf}")
            return []

        # 4. PDF를 이미지로 변환
        try:
            from pdf2image import convert_from_path
            
            # PDF를 이미지로 변환
            images = convert_from_path(pdf_file, dpi=300)
            
            # 이미지 파일 경로 목록
            image_paths = []
            
            # 각 이미지 저장
            for i, image in enumerate(images):
                # 이미지 파일 저장 (원래 파일명 사용하되 한글 오류 방지)
                image_path = os.path.join(output_dir, f"{safe_name}_slide_{i+1}.png")
                image.save(image_path, "PNG")
                
                # 흑백 반전
                invert_image_colors(image_path)
                image_paths.append(image_path)
                
            return image_paths
            
        except Exception as e:
            print(f"PDF를 이미지로 변환하는 중 오류 발생: {e}")
            raise
    
    except Exception as e:
        print(f"파일 변환 중 오류 발생: {e}")
        return []
        
    finally:
        # 임시 파일 정리
        try:
            cleanup_temp_files(pdf_file, modified_pptx_file, ppt_file, pptx_file)
        except Exception as e:
            print(f"임시 파일 정리 중 오류: {e}")

def cleanup_temp_files(pdf_file, modified_pptx_file, ppt_file, pptx_file):
    """임시 파일들을 안전하게 삭제합니다."""
    try:
        # PDF 파일 삭제
        if os.path.exists(pdf_file):
            os.remove(pdf_file)
            
        # 수정된 PPTX 파일 삭제
        if os.path.exists(modified_pptx_file):
            os.remove(modified_pptx_file)
            
        # 변환된 PPTX 파일 삭제 (원본이 PPT인 경우)
        if ppt_file.lower().endswith('.ppt') and pptx_file != ppt_file and os.path.exists(pptx_file):
            os.remove(pptx_file)
    except Exception as e:
        print(f"임시 파일 정리 중 오류 발생: {e}")

def convert_ppt_files(ppt_files, output_dir):
    """여러 PPT 파일을 이미지로 변환합니다."""
    all_image_paths = []

    for i, ppt_file in enumerate(ppt_files, 1):
        ppt_name = os.path.basename(ppt_file)
        print(f"[{i}/{len(ppt_files)}] '{ppt_name}' 처리 중...")
        
        # PPT 파일을 이미지로 변환
        image_paths = convert_ppt_to_images(ppt_file, output_dir)
        
        if image_paths:
            print(f"  {len(image_paths)}개의 슬라이드를 이미지로 변환했습니다.")
            all_image_paths.append((ppt_name, image_paths))
        else:
            print(f"  '{ppt_name}' 파일 변환에 실패했습니다.")

    return all_image_paths