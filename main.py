import pygame
import random

from settings import *
from systems.debugger import DebuggerOverlay
from systems.audio import init_sfx, play_music
from systems.level_manager import start_level

from entities.player import Player
from entities.enemy import Enemy
from entities.asteroid import Asteroid
from entities.boss import Boss, Boss2
from entities.projectiles import (
    Bullet, ShrapnelBullet, GravityBomb,
    spawn_shrapnel_explosion, spawn_gravity_explosion
)
from entities.powerups import Powerup


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
#            MAIN
# ==========================

def main():
    pygame.init()
    pygame.mixer.init()

    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Galaxyroids — Modular Edition")

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

        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 40))
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2))
        screen.blit(prompt_text, (WIDTH//2 - prompt_text.get_width()//2, HEIGHT//2 + 40))

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
            screen.blit(count_text, (WIDTH//2 - count_text.get_width()//2, HEIGHT//2))
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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        debugger.active = False
                    if event.key == pygame.K_q:
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
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Fire bullets
                if event.key in (pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT):
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
            for _ in range(5):
                e1 = Enemy((60, random.randint(100, HEIGHT - 100)), WIDTH, HEIGHT,
                           speed=current_enemy_speed, level=level)
                e2 = Enemy((WIDTH - 60, random.randint(100, HEIGHT - 100)), WIDTH, HEIGHT,
                           speed=current_enemy_speed, level=level)
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
                # --- Player hit by enemy bullets ---
                for b in boss_bullets.copy():
                    if b.rect.colliderect(player.rect):
                        boss_bullets.remove(b)
                        b.kill()
                        player.health -= HAZARD_DAMAGE
                        debugger.add_log("Player hit by enemy bullet")

                        if player.health <= 0:
                            if not handle_player_death():
                                running = False
                        break
                # --- Player hits enemies ---
                for e in enemies.copy():
                    enemy_removed = False

                    # Normal bullets
                    for b in bullets.copy():
                        if e.rect.colliderect(b.rect):
                            bullets.remove(b)
                            b.kill()
                            enemies.remove(e)
                            e.kill()
                            score += 10
                            enemy_removed = True
                            debugger.add_log("Enemy destroyed by bullet")
                            break
                    if enemy_removed:
                        continue

                    # Shrapnel grenades
                    for s in shrapnel_grenades.copy():
                        if s.exploded:
                            spawn_shrapnel_explosion(s.rect.center, all_sprites, bullets)
                            shrapnel_grenades.remove(s)
                            s.kill()
                            debugger.add_log("Shrapnel grenade exploded")
                            continue

                        if e.rect.colliderect(s.rect):
                            spawn_shrapnel_explosion(s.rect.center, all_sprites, bullets)
                            shrapnel_grenades.remove(s)
                            s.kill()
                            enemies.remove(e)
                            e.kill()
                            score += 10
                            debugger.add_log("Enemy destroyed by shrapnel")
                            enemy_removed = True
                            break
                    if enemy_removed:
                        continue

                    # Radial fragments
                    for b in bullets.copy():
                        if getattr(b, "is_bomber_fragment", False):
                            if e.rect.colliderect(b.rect):
                                bullets.remove(b)
                                b.kill()
                                enemies.remove(e)
                                e.kill()
                                score += 10
                                debugger.add_log("Enemy destroyed by fragment")
                                enemy_removed = True
                                break
                    if enemy_removed:
                        continue

                # --- Player collides with enemies ---
                for e in enemies.copy():
                    if player.rect.colliderect(e.rect):
                        enemies.remove(e)
                        e.kill()
                        player.health -= BLOB_DAMAGE
                        debugger.add_log("Player collided with enemy")

                        if player.health <= 0:
                            if not handle_player_death():
                                running = False
                        break

                # --- Player collides with asteroids (correct cooldown logic) ---
                now = pygame.time.get_ticks()

                for a in asteroids.copy():
                    if player.rect.colliderect(a.rect):
                        if now - player.last_asteroid_hit > player.asteroid_hit_cooldown:
                            player.health -= HAZARD_DAMAGE
                            player.last_asteroid_hit = now
                            debugger.add_log("Player collided with asteroid")

                            if player.health <= 0:
                                if not handle_player_death():
                                    running = False
                        break

                # --- Bullets hit asteroids ---
                for a in asteroids.copy():
                    for b in bullets.copy():
                        if a.rect.colliderect(b.rect):
                            bullets.remove(b)
                            b.kill()
                            a.health -= 1
                            debugger.add_log("Asteroid hit by bullet")

                            if a.health <= 0:
                                if a.size > 1:
                                    for _ in range(2):
                                        new_ast = Asteroid(WIDTH, HEIGHT, pos=a.pos, size=a.size - 1)
                                        asteroids.add(new_ast)
                                        all_sprites.add(new_ast)
                                asteroids.remove(a)
                                a.kill()
                            break

                # --- Shrapnel explosions hit asteroids ---
                for a in asteroids.copy():
                    for s in shrapnel_grenades.copy():
                        if s.exploded:
                            spawn_shrapnel_explosion(s.rect.center, all_sprites, bullets)
                            shrapnel_grenades.remove(s)
                            s.kill()
                            debugger.add_log("Shrapnel explosion hit asteroid")
                            break

                # --- Gravity bombs ---
                for g in gravity_bombs.copy():
                    if g.exploded:
                        spawn_gravity_explosion(g.rect.center, all_sprites, bullets)
                        gravity_bombs.remove(g)
                        g.kill()
                        debugger.add_log("Gravity bomb exploded")
                        continue

                    # Pull enemies
                    for e in enemies:
                        dist = e.pos.distance_to(g.pos)
                        if dist < 200:
                            pull = (g.pos - e.pos).normalize() * 0.4
                            e.pos += pull

                    # Pull asteroids
                    for a in asteroids:
                        dist = a.pos.distance_to(g.pos)
                        if dist < 200:
                            pull = (g.pos - a.pos).normalize() * 0.3
                            a.pos += pull

                # --- Player picks up powerups ---
                for p in powerups.copy():
                    if player.rect.colliderect(p.rect):
                        powerups.remove(p)
                        p.kill()
                        player.weapon_mode = "SPREAD"
                        player.powerup_hits = 0
                        player.update_appearance()
                        debugger.add_log("Player picked up powerup")

                # --- Boss damage ---
                if boss_spawned and len(boss_group) > 0:
                    boss = boss_group.sprites()[0]

                    # Player bullets hit boss
                    for b in bullets.copy():
                        if boss.rect.colliderect(b.rect):
                            bullets.remove(b)
                            b.kill()
                            boss.health -= BULLET_DAMAGE
                            boss.hit_flash = 5
                            debugger.add_log("Boss hit by bullet")

                            if boss.health <= 0:
                                boss.kill()
                                boss_group.remove(boss)
                                score += 500
                                debugger.add_log("Boss defeated")

                                # ------------------------------
                                #   SHOW VICTORY POPUP HERE
                                # ------------------------------
                                result = show_victory_popup(player, enemies_destroyed, level)

                                if result == "exit":
                                    running = False
                                    break

                                if result == "harder":
                                    current_enemy_speed += 0.3
                                    current_boss_speed += 0.3

                                # ------------------------------
                                #   PREPARE NEXT LEVEL
                                # ------------------------------
                                boss_spawned = False
                                level += 1

                                start_level(
                                    level, WIDTH, HEIGHT,
                                    all_sprites, enemies, asteroids,
                                    current_enemy_speed, enemies_per_side,
                                    debugger=debugger
                                )

                                level_start_time = pygame.time.get_ticks()


                            break
                    # Shrapnel hits boss
                    for s in shrapnel_grenades.copy():
                        if s.exploded:
                            spawn_shrapnel_explosion(s.rect.center, all_sprites, bullets)
                            shrapnel_grenades.remove(s)
                            s.kill()
                            boss.health -= SHRAPNEL_DAMAGE
                            boss.hit_flash = 5
                            debugger.add_log("Boss hit by shrapnel")

                            if boss.health <= 0:
                                boss.kill()
                                boss_group.remove(boss)
                                score += 500
                                debugger.add_log("Boss defeated")

                                # ------------------------------
                                #   SHOW VICTORY POPUP HERE
                                # ------------------------------
                                result = show_victory_popup(player, enemies_destroyed, level)

                                if result == "exit":
                                    running = False
                                    break

                                if result == "harder":
                                    current_enemy_speed += 0.3
                                    current_boss_speed += 0.3

                                # ------------------------------
                                #   PREPARE NEXT LEVEL
                                # ------------------------------
                                boss_spawned = False
                                level += 1

                                start_level(
                                    level, WIDTH, HEIGHT,
                                    all_sprites, enemies, asteroids,
                                    current_enemy_speed, enemies_per_side,
                                    debugger=debugger
                                )

                                level_start_time = pygame.time.get_ticks()


                            break

                    # Gravity bomb explosion hits boss
                    for g in gravity_bombs.copy():
                        if g.exploded:
                            spawn_gravity_explosion(g.rect.center, all_sprites, bullets)
                            gravity_bombs.remove(g)
                            g.kill()
                            boss.health -= SHRAPNEL_DAMAGE
                            boss.hit_flash = 5
                            debugger.add_log("Boss hit by gravity explosion")

                            if boss.health <= 0:
                                boss.kill()
                                boss_group.remove(boss)
                                score += 500
                                debugger.add_log("Boss defeated")

                                # ------------------------------
                                #   SHOW VICTORY POPUP HERE
                                # ------------------------------
                                result = show_victory_popup(player, enemies_destroyed, level)

                                if result == "exit":
                                    running = False
                                    break

                                if result == "harder":
                                    current_enemy_speed += 0.3
                                    current_boss_speed += 0.3

                                # ------------------------------
                                #   PREPARE NEXT LEVEL
                                # ------------------------------
                                boss_spawned = False
                                level += 1

                                start_level(
                                    level, WIDTH, HEIGHT,
                                    all_sprites, enemies, asteroids,
                                    current_enemy_speed, enemies_per_side,
                                    debugger=debugger
                                )

                                level_start_time = pygame.time.get_ticks()


                            break

                    # Boss laser hits player
                    if boss.laser_active_timer > 0:
                        laser_rect = pygame.Rect(
                            boss.rect.centerx - 40,
                            boss.rect.bottom,
                            80,
                            HEIGHT
                        )
                        if laser_rect.colliderect(player.rect):
                            player.health -= BOSS_DAMAGE
                            debugger.add_log("Player hit by boss laser")

                            if player.health <= 0:
                                if not handle_player_death():
                                    running = False

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

        # --- HUD TEXT (left‑aligned under bars) ---
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

        screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 60))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        screen.blit(prompt_text, (WIDTH//2 - prompt_text.get_width()//2, HEIGHT//2 + 40))

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
