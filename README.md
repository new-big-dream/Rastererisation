# Rastérerisation
Le but de ce programme est de convertir un fichier `.obj` (qui représente un objet 3D) en un rendu 2D convaincant. L'intérêt de ce code réside moins dans son utilisation pratique que dans l'exploration de ses fonctions et de leur structure ; il a été écrit en `Python` avec très peu de dépendance, et est fortement commenté en français afin d'en faciliter la lecture. 

## Dépendances
- **NumPy** : Calculs matriciels et opérations vectorielles
- **Pillow** : Génération et manipulation d'images


## Exemples
Voici quelques exemples de rendus générés très rapidement, sans texture. Les deux premiers rendus utilisent l'ombrage de Phong, le dernier n'utilise qu'une coloration selon la profondeur du triangle (avec suppression des faces cachées) :

<img width="200" alt="Rendu Phong 1" src="https://github.com/user-attachments/assets/4eaaf53a-7ff0-4248-809c-7157f520b19e" />
<img width="200" alt="Rendu Phong 2" src="https://github.com/user-attachments/assets/c28700e9-9461-4f9b-9a37-6a5d30aecb04" />
<img width="200" alt="Rendu profondeur" src="https://github.com/user-attachments/assets/4ddf3d40-096a-4b3f-89b8-7c71675e762c" />

