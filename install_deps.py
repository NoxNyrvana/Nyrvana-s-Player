import subprocess
import sys

# Liste des dépendances nécessaires
required = [
    "PyQt6",
    "pygame",
    "mutagen",
    "pyqtgraph",
    "pydub",
    "yt_dlp",
    "numpy"
]

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])

print("Installation des dépendances...")
for pkg in required:
    try:
        install(pkg)
        print(f"✅ {pkg} installé")
    except subprocess.CalledProcessError:
        print(f"❌ Erreur lors de l'installation de {pkg}")

print("✅ Installation terminée.")
