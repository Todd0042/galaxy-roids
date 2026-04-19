import pygame
from entities.projectiles import ShrapnelBullet
from ui.popups import show_pause_popup
from settings import SHRAPNEL_COOLDOWN_MAX


def handle_gameplay_input(event, player, groups, state, sfx):
    """
    Handles all gameplay-related input:
    - Pause
    - Fire button press/release
    - Shrapnel grenade
    """

    # --- Pause ---
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        result = show_pause_popup()
        if result == "exit":
            pygame.quit()
            raise SystemExit
        return

    # -------------------------------------------------------
    #   FIRE BUTTON PRESS
    # -------------------------------------------------------
    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT):
            player.fire_button_held = True

    # -------------------------------------------------------
    #   FIRE BUTTON RELEASE  ⭐ CRITICAL FIX
    # -------------------------------------------------------
    if event.type == pygame.KEYUP:
        if event.key in (pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT):
            player.fire_button_held = False
            state["single_shot_fired"] = False   # <-- prevents permanent lockout

    # -------------------------------------------------------
    #   SPECIAL GRENADE (Enter + Caps Lock)
    # -------------------------------------------------------
    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_RETURN, pygame.K_CAPSLOCK):
            if player.shrapnel_cooldown == 0:
                s = ShrapnelBullet(
                    player.pos,
                    player.angle,
                    state["WIDTH"],
                    state["HEIGHT"]
                )
                groups["shrapnel_grenades"].add(s)
                groups["all_sprites"].add(s)
                player.shrapnel_cooldown = SHRAPNEL_COOLDOWN_MAX
