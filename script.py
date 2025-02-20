import speech_recognition as sr
import time
from time import sleep
import RPi.GPIO as GPIO
import requests

# Initialisation du reconnaisseur vocal
recognizer = sr.Recognizer()

# Dictionnaire des commandes vocales
command_dict = {
    "numéro 1": "Vous avez dit 'un', message 1",
    "numéro 2": "Vous avez dit 'deux', message 2",
    "numéro 3": "Vous avez dit 'trois', message 3",
    "numéro 4": "Vous avez dit 'quatre', message 4",
    "numéro 5": "Vous avez dit 'cinq', message 5",
    "numéro 6": "Vous avez dit 'six', message 6",
    "numéro 7": "Vous avez dit 'sept', message 7",
    "numéro 8": "Vous avez dit 'huit', message 8",
    "numéro 9": "Vous avez dit 'neuf', message 9",
    "numéro 10": "Vous avez dit 'dix', message 10",
}

# Configuration des pins pour les moteurs et la LED
MOTOR_PINS = {
    "M1_En": 18,
    "M1_In1": 17,
    "M1_In2": 27,
    "M2_En": 13,
    "M2_In1": 22,
    "M2_In2": 24,
}
LED_PIN = 5

# Initialisation des GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(list(MOTOR_PINS.values()), GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)

# Initialisation des PWM pour les moteurs
pwm1 = GPIO.PWM(MOTOR_PINS["M1_En"], 1000)
pwm2 = GPIO.PWM(MOTOR_PINS["M2_En"], 1000)
pwm1.start(0)
pwm2.start(0)

# Fonctions pour la LED
def allumer_led():
    GPIO.output(LED_PIN, GPIO.HIGH)
    print("LED allumée.")

def eteindre_led():
    GPIO.output(LED_PIN, GPIO.LOW)
    print("LED éteinte.")

def clignoter_led(nb_fois, delai):
    """Fait clignoter la LED un certain nombre de fois."""
    for _ in range(nb_fois):
        allumer_led()
        sleep(delai)
        eteindre_led()
        sleep(delai)
    print(f"LED clignotée {nb_fois} fois.")

# Attente de connexion Wi-Fi
def attendre_connexion_wifi(timeout=120):
    """Attend que la Raspberry Pi soit connectée au Wi-Fi avant de continuer."""
    print("En attente de la connexion Wi-Fi...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Test de connexion à Internet via une requête
            response = requests.get("http://www.google.com", timeout=5)
            if response.status_code == 200:
                print("Connexion Wi-Fi établie.")
                clignoter_led(3, 0.5)  # Clignoter 3 fois avec un délai de 0.5 seconde
                return True
        except requests.RequestException:
            pass
        print("Connexion Wi-Fi indisponible. Nouvelle tentative...")
        sleep(5)  # Réessayer après 5 secondes
    print("Échec de connexion au Wi-Fi après le délai imparti.")
    return False

# Fonctions pour les moteurs
def avancer():
    allumer_led()
    GPIO.output(MOTOR_PINS["M1_In1"], GPIO.LOW)
    GPIO.output(MOTOR_PINS["M1_In2"], GPIO.HIGH)
    GPIO.output(MOTOR_PINS["M2_In1"], GPIO.LOW)
    GPIO.output(MOTOR_PINS["M2_In2"], GPIO.HIGH)
    pwm1.ChangeDutyCycle(30)
    pwm2.ChangeDutyCycle(30)
    print("Avancer.")
    eteindre_led()

def tourner_droite():
    allumer_led()
    GPIO.output(MOTOR_PINS["M1_In1"], GPIO.LOW)
    GPIO.output(MOTOR_PINS["M1_In2"], GPIO.HIGH)
    GPIO.output(MOTOR_PINS["M2_In1"], GPIO.LOW)
    GPIO.output(MOTOR_PINS["M2_In2"], GPIO.LOW)
    pwm1.ChangeDutyCycle(25)
    pwm2.ChangeDutyCycle(25)
    print("Tourner à droite.")
    eteindre_led()

def avancer_puis_tourner():
    allumer_led()
    avancer()
    sleep(2)
    tourner_droite()
    sleep(2)
    stopper_moteurs()
    eteindre_led()

def stopper_moteurs():
    allumer_led()
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)
    print("Moteurs arrêtés.")
    eteindre_led()

# Reconnaissance vocale
def recognize_and_print(audio):
    print("Tentative de reconnaissance vocale...")
    try:
        command_text = recognizer.recognize_google(audio, language="fr-FR").lower().strip()
        print(f"Commande reconnue : {command_text}")

        if "alexa" in command_text:
            allumer_led()
            sleep(1)
            eteindre_led()
            print("Mot 'Alexa' détecté.")
            return True

        if "stop" in command_text:
            print("Arrêt des moteurs et de la LED.")
            stopper_moteurs()
            eteindre_led()
            return False

        for key, message in command_dict.items():
            if key in command_text:
                print(message)
                avancer_puis_tourner()

    except sr.UnknownValueError:
        print("Aucun mot reconnu.")
    except sr.RequestError as e:
        print(f"Erreur avec le service de reconnaissance vocale : {e}")

    return True

def listen_for_keyword():
    with sr.Microphone() as source:
        print("Écoute en cours...")
        recognizer.adjust_for_ambient_noise(source)
        while True:
            try:
                audio = recognizer.listen(source)
                if not recognize_and_print(audio):
                    break
            except Exception as e:
                print(f"Erreur lors de l'écoute : {e}")

# Programme principal
def main():
    if attendre_connexion_wifi():
        print("Connexion Wi-Fi réussie. En attente des commandes vocales...")
        listen_for_keyword()
    else:
        print("Impossible de se connecter au Wi-Fi. Programme arrêté.")

if _name_ == "_main_":
    try:
        main()
    finally:
        print("Arrêt du programme. Nettoyage des ressources...")
        pwm1.stop()
        pwm2.stop()
        GPIO.cleanup()