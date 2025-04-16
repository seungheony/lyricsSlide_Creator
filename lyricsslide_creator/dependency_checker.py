"""
필요한 종속성을 확인하고 설치하는 모듈
"""

import sys
import subprocess
import os
import importlib
import platform
from shutil import which
import logging
from typing import List, Dict, Optional, Tuple, Any

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger("dependency_checker")

class DependencyChecker:
    """필요한 종속성을 확인하고 설치하는 클래스"""
    
    def __init__(self, verbose: bool = True, include_dev_tools: bool = False):
        self.verbose = verbose
        
        # 기본 패키지
        self.required_packages = ['python-pptx', 'Pillow', 'pdf2image']
        
        # 플랫폼별 추가 패키지
        if sys.platform.startswith('win'):
            # Windows에서만 필요한 패키지
            self.required_packages.append('comtypes')
        
        # 개발 도구 패키지 (package_build 모드에서 필요)
        self.dev_packages = ['setuptools', 'wheel', 'twine']
        
        if include_dev_tools:
            self.required_packages.extend(self.dev_packages)
    
    def log(self, message: str, level: str = "info") -> None:
        """로깅 메시지를 출력합니다."""
        if not self.verbose:
            return
            
        if level == "info":
            logger.info(message)
        elif level == "warning":
            logger.warning(message)
        elif level == "error":
            logger.error(message)
    
    def install_package(self, package_name: str) -> bool:
        """패키지를 설치합니다."""
        self.log(f"{package_name} 패키지를 설치합니다...")
        
        # 여러 설치 방법 시도
        methods = [
            # 먼저 사용자 공간에 설치 시도
            [sys.executable, "-m", "pip", "install", "--user", package_name],
            # 그 다음 일반 설치 시도
            [sys.executable, "-m", "pip", "install", package_name],
            # 마지막으로 시스템 제한을 무시하는 방법 시도 (위험!)
            [sys.executable, "-m", "pip", "install", "--break-system-packages", package_name]
        ]
        
        for method in methods:
            try:
                subprocess.check_call(method, stderr=subprocess.PIPE, 
                                     stdout=subprocess.PIPE if not self.verbose else None)
                self.log(f"{package_name} 패키지가 성공적으로 설치되었습니다.")
                return True
            except subprocess.CalledProcessError:
                continue
            except Exception as e:
                self.log(f"설치 방법 {' '.join(method)} 실패: {e}", "warning")
                continue
        
        self.log(f"{package_name} 패키지 설치에 실패했습니다.", "error")
        return False
    
    def check_python_packages(self) -> bool:
        """Python 패키지 종속성을 확인합니다."""
        missing_packages = []
        for package in self.required_packages:
            try:
                # 각 패키지별 임포트 방식 처리
                if package == 'python-pptx':
                    importlib.import_module('pptx')
                elif package == 'Pillow':
                    importlib.import_module('PIL')
                elif package == 'pdf2image':
                    importlib.import_module('pdf2image')
                else:
                    importlib.import_module(package.lower())
                self.log(f"{package} 패키지가 이미 설치되어 있습니다.")
            except ImportError:
                self.log(f"{package} 패키지가 설치되어 있지 않습니다.", "warning")
                missing_packages.append(package)
        
        # 누락된 패키지 설치 시도
        for package in missing_packages:
            if not self.install_package(package):
                return False
        
        return True
    
    def check_libreoffice(self) -> bool:
        """LibreOffice 설치 여부를 확인합니다."""
        self.log("LibreOffice 확인 중...")
        libreoffice_installed = False
        
        if sys.platform.startswith('darwin'):  # macOS
            libreoffice_paths = [
                '/Applications/LibreOffice.app/Contents/MacOS/soffice',
                '/Applications/LibreOffice.app/Contents/MacOS/soffice.bin'
            ]
            for path in libreoffice_paths:
                if os.path.exists(path):
                    self.log(f"LibreOffice가 설치되어 있습니다: {path}")
                    libreoffice_installed = True
                    break
                    
        elif sys.platform.startswith('win'):  # Windows
            # 여러 가능한 설치 경로 확인
            program_files_paths = [
                os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
                os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')
            ]
            
            for base_path in program_files_paths:
                libreoffice_paths = [
                    os.path.join(base_path, 'LibreOffice', 'program', 'soffice.exe'),
                    os.path.join(base_path, 'LibreOffice*', 'program', 'soffice.exe')
                ]
                
                for path_pattern in libreoffice_paths:
                    # 와일드카드가 포함된 경로인 경우 glob 사용
                    if '*' in path_pattern:
                        import glob
                        matching_paths = glob.glob(path_pattern)
                        if matching_paths:
                            self.log(f"LibreOffice가 설치되어 있습니다: {matching_paths[0]}")
                            libreoffice_installed = True
                            break
                    elif os.path.exists(path_pattern):
                        self.log(f"LibreOffice가 설치되어 있습니다: {path_pattern}")
                        libreoffice_installed = True
                        break
                
                if libreoffice_installed:
                    break
                    
        else:  # 기타 Unix 계열
            if which('libreoffice') is not None or which('soffice') is not None:
                self.log("LibreOffice가 설치되어 있습니다.")
                libreoffice_installed = True
        
        if not libreoffice_installed:
            self.log("LibreOffice가 설치되어 있지 않거나 기본 경로에 없습니다.", "warning")
            self.log("LibreOffice를 설치하거나 경로를 확인하십시오.", "warning")
            self.log("다운로드 링크: https://www.libreoffice.org/download/download/", "info")
            return False
            
        return True
        
    def check_poppler(self) -> bool:
        """Poppler 설치 여부를 확인합니다."""
        self.log("Poppler 확인 중...")
        poppler_installed = False
        
        if sys.platform.startswith('win'):
            # Windows에서는 poppler-windows 패키지 사용 여부 확인
            poppler_paths = [
                os.path.join(os.environ.get('USERPROFILE', ''), 'poppler', 'bin'),
                os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'poppler', 'bin'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'poppler', 'bin')
            ]
            
            for path in poppler_paths:
                if os.path.exists(os.path.join(path, 'pdftoppm.exe')):
                    self.log(f"Poppler가 설치되어 있습니다: {path}")
                    poppler_installed = True
                    # 환경 변수에 poppler 경로 추가
                    if path not in os.environ.get('PATH', ''):
                        os.environ['PATH'] += os.pathsep + path
                    break
            
            if not poppler_installed:
                self.log("Windows에서는 poppler-windows를 수동으로 설치해야 합니다.", "warning")
                self.log("다운로드 링크: https://github.com/oschwartz10612/poppler-windows/releases", "info")
                self.log("다운로드 후 압축을 풀고 환경변수 PATH에 bin 폴더를 추가하세요.", "info")
                return False
        else:
            # macOS/Linux에서는 pdftoppm 명령어 확인
            if which('pdftoppm') is not None:
                self.log("Poppler가 설치되어 있습니다.")
                poppler_installed = True
            else:
                self.log("Poppler가 설치되어 있지 않습니다.", "warning")
                if sys.platform.startswith('darwin'):
                    self.log("다음 명령어를 실행하여 Poppler를 설치하십시오:", "info")
                    self.log("brew install poppler", "info")
                elif sys.platform.startswith('linux'):
                    self.log("다음 명령어를 실행하여 Poppler를 설치하십시오:", "info")
                    self.log("sudo apt-get install poppler-utils  # Debian/Ubuntu 계열", "info")
                    self.log("sudo yum install poppler-utils      # Red Hat 계열", "info")
                return False
                
        return True
    
    def check_all(self) -> bool:
        """모든 종속성을 확인합니다."""
        self.log("=== 종속성 확인 시작 ===")
        
        # Python 패키지 확인
        if not self.check_python_packages():
            return False
            
        # LibreOffice 확인
        if not self.check_libreoffice():
            return False
            
        # Poppler 확인
        if not self.check_poppler():
            return False
            
        self.log("=== 모든 종속성이 설치되어 있습니다 ===")
        return True
        
    def check_dev_tools(self) -> bool:
        """개발 도구(setuptools, wheel 등)가 설치되어 있는지 확인합니다."""
        self.log("=== 개발 도구 확인 시작 ===")
        
        missing_packages = []
        for package in self.dev_packages:
            try:
                importlib.import_module(package)
                self.log(f"{package} 패키지가 이미 설치되어 있습니다.")
            except ImportError:
                self.log(f"{package} 패키지가 설치되어 있지 않습니다.", "warning")
                missing_packages.append(package)
        
        # 누락된 패키지 설치 시도
        for package in missing_packages:
            if not self.install_package(package):
                return False
                
        self.log("=== 모든 개발 도구가 설치되어 있습니다 ===")
        return True

def check_dependencies(verbose: bool = True) -> bool:
    """필요한 종속성이 설치되어 있는지 확인합니다."""
    checker = DependencyChecker(verbose=verbose)
    return checker.check_all()

def check_setup_dependencies(verbose: bool = True) -> bool:
    """setuptools 등 패키지 설치에 필요한 도구를 확인합니다."""
    checker = DependencyChecker(verbose=verbose)
    return checker.check_dev_tools()

def check_all_dependencies(verbose: bool = True) -> bool:
    """모든 종속성(실행 + 개발 도구)을 확인합니다."""
    checker = DependencyChecker(verbose=verbose, include_dev_tools=True)
    return checker.check_all()

if __name__ == "__main__":
    # 명령줄 인수에 따라 다른 모드로 실행
    import argparse
    parser = argparse.ArgumentParser(description='패키지 종속성 검사 도구')
    parser.add_argument('--dev', action='store_true', help='개발 도구(setuptools 등) 검사')
    parser.add_argument('--all', action='store_true', help='모든 종속성 검사')
    args = parser.parse_args()
    
    if args.dev:
        sys.exit(0 if check_setup_dependencies() else 1)
    elif args.all:
        sys.exit(0 if check_all_dependencies() else 1)
    else:
        sys.exit(0 if check_dependencies() else 1)