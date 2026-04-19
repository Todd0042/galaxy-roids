import pygame
from settings import BLACK, WHITE, CYAN, GOLDEN_YELLOW


def run_level_select(font):
    """
    Displays the starting level selection screen.
    Returns the selected starting level (int).
    """

    screen = pygame.display.get_surface()
    WIDTH, HEIGHT = screen.get_size()

    selected_start_level = 1
    waiting_for_start = True

    while waiting_for_start:
        screen.fill(BLACK)

        # --- Text surfaces ---
        title_text = font.render("Choose Starting Level", True, WHITE)
        level_text = font.render(f"Level: {selected_start_level}", True, CYAN)
        prompt_text = font.render(
            "LEFT/RIGHT to change — ENTER to start",
            True,
            GOLDEN_YELLOW
        )

        # --- Draw text ---
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 40))
        screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2))
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 40))

        pygame.display.flip()

        # --- Input handling ---
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:

                # Adjust level
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    selected_start_level = max(1, selected_start_level - 1)

                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    selected_start_level += 1

                # Confirm start
                if event.key == pygame.K_RETURN:
                    waiting_for_start = False

                # Quit
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit

    return selected_start_level
