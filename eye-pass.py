import os
import json
import base64
import random
import string
from cryptography.fernet import Fernet
from colorama import Fore, Style, init
from getpass import getpass
import shutil

# Initialiser Colorama pour les couleurs dans la CLI
init(autoreset=True)

# Chemins des fichiers
DB_FILE = 'passwords.json'
KEY_FILE = 'key.key'
VERSION_FILE = 'version.txt'

# Affichage d'ASCII Art avec couleurs
def print_logo():
    """Affiche le logo de EyePass avec des couleurs"""
    print(Fore.CYAN + """
    
███████╗██╗   ██╗███████╗    ██████╗  █████╗ ███████╗███████╗
██╔════╝╚██╗ ██╔╝██╔════╝    ██╔══██╗██╔══██╗██╔════╝██╔════╝
█████╗   ╚████╔╝ █████╗█████╗██████╔╝███████║███████╗███████╗
██╔══╝    ╚██╔╝  ██╔══╝╚════╝██╔═══╝ ██╔══██║╚════██║╚════██║
███████╗   ██║   ███████╗    ██║     ██║  ██║███████║███████║
╚══════╝   ╚═╝   ╚══════╝    ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝
                                                             

    """ + Style.RESET_ALL)

def load_key():
    """Charge la clé de chiffrement depuis le fichier"""
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)
    with open(KEY_FILE, 'rb') as key_file:
        key = key_file.read()
    return Fernet(key)

def encrypt_data(data, fernet):
    """Chiffre les données avec Fernet"""
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(data, fernet):
    """Déchiffre les données avec Fernet"""
    return fernet.decrypt(data.encode()).decode()

def generate_password(length):
    """Génère un mot de passe aléatoire"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

def save_password(name, password, fernet):
    """Sauvegarde un mot de passe dans la base de données en le cryptant"""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({}, f)
    
    with open(DB_FILE, 'r') as f:
        data = json.load(f)
    
    encrypted_password = encrypt_data(password, fernet)
    data[name] = encrypted_password
    
    with open(DB_FILE, 'w') as f:
        json.dump(data, f)
    print(Fore.GREEN + f"Mot de passe sauvegardé pour {name}" + Style.RESET_ALL)

def load_passwords(fernet):
    """Charge et décrypte tous les mots de passe depuis la base de données"""
    if not os.path.exists(DB_FILE):
        print(Fore.RED + f"Fichier de base de données non trouvé : {DB_FILE}" + Style.RESET_ALL)
        return {}
    
    with open(DB_FILE, 'r') as f:
        data = json.load(f)
    
    passwords = {}
    for name, encrypted_pw in data.items():
        try:
            passwords[name] = decrypt_data(encrypted_pw, fernet)
        except Exception as e:
            print(Fore.RED + f"Erreur lors du déchiffrement du mot de passe pour {name}: {e}" + Style.RESET_ALL)
    return passwords

def search_passwords(fernet):
    """Permet la recherche de mots de passe dans la base de données"""
    query = input(Fore.YELLOW + "Entrez le nom du mot de passe à rechercher : " + Style.RESET_ALL)
    passwords = load_passwords(fernet)
    filtered_passwords = {name: pw for name, pw in passwords.items() if query.lower() in name.lower()}

    if filtered_passwords:
        print(Fore.GREEN + "Résultats de la recherche:" + Style.RESET_ALL)
        for name, pw in filtered_passwords.items():
            print(Fore.CYAN + f"{name}: {pw}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "Aucun résultat trouvé." + Style.RESET_ALL)

def edit_password(name, fernet):
    """Modifie un mot de passe existant"""
    with open(DB_FILE, 'r') as f:
        data = json.load(f)
    
    if name in data:
        new_password = getpass(Fore.YELLOW + "Entrez le nouveau mot de passe : " + Style.RESET_ALL)
        encrypted_password = encrypt_data(new_password, fernet)
        data[name] = encrypted_password
        
        with open(DB_FILE, 'w') as f:
            json.dump(data, f)
        print(Fore.GREEN + f"Mot de passe mis à jour pour {name}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "Mot de passe non trouvé." + Style.RESET_ALL)

def export_passwords():
    """Exporte les mots de passe dans le dossier Downloads"""
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'exported_passwords.json')
    shutil.copy(DB_FILE, downloads_path)
    print(Fore.GREEN + f"Mots de passe exportés vers {downloads_path}" + Style.RESET_ALL)

def destroy_passwords():
    """Détruit la base de données des mots de passe"""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(Fore.RED + "Base de données détruite." + Style.RESET_ALL)
    else:
        print(Fore.RED + "La base de données n'existe pas." + Style.RESET_ALL)

def import_passwords():
    """Importe les mots de passe depuis un fichier"""
    import_file = input(Fore.YELLOW + "Entrez le chemin du fichier à importer : " + Style.RESET_ALL)
    if os.path.exists(import_file):
        shutil.copy(import_file, DB_FILE)
        print(Fore.GREEN + f"Mots de passe importés depuis {import_file}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "Fichier non trouvé." + Style.RESET_ALL)

def check_version():
    """Vérifie la version du script"""
    if not os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'w') as version_file:
            version_file.write("1.0.0")
    with open(VERSION_FILE, 'r') as version_file:
        version = version_file.read().strip()
    print(Fore.MAGENTA + f"Version: {version}" + Style.RESET_ALL)

def menu():
    """Affiche le menu principal et gère les options de l'utilisateur"""
    print_logo()

    fernet = load_key()
    check_version()
    
    while True:
        print("\n" + Fore.YELLOW + "Menu:" + Style.RESET_ALL)
        print("1. Générer un nouveau mot de passe")
        print("2. Consulter les mots de passe")
        print("3. Rechercher des mots de passe")
        print("4. Exporter les mots de passe")
        print("5. Importer des mots de passe")
        print("6. Modifier un mot de passe")
        print("7. Détruire la base de données")
        print("8. Quitter")

        choice = input(Fore.YELLOW + "Choisissez une option: " + Style.RESET_ALL)

        if choice == '1':
            name = input(Fore.YELLOW + "Nom du mot de passe: " + Style.RESET_ALL)
            length = int(input(Fore.YELLOW + "Longueur du mot de passe: " + Style.RESET_ALL))
            password = generate_password(length)
            save_password(name, password, fernet)
            print(Fore.GREEN + f"Mot de passe généré: {password}" + Style.RESET_ALL)
        
        elif choice == '2':
            passwords = load_passwords(fernet)
            if passwords:
                print(Fore.GREEN + "Liste des mots de passe:" + Style.RESET_ALL)
                for name, pw in passwords.items():
                    print(Fore.CYAN + f"{name}: {pw}" + Style.RESET_ALL)
            else:
                print(Fore.RED + "Aucun mot de passe trouvé." + Style.RESET_ALL)
        
        elif choice == '3':
            search_passwords(fernet)
        
        elif choice == '4':
            export_passwords()
        
        elif choice == '5':
            import_passwords()
        
        elif choice == '6':
            name = input(Fore.YELLOW + "Nom du mot de passe à modifier: " + Style.RESET_ALL)
            edit_password(name, fernet)
        
        elif choice == '7':
            destroy_passwords()
        
        elif choice == '8':
            print(Fore.GREEN + "Merci d'avoir utilisé EyePass. À bientôt!" + Style.RESET_ALL)
            break
        
        else:
            print(Fore.RED + "Option invalide. Essayez encore." + Style.RESET_ALL)

if __name__ == "__main__":
    menu()






