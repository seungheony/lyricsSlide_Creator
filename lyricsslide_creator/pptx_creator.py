# pptx_creator.py

import os
import tempfile
import shutil
import sys
from pptx import Presentation
from pptx.util import Inches
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def delete_existing_presentation(presentation_path):
    """기존 프레젠테이션 파일이 있다면 삭제합니다."""
    if os.path.exists(presentation_path):
        try:
            os.remove(presentation_path)
            print(f"기존의 '{presentation_path}' 파일을 삭제하였습니다.")
        except PermissionError:
            # Windows에서 파일 잠금 처리
            if sys.platform.startswith('win'):
                print(f"'{presentation_path}' 파일이 사용 중입니다. 대체 파일명을 사용합니다.")
                # 대체 파일명 생성
                base_name, ext = os.path.splitext(presentation_path)
                new_path = f"{base_name}_new{ext}"
                return new_path  # 대체 파일명 반환
            else:
                print(f"'{presentation_path}' 파일이 사용 중이어서 삭제할 수 없습니다. 파일을 닫고 다시 시도하세요.")
                return False
        except Exception as e:
            print(f"파일 삭제 중 오류 발생: {e}")
            return False
    return True  # 기존 파일이 없거나 삭제 성공

def set_slide_background_black(slide):
    """슬라이드의 배경을 검은색으로 설정합니다."""
    try:
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(0, 0, 0)  # 검은색
    except Exception as e:
        print(f"슬라이드 배경 설정 중 오류 발생: {e}")

def add_images_to_presentation(prs, image_paths):
    """이미지를 프레젠테이션에 추가합니다."""
    for image_path in image_paths:
        if not os.path.isfile(image_path):
            print(f"이미지 파일을 찾을 수 없습니다: {image_path}")
            continue
        try:
            slide = prs.slides.add_slide(prs.slide_layouts[6])  # 빈 슬라이드 레이아웃
            
            # 슬라이드 배경을 검은색으로 설정
            set_slide_background_black(slide)

            # 슬라이드 크기 가져오기
            slide_width = prs.slide_width
            slide_height = prs.slide_height

            # 이미지 크기 계산 (슬라이드 크기의 80%)
            image_width = slide_width * 0.8
            image_height = slide_height * 0.8

            # 이미지 위치 계산 (가운데 정렬, 위로 18% 이동)
            left = (slide_width - image_width) / 2
            top = -slide_height * 0.13  # 위로 이동시키기 위해 음수 값 사용

            # 이미지 추가
            pic = slide.shapes.add_picture(image_path, left, top, width=image_width, height=image_height)

            # 슬라이드 하단 35%를 가리는 검은색 직사각형 추가
            rect_height = slide_height * 0.4
            rect_top = slide_height * 0.6  # 슬라이드 높이의 65% 위치

            shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                left=0,  # 슬라이드의 왼쪽 끝
                top=rect_top,
                width=slide_width,
                height=rect_height
            )
            fill = shape.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(0, 0, 0)  # 검은색
            shape.line.color.rgb = RGBColor(0, 0, 0)  # 테두리 색상 제거

        except Exception as e:
            print(f"이미지 추가 중 오류가 발생했습니다: {e}")
            continue

def add_black_slide(prs):
    """검은색 배경의 빈 슬라이드를 추가합니다."""
    try:
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # 빈 슬라이드 레이아웃
        set_slide_background_black(slide)
    except Exception as e:
        print(f"검은색 슬라이드 추가 중 오류 발생: {e}")

def create_presentation(all_image_paths, output_pptx):
    """이미지 파일들로 새 프레젠테이션을 생성합니다."""
    # 임시 파일 경로 생성
    temp_output = os.path.join(tempfile.gettempdir(), f"temp_{os.path.basename(output_pptx)}")
    
    try:
        # 새로운 프레젠테이션 생성
        prs = Presentation()
        prs.slide_width = Inches(13.33)  # 와이드스크린
        prs.slide_height = Inches(7.5)

        # 슬라이드 마스터 배경을 검은색으로 설정 (선택 사항)
        for slide_master in prs.slide_masters:
            try:
                background = slide_master.background
                fill = background.fill
                fill.solid()
                fill.fore_color.rgb = RGBColor(0, 0, 0)  # 검은색
            except Exception as e:
                print(f"슬라이드 마스터 배경 설정 중 오류: {e}")
                continue

        for idx, (ppt_file, image_paths) in enumerate(all_image_paths):
            print(f"프레젠테이션에 '{os.path.basename(ppt_file)}' 파일의 슬라이드 추가 중...")
            add_images_to_presentation(prs, image_paths)
            if idx < len(all_image_paths) - 1:
                # 마지막 파일이 아닌 경우에만 검은색 슬라이드 추가
                add_black_slide(prs)

        # 임시 파일로 저장 후 이동 (파일 충돌 방지)
        prs.save(temp_output)
        
        # 기존 파일이 있으면 대체
        if os.path.exists(output_pptx):
            try:
                os.remove(output_pptx)
            except Exception as e:
                print(f"기존 파일 삭제 중 오류: {e}")
                
        # 임시 파일을 최종 위치로 이동
        shutil.move(temp_output, output_pptx)
        
        print(f"\n모든 슬라이드가 '{output_pptx}' 파일에 저장되었습니다.")
        
    except Exception as e:
        print(f"프레젠테이션 생성 중 오류 발생: {e}")
        # 임시 파일 정리
        if os.path.exists(temp_output):
            try:
                os.remove(temp_output)
            except:
                pass
        return False
        
    return True