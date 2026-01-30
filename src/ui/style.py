
# Modern & Clean Theme - Dark Mode Safe

# Color Palette
# Green: #00CD3C
# Bg: #F5F7FA
# Text: #333333 (Forced Dark Text)
# Secondary Text: #888888

GLOBAL_STYLE = """
QMainWindow {
    background-color: #F5F7FA;
}
/* Force all widgets to have dark text by default to override System Dark Mode text color */
QWidget {
    color: #333333;
    font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
}
"""

SEARCH_BAR_STYLE = """
QLineEdit {
    padding: 12px 15px;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    font-size: 16px;
    background-color: white;
    color: #333333; /* Explicit text color */
    selection-background-color: #00CD3C;
    selection-color: white;
}
QLineEdit:focus {
    border: 2px solid #00CD3C;
    outline: none;
}
QLineEdit::placeholder {
    color: #AAAAAA;
}
"""

BUTTON_STYLE = """
QPushButton {
    background-color: #00CD3C;
    color: white; /* Keep white text for green button */
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 15px;
    font-weight: bold;
    font-family: 'Apple SD Gothic Neo', sans-serif;
}
QPushButton:hover {
    background-color: #00B936;
    margin-top: 1px;
}
QPushButton:pressed {
    background-color: #00992D;
    margin-top: 2px;
}
QPushButton:disabled {
    background-color: #CCCCCC;
    color: #888888;
}
"""

SECONDARY_BUTTON_STYLE = """
QPushButton {
    background-color: white;
    color: #555555; /* Explicit dark gray text */
    border: 1px solid #ddd;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #f0f0f0;
    border-color: #ccc;
    color: #333333;
}
"""

LIST_WIDGET_STYLE = """
QListWidget {
    border: none;
    background-color: transparent;
    outline: none;
    color: #333333; /* Explicit text color */
}
QListWidget::item {
    background-color: white;
    border: 1px solid #EAEAEA;
    border-radius: 10px;
    margin-bottom: 8px;
    padding: 10px; /* Increased padding */
    color: #333333;
}
QListWidget::item:selected {
    background-color: white;
    border: 2px solid #00CD3C;
    outline: none;
    color: #333333; /* Keep text dark even when selected */
}
QListWidget::item:hover {
    background-color: #FAFAFA;
}
"""

TEXT_EDIT_STYLE = """
QTextEdit {
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 15px;
    font-size: 15px;
    line-height: 1.6;
    background-color: white;
    color: #333333; /* Explicit text color */
    font-family: 'Apple SD Gothic Neo', sans-serif;
}
QTextEdit:focus {
    border: 2px solid #00CD3C;
}
"""

TITLE_LABEL_STYLE = """
QLabel {
    font-size: 28px;
    font-weight: 800;
    color: #333333; /* Explicit text color */
    margin-bottom: 20px;
}
"""

CARD_TITLE_STYLE = """
QLabel {
    font-size: 16px;
    font-weight: bold;
    color: #222222; /* Very dark gray */
}
"""

CARD_SUBTITLE_STYLE = """
QLabel {
    font-size: 13px;
    color: #666666; /* Medium gray */
}
"""
