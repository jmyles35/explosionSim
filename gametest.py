import pygame
pygame.init()

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

size = (500, 500)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Explosion Test")

done = False

clock = pygame.time.Clock()

while not done:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # Game logic

    # Drawing

    screen.fill(WHITE)
    pygame.display.flip()
    clock.tick(60)

    pygame.draw.ellipse(screen, BLACK, [20, 20, 250, 100], 2)
    pygame.display.flip()

pygame.quit()
