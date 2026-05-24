import pygame
import numpy as np
import parse


pygame.init()

width, height = 1920, 1080
file = "diablo3_pose.obj"
fichier = "C:/Users/sami/Desktop/Rasterizer - Python/" + file
print(fichier)


framebuffer = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Python Rasterizer")
clock = pygame.time.Clock()

def projeter(s):
    x,y,z = s
    scale = 400
    cx, cy = width // 2, height // 2
    return int(cx + x * scale), int(cy - y * scale)

def line(framebuffer, color, s1,s2): #s1, s2 sont des listes de 3 éléments
    pygame.draw.line(framebuffer, color, projeter(s1), projeter(s2)) #color = RGB or RGBA


running = True
while running:
    # Process player inputs.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Do logical updates here.
    # ...

    framebuffer.fill("black")  # Fill the display with a solid color

    # Render the graphics here.
    #pygame.draw.line(framebuffer, color, start, end)
    #pygame.draw.circle(framebuffer, color, pos, 3)
    
    tab = parse.lire(fichier)
    for x,y,z in tab[1]:
        a, b, c = tab[0][x-1], tab[0][y-1], tab[0][z-1]
        line(framebuffer, (255,0,0) , a, b)
        line(framebuffer, (255,0,0) , a, c)
        line(framebuffer, (255,0,0) , b, c)        
        

    pygame.display.flip()  # Refresh on-screen display
    clock.tick(144)         # wait until next frame (at 60 FPS)

pygame.quit()

