import pygame
from entities.projectiles import ShrapnelBullet
from ui.popups import show_pause_popup
from settings import SHRAPNEL_COOLDOWN_MAX, MEGABOMB_MAX
from systems import audio
from core.combat import fire_megabomb



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
            raise SystemExit(0)
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
    #   SPECIAL WEAPON CHARGE START
    # -------------------------------------------------------
    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_RETURN, pygame.K_CAPSLOCK):
            player.special_charging = True
            player.special_charge = 0

    # -------------------------------------------------------
    #   SPECIAL WEAPON RELEASE (burst or megabomb)
    # -------------------------------------------------------
    if event.type == pygame.KEYUP:
        if event.key in (pygame.K_RETURN, pygame.K_CAPSLOCK):

            player.special_charging = False

            # Respect cooldown
            if player.shrapnel_cooldown == 0:

                # Megabomb threshold: 8 seconds at 60fps
                if player.special_charge >= 8 * 30:
                    if player.megabomb_used < MEGABOMB_MAX:
                        fire_megabomb(player, groups, state, sfx)
                        player.megabomb_used += 1
                    else:
                        audio.play_sfx(sfx, "error")  # optional
                else:
                    # Normal 8-direction burst
                    angles = [0, 45, 90, 135, 180, 225, 270, 315]

                    for ang in angles:
                        s = ShrapnelBullet(
                            player.pos,
                            ang,
                            state["WIDTH"],
                            state["HEIGHT"]
                        )
                        groups["shrapnel_grenades"].add(s)
                        groups["all_sprites"].add(s)

                    audio.play_sfx(sfx, "grenade_launch")

                # Apply cooldown AFTER firing
                player.shrapnel_cooldown = SHRAPNEL_COOLDOWN_MAX
