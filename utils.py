# utils.py

import subprocess
import sys
import os
import tempfile
import shutil
from pptx import Presentation
from pptx.dml.color import RGBColor

def install_package(package_name):
    try:
        print(f"패키지 '{package_name}'를 설치합니다...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"패키지 '{package_name}' 설치 완료.")
    except subprocess.CalledProcessError:
        print(f"패키지 '{package_name}' 설치에 실패했습니다. 수동으로 설치해 주십시오.")

def clear_directory(directory):
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"파일 삭제 중 오류 발생: {e}")
    else:
        os.makedirs(directory)
    print(f"'{directory}' 폴더를 정리하였습니다.")

def convert_ppt_to_pptx(ppt_file):
    # LibreOffice 실행 파일 경로 설정
    if sys.platform.startswith('darwin'):
        libreoffice_path = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    elif sys.platform.startswith('win'):
        libreoffice_path = r'C:\Program Files\LibreOffice\program\soffice.exe'
    else:
        libreoffice_path = 'libreoffice'

    # 임시 디렉토리 생성
    with tempfile.TemporaryDirectory() as temp_dir:
        command = [
            libreoffice_path,
            '--headless',
            '--convert-to', 'pptx',
            '--outdir', temp_dir,
            ppt_file
        ]

        try:
            subprocess.run(command, check=True)
            print(f"{ppt_file}를 PPTX로 변환 완료.")
        except subprocess.CalledProcessError as e:
            print(f"{ppt_file}를 PPTX로 변환 중 오류 발생: {e}")
            sys.exit(1)

        # 변환된 .pptx 파일 찾기
        for file_name in os.listdir(temp_dir):
            if file_name.lower().endswith('.pptx'):
                converted_pptx_file = os.path.join(temp_dir, file_name)
                # 임시 디렉토리가 삭제되기 전에 파일을 복사합니다.
                temp_pptx_file = os.path.join(tempfile.gettempdir(), file_name)
                shutil.copy(converted_pptx_file, temp_pptx_file)
                return temp_pptx_file

        # 변환된 파일을 찾지 못한 경우 오류 처리
        print(f"{ppt_file}를 PPTX로 변환하는데 실패하였습니다.")
        sys.exit(1)

def set_slide_background_to_white(pptx_file, modified_pptx_file):
    prs = Presentation(pptx_file)
    for slide in prs.slides:
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(255, 255, 255)  # 흰색
    prs.save(modified_pptx_file)
    print(f"슬라이드 배경을 흰색으로 변경하였습니다: {modified_pptx_file}")