import numpy as np
from PIL import Image
import random

import parse
import camera


file = "diablo3_pose.obj"
file = "head.obj"
fichier = "C:/Users/sami/Desktop/Rasterizer - Python/" + file

white = (255, 255, 255, 255) #automatiquement converti en tableau np.uint après assignement
green = (0,255,0,255)
red = (255,128,64,255)
blue = (0, 128, 255, 255)
yellow = (255, 200, 0, 255)
black = (0,0,0,0)


width  = 800
height = 800

# camera parameters
eye    = np.array([-1., 0., 2.])
center = np.array([0., 0., 0.])
up     = np.array([0., 1., 0.])

# build needed matrices
ModelView = camera.lookat(eye, center, up)
perspective = camera.perspective_make(np.linalg.norm(eye - center))
Viewport = camera.viewport_make(width/16, height/16, width*7/8, height*7/8)


framebuffer = np.zeros((width, height, 4), dtype = np.uint8) #RGBA
zbuffer = np.array([[-np.inf for j in range(height+2)] for i in range(width+2)])




def project(s): #project [x,y,z] into [x',y']
    x,y,z = s
    scale = 400 ##########################################
    cx, cy = width // 2, height // 2
    return [int(cx + x * scale), int(cy - y * scale)]

def project_with_depth(s): #camera.project [x,y,z] into [x',y',z]
    x,y,z = s
    scale = 400 ##########################################
    cx, cy = width // 2, height // 2
    return [int(cx + x * scale), int(cy - y * scale), z]

def homogene(s): #[x,y,z] into [x,y,z,1]
    x,y,z = s
    return np.array([x,y,z,1])

def random_rgba():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    a = random.randint(0, 255)
    return (r, g, b, a)


############# geometric primitives
def set(x,y,fb, color): #color = (R,G,B,A)
    if 0<=x<len(fb) and 0<=y<len(fb[x]):
        fb[x][y] = color
    
def clear(fb, color):
    for x in range(len(fb)):
        for y in range(len(fb[x])):
            fb[x][y] = color

def line(p1,p2,fb,color): #p = [x,y]
    ax, ay = p1
    bx, by = p2
    steep = abs(ax-by) < abs(ay-by)
    if steep: #if steep, we increment the y-axis
        ax, ay = ay, ax
        bx, by = by, bx
    if ax>bx:
        ax, bx = bx, ax
        ay, by = by, ay
    for x in range(ax,bx):
        t = (x-ax) / (bx-ax)
        y = int((ay + (by-ay)*t))
        if steep:
            set(y,x, fb, color)
        else:
            set(x,y,fb, color)

def triangle(clip, fb, zb, color):
    ndc = np.array([clip[i]/clip[i][3] for i in range(3)]) #normalized device coordinates
    screen = np.array([(Viewport @ ndc[i])[0:2] for i in range(3)]) #defined by top left and bottom right corner
    
    ax, ay = screen[0]
    bx, by= screen[1]
    cx, cy= screen[2]
    
    az,bz,cz = ndc[0][3], ndc[1][3], ndc[2][3]
    
    # bounding box
    bbminx = int(min(ax, bx, cx))
    bbminy = int(min(ay, by, cy))
    bbmaxx = int(max(ax, bx, cx))
    bbmaxy = int(max(ay, by, cy))
    

    
    ABC = np.array([np.concatenate((screen[i][0:2], [1])) for i in range(3)])
    area = np.linalg.det(ABC)
    
    if area >= 1 :  #backface culling + discarding triangles that cover less than a pixel
        for x in range(bbminx, bbmaxx + 1):
            for y in range(bbminy, bbmaxy + 1):
                
                #barycentric coordinates
                p = np.array([x,y,1])
                barycentric_coordinates = np.linalg.inv(ABC.T) @ p
                alpha, beta, gamma = barycentric_coordinates

                
                if alpha < 0 or beta < 0 or gamma < 0: #pixel outside the triangle
                    continue
                
                #compute z
                z = alpha*az + beta * bz + gamma * cz
                
                if 0<=x<width and 0<=y<height:
                    if z >= zb[x][y]:
                        set(x,y,zb,z)
                        
                        #set pixel, only if not behind already set one                                                
                        
                        z_min = zb[width][height]
                        z_max = zb[width+1][height+1]
                        
                        
                        #colors
                        ########change the *__
                        c = int(round((abs(z - z_min)/(z_max - z_min))*40)); c = 0 if c<0 else (255 if c>255 else c)
                        ##remove to have random colours
                        #color = (c,c,c,255)
                        
                        
                        set(x,y,fb, color)




###########image converters        
def obj_to_lines(fichier, fb, color):
    tab = parse.lire(fichier)
    for x,y,z in tab[1]:
        a, b, c = tab[0][x-1], tab[0][y-1], tab[0][z-1]
        a,b,c = project(a), project(b), project(c)

        line(a, b, fb, color)
        line(a, c, fb, color)
        line(b, c, fb, color)       
    
       
def rasterizer(fichier,fb, zb):

    tab = parse.lire(fichier)
    
    #bounds of rendered image
    xs = [p[0] for p in tab[0]]
    ys = [p[1] for p in tab[0]]
    zs = [p[2] for p in tab[0]]
    bounds = [[min(xs), max(xs)], [min(ys), max(ys)], [min(zs), max(zs)]]
    z_max = bounds[2][1]
    z_min = bounds[2][0]
        
    
    i = -1
    
    #iterate through all triangles
    for x,y,z in tab[1]:
        #loading screen
        i+=1
        if int(i/len(tab[1])*100) != int((i-1)/len(tab[1])*100):
            print(int(i/len(tab[1])*100), "%")
        
        
        #iterate through all three points of the triangle
        p1,p2,p3 = tab[0][x-1], tab[0][y-1], tab[0][z-1]
        clip = [p1,p2,p3] #clipping space
        for j in [0,1,2]: #for each point
            clip[j] = perspective @ ModelView @homogene(clip[j])
        
        #zbuffer update : last values of zb are z_min and z_max
        zb[width][height] = z_min
        zb[width+1][height+1] = z_max
        z1,z2,z3 = p1[2],p2[2],p3[2]
        
        #color
        color = random_rgba()
        
        #draw triangle
        triangle(clip, fb, zb, color)



def obj_to_triangles_RGBA(fichier,fb):
    tab = parse.lire(fichier)
    for x,y,z in tab[1]:
        p1,p2,p3 = tab[0][x-1], tab[0][y-1], tab[0][z-1]
        p1, p2, p3 = project(p1), project(p2), project(p3)
        color = random_rgba()
        triangle_new(p1,p2,p3,fb,color)
            

###main
clear(framebuffer,black)
rasterizer(fichier, framebuffer, zbuffer)

###rendering
Image.fromarray(framebuffer, 'RGBA').show()


