from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from threading import Thread, Event, Lock
import time
import os
import datetime
import padelbot  # Your Selenium logic: login, check_availability, process_reservation
from dotenv import load_dotenv
import subprocess

def install_chrome():
    """Ensure Chrome is installed in the runtime environment"""
    chrome_path = "/usr/bin/google-chrome"

    if not os.path.exists(chrome_path):
        print("🚀 Installing Google Chrome at runtime...")
        os.system("apt-get update && apt-get install -y wget curl gnupg unzip")
        os.system("wget -q -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
        os.system("dpkg -i /tmp/google-chrome.deb || apt-get -fy install")
        os.system("rm /tmp/google-chrome.deb")
    else:
        print("✅ Google Chrome already installed")

    # Verify installation
    try:
        chrome_version = subprocess.check_output([chrome_path, "--version"]).decode("utf-8").strip()
        print(f"✅ Chrome Installed: {chrome_version}")
    except Exception as e:
        print("❌ Chrome installation failed:", str(e))
        raise RuntimeError("Google Chrome is not installed correctly")

install_chrome()  # Run this before anything else in app.py


# Load .env only if running locally
if os.getenv("REPLIT_ENV") is None:
    load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")  # Remplacez par une clé aléatoire et sécurisée

# Variables globales pour gérer le thread du bot et les logs
bot_thread = None
stop_event = Event()
log_lock = Lock()
bot_logs = []

def log_message(message):
    """Ajoute un message dans les logs du bot, avec horodatage."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    with log_lock:
        bot_logs.append(entry)
    print(entry)

def run_bot():
    try:
        log_message("Bot démarré. Connexion en cours...")
        padelbot.login("clarence-dion@orange.fr", "Claclapadel2002!")
        log_message("Connexion réussie.")
        while not stop_event.is_set():
            log_message("Vérification de disponibilité...")
            clicked_slot = padelbot.check_availability(stop_event)
            if clicked_slot is None:
                # The stop event was set during check_availability; break the loop.
                break
            log_message(f"Créneau réservé : {clicked_slot}")
            padelbot.process_reservation()
            log_message("Processus de réservation terminé. (Vérifiez sur le site pour confirmation)")
            time.sleep(5)
    except Exception as e:
        log_message(f"Erreur dans le bot : {str(e)}")
    finally:
        log_message("Bot arrêté.")


@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    """Page de connexion."""
    erreur = None
    if request.method == "POST":
        utilisateur = request.form.get("utilisateur")
        motdepasse = request.form.get("motdepasse")
        # Vérification simple (remplacez par un vrai système d'auth)
        if utilisateur == "admin" and motdepasse == "adminpassword":
            session["connecte"] = True
            return redirect(url_for("accueil"))
        else:
            erreur = "Identifiants invalides. Veuillez réessayer."
    return render_template("connexion.html", erreur=erreur)

@app.route("/deconnexion")
def deconnexion():
    """Se déconnecter."""
    session.pop("connecte", None)
    return redirect(url_for("connexion"))

@app.route("/accueil")
def accueil():
    """Page principale avec les boutons pour démarrer/arrêter le bot et les logs."""
    if not session.get("connecte"):
        return redirect(url_for("connexion"))
    return render_template("accueil.html")

@app.route("/demarrer_bot", methods=["POST"])
def demarrer_bot():
    global bot_thread, stop_event
    if not session.get("connecte"):
        return redirect(url_for("connexion"))
    # Démarre le thread du bot s'il n'est pas déjà en cours
    if bot_thread is None or not bot_thread.is_alive():
        stop_event.clear()
        bot_thread = Thread(target=run_bot, daemon=True)
        bot_thread.start()
        log_message("Thread du bot lancé.")
    return redirect(url_for("accueil"))

@app.route("/arreter_bot", methods=["POST"])
def arreter_bot():
    global bot_thread, stop_event
    if not session.get("connecte"):
        return redirect(url_for("connexion"))
    stop_event.set()
    if bot_thread is not None:
        bot_thread.join(timeout=5)
    log_message("Thread du bot arrêté.")
    return redirect(url_for("accueil"))

@app.route("/logs")
def logs():
    """Retourne les logs du bot en JSON pour l'affichage en temps réel."""
    with log_lock:
        copie_logs = list(bot_logs)
    return jsonify(copie_logs)

@app.route("/statut")
def statut():
    """Indique si le bot est en cours d'exécution ou non."""
    if bot_thread and bot_thread.is_alive():
        return jsonify({"etat": "running"})
    else:
        return jsonify({"etat": "stopped"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Default to 8000 for Koyeb
    # Expose sur 0.0.0.0 pour être accessible via Internet
    app.run(host="0.0.0.0", port=5000, debug=True)
