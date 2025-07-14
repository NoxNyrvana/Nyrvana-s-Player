import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QMovie
import yt_dlp

# === lecture config.json ======
def load_config(path="config.json"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# === thread téléchargement =====
class DownloadThread(QThread):
    started_signal = pyqtSignal()
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, query: str, output_dir='assets/music'):
        super().__init__()
        self.query = query
        self.output_dir = output_dir

    def run(self):
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'noplaylist': True,
            }
            self.started_signal.emit()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"ytsearch1:{self.query}"])
            self.finished_signal.emit("Téléchargement terminé.")
        except Exception as e:
            self.error_signal.emit(str(e))

# === interface ===========
class MP3DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.setWindowTitle("Téléchargeur MP3 YouTube")
        win_cfg = self.config.get("window", {})
        self.setFixedSize(win_cfg.get("width", 400), win_cfg.get("height", 180))
        self.setStyleSheet(f"background-color: {win_cfg.get('background_color', '#222')};")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Entrez un titre de musique...")
        self.search_input.returnPressed.connect(self.start_download)
        layout.addWidget(self.search_input)

        self.search_button = QPushButton("Rechercher et Télécharger")
        self.search_button.clicked.connect(self.start_download)
        layout.addWidget(self.search_button)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # === GIF loading =========
        self.loading_gif = QMovie("assets/gifs/load.gif")
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setMovie(self.loading_gif)
        self.loading_label.setVisible(False)  # Caché par défaut
        layout.addWidget(self.loading_label)

        self.setLayout(layout)

    def start_download(self):
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un titre.")
            return

        self.search_button.setEnabled(False)
        self.status_label.setText("🔍 Recherche et téléchargement en cours...")

        # animation gif
        self.loading_label.setVisible(True)
        self.loading_gif.start()

        self.thread = DownloadThread(query)
        self.thread.started_signal.connect(lambda: self.status_label.setText("Téléchargement..."))
        self.thread.finished_signal.connect(self.on_finished)
        self.thread.error_signal.connect(self.on_error)
        self.thread.start()

    def on_finished(self, message):
        self.status_label.setText(message)
        self.search_button.setEnabled(True)
        self.loading_label.setVisible(False)
        self.loading_gif.stop()

    def on_error(self, error_msg):
        self.status_label.setText("❌ Erreur lors du téléchargement.")
        QMessageBox.critical(self, "Erreur", error_msg)
        self.search_button.setEnabled(True)
        self.loading_label.setVisible(False)
        self.loading_gif.stop()

# === porte d’entrée ==============
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MP3DownloaderApp()
    window.show()
    sys.exit(app.exec())
