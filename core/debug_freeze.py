import pygame


def debugger_freeze_loop(debugger, screen, WIDTH, HEIGHT):
    """
    Handles the debugger freeze mode.
    Returns True if the frame should be skipped (continue main loop).
    Returns False if normal gameplay should resume.
    """

    if not debugger.active:
        return False

    # Draw debugger overlay
    debugger.record_fps(pygame.time.Clock().get_fps())
    debugger.draw(screen, WIDTH, HEIGHT)
    pygame.display.flip()

    # Event loop while frozen
    for event in pygame.event.get():

        # Allow debugger to handle mouse selection + Ctrl+C
        debugger.handle_event(event)

        # Resume / Quit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                debugger.active = False
                return False  # resume gameplay

            elif event.key == pygame.K_q:
                pygame.quit()
                raise SystemExit(0)

    # Stay frozen — skip the rest of the frame
    return True
