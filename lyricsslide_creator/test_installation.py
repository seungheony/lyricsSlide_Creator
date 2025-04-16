#!/usr/bin/env python3
"""
패키지 설치 검증 스크립트
"""

import sys
import importlib
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class InstallationTester:
    """패키지 설치를 검증하는 클래스"""
    
    def __init__(self):
        # 필수 모듈 목록
        self.required_modules = ['pptx', 'PIL', 'pdf2image']
        
        # 플랫폼별 추가 모듈
        if sys.platform.startswith('win'):
            self.required_modules.append('comtypes')
            
        # 외부 의존성 목록
        self.external_dependencies = []
        if sys.platform.startswith('win'):
            self.external_dependencies.append(('Poppler', self._check_poppler_windows))
        else:
            self.external_dependencies.append(('Poppler', self._check_poppler_unix))
            
        self.external_dependencies.append(('LibreOffice', self._check_libreoffice))
    
    def _check_poppler_windows(self) -> bool:
        """Windows에서 Poppler 설치 여부를 확인합니다."""
        poppler_paths = [
            os.path.join(os.environ.get('USERPROFILE', ''), 'poppler', 'bin'),
            os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'poppler', 'bin'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'poppler', 'bin')
        ]
        
        for path in poppler_paths:
            if os.path.exists(os.path.join(path, 'pdftoppm.exe')):
                return True
        return False
    
    def _check_poppler_unix(self) -> bool:
        """Unix 계열 시스템에서 Poppler 설치 여부를 확인합니다."""
        from shutil import which
        return which('pdftoppm') is not None
    
    def _check_libreoffice(self) -> bool:
        """LibreOffice 설치 여부를 확인합니다."""
        from shutil import which
        
        if sys.platform.startswith('darwin'):  # macOS
            libreoffice_paths = [
                '/Applications/LibreOffice.app/Contents/MacOS/soffice',
                '/Applications/LibreOffice.app/Contents/MacOS/soffice.bin'
            ]
            return any(os.path.exists(path) for path in libreoffice_paths)
        elif sys.platform.startswith('win'):  # Windows
            program_files_paths = [
                os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
                os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')
            ]
            
            for base_path in program_files_paths:
                if os.path.exists(os.path.join(base_path, 'LibreOffice', 'program', 'soffice.exe')):
                    return True
                
                # 와일드카드 경로 확인
                import glob
                matching_paths = glob.glob(os.path.join(base_path, 'LibreOffice*', 'program', 'soffice.exe'))
                if matching_paths:
                    return True
            return False
        else:  # 기타 Unix 계열
            return which('libreoffice') is not None or which('soffice') is not None
    
    def test_imports(self) -> bool:
        """필요한 모듈을 임포트해서 패키지가 올바르게 설치되었는지 확인합니다."""
        all_ok = True
        
        print("\n📦 Python 패키지 확인:")
        for module in self.required_modules:
            try:
                importlib.import_module(module)
                print(f"✅ {module} 모듈을 성공적으로 임포트했습니다.")
            except ImportError as e:
                all_ok = False
                print(f"❌ {module} 모듈 임포트 실패: {e}")
        
        try:
            from lyricsslide_creator import __version__
            print(f"\n✅ lyricsslide-creator 버전 {__version__}이(가) 설치되었습니다.")
        except ImportError:
            all_ok = False
            print("\n❌ lyricsslide-creator 패키지를 임포트할 수 없습니다.")
        
        return all_ok
    
    def test_external_dependencies(self) -> bool:
        """외부 종속성이 설치되어 있는지 확인합니다."""
        all_ok = True
        
        print("\n🔧 외부 종속성 확인:")
        for name, check_func in self.external_dependencies:
            if check_func():
                print(f"✅ {name}가 설치되어 있습니다.")
            else:
                all_ok = False
                print(f"❌ {name}가 설치되어 있지 않습니다.")
        
        return all_ok
    
    def run_tests(self) -> bool:
        """모든 테스트를 실행합니다."""
        imports_ok = self.test_imports()
        dependencies_ok = self.test_external_dependencies()
        
        return imports_ok and dependencies_ok

def test_installation() -> bool:
    """패키지 설치 상태를 검증합니다."""
    tester = InstallationTester()
    return tester.run_tests()

if __name__ == "__main__":
    print("=== lyricsslide-creator 패키지 설치 검증 ===")
    if test_installation():
        print("\n✅ 축하합니다! 패키지가 성공적으로 설치되었습니다.")
        sys.exit(0)
    else:
        print("\n❌ 패키지 설치에 문제가 있습니다. 위 오류를 확인하세요.")
        sys.exit(1)