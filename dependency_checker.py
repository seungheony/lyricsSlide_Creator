# dependency_checker.py

import sys
import subprocess
import os
from utils import install_package

def check_python_packages():
    missing_packages = []
    try:
        import PIL
    except ImportError:
        missing_packages.append('Pillow')

    try:
        import pptx
    except ImportError:
        missing_packages.append('python-pptx')

    try:
        import pdf2image
    except ImportError:
        missing_packages.append('pdf2image')

    if missing_packages:
        print("다음 Python 패키지가 설치되어 있지 않습니다:")
        for pkg in missing_packages:
            print(f"- {pkg}")

        # 자동 설치 여부를 사용자에게 묻습니다.
        print("부족한 패키지를 설치하려면 엔터 키를 누르십시오. 취소하려면 'q'를 입력하고 엔터 키를 누르십시오.")
        choice = input().lower().strip()
        if choice == 'q':
            print("프로그램을 종료합니다.")
            return False
        else:
            for pkg in missing_packages:
                install_package(pkg)
            # 패키지 설치 후 다시 검사
            return check_python_packages()
    else:
        print("모든 필요한 Python 패키지가 설치되어 있습니다.")
        return True

def check_libreoffice():
    if sys.platform.startswith('darwin'):
        # macOS 환경
        libreoffice_path = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    elif sys.platform.startswith('win'):
        # Windows 환경
        libreoffice_path = r'C:\Program Files\LibreOffice\program\soffice.exe'
    else:
        # 기타 Unix 계열 시스템
        libreoffice_path = 'libreoffice'

    # LibreOffice 실행 파일 존재 여부 확인
    if sys.platform.startswith('darwin') or sys.platform.startswith('win'):
        if os.path.exists(libreoffice_path):
            print(f"LibreOffice가 설치되어 있습니다: {libreoffice_path}")
            return True
        else:
            print("LibreOffice가 설치되어 있지 않거나 기본 경로에 없습니다.")
            print("LibreOffice를 설치하거나 경로를 확인하십시오.")
            print("다운로드 링크: https://www.libreoffice.org/download/download/")
            return False
    else:
        # Unix 계열 시스템에서는 'which' 명령으로 확인
        from shutil import which
        if which('libreoffice') is not None or which('soffice') is not None:
            print("LibreOffice가 설치되어 있습니다.")
            return True
        else:
            print("LibreOffice가 설치되어 있지 않습니다.")
            print("LibreOffice를 설치하십시오.")
            print("다운로드 링크: https://www.libreoffice.org/download/download/")
            return False

def check_poppler():
    # Poppler 설치 여부 확인
    from shutil import which
    if which('pdftoppm') is not None:
        print("Poppler가 설치되어 있습니다.")
        return True
    else:
        print("Poppler가 설치되어 있지 않습니다.")
        if sys.platform.startswith('darwin'):
            print("다음 명령어를 실행하여 Poppler를 설치하십시오:")
            print("brew install poppler")
        elif sys.platform.startswith('linux'):
            print("다음 명령어를 실행하여 Poppler를 설치하십시오:")
            print("sudo apt-get install poppler-utils  # Debian/Ubuntu 계열")
            print("sudo yum install poppler-utils      # Red Hat 계열")
        else:
            print("Poppler 설치 방법을 확인하십시오: https://poppler.freedesktop.org/")
        return False

def check_dependencies():
    python_packages_ok = check_python_packages()
    libreoffice_ok = check_libreoffice()
    poppler_ok = check_poppler()

    if python_packages_ok and libreoffice_ok and poppler_ok:
        print("모든 종속성이 설치되어 있습니다.")
        return True
    else:
        print("필요한 종속성이 설치되어 있지 않습니다. 위의 안내에 따라 설치를 완료한 후 다시 시도하십시오.")
        return False