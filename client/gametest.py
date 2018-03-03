import pygame
pygame.init()

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

size = 500, 500
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Explosion Test")
clock = pygame.time.Clock()

done = False
screen.fill(WHITE)

while not done:
    mouseClick = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouseClick = not mouseClick

    if mouseClick:
        pygame.draw.ellipse(screen, RED, [200, 200, 100, 100], 1)

    font = pygame.font.SysFont('timesnewroman', 50, True, True)
    text = font.render("Hello.", False, BLACK)
    screen.blit(text, [190, 125])

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
