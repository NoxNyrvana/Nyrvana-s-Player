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
        self.add_visualizer_ui()

        self.save_button = QPushButton("Enregistrer la configuration")
        self.save_button.clicked.connect(self.save_config)
        self.main_layout.addWidget(self.save_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll)

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
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

    def pick_bg_color(self):
        current = QColor(self.config["window"].get("background_color", "#FFFFFF"))
        color = QColorDialog.getColor(current, self, "Choisir une couleur")
        if color.isValid():
            self.config["window"]["background_color"] = color.name()
            self.bg_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def pick_bg_image(self):
        dlg = QFileDialog(self, "Choisir une image ou un GIF")
        dlg.setNameFilters(["Images (*.png *.jpg *.bmp *.gif)"])
        if dlg.exec():
            path = dlg.selectedFiles()[0]
            self.config["window"]["background_image_path"] = path
            self.bg_img_label.setText(path)

    def add_buttons_general_ui(self):
        self.main_layout.addWidget(QLabel("--- Configuration générale des boutons ---"))

        self.main_layout.addWidget(QLabel("Police (standard) :"))
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Arial", "Times New Roman", "Courier New", "Verdana"])
        self.font_combo.setCurrentText(self.config["buttons"].get("font_family", "Arial"))
        self.main_layout.addWidget(self.font_combo)

        self.main_layout.addWidget(QLabel("Taille de police :"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 48)
        self.font_size_spin.setValue(self.config["buttons"].get("font_size", 12))
        self.main_layout.addWidget(self.font_size_spin)

        self.main_layout.addWidget(QLabel("Couleur du texte :"))
        self.text_color_btn = QPushButton()
        text_color = self.config["buttons"].get("text_color", "#000000")
        self.text_color_btn.setStyleSheet(f"background-color: {text_color}")
        self.text_color_btn.clicked.connect(self.pick_text_color)
        self.main_layout.addWidget(self.text_color_btn)

        self.main_layout.addWidget(QLabel("Police personnalisée :"))
        self.custom_font_btn = QPushButton("Choisir un fichier de police")
        self.custom_font_btn.clicked.connect(self.pick_custom_font)
        self.main_layout.addWidget(self.custom_font_btn)

        font_path = self.config["buttons"].get("font_path", "")
        self.custom_font_label = QLabel(font_path if font_path else "Aucune police chargée")
        self.main_layout.addWidget(self.custom_font_label)

    def pick_text_color(self):
        current = QColor(self.config["buttons"].get("text_color", "#000000"))
        color = QColorDialog.getColor(current, self, "Choisir couleur du texte")
        if color.isValid():
            self.config["buttons"]["text_color"] = color.name()
            self.text_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def pick_custom_font(self):
        dlg = QFileDialog(self, "Choisir une police personnalisée")
        dlg.setNameFilters(["Fichiers de police (*.ttf *.otf)"])
        if dlg.exec():
            path = dlg.selectedFiles()[0]
            self.config["buttons"]["font_path"] = path
            self.custom_font_label.setText(path)

    def add_buttons_detailed_ui(self):
        self.main_layout.addWidget(QLabel("--- Configuration détaillée des boutons ---"))
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        self.buttons_ui = []
        for name in ["play", "rewind", "forward", "rewind_backward"]:
            if name not in self.config["buttons"]:
                self.config["buttons"][name] = {
                    "shape": "rounded", "color": "#FFFFFF",
                    "size": [50, 50], "image_path": ""
                }
            ui = ButtonConfigUI(name, self.config["buttons"])
            self.buttons_ui.append(ui)
            self.tabs.addTab(ui, name.capitalize())

    def add_progress_bar_ui(self):
        self.main_layout.addWidget(QLabel("--- Configuration de la barre de progression ---"))

        self.pb_color_btn = QPushButton()
        self.pb_color_btn.setStyleSheet(f"background-color: {self.config['progress_bar']['color']}")
        self.pb_color_btn.clicked.connect(self.pick_pb_color)
        self.main_layout.addWidget(QLabel("Couleur de la barre :"))
        self.main_layout.addWidget(self.pb_color_btn)

        self.pb_bg_color_btn = QPushButton()
        self.pb_bg_color_btn.setStyleSheet(f"background-color: {self.config['progress_bar']['background_color']}")
        self.pb_bg_color_btn.clicked.connect(self.pick_pb_bg_color)
        self.main_layout.addWidget(QLabel("Fond de la barre :"))
        self.main_layout.addWidget(self.pb_bg_color_btn)

        self.pb_height_spin = QSpinBox()
        self.pb_height_spin.setRange(5, 50)
        self.pb_height_spin.setValue(self.config["progress_bar"]["height"])
        self.main_layout.addWidget(QLabel("Hauteur :"))
        self.main_layout.addWidget(self.pb_height_spin)

        self.pb_radius_spin = QSpinBox()
        self.pb_radius_spin.setRange(0, 30)
        self.pb_radius_spin.setValue(self.config["progress_bar"]["radius"])
        self.main_layout.addWidget(QLabel("Rayon des coins :"))
        self.main_layout.addWidget(self.pb_radius_spin)

    def pick_pb_color(self):
        color = QColorDialog.getColor(QColor(self.config["progress_bar"]["color"]), self)
        if color.isValid():
            self.config["progress_bar"]["color"] = color.name()
            self.pb_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def pick_pb_bg_color(self):
        color = QColorDialog.getColor(QColor(self.config["progress_bar"]["background_color"]), self)
        if color.isValid():
            self.config["progress_bar"]["background_color"] = color.name()
            self.pb_bg_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def add_visualizer_ui(self):
        self.main_layout.addWidget(QLabel("--- Visualiseur ---"))

        self.vis_bars_spin = QSpinBox()
        self.vis_bars_spin.setRange(5, 100)
        self.vis_bars_spin.setValue(self.config["visualizer"]["num_bars"])
        self.main_layout.addWidget(QLabel("Nombre de barres :"))
        self.main_layout.addWidget(self.vis_bars_spin)

        self.vis_color_start_btn = QPushButton()
        self.vis_color_start_btn.setStyleSheet(f"background-color: {self.config['visualizer']['color_start']}")
        self.vis_color_start_btn.clicked.connect(self.pick_vis_color_start)
        self.main_layout.addWidget(QLabel("Couleur de départ"))
        self.main_layout.addWidget(self.vis_color_start_btn)

        self.vis_color_end_btn = QPushButton()
        self.vis_color_end_btn.setStyleSheet(f"background-color: {self.config['visualizer']['color_end']}")
        self.vis_color_end_btn.clicked.connect(self.pick_vis_color_end)
        self.main_layout.addWidget(QLabel("Couleur de fin"))
        self.main_layout.addWidget(self.vis_color_end_btn)

        self.vis_intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.vis_intensity_slider.setRange(1, 100)
        self.vis_intensity_slider.setValue(int(self.config["visualizer"]["intensity"] * 10))
        self.vis_intensity_slider.valueChanged.connect(self.vis_intensity_changed)
        self.main_layout.addWidget(QLabel("Intensité"))
        self.main_layout.addWidget(self.vis_intensity_slider)

    def pick_vis_color_start(self):
        color = QColorDialog.getColor(QColor(self.config["visualizer"]["color_start"]), self)
        if color.isValid():
            self.config["visualizer"]["color_start"] = color.name()
            self.vis_color_start_btn.setStyleSheet(f"background-color: {color.name()}")

    def pick_vis_color_end(self):
        color = QColorDialog.getColor(QColor(self.config["visualizer"]["color_end"]), self)
        if color.isValid():
            self.config["visualizer"]["color_end"] = color.name()
            self.vis_color_end_btn.setStyleSheet(f"background-color: {color.name()}")

    def vis_intensity_changed(self, value):
        self.config["visualizer"]["intensity"] = value / 10.0

    def save_config(self):
        for ui in self.buttons_ui:
            ui.update_config()

        self.config["window"]["width"] = self.width_spin.value()
        self.config["window"]["height"] = self.height_spin.value()
        self.config["buttons"]["font_family"] = self.font_combo.currentText()
        self.config["buttons"]["font_size"] = self.font_size_spin.value()
        self.config["progress_bar"]["height"] = self.pb_height_spin.value()
        self.config["progress_bar"]["radius"] = self.pb_radius_spin.value()
        self.config["visualizer"]["num_bars"] = self.vis_bars_spin.value()

        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)
        print("Configuration enregistrée.")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ConfigUI()
    window.show()
    sys.exit(app.exec())
