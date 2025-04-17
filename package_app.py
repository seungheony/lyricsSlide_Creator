#!/usr/bin/env python3
"""
LyricsSlide Creator 패키징 자동화 스크립트
macOS 및 Windows에서 실행 가능한 배포 패키지를 자동으로 생성합니다.
"""

import os
import sys
import platform
import subprocess
import shutil
import tempfile
from pathlib import Path

# 색상 코드 (출력 강조용)
GREEN = "\033[92m" if sys.platform != "win32" else ""
YELLOW = "\033[93m" if sys.platform != "win32" else ""
RED = "\033[91m" if sys.platform != "win32" else ""
RESET = "\033[0m" if sys.platform != "win32" else ""

# 프로젝트 루트 경로 설정 (스크립트 위치 기준)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def print_step(message):
    """단계 메시지 출력"""
    print(f"\n{GREEN}=== {message} ==={RESET}")

def print_warning(message):
    """경고 메시지 출력"""
    print(f"{YELLOW}경고: {message}{RESET}")

def print_error(message):
    """오류 메시지 출력"""
    print(f"{RED}오류: {message}{RESET}")

def run_command(command, shell=False, cwd=None):
    """명령어 실행 및 결과 반환"""
    try:
        if cwd is None:
            cwd = PROJECT_ROOT
            
        result = subprocess.run(
            command, 
            shell=shell, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"명령어 실행 실패: {' '.join(command) if not shell else command}")
        print(f"오류 메시지: {e.stderr}")
        return False, e.stderr

def create_resources_folder():
    """리소스 폴더 생성 및 기본 아이콘 생성"""
    print_step("리소스 폴더 설정")
    
    # 리소스 폴더 생성
    resources_dir = os.path.join(PROJECT_ROOT, "resources")
    os.makedirs(resources_dir, exist_ok=True)
    
    # 기본 아이콘 파일 생성 (아이콘이 없는 경우)
    icon_path_win = os.path.join(resources_dir, "icon.ico")
    icon_path_mac = os.path.join(resources_dir, "icon.icns")
    
    # 아이콘 생성 전 필요한 Pillow 패키지 설치 시도
    try:
        import importlib
        try:
            importlib.import_module('PIL')
            print("Pillow 패키지가 이미 설치되어 있습니다.")
        except ImportError:
            print("Pillow 패키지 설치 중...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    except Exception as e:
        print_warning(f"Pillow 설치 실패: {e}. 아이콘 생성을 건너뜁니다.")
        return True
        
    # 이제 PIL 임포트 시도
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print_warning("Pillow 패키지를 임포트할 수 없습니다. 기본 아이콘 생성을 건너뜁니다.")
        return True
    
    if not os.path.exists(icon_path_win) and platform.system() == "Windows":
        print("Windows용 기본 아이콘 생성 중...")
        try:
            img = Image.new('RGBA', (256, 256), color=(73, 109, 137, 255))
            d = ImageDraw.Draw(img)
            d.text((20, 128), "LyricsSlide", fill=(255, 255, 255))
            img.save(icon_path_win)
            print(f"기본 아이콘 생성 완료: {icon_path_win}")
        except Exception as e:
            print_warning(f"아이콘 생성 실패. 계속 진행합니다: {e}")
    
    if not os.path.exists(icon_path_mac) and platform.system() == "Darwin":
        print("macOS용 기본 아이콘 생성 중...")
        try:
            img = Image.new('RGBA', (1024, 1024), color=(73, 109, 137, 255))
            d = ImageDraw.Draw(img)
            d.text((100, 512), "LyricsSlide", fill=(255, 255, 255))
            img.save(os.path.join(resources_dir, "icon.png"))
            print(f"기본 아이콘 생성 완료: {os.path.join(resources_dir, 'icon.png')}")
        except Exception as e:
            print_warning(f"아이콘 생성 실패. 계속 진행합니다: {e}")
    
    return True

def create_spec_file():
    """PyInstaller 스펙 파일 생성"""
    print_step("PyInstaller 스펙 파일 생성")
    
    spec_content = """# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# 프로젝트 경로 설정
project_root = os.path.abspath(SPECPATH)
src_path = os.path.join(project_root, 'lyricsslide_creator')

# 실행 파일 이름 설정
if sys.platform.startswith('win'):
    exe_name = 'lyrics_slide.exe'
    icon_file = os.path.join(project_root, 'resources', 'icon.ico')
else:
    exe_name = 'lyrics_slide'
    icon_file = os.path.join(project_root, 'resources', 'icon.icns')
    if not os.path.exists(icon_file):
        icon_file = os.path.join(project_root, 'resources', 'icon.png')

# 파일 목록 설정 (패키지에 포함될 추가 파일)
add_files = [
    (os.path.join(project_root, 'requirements.txt'), '.'),
    (os.path.join(project_root, 'README.md'), '.'),
]

# 실행할 메인 스크립트
main_script = os.path.join(src_path, 'main.py')

a = Analysis(
    [main_script],
    pathex=[project_root],
    binaries=[],
    datas=add_files,
    hiddenimports=[
        'PIL', 
        'pdf2image', 
        'requests', 
        'bs4',
        'pptx',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file if os.path.exists(icon_file) else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='lyrics_slide',
)

# macOS용 앱 번들 생성
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='LyricsSlide.app',
        icon=icon_file if os.path.exists(icon_file) else None,
        bundle_identifier='com.lyricsslide.app',
        info_plist={
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': 'True',
        },
    )
"""
    
    spec_file_path = os.path.join(PROJECT_ROOT, "lyrics_slide.spec")
    with open(spec_file_path, "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print(f"스펙 파일 생성 완료: {spec_file_path}")
    return True

def setup_virtual_environment():
    """가상 환경 설정 및 필요한 패키지 설치"""
    print_step("가상 환경 설정")
    
    venv_dir = os.path.join(PROJECT_ROOT, "build_env")
    
    # 기존 가상 환경 제거 (있는 경우)
    if os.path.exists(venv_dir):
        print("기존 가상 환경 제거 중...")
        try:
            shutil.rmtree(venv_dir, ignore_errors=True)
        except Exception as e:
            print_warning(f"가상 환경 제거 중 오류: {e}. 계속 진행합니다.")
    
    # 가상 환경 생성
    print("새 가상 환경 생성 중...")
    success, _ = run_command([sys.executable, "-m", "venv", venv_dir])
    if not success:
        print_error("가상 환경 생성 실패")
        return False
    
    # 플랫폼에 맞는 파이썬 및 pip 경로 설정
    if platform.system() == "Windows":
        python_path = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        python_path = os.path.join(venv_dir, "bin", "python")
        pip_path = os.path.join(venv_dir, "bin", "pip")
    
    # pip 업그레이드
    print("pip 업그레이드 중...")
    success, _ = run_command([pip_path, "install", "--upgrade", "pip"])
    if not success:
        print_warning("pip 업그레이드 실패. 계속 진행합니다.")
    
    # 필요한 패키지 설치
    print("필요한 패키지 설치 중...")
    
    # PyInstaller 설치
    success, _ = run_command([pip_path, "install", "pyinstaller"])
    if not success:
        print_error("PyInstaller 설치 실패")
        return False
    
    # requirements.txt 절대 경로로 지정
    req_path = os.path.join(PROJECT_ROOT, "requirements.txt")
    if not os.path.exists(req_path):
        print_error(f"requirements.txt 파일을 찾을 수 없습니다: {req_path}")
        print("기본 종속성만 설치합니다.")
        
        # 기본 종속성 직접 설치
        for pkg in ["python-pptx", "Pillow", "pdf2image", "requests", "beautifulsoup4"]:
            print(f"{pkg} 설치 중...")
            success, _ = run_command([pip_path, "install", pkg])
            if not success:
                print_warning(f"{pkg} 설치 실패. 계속 진행합니다.")
    else:
        success, _ = run_command([pip_path, "install", "-r", req_path])
        if not success:
            print_error("종속성 패키지 설치 실패")
            return False
    
    # PIL 설치 (아이콘 생성용)
    success, _ = run_command([pip_path, "install", "pillow"])
    if not success:
        print_warning("Pillow 설치 실패. 계속 진행합니다.")
    
    return python_path, pip_path

def build_for_macos(python_path):
    """macOS용 애플리케이션 빌드"""
    print_step("macOS용 애플리케이션 빌드")
    
    # 기존 빌드 디렉토리 정리
    build_dir = os.path.join(PROJECT_ROOT, "build")
    dist_dir = os.path.join(PROJECT_ROOT, "dist")
    
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir, ignore_errors=True)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir, ignore_errors=True)
    
    # PyInstaller 실행
    print("PyInstaller로 빌드 중...")
    spec_path = os.path.join(PROJECT_ROOT, "lyrics_slide.spec")
    success, _ = run_command([python_path, "-m", "PyInstaller", spec_path])
    if not success:
        print_error("PyInstaller 빌드 실패")
        return False
    
    # DMG 생성
    print("DMG 파일 생성 중...")
    dmg_dir = os.path.join(PROJECT_ROOT, "dist", "dmg")
    os.makedirs(dmg_dir, exist_ok=True)
    
    app_path = os.path.join(PROJECT_ROOT, "dist", "lyrics_slide", "LyricsSlide.app")
    if os.path.exists(app_path):
        shutil.copytree(app_path, os.path.join(dmg_dir, "LyricsSlide.app"), dirs_exist_ok=True)
    else:
        # 앱 번들이 생성되지 않은 경우 일반 폴더 복사
        folder_path = os.path.join(PROJECT_ROOT, "dist", "lyrics_slide")
        if os.path.exists(folder_path):
            shutil.copytree(folder_path, os.path.join(dmg_dir, "LyricsSlide"), dirs_exist_ok=True)
    
    # DMG 생성 명령 실행
    dmg_path = os.path.join(PROJECT_ROOT, "dist", "LyricsSlide_Creator.dmg")
    success, _ = run_command([
        "hdiutil", "create", 
        "-volname", "LyricsSlide Creator", 
        "-srcfolder", dmg_dir, 
        "-ov", "-format", "UDZO",
        dmg_path
    ])
    
    if not success:
        print_warning("DMG 파일 생성 실패. 실행 가능한 폴더가 생성되었습니다.")
        print(f"dist/lyrics_slide 폴더에서 애플리케이션을 찾을 수 있습니다.")
        return True  # 실행 파일은 생성됨
    
    print(f"DMG 파일 생성 완료: {dmg_path}")
    return True

def build_for_windows(python_path):
    """Windows용 애플리케이션 빌드"""
    print_step("Windows용 애플리케이션 빌드")
    
    # 기존 빌드 디렉토리 정리
    build_dir = os.path.join(PROJECT_ROOT, "build")
    dist_dir = os.path.join(PROJECT_ROOT, "dist")
    
    if os.path.exists(dist_dir):
        try:
            shutil.rmtree(dist_dir, ignore_errors=True)
        except Exception as e:
            print_warning(f"dist 폴더 제거 중 오류: {e}. 계속 진행합니다.")
    if os.path.exists(build_dir):
        try:
            shutil.rmtree(build_dir, ignore_errors=True)
        except Exception as e:
            print_warning(f"build 폴더 제거 중 오류: {e}. 계속 진행합니다.")
    
    # PyInstaller 실행
    print("PyInstaller로 빌드 중...")
    spec_path = os.path.join(PROJECT_ROOT, "lyrics_slide.spec")
    success, _ = run_command([python_path, "-m", "PyInstaller", spec_path])
    if not success:
        print_error("PyInstaller 빌드 실패")
        return False
    
    # 설치 프로그램 스크립트 생성
    print("NSIS 설치 스크립트 생성 중...")
    nsis_script = """; NSIS 설치 스크립트
Name "LyricsSlide Creator"
OutFile "dist\\LyricsSlide_Creator_Setup.exe"
InstallDir "$PROGRAMFILES\\LyricsSlide Creator"
Section ""
  SetOutPath "$INSTDIR"
  File /r "dist\\lyrics_slide\\*.*"
  CreateDirectory "$SMPROGRAMS\\LyricsSlide Creator"
  CreateShortCut "$SMPROGRAMS\\LyricsSlide Creator\\LyricsSlide Creator.lnk" "$INSTDIR\\lyrics_slide.exe"
  CreateShortCut "$DESKTOP\\LyricsSlide Creator.lnk" "$INSTDIR\\lyrics_slide.exe"
  WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd
Section "Uninstall"
  Delete "$INSTDIR\\uninstall.exe"
  RMDir /r "$INSTDIR"
  Delete "$SMPROGRAMS\\LyricsSlide Creator\\LyricsSlide Creator.lnk"
  RMDir "$SMPROGRAMS\\LyricsSlide Creator"
  Delete "$DESKTOP\\LyricsSlide Creator.lnk"
SectionEnd
"""
    
    nsis_path = os.path.join(PROJECT_ROOT, "installer.nsi")
    with open(nsis_path, "w") as f:
        f.write(nsis_script)
    
    # NSIS가 설치되어 있는지 확인
    if platform.system() == "Windows":
        print("NSIS 설치 여부 확인 중...")
        try:
            # Windows에서 where 명령을 사용해 makensis 있는지 확인
            result = subprocess.run("where makensis", shell=True, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            makensis_exists = result.returncode == 0
        except Exception:
            makensis_exists = False
        
        if makensis_exists:
            print("NSIS로 설치 프로그램 생성 중...")
            success, _ = run_command(["makensis", nsis_path])
            
            if success:
                print("설치 프로그램 생성 완료: dist\\LyricsSlide_Creator_Setup.exe")
            else:
                print_warning("설치 프로그램 생성 실패. 실행 가능한 폴더가 생성되었습니다.")
        else:
            print_warning("NSIS가 설치되어 있지 않아 설치 프로그램을 생성할 수 없습니다.")
            print("NSIS는 https://nsis.sourceforge.io/Download 에서 다운로드할 수 있습니다.")
    else:
        print_warning("Windows 환경이 아니므로 설치 프로그램은 생성하지 않습니다.")
    
    # 실행 파일 생성 위치 안내
    dist_path = os.path.join(PROJECT_ROOT, "dist", "lyrics_slide")
    print(f"실행 파일 생성 완료: {dist_path}")
    return True

def main():
    """메인 함수"""
    print(f"{GREEN}LyricsSlide Creator 패키징 자동화 시작{RESET}")
    
    # 작업 디렉토리를 프로젝트 루트로 변경
    os.chdir(PROJECT_ROOT)
    print(f"작업 디렉토리: {os.getcwd()}")
    
    # 1. 리소스 폴더 설정
    if not create_resources_folder():
        sys.exit(1)
    
    # 2. PyInstaller 스펙 파일 생성
    if not create_spec_file():
        sys.exit(1)
    
    # 3. 가상 환경 설정
    result = setup_virtual_environment()
    if not result:
        sys.exit(1)
    
    python_path, _ = result
    
    # 4. 플랫폼별 빌드
    if platform.system() == "Darwin":  # macOS
        if not build_for_macos(python_path):
            sys.exit(1)
    elif platform.system() == "Windows":  # Windows
        if not build_for_windows(python_path):
            sys.exit(1)
    else:
        print_error(f"지원되지 않는 플랫폼: {platform.system()}")
        sys.exit(1)
    
    print(f"\n{GREEN}LyricsSlide Creator 패키징 완료!{RESET}")
    print(f"\n결과물은 dist 폴더에서 찾을 수 있습니다.")
    print(f"위치: {os.path.join(PROJECT_ROOT, 'dist')}")

if __name__ == "__main__":
    main()