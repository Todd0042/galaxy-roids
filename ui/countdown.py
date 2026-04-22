import pygame
from settings import BLACK, GOLDEN_YELLOW


def run_countdown(screen, font, seconds=3):
    """
    Displays a countdown (3..2..1) before gameplay starts.
    Blocks until finished or until the user quits.
    """

    WIDTH, HEIGHT = screen.get_size()

    for i in range(seconds, 0, -1):
        start_ticks = pygame.time.get_ticks()

        # Display each number for ~1 second
        while pygame.time.get_ticks() - start_ticks < 1000:
            screen.fill(BLACK)

            count_text = font.render(str(i), True, GOLDEN_YELLOW)
            screen.blit(
                count_text,
                (WIDTH // 2 - count_text.get_width() // 2,
                 HEIGHT // 2 - count_text.get_height() // 2)
            )

            pygame.display.flip()

            # Allow quitting during countdown
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit(0)
