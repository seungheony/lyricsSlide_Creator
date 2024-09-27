# main.py

import sys
import os
from dependency_checker import check_dependencies
from ppt_converter import convert_ppt_files
from pptx_creator import create_presentation, delete_existing_presentation
from utils import clear_directory

def main():
    # 종속성 검사
    if not check_dependencies():
        sys.exit(1)

    # 기존의 'merged_presentation.pptx' 파일 삭제
    delete_existing_presentation('merged_presentation.pptx')

    # 사용자로부터 디렉토리 경로 입력 받기
    directory = input("변환할 PPT 파일들이 있는 디렉토리의 경로를 입력하세요: ")
    if not os.path.isdir(directory):
        print("유효한 디렉토리 경로가 아닙니다.")
        sys.exit(1)

    # 이미지가 저장될 디렉토리 설정 및 정리
    output_dir = 'converted_images'
    clear_directory(output_dir)

    # PPT 파일을 이미지로 변환
    ppt_files = [os.path.join(directory, f) for f in os.listdir(directory)
                 if f.lower().endswith(('.ppt', '.pptx'))]

    if not ppt_files:
        print("지정된 디렉토리에 PPT 파일이 없습니다.")
        sys.exit(1)

    all_image_paths = convert_ppt_files(ppt_files, output_dir)

    # 새로운 프레젠테이션 생성 및 이미지 추가
    create_presentation(all_image_paths, 'merged_presentation.pptx')

if __name__ == "__main__":
    main()