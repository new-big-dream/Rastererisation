"""
Module d'ombrage (shading) avec modèle d'illumination Phong.

Implémente l'algorithme d'éclairage Phong pour calculer
les couleurs des surfaces en fonction de la lumière et des normales.
"""

import numpy as np


# ============================================================================
# UTILITAIRES
# ============================================================================

def normalize_vector(v):
    """
    Normalise un vecteur 3D à longueur 1.
    
    Args:
        v: Vecteur [x, y, z]
        
    Returns:
        Vecteur normalisé ou [0, 0, 0] si le vecteur est nul
    """
    x, y, z = v
    norm = np.sqrt(x**2 + y**2 + z**2)
    
    if norm == 0:
        return np.array([0, 0, 0])
    else:
        return np.array([x / norm, y / norm, z / norm])


# ============================================================================
# MODÈLE D'ÉCLAIRAGE PHONG
# ============================================================================

def phong_color(p1, p2, p3, light):
    """
    Calcule la couleur d'un triangle avec le modèle d'éclairage Phong.
    
    Le modèle Phong combine trois composantes :
    1. Ambient : lumière ambiante (base minimale)
    2. Diffuse : réflexion diffuse (mat/granuleux)
    3. Specular : réflexion spéculaire (brillant/lisse)
    
    Formule :
        intensity = ambient + diffuse × (n·l) + specular × (r·e)^p
    
    où:
        n = normale de la surface
        l = direction vers la lumière
        r = direction de la lumière réfléchie
        e = direction vers l'observateur (caméra)
        p = facteur de brillance
    
    Args:
        p1, p2, p3: Sommets du triangle [x, y, z]
        light: Vecteur pointant vers la lumière
        
    Returns:
        Tuple RGBA (r, g, b, a) avec niveaux de gris basés sur l'intensité
    """
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)
    
    # ---- Calcul de la normale du triangle ----
    # La normale est perpendiculaire à la surface
    # cross(p2-p1, p3-p1) donne un vecteur perpendiculaire au triangle
    n = normalize_vector(np.cross(p2 - p1, p3 - p1))
    
    # ---- Normalisation des vecteurs ----
    l = normalize_vector(light)  # Direction vers la lumière
    
    # ---- Calcul du rayon réfléchi ----
    # Formule de réflexion : r = 2(n·l)n - l
    r = normalize_vector(2 * n * np.dot(n, l) - l)
    
    # ---- Composantes de l'éclairage Phong ----
    ambient = 0.01  # Lumière ambiante (valeur faible)
    diff = abs(np.dot(n, l))  # Composante diffuse (0 à 1)
    spec = max(r[2], 0.0) ** 0.002  # Composante spéculaire (brillance faible)
    
    # ---- Intensité totale ----
    intensity = min(1.0, ambient + 0.4 * diff + 0.9 * spec)
    c = int(round(255 * intensity))
    
    # Retourne un tuple RGBA avec niveaux de gris
    return (c, c, c, 255)


def phong_color_normal(n, light):
    """
    Calcule la couleur avec le modèle d'éclairage Phong à partir d'une normale.
    
    Version optimisée qui accepte directement la normale du triangle
    au lieu de recalculer à partir des sommets.
    
    Args:
        n: Normale du triangle [nx, ny, nz]
        light: Vecteur pointant vers la lumière
        
    Returns:
        Tuple RGBA (r, g, b, a) avec niveaux de gris basés sur l'intensité
    """
    # ---- Normalisation des vecteurs ----
    l = normalize_vector(light)  # Direction vers la lumière
    
    # ---- Calcul du rayon réfléchi ----
    # Formule de réflexion : r = 2(n·l)n - l
    r = normalize_vector(2 * n * np.dot(n, l) - l)
    
    # ---- Composantes de l'éclairage Phong ----
    ambient = 0.01  # Lumière ambiante
    diff = abs(np.dot(n, l))  # Composante diffuse
    spec = max(r[2], 0.0) ** 0.002  # Composante spéculaire
    
    # ---- Intensité totale ----
    intensity = min(1.0, ambient + 0.4 * diff + 0.9 * spec)
    c = int(round(255 * intensity))
    
    # Retourne un tuple RGBA avec niveaux de gris
    return (c, c, c, 255)
