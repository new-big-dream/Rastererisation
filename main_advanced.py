"""
Rastérisation 3D avancée avec gestion de profondeur.

Ce script convertit un fichier OBJ en image 2D rendue avec :
- Projection en perspective
- Z-buffer pour l'élimination des surfaces cachées
- Caméra positionnée dans la scène
- Coordonnées barycentriques pour le remplissage de triangles
"""

import numpy as np
from PIL import Image
import random

import parse
import camera
#import shader

# ============================================================================
# CONFIGURATION
# ============================================================================

# Chemin du fichier OBJ à charger
fichier = "path/to/your/file.obj"  # À remplacer par l'adresse complète du fichier .obj

# Définition des couleurs (format RGBA)
white = (255, 255, 255, 255)
green = (0, 255, 0, 255)
red = (255, 128, 64, 255)
blue = (0, 128, 255, 255)
yellow = (255, 200, 0, 255)
black = (0, 0, 0, 0)

# Dimensions de l'écran
width = 800
height = 800

# Paramètres de la caméra
eye = np.array([-1., 0., 2.])      # Position de la caméra
center = np.array([0., 0., 0.])    # Point regardé
up = np.array([0., 1., 0.])        # Vecteur "haut"

# Matrices du pipeline graphique
ModelView = camera.lookat(eye, center, up)
perspective = camera.perspective_make(np.linalg.norm(eye - center))
Viewport = camera.viewport_make(width / 16, height / 16, width * 7 / 8, height * 7 / 8)

# Framebuffer et Z-buffer
framebuffer = np.zeros((width, height, 4), dtype=np.uint8)  # RGBA
zbuffer = np.array([[-np.inf for j in range(height + 2)] for i in range(width + 2)])


# ============================================================================
# PROJECTIONS
# ============================================================================

def project(s):
    """
    Projette un point 3D en point écran 2D (projection orthographique).
    
    Args:
        s: Point [x, y, z]
        
    Returns:
        Point projeté [x', y'] en coordonnées écran
    """
    x, y, z = s
    scale = 400  # Facteur d'échelle
    cx, cy = width // 2, height // 2
    return [int(cx + x * scale), int(cy - y * scale)]


def project_with_depth(s):
    """
    Projette un point 3D en point écran 2D avec conservation de la profondeur.
    
    Args:
        s: Point [x, y, z]
        
    Returns:
        Point projeté [x', y', z] conservant la profondeur
    """
    x, y, z = s
    scale = 400
    cx, cy = width // 2, height // 2
    return [int(cx + x * scale), int(cy - y * scale), z]


def homogene(s):
    """
    Convertit un point 3D en coordonnées homogènes 4D.
    
    Args:
        s: Point [x, y, z]
        
    Returns:
        Point homogène [x, y, z, 1]
    """
    x, y, z = s
    return np.array([x, y, z, 1])


# ============================================================================
# UTILITAIRES
# ============================================================================

def random_rgba():
    """
    Génère une couleur RGBA aléatoire.
    
    Returns:
        Tuple (r, g, b, a) avec valeurs entre 0 et 255
    """
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    a = random.randint(0, 255)
    return (r, g, b, a)


# ============================================================================
# PRIMITIVES GÉOMÉTRIQUES
# ============================================================================

def set(x, y, fb, color):
    """
    Place un pixel à la position (x, y) avec la couleur spécifiée.
    
    Args:
        x, y: Coordonnées du pixel
        fb: Framebuffer (ou Z-buffer)
        color: Couleur RGBA ou valeur de profondeur
    """
    if 0 <= x < len(fb) and 0 <= y < len(fb[x]):
        fb[x][y] = color


def clear(fb, color):
    """
    Efface le framebuffer en le remplissant d'une couleur.
    
    Args:
        fb: Framebuffer
        color: Couleur de remplissage
    """
    for x in range(len(fb)):
        for y in range(len(fb[x])):
            fb[x][y] = color


def line(p1, p2, fb, color):
    """
    Trace une ligne entre deux points avec l'algorithme de Bresenham.
    Gère automatiquement les lignes abruptes et douces.
    
    Args:
        p1: Point de départ [x, y]
        p2: Point d'arrivée [x, y]
        fb: Framebuffer
        color: Couleur de la ligne
    """
    ax, ay = p1
    bx, by = p2
    
    # Détermine si la ligne est abrupte
    steep = abs(ax - bx) < abs(ay - by)
    
    if steep:
        # Échange x et y si la ligne est abrupte
        ax, ay = ay, ax
        bx, by = by, bx
    
    if ax > bx:
        # Assure que on va de gauche à droite
        ax, bx = bx, ax
        ay, by = by, ay
    
    for x in range(ax, bx):
        t = (x - ax) / (bx - ax)
        y = int((ay + (by - ay) * t))
        
        if steep:
            set(y, x, fb, color)
        else:
            set(x, y, fb, color)


def triangle(clip, fb, zb, color):
    """
    Rastérise un triangle rempli avec gestion de profondeur.
    
    Utilise :
    - Les coordonnées barycentriques pour le remplissage
    - Le Z-buffer pour l'élimination des surfaces cachées
    - Le backface culling pour éliminer les faces arrière
    - L'interpolation de profondeur avec division perspective
    
    Args:
        clip: Sommets du triangle en coordonnées de clipping [p1, p2, p3]
        fb: Framebuffer
        zb: Z-buffer
        color: Couleur du triangle
    """
    # Conversion en coordonnées de dispositif normalisé (division perspective)
    ndc = np.array([clip[i] / clip[i][3] for i in range(3)])
    
    # Transformation en coordonnées écran
    screen = np.array([(Viewport @ ndc[i])[0:2] for i in range(3)])
    
    ax, ay = screen[0]
    bx, by = screen[1]
    cx, cy = screen[2]
    
    # Profondeurs après division perspective
    az, bz, cz = ndc[0][2], ndc[1][2], ndc[2][2]
    
    # ---- Boîte englobante ----
    bbminx = int(min(ax, bx, cx))
    bbminy = int(min(ay, by, cy))
    bbmaxx = int(max(ax, bx, cx))
    bbmaxy = int(max(ay, by, cy))
    
    # ---- Calcul de l'aire ----
    ABC = np.array([np.concatenate((screen[i][0:2], [1])) for i in range(3)])
    area = np.linalg.det(ABC)
    
    # Backface culling + élimine les très petits triangles
    if area >= 1:
        for x in range(bbminx, bbmaxx + 1):
            for y in range(bbminy, bbmaxy + 1):
                
                # ---- Coordonnées barycentriques ----
                p = np.array([x, y, 1])
                barycentric_coordinates = np.linalg.inv(ABC.T) @ p
                alpha, beta, gamma = barycentric_coordinates
                
                # Pixel en dehors du triangle ?
                if alpha < 0 or beta < 0 or gamma < 0:
                    continue
                
                # ---- Interpolation de profondeur ----
                z = alpha * az + beta * bz + gamma * cz
                
                if 0 <= x < width and 0 <= y < height:
                    if z >= zb[x][y]:
                        set(x, y, zb, z)
                        
                        # Coloration basée sur la profondeur (à enlever pour avoir coloration aléatoire ou utiliser coloration de phong)
                        z_min = zb[width][height]
                        z_max = zb[width + 1][height + 1] 
                        
                        # Normalise la profondeur en [0, 255]
                        c = int(round((abs(z - z_min) / (z_max - z_min)) * 40)) #on suppose l'objet non plat (3D par hypothèse)
                        c = 0 if c < 0 else (255 if c > 255 else c)
                        
                        # Affiche le pixel
                        set(x, y, fb, color)


# ============================================================================
# CONVERSIONS OBJ -> RENDU
# ============================================================================

def obj_to_lines(fichier, fb, color):
    """
    Convertit un fichier OBJ en structure filaire (wireframe).
    
    Args:
        fichier: Chemin du fichier OBJ
        fb: Framebuffer
        color: Couleur des arêtes
    """
    tab = parse.lire(fichier)
    
    for x, y, z in tab[1]:
        # Récupère les trois sommets du triangle
        a, b, c = tab[0][x - 1], tab[0][y - 1], tab[0][z - 1]
        
        # Projette les sommets
        a, b, c = project(a), project(b), project(c)
        
        # Trace les trois arêtes
        line(a, b, fb, color)
        line(a, c, fb, color)
        line(b, c, fb, color)


def rasterizer(fichier, fb, zb):
    """
    Rastérise complètement un fichier OBJ avec gestion de profondeur.
    
    Applique la transformation complète :
    1. ModelView (positionnement caméra)
    2. Projection en perspective
    3. Division perspective
    4. Viewport
    5. Rastérisation avec Z-buffer
    
    Args:
        fichier: Chemin du fichier OBJ
        fb: Framebuffer
        zb: Z-buffer
    """
    tab = parse.lire(fichier)
    
    # ---- Calcul des bornes de la scène ----
    xs = [p[0] for p in tab[0]]
    ys = [p[1] for p in tab[0]]
    zs = [p[2] for p in tab[0]]
    bounds = [[min(xs), max(xs)], [min(ys), max(ys)], [min(zs), max(zs)]]
    z_max = bounds[2][1]
    z_min = bounds[2][0]
    
    i = -1
    total_triangles = len(tab[1])
    
    # ---- Itération sur tous les triangles ----
    for x, y, z in tab[1]:
        i += 1
        
        # Affiche la progression
        progress = int(i / total_triangles * 100)
        prev_progress = int((i - 1) / total_triangles * 100)
        if progress != prev_progress:
            print(progress, "%")
        
        # ---- Récupère les trois sommets ----
        p1, p2, p3 = tab[0][x - 1], tab[0][y - 1], tab[0][z - 1]
        clip = [p1, p2, p3]
        
        # ---- Applique les transformations ====
        for j in [0, 1, 2]:
            clip[j] = perspective @ ModelView @ homogene(clip[j])
        
        # ---- Mise à jour du Z-buffer avec les bornes ----
        zb[width][height] = z_min
        zb[width + 1][height + 1] = z_max
        
        # ---- Couleur aléatoire ----
        color = random_rgba()
        
        # ---- Rastérisation du triangle ----
        triangle(clip, fb, zb, color)


def obj_to_triangles_RGBA(fichier, fb):
    """
    Convertit un fichier OBJ en triangles remplis avec couleurs aléatoires RGBA.
    Utilise la projection orthographique simple (sans gestion de profondeur).
    
    Args:
        fichier: Chemin du fichier OBJ
        fb: Framebuffer
    """
    tab = parse.lire(fichier)
    
    for x, y, z in tab[1]:
        p1, p2, p3 = tab[0][x - 1], tab[0][y - 1], tab[0][z - 1]
        p1, p2, p3 = project(p1), project(p2), project(p3)
        color = random_rgba()
        triangle_new(p1, p2, p3, fb, color)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """
    Point d'entrée du programme.
    Efface le framebuffer et rastérise le modèle OBJ.
    """
    # Efface le framebuffer
    clear(framebuffer, black)
    
    # Rastérise le modèle OBJ
    rasterizer(fichier, framebuffer, zbuffer)
    
    # Affiche l'image rendue
    Image.fromarray(framebuffer, 'RGBA').show()


if __name__ == "__main__":
    main()
