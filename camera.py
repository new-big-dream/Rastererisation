"""
Module de gestion de caméra pour la rastérisation 3D.

Fournit les fonctions essentielles pour :
- Normalisation de vecteurs
- Matrices de transformation (ModelView, Perspective, Viewport)
- Changement de repère (lookat)
- Normalisation de coordonnées
"""

import numpy as np


# ============================================================================
# NORMALISATION DE VECTEURS
# ============================================================================

def normalize_vector(v):
    """
    Normalise un vecteur 3D (le ramène à longueur 1).
    
    Args:
        v: Vecteur [x, y, z]
        
    Returns:
        Vecteur normalisé ou 0 si le vecteur est nul
    """
    x, y, z = v
    norm = np.sqrt(x**2 + y**2 + z**2)
    
    if norm == 0:
        return 0
    else:
        return np.array([x / norm, y / norm, z / norm])


# ============================================================================
# MATRICES DE TRANSFORMATION (PIPELINE GRAPHIQUE)
# ============================================================================

def viewport_make(x, y, w, h):
    """
    Crée la matrice de transformation du viewport.
    
    Transforme les coordonnées NDC (Normalized Device Coordinates) 
    en coordonnées écran (pixel).
    
    Args:
        x, y: Coin supérieur gauche du viewport
        w, h: Largeur et hauteur du viewport
        
    Returns:
        Matrice 4x4 de transformation du viewport
    """
    return np.array([
        [w / 2., 0., 0., x + w / 2.],
        [0., h / 2., 0., y + h / 2.],
        [0., 0., 1., 0.],
        [0., 0., 0., 1.],
    ])


def perspective_make(f):
    """
    Crée la matrice de projection en perspective.
    
    Applique une division perspective : plus les objets sont loin,
    plus ils sont petits.
    
    Args:
        f: Distance focale (distance de la caméra)
        
    Returns:
        Matrice 4x4 de projection en perspective
    """
    return np.array([
        [1., 0., 0., 0.],
        [0., 1., 0., 0.],
        [0., 0., 1., 0.],
        [0., 0., -1. / f, 1.],
    ])


def project_matrix(v, w, h):
    """
    Projette un point du clip space vers l'espace écran.
    
    [Fonction auxiliaire - peu utilisée]
    
    Args:
        v: Point [x, y, z]
        w, h: Largeur et hauteur de l'écran
        
    Returns:
        Point projeté [x', y', z'] en espace écran
    """
    x, y, z = v
    return np.array([(x + 1) * w, (y + 1) * h, (z + 1) * 255 / 2])


def lookat(eye, center, up):
    """
    Crée la matrice ModelView avec la méthode "lookat".
    
    Positionne la caméra en 'eye', la tourne vers 'center',
    et oriente le "haut" selon 'up'.
    
    Construit un nouveau repère basé sur :
    - n : vecteur arrière (eye -> center)
    - l : vecteur gauche (produit vectoriel)
    - m : vecteur haut (produit vectoriel)
    
    Args:
        eye: Position de la caméra [x, y, z]
        center: Point regardé [x, y, z]
        up: Vecteur "haut" [x, y, z]
        
    Returns:
        Matrice ModelView 4x4 = R @ T
    """
    # Calcule les vecteurs du nouveau repère
    n = normalize_vector(eye - center)  # Arrière
    l = normalize_vector(np.cross(up, n))  # Gauche
    m = normalize_vector(np.cross(n, l))  # Haut
    
    # Extraction des composantes
    cx, cy, cz = center
    lx, ly, lz = l
    mx, my, mz = m
    nx, ny, nz = n
    
    # Matrice de rotation (changement de repère)
    R = np.array([
        [lx, ly, lz, 0.],
        [mx, my, mz, 0.],
        [nx, ny, nz, 0.],
        [0., 0., 0., 1.],
    ])
    
    # Matrice de translation
    T = np.array([
        [1., 0., 0., -cx],
        [0., 1., 0., -cy],
        [0., 0., 1., -cz],
        [0., 0., 0., 1.],
    ])
    
    # ModelView = Rotation @ Translation
    return R @ T


# ============================================================================
# FONCTIONS OBSOLÈTES (À FUSIONNER)
# ============================================================================
# Ces fonctions sont des méthodes anciennes qui pourraient être fusionnées
# avec les nouvelles dans une version ultérieure.

def rot(v, theta):
    """
    [OBSOLÈTE] Effectue une rotation autour de l'axe Y.
    
    Args:
        v: Vecteur [x, y, z]
        theta: Angle de rotation en radians
        
    Returns:
        Vecteur après rotation
    """
    x, y, z = v
    
    # Rotation autour de l'axe Y
    x_new = np.cos(theta) * x + np.sin(theta) * z
    y_new = y
    z_new = -np.sin(theta) * x + np.cos(theta) * z
    
    return [x_new, y_new, z_new]


def persp(v, c):
    """
    [OBSOLÈTE] Effectue une projection en perspective centrale.
    
    Args:
        v: Vecteur [x, y, z]
        c: Distance focale
        
    Returns:
        Vecteur après projection
    """
    return v / (1 - v[2] / c)


# ============================================================================
# NORMALISATION DE COORDONNÉES
# ============================================================================
# Note : Ces deux fonctions font un travail similaire et pourraient
# être fusionnées ultérieurement.

def normalize(s, bounds):
    """
    Normalise les coordonnées 3D dans la plage [-1, 1].
    
    Utile pour transformer les coordonnées du modèle vers
    l'espace NDC (Normalized Device Coordinates).
    
    Args:
        s: Point [x, y, z]
        bounds: Limites de la scène [[xmin, xmax], [ymin, ymax], [zmin, zmax]]
        
    Returns:
        Point normalisé [nx, ny, nz] dans [-1, 1]
    """
    x, y, z = s
    xmin, xmax = bounds[0]
    ymin, ymax = bounds[1]
    zmin, zmax = bounds[2]
    
    # Ramène dans [-1, 1]
    nx = 2 * (x - xmin) / (xmax - xmin) - 1
    ny = 2 * (y - ymin) / (ymax - ymin) - 1
    nz = 2 * (z - zmin) / (zmax - zmin) - 1
    
    return [nx, ny, nz]


def normalize2(s, bounds):
    """
    Normalise les coordonnées 2D dans la plage [-1, 1].
    
    Version 2D de normalize().
    
    Args:
        s: Point [x, y]
        bounds: Limites [[xmin, xmax], [ymin, ymax]]
        
    Returns:
        Point normalisé [nx, ny] dans [-1, 1]
    """
    x, y = s
    xmin, xmax = bounds[0]
    ymin, ymax = bounds[1]
    
    # Ramène dans [-1, 1]
    nx = 2 * (x - xmin) / (xmax - xmin) - 1
    ny = 2 * (y - ymin) / (ymax - ymin) - 1
    
    return [nx, ny]
