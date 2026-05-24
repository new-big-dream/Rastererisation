import numpy as np
from PIL import Image
import random

import parse
import camera

file = "   " #mettre le l'adresse complète du fichier .obj

white = (255, 255, 255, 255) #automatiquement converti en tableau np.uint après assignement
green = (0,255,0,255)
red = (255,128,64,255)
blue = (0, 128, 255, 255)
yellow = (255, 200, 0, 255)
black = (0,0,0,0)


width = 1920
height = 1080


framebuffer = np.zeros((width, height, 4), dtype = np.uint8) #RGBA
zbuffer = np.array([[-np.inf for j in range(height+2)] for i in range(width+2)])


def project(s): #project [x,y,z] into [x',y']
    x,y,z = s
    scale = 400 ##########################################
    cx, cy = width // 2, height // 2
    return [int(cx + x * scale), int(cy - y * scale)]






"""
class Point:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

def to_point(lst): #Convert [x, y, z] list or tuple into a Point object.
    x, y, z = lst
    return Point(x, y, z)
"""

def random_rgba():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    a = random.randint(0, 255)
    return (r, g, b, a)


def set(x,y,fb, color): #color = (R,G,B,A)
    if 0<=x<len(fb) and 0<=y<len(fb[x]):
        fb[x][y] = color
    
def clear(fb, color):
    for x in range(len(fb)):
        for y in range(len(fb[x])):
            fb[x][y] = color
    
    




def line_naif1(p1,p2, fb, color): #p = [x,y]
    ax, ay = p1
    bx, by = p2
    
    for t in np.arange(0,1,0.02):
        x = int(ax + (bx-ax)*t)
        y = int(ay +  (by-ay)*t)
        set(x,y, fb, color)

def line_naif2(p1,p2, fb, color): #p = [x,y]
    ax, ay = p1
    bx, by = p2
    for x in range(ax,bx):
        t = (x-ax)/(bx-ax)
        y = int(ay + (by-ay)*t)
        set(x,y,fb,color)
   
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


def obj_to_lines(fichier, fb, color):
    tab = parse.lire(fichier)
    for x,y,z in tab[1]:
        a, b, c = tab[0][x-1], tab[0][y-1], tab[0][z-1]
        a,b,c = project(a), project(b), project(c)

        line(a, b, fb, color)
        line(a, c, fb, color)
        line(b, c, fb, color)        
    
def triangle_contour(p1,p2,p3,fb,color):
    line(p1,p2, fb, color)
    line(p1,p3, fb, color)
    line(p2,p3, fb, color)
    
def triangle_old(p1,p2,p3,fb, color):
    #bubble sort, increasing y-axis
    ax,bx,cx = p1[0], p2[0], p3[0]
    ay,by,cy = p1[1], p2[1], p3[1]
    if ay>by : ax,bx = bx,ax ; ay,by = by,ay
    if ay>cy : ax,cx = cx,ax ; ay,cy = cy,ay
    if by>cy : cx,bx = bx,cx ; cy,by = by,cy
    
    total_height = cy-ay
    
    if ay != by:
        segment_height = by-ay
        for y in range(ay,by): #interpolation linéaire
            x1 = ax + ((cx-ax)*(y-ay)) // total_height #find x from y (from a to c)
            x2 = ax + ((bx-ax)*(y-ay)) // segment_height #find x from y (from a to b)
            line([x1,y],[x2,y], fb, color)
        
    if by != cy:
        segment_height = cy-by
        ax,bx,cx = p1[0], p2[0], p3[0]
        for y in range(by,cy): #interpolation linéaire
            x1 = ax + ((cx-ax)*(y-ay)) // total_height #find x from y (from a to c)
            x2 = ax + ((bx-ax)*(y-ay)) // segment_height #find x from y (from a to b)
            line([x1,y],[x2,y], fb, color)
        
def triangle_new(p1,p2,p3, fb, color):
    ax, ay = p1
    bx, by = p2
    cx, cy = p3
    
    # bounding box
    bbminx = min(ax, bx, cx)
    bbminy = min(ay, by, cy)
    bbmaxx = max(ax, bx, cx)
    bbmaxy = max(ay, by, cy)
    
    def signed_triangle_area(ax, ay, bx, by, cx, cy):
        return 0.5 * ((by - ay)*(bx + ax) + (cy - by)*(cx + bx) + (ay - cy)*(ax + cx))

    total_area = signed_triangle_area(ax, ay, bx, by, cx, cy)
    if total_area >= 1 :  #############
        for x in range(bbminx, bbmaxx + 1):
            for y in range(bbminy, bbmaxy + 1):
                alpha = signed_triangle_area(x, y, bx, by, cx, cy) / total_area
                beta  = signed_triangle_area(x, y, cx, cy, ax, ay) / total_area
                gamma = signed_triangle_area(x, y, ax, ay, bx, by) / total_area
                if alpha < 0 or beta < 0 or gamma < 0: #pixel outside the triangle
                    continue
                
                #color = (alpha * 255, beta * 255, gamma * 255, 255) #coloration barycentrique RGB
                
                #g = min(alpha,beta,gamma)
                #color = (g * 255, g * 255, g * 255, 255) #coloration barycentrique grayscale avec min ou max
                set(x,y,fb, color)
    
def triangle_new_depth_interpolation(s1,s2,s3, fb, color, zb):
    ax, ay, az = s1
    bx, by, bz = s2
    cx, cy, cz = s3
    # bounding box
    bbminx = min(ax, bx, cx)
    bbminy = min(ay, by, cy)
    bbmaxx = max(ax, bx, cx)
    bbmaxy = max(ay, by, cy)
    
    def signed_triangle_area(ax, ay, bx, by, cx, cy):
        return 0.5 * ((by - ay)*(bx + ax) + (cy - by)*(cx + bx) + (ay - cy)*(ax + cx))

    total_area = signed_triangle_area(ax, ay, bx, by, cx, cy)
    if total_area > 0 :  #############
        for x in range(bbminx, bbmaxx + 1):
            for y in range(bbminy, bbmaxy + 1):
                alpha = signed_triangle_area(x, y, bx, by, cx, cy) / total_area
                beta  = signed_triangle_area(x, y, cx, cy, ax, ay) / total_area
                gamma = signed_triangle_area(x, y, ax, ay, bx, by) / total_area
                
                
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
                        
                        ########change the *__
                        c = int(round((abs(z - z_min)/(z_max - z_min))*255)); c = 0 if c<0 else (255 if c>255 else c)
                        ##remove to have random colours
                        color = (c,c,c,255)
                        set(x,y,fb, color)
    
    
def obj_to_triangles_grayscale(fichier,fb):
    tab = parse.lire(fichier)
    
    xs = [p[0] for p in tab[0]]
    ys = [p[1] for p in tab[0]]
    zs = [p[2] for p in tab[0]]
    bounds = [[min(xs), max(xs)], [min(ys), max(ys)], [min(zs), max(zs)]]

    
    for x,y,z in tab[1]:
        p1,p2,p3 = tab[0][x-1], tab[0][y-1], tab[0][z-1]
        #p1,p2,p3 = camera.normalize(p1, bounds), camera.normalize(p2, bounds), camera.normalize(p3, bounds)### pour agrandir au risque de déformer
        
        
        z1,z2,z3 = p1[2],p2[2],p3[2]
        color = random_rgba()
        #triangle_new(p1,p2,p3,fb,color)
        
        z_max = bounds[2][1]
        z_min = bounds[2][0]
        color = ((z1-z_min)/(-z_min + z_max)*255,(z2-z_min)/(-z_min + z_max)*255,(z3-z_min)/(-z_min + z_max)*255,255)
        
        p1,p2,p3 = project(p1), project(p2), project(p3)
        triangle_new(p1,p2,p3, fb, color)    
    
def obj_to_triangles_grayscale_depth_interpolation(fichier,fb, zb):
    tab = parse.lire(fichier)
    
    xs = [p[0] for p in tab[0]]
    ys = [p[1] for p in tab[0]]
    zs = [p[2] for p in tab[0]]
    bounds = [[min(xs), max(xs)], [min(ys), max(ys)], [min(zs), max(zs)]]

    i = -1
    for x,y,z in tab[1]:
        i+=1
        if int(i/len(tab[1])*100) != int((i-1)/len(tab[1])*100):
            print(int(i/len(tab[1])*100), "%")
        
        p1,p2,p3 = tab[0][x-1], tab[0][y-1], tab[0][z-1]
        #
        p1,p2,p3 = camera.normalize(p1, bounds), camera.normalize(p2, bounds), camera.normalize(p3, bounds)### pour agrandir au risque de déformer
        
        #camera
        
        

        z1,z2,z3 = p1[2],p2[2],p3[2]
        color = random_rgba()
        #triangle_new(p1,p2,p3,fb,color)
        
        z_max = bounds[2][1]
        z_min = bounds[2][0]
        
        #last values of zb are z_min and z_max
        zb[width][height] = z_min
        zb[width+1][height+1] = z_max

        
        def project_with_depth(s): #camera.project [x,y,z] into [x',y',z]
            x,y,z = s
            scale = 400 ##########################################
            cx, cy = width // 2, height // 2
            return [int(cx + x * scale), int(cy - y * scale), z]
                
        p1,p2,p3 = project_with_depth(p1), project_with_depth(p2), project_with_depth(p3)
        
        triangle_new_depth_interpolation(p1,p2,p3, fb, color, zb)






            
            
            
def obj_to_triangles_RGBA(fichier,fb):
    tab = parse.lire(fichier)
    for x,y,z in tab[1]:
        p1,p2,p3 = tab[0][x-1], tab[0][y-1], tab[0][z-1]
        p1, p2, p3 = project(p1), project(p2), project(p3)
        color = random_rgba()
        triangle_new(p1,p2,p3,fb,color)
            

###main
clear(framebuffer,white)
#obj_to_lines(fichier, framebuffer, red)
#obj_to_triangles_grayscale_depth_interpolation(fichier,framebuffer,zbuffer)
#triangle2([100,500],[1000,10],[900,800], framebuffer, white)

p1,p2, p3, p4 =  [70,100], [40,50], [60, 30], [16,90]

#obj_to_triangles_grayscale_depth_interpolation(file, framebuffer, zbuffer)

#triangle_new(p1,p3,p4,framebuffer, red )
obj_to_triangles_grayscale_depth_interpolation(fichier,framebuffer, zbuffer)

###rendering
img = Image.fromarray(framebuffer)
Image.fromarray(framebuffer, 'RGBA').show()
img.save("a_line.png")



