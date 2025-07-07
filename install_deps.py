import subprocess
import sys
import os
import platform

# Liste des packages nécessaires
required = [
    "PyQt6",
    "pygame",
    "mutagen",
    "pyqtgraph",
    "pydub",
    "yt_dlp",
    "numpy",
    "pyaudio"  # Ajouté si requis
]

def install(package):
    # Python >= 3.11 supporte --break-system-packages sur Linux
    pip_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", package]
    
    if platform.system() == "Linux":
        pip_cmd += ["--break-system-packages"]
    
    try:
        subprocess.check_call(pip_cmd)
        print(f"✅ {package} installé avec succès")
    except subprocess.CalledProcessError:
        print(f"❌ Échec de l'installation de {package}")

# Si audioop est manquant → avertir (car non installable via pip)
try:
    import audioop
except ImportError:
    print("⚠️ Module 'audioop' manquant. Assure-toi d'utiliser une version standard de Python (pas embeddable).")

print("📦 Installation des dépendances Python...")
for pkg in required:
    install(pkg)

