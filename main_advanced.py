import numpy as np
from PIL import Image
import random

import parse
import camera
import shader

file = "rp_dennis_posed_004.obj"
fichier = "C:/Users/sami/Desktop/Rasterizer - Python/" + file

diffuse_img = Image.open("C:/Users/sami/Desktop/Rasterizer - Python/rp_dennis_posed_004_dif.tga").convert("RGBA")
diffuse_pixels = np.array(diffuse_img)  # shape (H, W, 4)

white = (255, 255, 255, 255) #automatiquement converti en tableau np.uint après assignement
green = (0,255,0,255)
red = (255,128,64,255)
blue = (0, 128, 255, 255)
yellow = (255, 200, 0, 255)
black = (0,0,0,0)


width  = 1024
height = 1024

#print(len(diffuse_pixels), len(diffuse_pixels[0]), height, width)


# camera parameters
eye    = np.array([-1., 0., 2.])
center = np.array([0., 0., 0.])
up     = np.array([0., 1., 0.])

# build needed matrices
ModelView = camera.lookat(eye, center, up)
perspective = camera.perspective_make(np.linalg.norm(eye - center))
viewport = camera.viewport_make(width/16, height/16, width*7/8, height*7/8)
light = np.array([0.5,0.5,1])


framebuffer = np.zeros((width, height, 4), dtype = np.uint8) #RGBA
zbuffer = np.array([[-np.inf for j in range(height+2)] for i in range(width+2)])






def project(s): #project [x,y,z] into [x',y']
    x,y = s
    scale = 400 ##########################################
    cx, cy = width // 2, height // 2
    return [int(cx + x * scale), int(cy - y * scale)]

def project_with_depth(s): #camera.project [x,y,z] into [x',y',z]
    x,y,z = s
    scale = 400 ##########################################
    cx, cy = width // 2, height // 2
    return np.array([int(cx + x * scale), int(cy - y * scale), z])


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

def triangle(s1,s2,s3, fb, color, zb):
    ax, ay, az = s1
    bx, by, bz = s2
    cx, cy, cz = s3
    
    # bounding box
    bbminx = int(min(ax, bx, cx))
    bbminy = int(min(ay, by, cy))
    bbmaxx = int(max(ax, bx, cx))
    bbmaxy = int(max(ay, by, cy))
    
    def signed_triangle_area(ax, ay, bx, by, cx, cy):
        return 0.5 * ((by - ay)*(bx + ax) + (cy - by)*(cx + bx) + (ay - cy)*(ax + cx))

    total_area = signed_triangle_area(ax, ay, bx, by, cx, cy)
    if total_area >= 1 :  #############
        for x in range(bbminx, bbmaxx + 1):
            for y in range(bbminy, bbmaxy + 1):
                
                #barycentric coordinates
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
                        c = int(round((abs(z - z_min)/(z_max - z_min))*40)); c = 0 if c<0 else (255 if c>255 else c)
                        ##remove to have random colours
                        #color = (c,c,c,255)
                        set(x,y,fb, color)



def triangle_smooth(s1,s2,s3,n1,n2,n3, fb, color, zb):
    ax, ay, az = s1
    bx, by, bz = s2
    cx, cy, cz = s3
    
    # bounding box
    bbminx = int(min(ax, bx, cx))
    bbminy = int(min(ay, by, cy))
    bbmaxx = int(max(ax, bx, cx))
    bbmaxy = int(max(ay, by, cy))
    
    def signed_triangle_area(ax, ay, bx, by, cx, cy):
        return 0.5 * ((by - ay)*(bx + ax) + (cy - by)*(cx + bx) + (ay - cy)*(ax + cx))

    total_area = signed_triangle_area(ax, ay, bx, by, cx, cy)
    if total_area >= 1 :  #############
        for x in range(bbminx, bbmaxx + 1):
            for y in range(bbminy, bbmaxy + 1):
                
                #barycentric coordinates
                alpha = signed_triangle_area(x, y, bx, by, cx, cy) / total_area
                beta  = signed_triangle_area(x, y, cx, cy, ax, ay) / total_area
                gamma = signed_triangle_area(x, y, ax, ay, bx, by) / total_area
                
                
                if alpha < 0 or beta < 0 or gamma < 0: #pixel outside the triangle
                    continue
                
                #compute z
                z = alpha*az + beta * bz + gamma * cz
                n = alpha*n1 + beta * n2 + gamma*n3
                
                #color = shader.phong_color_normal(n,light)
                
                
                
                if 0<=x<width and 0<=y<height:
                    if z >= zb[x][y]:
                        set(x,y,zb,z)
                        #set pixel, only if not behind already set one                                                
                        
                        z_min = zb[width][height]
                        z_max = zb[width+1][height+1]
                        
                        color = diffuse_pixels[y][x]
                        ########change the *__
                        #c = int(round((abs(z - z_min)/(z_max - z_min))*40)); c = 0 if c<0 else (255 if c>255 else c)
                        ##remove to have random colours
                        #color = (c,c,c,255)
                        set(x,y,fb, color)


def triangle_smooth_texture(data, fb, color, zb):
    s1,s2,s3,uv1, uv2,uv3, n1,n2,n3 = data
    ax, ay, az = s1
    bx, by, bz = s2
    cx, cy, cz = s3
    
    # bounding box
    bbminx = int(min(ax, bx, cx))
    bbminy = int(min(ay, by, cy))
    bbmaxx = int(max(ax, bx, cx))
    bbmaxy = int(max(ay, by, cy))
    
    def signed_triangle_area(ax, ay, bx, by, cx, cy):
        return 0.5 * ((by - ay)*(bx + ax) + (cy - by)*(cx + bx) + (ay - cy)*(ax + cx))

    total_area = signed_triangle_area(ax, ay, bx, by, cx, cy)
    if total_area >= 1 :  #############
        
        for x in range(bbminx, bbmaxx + 1):
            for y in range(bbminy, bbmaxy + 1):
                
                #barycentric coordinates
                alpha = signed_triangle_area(x, y, bx, by, cx, cy) / total_area
                beta  = signed_triangle_area(x, y, cx, cy, ax, ay) / total_area
                gamma = signed_triangle_area(x, y, ax, ay, bx, by) / total_area
                
                
                if alpha < 0 or beta < 0 or gamma < 0: #pixel outside the triangle
                    continue
                
                #compute z (lissage par triangle)
                z = alpha*az + beta * bz + gamma * cz
                n = alpha*n1 + beta * n2 + gamma*n3
                u = alpha*uv1[0] + beta * uv2[0] + gamma*uv3[0]
                v = alpha*uv1[1] + beta * uv2[1] + gamma*uv3[1]
                
                #color = shader.phong_color_normal(n,light)
                
                
                
                if 0<=x<width and 0<=y<height:
                    if z >= zb[x][y]:
                        set(x,y,zb,z)
                        #set pixel, only if not behind already set one                                                
                        
                        z_min = zb[width][height]
                        z_max = zb[width+1][height+1]
                        
                        ty = (1-v)*(height-1)
                        tx = u*(width-1)
                        #### should check not out of range (if the framebuffer bigger than the texturea array
                        color = diffuse_pixels[int(ty)][int(tx)]
                        ########change the *__
                        #c = int(round((abs(z - z_min)/(z_max - z_min))*40)); c = 0 if c<0 else (255 if c>255 else c)
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
    
       
def rasterizer_smooth(fichier,fb, zb):
    tab = parse.lire_plus(fichier)
    
    #bounds of rendered image
    xs = [p[0] for p in tab[0]]
    ys = [p[1] for p in tab[0]]
    zs = [p[2] for p in tab[0]]
    bounds = [[min(xs), max(xs)], [min(ys), max(ys)], [min(zs), max(zs)]]
    z_max = bounds[2][1]
    z_min = bounds[2][0]
        
    
    i = -1
    
    #iterate through all triangles
    for (px,nx), (py,ny) , (pz,nz) in tab[1]: 
        
        #loading screen
        i+=1
        if int(i/len(tab[1])*100) != int((i-1)/len(tab[1])*100):
            print(int(i/len(tab[1])*100), "%")
        
        
        #iterate through all three points of the triangle
        p1,p2,p3 = tab[0][px-1], tab[0][py-1], tab[0][pz-1]
        n1,n2,n3 = tab[2][nx-1], tab[2][ny-1], tab[2][nz-1]
        
        n1 = np.array(n1)
        n2 = np.array(n2)
        n3 = np.array(n3)

        #color
        color = random_rgba()
        #color = shader.phong_color(p1, p2, p3, light)

        
        #zbuffer update : last values of zb are z_min and z_max
        zb[width][height] = z_min
        zb[width+1][height+1] = z_max
        z1,z2,z3 = p1[2],p2[2],p3[2]
        
        #camera
        
        p1,p2,p3 = camera.normalize(p1, bounds), camera.normalize(p2, bounds), camera.normalize(p3, bounds)### pour agrandir au risque de déformer
        
        
        p1 = camera.rot(p1, np.pi+0.2)
        p2 = camera.rot(p2, np.pi+0.2)
        p3 = camera.rot(p3, np.pi+0.2)
        
        p1,p2,p3 = project_with_depth(p1), project_with_depth(p2), project_with_depth(p3)

        
        #draw triangle
        triangle_smooth(p1,p2,p3,n1,n2,n3, fb, color, zb)



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
        
        #color
        color = random_rgba()
        #color = shader.phong_color(p1, p2, p3, light)

        
        #zbuffer update : last values of zb are z_min and z_max
        zb[width][height] = z_min
        zb[width+1][height+1] = z_max
        z1,z2,z3 = p1[2],p2[2],p3[2]
        
        #camera
        p1,p2,p3 = camera.normalize(p1, bounds), camera.normalize(p2, bounds), camera.normalize(p3, bounds)### pour agrandir au risque de déformer
        
        p1 = camera.rot(p1, np.pi+0.2)
        p2 = camera.rot(p2, np.pi+0.2)
        p3 = camera.rot(p3, np.pi+0.2)
        
        p1,p2,p3 = project_with_depth(p1), project_with_depth(p2), project_with_depth(p3)

        
        #draw triangle
        triangle(p1,p2,p3, fb, color, zb)


def rasterizer_smooth_texture(fichier,fb, zb):
    tab = parse.lire_final(fichier)
    print("File parsed.")
    #bounds of rendered image
    xs = [p[0] for p in tab[1]]
    ys = [p[1] for p in tab[1]]
    zs = [p[2] for p in tab[1]]
    bounds = [[min(xs), max(xs)], [min(ys), max(ys)], [min(zs), max(zs)]]
    z_max = bounds[2][1]
    z_min = bounds[2][0]
        
    
    i = -1
    
    #iterate through all triangles
    for x,y,z in tab[0]:
        px,uvx,nx = x
        py,uvy,ny = y
        pz,uvz,nz = z
        print(i)
        
        #loading screen
        i+=1
        if int(i/len(tab[0])*100) != int((i-1)/len(tab[0])*100):
            print(int(i/len(tab[0])*100), "%") #pourcentage des triangles traités
        
        
        #iterate through all three points of the triangle
        p1,p2,p3 = tab[1][px-1], tab[1][py-1], tab[1][pz-1]
        uv1,uv2,uv3 = tab[2][uvx-1], tab[2][uvy-1], tab[2][uvz-1]
        n1,n2,n3 = tab[3][nx-1], tab[3][ny-1], tab[3][nz-1]
    
            
        n1 = np.array(n1)
        n2 = np.array(n2)
        n3 = np.array(n3)

        #color
        color = random_rgba()
        #color = shader.phong_color(p1, p2, p3, light)

        
        #zbuffer update : last values of zb are z_min and z_max
        zb[width][height] = z_min
        zb[width+1][height+1] = z_max
        z1,z2,z3 = p1[2],p2[2],p3[2]
        
        #camera
        """
        p1,p2,p3 = camera.normalize(p1, bounds), camera.normalize(p2, bounds), camera.normalize(p3, bounds)### pour agrandir au risque de déformer
        #uv1,uv2,uv3= camera.normalize2(uv1, bounds), camera.normalize2(uv2,bounds), camera.normalize2(uv3,bounds)
        n1,n2,n3 = camera.normalize(n1, bounds), camera.normalize(n2, bounds), camera.normalize(n3, bounds)
        
        p1 = camera.rot(p1, np.pi+0.2)
        p2 = camera.rot(p2, np.pi+0.2)
        p3 = camera.rot(p3, np.pi+0.2)
        """
        
        
        #La texture est appliquée sur la face arrière du triangle donc :
        p1 = camera.rot(p1, np.pi)
        p2 = camera.rot(p2, np.pi)
        p3 = camera.rot(p3, np.pi)
        
        
        p1,p2,p3 = project_with_depth(p1), project_with_depth(p2), project_with_depth(p3)
        #uv1, uv2, uv3 = project(uv1), project(uv2), project(uv3)
        n1,n2,n3 = project_with_depth(n1), project_with_depth(n2), project_with_depth(n3)

        data = p1,p2,p3,uv1,uv2,uv3,n1,n2,n3
        
        #draw triangle
        triangle_smooth_texture(data, fb, color, zb)


def obj_to_triangles_RGBA(fichier,fb):
    tab = parse.lire(fichier)
    for x,y,z in tab[1]:
        p1,p2,p3 = tab[0][x-1], tab[0][y-1], tab[0][z-1]
        p1, p2, p3 = project(p1), project(p2), project(p3)
        color = random_rgba()
        main_basic.triangle_old(p1,p2,p3,fb,color)
            

###main
clear(framebuffer,black)
rasterizer_smooth_texture(fichier, framebuffer, zbuffer)

###rendering
#Image.fromarray(framebuffer, 'RGBA').show()


###rendering
img = Image.fromarray(framebuffer)
Image.fromarray(framebuffer, 'RGBA').show()
img.save("a_line.png")

