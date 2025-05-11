"""
가사 슬라이드 메인 모듈
"""

import os
import sys
import time
import traceback
import argparse
import subprocess
import importlib
from pathlib import Path
from typing import List, Dict

# 상대 경로 임포트 대신 절대 경로 임포트 사용
try:
    # 패키지로 설치된 경우
    from lyricsslide_creator.lyrics_scraper import LyricsScraper
    from lyricsslide_creator.lyrics_formatter import LyricsFormatter
    from lyricsslide_creator.ppt_creator import LyricsPPTCreator
except ImportError:
    # 직접 실행하는 경우
    from lyrics_scraper import LyricsScraper
    from lyrics_formatter import LyricsFormatter
    from ppt_creator import LyricsPPTCreator

"""
PPT 파일을 변환하여 가사 슬라이드에 최적화된 프레젠테이션을 생성하는 도구
"""

# 패키지 버전 정보
__version__ = '0.1.0'

def is_packaged():
    """패키징된 환경인지 확인"""
    return getattr(sys, 'frozen', False)

def get_app_directory():
    """애플리케이션 실행 파일 위치 반환"""
    if is_packaged():
        # 패키징된 환경에서는 sys.executable 또는 sys._MEIPASS 경로 사용
        if hasattr(sys, '_MEIPASS'):
            return os.path.dirname(sys._MEIPASS)
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        # 개발 환경에서는 현재 파일 위치 사용
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ensure_dependencies():
    """필요한 종속성을 확인하고 없으면 자동으로 설치합니다."""
    print("종속성 확인 중...")
    
    # requirements.txt 파일에서 종속성 목록 읽기
    requirements_path = os.path.join(get_app_directory(), "requirements.txt")
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

def get_package_folders():
    """패키지 폴더 경로 반환"""
    app_dir = get_app_directory()
    input_dir = os.path.join(app_dir, "input_ppts")
    output_dir = os.path.join(app_dir, "output_ppts")
    return input_dir, output_dir

def ensure_package_folders():
    """패키지 폴더 존재 확인 및 생성"""
    app_dir = get_app_directory()
    input_dir = os.path.join(app_dir, "input_ppts")
    output_dir = os.path.join(app_dir, "output_ppts")
    
    folders_created = False
    
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"\n변환할 PPT 파일을 넣을 폴더를 생성했습니다: {input_dir}")
        folders_created = True
        
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"\n변환된 PPT 파일이 저장될 폴더를 생성했습니다: {output_dir}")
        folders_created = True
    
    return folders_created, input_dir, output_dir

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

def search_and_select_song(scraper, song_title):
    """노래 검색 및 선택"""
    print(f"\n'{song_title}' 검색 중...")
    search_results = scraper.search_songs(song_title)
    
    if not search_results:
        print(f"'{song_title}'에 대한 검색 결과가 없습니다.")
        return None
    
    print(f"\n'{song_title}'에 대한 검색 결과 ({len(search_results)}개):")
    for i, result in enumerate(search_results, 1):
        preview = result.get('preview', '가사 없음')
        if len(preview) > 50:
            preview = preview[:50] + "..."
            
        print(f"{i}. {result['title']} - {result['artist']} [{result['album']}]")
        print(f"   {preview}")
    
    # 사용자 선택
    print("\n사용할 노래 번호를 선택하세요 (0: 건너뛰기):")
    selection = int(input("> ").strip())
    
    if selection == 0:
        print(f"'{song_title}' 건너뛰기...")
        return None
    
    if selection < 1 or selection > len(search_results):
        print("올바른 번호를 입력해주세요.")
        return None
    
    return search_results[selection-1]

def process_lyrics(scraper, selected_song):
    """가사 처리"""
    print(f"\n'{selected_song['title']}' 가사 가져오는 중...")
    song_info = scraper.get_song_details(selected_song['id'])
    
    print("\n=== 노래 정보 ===")
    print(f"제목: {song_info['title']}")
    print(f"아티스트: {song_info['artist']}")
    print(f"앨범: {song_info['album']}")

    print("\n=== 가사 미리보기 ===")
    full_lyrics = song_info['lyrics']
    if len(full_lyrics) > 200:
        print(f"{full_lyrics[:200]}...")
    else:
        print(full_lyrics)

    print(f"\n이 노래의 가사로 PPT를 만드시겠습니까? (확인: 엔터, 이전으로: b):")
    user_choice = input("> ").strip().lower()
    if user_choice == 'b':
        print(f"'{selected_song['title']}' 건너뛰기, 노래 선택 화면으로 돌아갑니다...")
        return None
    
    return song_info

# split_lyrics_pages 함수 수정 - 노래 제목 표시
def split_lyrics_pages(song_info):
    """노래의 가사를 페이지로 분할합니다."""
    print(f"\n=== '{song_info['title']}' 가사 분할 ===")
    print("분할 방식을 선택하세요:")
    print("1. 자동 분할 (2줄씩)")
    print("2. 자동 분할 후 특정 페이지 선택")
    print("3. 수동 분할 (직접 줄 번호 지정)")

    split_mode = input("> ").strip()

    formatter = LyricsFormatter()
    if split_mode == "3":
        # 완전 수동 분할
        lyrics_pages = formatter.split_lyrics_with_user_input(song_info['lyrics'])
    elif split_mode == "2":
        # 자동 분할 후 특정 페이지 선택
        lyrics_pages = formatter.split_lyrics_with_interactive_selection(song_info['lyrics'])
    else:
        # 자동 분할 (2줄씩)
        print(f"\n'{song_info['title']}' 가사를 자동으로 페이지를 분할합니다 (2줄씩)...")
        formatter = LyricsFormatter(max_lines_per_slide=2)
        lyrics_pages = formatter.split_lyrics_into_pages(song_info['lyrics'])

    print(f"\n'{song_info['title']}' 가사가 총 {len(lyrics_pages)}개의 페이지로 분할되었습니다.")
    return lyrics_pages

# run_lyrics_ppt_creator 함수 수정 - 노래별 폰트 크기 설정 및 구분 슬라이드 추가
def run_lyrics_ppt_creator():
    """가사 PPT 생성 기능 실행"""
    print("\n=== 가사 PPT 제작 ===")
    
    # 패키지 폴더 확인
    _, _, output_dir = ensure_package_folders()
    
    # 노래 검색
    print("\n노래 제목을 입력하세요 (여러 곡을 검색하려면 쉼표로 구분):")
    search_input = input("> ").strip()
    
    if not search_input:
        print("검색어를 입력해주세요.")
        return
    
    song_titles = [title.strip() for title in search_input.split(',')]
    selected_songs = []
    scraper = LyricsScraper()
    
    # 모든 제목에 대해 검색 수행
    for song_title in song_titles:
        try:
            # 노래 검색 및 선택
            selected_song = search_and_select_song(scraper, song_title)
            if not selected_song:
                continue
                
            # 가사 처리
            song_info = process_lyrics(scraper, selected_song)
            if not song_info:
                continue
                
            # 선택한 노래 저장
            song_info['formatted_lyrics'] = None  # 가사 페이지 분할 정보는 나중에 처리
            selected_songs.append(song_info)
            
        except Exception as e:
            print(f"처리 중 오류 발생: {e}")
            continue
    
    # 선택한 노래가 없는 경우
    if not selected_songs:
        print("선택한 노래가 없습니다.")
        return
    
    # 출력 파일 경로 지정
    import time
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"멜론검색_{timestamp}.pptx")
    
    # 가사 페이지와 노래 구분점 저장
    all_lyrics_pages = []
    song_breaks = []  # 노래가 바뀌는 인덱스 저장
    font_sizes = []   # 노래별 폰트 크기 저장
    
    # 각 노래에 대해 가사 분할 및 폰트 크기 설정
    for song_info in selected_songs:
        # 현재 페이지 수에 따른 구분점 추가
        if all_lyrics_pages:  # 첫 번째 노래가 아닌 경우
            song_breaks.append(len(all_lyrics_pages))
        
        # 사용자로부터 폰트 크기 입력받기
        from lyricsslide_creator.template_ppt_creator import get_font_size_from_user
        print(f"\n=== '{song_info['title']}' 폰트 크기 설정 ===")
        font_size = get_font_size_from_user()
        font_sizes.append(font_size)
        
        # 가사 페이지 분할
        lyrics_pages = split_lyrics_pages(song_info)
        all_lyrics_pages.extend(lyrics_pages)
        print(f"'{song_info['title']}' 가사가 추가되었습니다.")
    
    # 템플릿 기반 PPT 생성 (노래 구분점과 폰트 크기 목록 전달)
    from lyricsslide_creator.template_ppt_creator import create_lyrics_slides_from_template
    result_path = create_lyrics_slides_from_template(
        output_file, 
        all_lyrics_pages, 
        song_breaks=song_breaks, 
        font_size=font_sizes
    )
    
    print(f"\nPPT 생성 완료: {result_path}")
    print(f"총 {len(selected_songs)}개 노래의 가사가 포함되었습니다.")
    print(f"결과물은 다음 폴더에 저장되었습니다: {output_dir}")

def run_ppt_convert():
    """악보 PPT를 가사 형식으로 변환하는 기능 실행"""
    print("\n=== 악보 PPT 변환 ===")
    
    # 패키지 폴더 확인 - 순서 수정
    folders_created, input_dir, output_dir = ensure_package_folders()
    
    # PPT 파일 목록 확인
    ppt_files = []
    for file in os.listdir(input_dir):
        if file.lower().endswith(('.pptx', '.ppt')):
            ppt_files.append(file)
    
    if not ppt_files:
        print(f"\n'{input_dir}' 폴더에 변환할 PPT 파일이 없습니다.")
        print("PPT 파일을 input_ppts 폴더에 넣은 후 다시 시도해주세요.")
        return
    
    print(f"\n다음 PPT 파일을 발견했습니다 (총 {len(ppt_files)}개):")
    for i, file in enumerate(ppt_files, 1):
        print(f"{i}. {file}")
    
    # 변환 확인 - 기본값을 y로 설정
    print("\n이 파일들을 가사 형식으로 변환하시겠습니까? (y/n, 기본값: y)")
    choice = input("> ").strip().lower()
    
    # 엔터 키 또는 'y'인 경우 진행
    if choice and choice != 'y':
        print("변환 취소")
        return
    
    print("\n변환 중...")
    
    try:
        # 임시 폴더 생성
        temp_output_dir = os.path.join(output_dir, "temp_images")
        os.makedirs(temp_output_dir, exist_ok=True)
        
        # 모든 PPT 파일 변환
        from lyricsslide_creator.ppt_converter import convert_ppt_files
        converted_files = convert_ppt_files(input_dir, temp_output_dir)
        
        # 변환 실패 시 종료
        if not converted_files:
            print("PPT 변환에 실패했습니다.")
            import shutil
            shutil.rmtree(temp_output_dir, ignore_errors=True)
            return
        
        # 타임스탬프 생성
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # 각 PPT 파일에 대해 개별 처리
        output_pptx_files = []
        
        for converted in converted_files:
            # 현재 PPT 파일의 출력 디렉토리
            ppt_output_dir = converted['output_dir']
            file_basename = converted['basename']
            
            # 이미지를 새 PPT로 변환
            from lyricsslide_creator.pptx_creator import create_presentation
            output_file = os.path.join(output_dir, f"{file_basename}_{timestamp}.pptx")
            
            try:
                create_presentation(output_file, ppt_output_dir, invert_colors=True)
                output_pptx_files.append(output_file)
                print(f"생성 완료: {output_file}")
            except Exception as e:
                print(f"변환 중 오류 발생: {str(e)}")
                continue
        
        if len(output_pptx_files) > 1:
            print(f"\n총 {len(output_pptx_files)}개의 PPT 파일이 생성되었습니다.")
        
        # 임시 폴더 정리
        import shutil
        shutil.rmtree(temp_output_dir, ignore_errors=True)
        
        print("\n변환이 완료되었습니다.")
        print(f"결과물은 다음 폴더에 저장되었습니다: {output_dir}")
        
    except Exception as e:
        import traceback
        print(f"변환 중 오류가 발생했습니다: {str(e)}")
        traceback.print_exc()
        
        # 임시 폴더 정리 시도
        try:
            import shutil
            shutil.rmtree(temp_output_dir, ignore_errors=True)
        except:
            pass

def main():
    """메인 실행 함수"""
    # 의존성 확인
    if not ensure_dependencies():
        print("필요한 패키지가 설치되지 않아 종료합니다.")
        return
    
    # 패키지 폴더 확인 및 생성
    folders_created, input_dir, output_dir = ensure_package_folders()
    
    # 폴더 안내 메시지
    if folders_created and is_packaged():
        print("\n=== 폴더 사용 안내 ===")
        print("1. 변환할 PPT 파일은 다음 폴더에 넣어주세요:")
        print(f"   {input_dir}")
        print("2. 생성된 모든 PPT 파일은 다음 폴더에서 찾을 수 있습니다:")
        print(f"   {output_dir}")
        print("3. 프로그램을 시작하기 전에 변환할 PPT 파일을 미리 폴더에 넣어두세요.")
    
    while True:
        print("\n=== lyricsSlide Creator ===")
        print("1. 가사 PPT 제작 (멜론 검색)")
        print("2. 악보 포함 가사 PPT 제작")
        print("0. 종료")
        
        print("\n원하는 기능을 선택하세요:", end=" ")
        choice = input().strip()
        
        if choice == "1":
            run_lyrics_ppt_creator()
        elif choice == "2":
            run_ppt_convert()
        elif choice == "0":
            print("프로그램을 종료합니다.")
            break
        else:
            print("올바른 번호를 입력해주세요.")

def cli_entry_point():
    """명령줄 도구의 진입점"""
    main()

if __name__ == "__main__":
    main()