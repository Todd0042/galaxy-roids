import pygame
from settings import BLACK, WHITE, CYAN, GOLDEN_YELLOW
import systems.audio as audio   # music mode toggle support


def run_level_select(font, state):
    """
    Displays the starting level selection screen.
    Returns the selected starting level (int).
    """

    screen = pygame.display.get_surface()

    selected_start_level = 1
    waiting_for_start = True

    # ⭐ Mouse click debounce flag
    mouse_was_down = False

    while waiting_for_start:
        WIDTH, HEIGHT = screen.get_size()
        state["WIDTH"] = WIDTH
        state["HEIGHT"] = HEIGHT

        screen.fill(BLACK)

        # --- Text surfaces ---
        title_text = font.render("Choose Starting Level", True, WHITE)
        level_text = font.render(f"Level: {selected_start_level}", True, CYAN)
        music_text = font.render(f"Music: {audio.music_mode}", True, GOLDEN_YELLOW)
        prompt_text = font.render(
            "LEFT/RIGHT to change — ENTER to start — M to toggle music",
            True,
            GOLDEN_YELLOW
        )

        # --- Positions ---
        title_pos = (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 80)
        level_pos = (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2 - 20)
        music_pos = (WIDTH // 2 - music_text.get_width() // 2, HEIGHT // 2 + 20)
        prompt_pos = (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 70)

        # Draw text
        screen.blit(title_text, title_pos)
        screen.blit(level_text, level_pos)
        screen.blit(music_text, music_pos)
        screen.blit(prompt_text, prompt_pos)

        pygame.display.flip()

        # --- Mouse handling ---
        mouse_down = pygame.mouse.get_pressed()[0]  # left button
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Clickable zones
        level_rect = pygame.Rect(level_pos[0], level_pos[1],
                                 level_text.get_width(), level_text.get_height())

        music_rect = pygame.Rect(music_pos[0], music_pos[1],
                                 music_text.get_width(), music_text.get_height())

        prompt_rect = pygame.Rect(prompt_pos[0], prompt_pos[1],
                                  prompt_text.get_width(), prompt_text.get_height())

        # ⭐ Debounced click: only fires on press, not hold
        if mouse_down and not mouse_was_down:

            if level_rect.collidepoint(mouse_x, mouse_y):
                # Click left half = decrement
                if mouse_x < level_pos[0] + level_text.get_width() // 2:
                    selected_start_level = max(1, selected_start_level - 1)
                else:
                    selected_start_level += 1

            if music_rect.collidepoint(mouse_x, mouse_y):
                audio.music_mode = "8bit" if audio.music_mode == "16bit" else "16bit"
                audio.play_music("menu_theme")

            if prompt_rect.collidepoint(mouse_x, mouse_y):
                waiting_for_start = False

        # Update debounce state
        mouse_was_down = mouse_down

        # --- Keyboard handling ---
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:

                if event.key in (pygame.K_LEFT, pygame.K_a):
                    selected_start_level = max(1, selected_start_level - 1)

                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    selected_start_level += 1

                if event.key == pygame.K_m:
                    audio.music_mode = "8bit" if audio.music_mode == "16bit" else "16bit"
                    audio.play_music("menu_theme")

                if event.key == pygame.K_RETURN:
                    waiting_for_start = False

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit

    return selected_start_level

