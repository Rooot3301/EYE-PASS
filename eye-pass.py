import os
import json
import base64
import hashlib
import logging
import time
import sys
from cryptography.fernet import Fernet
from getpass import getpass
from colorama import Fore, Style, init

# Initialisation de Colorama
init()

# Répertoires et fichiers de configuration
CONFIG_DIR = 'config'
KEY_FILE = os.path.join(CONFIG_DIR, 'key.key')
USERS_FILE = os.path.join(CONFIG_DIR, 'users.json')
VERSION_FILE = os.path.join(CONFIG_DIR, 'version.txt')
LOGS_DIR = 'logs'
LOGS_FILE = os.path.join(LOGS_DIR, 'activity.log')

# Création des répertoires nécessaires s'ils n'existent pas
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# Configuration de la journalisation
logging.basicConfig(filename=LOGS_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fonction pour afficher l'art ASCII
def print_ascii_art(title, color=Fore.GREEN):
    ascii_art = {
        'login': r"""

██     ██ ███████ ██       ██████  ██████  ███    ███ ███████ 
██     ██ ██      ██      ██      ██    ██ ████  ████ ██      
██  █  ██ █████   ██      ██      ██    ██ ██ ████ ██ █████   
██ ███ ██ ██      ██      ██      ██    ██ ██  ██  ██ ██      
 ███ ███  ███████ ███████  ██████  ██████  ██      ██ ███████ 
                                                              
                                                              

    """,
        'home': r"""
███████╗██╗   ██╗███████╗    ██████╗  █████╗ ███████╗███████╗
██╔════╝╚██╗ ██╔╝██╔════╝    ██╔══██╗██╔══██╗██╔════╝██╔════╝
█████╗   ╚████╔╝ █████╗█████╗██████╔╝███████║███████╗███████╗
██╔══╝    ╚██╔╝  ██╔══╝╚════╝██╔═══╝ ██╔══██║╚════██║╚════██║
███████╗   ██║   ███████╗    ██║     ██║  ██║███████║███████║
╚══════╝   ╚═╝   ╚══════╝    ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝
    """
    }
    if title in ascii_art:
        # Afficher l'art ASCII
        print(color + ascii_art[title] + Style.RESET_ALL)

def print_progress_bar(iteration, total, prefix='', length=50, fill='█', print_end="\r"):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% Complete')
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write(print_end)
        sys.stdout.flush()

# Chargement de la version
def load_version():
    if not os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'w') as f:
            f.write('1.0.0')  # Version initiale
    with open(VERSION_FILE, 'r') as f:
        return f.read().strip()

# Générer une nouvelle clé de chiffrement
def generate_key():
    return Fernet.generate_key()

# Sauvegarder la clé de chiffrement
def save_key(key):
    with open(KEY_FILE, 'wb') as f:
        f.write(key)

# Charger la clé de chiffrement
def load_key():
    with open(KEY_FILE, 'rb') as f:
        return f.read()

# Générer un mot de passe sécurisé
def generate_password(length=12):
    import random
    import string
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

# Créer un utilisateur
def create_user():
    print(Fore.YELLOW + "Création du premier utilisateur." + Style.RESET_ALL)
    username = input(Fore.CYAN + "Nom d'utilisateur : " + Style.RESET_ALL)
    password = getpass(Fore.CYAN + "Mot de passe : " + Style.RESET_ALL)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    users = load_users()
    if username in users:
        print(Fore.RED + "Cet utilisateur existe déjà." + Style.RESET_ALL)
        return
    users[username] = hashed_password
    save_users(users)
    print(Fore.GREEN + "Utilisateur créé avec succès." + Style.RESET_ALL)

# Charger les utilisateurs
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

# Sauvegarder les utilisateurs
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# Authentifier l'utilisateur
def authenticate():
    print_ascii_art('login', Fore.CYAN)
    users = load_users()
    if not users:
        print(Fore.YELLOW + "Aucun utilisateur trouvé. Création du premier utilisateur..." + Style.RESET_ALL)
        create_user()
    username = input(Fore.CYAN + "Nom d'utilisateur : " + Style.RESET_ALL)
    password = getpass(Fore.CYAN + "Mot de passe : " + Style.RESET_ALL)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if users.get(username) == hashed_password:
        print(Fore.GREEN + "Connexion réussie." + Style.RESET_ALL)
        logging.info(f"User {username} logged in.")
        return username
    else:
        print(Fore.RED + "Nom d'utilisateur ou mot de passe incorrect." + Style.RESET_ALL)
        logging.warning(f"Failed login attempt for user {username}.")
        return None

# Cryptage des données
def encrypt_data(data, fernet):
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(data, fernet):
    try:
        return fernet.decrypt(data.encode()).decode()
    except Exception as e:
        print(Fore.RED + f"Erreur de décryptage : {e}" + Style.RESET_ALL)
        return None

# Sauvegarder un mot de passe
def save_password(name, password, fernet):
    passwords = load_passwords(fernet)
    passwords[name] = encrypt_data(password, fernet)
    with open('passwords.json', 'w') as f:
        json.dump(passwords, f)

# Charger les mots de passe
def load_passwords(fernet):
    if not os.path.exists('passwords.json'):
        return {}
    with open('passwords.json', 'r') as f:
        data = json.load(f)
        return {name: decrypt_data(pw, fernet) for name, pw in data.items()}

# Générer un mot de passe et l'ajouter à la base de données
def generate_password_and_save():
    name = input(Fore.CYAN + "Nom du mot de passe : " + Style.RESET_ALL)
    length = int(input(Fore.CYAN + "Longueur du mot de passe : " + Style.RESET_ALL))
    password = generate_password(length)
    print(Fore.GREEN + f"Mot de passe généré : {password}" + Style.RESET_ALL)
    fernet = Fernet(load_key())
    save_password(name, password, fernet)

# Consulter les mots de passe
def consult_passwords():
    fernet = Fernet(load_key())
    passwords = load_passwords(fernet)
    if not passwords:
        print(Fore.YELLOW + "Aucun mot de passe enregistré." + Style.RESET_ALL)
    for name, password in passwords.items():
        print(Fore.CYAN + f"{name}: {password}" + Style.RESET_ALL)

# Exporter des mots de passe
def export_passwords():
    fernet = Fernet(load_key())
    passwords = load_passwords(fernet)
    file_path = input(Fore.CYAN + "Chemin du fichier d'exportation : " + Style.RESET_ALL)
    with open(file_path, 'w') as f:
        json.dump(passwords, f)
    print(Fore.GREEN + "Mots de passe exportés avec succès." + Style.RESET_ALL)

# Importer des mots de passe
def import_passwords():
    file_path = input(Fore.CYAN + "Chemin du fichier d'importation : " + Style.RESET_ALL)
    with open(file_path, 'r') as f:
        passwords = json.load(f)
    fernet = Fernet(load_key())
    for name, password in passwords.items():
        save_password(name, password, fernet)
    print(Fore.GREEN + "Mots de passe importés avec succès." + Style.RESET_ALL)

# Modifier un mot de passe
def modify_password():
    fernet = Fernet(load_key())
    passwords = load_passwords(fernet)
    name = input(Fore.CYAN + "Nom du mot de passe à modifier : " + Style.RESET_ALL)
    if name not in passwords:
        print(Fore.RED + "Mot de passe non trouvé." + Style.RESET_ALL)
        return
    new_password = getpass(Fore.CYAN + "Nouveau mot de passe : " + Style.RESET_ALL)
    passwords[name] = encrypt_data(new_password, fernet)
    with open('passwords.json', 'w') as f:
        json.dump(passwords, f)
    print(Fore.GREEN + "Mot de passe modifié avec succès." + Style.RESET_ALL)

# Détruire la base de données
def destroy_database():
    if os.path.exists('passwords.json'):
        os.remove('passwords.json')
        print(Fore.RED + "Base de données détruite." + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + "Aucune base de données à détruire." + Style.RESET_ALL)

# Rechercher un mot de passe
def search_password():
    fernet = Fernet(load_key())
    passwords = load_passwords(fernet)
    query = input(Fore.CYAN + "Nom du mot de passe à rechercher : " + Style.RESET_ALL)
    result = {name: pw for name, pw in passwords.items() if query.lower() in name.lower()}
    if not result:
        print(Fore.YELLOW + "Aucun mot de passe trouvé pour cette recherche." + Style.RESET_ALL)
    for name, password in result.items():
        print(Fore.CYAN + f"{name}: {password}" + Style.RESET_ALL)

# Menu principal
def menu():
    print_ascii_art('home', Fore.CYAN)
    version = load_version()
    print(Fore.YELLOW + f"\nVersion : {version}" + Style.RESET_ALL)
    
    while True:
        print(Fore.YELLOW + "\nMenu:" + Style.RESET_ALL)
        print(Fore.CYAN + "1. Générer un nouveau mot de passe" + Style.RESET_ALL)
        print(Fore.CYAN + "2. Consulter les mots de passe" + Style.RESET_ALL)
        print(Fore.CYAN + "3. Exporter les mots de passe" + Style.RESET_ALL)
        print(Fore.CYAN + "4. Importer des mots de passe" + Style.RESET_ALL)
        print(Fore.CYAN + "5. Modifier un mot de passe" + Style.RESET_ALL)
        print(Fore.CYAN + "6. Détruire la base de données" + Style.RESET_ALL)
        print(Fore.CYAN + "7. Rechercher un mot de passe" + Style.RESET_ALL)
        print(Fore.CYAN + "8. Quitter" + Style.RESET_ALL)
        choice = input(Fore.YELLOW + "Choisissez une option : " + Style.RESET_ALL)
        if choice == '1':
            generate_password_and_save()
        elif choice == '2':
            consult_passwords()
        elif choice == '3':
            export_passwords()
        elif choice == '4':
            import_passwords()
        elif choice == '5':
            modify_password()
        elif choice == '6':
            destroy_database()
        elif choice == '7':
            search_password()
        elif choice == '8':
            break
        else:
            print(Fore.RED + "Choix non valide." + Style.RESET_ALL)

if __name__ == "__main__":
    # Simuler le chargement avec une barre de progression
    print(Fore.CYAN + "Chargement en cours..." + Style.RESET_ALL)
    for i in range(100):
        print_progress_bar(i + 1, 100, prefix='Chargement')
        time.sleep(0.05)  # Pause pour chaque mise à jour de la barre de progression
    
    if not os.path.exists(KEY_FILE):
        save_key(generate_key())
    if not os.path.exists(USERS_FILE):
        create_user()  # Créer un utilisateur lors du premier lancement
    authenticated_user = authenticate()
    if authenticated_user:
        menu()
    print(Fore.YELLOW + "Déconnexion..." + Style.RESET_ALL)
