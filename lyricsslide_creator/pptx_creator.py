# pptx_creator.py

import os
import tempfile
import shutil
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from io import BytesIO

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

def add_images_to_presentation(presentation, images_path, invert_colors=False):
    """
    이미지들을 프레젠테이션에 추가합니다.
    
    Args:
        presentation: 이미지를 추가할 pptx Presentation 객체
        images_path: 이미지들이 있는 폴더 경로
        invert_colors: 색상을 반전할지 여부
    """
    from lyricsslide_creator.image_processor import invert_image_colors
    from PIL import Image
    import io
    from pptx.util import Inches
    from pptx.dml.color import RGBColor
    
    # 이미지 파일 목록 가져오기
    image_files = []
    for file in sorted(os.listdir(images_path)):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_files.append(os.path.join(images_path, file))
    
    # 이미지 순서대로 슬라이드에 추가
    for image_file in image_files:
        # 슬라이드 추가
        slide = presentation.slides.add_slide(presentation.slide_layouts[6])
        
        # 슬라이드 배경을 검은색으로 설정
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(0, 0, 0)
        
        # 슬라이드 크기 가져오기
        slide_width = presentation.slide_width
        slide_height = presentation.slide_height
        
        # 이미지 색상 반전 처리
        if invert_colors:
            # 원본 이미지의 가로/세로 비율을 유지하기 위해 이미지 크기 정보 가져오기
            try:
                with Image.open(image_file) as img:
                    img_width, img_height = img.size
                    aspect_ratio = img_width / img_height
            except Exception as e:
                print(f"이미지 크기 정보 읽기 실패: {e}")
                aspect_ratio = slide_width / slide_height  # 기본값: 슬라이드 비율 사용
            
            # 이미지 반전 처리
            image_data = invert_image_colors(image_file)
            if image_data is None:
                # 반전 실패 시 원본 이미지 사용
                print(f"이미지 반전 실패, 원본 사용: {image_file}")
                image_data = image_file
            
            # 이미지 위치를 20% 위로 이동
            top_position = -slide_height * 0.16
            
            # 슬라이드 너비에 맞춰 크기 계산하되, 가로/세로 비율 유지
            image_width = slide_width
            image_height = image_width / aspect_ratio
            
            # 이미지가 슬라이드 높이보다 작다면 높이에 맞춤
            if image_height < slide_height:
                image_height = slide_height
                image_width = image_height * aspect_ratio
            
            # 이미지를 가운데 정렬
            left_position = (slide_width - image_width) / 2
            if left_position < 0:
                left_position = 0
            
            # 이미지 추가
            slide.shapes.add_picture(
                image_data, 
                left_position,  # 가운데 정렬
                top_position,   # 20% 위로 이동
                width=image_width,
                height=image_height
            )
            
            # 슬라이드 하단 25%를 가리는 검은색 직사각형 추가
            bottom_rect_height = slide_height * 0.25
            bottom_rect_top = slide_height - bottom_rect_height
            
            # 검은색 직사각형 추가
            rect = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                0,  # 왼쪽 위치
                bottom_rect_top,  # 상단 위치 (슬라이드 높이의 75% 지점)
                slide_width,  # 넓이
                bottom_rect_height  # 높이 (슬라이드 높이의 25%)
            )
            
            # 직사각형 속성 설정
            fill = rect.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(0, 0, 0)  # 검은색
            rect.line.color.rgb = RGBColor(0, 0, 0)  # 테두리도 검은색
        else:
            # 원래 기능대로 이미지 추가 (색상 반전 없는 경우)
            slide.shapes.add_picture(
                image_file, 
                0, 
                0,
                width=slide_width,
                height=slide_height
            )

def add_black_slide(prs):
    """검은색 배경의 빈 슬라이드를 추가합니다."""
    try:
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # 빈 슬라이드 레이아웃
        set_slide_background_black(slide)
    except Exception as e:
        print(f"검은색 슬라이드 추가 중 오류 발생: {e}")

def add_text_to_slide(slide, text, left=None, top=None, width=None, height=None):
    """슬라이드에 텍스트 요소를 추가합니다."""
    # 슬라이드 크기 가져오기
    slide_width = slide.shapes.part.slide_layout.part.slide_master.part.presentation.slide_width
    slide_height = slide.shapes.part.slide_layout.part.slide_master.part.presentation.slide_height
    
    # 좌우 공백 없이 텍스트 박스 설정
    if left is None:
        left = 0  # 좌측 끝에서 시작
    if width is None:
        width = slide_width  # 슬라이드 너비 전체 사용
    if top is None:
        top = Inches(1.5)  # 상단 위치 조정
    if height is None:
        height = Inches(4.0)  # 높이 조정
    
    text_box = slide.shapes.add_textbox(left, top, width, height)
    text_frame = text_box.text_frame
    text_frame.word_wrap = True
    text_frame.vertical_anchor = MSO_ANCHOR.TOP
    
    # 텍스트 줄 추가
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        if i == 0:
            p = text_frame.paragraphs[0]
        else:
            p = text_frame.add_paragraph()
            
        p.text = line
        p.font.size = Pt(42)  # 폰트 크기
        p.font.name = "맑은 고딕"
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)  # 흰색
        p.alignment = PP_ALIGN.CENTER
        
        # 빨간색 밑줄 추가 (각 문장 아래)
        line_left = Inches(1.0)
        line_top = top + Inches(0.2 + i * 1.2)  # 텍스트 아래에 위치
        line_width = slide_width - Inches(2.0)  # 양쪽 여백
        line_height = Inches(0.03)  # 얇은 선
        
        line_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            line_left,
            line_top,
            line_width,
            line_height
        )
        fill = line_shape.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(255, 0, 0)  # 빨간색
    
    return text_box

def create_presentation(output_file, images_folder, invert_colors=False):
    """
    이미지 폴더로부터 프레젠테이션을 생성합니다.
    
    Args:
        output_file: 출력 파일 경로
        images_folder: 이미지 폴더 경로
        invert_colors: 이미지 색상을 반전할지 여부 (기본값: False)
    """
    # 기존 함수 구현에서 invert_colors 매개변수 활용
    
    # 프레젠테이션 객체 생성
    prs = Presentation()
    
    # 슬라이드 크기 설정 (16:9 비율)
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)
    
    # 이미지 추가 (이 함수도 invert_colors 매개변수 지원 필요)
    add_images_to_presentation(prs, images_folder, invert_colors)
    
    # 저장
    prs.save(output_file)
    return output_file

def merge_presentations(presentation_paths, output_path=None):
    """여러 프레젠테이션을 하나로 병합"""
    if not presentation_paths:
        print("병합할 프레젠테이션이 없습니다.")
        return None
        
    if not output_path:
        output_path = "merged_presentation.pptx"
    
    # 첫 번째 프레젠테이션으로 새 객체 생성
    try:
        print("새 프레젠테이션 객체 생성 중...")
        
        # 단순히 병합 대신 첫 번째 파일을 복사하여 시작
        first_ppt = presentation_paths[0]
        shutil.copy(first_ppt, output_path)
        
        if len(presentation_paths) == 1:
            print(f"변환된 파일이 하나뿐이므로 복사만 수행: {output_path}")
            return output_path
            
        # 첫 번째 파일을 제외한 나머지 파일들을 추가
        merged_prs = Presentation(output_path)
        total_slides = len(merged_prs.slides)
        
        print(f"첫 번째 프레젠테이션에서 {total_slides}개 슬라이드 확인")
        
        # 두 번째 프레젠테이션부터 슬라이드 추가
        for ppt_path in presentation_paths[1:]:
            if not os.path.exists(ppt_path):
                print(f"파일을 찾을 수 없습니다: {ppt_path}")
                continue
                
            try:
                print(f"'{os.path.basename(ppt_path)}' 병합 중...")
                source_prs = Presentation(ppt_path)
                
                # 슬라이드 개수 로깅
                slide_count = len(source_prs.slides)
                print(f"소스 프레젠테이션에서 {slide_count}개 슬라이드 발견")
                
                # 전체 슬라이드 복사: python-pptx에서는 슬라이드 직접 복사가 어려움
                # 대안: 슬라이드를 XML로 추출하여 새 프레젠테이션에 삽입
                for slide in source_prs.slides:
                    # 이 소스 프레젠테이션의 마스터 슬라이드와 레이아웃 정보 가져오기
                    layout = slide.slide_layout
                    
                    # 새 슬라이드 추가
                    new_slide = merged_prs.slides.add_slide(merged_prs.slide_layouts[6])  # 빈 레이아웃
                    
                    # 배경 설정
                    background = new_slide.background
                    fill = background.fill
                    fill.solid()
                    fill.fore_color.rgb = RGBColor(0, 0, 0)  # 검은색
                    
                    # 슬라이드 요소 복사 (이미지, 텍스트 등)
                    for shape in slide.shapes:
                        # 이미지 처리
                        if shape.shape_type == MSO_SHAPE.PICTURE:
                            try:
                                image = shape.image
                                image_bytes = image.blob
                                left = shape.left
                                top = shape.top
                                width = shape.width
                                height = shape.height
                                
                                # 새 슬라이드에 이미지 추가
                                new_shape = new_slide.shapes.add_picture(
                                    BytesIO(image_bytes), left, top, width, height
                                )
                                print(f"이미지 추가됨: {width}x{height}")
                            except Exception as e:
                                print(f"이미지 추가 실패: {e}")
                        
                        # 도형 처리
                        elif shape.shape_type == MSO_SHAPE.AUTO_SHAPE:
                            try:
                                left = shape.left
                                top = shape.top
                                width = shape.width
                                height = shape.height
                                
                                new_shape = new_slide.shapes.add_shape(
                                    shape.auto_shape_type, left, top, width, height
                                )
                                
                                # 도형 스타일 복사
                                if hasattr(shape, 'fill'):
                                    new_shape.fill.solid()
                                    if hasattr(shape.fill, 'fore_color') and shape.fill.fore_color:
                                        new_shape.fill.fore_color.rgb = shape.fill.fore_color.rgb
                                
                                # 텍스트 복사
                                if hasattr(shape, 'text_frame') and shape.text:
                                    new_shape.text = shape.text
                                    print(f"텍스트 도형 추가됨: {shape.text[:20]}...")
                            except Exception as e:
                                print(f"도형 추가 실패: {e}")
                            
                        # 텍스트 처리
                        if hasattr(shape, 'text_frame') and shape.text.strip():
                            # 슬라이드 크기 가져오기
                            slide_width = new_slide.shapes.part.slide_layout.part.slide_master.part.presentation.slide_width
                            slide_height = new_slide.shapes.part.slide_layout.part.slide_master.part.presentation.slide_height
                            
                            # 텍스트 내용 가져오기
                            text = shape.text.strip()
                            
                            # 좌우 공백 없이 텍스트 박스 설정
                            left = 0  # 좌측 끝에서 시작
                            top = Inches(1.5)  # 상단 위치 조정
                            width = slide_width  # 슬라이드 너비 전체 사용
                            height = Inches(4.0)
                            
                            text_box = new_slide.shapes.add_textbox(left, top, width, height)
                            text_frame = text_box.text_frame
                            text_frame.word_wrap = True
                            text_frame.vertical_anchor = MSO_ANCHOR.TOP
                            
                            # 텍스트 줄 추가
                            lines = text.split('\n')
                            
                            for i, line in enumerate(lines):
                                if i == 0:
                                    p = text_frame.paragraphs[0]
                                else:
                                    p = text_frame.add_paragraph()
                                    
                                p.text = line
                                p.font.size = Pt(42)
                                p.font.name = "맑은 고딕"
                                p.font.bold = True
                                p.font.color.rgb = RGBColor(255, 255, 255)  # 흰색
                                p.alignment = PP_ALIGN.CENTER
                                
                                # 빨간색 밑줄 추가 (각 문장 아래)
                                line_left = Inches(1.0)
                                line_top = top + Inches(0.2 + i * 1.2)  # 텍스트 아래에 위치
                                line_width = slide_width - Inches(2.0)  # 양쪽 여백
                                line_height = Inches(0.03)  # 얇은 선
                                
                                line_shape = new_slide.shapes.add_shape(
                                    MSO_SHAPE.RECTANGLE,
                                    line_left,
                                    line_top,
                                    line_width,
                                    line_height
                                )
                                fill = line_shape.fill
                                fill.solid()
                                fill.fore_color.rgb = RGBColor(255, 0, 0)  # 빨간색
                
                total_slides += slide_count
                print(f"'{os.path.basename(ppt_path)}'에서 {slide_count}개 슬라이드 병합됨")
                
            except Exception as e:
                print(f"'{ppt_path}' 병합 중 오류 발생: {e}")
        
        # 저장
        merged_prs.save(output_path)
        print(f"\n병합된 프레젠테이션 저장 완료: {output_path}")
        print(f"총 {total_slides}개 슬라이드가 병합되었습니다.")
        
        return output_path  # 성공 시 경로 반환
        
    except Exception as e:
        print(f"프레젠테이션 병합 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None  # 실패 시 None 반환

def convert_presentation_to_lyrics_format(input_ppt, output_ppt=None):
    """PPT 파일을 가사 형식으로 변환합니다."""
    import tempfile
    from lyricsslide_creator.ppt_converter import convert_ppt_to_images
    
    if not output_ppt:
        base_name, ext = os.path.splitext(input_ppt)
        # 항상 .pptx 확장자로 저장
        output_ppt = f"{base_name}_lyrics.pptx"
    
    # 출력 파일이 .pptx로 끝나는지 확인
    if not output_ppt.lower().endswith('.pptx'):
        output_ppt = f"{os.path.splitext(output_ppt)[0]}.pptx"
        print(f"참고: 출력 파일은 항상 .pptx 형식으로 저장됩니다. 변경된 경로: {output_ppt}")
    
    # 이미지 추출용 임시 폴더 생성
    temp_dir = tempfile.mkdtemp()
    try:
        print(f"'{input_ppt}'에서 이미지를 추출하는 중...")
        
        # PPT를 이미지로 변환
        image_paths = convert_ppt_to_images(input_ppt, temp_dir)
        
        if not image_paths:
            print("이미지 추출에 실패했습니다.")
            return None
        
        # 추출된 이미지를 새 프레젠테이션에 추가
        print("추출된 이미지로 프레젠테이션 생성 중...")
        all_image_paths = [(input_ppt, image_paths)]
        success = create_presentation(all_image_paths, output_ppt)
        
        if success:
            print(f"변환 완료: {output_ppt}")
            return output_ppt
        else:
            print("프레젠테이션 생성 중 오류가 발생했습니다.")
            return None
    
    except Exception as e:
        print(f"프레젠테이션 변환 중 오류 발생: {e}")
        return None
    
    finally:
        # 임시 파일 정리
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)