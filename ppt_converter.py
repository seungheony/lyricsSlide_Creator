# ppt_converter.py

import os
import sys
import subprocess
import tempfile
from utils import convert_ppt_to_pptx, set_slide_background_to_white
from image_processor import invert_image_colors

def convert_ppt_to_images(ppt_file, output_dir):
    # PPT 파일 이름
    ppt_name = os.path.splitext(os.path.basename(ppt_file))[0]

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

    # 3. 수정된 PPTX를 PDF로 변환
    if sys.platform.startswith('darwin'):
        libreoffice_path = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    elif sys.platform.startswith('win'):
        libreoffice_path = r'C:\Program Files\LibreOffice\program\soffice.exe'
    else:
        libreoffice_path = 'libreoffice'

    command = [
        libreoffice_path,
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', output_dir,
        modified_pptx_file
    ]

    try:
        subprocess.run(command, check=True)
        print(f"{modified_pptx_file}를 PDF로 변환 완료.")
    except subprocess.CalledProcessError as e:
        print(f"{modified_pptx_file}를 PDF로 변환 중 오류 발생: {e}")
        os.unlink(modified_pptx_file)
        sys.exit(1)

    # 4. PDF를 이미지로 변환
    from pdf2image import convert_from_path

    pdf_file = os.path.join(output_dir, os.path.splitext(os.path.basename(modified_pptx_file))[0] + '.pdf')

    image_paths = []  # 생성된 이미지 파일 경로를 저장

    try:
        images = convert_from_path(pdf_file, dpi=300)

        for idx, image in enumerate(images):
            image_filename = f"{ppt_name}_slide{idx + 1}.png"
            image_path = os.path.join(output_dir, image_filename)
            image.save(image_path, 'PNG')

            # 이미지 색상 반전
            invert_image_colors(image_path)

            image_paths.append(image_path)  # 이미지 경로 저장

        print("PDF를 이미지로 변환 및 색상 반전 완료.")
    except Exception as e:
        print(f"PDF를 이미지로 변환 중 오류 발생: {e}")
        os.unlink(modified_pptx_file)
        sys.exit(1)

    # 5. 중간 파일 삭제
    os.remove(pdf_file)
    os.unlink(modified_pptx_file)
    if ppt_file.lower().endswith('.ppt'):
        os.remove(pptx_file)

    return image_paths  # 이미지 경로 리스트 반환

def convert_ppt_files(ppt_files, output_dir):
    all_image_paths = []
    for ppt_file in ppt_files:
        print(f"\n파일 변환 시작: {ppt_file}")
        image_paths = convert_ppt_to_images(ppt_file, output_dir)
        all_image_paths.append((ppt_file, image_paths))
    return all_image_paths