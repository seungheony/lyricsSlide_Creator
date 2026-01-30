import sys
import os

# PyInstaller 환경에서 src 폴더를 찾기 위한 경로 설정
# 이 코드가 없으면 'No module named ui' 오류가 발생할 수 있습니다.
if getattr(sys, 'frozen', False):
    # The application is frozen
    base_path = sys._MEIPASS
    sys.path.insert(0, os.path.join(base_path, 'src'))
else:
    # The application is not frozen
    # 모듈이 src 폴더 내에 있으므로, 프로젝트 루트를 path에 추가
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()