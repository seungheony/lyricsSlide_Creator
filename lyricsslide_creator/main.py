"""
PPT 파일을 변환하여 가사 슬라이드에 최적화된 프레젠테이션을 생성하는 도구
"""

import sys
import os
import traceback
import argparse
import subprocess
import importlib
from pathlib import Path

# 패키지 임포트 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 패키지 버전 정보
__version__ = '0.1.0'

def check_dependencies():
    """필요한 패키지가 설치되어 있는지 확인합니다."""
    # 로그 출력
    print("종속성 확인 중...")
    
    # dependency_checker 모듈 사용 시도
    try:
        # 상대 경로로 시도
        try:
            from .dependency_checker import check_dependencies
            print("패키지 모드에서 종속성 확인 중...")
            return check_dependencies()
        except (ImportError, ValueError) as e:
            print(f"패키지 모드 임포트 실패: {e}")
            
            # 절대 경로로 시도
            try:
                from lyricsslide_creator.dependency_checker import check_dependencies
                print("절대 경로 모드에서 종속성 확인 중...")
                return check_dependencies()
            except ImportError as e:
                print(f"절대 경로 임포트 실패: {e}")
                
                # 소스 디렉토리에서 직접 시도
                try:
                    # 같은 디렉토리에서 직접 임포트
                    import dependency_checker
                    print("로컬 모드에서 종속성 확인 중...")
                    return dependency_checker.check_dependencies()
                except ImportError as e:
                    print(f"로컬 임포트 실패: {e}")
                    raise
    except Exception as e:
        print(f"종속성 확인 모듈 임포트 중 오류: {e}")
        
        # 종속성 확인 모듈 자체가 로드되지 않을 경우 - 최소한의 직접 확인
        print("종속성 확인 모듈을 불러올 수 없습니다. 기본 확인을 수행합니다...")
        
        # 필요한 패키지 목록
        required_packages = ['python-pptx', 'Pillow', 'pdf2image']
        if sys.platform.startswith('win'):
            required_packages.append('comtypes')
            
        # 패키지 확인
        missing_packages = []
        for package in required_packages:
            try:
                if package == 'python-pptx':
                    importlib.import_module('pptx')
                elif package == 'Pillow':
                    importlib.import_module('PIL')
                elif package == 'pdf2image':
                    importlib.import_module('pdf2image')
                else:
                    importlib.import_module(package.lower())
                print(f"{package} 패키지가 이미 설치되어 있습니다.")
            except ImportError:
                print(f"{package} 패키지가 설치되어 있지 않습니다.")
                missing_packages.append(package)
        
        # 누락된 패키지 설치 제안
        if missing_packages:
            print("\n다음 패키지를 설치해야 합니다:")
            for pkg in missing_packages:
                print(f" - {pkg}")
            print("\n설치 명령어:")
            print(f"pip install {' '.join(missing_packages)}")
            
            # 자동 설치 시도 여부 확인
            try:
                install = input("\n누락된 패키지를 자동으로 설치하시겠습니까? (y/n): ").strip().lower()
                if install == 'y':
                    print("\n패키지 설치 중...")
                    try:
                        for pkg in missing_packages:
                            print(f"{pkg} 설치 중...")
                            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
                        print("\n모든 패키지가 설치되었습니다!")
                        return True
                    except Exception as e:
                        print(f"패키지 설치 중 오류 발생: {e}")
            except (KeyboardInterrupt, EOFError):
                print("\n자동 설치를 건너뜁니다.")
        
        return len(missing_packages) == 0

def get_args():
    """명령줄 인수를 파싱합니다."""
    parser = argparse.ArgumentParser(description='PPT 파일을 변환하여 새로운 프레젠테이션을 생성합니다.')
    parser.add_argument('-d', '--directory', help='변환할 PPT 파일들이 있는 디렉토리 경로')
    parser.add_argument('-o', '--output', default='merged_presentation.pptx', 
                        help='생성될 프레젠테이션 파일 이름 (기본값: merged_presentation.pptx)')
    parser.add_argument('-i', '--images-dir', default='converted_images',
                        help='변환된 이미지가 저장될 디렉토리 (기본값: converted_images)')
    parser.add_argument('--keep-images', action='store_true',
                        help='처리 후 변환된 이미지 파일 유지')
    parser.add_argument('--dependency-check', action='store_true',
                        help='필요한 종속성을 확인하고 종료합니다')
    parser.add_argument('--version', action='version', 
                        version=f'lyricsslide-creator {__version__}')
    return parser.parse_args()

def run_main():
    """메인 프로그램 실행 함수"""
    try:
        # 명령줄 인수 파싱
        args = get_args()
        
        # 종속성 확인 모드일 경우
        if args.dependency_check:
            if check_dependencies():
                print("\n✅ 모든 종속성이 설치되어 있습니다.")
                sys.exit(0)
            else:
                print("\n❌ 일부 종속성이 설치되어 있지 않습니다.")
                sys.exit(1)
        
        # 필요한 패키지 확인
        if not check_dependencies():
            print("필요한 패키지가 모두 설치되어 있지 않습니다.")
            print("pip install python-pptx Pillow pdf2image 명령으로 설치하세요.")
            if sys.platform.startswith('win'):
                print("Windows에서는 comtypes 패키지도 필요합니다: pip install comtypes")
            sys.exit(1)
            
        # 패키지 내 모듈 임포트 - 패키지 내 혹은 개발 모드에서 모두 작동하도록
        try:
            # 패키지로 설치 시
            from .pptx_creator import create_presentation, delete_existing_presentation
            from .ppt_converter import convert_ppt_files
            from .utils import clear_directory
        except (ImportError, ValueError):
            # 개발 중 직접 실행 시
            from lyricsslide_creator.pptx_creator import create_presentation, delete_existing_presentation
            from lyricsslide_creator.ppt_converter import convert_ppt_files
            from lyricsslide_creator.utils import clear_directory

        # 출력 파일 이름 설정
        output_pptx = args.output

        # 기존의 출력 파일 삭제
        if not delete_existing_presentation(output_pptx):
            print(f"'{output_pptx}' 파일을 사용 중이거나 접근할 수 없습니다. 프로그램을 종료합니다.")
            sys.exit(1)

        # 사용자로부터 디렉토리 경로 입력 받기
        directory = args.directory
        if not directory:
            directory = input("변환할 PPT 파일들이 있는 디렉토리의 경로를 입력하세요: ")
        
        if not os.path.isdir(directory):
            print("유효한 디렉토리 경로가 아닙니다.")
            sys.exit(1)

        # 이미지가 저장될 디렉토리 설정 및 정리
        output_dir = args.images_dir
        clear_directory(output_dir)

        # PPT 파일을 이미지로 변환
        ppt_files = [os.path.join(directory, f) for f in os.listdir(directory)
                    if f.lower().endswith(('.ppt', '.pptx'))]

        if not ppt_files:
            print("지정된 디렉토리에 PPT 파일이 없습니다.")
            sys.exit(1)

        print(f"\n{len(ppt_files)}개의 PPT 파일을 처리합니다...")
        all_image_paths = convert_ppt_files(ppt_files, output_dir)

        # 이미지 수 확인
        total_images = sum(len(images) for _, images in all_image_paths)
        print(f"\n총 {total_images}개의 슬라이드 이미지가 생성되었습니다.")

        # 새로운 프레젠테이션 생성 및 이미지 추가
        if create_presentation(all_image_paths, output_pptx):
            print("\n변환 작업이 성공적으로 완료되었습니다.")
            print(f"생성된 파일: {os.path.abspath(output_pptx)}")
        else:
            print("\n프레젠테이션 생성 중 오류가 발생했습니다.")
            sys.exit(1)
            
        # 이미지 파일 정리 (선택적)
        if not args.keep_images:
            clear_directory(output_dir)
            print(f"'{output_dir}' 임시 이미지 폴더가 정리되었습니다.")
        else:
            print(f"변환된 이미지가 '{output_dir}' 폴더에 보존되었습니다.")
            
    except KeyboardInterrupt:
        print("\n사용자에 의해 프로그램이 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n예상치 못한 오류가 발생했습니다: {e}")
        print("오류 상세 정보:")
        traceback.print_exc()
        sys.exit(1)

def cli_entry_point():
    """명령줄 도구의 진입점"""
    run_main()

if __name__ == "__main__":
    run_main()