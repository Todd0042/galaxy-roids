import pygame
import random

from settings import *
from systems.debugger import DebuggerOverlay
from systems.audio import init_sfx, play_music
from systems.level_manager import start_level

from entities.player import Player
from entities.asteroid import Asteroid
from entities.boss import Boss, Boss2
from entities.projectiles import (
    Bullet, ShrapnelBullet, GravityBomb,
    spawn_shrapnel_explosion, spawn_gravity_explosion
)
from entities.powerups import Powerup

# NEW modular enemy system
from enemies.regular_enemy import RegularEnemy
from enemies.blob_enemy import BlobEnemy
from enemies.bomber_enemy import BomberEnemy
from enemies.stinger_enemy import StingerEnemy

# COLLISIONS
from collisions.collision_player_enemy import handle_player_hits_enemies
from collisions.collision_enemy_player import handle_enemies_hit_player
from collisions.collision_misc import handle_misc_collisions
from collisions.collision_boss import handle_boss_collisions
from collisions.boss_death_handler import handle_boss_death



# ==========================
#        HUD FUNCTIONS
# ==========================

def draw_player_health_bar(screen, player):
    bar_width = 200
    bar_height = 18
    x = 20
    y = 20

    ratio = max(player.health / player.max_health, 0)

    pygame.draw.rect(screen, (60, 60, 60), (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, (60, 200, 60),
                     (x, y, int(bar_width * ratio), bar_height))
    pygame.draw.rect(screen, (255, 255, 255),
                     (x, y, bar_width, bar_height), 2)


def draw_shrapnel_cooldown(screen, player):
    bar_width = 200
    bar_height = 12
    x = 20
    y = 50

    ratio = min(player.shrapnel_cooldown / SHRAPNEL_COOLDOWN_MAX, 1)

    pygame.draw.rect(screen, (60, 60, 60), (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, (200, 200, 40),
                     (x, y, int(bar_width * ratio), bar_height))
    pygame.draw.rect(screen, (255, 255, 255),
                     (x, y, bar_width, bar_height), 2)


def draw_boss_health_bar(screen, boss, WIDTH):
    if boss is None:
        return

    bar_width = 220
    bar_height = 20
    x = WIDTH - bar_width - 20
    y = 20

    ratio = max(boss.health / boss.max_health, 0)

    pygame.draw.rect(screen, (60, 60, 60), (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, (255, 60, 60),
                     (x, y, int(bar_width * ratio), bar_height))
    pygame.draw.rect(screen, (255, 255, 255),
                     (x, y, bar_width, bar_height), 2)


# ==========================
#        POPUP SYSTEM
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
    WIDTH, HEIGHT = screen.get_size()

    selected = 0
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
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
        y += 40
        for i, (label, _) in enumerate(options):
            color = (255, 255, 255) if i == selected else (150, 150, 150)
            opt_surf = font.render(label, True, color)
            screen.blit(opt_surf, (WIDTH // 2 - opt_surf.get_width() // 2, y))
            y += 50

        pygame.display.flip()

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


# ==========================
#            MAIN
# ==========================

def main():
    pygame.init()
    pygame.mixer.init()

    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Galaxyroids — Modular Edition")
    enemies_destroyed = 0

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    debugger = DebuggerOverlay(font)
    sfx = init_sfx()

    # Sprite groups
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    shrapnel_grenades = pygame.sprite.Group()
    boss_group = pygame.sprite.Group()
    boss_bullets = pygame.sprite.Group()
    gravity_bombs = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    trail_group = pygame.sprite.Group()

    # Player
    player = Player(WIDTH, HEIGHT)
    all_sprites.add(player)

    # Joysticks
    joysticks = []
    for i in range(pygame.joystick.get_count()):
        joy = pygame.joystick.Joystick(i)
        joy.init()
        joysticks.append(joy)

    # Game state
    lives = INITIAL_LIVES
    score = 0
    level = 1
    game_active = False

    enemies_per_side = 6
    current_enemy_speed = ENEMY_SPEED
    current_boss_speed = BOSS_SPEED_BASE

    last_pew_time = 0
    last_periodic_spawn = 0
    boss_spawned = False
    level_start_time = pygame.time.get_ticks()

    # ==========================
    #       LEVEL SELECT
    # ==========================
    waiting_for_start = True
    selected_start_level = 1

    while waiting_for_start:
        screen.fill(BLACK)

        title_text = font.render("Choose Starting Level", True, WHITE)
        level_text = font.render(f"Level: {selected_start_level}", True, CYAN)
        prompt_text = font.render("LEFT/RIGHT to change — ENTER to start", True, GOLDEN_YELLOW)

        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 40))
        screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2))
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 40))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    selected_start_level = max(1, selected_start_level - 1)
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    selected_start_level += 1
                if event.key == pygame.K_RETURN:
                    waiting_for_start = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

    # ==========================
    #       COUNTDOWN
    # ==========================
    for i in range(3, 0, -1):
        start_ticks = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_ticks < 1000:
            screen.fill(BLACK)
            count_text = font.render(str(i), True, GOLDEN_YELLOW)
            screen.blit(count_text, (WIDTH // 2 - count_text.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

    game_active = True
    level = selected_start_level

    start_level(
        level, WIDTH, HEIGHT,
        all_sprites, enemies, asteroids,
        current_enemy_speed, enemies_per_side,
        debugger=debugger
    )
    level_start_time = pygame.time.get_ticks()

    # ==========================
    #         MAIN LOOP
    # ==========================
    running = True
    while running:
        clock.tick(FPS)

        # Debugger freeze mode
        if debugger.active:
            debugger.record_fps(clock.get_fps())
            debugger.draw(screen, WIDTH, HEIGHT)
            pygame.display.flip()

            for event in pygame.event.get():

                # NEW: let debugger handle mouse selection + Ctrl+C
                debugger.handle_event(event)

                # Resume / Quit still work the same
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        debugger.active = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        return

            continue



        # ==========================
        #       EVENT HANDLING
        # ==========================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # Pause
                if event.key == pygame.K_ESCAPE:
                    result = show_pause_popup()
                    if result == "exit":
                        running = False

                # --- FIRE BUTTON PRESS ---
                if event.key in (pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT):
                    player.fire_button_held = True

                # --- FIRE BUTTON RELEASE ---
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT):
                        player.fire_button_held = False

                # --- SPECIAL GRENADE (Enter + Caps Lock) ---
                if event.key in (pygame.K_RETURN, pygame.K_CAPSLOCK):
                    if player.shrapnel_cooldown == 0:
                        s = ShrapnelBullet(player.pos, player.angle, WIDTH, HEIGHT)
                        shrapnel_grenades.add(s)
                        all_sprites.add(s)
                        player.shrapnel_cooldown = SHRAPNEL_COOLDOWN_MAX



                # Shrapnel grenade
                if event.key in (pygame.K_CAPSLOCK, pygame.K_RETURN):
                    if player.shrapnel_cooldown == 0:
                        s = ShrapnelBullet(player.pos, player.angle, WIDTH, HEIGHT)
                        shrapnel_grenades.add(s)
                        all_sprites.add(s)
                        player.shrapnel_cooldown = SHRAPNEL_COOLDOWN_MAX

        # ==========================
        #     RANDOM POWERUPS
        # ==========================
        if game_active and random.random() < POWERUP_SPAWN_CHANCE:
            p = Powerup(WIDTH, HEIGHT)
            powerups.add(p)
            all_sprites.add(p)

        # ==========================
        #       BOSS SPAWN
        # ==========================
        ticks = pygame.time.get_ticks()
        if game_active and not boss_spawned and ticks - level_start_time > BOSS_SPAWN_TIME:
            if 4 <= level <= 6:
                boss = Boss2(WIDTH, HEIGHT, level, speed=current_boss_speed)
            else:
                boss = Boss(WIDTH, HEIGHT, level, speed=current_boss_speed)

            boss_group.add(boss)
            all_sprites.add(boss)
            boss_spawned = True

            play_music(f"boss{((level - 1) % 5) + 1}.midi")

        # ==========================
        #   PERIODIC ENEMY WAVES
        # ==========================
        if game_active and not boss_spawned and ticks - last_periodic_spawn > 5000:

            # Build enemy pool based on level
            enemy_pool = []

            if level >= 1:
                enemy_pool.append(RegularEnemy)

            if level >= 4:
                enemy_pool.append(BlobEnemy)

            if level >= 7:
                enemy_pool.append(BomberEnemy)

            if level >= 10:
                enemy_pool.append(StingerEnemy)

            # Spawn 5 pairs (left + right)
            for _ in range(5):
                EnemyClass = random.choice(enemy_pool)

                e1 = EnemyClass(
                    pos=(60, random.randint(100, HEIGHT - 100)),
                    width=WIDTH,
                    height=HEIGHT,
                    speed=current_enemy_speed,
                    level=level
                )

                e2 = EnemyClass(
                    pos=(WIDTH - 60, random.randint(100, HEIGHT - 100)),
                    width=WIDTH,
                    height=HEIGHT,
                    speed=current_enemy_speed,
                    level=level
                )

                enemies.add(e1, e2)
                all_sprites.add(e1, e2)

            last_periodic_spawn = ticks


        # ==========================
        #   PERIODIC ASTEROID RESPAWN
        # ==========================
        if game_active and ticks % 7000 < 20:
            for _ in range(3):
                a = Asteroid(WIDTH, HEIGHT)
                asteroids.add(a)
                all_sprites.add(a)

        # ==========================
        #   UPDATE + COLLISIONS
        # ==========================
        if game_active:

            # --------------------------
            #       UPDATE SPRITES
            # --------------------------
            try:
                for sprite in all_sprites:
                    debugger.last_sprite = sprite.__class__.__name__
                    sprite.update(
                        player_pos=player.pos,
                        joysticks=joysticks,
                        trail_group=trail_group,
                        boss_bullets=boss_bullets,
                        all_sprites=all_sprites
                    )
                    debugger.add_log(f"Updated: {sprite.__class__.__name__}")

                trail_group.update()

            except Exception as e:
                debugger.capture_exception(e, debugger.last_sprite)
                continue
            # ==========================
            #        AUTO-FIRE
            # ==========================
            if player.fire_button_held or player.powerup_hits >= 2:
                if player.fire_cooldown == 0:
                    now = pygame.time.get_ticks()
                    if sfx["pew"] and now - last_pew_time > 150:
                        sfx["pew"].play()
                        last_pew_time = now

                    if player.weapon_mode == "SPREAD":
                        for offset in (-15, 0, 15):
                            b = Bullet(player.pos, player.angle + offset, WIDTH, HEIGHT)
                            bullets.add(b)
                            all_sprites.add(b)
                    else:
                        b = Bullet(player.pos, player.angle, WIDTH, HEIGHT)
                        bullets.add(b)
                        all_sprites.add(b)

                    player.fire_cooldown = 10  # adjust fire rate


            # --------------------------
            #     PLAYER DEATH HANDLER
            # --------------------------
            def handle_player_death():
                nonlocal lives, player

                lives -= 1

                if lives <= 0:
                    return False

                player.health = PLAYER_MAX_HEALTH
                player.pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
                player.vel = pygame.Vector2(0, 0)
                player.rect.center = player.pos
                player.invulnerable_timer = 120

                return True


            # --------------------------
            #         COLLISIONS
            # --------------------------
            try:
                # 1. Player bullets → enemies
                score = handle_player_hits_enemies(
                    player,
                    enemies,
                    bullets,
                    shrapnel_grenades,
                    all_sprites,
                    debugger,
                    score,
                    spawn_shrapnel_explosion
                )

                # 2. Enemies → player (enemy bullets, contact, blobs, bombers, asteroids)
                player.health = handle_enemies_hit_player(
                    player,
                    enemies,
                    boss_bullets,
                    asteroids,
                    debugger,
                    pygame.time.get_ticks()
                )

                # If player died from any of the above:
                if player.health <= 0:
                    if not handle_player_death():
                        running = False

                # 3. Misc collisions (asteroids, powerups, grenade triggers, gravity bombs)
                handle_misc_collisions(
                    player,
                    bullets,
                    asteroids,
                    powerups,
                    all_sprites,
                    debugger,
                    spawn_shrapnel_explosion,
                    shrapnel_grenades
                )

                # 4. Boss collisions (bullets, shrapnel, gravity bombs, laser)
                boss = handle_boss_collisions(
                    player,
                    bullets,
                    shrapnel_grenades,
                    gravity_bombs,
                    boss_group,
                    all_sprites,
                    debugger,
                    spawn_shrapnel_explosion,
                    spawn_gravity_explosion
                )

                # 5. Boss death handler (NO level transitions here)
                result = handle_boss_death(boss_group, score, debugger)

                if result is not None:
                    status, score = result

                    if status == "dead":
                        # The boss is dead — now YOU handle:
                        # - victory popup
                        # - difficulty scaling
                        # - next level
                        # - start_level()
                        # - resetting timers

                        result = show_victory_popup(score, level)

                        if result == "exit":
                            running = False

                        elif result == "harder":
                            current_enemy_speed += 0.3
                            current_boss_speed += 0.3

                        # Next level
                        boss_spawned = False
                        level += 1

                        start_level(
                            level, WIDTH, HEIGHT,
                            all_sprites, enemies, asteroids,
                            current_enemy_speed, enemies_per_side,
                            debugger=debugger
                        )

                        level_start_time = pygame.time.get_ticks()

            except Exception as e:
                debugger.capture_exception(e, "CollisionHandler")
                continue

        # ==========================
        #       DRAW FRAME
        # ==========================
        screen.fill(BLACK)

        # Trails first (behind everything)
        trail_group.draw(screen)

        # All sprites
        all_sprites.draw(screen)

        # --- HUD BARS ---
        draw_player_health_bar(screen, player)
        draw_shrapnel_cooldown(screen, player)

        if boss_spawned:
            draw_boss_health_bar(screen, boss, WIDTH)

        # --- HUD TEXT ---
        lives_text = font.render(f"LIVES: {lives}", True, WHITE)
        level_text = font.render(f"LEVEL: {level}", True, WHITE)
        score_text = font.render(f"SCORE: {score}", True, WHITE)

        screen.blit(lives_text, (20, 80))
        screen.blit(level_text, (20, 110))
        screen.blit(score_text, (20, 140))

        pygame.display.flip()

    # ==========================
    #        GAME OVER
    # ==========================
    game_over = True
    while game_over:
        screen.fill(BLACK)

        over_text = font.render("GAME OVER", True, RED)
        score_text = font.render(f"Final Score: {score}", True, WHITE)
        prompt_text = font.render("Press R to Restart or Q to Quit", True, CYAN)

        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 60))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 40))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    game_over = False

                if event.key == pygame.K_r:
                    main()
                    return

    pygame.quit()


if __name__ == "__main__":
    main()
