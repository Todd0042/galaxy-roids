import pygame

# --- Core Systems ---
from core.game_init import initialize_game
from core.debug_freeze import debugger_freeze_loop
from core.input_handler import handle_gameplay_input
from core.spawner import (
    spawn_random_powerups,
    spawn_boss_if_ready,
    spawn_periodic_enemy_waves,
    spawn_periodic_asteroids
)
from core.updater import update_all_sprites
from core.combat import handle_autofire
from core.collision_manager import process_collisions
from core.level_flow import handle_boss_defeat
from core.renderer import render_frame

# --- UI ---
from ui.level_select import run_level_select
from ui.countdown import run_countdown
from ui.game_over import run_game_over


def main():
    # ==========================
    # INITIALIZATION
    # ==========================
    game = initialize_game()

    screen      = game["screen"]
    clock       = game["clock"]
    font        = game["font"]
    debugger    = game["debugger"]
    sfx         = game["sfx"]
    player      = game["player"]
    joysticks   = game["joysticks"]
    groups      = game["groups"]
    state       = game["state"]

    WIDTH       = game["WIDTH"]
    HEIGHT      = game["HEIGHT"]

    # Store width/height in state for modules that expect it
    state["WIDTH"] = WIDTH
    state["HEIGHT"] = HEIGHT

    # Create the dynamic render surface
    render_surface = pygame.Surface((WIDTH, HEIGHT))
    state["render_surface"] = render_surface

    # ==========================
    # LEVEL SELECT
    # ==========================
    start_level = run_level_select(font, state)
    state["level"] = start_level

    # ==========================
    # COUNTDOWN
    # ==========================
    run_countdown(screen, font, seconds=3)

    # Begin gameplay
    state["game_active"] = True
    running = True

    # ==========================
    # MAIN GAME LOOP
    # ==========================
    while running:
        clock.tick(60)

        # --------------------------
        # DEBUG FREEZE MODE
        # --------------------------
        if debugger_freeze_loop(debugger, screen, WIDTH, HEIGHT):
            continue

        # --------------------------
        # INPUT + EVENTS
        # --------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # --- Handle window resizing ---
            if event.type == pygame.VIDEORESIZE:
                WIDTH = event.w
                HEIGHT = event.h

                # Recreate window in RESIZABLE mode
                screen = pygame.display.set_mode(
                    (WIDTH, HEIGHT),
                    pygame.RESIZABLE
                )

                # Recreate the dynamic render surface
                render_surface = pygame.Surface((WIDTH, HEIGHT))

                # Update state so all modules see new size
                state["WIDTH"] = WIDTH
                state["HEIGHT"] = HEIGHT
                state["render_surface"] = render_surface

                continue

            handle_gameplay_input(event, player, groups, state, sfx)

        # --------------------------
        # AUTO-FIRE
        # --------------------------
        handle_autofire(player, groups, sfx, state)

        # --------------------------
        # SPAWNING
        # --------------------------
        spawn_random_powerups(state, groups)
        spawn_boss_if_ready(state, groups, play_music=sfx["play_music"])
        spawn_periodic_enemy_waves(state, groups)
        spawn_periodic_asteroids(state, groups)

        # --------------------------
        # UPDATE SPRITES
        # --------------------------
        if not update_all_sprites(player, joysticks, groups, debugger, state):

            continue

        # --------------------------
        # COLLISIONS
        # --------------------------
        collision_result = process_collisions(player, groups, state, sfx)

        if collision_result == "player_dead":
            running = False
            break

        if collision_result == "boss_dead":
            flow = handle_boss_defeat(player, groups, state, sfx, screen, font)
            if flow == "exit":
                running = False
                break
            continue

        # --------------------------
        # RENDER (NEW PIPELINE)
        # --------------------------
        # Draw everything to the dynamic render surface
        render_frame(render_surface, player, groups, state, debugger)

        # Blit the render surface to the actual window
        screen.blit(render_surface, (0, 0))
        pygame.display.flip()

    # ==========================
    # GAME OVER SCREEN
    # ==========================
    result = run_game_over(screen, font, state["score"])
    if result == "restart":
        main()


if __name__ == "__main__":
    main()
