import pygame
from settings import BLACK, WHITE, CYAN, RED


def run_game_over(screen, font, score):
    """
    Displays the Game Over screen.
    Returns:
        "restart"  – player pressed R
        "quit"     – player pressed Q or closed window
    """

    WIDTH, HEIGHT = screen.get_size()
    game_over = True

    while game_over:
        screen.fill(BLACK)

        # --- Text surfaces ---
        over_text = font.render("GAME OVER", True, RED)
        score_text = font.render(f"Final Score: {score}", True, WHITE)
        prompt_text = font.render("Press R to Restart or Q to Quit", True, CYAN)

        # --- Draw text ---
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2,
                                HEIGHT // 2 - 60))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2,
                                 HEIGHT // 2))
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2,
                                  HEIGHT // 2 + 40))

        pygame.display.flip()

        # --- Input handling ---
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_q:
                    return "quit"

                if event.key == pygame.K_r:
                    return "restart"
