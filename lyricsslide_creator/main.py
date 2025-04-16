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

# 패키지 버전 정보
__version__ = '0.1.0'

def ensure_dependencies():
    """필요한 종속성을 확인하고 없으면 자동으로 설치합니다."""
    print("종속성 확인 중...")
    
    # requirements.txt 파일에서 종속성 목록 읽기
    requirements_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "requirements.txt")
    dependencies = []
    
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            for line in f:
                # 주석 또는 빈 줄 무시
                if line.strip() and not line.strip().startswith('//'):
                    # 버전 정보 제거 (예: requests>=2.28.0 -> requests)
                    package = line.strip().split('>=')[0].split('==')[0].strip()
                    dependencies.append(package)
    else:
        # requirements.txt가 없는 경우 기본 종속성 사용
        dependencies = [
            'python-pptx', 'Pillow', 'pdf2image', 
            'requests', 'beautifulsoup4'
        ]
    
    # 모든 종속성 확인 및 설치
    missing_dependencies = []
    
    for package in dependencies:
        try:
            # 패키지별 특수 처리
            if package == 'python-pptx':
                importlib.import_module('pptx')
            elif package == 'Pillow':
                importlib.import_module('PIL')
            elif package == 'beautifulsoup4':
                importlib.import_module('bs4')
            else:
                importlib.import_module(package)
            print(f"✓ {package} 패키지가 이미 설치되어 있습니다.")
        except ImportError:
            print(f"✗ {package} 패키지가 설치되어 있지 않습니다.")
            missing_dependencies.append(package)
    
    # 누락된 종속성 설치
    if missing_dependencies:
        print(f"\n다음 패키지를 설치합니다: {', '.join(missing_dependencies)}")
        
        for package in missing_dependencies:
            try:
                print(f"{package} 설치 중...")
                # pip을 통한 패키지 설치
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ {package} 설치 완료")
            except subprocess.CalledProcessError as e:
                print(f"✗ {package} 설치 실패: {e}")
                return False
    
    print("모든 종속성이 설치되었습니다.")
    return True

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

def run_lyrics_ppt_creator():
    """가사 PPT 제작 기능 실행"""
    print("\n=== 가사 PPT 제작 ===")
    
    # 멜론 스크래퍼 초기화
    try:
        from lyricsslide_creator.lyrics_scraper import MelonScraper
        from lyricsslide_creator.lyrics_formatter import LyricsFormatter
        from lyricsslide_creator.ppt_creator import LyricsPPTCreator
    except ImportError as e:
        print(f"필요한 모듈을 임포트할 수 없습니다: {e}")
        return
    
    scraper = MelonScraper()
    
    # 노래 제목 입력 (여러 개 가능)
    print("\n노래 제목을 입력하세요 (여러 곡을 검색하려면 쉼표로 구분):")
    song_input = input("> ")
    
    song_titles = [title.strip() for title in song_input.split(",")]
    
    if not song_titles:
        print("검색할 노래 제목이 없습니다.")
        return
    
    # 각 노래 제목 검색
    for song_title in song_titles:
        print(f"\n'{song_title}' 검색 중...")
        search_results = scraper.search_songs(song_title)
        
        if not search_results:
            print(f"'{song_title}'에 대한 검색 결과가 없습니다.")
            continue
        
        # 검색 결과 표시
        print(f"\n'{song_title}'에 대한 검색 결과 ({len(search_results)}개):")
        for i, song in enumerate(search_results):
            print(f"{i+1}. {song['title']} - {song['artist']} [{song['album']}]")
            print(f"   {song['preview']}")
        
        # 노래 선택
        print("\n사용할 노래 번호를 선택하세요 (0: 건너뛰기):")
        try:
            choice = int(input("> ")) - 1
            
            if choice < 0 or choice >= len(search_results):
                print("선택을 건너뜁니다.")
                continue
            
            selected_song = search_results[choice]
            
            # 전체 가사 가져오기
            print(f"\n'{selected_song['title']}' 가사 가져오는 중...")
            song_info, full_lyrics = scraper.get_full_lyrics(selected_song['id'])
            
            # 가사 확인
            print("\n=== 노래 정보 ===")
            print(f"제목: {song_info['title']}")
            print(f"아티스트: {song_info['artist']}")
            print(f"앨범: {song_info['album']}")
            
            print("\n=== 가사 미리보기 ===")
            preview_lines = full_lyrics.split('\n')[:5]
            print('\n'.join(preview_lines))
            print("...")
            
            # 계속 진행 여부 확인
            print("\n이 노래의 가사로 PPT를 만드시겠습니까? (y/n):")
            confirm = input("> ").strip().lower()
            
            if confirm != 'y':
                print("선택을 취소했습니다.")
                continue
            
            # 가사 페이지 분할
            print("\n가사를 페이지로 분할 중...")
            formatter = LyricsFormatter()
            lyrics_pages = formatter.split_lyrics_into_pages(full_lyrics)
            
            print(f"총 {len(lyrics_pages)}개의 페이지로 분할되었습니다.")
            
            # PPT 생성
            print("\nPPT 생성 중...")
            output_file = f"{song_info['title']}_가사.pptx"
            creator = LyricsPPTCreator(output_file)
            result_path = creator.create_presentation(song_info, lyrics_pages)
            
            print(f"\nPPT 생성 완료: {result_path}")
            
        except ValueError:
            print("잘못된 입력입니다. 숫자를 입력해주세요.")
            continue
        except Exception as e:
            print(f"처리 중 오류 발생: {e}")
            continue

def run_ppt_converter(args):
    """기존 PPT 변환 기능 실행"""
    try:
        # 패키지 내 모듈 임포트
        from lyricsslide_creator.pptx_creator import create_presentation, delete_existing_presentation
        from lyricsslide_creator.ppt_converter import convert_ppt_files
        from lyricsslide_creator.utils import clear_directory
        
        # 출력 파일 이름 설정
        output_pptx = args.output

        # 기존의 출력 파일 삭제
        if not delete_existing_presentation(output_pptx):
            print(f"'{output_pptx}' 파일을 사용 중이거나 접근할 수 없습니다. 프로그램을 종료합니다.")
            return False

        # 사용자로부터 디렉토리 경로 입력 받기
        directory = args.directory
        if not directory:
            directory = input("변환할 PPT 파일들이 있는 디렉토리의 경로를 입력하세요: ")
        
        if not os.path.isdir(directory):
            print("유효한 디렉토리 경로가 아닙니다.")
            return False

        # 이미지가 저장될 디렉토리 설정 및 정리
        output_dir = args.images_dir
        clear_directory(output_dir)

        # PPT 파일을 이미지로 변환
        ppt_files = [os.path.join(directory, f) for f in os.listdir(directory)
                    if f.lower().endswith(('.ppt', '.pptx'))]

        if not ppt_files:
            print("지정된 디렉토리에 PPT 파일이 없습니다.")
            return False

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
            return False
            
        # 이미지 파일 정리 (선택적)
        if not args.keep_images:
            clear_directory(output_dir)
            print(f"'{output_dir}' 임시 이미지 폴더가 정리되었습니다.")
        else:
            print(f"변환된 이미지가 '{output_dir}' 폴더에 보존되었습니다.")
        
        return True
    except Exception as e:
        print(f"PPT 변환 기능 실행 중 오류 발생: {e}")
        return False

def run_main():
    """메인 프로그램 실행 함수"""
    try:
        # 명령줄 인수 파싱
        args = get_args()
        
        # 종속성 확인 모드일 경우
        if args.dependency_check:
            if ensure_dependencies():
                print("\n✅ 모든 종속성이 설치되어 있습니다.")
                sys.exit(0)
            else:
                print("\n❌ 일부 종속성이 설치되어 있지 않습니다.")
                sys.exit(1)
        
        # 필요한 패키지 확인 및 설치
        if not ensure_dependencies():
            print("필요한 종속성을 설치할 수 없습니다. 프로그램을 종료합니다.")
            sys.exit(1)
            
        # 기능 선택 메뉴
        print("\n=== lyricsSlide Creator ===")
        print("1. 가사 PPT 제작 (멜론 검색)")
        print("2. 악보 포함 가사 PPT 제작 (기존 PPT 변환)")
        print("0. 종료")
        
        try:
            choice = int(input("\n원하는 기능을 선택하세요: "))
            
            if choice == 0:
                print("프로그램을 종료합니다.")
                return
            elif choice == 1:
                # 새로운 기능: 가사 PPT 제작
                run_lyrics_ppt_creator()
            elif choice == 2:
                # 기존 기능: 악보 포함 가사 PPT 제작
                if not run_ppt_converter(args):
                    print("PPT 변환 기능 실행에 실패했습니다.")
            else:
                print("잘못된 선택입니다.")
        except ValueError:
            print("숫자를 입력해주세요.")
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"\n예상치 못한 오류가 발생했습니다: {e}")
        traceback.print_exc()

def cli_entry_point():
    """명령줄 도구의 진입점"""
    run_main()

if __name__ == "__main__":
    run_main()