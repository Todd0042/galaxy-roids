import pygame


# ==========================
#     GENERIC POPUP MENU
# ==========================

def popup_menu_loop(title, lines, options):
    """
    Generic popup menu loop.
    - title: string
    - lines: list of strings
    - options: list of (label, return_value)
    Returns: return_value of selected option, or "escape"
    """

    pygame.font.init()
    font = pygame.font.SysFont("Arial", 28)
    small_font = pygame.font.SysFont("Arial", 22)

    screen = pygame.display.get_surface()

    selected = 0
    clock = pygame.time.Clock()

    # ⭐ Mouse click debounce
    mouse_was_down = False

    while True:
        clock.tick(60)
        WIDTH, HEIGHT = screen.get_size()
        screen.fill((0, 0, 0))

        # --- Title ---
        title_surf = font.render(title, True, (255, 255, 0))
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 120))

        # --- Lines ---
        y = 200
        for line in lines:
            line_surf = small_font.render(line, True, (200, 200, 200))
            screen.blit(line_surf, (WIDTH // 2 - line_surf.get_width() // 2, y))
            y += 30

        # --- Options ---
        option_rects = []
        y += 40
        for i, (label, _) in enumerate(options):
            color = (255, 255, 255) if i == selected else (150, 150, 150)
            opt_surf = font.render(label, True, color)
            pos = (WIDTH // 2 - opt_surf.get_width() // 2, y)
            screen.blit(opt_surf, pos)

            # Store clickable rect
            rect = pygame.Rect(pos[0], pos[1], opt_surf.get_width(), opt_surf.get_height())
            option_rects.append(rect)

            y += 50

        pygame.display.flip()

        # --- Mouse handling ---
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]

        # Hover selects option
        for i, rect in enumerate(option_rects):
            if rect.collidepoint(mouse_x, mouse_y):
                selected = i

        # Debounced click
        if mouse_down and not mouse_was_down:
            for i, rect in enumerate(option_rects):
                if rect.collidepoint(mouse_x, mouse_y):
                    return options[i][1]

        mouse_was_down = mouse_down

        # --- Keyboard handling ---
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return "exit"

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    return "escape"

                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)

                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)

                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return options[selected][1]


# ==========================
#     VICTORY POPUP
# ==========================

def show_victory_popup(score, current_level):
    """
    Victory popup after defeating a boss.
    Returns: "harder", "same", or "exit"
    """

    title = "VICTORIOUS!"

    lines = [
        f"Level {current_level} Complete",
        f"Score: {score}",
        "",
        "You pushed back the invasion threat.",
        "Prepare for the next challenge."
    ]

    options = [
        ("Greater Challenge", "harder"),
        ("Just Vibe", "same"),
        ("Exit", "exit")
    ]

    result = popup_menu_loop(title, lines, options)

    if result == "escape":
        return "exit"

    return result


# ==========================
#       PAUSE POPUP
# ==========================

def show_pause_popup():
    """
    Pause menu popup.
    Returns: "resume" or "exit"
    """

    title = "PAUSED"

    lines = [
        "",
        "Take a breather.",
        "",
        "Use UP/DOWN to choose, ENTER to confirm."
    ]

    options = [
        ("Resume", "resume"),
        ("Exit to Desktop", "exit")
    ]

    result = popup_menu_loop(title, lines, options)

    if result in ("escape", None):
        return "resume"

    return result
