import pygame
from settings import BLACK, WHITE, CYAN, RED


def run_game_over(screen, font, score):
    """
    Displays the Game Over screen.
    Returns:
        "restart"  – player pressed R or clicked Restart
        "quit"     – player pressed Q, clicked Quit, or closed window
    """

    game_over = True

    # ⭐ Mouse click debounce
    mouse_was_down = False

    while game_over:
        WIDTH, HEIGHT = screen.get_size()
        screen.fill(BLACK)

        # --- Text surfaces ---
        over_text = font.render("GAME OVER", True, RED)
        score_text = font.render(f"Final Score: {score}", True, WHITE)
        prompt_text = font.render("Restart (R)     Quit (Q)", True, CYAN)

        # --- Positions ---
        over_pos = (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 80)
        score_pos = (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 20)
        prompt_pos = (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 40)

        # Draw text
        screen.blit(over_text, over_pos)
        screen.blit(score_text, score_pos)
        screen.blit(prompt_text, prompt_pos)

        pygame.display.flip()

        # --- Mouse handling ---
        mouse_down = pygame.mouse.get_pressed()[0]
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Clickable zones
        prompt_rect = pygame.Rect(
            prompt_pos[0], prompt_pos[1],
            prompt_text.get_width(), prompt_text.get_height()
        )

        # ⭐ Debounced click
        if mouse_down and not mouse_was_down:

            if prompt_rect.collidepoint(mouse_x, mouse_y):
                # Split the prompt into left/right halves
                mid_x = prompt_pos[0] + prompt_text.get_width() // 2

                if mouse_x < mid_x:
                    return "restart"
                else:
                    return "quit"

        mouse_was_down = mouse_down

        # --- Keyboard handling ---
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_q:
                    return "quit"

                if event.key == pygame.K_r:
                    return "restart"
