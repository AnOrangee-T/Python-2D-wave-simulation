import pygame
import sys
import cupy as cp
from math import e, sqrt, dist, atan2, cos, sin

pygame.init()
print("----------------")
print("How small a pixel of a pond? (15: Small, 10: For Small-Medium, 7: Medium, 5: Large-Medium, 3: Large) The larger the pond, the laggier it get")
Res = int(input())
W = 800
H = 600
print("----------------")
print("Max FPS / How fast waves move")
fps=int(input())
print("Grid creation")

grid = cp.zeros((800//Res,600//Res))
grid_vel = cp.zeros((800//Res,600//Res))
_zeros = cp.zeros((800//Res,600//Res))
_255s = cp.ones((800//Res,600//Res))*255

print("Grid created")

diag = sqrt(2)/2

print("Setting up window")

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Wavez")
surf = pygame.Surface((W, H))
ssurf = pygame.Surface((W//Res, H//Res))

print("Set up window")

clock = pygame.time.Clock()
print("Run")
mx,my=pygame.mouse.get_pos()
running = True
while running:
    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[0]:
        dg=atan2(pygame.mouse.get_pos()[1]-my,pygame.mouse.get_pos()[0]-mx)
        mx+=cos(dg)*2
        my+=sin(dg)*2
    else:
        mx=pygame.mouse.get_pos()[0]
        my=pygame.mouse.get_pos()[1]
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("Closing...")
            running = False
            
    screen.fill((128,128,128))

    gridr = cp.pad(grid[1:, :], ((0, 1), (0, 0)), mode='constant')
    gridl = cp.pad(grid[:-1, :], ((1, 0), (0, 0)), mode='constant')
    gridu = cp.pad(grid[:, 1:], ((0, 0), (0, 1)), mode='constant')
    gridd = cp.pad(grid[:, :-1], ((0, 0), (1, 0)), mode='constant')
    gridru = cp.pad(grid[1:, 1:], ((0, 1), (0, 1)), mode='constant') * diag
    gridlu = cp.pad(grid[:-1, 1:], ((1, 0), (0, 1)), mode='constant') * diag
    gridrd = cp.pad(grid[1:, :-1], ((0, 1), (1, 0)), mode='constant') * diag
    gridld = cp.pad(grid[:-1, :-1], ((1, 0), (1, 0)), mode='constant') * diag

    grid_vel = grid_vel*0.995 + (((gridr + gridl + gridu + gridd + gridru + gridlu + gridrd + gridld) / 8)-grid)/50 
    grid += grid_vel

    colorgrid = 255/(1+cp.exp(0-(grid-gridl)))
    rgb_grid = cp.stack((cp.maximum(colorgrid-128,_zeros),(cp.minimum(colorgrid*2, _255s)*0.75)+((cp.maximum(colorgrid-128,_zeros)*0.25)),cp.minimum(colorgrid*2, _255s)), axis=-1)
    rgb_cpu = rgb_grid.get()
    pygame.surfarray.blit_array(ssurf, rgb_cpu)
    scaled_surf = pygame.transform.scale(ssurf, (W, H))
    screen.blit(scaled_surf, (0, 0))
    pygame.draw.circle(screen,(255,255,255),(mx,my),4*Res,2)

    if mouse_buttons[0]:
        for x in range(-2,3):
            if 0 <= mx//Res+x < W//Res:
                for y in range(-2,3):
                    if 0 <= my//Res+y < H//Res:
                        grid[mx//Res+x,my//Res+y] -= max(0,3-dist((x,y),(0,0)))

    pygame.display.flip()
    dt = clock.tick(fps)
    print(1000/dt)

pygame.quit()
print("Closed")
sys.exit()