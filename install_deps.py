import subprocess
import sys
import platform

# Liste propre des vraies dépendances nécessaires (à adapter si besoin)
DEPENDENCIES = [
    "pyaudio",      # interface audio
    "pygame",       # moteur audio
    "pyqtgraph",    # graphique
    "PyQt6",        # interface utilisateur
    "mutagen",      # métadonnées audio
    "pydub",        # traitement audio
    "yt-dlp",       # téléchargement youtube
    "numpy"         # calcul numérique
]

def install_package(package):
    command = [sys.executable, "-m", "pip", "install", "--upgrade", package]
    
    # Ajout de --break-system-packages si sur Linux
    if platform.system() == "Linux":
        command.append("--break-system-packages")

    try:
        print(f"📦 Installation de {package}...")
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        print(f"❌ Échec de l'installation de {package}. Vérifie ta connexion ou ton environnement.")

def check_audioop():
    try:
        import audioop
        print("✅ Le module standard 'audioop' est présent.")
    except ImportError:
        print("⚠️ 'audioop' est manquant ! Installe un Python complet (non embeddable).")

def main():
    print("🚀 Installation des dépendances Python pour le projet...\n")
    for package in DEPENDENCIES:
        install_package(package)

    print("\n🔍 Vérification de la présence du module standard 'audioop'...")
    check_audioop()

    print("\n✅ Installation terminée.")

if __name__ == "__main__":
    main()

