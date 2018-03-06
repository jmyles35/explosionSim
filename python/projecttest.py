import pygame
pygame.init()

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

size = (600, 600)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Projectile Test")
clock = pygame.time.Clock()

#Initial values
x = 10
y = 590
v_x = 100
v_y = 150
a_x = 0
a_y = -1*9.81

done = False

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    screen.fill(BLACK)

    dt = clock.get_time() / 100;

    v_x += a_x * dt
    v_y += a_y * dt
    x += v_x * dt + 1/2 * a_x * dt
    y += -1 * v_y * dt - 1/2 * a_y * dt #Backwards

    if x < 10 or x > 590:
        v_x *= -1
        if x < 10:
            x += 10
        elif x > 590:
            x -= 10

    if y < 10 or y > 590:
        v_y *= -1
        if y < 10:
            y += 10
        elif y > 590:
            y -= 10

    pygame.draw.circle(screen, WHITE, [int(x), int(y)], 10)

    pygame.display.flip()
    clock.tick(60)

pygame.quit
