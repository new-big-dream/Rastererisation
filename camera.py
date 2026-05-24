import numpy as np

def normalize_vector(v):
    x,y,z = v
    norm = np.sqrt(x**2 + y**2 + z**2)
    if norm == 0:
        return 0
    else:
        return np.array([x/norm,y/norm,z/norm])
    

def viewport_make(x,y, w, h): #(x,y) top left corner, (w,h) = size of the window
    return np.array(
    [
        [w/2., 0.,   0., x + w/2.],
        [0.,   h/2., 0., y + h/2.],
        [0.,   0.,   1., 0.      ],
        [0.,   0.,   0., 1.      ],
    ])

def perspective_make(f):
    return np.array([
    [1., 0., 0., 0.],
    [0., 1., 0., 0.],
    [0., 0., 1., 0.],
    [0., 0., -1./f, 1.],
        ])

def project_matrix(v,w,h):
    x,y,z = v
    return np.array([(x+1)*w, (y+1)*h,(z+1)*255/2])
  

def lookat(eye, center, up):
    n = normalize_vector(eye - center)
    l = normalize_vector(np.cross(up, n))
    m = normalize_vector(np.cross(n,l))
    
    cx,cy,cz = center
    lx,ly,lz = l
    mx,my,mz = m
    nx,ny,nz = n
    
    R = np.array([
        [lx, ly, lz, 0.],
        [mx, my, mz, 0.],
        [nx, ny, nz, 0.],
        [0.,  0.,  0.,  1.],
    ])

    T = np.array([
        [1., 0., 0., -cx],
        [0., 1., 0., -cy],
        [0., 0., 1., -cz],
        [0., 0., 0.,  1.],
    ])
    return R @ T # =ModelView





###########"old functions

def rot(v, theta):
    x, y, z = v
    # rotation autour de l'axe Y
    x_new = np.cos(theta)*x + np.sin(theta)*z
    y_new = y
    z_new = -np.sin(theta)*x + np.cos(theta)*z
    return [x_new, y_new, z_new]

def persp(v, c): #centrale projection
    x,y,z = v
    return v / (1-z/c)





#have to merge them into one later
def normalize(s, bounds): #bounds = [[xmin,xmax], ...] #normalize around [-1,1]
    x, y, z = s
    xmin, xmax = bounds[0]
    ymin, ymax = bounds[1]
    zmin, zmax = bounds[2]

    nx = 2 * (x - xmin) / (xmax - xmin) - 1
    ny = 2 * (y - ymin) / (ymax - ymin) - 1
    nz = 2 * (z - zmin) / (zmax - zmin) - 1

    return [nx, ny, nz]
    
def normalize2(s, bounds): #bounds = [[xmin,xmax], ...] #normalize around [-1,1]
    x, y = s
    xmin, xmax = bounds[0]
    ymin, ymax = bounds[1]

    nx = 2 * (x - xmin) / (xmax - xmin) - 1
    ny = 2 * (y - ymin) / (ymax - ymin) - 1

    return [nx, ny]
    

