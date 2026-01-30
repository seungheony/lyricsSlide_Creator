import sys
import os
import requests
import traceback
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QLabel, QStackedWidget,
    QSplitter, QTextEdit, QFileDialog, QMessageBox, QProgressBar, QFrame,
    QGraphicsOpacityEffect, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QSize, QTimer,
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
)
from PyQt6.QtGui import QPixmap

from src.utils.melon_api import MelonScraper
from src.utils.ppt_engine import PPTBuilder
from src.utils.helpers import resource_path
from src.utils.version import get_version
from src.ui.style import *


def show_critical_error(parent, text, detailed_text=""):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setText(text)
    msg.setDetailedText(detailed_text)
    msg.setWindowTitle("오류")
    msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    msg.exec()


# --- Toast Notification ---
class ToastWidget(QFrame):
    def __init__(self, parent, message, is_error=False):
        super().__init__(parent)
        self.setStyleSheet(TOAST_STYLE_ERROR if is_error else TOAST_STYLE_SUCCESS)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 10, 16, 10)
        icon = "✕" if is_error else "✓"
        icon_color = "#E53E3E" if is_error else PRIMARY
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size:18px; font-weight:bold; color:{icon_color};")
        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet(f"font-size:14px; color:{TEXT_PRIMARY};")
        lay.addWidget(icon_lbl)
        lay.addWidget(msg_lbl)
        lay.addStretch()
        self.setFixedHeight(48)
        self.adjustSize()

        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(0.0)

    def show_toast(self, duration=2500):
        self.show()
        self.raise_()
        pw = self.parent().width()
        w = min(400, pw - 40)
        self.setFixedWidth(w)
        self.move((pw - w) // 2, 20)

        self._anim_in = QPropertyAnimation(self._opacity, b"opacity")
        self._anim_in.setDuration(200)
        self._anim_in.setStartValue(0.0)
        self._anim_in.setEndValue(1.0)
        self._anim_in.start()

        QTimer.singleShot(duration, self._fade_out)

    def _fade_out(self):
        self._anim_out = QPropertyAnimation(self._opacity, b"opacity")
        self._anim_out.setDuration(400)
        self._anim_out.setStartValue(1.0)
        self._anim_out.setEndValue(0.0)
        self._anim_out.finished.connect(self.deleteLater)
        self._anim_out.start()


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


class AlbumArtLoaderThread(QThread):
    """song_id로 앨범아트 URL을 조회한 뒤 이미지를 다운로드한다."""
    loaded = pyqtSignal(bytes)
    def __init__(self, scraper, song_id):
        super().__init__()
        self.scraper = scraper
        self.song_id = song_id
    def run(self):
        try:
            url = self.scraper.get_album_image_url(self.song_id)
            if url:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    self.loaded.emit(resp.content)
        except:
            pass


class SongItemWidget(QWidget):
    IMG_SIZE = 48  # 이미지 크기 축소

    def __init__(self, title, artist, album):
        super().__init__()
        # 위젯 layout이 여백을 담당 (CSS padding 0)
        # SlideItemWidget과 동일한 패턴 사용 (setSizePolicy 제거)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)  # 위젯이 여백 담당
        layout.setSpacing(12)

        self.img_label = QLabel()
        self.img_label.setFixedSize(self.IMG_SIZE, self.IMG_SIZE)
        self.img_label.setStyleSheet(ALBUM_ART_STYLE)
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info = QVBoxLayout()
        info.setSpacing(4)
        info.setContentsMargins(0, 0, 0, 0)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(CARD_TITLE_STYLE)
        title_lbl.setWordWrap(False)

        # 아티스트명 중복 제거
        artist_clean = artist.strip()
        # 같은 텍스트가 반복되는 경우 제거 (예: "아티스트아티스트" -> "아티스트")
        if len(artist_clean) > 0 and len(artist_clean) % 2 == 0:
            half = len(artist_clean) // 2
            if artist_clean[:half] == artist_clean[half:]:
                artist_clean = artist_clean[:half]

        desc_lbl = QLabel(f"{artist_clean}  ·  {album}")
        desc_lbl.setStyleSheet(CARD_SUBTITLE_STYLE)
        desc_lbl.setWordWrap(False)

        info.addWidget(title_lbl)
        info.addWidget(desc_lbl)
        info.addStretch()  # 아래쪽 공간 확보 (SlideItemWidget 패턴)

        # 이미지와 텍스트 레이아웃 추가
        layout.addWidget(self.img_label)
        layout.addLayout(info, 1)


class SlideItemWidget(QWidget):
    """미리보기 슬라이드를 표시하는 커스텀 위젯 (슬라이드 번호 뱃지 포함)"""
    def __init__(self, slide_number, text):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 슬라이드 번호 뱃지
        badge = QLabel(f"슬라이드 {slide_number}")
        badge.setStyleSheet(SLIDE_BADGE_STYLE)
        badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout.addWidget(badge)

        # 가사 텍스트
        text_label = QLabel(text)
        text_label.setStyleSheet(SLIDE_TEXT_STYLE)
        text_label.setWordWrap(True)
        text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(text_label)
        layout.addStretch()  # 아래쪽 공간 확보


# --- 메인 윈도우 ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lyrics Slide Creator")
        self.resize(1000, 800)
        self.setMinimumSize(700, 500)
        self.scraper = MelonScraper()
        self.template_path = resource_path("template.pptx")
        self._threads = []
        self.slide_chunks = []
        self._active_split = 2
        self.setStyleSheet(GLOBAL_STYLE)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.create_search_page()
        self.create_editor_page()

        # Version label (top-right overlay)
        self._version_label = QLabel(f"v{get_version()}", self)
        self._version_label.setStyleSheet(VERSION_LABEL_STYLE)
        self._version_label.adjustSize()
        self._version_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    # ── Search Page ──
    def create_search_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 20)
        layout.setSpacing(0)

        # Title area (fixed)
        header = QLabel("Lyrics Slide Creator")
        header.setStyleSheet(TITLE_LABEL_STYLE)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        subtitle = QLabel("멜론에서 노래를 검색하고 가사 슬라이드를 만들어보세요")
        subtitle.setStyleSheet(f"font-size:14px; color:{TEXT_HINT};")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # Integrated Search bar (fixed height)
        search_frame = QFrame()
        search_frame.setStyleSheet(SEARCH_CONTAINER_STYLE)
        search_frame.setFixedHeight(64)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(6, 6, 6, 6)
        search_layout.setSpacing(6)

        # Search icon
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet(SEARCH_ICON_STYLE)
        search_layout.addWidget(search_icon)

        # Input field
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("노래 제목 또는 가수 이름을 입력하세요")
        self.search_input.setStyleSheet(SEARCH_BAR_STYLE)
        self.search_input.returnPressed.connect(self.do_search)
        search_layout.addWidget(self.search_input, 1)

        # Search button
        self.search_btn = QPushButton("검색")
        self.search_btn.setStyleSheet(SEARCH_BUTTON_STYLE)
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_btn.clicked.connect(self.do_search)
        search_layout.addWidget(self.search_btn)

        layout.addWidget(search_frame)

        # Progress bar (fixed)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setRange(0, 0)
        self.progress.setStyleSheet(PROGRESS_STYLE)
        self.progress.setFixedHeight(4)
        layout.addWidget(self.progress)

        layout.addSpacing(8)

        # Empty state (centered in remaining space)
        self.empty_state = QLabel("검색 결과가 여기에 표시됩니다")
        self.empty_state.setStyleSheet(EMPTY_STATE_STYLE)
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Results list (stretches to fill remaining space)
        self.result_list = QListWidget()
        self.result_list.setStyleSheet(LIST_WIDGET_STYLE)
        self.result_list.setSpacing(2)  # 아이템 간 간격
        self.result_list.itemClicked.connect(self.on_song_select)
        self.result_list.setVisible(False)

        layout.addWidget(self.empty_state, 1)
        layout.addWidget(self.result_list, 1)
        self.stack.addWidget(page)

    # ── Editor Page ──
    def create_editor_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(10)

        # Top bar (fixed height)
        top = QHBoxLayout()
        top.setSpacing(12)
        back = QPushButton("← 뒤로")
        back.setStyleSheet(BACK_BUTTON_STYLE)
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.setFixedHeight(36)
        back.clicked.connect(lambda: self._switch_page(0))

        self.editor_art = QLabel()
        self.editor_art.setFixedSize(56, 56)
        self.editor_art.setMinimumSize(56, 56)
        self.editor_art.setMaximumSize(56, 56)
        self.editor_art.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.editor_art.setStyleSheet(ALBUM_ART_STYLE)
        self.editor_art.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.info_lbl = QLabel("노래 정보")
        self.info_lbl.setStyleSheet(EDITOR_INFO_STYLE)

        top.addWidget(back)
        top.addSpacing(8)
        top.addWidget(self.editor_art)
        top.addSpacing(12)
        top.addWidget(self.info_lbl)
        top.addStretch()
        layout.addLayout(top)

        # Divider (fixed)
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {BORDER_LIGHT};")
        divider.setFixedHeight(1)
        layout.addWidget(divider)

        # Splitter: lyrics editor | preview (STRETCH — takes all remaining space)
        split = QSplitter(Qt.Orientation.Horizontal)
        split.setHandleWidth(1)

        # Left panel
        left = QWidget()
        l_ly = QVBoxLayout(left)
        l_ly.setContentsMargins(0, 4, 8, 0)
        l_ly.setSpacing(6)

        sec_title = QLabel("가사 편집")
        sec_title.setStyleSheet(SECTION_TITLE_STYLE)
        sec_title.setFixedHeight(20)
        l_ly.addWidget(sec_title)

        self.lyrics_edit = QTextEdit()
        self.lyrics_edit.setStyleSheet(TEXT_EDIT_STYLE)
        l_ly.addWidget(self.lyrics_edit, 1)  # stretch

        # Segment control (fixed height)
        split_row = QHBoxLayout()
        split_row.setSpacing(0)
        split_label = QLabel("슬라이드 분할:")
        split_label.setStyleSheet(f"font-size:13px; color:{TEXT_SECONDARY}; margin-right:8px;")
        split_row.addWidget(split_label)

        self._seg_buttons = []
        for n in [1, 2]:
            b = QPushButton(f"{n}줄씩")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedHeight(32)
            b.clicked.connect(lambda _, n=n: self.apply_split(n))
            self._seg_buttons.append((n, b))
            split_row.addWidget(b)

        split_row.addStretch()
        l_ly.addLayout(split_row)
        self._update_segment_buttons()

        # Right panel
        right = QWidget()
        r_ly = QVBoxLayout(right)
        r_ly.setContentsMargins(8, 4, 0, 0)
        r_ly.setSpacing(6)

        preview_header = QHBoxLayout()
        sec_title2 = QLabel("미리보기")
        sec_title2.setStyleSheet(SECTION_TITLE_STYLE)
        sec_title2.setFixedHeight(20)
        hint = QLabel("더블클릭으로 분리/병합")
        hint.setStyleSheet(f"font-size:11px; color:{TEXT_HINT};")
        preview_header.addWidget(sec_title2)
        preview_header.addStretch()
        preview_header.addWidget(hint)
        r_ly.addLayout(preview_header)

        self.prev_list = QListWidget()
        self.prev_list.setStyleSheet(PREVIEW_LIST_STYLE)
        self.prev_list.setSpacing(2)  # 아이템 간 간격
        self.prev_list.itemDoubleClicked.connect(self.on_slide_double_click)
        r_ly.addWidget(self.prev_list, 1)  # stretch

        split.addWidget(left)
        split.addWidget(right)
        split.setSizes([500, 500])
        layout.addWidget(split, 1)  # THIS is the key: stretch factor 1

        # Bottom toolbar (FIXED height)
        bottom = QFrame()
        bottom.setFixedHeight(52)
        bottom.setStyleSheet(f"QFrame {{ background-color: {SURFACE}; border: 1px solid {BORDER_LIGHT}; border-bottom: 2px solid {BORDER_LIGHT}; border-radius: {RADIUS_SM}; }}")
        bl = QHBoxLayout(bottom)
        bl.setContentsMargins(14, 0, 14, 0)

        self.tmpl_lbl = QLabel(f"템플릿: {os.path.basename(self.template_path)}")
        self.tmpl_lbl.setStyleSheet(TEMPLATE_LABEL_STYLE)
        btn_tmpl = QPushButton("변경")
        btn_tmpl.setStyleSheet(SECONDARY_BUTTON_STYLE)
        btn_tmpl.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_tmpl.setFixedHeight(34)
        btn_tmpl.clicked.connect(self.choose_template)

        btn_gen = QPushButton("PPT 생성")
        btn_gen.setStyleSheet(BUTTON_STYLE)
        btn_gen.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_gen.setFixedHeight(38)
        btn_gen.clicked.connect(self.generate_ppt)

        bl.addWidget(self.tmpl_lbl)
        bl.addSpacing(8)
        bl.addWidget(btn_tmpl)
        bl.addStretch()
        bl.addWidget(btn_gen)

        layout.addWidget(bottom)
        self.stack.addWidget(page)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        lbl = self._version_label
        lbl.adjustSize()
        lbl.move(self.width() - lbl.width() - 12, 8)

    # ── Page transition ──
    def _switch_page(self, index):
        old_widget = self.stack.currentWidget()
        self.stack.setCurrentIndex(index)
        new_widget = self.stack.currentWidget()

        # Fade in the new page
        effect = QGraphicsOpacityEffect(new_widget)
        new_widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(200)
        anim.setStartValue(0.3)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._page_anim = anim  # prevent GC
        anim.finished.connect(lambda: new_widget.setGraphicsEffect(None))
        anim.start()

    # ── Segment button state ──
    def _update_segment_buttons(self):
        for n, b in self._seg_buttons:
            if n == self._active_split:
                b.setStyleSheet(SEGMENT_BUTTON_ACTIVE)
            else:
                b.setStyleSheet(SEGMENT_BUTTON_INACTIVE)

    # ── Search ──
    def do_search(self):
        k = self.search_input.text().strip()
        if not k or not self.search_btn.isEnabled(): return
        self.result_list.clear()
        self.search_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.empty_state.setVisible(False)
        self.result_list.setVisible(True)
        t = SearchThread(self.scraper, k)
        t.finished.connect(self.on_search_finished)
        t.error.connect(self.on_thread_error)
        self._threads.append(t)
        t.start()

    def on_search_finished(self, res):
        self.progress.setVisible(False)
        self.search_btn.setEnabled(True)
        if not res:
            self.empty_state.setText("검색 결과가 없습니다")
            self.empty_state.setVisible(True)
            self.result_list.setVisible(False)
            return
        for s in res:
            item_w = SongItemWidget(s.get('title', ''), s.get('artist', ''), s.get('album', ''))
            item = QListWidgetItem(self.result_list)
            # 위젯의 sizeHint()가 margin 포함 (SlideItemWidget 패턴)
            item.setSizeHint(item_w.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, s)
            self.result_list.addItem(item)
            self.result_list.setItemWidget(item, item_w)
            # 앨범아트 비동기 로드 (상세 페이지에서 가져옴)
            song_id = s.get('song_id', '')
            if song_id:
                loader = AlbumArtLoaderThread(self.scraper, song_id)
                target_label = item_w.img_label
                loader.loaded.connect(lambda data, lbl=target_label: self._set_thumbnail(lbl, data))
                self._threads.append(loader)
                loader.start()

    def on_song_select(self, item):
        sd = item.data(Qt.ItemDataRole.UserRole)
        if not sd: return
        self.info_lbl.setText(f"{sd.get('title', '')} — {sd.get('artist', '')}")
        self.progress.setVisible(True)
        self.search_btn.setEnabled(False)
        t = DetailThread(self.scraper, sd.get('song_id'))
        t.finished.connect(self.on_detail_finished)
        t.error.connect(self.on_thread_error)
        self._threads.append(t)
        t.start()

    def on_detail_finished(self, det):
        self.lyrics_edit.setPlainText(det.get('lyrics', ''))
        if det.get('image_url'):
            it = ImageLoaderThread(det.get('image_url'))
            it.loaded.connect(self.on_editor_art_loaded)
            self._threads.append(it)
            it.start()
        self.apply_split(2)
        QTimer.singleShot(10, self.show_editor)

    def show_editor(self):
        self.progress.setVisible(False)
        self.search_btn.setEnabled(True)
        self._switch_page(1)

    def on_thread_error(self, error_msg):
        self.progress.setVisible(False)
        self.search_btn.setEnabled(True)
        show_critical_error(self, "작업 중 오류가 발생했습니다.", error_msg)

    def _set_thumbnail(self, label, data):
        px = QPixmap()
        if px.loadFromData(data):
            # 정사각형으로 center crop
            s = min(px.width(), px.height())
            x = (px.width() - s) // 2
            y = (px.height() - s) // 2
            px = px.copy(x, y, s, s)

            # 라벨의 고정 크기 가져오기 (width == height이어야 함)
            target_size = label.width() if label.width() > 0 else label.height()
            if target_size <= 0:
                # 레이아웃 전이면 고정 크기 사용
                target_size = 48

            # 정사각형으로 스케일링
            label.setPixmap(px.scaled(
                target_size, target_size,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))

    def on_editor_art_loaded(self, data):
        self._set_thumbnail(self.editor_art, data)

    # ── Slide editing ──
    def apply_split(self, n):
        self._active_split = n
        self._update_segment_buttons()
        self.slide_chunks = PPTBuilder.split_lyrics(self.lyrics_edit.toPlainText(), n)
        self.refresh_preview()

    def refresh_preview(self):
        self.prev_list.clear()
        for i, c in enumerate(self.slide_chunks):
            slide_widget = SlideItemWidget(i + 1, c)
            item = QListWidgetItem(self.prev_list)
            item.setSizeHint(slide_widget.sizeHint())
            self.prev_list.addItem(item)
            self.prev_list.setItemWidget(item, slide_widget)

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
        rest_lines = remaining
        for chunk in self.slide_chunks[idx + 1:]:
            rest_lines.extend(chunk.split('\n'))
        new_chunks = self.slide_chunks[:idx]
        new_chunks.append(first_line)
        for i in range(0, len(rest_lines), 2):
            new_chunks.append("\n".join(rest_lines[i:i + 2]))
        self.slide_chunks = new_chunks
        self.refresh_preview()

    def choose_template(self):
        p, _ = QFileDialog.getOpenFileName(self, "PPT 템플릿", "", "PowerPoint (*.pptx)")
        if p:
            self.template_path = p
            self.tmpl_lbl.setText(f"템플릿: {os.path.basename(p)}")

    def generate_ppt(self):
        lyrics_text = self.lyrics_edit.toPlainText()
        if not lyrics_text.strip():
            QMessageBox.warning(self, "알림", "가사가 없습니다.")
            return

        if not os.path.exists(self.template_path):
            show_critical_error(self, "템플릿 파일을 찾을 수 없습니다.", f"경로: {self.template_path}")
            return

        default_filename = f"{self.info_lbl.text().replace('/', '_')}.pptx"
        save_path, _ = QFileDialog.getSaveFileName(self, "PPT 저장", default_filename, "PowerPoint (*.pptx)")

        if not save_path:
            return

        try:
            chunks = self.slide_chunks if self.slide_chunks else PPTBuilder.split_lyrics(lyrics_text, 2)
            builder = PPTBuilder(self.template_path)
            ppt_buffer = builder.generate_slides_to_memory(chunks)

            if not ppt_buffer:
                show_critical_error(self, "PPT 생성 실패.", "메모리에서 PPT 객체를 생성하지 못했습니다.")
                return

            if PPTBuilder.save_to_file(ppt_buffer, save_path):
                toast = ToastWidget(self, "PPT 생성이 완료되었습니다!")
                toast.show_toast()
            else:
                show_critical_error(self, "파일 저장 실패.", f"다음 경로에 파일을 쓸 수 없습니다:\n{save_path}\n\n권한 문제를 확인해주세요.")

        except Exception:
            show_critical_error(self, "PPT 생성 중 예외가 발생했습니다.", traceback.format_exc())
