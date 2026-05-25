"""
Module de parsing pour fichiers OBJ (Wavefront).

Fournit trois niveaux de parsing :
1. lire() : Parsing basique (sommets et faces)
2. lire_plus() : Parsing avec normales et coordonnées de texture
3. lire_final() : Parsing complet (format OBJ standard)

Format OBJ :
- v x y z : vertex (sommet)
- vt u v : texture coordinate
- vn x y z : vertex normal (normale)
- f v/vt/vn v/vt/vn v/vt/vn : face (triangle)
"""


# ============================================================================
# PARSING BASIQUE
# ============================================================================

def lire(file_name):
    """
    Parsing basique d'un fichier OBJ.
    
    Extrait uniquement les sommets (vertices) et les faces (triangles).
    Ignore les normales et coordonnées de texture.
    
    Format retourné :
    res[0] : Liste des sommets [[x1, y1, z1], [x2, y2, z2], ...]
    res[1] : Liste des faces (indices) [[v1, v2, v3], [v4, v5, v6], ...]
    
    Args:
        file_name: Chemin du fichier OBJ
        
    Returns:
        Liste [vertices, faces] où :
        - vertices: List[[x, y, z], ...]
        - faces: List[[v1, v2, v3], ...] (indices 1-basés)
    """
    res = [[], []]
    
    for line in open(file_name):
        parts = line.split()
        
        if len(parts) >= 4:
            # Ligne de sommet
            if parts[0] == 'v':
                res[0].append([float(_) for _ in parts[1:4]])
            
            # Ligne de face (triangle)
            if parts[0] == 'f':
                # Extrait les indices de vertices (ignore texture/normal)
                res[1].append([int(v.split('/')[0]) for v in parts[1:4]])
    
    return res


# ============================================================================
# PARSING INTERMÉDIAIRE
# ============================================================================

def lire_plus(file_name):
    """
    Parsing intermédiaire d'un fichier OBJ.
    
    Extrait sommets, faces, normales et coordonnées de texture.
    Les faces stockent les indices de sommet ET de normale.
    
    Format retourné :
    res[0] : Sommets [[x, y, z], ...]
    res[1] : Faces avec indices [[v_idx, n_idx], ...]
    res[2] : Normales [[nx, ny, nz], ...]
    res[3] : Coordonnées de texture [[u, v, w], ...]
    
    Args:
        file_name: Chemin du fichier OBJ
        
    Returns:
        Liste [vertices, faces_with_normals, normals, textures]
    """
    res = [[], [], [], []]
    
    for line in open(file_name):
        parts = line.split()
        
        if len(parts) >= 4:
            # Sommet
            if parts[0] == 'v':
                res[0].append([float(_) for _ in parts[1:4]])
            
            # Face : stocke indices de sommet ET normale
            if parts[0] == 'f':
                res[1].append([
                    [int(v.split('/')[0]), int(v.split('/')[-1])]
                    for v in parts[1:4]
                ])
            
            # Normale du sommet
            if parts[0] == 'vn':
                res[2].append([float(_) for _ in parts[1:4]])
            
            # Coordonnée de texture
            if parts[0] == 'vt':
                res[3].append([float(_) for _ in parts[1:4]])
    
    return res


# ============================================================================
# PARSING COMPLET
# ============================================================================

def lire_final(file_name):
    """
    Parsing complet d'un fichier OBJ (format standard).
    
    Extrait et structure tous les éléments :
    - Faces avec indices complets (vertex/texture/normal)
    - Sommets
    - Normales
    - Coordonnées de texture
    
    Format d'une face OBJ : f v/vt/vn v/vt/vn v/vt/vn
    - v : indice de sommet
    - vt : indice de coordonnée texture
    - vn : indice de normale
    
    Format retourné :
    res[0] : Faces [[v1/vt1/vn1, v2/vt2/vn2, v3/vt3/vn3], ...]
    res[1] : Sommets [[x, y, z], ...]
    res[2] : Coordonnées de texture [[u, v, w], ...]
    res[3] : Normales [[nx, ny, nz], ...]
    
    Args:
        file_name: Chemin du fichier OBJ
        
    Returns:
        Liste [faces, vertices, textures, normals]
    """
    res = [[], [], [], []]
    
    for line in open(file_name):
        parts = line.split()
        
        # Ignore les lignes vides
        if not parts:
            continue
        
        # Traite les faces et sommets
        if len(parts) >= 4:
            # Face avec tous les indices (v/vt/vn)
            if parts[0] == 'f':
                res[0].append([
                    [
                        int(v.split('/')[0]),      # Indice sommet
                        int(v.split('/')[1]),      # Indice texture
                        int(v.split('/')[2])       # Indice normale
                    ]
                    for v in parts[1:4]
                ])
            
            # Sommet
            if parts[0] == 'v':
                res[1].append([float(_) for _ in parts[1:4]])
            
            # Normale
            if parts[0] == 'vn':
                res[3].append([float(_) for _ in parts[1:4]])
        
        # Traite les coordonnées de texture (peuvent être 2D ou 3D)
        if len(parts) >= 3:
            if parts[0] == 'vt':
                res[2].append([float(_) for _ in parts[1:4]])
    
    return res
