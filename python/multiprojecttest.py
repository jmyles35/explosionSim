import pygame
pygame.init()

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

size = (600, 600)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Multiple Projectile Test")
clock = pygame.time.Clock()

#Initial values
x = [ 10,  73, 145, 218, 290, 363, 435, 507, 590]
y = [590, 590, 590, 590, 590, 590, 590, 590, 590]
v_x = [100,  80,  60,  50, 120, 100,  20,  80, 160]
v_y = [150, 170, 120, 140, 100,  90, 190, 170, 120]
a_x = 0
a_y = -9.81

def get_colour( i ):
    colour = (0, 0, 0)
    if i % 3 == 0:
        colour =  RED
    elif i % 3 == 1:
        colour = GREEN
    else:
        colour =  BLUE
    return colour;

done = False
mouseClick = False

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouseClick = not mouseClick

    screen.fill(BLACK)

    if mouseClick:
        font = pygame.font.SysFont('timesnewroman', 45, True, True)
        text = font.render("Pause.", False, WHITE)
        screen.blit(text, [20, 200])

    if not mouseClick:
        font = pygame.font.SysFont('timesnewroman', 45, True, True)
        text = font.render("Go.", False, WHITE)
        screen.blit(text, [20, 200])

        dt = clock.get_time() / 100;

        for i in range(8):
            x[i] += v_x[i] * dt + 1/2 * a_x * dt * dt
            y[i] += -1 * v_y[i] * dt - 1/2 * a_y * dt * dt #Backwards

            if x[i] < 10 or x[i] > 590:
                v_x[i] *= -0.9
                if x[i] < 10:
                    x[i] += 10
                elif x[i] > 590:
                    x[i] -= 5

            if y[i] < 10 or y[i] > 590:
                v_y[i] *= -0.9
                if y[i] < 10:
                    y[i] += 10
                elif y[i] > 590:
                    y[i] -= 5

    for i in range(8):
        c = get_colour(i)
        pygame.draw.circle(screen, c, [int(x[i]), int(y[i])], 10)

    pygame.display.flip()
    clock.tick(60)

pygame.quit
