# import os
# import sys
# import subprocess
# import tempfile
# import shutil
# from PIL import Image, ImageOps
# from pptx import Presentation
# from pptx.util import Inches, Pt
# from pptx.dml.color import RGBColor
# from pptx.enum.shapes import MSO_SHAPE

# def install_package(package_name):
#     try:
#         print(f"패키지 '{package_name}'를 설치합니다...")
#         subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
#         print(f"패키지 '{package_name}' 설치 완료.")
#     except subprocess.CalledProcessError:
#         print(f"패키지 '{package_name}' 설치에 실패했습니다. 수동으로 설치해 주십시오.")

# def check_python_packages():
#     missing_packages = []
#     try:
#         import PIL
#     except ImportError:
#         missing_packages.append('Pillow')

#     try:
#         import pptx
#     except ImportError:
#         missing_packages.append('python-pptx')

#     try:
#         import pdf2image
#     except ImportError:
#         missing_packages.append('pdf2image')

#     if missing_packages:
#         print("다음 Python 패키지가 설치되어 있지 않습니다:")
#         for pkg in missing_packages:
#             print(f"- {pkg}")

#         # 자동 설치 여부를 사용자에게 묻습니다.
#         print("부족한 패키지를 설치하려면 엔터 키를 누르십시오. 취소하려면 'q'를 입력하고 엔터 키를 누르십시오.")
#         choice = input().lower().strip()
#         if choice == 'q':
#             print("프로그램을 종료합니다.")
#             sys.exit(1)
#         else:
#             for pkg in missing_packages:
#                 install_package(pkg)
#             # 패키지 설치 후 다시 검사
#             return check_python_packages()
#     else:
#         print("모든 필요한 Python 패키지가 설치되어 있습니다.")
#         return True

# def check_libreoffice():
#     if sys.platform.startswith('darwin'):
#         # macOS 환경
#         libreoffice_path = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
#     elif sys.platform.startswith('win'):
#         # Windows 환경
#         libreoffice_path = r'C:\Program Files\LibreOffice\program\soffice.exe'
#     else:
#         # 기타 Unix 계열 시스템
#         libreoffice_path = 'libreoffice'

#     # LibreOffice 실행 파일 존재 여부 확인
#     if sys.platform.startswith('darwin') or sys.platform.startswith('win'):
#         if os.path.exists(libreoffice_path):
#             print(f"LibreOffice가 설치되어 있습니다: {libreoffice_path}")
#             return True
#         else:
#             print("LibreOffice가 설치되어 있지 않거나 기본 경로에 없습니다.")
#             print("LibreOffice를 설치하거나 경로를 확인하십시오.")
#             print("다운로드 링크: https://www.libreoffice.org/download/download/")
#             return False
#     else:
#         # Unix 계열 시스템에서는 'which' 명령으로 확인
#         from shutil import which
#         if which('libreoffice') is not None or which('soffice') is not None:
#             print("LibreOffice가 설치되어 있습니다.")
#             return True
#         else:
#             print("LibreOffice가 설치되어 있지 않습니다.")
#             print("LibreOffice를 설치하십시오.")
#             print("다운로드 링크: https://www.libreoffice.org/download/download/")
#             return False

# def check_dependencies():
#     python_packages_ok = check_python_packages()
#     libreoffice_ok = check_libreoffice()

#     if python_packages_ok and libreoffice_ok:
#         print("모든 종속성이 설치되어 있습니다.")
#         return True
#     else:
#         print("필요한 종속성이 설치되어 있지 않습니다. 위의 안내에 따라 설치를 완료한 후 다시 시도하십시오.")
#         return False

# def clear_converted_images_folder(output_dir):
#     if os.path.exists(output_dir):
#         for filename in os.listdir(output_dir):
#             file_path = os.path.join(output_dir, filename)
#             try:
#                 if os.path.isfile(file_path):
#                     os.unlink(file_path)
#             except Exception as e:
#                 print(f"파일 삭제 중 오류 발생: {e}")
#     else:
#         os.makedirs(output_dir)
#     print(f"'{output_dir}' 폴더를 정리하였습니다.")

# def convert_ppt_to_pptx(ppt_file):
#     # LibreOffice 실행 파일 경로 설정
#     if sys.platform.startswith('darwin'):
#         libreoffice_path = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
#     elif sys.platform.startswith('win'):
#         libreoffice_path = r'C:\Program Files\LibreOffice\program\soffice.exe'
#     else:
#         libreoffice_path = 'libreoffice'

#     # 임시 디렉토리 생성
#     with tempfile.TemporaryDirectory() as temp_dir:
#         command = [
#             libreoffice_path,
#             '--headless',
#             '--convert-to', 'pptx',
#             '--outdir', temp_dir,
#             ppt_file
#         ]

#         try:
#             subprocess.run(command, check=True)
#             print(f"{ppt_file}를 PPTX로 변환 완료.")
#         except subprocess.CalledProcessError as e:
#             print(f"{ppt_file}를 PPTX로 변환 중 오류 발생: {e}")
#             sys.exit(1)

#         # 변환된 .pptx 파일 찾기
#         for file_name in os.listdir(temp_dir):
#             if file_name.lower().endswith('.pptx'):
#                 converted_pptx_file = os.path.join(temp_dir, file_name)
#                 # 임시 디렉토리가 삭제되기 전에 파일을 복사합니다.
#                 temp_pptx_file = os.path.join(tempfile.gettempdir(), file_name)
#                 shutil.copy(converted_pptx_file, temp_pptx_file)
#                 return temp_pptx_file

#         # 변환된 파일을 찾지 못한 경우 오류 처리
#         print(f"{ppt_file}를 PPTX로 변환하는데 실패하였습니다.")
#         sys.exit(1)

# def set_slide_background_to_white(pptx_file, modified_pptx_file):
#     from pptx import Presentation
#     from pptx.dml.color import RGBColor

#     prs = Presentation(pptx_file)
#     for slide in prs.slides:
#         background = slide.background
#         fill = background.fill
#         fill.solid()
#         fill.fore_color.rgb = RGBColor(255, 255, 255)  # 흰색
#     prs.save(modified_pptx_file)
#     print(f"슬라이드 배경을 흰색으로 변경하였습니다: {modified_pptx_file}")

# def invert_image_colors(image_path):
#     with Image.open(image_path) as img:
#         inverted_image = ImageOps.invert(img.convert('RGB'))
#         inverted_image.save(image_path)
#         print(f"이미지 색상을 반전시켰습니다: {image_path}")

# def convert_ppt_to_images(ppt_file, output_dir):
#     # PPT 파일 이름
#     ppt_name = os.path.splitext(os.path.basename(ppt_file))[0]

#     # 1. .ppt 파일을 .pptx로 변환 (필요한 경우)
#     if ppt_file.lower().endswith('.ppt'):
#         # .ppt를 .pptx로 변환하고 변환된 파일의 경로를 얻습니다.
#         pptx_file = convert_ppt_to_pptx(ppt_file)
#     else:
#         pptx_file = ppt_file

#     # 2. 슬라이드 배경을 흰색으로 변경하여 임시 파일에 저장
#     with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx') as tmp_pptx:
#         modified_pptx_file = tmp_pptx.name

#     set_slide_background_to_white(pptx_file, modified_pptx_file)

#     # 3. 수정된 PPTX를 PDF로 변환
#     if sys.platform.startswith('darwin'):
#         libreoffice_path = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
#     elif sys.platform.startswith('win'):
#         libreoffice_path = r'C:\Program Files\LibreOffice\program\soffice.exe'
#     else:
#         libreoffice_path = 'libreoffice'

#     command = [
#         libreoffice_path,
#         '--headless',
#         '--convert-to', 'pdf',
#         '--outdir', output_dir,
#         modified_pptx_file
#     ]

#     try:
#         subprocess.run(command, check=True)
#         print(f"{modified_pptx_file}를 PDF로 변환 완료.")
#     except subprocess.CalledProcessError as e:
#         print(f"{modified_pptx_file}를 PDF로 변환 중 오류 발생: {e}")
#         os.unlink(modified_pptx_file)
#         sys.exit(1)

#     # 4. PDF를 이미지로 변환
#     from pdf2image import convert_from_path

#     pdf_file = os.path.join(output_dir, os.path.splitext(os.path.basename(modified_pptx_file))[0] + '.pdf')

#     image_paths = []  # 생성된 이미지 파일 경로를 저장

#     try:
#         images = convert_from_path(pdf_file, dpi=300)

#         for idx, image in enumerate(images):
#             image_filename = f"{ppt_name}_slide{idx + 1}.png"
#             image_path = os.path.join(output_dir, image_filename)
#             image.save(image_path, 'PNG')

#             # 이미지 색상 반전
#             invert_image_colors(image_path)

#             image_paths.append(image_path)  # 이미지 경로 저장

#         print("PDF를 이미지로 변환 및 색상 반전 완료.")
#     except Exception as e:
#         print(f"PDF를 이미지로 변환 중 오류 발생: {e}")
#         os.unlink(modified_pptx_file)
#         sys.exit(1)

#     # 5. 중간 파일 삭제
#     os.remove(pdf_file)
#     os.unlink(modified_pptx_file)
#     if ppt_file.lower().endswith('.ppt'):
#         os.remove(pptx_file)

#     return image_paths  # 이미지 경로 리스트 반환

# def add_images_to_presentation(prs, image_paths):
#     for image_path in image_paths:
#         slide = prs.slides.add_slide(prs.slide_layouts[6])  # 빈 슬라이드 레이아웃

#         # 슬라이드 크기 가져오기
#         slide_width = prs.slide_width
#         slide_height = prs.slide_height

#         # 이미지 위치 및 크기 계산
#         shift_up = slide_height * 0.15  # 슬라이드 높이의 15%만큼 위로 이동
#         image_height = slide_height * (1 + 0.15)  # 이미지 높이를 슬라이드 높이의 115%로 설정

#         left = Inches(0)
#         top = -shift_up  # 위로 이동시키기 위해 음수 값 사용

#         # 이미지 추가
#         pic = slide.shapes.add_picture(image_path, left, top, width=slide_width, height=image_height)
#         print(f"이미지를 슬라이드에 추가하였습니다: {image_path}")

#         # 슬라이드 하단 20%를 가리는 검은색 직사각형 추가
#         rect_height = slide_height * 0.2
#         rect_top = slide_height * 0.8  # 슬라이드 높이의 80% 위치

#         shape = slide.shapes.add_shape(
#             MSO_SHAPE.RECTANGLE,
#             left=Inches(0),
#             top=rect_top,
#             width=slide_width,
#             height=rect_height
#         )
#         fill = shape.fill
#         fill.solid()
#         fill.fore_color.rgb = RGBColor(0, 0, 0)  # 검은색
#         shape.line.color.rgb = RGBColor(0, 0, 0)  # 테두리 색상 제거
#         print("하단 검은색 직사각형을 추가하였습니다.")

# def add_black_slide(prs):
#     slide = prs.slides.add_slide(prs.slide_layouts[6])  # 빈 슬라이드 레이아웃
#     background = slide.background
#     fill = background.fill
#     fill.solid()
#     fill.fore_color.rgb = RGBColor(0, 0, 0)  # 검은색
#     print("검은색 배경 슬라이드를 추가하였습니다.")

# def main():
#     # 종속성 검사
#     if not check_dependencies():
#         sys.exit(1)

#     # 기존의 'merged_presentation.pptx' 파일 삭제
#     output_pptx = 'merged_presentation.pptx'
#     if os.path.exists(output_pptx):
#         os.remove(output_pptx)
#         print(f"기존의 '{output_pptx}' 파일을 삭제하였습니다.")

#     # 사용자로부터 디렉토리 경로 입력 받기
#     directory = input("변환할 PPT 파일들이 있는 디렉토리의 경로를 입력하세요: ")
#     if not os.path.isdir(directory):
#         print("유효한 디렉토리 경로가 아닙니다.")
#         sys.exit(1)

#     # 이미지가 저장될 디렉토리 설정 및 정리
#     output_dir = 'converted_images'
#     clear_converted_images_folder(output_dir)

#     # 새로운 프레젠테이션 생성
#     prs = Presentation()
#     prs.slide_width = Inches(13.33)  # 일반적인 와이드스크린 사이즈
#     prs.slide_height = Inches(7.5)

#     # 디렉토리 내의 모든 PPT/PPTX 파일 처리
#     ppt_files = [f for f in os.listdir(directory) if f.lower().endswith(('.ppt', '.pptx'))]
#     for idx, file_name in enumerate(ppt_files):
#         ppt_file = os.path.join(directory, file_name)
#         print(f"\n파일 변환 시작: {ppt_file}")
#         image_paths = convert_ppt_to_images(ppt_file, output_dir)
#         add_images_to_presentation(prs, image_paths)
#         if idx < len(ppt_files) - 1:
#             # 마지막 파일이 아닌 경우에만 검은색 슬라이드 추가
#             add_black_slide(prs)

#     # 새로운 PPT 파일 저장
#     prs.save(output_pptx)
#     print(f"\n모든 슬라이드가 '{output_pptx}' 파일에 저장되었습니다.")

# if __name__ == "__main__":
#     main()