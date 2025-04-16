# utils.py

import subprocess
import sys
import os
import tempfile
import shutil
import platform
from pptx import Presentation
from pptx.dml.color import RGBColor

def install_package(package_name):
    """패키지를 설치합니다. (dependency_checker.py의 함수와 중복되므로 삭제 예정)"""
    try:
        print(f"패키지 '{package_name}'를 설치합니다...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"패키지 '{package_name}' 설치 완료.")
    except subprocess.CalledProcessError:
        print(f"패키지 '{package_name}' 설치에 실패했습니다. 수동으로 설치해 주십시오.")

def clear_directory(directory):
    """디렉토리를 비우거나 생성합니다."""
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):  # 하위 디렉토리 처리 추가
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"파일 삭제 중 오류 발생: {e}")
    else:
        os.makedirs(directory)
    print(f"'{directory}' 폴더를 정리하였습니다.")

def get_libreoffice_path():
    """운영체제에 맞는 LibreOffice 경로를 반환합니다."""
    if sys.platform.startswith('darwin'):  # macOS
        paths = [
            '/Applications/LibreOffice.app/Contents/MacOS/soffice',
            '/Applications/LibreOffice.app/Contents/MacOS/soffice.bin'
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return '/Applications/LibreOffice.app/Contents/MacOS/soffice'  # 기본값
        
    elif sys.platform.startswith('win'):  # Windows
        # 여러 가능한 설치 경로 확인
        program_files_paths = [
            os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
            os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')
        ]
        
        for base in program_files_paths:
            paths = [
                os.path.join(base, 'LibreOffice', 'program', 'soffice.exe'),
                os.path.join(base, 'LibreOffice*', 'program', 'soffice.exe')
            ]
            
            for path in paths:
                if '*' in path:
                    import glob
                    matches = glob.glob(path)
                    if matches:
                        return matches[0]
                elif os.path.exists(path):
                    return path
                    
        return os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 
                          'LibreOffice', 'program', 'soffice.exe')  # 기본값
    else:  # Linux 등
        from shutil import which
        soffice_path = which('soffice')
        if soffice_path:
            return soffice_path
        return 'libreoffice'  # 기본값

def convert_ppt_to_pptx(ppt_file):
    """PPT 파일을 PPTX로 변환합니다."""
    # LibreOffice 실행 파일 경로 설정
    libreoffice_path = get_libreoffice_path()

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
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"{ppt_file}를 PPTX로 변환 완료.")
        except subprocess.CalledProcessError as e:
            print(f"{ppt_file}를 PPTX로 변환 중 오류 발생: {e}")
            if e.stderr:
                print(f"오류 메시지: {e.stderr}")
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
    """슬라이드 배경을 흰색으로 설정합니다."""
    try:
        prs = Presentation(pptx_file)
        for slide in prs.slides:
            background = slide.background
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(255, 255, 255)  # 흰색
        prs.save(modified_pptx_file)
        print(f"슬라이드 배경을 흰색으로 변경하였습니다: {modified_pptx_file}")
    except Exception as e:
        print(f"슬라이드 배경 변경 중 오류 발생: {e}")
        raise

def check_system_dependencies():
    """LibreOffice와 Poppler와 같은 시스템 의존성을 확인합니다."""
    dependencies_ok = True
    
    # LibreOffice 확인
    if not os.path.exists(get_libreoffice_path()):
        dependencies_ok = False
        print("⚠️ LibreOffice가 설치되어 있지 않거나 기본 경로에 없습니다.")
        print("  다운로드: https://www.libreoffice.org/download/download/")
    else:
        print("✅ LibreOffice가 설치되어 있습니다.")
    
    # Poppler 확인
    if sys.platform.startswith('win'):
        poppler_ok = False
        poppler_paths = [
            os.path.join(os.environ.get('USERPROFILE', ''), 'poppler', 'bin'),
            os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'poppler', 'bin'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'poppler', 'bin')
        ]
        
        for path in poppler_paths:
            if os.path.exists(os.path.join(path, 'pdftoppm.exe')):
                poppler_ok = True
                break
                
        if not poppler_ok:
            dependencies_ok = False
            print("⚠️ Windows에서는 Poppler가 필요합니다.")
            print("  다운로드: https://github.com/oschwartz10612/poppler-windows/releases")
    else:
        from shutil import which
        if which('pdftoppm') is None:
            dependencies_ok = False
            if sys.platform.startswith('darwin'):  # macOS
                print("⚠️ Poppler가 설치되어 있지 않습니다.")
                print("  설치 명령어: brew install poppler")
            else:  # Linux
                print("⚠️ Poppler가 설치되어 있지 않습니다.")
                print("  설치 명령어: sudo apt-get install poppler-utils (Debian/Ubuntu)")
                print("  또는: sudo yum install poppler-utils (Red Hat/Fedora)")
        else:
            print("✅ Poppler가 설치되어 있습니다.")
    
    return dependencies_ok