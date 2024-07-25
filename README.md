# EyePass

**EyePass** est un outil de gestion de mots de passe sécurisé avec une interface en ligne de commande (CLI). Il permet de générer, stocker, rechercher, modifier, exporter et détruire des mots de passe de manière sécurisée en utilisant le chiffrement Fernet.

## Fonctionnalités

- **Génération de Mots de Passe** : Créez des mots de passe aléatoires avec une longueur spécifiée.
- **Consultation des Mots de Passe** : Affichez les mots de passe stockés dans une base de données sécurisée.
- **Recherche de Mots de Passe** : Trouvez des mots de passe spécifiques par nom.
- **Éditeur de Mot de Passe** : Modifiez les mots de passe existants.
- **Exportation** : Exportez les mots de passe dans un fichier sécurisé.
- **Importation** : Importez des mots de passe depuis un fichier sécurisé.
- **Destruction** : Supprimez définitivement la base de données des mots de passe.

## Prérequis

- Python 3.7 ou supérieur
- Les bibliothèques Python suivantes :
  - `cryptography`
  - `colorama`

## Installation

1. **Clonez le Répertoire**

   Clonez ce répertoire sur votre machine locale en utilisant Git :
   ```bash
   git clone https://github.com/Rooot3301/eye-pass.git
   cd eye-pass

