"""
유틸리티 함수 모음
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from pptx import Presentation
from pptx.dml.color import RGBColor
import tempfile

def ensure_safe_path(path):
    """경로가 한글 등 특수 문자를 포함할 경우 안전하게 처리합니다."""
    if sys.platform.startswith('win'):
        # Windows에서는 긴 경로 지원 활성화 (> 260자)
        if not path.startswith('\\\\?\\'):
            if os.path.isabs(path):
                return '\\\\?\\' + path
    return path

def clear_directory(directory):
    """디렉토리를 비우거나 생성합니다."""
    # 경로 안전하게 처리
    safe_dir = ensure_safe_path(directory)
    
    if os.path.exists(safe_dir):
        for filename in os.listdir(safe_dir):
            file_path = os.path.join(safe_dir, filename)
            safe_file_path = ensure_safe_path(file_path)
            try:
                if os.path.isfile(safe_file_path):
                    os.unlink(safe_file_path)
                elif os.path.isdir(safe_file_path):  # 하위 디렉토리 처리 추가
                    shutil.rmtree(safe_file_path)
            except PermissionError as e:
                # Windows에서 파일 접근 권한 문제 처리
                print(f"권한 문제로 파일 삭제 실패: {e}")
                if sys.platform.startswith('win'):
                    print("파일이 다른 프로그램에서 사용 중일 수 있습니다. 해당 프로그램을 종료하고 다시 시도하세요.")
            except Exception as e:
                print(f"파일 삭제 중 오류 발생: {e}")
    else:
        os.makedirs(safe_dir)
    print(f"'{directory}' 폴더를 정리하였습니다.")

def get_libreoffice_path():
    """시스템에 설치된 LibreOffice 경로를 찾습니다."""
    if sys.platform.startswith('win'):
        # Windows에서 LibreOffice 경로 검색
        office_paths = [
            os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'LibreOffice', 'program', 'soffice.exe'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'LibreOffice', 'program', 'soffice.exe')
        ]
        for path in office_paths:
            if os.path.exists(path):
                return path
    elif platform.system() == 'Darwin':  # macOS
        # macOS에서 LibreOffice 경로 검색
        office_paths = [
            '/Applications/LibreOffice.app/Contents/MacOS/soffice',
            '/Applications/LibreOffice.app/Contents/MacOS/soffice.bin'
        ]
        for path in office_paths:
            if os.path.exists(path):
                return path
    else:  # Linux 등
        # 시스템 경로에서 검색
        for cmd in ['libreoffice', 'soffice']:
            path = shutil.which(cmd)
            if path:
                return path
    
    return None

def convert_ppt_to_pptx(ppt_file):
    """
    .ppt 파일을 .pptx 파일로 변환합니다.
    """
    pptx_file = os.path.splitext(ppt_file)[0] + '.pptx'
    if os.path.exists(pptx_file):
        print(f"이미 변환된 파일이 존재합니다: {pptx_file}")
        return pptx_file

    print(f".ppt 파일을 .pptx로 변환합니다: {ppt_file}")
    
    libreoffice_path = get_libreoffice_path()
    if libreoffice_path is None:
        raise ValueError("LibreOffice가 설치되어 있지 않습니다.")
    
    # 임시 디렉토리 생성
    temp_dir = os.path.join(tempfile.gettempdir(), "ppt_converter")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # LibreOffice로 변환 실행
    cmd = [
        libreoffice_path,
        '--headless',
        '--convert-to', 'pptx',
        '--outdir', os.path.dirname(pptx_file),
        ppt_file
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if os.path.exists(pptx_file):
            print(f"변환 완료: {pptx_file}")
            return pptx_file
        else:
            print(f"변환된 파일을 찾을 수 없습니다: {pptx_file}")
            return ppt_file
    except subprocess.CalledProcessError as e:
        print(f"변환 중 오류 발생: {e}")
        return ppt_file

def set_slide_background_to_white(input_pptx, output_pptx):
    """
    프레젠테이션의 모든 슬라이드 배경을 흰색으로 설정합니다.
    """
    try:
        # 프레젠테이션 열기
        prs = Presentation(input_pptx)
        
        # 각 슬라이드의 배경을 흰색으로 설정
        for slide in prs.slides:
            background = slide.background
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(255, 255, 255)
        
        # 수정된 프레젠테이션 저장
        prs.save(output_pptx)
        print(f"슬라이드 배경이 흰색으로 설정되었습니다: {output_pptx}")
        return True
    except Exception as e:
        print(f"슬라이드 배경 설정 중 오류 발생: {e}")
        # 실패 시 원본 파일 복사
        shutil.copy2(input_pptx, output_pptx)
        return False