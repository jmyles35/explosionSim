import pygame
pygame.init()

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

size = (500, 500)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Animation Test")
clock = pygame.time.Clock()

rect_c = [50, 50]
rect_speed = 5

done = False

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    screen.fill(BLACK)

    pygame.draw.rect(screen, WHITE, [rect_c[0], rect_c[1], 50, 50])
    rect_c[0] += rect_speed
    rect_c[1] += rect_speed

    if rect_c[0] > 450 or rect_c[0] < 0:
        rect_speed *= -1

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
