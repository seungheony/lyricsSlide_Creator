import sys
import subprocess


def get_version():
    """빌드 환경에 따라 버전 문자열을 반환한다.

    - 소스 직접 실행 (not frozen): "TEST"
    - PyInstaller 패키징 실행 (frozen):
        - release/X.Y.Z 브랜치 → "X.Y.Z"
        - beta/X.Y.Z 브랜치   → "X.Y.Z (beta)"
        - 그 외 브랜치         → "DEVELOP"
    """
    if not getattr(sys, 'frozen', False):
        return "TEST"

    # 패키징 시 빌드 스크립트가 _BUILD_BRANCH를 주입할 수 있음
    branch = getattr(sys, '_BUILD_BRANCH', None)
    if branch is None:
        try:
            branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                stderr=subprocess.DEVNULL, timeout=5
            ).decode().strip()
        except Exception:
            return "DEVELOP"

    if branch.startswith('release/'):
        return branch[len('release/'):]
    elif branch.startswith('beta/'):
        return f"{branch[len('beta/'):]} (beta)"
    else:
        return "DEVELOP"
