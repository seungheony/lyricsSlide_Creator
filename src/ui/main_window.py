import sys
import os
import requests
import traceback
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QLabel, QStackedWidget,
    QSplitter, QTextEdit, QFileDialog, QMessageBox, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QPixmap

from src.utils.melon_api import MelonScraper
from src.utils.ppt_engine import PPTBuilder
from src.utils.helpers import resource_path
from src.ui.style import *

def show_critical_error(parent, text, detailed_text=""):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setText(text)
    msg.setDetailedText(detailed_text)
    msg.setWindowTitle("오류")
    msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    msg.exec()

# --- 스레드 클래스들 ---
class SearchThread(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    def __init__(self, scraper, keyword):
        super().__init__(); self.scraper = scraper; self.keyword = keyword
    def run(self):
        try:
            res = self.scraper.search_song(self.keyword)
            self.finished.emit(res if res else [])
        except Exception: self.error.emit(traceback.format_exc())

class DetailThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    def __init__(self, scraper, song_id):
        super().__init__(); self.scraper = scraper; self.song_id = song_id
    def run(self):
        try:
            det = self.scraper.get_song_detail(self.song_id)
            if det and det.get('lyrics'): self.finished.emit(det)
            else: self.error.emit("가사 정보를 가져오지 못했습니다.\n네트워크 상태를 확인하거나 다른 곡으로 시도해보세요.")
        except Exception: self.error.emit(traceback.format_exc())

class ImageLoaderThread(QThread):
    loaded = pyqtSignal(bytes)
    def __init__(self, url):
        super().__init__(); self.url = url
    def run(self):
        try:
            if self.url:
                resp = requests.get(self.url, timeout=10)
                if resp.status_code == 200: self.loaded.emit(resp.content)
        except: pass

class SongItemWidget(QWidget):
    def __init__(self, title, artist, album):
        super().__init__()
        layout = QHBoxLayout(self); layout.setContentsMargins(10, 10, 10, 10); layout.setSpacing(15)
        self.img_label = QLabel(); self.img_label.setFixedSize(60, 60); self.img_label.setStyleSheet("background-color: #EEE; border-radius: 4px;")
        info = QVBoxLayout(); title_lbl = QLabel(title); title_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        desc_lbl = QLabel(f"{artist} • {album}"); desc_lbl.setStyleSheet("font-size: 12px; color: #777;")
        info.addWidget(title_lbl); info.addWidget(desc_lbl); layout.addWidget(self.img_label); layout.addLayout(info); layout.addStretch()

# --- 메인 윈도우 ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lyrics Slide Creator"); self.resize(1000, 800)
        self.scraper = MelonScraper(); self.template_path = resource_path("template.pptx")
        self._threads = []; self.slide_chunks = []
        self.setStyleSheet(GLOBAL_STYLE)
        self.stack = QStackedWidget(); self.setCentralWidget(self.stack)
        self.create_search_page(); self.create_editor_page()
        
    def create_search_page(self):
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(30, 30, 30, 30)
        header = QLabel("Melon Lyrics Search"); header.setStyleSheet(TITLE_LABEL_STYLE); header.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(header)
        search_box = QHBoxLayout(); self.search_input = QLineEdit(); self.search_input.setPlaceholderText("노래 제목 또는 가수 검색"); self.search_input.setStyleSheet(SEARCH_BAR_STYLE); self.search_input.returnPressed.connect(self.do_search)
        self.search_btn = QPushButton("검색"); self.search_btn.setStyleSheet(BUTTON_STYLE); self.search_btn.clicked.connect(self.do_search)
        search_box.addWidget(self.search_input); search_box.addWidget(self.search_btn); layout.addLayout(search_box)
        self.result_list = QListWidget(); self.result_list.setStyleSheet(LIST_WIDGET_STYLE); self.result_list.itemClicked.connect(self.on_song_select); layout.addWidget(self.result_list)
        self.progress = QProgressBar(); self.progress.setVisible(False); self.progress.setRange(0, 0); layout.addWidget(self.progress); self.stack.addWidget(page)

    def create_editor_page(self):
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(20, 20, 20, 20)
        top = QHBoxLayout(); back = QPushButton("❮ 뒤로"); back.setStyleSheet("background:transparent;font-weight:bold;"); back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.editor_art = QLabel(); self.editor_art.setFixedSize(40, 40); self.editor_art.setStyleSheet("background:#EEE;border-radius:4px;")
        self.info_lbl = QLabel("노래 정보"); self.info_lbl.setStyleSheet("font-size:16px;font-weight:bold;")
        top.addWidget(back); top.addWidget(self.editor_art); top.addSpacing(10); top.addWidget(self.info_lbl); top.addStretch(); layout.addLayout(top)
        split = QSplitter(Qt.Orientation.Horizontal); left = QWidget(); l_ly = QVBoxLayout(left); l_ly.addWidget(QLabel("가사 편집")); self.lyrics_edit = QTextEdit(); self.lyrics_edit.setStyleSheet(TEXT_EDIT_STYLE); l_ly.addWidget(self.lyrics_edit)
        btns = QHBoxLayout()
        for n in [1, 2]:
            b = QPushButton(f"{n}줄씩"); b.setStyleSheet(SECONDARY_BUTTON_STYLE); b.clicked.connect(lambda _, n=n: self.apply_split(n)); btns.addWidget(b)
        l_ly.addLayout(btns); right = QWidget(); r_ly = QVBoxLayout(right); r_ly.addWidget(QLabel("미리보기"))
        self.prev_list = QListWidget(); self.prev_list.setStyleSheet(LIST_WIDGET_STYLE + "\nQListWidget::item { padding: 4px 6px; }")
        self.prev_list.itemDoubleClicked.connect(self.on_slide_double_click)
        r_ly.addWidget(self.prev_list)
        split.addWidget(left); split.addWidget(right); layout.addWidget(split)
        bottom = QFrame(); bl = QHBoxLayout(bottom); self.tmpl_lbl = QLabel(f"템플릿: {os.path.basename(self.template_path)}"); btn_tmpl = QPushButton("변경"); btn_tmpl.setStyleSheet(SECONDARY_BUTTON_STYLE); btn_tmpl.clicked.connect(self.choose_template)
        btn_gen = QPushButton("PPT 생성"); btn_gen.setStyleSheet(BUTTON_STYLE); btn_gen.clicked.connect(self.generate_ppt)
        bl.addWidget(self.tmpl_lbl); bl.addWidget(btn_tmpl); bl.addStretch(); bl.addWidget(btn_gen); layout.addWidget(bottom); self.stack.addWidget(page)

    def do_search(self):
        k = self.search_input.text().strip();
        if not k or not self.search_btn.isEnabled(): return
        self.result_list.clear(); self.search_btn.setEnabled(False); self.progress.setVisible(True)
        t = SearchThread(self.scraper, k); t.finished.connect(self.on_search_finished); t.error.connect(self.on_thread_error); self._threads.append(t); t.start()

    def on_search_finished(self, res):
        self.progress.setVisible(False); self.search_btn.setEnabled(True)
        if not res: QMessageBox.information(self, "알림", "검색 결과가 없습니다."); return
        for s in res:
            item_w = SongItemWidget(s.get('title',''), s.get('artist',''), s.get('album',''))
            item = QListWidgetItem(self.result_list); item.setSizeHint(QSize(300, 85)); item.setData(Qt.ItemDataRole.UserRole, s); self.result_list.addItem(item); self.result_list.setItemWidget(item, item_w)

    def on_song_select(self, item):
        sd = item.data(Qt.ItemDataRole.UserRole)
        if not sd: return
        self.info_lbl.setText(f"{sd.get('title','') if sd.get('title') else ''} - {sd.get('artist','') if sd.get('artist') else ''}")
        self.progress.setVisible(True); self.search_btn.setEnabled(False)
        t = DetailThread(self.scraper, sd.get('song_id')); t.finished.connect(self.on_detail_finished); t.error.connect(self.on_thread_error); self._threads.append(t); t.start()

    def on_detail_finished(self, det):
        self.lyrics_edit.setPlainText(det.get('lyrics',''))
        if det.get('image_url'):
            it = ImageLoaderThread(det.get('image_url')); it.loaded.connect(self.on_editor_art_loaded); self._threads.append(it); it.start()
        self.apply_split(2); QTimer.singleShot(10, self.show_editor)

    def show_editor(self):
        self.progress.setVisible(False); self.search_btn.setEnabled(True); self.stack.setCurrentIndex(1)

    def on_thread_error(self, error_msg):
        self.progress.setVisible(False)
        self.search_btn.setEnabled(True)
        show_critical_error(self, "작업 중 오류가 발생했습니다.", error_msg)

    def on_editor_art_loaded(self, data):
        px = QPixmap(); 
        if px.loadFromData(data): self.editor_art.setPixmap(px)

    def apply_split(self, n):
        self.slide_chunks = PPTBuilder.split_lyrics(self.lyrics_edit.toPlainText(), n)
        self.refresh_preview()

    def refresh_preview(self):
        self.prev_list.clear()
        for i, c in enumerate(self.slide_chunks):
            self.prev_list.addItem(f"[슬라이드 {i+1}]\n{c}")

    def on_slide_double_click(self, item):
        idx = self.prev_list.row(item)
        lines = self.slide_chunks[idx].split('\n')
        if len(lines) >= 2:
            self.split_slide_at(idx)
        elif idx > 0:
            self.merge_slide_up(idx)

    def merge_slide_up(self, idx):
        current = self.slide_chunks[idx]
        prev = self.slide_chunks[idx - 1]
        msg = QMessageBox(self)
        msg.setWindowTitle("병합 방식 선택")
        msg.setText(f"'{current}'을(를) 이전 슬라이드에 어떻게 병합할까요?")
        btn_append = msg.addButton("이어붙이기", QMessageBox.ButtonRole.AcceptRole)
        btn_newline = msg.addButton("다음 줄에 추가", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("취소", QMessageBox.ButtonRole.RejectRole)
        msg.exec()
        clicked = msg.clickedButton()
        if clicked == btn_newline:
            self.slide_chunks[idx - 1] = prev + "\n" + current
        elif clicked == btn_append:
            lines = prev.split('\n')
            lines[-1] = lines[-1] + " " + current
            self.slide_chunks[idx - 1] = "\n".join(lines)
        else:
            return
        del self.slide_chunks[idx]
        self.refresh_preview()

    def split_slide_at(self, idx):
        lines = self.slide_chunks[idx].split('\n')
        if len(lines) < 2:
            return
        first_line = lines[0]
        remaining = lines[1:]
        # Flatten all lines from remaining + subsequent slides
        rest_lines = remaining
        for chunk in self.slide_chunks[idx + 1:]:
            rest_lines.extend(chunk.split('\n'))
        # Rebuild: keep slides before idx, add single-line slide, then re-chunk rest 2 lines at a time
        new_chunks = self.slide_chunks[:idx]
        new_chunks.append(first_line)
        for i in range(0, len(rest_lines), 2):
            new_chunks.append("\n".join(rest_lines[i:i + 2]))
        self.slide_chunks = new_chunks
        self.refresh_preview()

    def choose_template(self):
        p, _ = QFileDialog.getOpenFileName(self, "PPT 템플릿", "", "PowerPoint (*.pptx)");
        if p: self.template_path = p; self.tmpl_lbl.setText(f"템플릿: {os.path.basename(p)}")

    def generate_ppt(self):
        lyrics_text = self.lyrics_edit.toPlainText()
        if not lyrics_text.strip():
            QMessageBox.warning(self, "알림", "가사가 없습니다."); return

        if not os.path.exists(self.template_path):
            show_critical_error(self, "템플릿 파일을 찾을 수 없습니다.", f"경로: {self.template_path}")
            return
            
        default_filename = f"{self.info_lbl.text().replace('/', '_')}.pptx"
        save_path, _ = QFileDialog.getSaveFileName(self, "PPT 저장", default_filename, "PowerPoint (*.pptx)")
        
        if not save_path:
            return

        try:
            # 1. 메모리에 PPT 생성
            chunks = self.slide_chunks if self.slide_chunks else PPTBuilder.split_lyrics(lyrics_text, 2)
            builder = PPTBuilder(self.template_path)
            ppt_buffer = builder.generate_slides_to_memory(chunks)
            
            if not ppt_buffer:
                show_critical_error(self, "PPT 생성 실패.", "메모리에서 PPT 객체를 생성하지 못했습니다.")
                return

            # 2. 메모리의 내용을 파일로 직접 저장
            if PPTBuilder.save_to_file(ppt_buffer, save_path):
                QMessageBox.information(self, "성공", "PPT 생성이 완료되었습니다!")
            else:
                show_critical_error(self, "파일 저장 실패.", f"다음 경로에 파일을 쓸 수 없습니다:\n{save_path}\n\n권한 문제를 확인해주세요.")

        except Exception as e:
            show_critical_error(self, "PPT 생성 중 예외가 발생했습니다.", traceback.format_exc())