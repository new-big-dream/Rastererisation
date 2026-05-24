import numpy as np

def normalize_vector(v):
    x,y,z = v
    norm = np.sqrt(x**2 + y**2 + z**2)
    if norm == 0:
        return np.array([0, 0, 0])
    else:
        return np.array([x/norm,y/norm,z/norm])

def phong_color(p1, p2, p3, light): #light = vecteur qui pointe vers lumière
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)
    # normale du triangle (coordonnées caméra)
    n = normalize_vector(np.cross(p2 - p1, p3 - p1))
    l = normalize_vector(light)
    # réflexion
    r = normalize_vector(2 * n * np.dot(n, l) - l)

    ambient = 0.01
    diff = abs(np.dot(n, l))
    spec = max(r[2], 0.0) ** 0.002

    intensity = min(1.0, ambient + 0.4 * diff + 0.9 * spec)
    c = int(round(255 * intensity))

    # retourne directement un tuple RGBA
    return (c, c, c, 255)

def phong_color_normal(n,light):
    l = normalize_vector(light)
    # réflexion
    r = normalize_vector(2 * n * np.dot(n, l) - l)

    ambient = 0.01
    diff = abs(np.dot(n, l))
    spec = max(r[2], 0.0) ** 0.002

    intensity = min(1.0, ambient + 0.4 * diff + 0.9 * spec)
    c = int(round(255 * intensity))

    # retourne directement un tuple RGBA
    return (c, c, c, 255)

