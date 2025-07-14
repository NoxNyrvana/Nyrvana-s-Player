import json
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QColorDialog,
    QComboBox, QSpinBox, QFileDialog, QApplication, QHBoxLayout,
    QSlider, QTabWidget, QScrollArea
)
from PyQt6.QtGui import QColor, QFontDatabase
from PyQt6.QtCore import Qt
import pyqtgraph as pg

CONFIG_FILE = "config.json"

class ButtonConfigUI(QWidget):
    def __init__(self, button_name, config):
        super().__init__()
        self.button_name = button_name
        self.config = config

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Configuration du bouton '{button_name}'"))

        # Forme
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["rounded", "square"])
        self.shape_combo.setCurrentText(self.config[button_name].get("shape", "rounded"))
        layout.addWidget(QLabel("Forme"))
        layout.addWidget(self.shape_combo)

        # Couleur de fond
        self.color_button = QPushButton("Choisir couleur de fond")
        bg_color = self.config[button_name].get("color", "#FFFFFF")
        self.color_button.setStyleSheet(f"background-color: {bg_color}")
        self.color_button.clicked.connect(self.pick_bg_color)
        layout.addWidget(QLabel("Couleur de fond"))
        layout.addWidget(self.color_button)

        # Taille
        size_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(10, 200)
        self.width_spin.setValue(self.config[button_name].get("size", [50, 50])[0])
        self.height_spin = QSpinBox()
        self.height_spin.setRange(10, 200)
        self.height_spin.setValue(self.config[button_name].get("size", [50, 50])[1])
        size_layout.addWidget(QLabel("Largeur"))
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("Hauteur"))
        size_layout.addWidget(self.height_spin)
        layout.addWidget(QLabel("Taille"))
        layout.addLayout(size_layout)

        # Image ou GIF
        self.image_button = QPushButton("Charger image/GIF")
        self.image_button.clicked.connect(self.load_image)
        layout.addWidget(self.image_button)

        img_path = self.config[button_name].get("image_path", "")
        self.image_path_label = QLabel(img_path if img_path else "Aucune image chargée")
        layout.addWidget(self.image_path_label)

    def pick_bg_color(self):
        current = QColor(self.config[self.button_name].get("color", "#FFFFFF"))
        color = QColorDialog.getColor(current, self, "Choisir couleur")
        if color.isValid():
            self.config[self.button_name]["color"] = color.name()
            self.color_button.setStyleSheet(f"background-color: {color.name()}")

    def load_image(self):
        dlg = QFileDialog(self, "Choisir une image ou un GIF")
        dlg.setNameFilters(["Images (*.png *.jpg *.bmp *.gif)"])
        if dlg.exec():
            path = dlg.selectedFiles()[0]
            self.config[self.button_name]["image_path"] = path
            self.image_path_label.setText(path)

    def update_config(self):
        self.config[self.button_name]["shape"] = self.shape_combo.currentText()
        self.config[self.button_name]["size"] = [self.width_spin.value(), self.height_spin.value()]

class ConfigUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuration Interface")
        self.config = self.load_config()

        self.resize(self.config["window"].get("width", 800), self.config["window"].get("height", 600))
        self.setStyleSheet(f"background-color: {self.config['window'].get('background_color', '#FFFFFF')};")

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.scroll.setWidget(self.container)
        self.main_layout = QVBoxLayout(self.container)

        self.add_window_config_ui()
        self.add_buttons_general_ui()
        self.add_buttons_detailed_ui()
        self.add_progress_bar_ui()
        self.add_volume_bar_ui()
        self.add_visualizer_ui()

        self.save_button = QPushButton("Enregistrer la configuration")
        self.save_button.clicked.connect(self.save_config)
        self.main_layout.addWidget(self.save_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll)

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                loaded = json.load(f)
                return self.merge_defaults(self.default_config(), loaded)
        except Exception:
            return self.default_config()

    def default_config(self):
        return {
            "window": {
                "width": 800,
                "height": 600,
                "background_color": "#FFFFFF",
                "background_image_path": ""
            },
            "buttons": {
                "font_family": "Arial",
                "font_path": "",
                "font_size": 12,
                "text_color": "#000000",
                "play": {"shape": "rounded", "color": "#FFFFFF", "size": [50, 50], "image_path": ""},
                "loop": {"shape": "rounded", "color": "#FFFFFF", "size": [50, 50], "image_path": ""},
                "rewind": {"shape": "rounded", "color": "#FFFFFF", "size": [50, 50], "image_path": ""},
                "forward": {"shape": "rounded", "color": "#FFFFFF", "size": [50, 50], "image_path": ""},
                "rewind_backward": {"shape": "rounded", "color": "#FFFFFF", "size": [50, 50], "image_path": ""}
            },
            "progress_bar": {
                "color": "#00FF00",
                "background_color": "#444444",
                "height": 20,
                "radius": 10
            },
            "visualizer": {
                "num_bars": 20,
                "color_start": "#FF0000",
                "color_end": "#0000FF",
                "intensity": 1.0
            },
            "volume_bar": {
                "background_color": "#333333",
                "slider_color": "#00FF00",
                "height": 10,
                "slider_shape": "rounded",
                "radius": 5
            }           
        }

    def add_window_config_ui(self):
        self.main_layout.addWidget(QLabel("Couleur de fond de la fenêtre :"))
        self.bg_color_btn = QPushButton()
        color = self.config["window"].get("background_color", "#FFFFFF")
        self.bg_color_btn.setStyleSheet(f"background-color: {color}")
        self.bg_color_btn.clicked.connect(self.pick_bg_color)
        self.main_layout.addWidget(self.bg_color_btn)

        self.main_layout.addWidget(QLabel("Image de fond :"))
        self.bg_img_btn = QPushButton("Choisir image/GIF")
        self.bg_img_btn.clicked.connect(self.pick_bg_image)
        self.main_layout.addWidget(self.bg_img_btn)

        img_path = self.config["window"].get("background_image_path", "")
        self.bg_img_label = QLabel(img_path if img_path else "Aucune image chargée")
        self.main_layout.addWidget(self.bg_img_label)

        self.main_layout.addWidget(QLabel("Taille de la fenêtre :"))
        size_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(200, 1920)
        self.width_spin.setValue(self.config["window"].get("width", 800))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(200, 1080)
        self.height_spin.setValue(self.config["window"].get("height", 600))
        size_layout.addWidget(QLabel("Largeur"))
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("Hauteur"))
        size_layout.addWidget(self.height_spin)
        self.main_layout.addLayout(size_layout)
        
    def merge_defaults(self, defaults, loaded):
        if not isinstance(loaded, dict):
            return defaults
        result = dict(defaults)
        for k, v in defaults.items():
            if k not in loaded:
                result[k] = v
            else:
                if isinstance(v, dict):
                    result[k] = self.merge_defaults(v, loaded[k])
                else:
                    result[k] = loaded[k]
        return result

        
    def add_volume_bar_ui(self):
        self.main_layout.addWidget(QLabel("--- Configuration de la barre de volume ---"))
        self.volume_slider_color_btn = QPushButton()
        self.volume_slider_color_btn.setStyleSheet(f"background-color: {self.config['volume_bar']['slider_color']}")
        self.volume_slider_color_btn.clicked.connect(self.pick_volume_slider_color)
        self.main_layout.addWidget(QLabel("Couleur du slider"))
        self.main_layout.addWidget(self.volume_slider_color_btn)

        self.volume_bg_color_btn = QPushButton()
        self.volume_bg_color_btn.setStyleSheet(f"background-color: {self.config['volume_bar']['background_color']}")
        self.volume_bg_color_btn.clicked.connect(self.pick_volume_bg_color)
        self.main_layout.addWidget(QLabel("Couleur du fond"))
        self.main_layout.addWidget(self.volume_bg_color_btn)

        self.volume_height_spin = QSpinBox()
        self.volume_height_spin.setRange(1, 50)
        self.volume_height_spin.setValue(self.config["volume_bar"]["height"])
        self.main_layout.addWidget(QLabel("Hauteur"))
        self.main_layout.addWidget(self.volume_height_spin)

        self.volume_radius_spin = QSpinBox()
        self.volume_radius_spin.setRange(0, 30)
        self.volume_radius_spin.setValue(self.config["volume_bar"]["radius"])
        self.main_layout.addWidget(QLabel("Rayon"))
        self.main_layout.addWidget(self.volume_radius_spin)

        self.volume_slider_shape_combo = QComboBox()
        self.volume_slider_shape_combo.addItems(["rounded", "square"])
        self.volume_slider_shape_combo.setCurrentText(self.config["volume_bar"]["slider_shape"])
        self.main_layout.addWidget(QLabel("Forme du slider"))
        self.main_layout.addWidget(self.volume_slider_shape_combo)

    def pick_volume_slider_color(self):
        current = QColor(self.config['volume_bar']['slider_color'])
        color = QColorDialog.getColor(current, self, "Choisir couleur du slider volume")
        if color.isValid():
            self.config['volume_bar']['slider_color'] = color.name()
            self.volume_slider_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def pick_volume_bg_color(self):
        current = QColor(self.config['volume_bar']['background_color'])
        color = QColorDialog.getColor(current, self, "Choisir couleur de fond volume")
        if color.isValid():
            self.config['volume_bar']['background_color'] = color.name()
            self.volume_bg_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def add_buttons_general_ui(self):
        self.main_layout.addWidget(QLabel("--- Configuration générale des boutons ---"))
        self.main_layout.addWidget(QLabel("Police de caractères :"))

        self.font_family_combo = QComboBox()
        fonts = QFontDatabase.families()
        self.font_family_combo.addItems(fonts)
        self.font_family_combo.setCurrentText(self.config["buttons"].get("font_family", "Arial"))
        self.main_layout.addWidget(self.font_family_combo)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(5, 50)
        self.font_size_spin.setValue(self.config["buttons"].get("font_size", 12))
        self.main_layout.addWidget(QLabel("Taille de police"))
        self.main_layout.addWidget(self.font_size_spin)

        self.main_layout.addWidget(QLabel("Couleur du texte"))
        self.text_color_btn = QPushButton()
        self.text_color_btn.setStyleSheet(f"background-color: {self.config['buttons']['text_color']}")
        self.text_color_btn.clicked.connect(self.pick_text_color)
        self.main_layout.addWidget(self.text_color_btn)

    def pick_text_color(self):
        current = QColor(self.config['buttons']['text_color'])
        color = QColorDialog.getColor(current, self, "Choisir couleur du texte")
        if color.isValid():
            self.config['buttons']['text_color'] = color.name()
            self.text_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def add_buttons_detailed_ui(self):
        self.main_layout.addWidget(QLabel("--- Configuration détaillée des boutons ---"))
        self.buttons_tabs = QTabWidget()
        self.button_config_uis = {}
        for btn_name in self.config["buttons"]:
            if btn_name in ("font_family", "font_size", "text_color", "font_path"):
                continue
            ui = ButtonConfigUI(btn_name, self.config["buttons"])
            self.buttons_tabs.addTab(ui, btn_name.capitalize())
            self.button_config_uis[btn_name] = ui
        self.main_layout.addWidget(self.buttons_tabs)

    def add_progress_bar_ui(self):
        self.main_layout.addWidget(QLabel("--- Configuration de la barre de progression ---"))
        self.progress_color_btn = QPushButton()
        self.progress_color_btn.setStyleSheet(f"background-color: {self.config['progress_bar']['color']}")
        self.progress_color_btn.clicked.connect(self.pick_progress_color)
        self.main_layout.addWidget(QLabel("Couleur"))
        self.main_layout.addWidget(self.progress_color_btn)

        self.progress_bg_color_btn = QPushButton()
        self.progress_bg_color_btn.setStyleSheet(f"background-color: {self.config['progress_bar']['background_color']}")
        self.progress_bg_color_btn.clicked.connect(self.pick_progress_bg_color)
        self.main_layout.addWidget(QLabel("Couleur du fond"))
        self.main_layout.addWidget(self.progress_bg_color_btn)

        self.progress_height_spin = QSpinBox()
        self.progress_height_spin.setRange(1, 100)
        self.progress_height_spin.setValue(self.config["progress_bar"]["height"])
        self.main_layout.addWidget(QLabel("Hauteur"))
        self.main_layout.addWidget(self.progress_height_spin)

        self.progress_radius_spin = QSpinBox()
        self.progress_radius_spin.setRange(0, 50)
        self.progress_radius_spin.setValue(self.config["progress_bar"]["radius"])
        self.main_layout.addWidget(QLabel("Rayon"))
        self.main_layout.addWidget(self.progress_radius_spin)

    def pick_progress_color(self):
        current = QColor(self.config['progress_bar']['color'])
        color = QColorDialog.getColor(current, self, "Choisir couleur de la barre de progression")
        if color.isValid():
            self.config['progress_bar']['color'] = color.name()
            self.progress_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def pick_progress_bg_color(self):
        current = QColor(self.config['progress_bar']['background_color'])
        color = QColorDialog.getColor(current, self, "Choisir couleur de fond de la barre de progression")
        if color.isValid():
            self.config['progress_bar']['background_color'] = color.name()
            self.progress_bg_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def add_visualizer_ui(self):
        self.main_layout.addWidget(QLabel("--- Configuration du visualiseur ---"))
        self.num_bars_spin = QSpinBox()
        self.num_bars_spin.setRange(1, 100)
        self.num_bars_spin.setValue(self.config["visualizer"]["num_bars"])
        self.main_layout.addWidget(QLabel("Nombre de barres"))
        self.main_layout.addWidget(self.num_bars_spin)

        self.color_start_btn = QPushButton()
        self.color_start_btn.setStyleSheet(f"background-color: {self.config['visualizer']['color_start']}")
        self.color_start_btn.clicked.connect(self.pick_visualizer_color_start)
        self.main_layout.addWidget(QLabel("Couleur de début"))
        self.main_layout.addWidget(self.color_start_btn)

        self.color_end_btn = QPushButton()
        self.color_end_btn.setStyleSheet(f"background-color: {self.config['visualizer']['color_end']}")
        self.color_end_btn.clicked.connect(self.pick_visualizer_color_end)
        self.main_layout.addWidget(QLabel("Couleur de fin"))
        self.main_layout.addWidget(self.color_end_btn)

        self.intensity_spin = QSpinBox()
        self.intensity_spin.setRange(1, 50)
        self.intensity_spin.setValue(int(self.config["visualizer"]["intensity"] * 10))
        self.main_layout.addWidget(QLabel("Intensité (1-50)"))
        self.main_layout.addWidget(self.intensity_spin)

    def pick_visualizer_color_start(self):
        current = QColor(self.config['visualizer']['color_start'])
        color = QColorDialog.getColor(current, self, "Choisir couleur début visualiseur")
        if color.isValid():
            self.config['visualizer']['color_start'] = color.name()
            self.color_start_btn.setStyleSheet(f"background-color: {color.name()}")

    def pick_visualizer_color_end(self):
        current = QColor(self.config['visualizer']['color_end'])
        color = QColorDialog.getColor(current, self, "Choisir couleur fin visualiseur")
        if color.isValid():
            self.config['visualizer']['color_end'] = color.name()
            self.color_end_btn.setStyleSheet(f"background-color: {color.name()}")

    def pick_bg_color(self):
        current = QColor(self.config["window"].get("background_color", "#FFFFFF"))
        color = QColorDialog.getColor(current, self, "Choisir couleur de fond")
        if color.isValid():
            self.config["window"]["background_color"] = color.name()
            self.bg_color_btn.setStyleSheet(f"background-color: {color.name()}")
            self.setStyleSheet(f"background-color: {color.name()};")

    def pick_bg_image(self):
        dlg = QFileDialog(self, "Choisir une image ou un GIF")
        dlg.setNameFilters(["Images (*.png *.jpg *.bmp *.gif)"])
        if dlg.exec():
            path = dlg.selectedFiles()[0]
            self.config["window"]["background_image_path"] = path
            self.bg_img_label.setText(path)

    def save_config(self):
        # Update from UI controls to config dictionary
        self.config["window"]["width"] = self.width_spin.value()
        self.config["window"]["height"] = self.height_spin.value()
        self.config["buttons"]["font_family"] = self.font_family_combo.currentText()
        self.config["buttons"]["font_size"] = self.font_size_spin.value()
        # text_color updated on pick

        for btn_name, ui in self.button_config_uis.items():
            ui.update_config()

        # Progress bar
        self.config["progress_bar"]["color"] = self.progress_color_btn.styleSheet().split(":")[-1].strip()
        self.config["progress_bar"]["background_color"] = self.progress_bg_color_btn.styleSheet().split(":")[-1].strip()
        self.config["progress_bar"]["height"] = self.progress_height_spin.value()
        self.config["progress_bar"]["radius"] = self.progress_radius_spin.value()

        # Visualizer
        self.config["visualizer"]["num_bars"] = self.num_bars_spin.value()
        self.config["visualizer"]["color_start"] = self.color_start_btn.styleSheet().split(":")[-1].strip()
        self.config["visualizer"]["color_end"] = self.color_end_btn.styleSheet().split(":")[-1].strip()
        self.config["visualizer"]["intensity"] = self.intensity_spin.value() / 10.0

        # Volume bar
        self.config["volume_bar"]["slider_color"] = self.volume_slider_color_btn.styleSheet().split(":")[-1].strip()
        self.config["volume_bar"]["background_color"] = self.volume_bg_color_btn.styleSheet().split(":")[-1].strip()
        self.config["volume_bar"]["height"] = self.volume_height_spin.value()
        self.config["volume_bar"]["radius"] = self.volume_radius_spin.value()
        self.config["volume_bar"]["slider_shape"] = self.volume_slider_shape_combo.currentText()

        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

        print("Configuration enregistrée.")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = ConfigUI()
    win.show()
    sys.exit(app.exec())

