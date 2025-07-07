from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
from pydub import AudioSegment
import numpy as np
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

class AudioVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Rendre le widget lui-même transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(None)  # fond transparent pyqtgraph
        self.plot_widget.setYRange(0, 1)
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.hideAxis('bottom')
        self.plot_widget.hideAxis('left')
        self.plot_widget.getPlotItem().layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(self.plot_widget)

        # Valeurs par défaut
        self.num_bars = 30
        self.intensity = 1.0
        self.bar_width = 0.8
        self.color_start = (0, 255, 0)  # vert
        self.color_end = (255, 0, 0)    # rouge

        self.data = np.zeros(self.num_bars)
        self.x = np.arange(self.num_bars)

        self.brushes = self._generate_brushes()
        self.bar_graph = pg.BarGraphItem(
            x=self.x, height=self.data, width=self.bar_width, brushes=self.brushes
        )
        self.plot_widget.addItem(self.bar_graph)

        self.audio_segment = None

    def _generate_brushes(self):
        brushes = []
        for i in range(self.num_bars):
            ratio = i / max(self.num_bars - 1, 1)
            r = int(self.color_start[0] * (1 - ratio) + self.color_end[0] * ratio)
            g = int(self.color_start[1] * (1 - ratio) + self.color_end[1] * ratio)
            b = int(self.color_start[2] * (1 - ratio) + self.color_end[2] * ratio)
            color = QColor(r, g, b)
            brushes.append(pg.mkBrush(color))
        return brushes

    def configure(self, config=None):
        """
        Configure le visualiseur selon un dictionnaire de configuration.
        Si aucun config n'est donné, applique les valeurs par défaut.
        """
        if config and isinstance(config, dict):
            vis_cfg = config.get("visualizer", {})
            self.num_bars = vis_cfg.get("num_bars", 30)
            self.intensity = vis_cfg.get("intensity", 1.0)
            self.bar_width = vis_cfg.get("bar_width", 0.8)  # optionnel dans JSON
            colors = [
                vis_cfg.get("color_start", "#00FF00"),
                vis_cfg.get("color_end", "#FF0000"),
            ]
            self.color_start = self._color_to_rgb(colors[0])
            self.color_end = self._color_to_rgb(colors[1])
        else:
            # Valeurs par défaut
            self.num_bars = 30
            self.intensity = 1.0
            self.bar_width = 0.8
            self.color_start = (0, 255, 0)
            self.color_end = (255, 0, 0)

        self.x = np.arange(self.num_bars)
        self.data = np.zeros(self.num_bars)
        self.plot_widget.clear()

        self.brushes = self._generate_brushes()
        self.bar_graph = pg.BarGraphItem(
            x=self.x, height=self.data, width=self.bar_width, brushes=self.brushes
        )
        self.plot_widget.addItem(self.bar_graph)

    def _color_to_rgb(self, color):
        """
        Convertit une couleur hex en tuple RGB.
        Accepte aussi directement un tuple RGB.
        """
        if isinstance(color, tuple) and len(color) == 3:
            return color
        if isinstance(color, str):
            color = color.lstrip("#")
            lv = len(color)
            return tuple(
                int(color[i : i + lv // 3], 16) for i in range(0, lv, lv // 3)
            )
        return (0, 255, 0)  # default vert

    def load_audio(self, file_path):
        self.audio_segment = AudioSegment.from_file(file_path)

    def update_visualizer(self, position_ms):
        if self.audio_segment is None:
            self.data = np.zeros(self.num_bars)
            self.bar_graph.setOpts(height=self.data)
            return

        window_size = 100  # fenêtre de 100 ms
        start = int(position_ms)
        end = min(start + window_size, len(self.audio_segment))

        chunk = self.audio_segment[start:end]
        samples = np.array(chunk.get_array_of_samples())

        if chunk.channels == 2:
            samples = samples[::2]

        if len(samples) == 0:
            self.data = np.zeros(self.num_bars)
            self.bar_graph.setOpts(height=self.data)
            return

        fft = np.abs(np.fft.rfft(samples))
        max_fft = np.max(fft)
        if max_fft != 0:
            fft = fft / max_fft
        fft = fft * self.intensity

        bins = np.array_split(fft, self.num_bars)
        magnitudes = np.array([np.mean(b) for b in bins])
        magnitudes = np.clip(magnitudes, 0, 1)

        self.data = magnitudes
        self.bar_graph.setOpts(height=self.data)
