from .game_init import initialize_game
from .debug_freeze import debugger_freeze_loop
from .input_handler import handle_gameplay_input
from .spawner import (
    spawn_random_powerups,
    spawn_boss_if_ready,
    spawn_periodic_enemy_waves,
    spawn_periodic_asteroids
)
from .updater import update_all_sprites
from .combat import handle_autofire
from .collision_manager import process_collisions
from .level_flow import handle_boss_defeat
from .renderer import render_frame
from .player_state import handle_player_death

__all__ = [
    "initialize_game",
    "debugger_freeze_loop",
    "handle_gameplay_input",
    "spawn_random_powerups",
    "spawn_boss_if_ready",
    "spawn_periodic_enemy_waves",
    "spawn_periodic_asteroids",
    "update_all_sprites",
    "handle_autofire",
    "process_collisions",
    "handle_boss_defeat",
    "render_frame",
    "handle_player_death",
]
