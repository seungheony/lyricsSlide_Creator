#!/usr/bin/env python3
"""
lyricsSlide_Creator 실행기 - 모든 설정 및 종속성을 자동으로 처리합니다.
"""

import os
import sys
import platform
import subprocess
import tempfile
import shutil
from pathlib import Path

# 프로젝트 root 경로
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def ensure_venv():
    """가상환경을 확인하고 필요시 생성합니다."""
    venv_dir = os.path.join(ROOT_DIR, "venv")
    
    # 가상환경 존재 확인
    if not os.path.exists(venv_dir):
        print("가상환경이 없습니다. 새로 생성합니다...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
            print("가상환경이 생성되었습니다.")
        except Exception as e:
            print(f"가상환경 생성 중 오류 발생: {e}")
            return False
    
    # 가상환경의 Python/pip 경로
    if platform.system() == "Windows":
        python_path = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        python_path = os.path.join(venv_dir, "bin", "python")
        pip_path = os.path.join(venv_dir, "bin", "pip")
    
    # 가상환경 Python이 없는 경우 재생성
    if not os.path.exists(python_path):
        print("가상환경이 손상되었습니다. 재생성합니다...")
        shutil.rmtree(venv_dir, ignore_errors=True)
        return ensure_venv()
    
    return python_path, pip_path

def ensure_package_installed():
    """패키지가 설치되어 있는지 확인하고 필요시 설치합니다."""
    python_path, pip_path = ensure_venv()
    if not python_path:
        return False
    
    # 패키지 설치
    print("필요한 패키지를 확인합니다...")
    try:
        # pip 업그레이드
        subprocess.check_call([pip_path, "install", "--upgrade", "pip"])
        
        # 패키지 설치
        subprocess.check_call([pip_path, "install", "-e", ROOT_DIR])
        print("모든 패키지가 설치되었습니다.")
        return True
    except Exception as e:
        print(f"패키지 설치 중 오류 발생: {e}")
        return False

def ensure_external_dependencies():
    """외부 종속성(LibreOffice, Poppler)을 확인하고 필요시 설치합니다."""
    if platform.system() == "Windows":
        return ensure_windows_dependencies()
    elif platform.system() == "Darwin":  # macOS
        return ensure_macos_dependencies()
    else:
        print("현재 시스템은 지원되지 않습니다. Windows 또는 macOS에서 실행해주세요.")
        return False

def ensure_windows_dependencies():
    """Windows 환경에서 필요한 외부 종속성을 확인합니다."""
    # LibreOffice 확인
    libreoffice_paths = [
        os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'LibreOffice', 'program', 'soffice.exe'),
        os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'LibreOffice', 'program', 'soffice.exe')
    ]
    
    libreoffice_installed = any(os.path.exists(path) for path in libreoffice_paths)
    
    if not libreoffice_installed:
        print("\nLibreOffice가 설치되어 있지 않습니다.")
        print("LibreOffice 설치 파일을 다운로드하시겠습니까? (y/n)")
        if input().strip().lower() == 'y':
            print("LibreOffice 설치 파일을 다운로드합니다...")
            # 다운로드 URL은 변경될 수 있으므로 최신 URL을 사용해야 합니다
            download_url = "https://download.documentfoundation.org/libreoffice/stable/7.5.4/win/x86_64/LibreOffice_7.5.4_Win_x86-64.msi"
            download_path = os.path.join(tempfile.gettempdir(), "LibreOffice_Setup.msi")
            
            try:
                import urllib.request
                urllib.request.urlretrieve(download_url, download_path)
                
                print("LibreOffice 설치를 시작합니다...")
                subprocess.call(["msiexec", "/i", download_path, "/qb"])
                print("LibreOffice 설치가 완료되었습니다.")
            except Exception as e:
                print(f"LibreOffice 다운로드 또는 설치 중 오류 발생: {e}")
                print("수동으로 다음 링크에서 설치하세요: https://www.libreoffice.org/download/download/")
    else:
        print("LibreOffice가 이미 설치되어 있습니다.")
    
    # Poppler 확인
    poppler_bin = "C:\\poppler\\bin"
    pdftoppm_path = os.path.join(poppler_bin, "pdftoppm.exe")
    
    if not os.path.exists(pdftoppm_path):
        print("\nPoppler가 설치되어 있지 않습니다.")
        print("Poppler를 다운로드하고 설치하시겠습니까? (y/n)")
        if input().strip().lower() == 'y':
            import urllib.request
            import zipfile
            
            print("Poppler를 다운로드합니다...")
            # 다운로드 URL은 변경될 수 있으므로 최신 URL을 사용해야 합니다
            download_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.11.0-0/Release-23.11.0-0.zip"
            download_path = os.path.join(tempfile.gettempdir(), "poppler.zip")
            
            try:
                urllib.request.urlretrieve(download_url, download_path)
                
                print("Poppler 압축을 해제합니다...")
                if not os.path.exists("C:\\poppler"):
                    os.makedirs("C:\\poppler")
                
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall("C:\\poppler")
                
                # PATH 환경 변수에 추가
                if os.path.exists(poppler_bin):
                    if poppler_bin not in os.environ.get('PATH', ''):
                        os.environ['PATH'] += os.pathsep + poppler_bin
                    print("Poppler가 설치되었습니다. 환경변수 PATH에 추가되었습니다.")
                else:
                    print("Poppler 설치 중 오류가 발생했습니다.")
                    return False
            except Exception as e:
                print(f"Poppler 다운로드 또는 설치 중 오류 발생: {e}")
                print("수동으로 다음 링크에서 설치하세요: https://github.com/oschwartz10612/poppler-windows/releases")
                return False
    else:
        print("Poppler가 이미 설치되어 있습니다.")
        # PATH에 추가
        if poppler_bin not in os.environ.get('PATH', ''):
            os.environ['PATH'] += os.pathsep + poppler_bin
    
    return True

def ensure_macos_dependencies():
    """macOS 환경에서 필요한 외부 종속성을 확인합니다."""
    # Homebrew 확인
    brew_path = None
    for path in ["/usr/local/bin/brew", "/opt/homebrew/bin/brew"]:
        if os.path.exists(path):
            brew_path = path
            break
    
    if not brew_path:
        print("\nHomebrew가 설치되어 있지 않습니다.")
        print("Homebrew를 설치하시겠습니까? (y/n)")
        if input().strip().lower() == 'y':
            print("Homebrew를 설치합니다...")
            try:
                install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                subprocess.call(install_cmd, shell=True)
                print("Homebrew 설치가 완료되었습니다.")
                # 설치 후 경로 재확인
                for path in ["/usr/local/bin/brew", "/opt/homebrew/bin/brew"]:
                    if os.path.exists(path):
                        brew_path = path
                        break
            except Exception as e:
                print(f"Homebrew 설치 중 오류 발생: {e}")
                print("수동으로 다음 명령어로 설치하세요: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
                return False
    
    if not brew_path:
        print("Homebrew 설치에 실패했습니다.")
        return False
    
    # LibreOffice 확인
    libreoffice_path = "/Applications/LibreOffice.app"
    if not os.path.exists(libreoffice_path):
        print("\nLibreOffice가 설치되어 있지 않습니다.")
        print("LibreOffice를 설치하시겠습니까? (y/n)")
        if input().strip().lower() == 'y':
            print("LibreOffice를 설치합니다...")
            try:
                subprocess.check_call([brew_path, "install", "--cask", "libreoffice"])
                print("LibreOffice 설치가 완료되었습니다.")
            except Exception as e:
                print(f"LibreOffice 설치 중 오류 발생: {e}")
                print("수동으로 다음 명령어로 설치하세요: brew install --cask libreoffice")
                return False
    else:
        print("LibreOffice가 이미 설치되어 있습니다.")
    
    # Poppler 확인
    import shutil
    if shutil.which("pdftoppm") is None:
        print("\nPoppler가 설치되어 있지 않습니다.")
        print("Poppler를 설치하시겠습니까? (y/n)")
        if input().strip().lower() == 'y':
            print("Poppler를 설치합니다...")
            try:
                subprocess.check_call([brew_path, "install", "poppler"])
                print("Poppler 설치가 완료되었습니다.")
            except Exception as e:
                print(f"Poppler 설치 중 오류 발생: {e}")
                print("수동으로 다음 명령어로 설치하세요: brew install poppler")
                return False
    else:
        print("Poppler가 이미 설치되어 있습니다.")
    
    return True

def run_program():
    """모든 설정을 마친 후 프로그램을 실행합니다."""
    python_path, _ = ensure_venv()
    if not python_path:
        print("가상환경 설정에 실패했습니다.")
        return False
    
    # lyricsSlide_Creator 실행
    print("\n프로그램을 실행합니다...")
    
    # 프로그램 진입점 모듈 경로
    main_module = "lyricsslide_creator.main"
    
    # 가상환경의 Python으로 모듈 실행
    try:
        subprocess.call([python_path, "-m", main_module])
        return True
    except Exception as e:
        print(f"프로그램 실행 중 오류 발생: {e}")
        return False

def main():
    """메인 함수"""
    print("=== lyricsSlide_Creator ===")
    
    # 1. 가상환경 확인
    if not ensure_venv():
        print("가상환경 설정에 실패했습니다.")
        sys.exit(1)
    
    # 2. 패키지 설치
    if not ensure_package_installed():
        print("패키지 설치에 실패했습니다.")
        sys.exit(1)
    
    # 3. 외부 종속성 확인
    if not ensure_external_dependencies():
        print("외부 종속성 설정에 실패했습니다.")
        print("프로그램은 실행할 수 있지만 일부 기능이 제한될 수 있습니다.")
    
    # 4. 프로그램 실행
    if not run_program():
        print("프로그램 실행에 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()