# pptx_creator.py

import os
import tempfile
import shutil
import sys
from pptx import Presentation
from pptx.util import Inches
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
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
                            
                        # 플레이스홀더 및 기타 텍스트 도형 처리
                        elif hasattr(shape, 'text_frame'):
                            try:
                                if shape.text.strip():
                                    left = shape.left
                                    top = shape.top
                                    width = shape.width
                                    height = shape.height
                                    
                                    text_box = new_slide.shapes.add_textbox(
                                        left, top, width, height
                                    )
                                    text_box.text = shape.text
                                    print(f"텍스트 추가됨: {shape.text[:20]}...")
                            except Exception as e:
                                print(f"텍스트 추가 실패: {e}")
                
                total_slides += slide_count
                print(f"'{os.path.basename(ppt_path)}'에서 {slide_count}개 슬라이드 병합됨")
                
            except Exception as e:
                print(f"'{ppt_path}' 병합 중 오류 발생: {e}")
        
        # 저장
        merged_prs.save(output_path)
        print(f"\n병합된 프레젠테이션 저장 완료: {output_path}")
        print(f"총 {total_slides}개 슬라이드가 병합되었습니다.")
        
        return output_path
        
    except Exception as e:
        print(f"프레젠테이션 병합 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

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