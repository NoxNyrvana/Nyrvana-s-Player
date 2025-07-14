import sys
import os
import json

ffmpeg_bin_path = os.path.join(os.path.dirname(sys.executable), "ffmpeg", "bin")
os.environ["PATH"] = ffmpeg_bin_path + os.pathsep + os.environ.get("PATH", "")

import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QListWidget, QSlider
)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPixmap, QFont

from core.actions import (
    load_playlist_from_folder, play_music, pause_music, stop_music,
    load_track_by_index, get_current_position_ms, get_current_track_duration_ms,
    set_volume, playlist, get_current_track_name, get_current_index, set_current_index,
    seek_to_position
)

from core.visualizer import AudioVisualizer

def ms_to_mmss(ms: int) -> str:
    seconds = ms // 1000
    return f"{seconds // 60:02}:{seconds % 60:02}"

def load_config(path="config.json") -> dict:
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class MusicApp(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.is_playing = False
        self.track_finished = False
        self._drag_pos = None

        self.setup_window()
        self.setup_ui()
        self.load_music()

        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start()

        self.on_volume_change(self.volume_slider.value())

        self.show()

    def setup_window(self):
        cfg = self.config.get("window", {})
        width = cfg.get("width", 270)
        height = cfg.get("height", 450)

        self.setFixedSize(width, height)
        self.setWindowTitle(cfg.get("title", "Lecteur de musique"))

        bg_color = cfg.get("background_color", "#9141ac")
        self.setStyleSheet(f"background-color: {bg_color};")

        self.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        bg_path = cfg.get("background_image_path", "")
        if bg_path and os.path.isfile(bg_path):
            pixmap = QPixmap(bg_path).scaled(width, height, Qt.AspectRatioMode.KeepAspectRatioByExpanding)
            self.bg_label = QLabel(self)
            self.bg_label.setPixmap(pixmap)
            self.bg_label.setGeometry(0, 0, width, height)
            self.bg_label.lower()
            self.bg_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(8)

        btn_cfg = self.config.get("buttons", {})
        font_family = btn_cfg.get("font_family", "Arial")
        font_size = btn_cfg.get("font_size", 14)
        self.app_font = QFont(font_family, font_size)

        # ----- barre titre ---------------
        title_bar = QHBoxLayout()
        title_bar.setSpacing(5)

        self.title = QLabel(" ")
        self.title.setStyleSheet("color: white; font-size: 14px;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_bar.addWidget(self.title)
        title_bar.addStretch()

        def create_btn_from_config(symbol, callback):
            cfg = self.config.get("buttons", {}).get("rewind_backward", {})
            size = cfg.get("size", [30, 30])
            color = cfg.get("color", "#ffffff")
            text_color = cfg.get("text_color", "#000000")
            shape = cfg.get("shape", "")
            border_radius = 8 if shape == "rounded" else 0
            image_path = cfg.get("image_path", "")

            btn = QPushButton(symbol)
            btn.setFont(self.app_font)
            btn.setFixedSize(*size)

            if image_path and os.path.isfile(image_path):
                btn.setText("")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        border-radius: {border_radius}px;
                        background-image: url({image_path});
                        background-repeat: no-repeat;
                        background-position: center;
                        border: none;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    background-color: {color};
                    color: {text_color};
                    border-radius: {border_radius}px;
                """)

            btn.clicked.connect(callback)
            return btn

        self.config_button = create_btn_from_config("☼", self.launch_config_ui)
        self.search_button = create_btn_from_config("♫", self.launch_research_ui)
        self.reload_button = create_btn_from_config("⤷", self.reload_app)
        self.btn_minimize = create_btn_from_config("—", self.showMinimized)
        self.btn_close = create_btn_from_config("✕", self.close)

        for btn in [self.config_button, self.search_button, self.reload_button,
                    self.btn_minimize, self.btn_close]:
            title_bar.addWidget(btn)

        main_layout.addLayout(title_bar)

        # ----- playlist -------------------
        self.list_widget = QListWidget()
        self.list_widget.setFont(self.app_font)
        self.list_widget.clicked.connect(self.select_track)
        main_layout.addWidget(self.list_widget)

        self.track_label = QLabel("")
        self.track_label.setFont(self.app_font)
        self.track_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.track_label.setStyleSheet("color: white; background: transparent;")
        main_layout.addWidget(self.track_label)

        # ----- Barre de progression -----
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setTextVisible(False)

        pb_cfg = self.config.get("progress_bar", {})
        chunk_color = pb_cfg.get("color", "#d09dd2")
        bg_color = pb_cfg.get("background_color", "#350b4a")
        radius = pb_cfg.get("radius", 10)
        height = pb_cfg.get("height", 10)

        self.progress_bar.setFixedHeight(height)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {bg_color};
                border-radius: {radius}px;
            }}
            QProgressBar::chunk {{
                background-color: {chunk_color};
                border-radius: {radius}px;
            }}
        """)
        self.progress_bar.mousePressEvent = self.progress_clicked
        main_layout.addWidget(self.progress_bar)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setFont(self.app_font)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("color: white; background: transparent;")
        main_layout.addWidget(self.time_label)

        # ----- controles musique -------------
        controls = QHBoxLayout()
        self.buttons = {}

        def create_btn(name, symbol, handler):
            cfg = self.config.get("buttons", {}).get(name, {})
            size = cfg.get("size", [30, 30])
            color = cfg.get("color", "#613583")
            text_color = self.config.get("buttons", {}).get("text_color", "#FFFFFF")
            border_radius = 8 if cfg.get("shape", "") == "rounded" else 0
            image_path = cfg.get("image_path", "")

            btn = QPushButton(symbol)
            btn.setFont(self.app_font)
            btn.setFixedSize(*size)

            if image_path and os.path.isfile(image_path):
                btn.setText("")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        border-radius: {border_radius}px;
                        background-image: url({image_path});
                        background-repeat: no-repeat;
                        background-position: center;
                        border: none;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    background-color: {color};
                    color: {text_color};
                    border-radius: {border_radius}px;
                """)

            btn.clicked.connect(handler)
            return btn

        self.buttons["rewind"] = create_btn("rewind", "❮❮", self.on_skip_back)
        self.buttons["play"] = create_btn("play", "➤", self.on_toggle_play_pause)
        self.buttons["forward"] = create_btn("forward", "❯❯", self.on_skip)

        for btn in ["rewind", "play", "forward"]:
            controls.addWidget(self.buttons[btn])
        main_layout.addLayout(controls)

        # ----- volume ------------------
        volume_layout = QHBoxLayout()
        self.volume_label = QLabel("❘❘❙❙")
        self.volume_label.setFont(self.app_font)
        self.volume_label.setStyleSheet("background: transparent;")

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.on_volume_change)

        volume_layout.addWidget(self.volume_label)
        volume_layout.addWidget(self.volume_slider)
        main_layout.addLayout(volume_layout)

        # ----- visualiseur ---------------
        self.visualizer = AudioVisualizer()
        self.visualizer.configure(self.config)
        main_layout.addWidget(self.visualizer)

    def launch_config_ui(self):
        try:
            subprocess.Popen([sys.executable, "config_ui.py"])
        except Exception as e:
            print(f"Erreur lancement config_ui.py : {e}")

    def launch_research_ui(self):
        try:
            subprocess.Popen([sys.executable, "research.py"])
        except Exception as e:
            print(f"Erreur lancement research.py : {e}")

    def reload_app(self):
        try:
            subprocess.Popen([sys.executable, "main.py"])
            QApplication.quit()
        except Exception as e:
            print(f"Erreur lors du redémarrage : {e}")

    def load_music(self):
        music_dir = os.path.join(os.getcwd(), "assets", "music")
        os.makedirs(music_dir, exist_ok=True)
        load_playlist_from_folder(music_dir)
        self.list_widget.clear()
        for path in playlist:
            self.list_widget.addItem(os.path.basename(path))
        if playlist:
            set_current_index(0)
            load_track_by_index(0)
            self.track_finished = False
            self.list_widget.setCurrentRow(0)
            self.update_track_label()
            self.visualizer.load_audio(playlist[get_current_index()])
        else:
            self.track_label.setText("Aucune musique trouvée")

    def update_track_label(self):
        name = get_current_track_name()
        self.track_label.setText(name or "Aucune musique")
        try:
            idx = playlist.index(os.path.join(os.getcwd(), "assets", "music", name))
            self.list_widget.setCurrentRow(idx)
        except ValueError:
            pass

    def update_progress(self):
        pos = get_current_position_ms()
        dur = get_current_track_duration_ms()
        if dur > 0:
            self.progress_bar.setValue(int((pos / dur) * 1000))
            self.time_label.setText(f"{ms_to_mmss(pos)} / {ms_to_mmss(dur)}")


            if not self.track_finished:
                if pos >= dur - 500:
                    self.track_finished = True
                    self.on_skip()
            else:
                if pos < dur - 1000:
                    self.track_finished = False

        else:
            self.progress_bar.setValue(0)
            self.time_label.setText("00:00 / 00:00")
        self.visualizer.update_visualizer(pos)

    def progress_clicked(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            ratio = event.position().x() / self.progress_bar.width()
            seek_to_position(int(get_current_track_duration_ms() * ratio))

    def select_track(self, index):
        i = index.row()
        if 0 <= i < len(playlist):
            set_current_index(i)
            load_track_by_index(i)
            self.track_finished = False
            self.update_track_label()
            self.visualizer.load_audio(playlist[i])
            if self.is_playing:
                play_music()

    def on_toggle_play_pause(self):
        if self.is_playing:
            pause_music()
            self.is_playing = False
            self.buttons["play"].setText("➤")
        else:
            play_music()
            self.is_playing = True
            self.buttons["play"].setText("ןן")

    def on_skip(self):
        i = (get_current_index() + 1) % len(playlist)
        set_current_index(i)
        load_track_by_index(i)
        self.track_finished = False
        self.update_track_label()
        self.visualizer.load_audio(playlist[i])
        if self.is_playing:
            play_music()

    def on_skip_back(self):
        i = (get_current_index() - 1) % len(playlist)
        set_current_index(i)
        load_track_by_index(i)
        self.track_finished = False
        self.update_track_label()
        self.visualizer.load_audio(playlist[i])
        if self.is_playing:
            play_music()

    def on_volume_change(self, value):
        set_volume(value / 100)
        if value == 0:
            self.volume_label.setText(" ")
        elif value < 30:
            self.volume_label.setText(" ")
        elif value < 70:
            self.volume_label.setText(" ")
        else:
            self.volume_label.setText(" ")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MusicApp()
    sys.exit(app.exec())
