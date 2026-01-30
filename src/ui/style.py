
# Modern & Clean Theme — Refined Design System

# ── Color Palette ──
PRIMARY = "#00CD3C"
PRIMARY_HOVER = "#00B936"
PRIMARY_PRESSED = "#00992D"
BG = "#F5F7FA"
SURFACE = "#FFFFFF"
TEXT_PRIMARY = "#222222"
TEXT_SECONDARY = "#666666"
TEXT_HINT = "#AAAAAA"
BORDER = "#E2E5E9"
BORDER_LIGHT = "#EDEEF0"
DIVIDER = "#F0F1F3"
HOVER_BG = "#F7F8FA"
SELECTED_BG = "#F0FFF4"
RADIUS_SM = "8px"
RADIUS_MD = "12px"
RADIUS_LG = "16px"

GLOBAL_STYLE = f"""
QMainWindow {{
    background-color: {BG};
}}
QWidget {{
    color: {TEXT_PRIMARY};
    font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', -apple-system, sans-serif;
}}
QSplitter::handle {{
    background-color: {BORDER_LIGHT};
    width: 1px;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 4px 0;
}}
QScrollBar::handle:vertical {{
    background: #CCC;
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: #AAA;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    height: 0;
}}
"""

SEARCH_CONTAINER_STYLE = f"""
QFrame {{
    background-color: {SURFACE};
    border: 1.5px solid {BORDER};
    border-bottom: 2px solid {BORDER};
    border-radius: {RADIUS_MD};
    padding: 6px;
}}
"""

SEARCH_BAR_STYLE = f"""
QLineEdit {{
    padding: 10px 16px;
    border: none;
    border-radius: {RADIUS_SM};
    font-size: 15px;
    background-color: transparent;
    color: {TEXT_PRIMARY};
    selection-background-color: {PRIMARY};
    selection-color: white;
}}
QLineEdit::placeholder {{
    color: {TEXT_HINT};
    padding-top: 1px;
}}
"""

SEARCH_ICON_STYLE = f"""
QLabel {{
    font-size: 20px;
    color: {TEXT_HINT};
    padding: 0 8px 2px 12px;
}}
"""

SEARCH_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {PRIMARY};
    color: white;
    border: none;
    padding: 10px 28px;
    border-radius: {RADIUS_SM};
    font-size: 15px;
    font-weight: 600;
    min-width: 80px;
}}
QPushButton:hover {{
    background-color: {PRIMARY_HOVER};
}}
QPushButton:pressed {{
    background-color: {PRIMARY_PRESSED};
}}
QPushButton:disabled {{
    background-color: #DDD;
    color: #999;
}}
"""

BUTTON_STYLE = f"""
QPushButton {{
    background-color: {PRIMARY};
    color: white;
    border: none;
    padding: 12px 28px;
    border-radius: {RADIUS_SM};
    font-size: 15px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {PRIMARY_HOVER};
}}
QPushButton:pressed {{
    background-color: {PRIMARY_PRESSED};
}}
QPushButton:disabled {{
    background-color: #DDD;
    color: #999;
}}
"""

SECONDARY_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {SURFACE};
    color: {TEXT_SECONDARY};
    border: 1.5px solid {BORDER};
    padding: 8px 18px;
    border-radius: {RADIUS_SM};
    font-size: 14px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {HOVER_BG};
    border-color: #CCC;
    color: {TEXT_PRIMARY};
}}
"""

SEGMENT_BUTTON_ACTIVE = f"""
QPushButton {{
    background-color: {PRIMARY};
    color: white;
    border: 1.5px solid {PRIMARY};
    padding: 4px 20px;
    border-radius: {RADIUS_SM};
    font-size: 14px;
    font-weight: 600;
    margin-left: 4px;
}}
"""

SEGMENT_BUTTON_INACTIVE = f"""
QPushButton {{
    background-color: {SURFACE};
    color: {TEXT_SECONDARY};
    border: 1.5px solid {BORDER};
    padding: 4px 20px;
    border-radius: {RADIUS_SM};
    font-size: 14px;
    font-weight: 500;
    margin-left: 4px;
}}
QPushButton:hover {{
    background-color: {HOVER_BG};
    color: {TEXT_PRIMARY};
}}
"""

LIST_WIDGET_STYLE = f"""
QListWidget {{
    border: none;
    background-color: transparent;
    outline: none;
    color: {TEXT_PRIMARY};
}}
QListWidget::item {{
    background-color: {SURFACE};
    border: 1px solid {BORDER_LIGHT};
    border-bottom: 2px solid {BORDER_LIGHT};
    border-radius: {RADIUS_MD};
    margin-bottom: 6px;
    padding: 0;
    color: {TEXT_PRIMARY};
}}
QListWidget::item:selected {{
    background-color: {SELECTED_BG};
    border: 1.5px solid {PRIMARY};
    border-bottom: 2.5px solid {PRIMARY};
    color: {TEXT_PRIMARY};
}}
QListWidget::item:hover {{
    background-color: {HOVER_BG};
    border-color: {BORDER};
    border-bottom-color: #CCC;
}}
"""

PREVIEW_LIST_STYLE = f"""
QListWidget {{
    border: none;
    background-color: transparent;
    outline: none;
    color: {TEXT_PRIMARY};
}}
QListWidget::item {{
    background-color: {SURFACE};
    border: 1px solid {BORDER_LIGHT};
    border-bottom: 2px solid {BORDER_LIGHT};
    border-radius: {RADIUS_SM};
    margin-bottom: 4px;
    padding: 0;
    color: {TEXT_PRIMARY};
}}
QListWidget::item:selected {{
    background-color: {SELECTED_BG};
    border: 1.5px solid {PRIMARY};
    border-bottom: 2.5px solid {PRIMARY};
    color: {TEXT_PRIMARY};
}}
QListWidget::item:hover {{
    background-color: {HOVER_BG};
    border-bottom-color: #CCC;
}}
"""

SLIDE_BADGE_STYLE = f"""
QLabel {{
    background-color: {PRIMARY};
    color: white;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 4px;
}}
"""

SLIDE_TEXT_STYLE = f"""
QLabel {{
    font-size: 14px;
    color: {TEXT_PRIMARY};
    line-height: 1.5;
    padding: 0 0 8px 0;
}}
"""

TEXT_EDIT_STYLE = f"""
QTextEdit {{
    border: 1.5px solid {BORDER};
    border-bottom: 2px solid {BORDER};
    border-radius: {RADIUS_MD};
    padding: 16px;
    font-size: 15px;
    line-height: 1.6;
    background-color: {SURFACE};
    color: {TEXT_PRIMARY};
    font-family: 'Apple SD Gothic Neo', sans-serif;
}}
QTextEdit:focus {{
    border: 2px solid {PRIMARY};
    border-bottom: 2.5px solid {PRIMARY};
}}
"""

TITLE_LABEL_STYLE = f"""
QLabel {{
    font-size: 26px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    margin-bottom: 8px;
}}
"""

SECTION_TITLE_STYLE = f"""
QLabel {{
    font-size: 14px;
    font-weight: 600;
    color: {TEXT_SECONDARY};
    margin-bottom: 6px;
    letter-spacing: 0.5px;
}}
"""

CARD_TITLE_STYLE = f"""
QLabel {{
    font-size: 15px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}
"""

CARD_SUBTITLE_STYLE = f"""
QLabel {{
    font-size: 13px;
    color: {TEXT_SECONDARY};
}}
"""

BACK_BUTTON_STYLE = f"""
QPushButton {{
    background-color: transparent;
    color: {TEXT_SECONDARY};
    border: 1.5px solid {BORDER};
    padding: 6px 14px;
    border-radius: {RADIUS_SM};
    font-size: 14px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {HOVER_BG};
    color: {TEXT_PRIMARY};
    border-color: #CCC;
}}
"""

EDITOR_INFO_STYLE = f"""
QLabel {{
    font-size: 16px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}
"""

TEMPLATE_LABEL_STYLE = f"""
QLabel {{
    font-size: 13px;
    color: {TEXT_SECONDARY};
}}
"""

ALBUM_ART_STYLE = f"""
QLabel {{
    background-color: {BORDER_LIGHT};
    border-radius: {RADIUS_SM};
}}
"""

EMPTY_STATE_STYLE = f"""
QLabel {{
    font-size: 15px;
    color: {TEXT_HINT};
    padding: 40px;
}}
"""

PROGRESS_STYLE = f"""
QProgressBar {{
    border: none;
    background-color: {BORDER_LIGHT};
    border-radius: 3px;
    max-height: 4px;
}}
QProgressBar::chunk {{
    background-color: {PRIMARY};
    border-radius: 3px;
}}
"""

TOAST_STYLE_SUCCESS = f"""
QFrame {{
    background-color: #F0FFF4;
    border: 1px solid #C6F6D5;
    border-radius: {RADIUS_SM};
    padding: 12px 20px;
}}
"""

TOAST_STYLE_ERROR = f"""
QFrame {{
    background-color: #FFF5F5;
    border: 1px solid #FED7D7;
    border-radius: {RADIUS_SM};
    padding: 12px 20px;
}}
"""

VERSION_LABEL_STYLE = f"""
QLabel {{
    font-size: 11px;
    color: {TEXT_HINT};
    padding: 2px 8px;
}}
"""
