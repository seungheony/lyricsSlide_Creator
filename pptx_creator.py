# pptx_creator.py

import os
from pptx import Presentation
from pptx.util import Inches
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from utils import clear_directory

def delete_existing_presentation(presentation_path):
    if os.path.exists(presentation_path):
        os.remove(presentation_path)
        print(f"기존의 '{presentation_path}' 파일을 삭제하였습니다.")

def add_images_to_presentation(prs, image_paths):
    for image_path in image_paths:
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # 빈 슬라이드 레이아웃

        # 슬라이드 크기 가져오기
        slide_width = prs.slide_width
        slide_height = prs.slide_height

        # 이미지 위치 및 크기 계산
        shift_up = slide_height * 0.15  # 슬라이드 높이의 15%만큼 위로 이동
        image_height = slide_height * (1 + 0.15)  # 이미지 높이를 슬라이드 높이의 115%로 설정

        left = Inches(0)
        top = -shift_up  # 위로 이동시키기 위해 음수 값 사용

        # 이미지 추가
        pic = slide.shapes.add_picture(image_path, left, top, width=slide_width, height=image_height)
        print(f"이미지를 슬라이드에 추가하였습니다: {image_path}")

        # 슬라이드 하단 20%를 가리는 검은색 직사각형 추가
        rect_height = slide_height * 0.2
        rect_top = slide_height * 0.8  # 슬라이드 높이의 80% 위치

        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            left=Inches(0),
            top=rect_top,
            width=slide_width,
            height=rect_height
        )
        fill = shape.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(0, 0, 0)  # 검은색
        shape.line.color.rgb = RGBColor(0, 0, 0)  # 테두리 색상 제거
        print("하단 검은색 직사각형을 추가하였습니다.")

def add_black_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # 빈 슬라이드 레이아웃
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(0, 0, 0)  # 검은색
    print("검은색 배경 슬라이드를 추가하였습니다.")

def create_presentation(all_image_paths, output_pptx):
    # 새로운 프레젠테이션 생성
    prs = Presentation()
    prs.slide_width = Inches(13.33)  # 와이드스크린
    prs.slide_height = Inches(7.5)

    for idx, (ppt_file, image_paths) in enumerate(all_image_paths):
        add_images_to_presentation(prs, image_paths)
        if idx < len(all_image_paths) - 1:
            # 마지막 파일이 아닌 경우에만 검은색 슬라이드 추가
            add_black_slide(prs)

    # 새로운 PPT 파일 저장
    prs.save(output_pptx)
    print(f"\n모든 슬라이드가 '{output_pptx}' 파일에 저장되었습니다.")