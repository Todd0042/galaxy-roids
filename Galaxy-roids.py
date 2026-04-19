import pygame
import math
import random

# --- Configuration (Tinker with these!) ---
FPS = 60
INITIAL_LIVES = 1
DEBUG_MODE = True  # Toggle this to show/hide debug info
DIFFICULTY_MULTIPLIER = 0.3

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
GOLDEN_YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)

# Player Physics & Combat
PLAYER_ROT_SPEED = 5
PLAYER_THRUST = 0.2
PLAYER_FRICTION = 0.98
PLAYER_REVERSE_THRUST = 0.03
PLAYER_BRAKE_FRICTION = 0.95
PLAYER_MAX_HEALTH = 100
HAZARD_DAMAGE = 50
BLOB_DAMAGE = 10
BOMBER_DAMAGE = 3
BLOB_STUN_TIME = 30  # 0.5 seconds at 60 FPS
PLAYER_FIRE_RATE = 10
BULLET_DAMAGE = 1
SHRAPNEL_DAMAGE = 10
ENEMY_HEALTH = 1
ASTEROID_HEALTH_LARGE = 3
ASTEROID_HEALTH_MEDIUM = 2
ASTEROID_HEALTH_SMALL = 1
PLAYER_COLLISION_DAMAGE = 10
SHRAPNEL_COOLDOWN_MAX = 120  # 2 seconds at 60 FPS
SPREAD_HITS_REVERT = 1
ENEMY_WAVE_DELAY = 10  # Seconds before the second wave spawns
BOSS_SPAWN_TIME = 75000  # 15 seconds in milliseconds
BOSS_HEALTH_BASE = 40 * DIFFICULTY_MULTIPLIER
BOSS_LASER_COOLDOWN = 600 # 10 seconds at 60 FPS
BOSS_LASER_DURATION = 180 # 3 seconds
BOSS_LASER_WARNING = 90  # 1.5 seconds of warning
BOSS_SPEED_BASE = 0.8 * DIFFICULTY_MULTIPLIER  # Much slower starting speed for the Planet Breaker
BOSS_SPEED_SCALE = 1.15 # 15% speed increase per level

# Projectiles & Hazards
BULLET_SPEED = 10
BULLET_LIFESPAN = 60
ENEMY_SPEED = 2 * DIFFICULTY_MULTIPLIER
ENEMY_DIVE_CHANCE = 0.04 * DIFFICULTY_MULTIPLIER
ASTEROID_START_COUNT = int(6 * DIFFICULTY_MULTIPLIER)
ASTEROID_SPEED_RANGE = (-1.5, 1.5)
POWERUP_SPAWN_CHANCE = 0.005

# Entity Sizes
PLAYER_SIZE = 30
ENEMY_SIZE = 25

class Player(pygame.sprite.Sprite):
    def __init__(self, screen_w, screen_h):
        super().__init__()
        self.original_image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        self.color = CYAN
        pygame.draw.polygon(self.original_image, self.color, [(PLAYER_SIZE, PLAYER_SIZE//2), (0, 0), (5, PLAYER_SIZE//2), (0, PLAYER_SIZE)])
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(screen_w // 2, screen_h // 2))
        
        # Physics
        self.screen_w, self.screen_h = screen_w, screen_h
        self.spawn_pos = pygame.Vector2(screen_w // 2, screen_h // 2)
        self.pos = pygame.Vector2(self.spawn_pos)
        self.vel = pygame.Vector2(0, 0)
        self.direction = pygame.Vector2(1, 0)
        self.angle = 0
        self.rotation_speed = PLAYER_ROT_SPEED
        self.thrust = PLAYER_THRUST
        self.friction = PLAYER_FRICTION
        
        # Combat State
        self.shrapnel_cooldown = 0
        self.weapon_mode = "NORMAL" # NORMAL or SPREAD
        self.powerup_hits = 0
        self.invulnerable_timer = 0
        self.health = PLAYER_MAX_HEALTH
        self.stun_timer = 0

    def update_appearance(self):
        self.color = GOLDEN_YELLOW if self.weapon_mode == "SPREAD" else CYAN
        self.original_image.fill((0, 0, 0, 0))
        pygame.draw.polygon(self.original_image, self.color, [(PLAYER_SIZE, PLAYER_SIZE//2), (0, 0), (5, PLAYER_SIZE//2), (0, PLAYER_SIZE)])
        self.rotate(0) # Refresh image rotation with new color

    def rotate(self, angle_change):
        self.angle += angle_change
        self.direction = pygame.Vector2(1, 0).rotate(self.angle)
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, **kwargs):
        # Handle Invulnerability Flashing
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

        keys = pygame.key.get_pressed()
        joysticks = kwargs.get('joysticks', [])
        trail_group = kwargs.get('trail_group')
        is_thrusting = False

        # Handle Stun/Capture
        if self.stun_timer > 0:
            self.stun_timer -= 1
            self.vel = pygame.Vector2(0, 0) # Completely stop movement while stunned
        else:
            # Joystick Axis Control
            for joy in joysticks:
                if joy.get_axis(0) < -0.3: # Left
                    self.rotate(-self.rotation_speed)
                elif joy.get_axis(0) > 0.3: # Right
                    self.rotate(self.rotation_speed)
                if joy.get_axis(1) < -0.3: # Up (negative axis)
                    self.vel += self.direction * self.thrust
                    is_thrusting = True
                if joy.get_axis(1) > 0.3: # Down
                    self.vel *= PLAYER_BRAKE_FRICTION
                    self.vel -= self.direction * PLAYER_REVERSE_THRUST

            # WASD & Arrow Compatibility
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.rotate(-self.rotation_speed)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.rotate(self.rotation_speed)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.vel += self.direction * self.thrust
                is_thrusting = True
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.vel *= PLAYER_BRAKE_FRICTION
                self.vel -= self.direction * PLAYER_REVERSE_THRUST

        # Spawn Jet Trails
        if is_thrusting and trail_group is not None:
            # Create twin streaks from the engine ports
            for side in [-1, 1]:
                # Offset slightly to the rear and sides of the ship center
                offset = self.direction.rotate(90 * side) * 8 - self.direction * 10
                trail_pos = self.pos + offset
                # Add slight random jitter for a "smoke/vapor" effect
                trail_pos += pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                trail_group.add(TrailSegment(trail_pos))

        # Apply friction and move
        self.vel *= self.friction
        self.pos += self.vel
        
        self.pos.x %= self.screen_w
        self.pos.y %= self.screen_h
        self.rect.center = self.pos
        
        # Visual feedback for invulnerability
        if self.stun_timer > 0:
            self.image.set_alpha(150) # Dim when captured
        elif self.invulnerable_timer % 10 > 5:
            self.image.set_alpha(0)
        else:
            self.image.set_alpha(255)

        if self.shrapnel_cooldown > 0:
            self.shrapnel_cooldown -= 1

class TrailSegment(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        # Using a soft white/cyan for that "condensed vapor" look
        pygame.draw.circle(self.image, (220, 240, 255), (2, 2), 2)
        self.rect = self.image.get_rect(center=pos)
        self.alpha = 180

    def update(self, **kwargs):
        self.alpha -= 6 # Fade out over 30 frames
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle, screen_w, screen_h, color=YELLOW, size=4):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.vel = pygame.Vector2(BULLET_SPEED, 0).rotate(angle)
        self.screen_w, self.screen_h = screen_w, screen_h

    def update(self, **kwargs):
        self.rect.center += self.vel
        # Kill when hitting the edge of the screen
        if not (0 <= self.rect.centerx <= self.screen_w and 0 <= self.rect.centery <= self.screen_h):
            self.kill()

class ShrapnelBullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle, screen_w, screen_h):
        super().__init__()
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(self.image, ORANGE, (12, 12), 12)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(BULLET_SPEED * 0.7, 0).rotate(angle)
        self.screen_w, self.screen_h = screen_w, screen_h
        self.timer = 240 # Dissipate after 4 seconds to prevent orbital leak
        self.exploded = False

    def update(self, **kwargs):
        self.pos += self.vel
        self.pos.x %= self.screen_w
        self.pos.y %= self.screen_h
        self.rect.center = self.pos
        self.timer -= 1
        if self.timer <= 0:
            self.exploded = True

class Powerup(pygame.sprite.Sprite):
    def __init__(self, screen_w, screen_h):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GOLDEN_YELLOW, (10, 10), 8)
        pygame.draw.circle(self.image, WHITE, (10, 10), 10, 2)
        self.pos = pygame.Vector2(random.randint(50, screen_w-50), random.randint(50, screen_h-50))
        self.rect = self.image.get_rect(center=self.pos)
        self.vel = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.screen_w, self.screen_h = screen_w, screen_h

    def update(self, **kwargs):
        self.pos += self.vel
        # Wrap powerups so they stay in play until collected
        self.pos.x %= self.screen_w
        self.pos.y %= self.screen_h
        self.rect.center = self.pos

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, screen_w, screen_h, pos=None, size=3):
        super().__init__()
        self.screen_w, self.screen_h = screen_w, screen_h
        self.size = size
        radius = self.size * 15
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        # Health based on size
        if size == 3: self.health = ASTEROID_HEALTH_LARGE
        elif size == 2: self.health = ASTEROID_HEALTH_MEDIUM
        else: self.health = ASTEROID_HEALTH_SMALL
        # Drawing a rough jagged circle/polygon would be better, but a circle works for the prototype
        pygame.draw.circle(self.image, WHITE, (radius, radius), radius, 2)
        self.rect = self.image.get_rect()
        
        if pos:
            self.pos = pygame.Vector2(pos)
        else:
            self.pos = pygame.Vector2(random.randint(0, screen_w), random.randint(0, screen_h))
            
        self.rect.center = self.pos
        v_min, v_max = ASTEROID_SPEED_RANGE
        self.vel = pygame.Vector2(random.uniform(v_min, v_max), random.uniform(v_min, v_max))

    def update(self, **kwargs):
        player_pos = kwargs.get('player_pos')
        boss_bullets = kwargs.get('boss_bullets')
        all_sprites_group = kwargs.get('all_sprites')

        self.pos += self.vel
        # Asteroid screen wrap
        self.pos.x %= self.screen_w
        self.pos.y %= self.screen_h
        self.rect.center = self.pos

        # Mortar Turret Logic (Every 3rd Level)
        if self.has_turret and player_pos and boss_bullets:
            if self.fire_cooldown > 0:
                self.fire_cooldown -= 1
            else:
                angle = (player_pos - self.pos).angle_to(pygame.Vector2(1, 0))
                m = Bullet(self.rect.center, -angle, self.screen_w, self.screen_h, color=RED, size=8)
                m.vel *= 0.4 
                boss_bullets.add(m)
                if all_sprites_group: all_sprites_group.add(m)
                self.fire_cooldown = 180

class Enemy(pygame.sprite.Sprite):
    def __init__(self, slot_pos, screen_w, screen_h, speed=ENEMY_SPEED, level=1):
        super().__init__()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, RED, [(12, 0), (25, 25), (12, 18), (0, 25)])
        self.rect = self.image.get_rect()
        
        self.slot_pos = pygame.Vector2(slot_pos)
        self.pos = pygame.Vector2(slot_pos)
        self.state = "FORMATION" # FORMATION or DIVING
        self.vel = pygame.Vector2(0, 0)
        self.speed = speed
        self.health = ENEMY_HEALTH
        
        # Dive type selection logic: Weights favor newer elite types as levels increase
        if level >= 7:
            self.dive_type = random.choices(["NORMAL", "SQUIGGLE", "BLOB", "BOMBER"], weights=[0.2, 0.2, 0.2, 0.4])[0]
        elif level >= 3:
            self.dive_type = random.choices(["NORMAL", "SQUIGGLE", "BLOB"], weights=[0.3, 0.3, 0.4])[0]
        else:
            self.dive_type = random.choices(["NORMAL", "SQUIGGLE"], weights=[0.7, 0.3])[0]
        
        self.target_pos = None
        self.reached_target = False

        if self.dive_type == "BLOB":
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (150, 0, 255), (15, 15), 12) # Purple blob
            pygame.draw.circle(self.image, WHITE, (10, 10), 3) # Eye 1
            pygame.draw.circle(self.image, WHITE, (20, 10), 3) # Eye 2
            self.rect = self.image.get_rect()

        if self.dive_type == "BOMBER":
            self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, ORANGE, [(12, 0), (25, 25), (12, 18), (0, 25)])

        self.dive_timer = 0

    def update(self, **kwargs):
        player_pos = kwargs.get('player_pos')
        boss_bullets = kwargs.get('boss_bullets')
        ticks = pygame.time.get_ticks()
        
        if self.state == "FORMATION":
            # Set Pattern: Synchronized side-to-side and vertical oscillation
            pattern_x = math.sin(ticks * 0.002) * 30
            pattern_y = math.cos(ticks * 0.003) * 15
            target = self.slot_pos + pygame.Vector2(pattern_x, pattern_y)
            self.pos += (target - self.pos) * 0.1
        
        elif self.state == "DIVING":
            if player_pos is None: return
            self.dive_timer += 1
            
            # Calculate base vector to player
            to_player = (player_pos - self.pos)
            
            # Priority 1: High-Speed Bomber (Commits to its vector at 3x speed)
            if self.dive_type == "BOMBER":
                if self.target_pos is None:
                    self.target_pos = pygame.Vector2(player_pos)
                    diff = self.target_pos - self.pos
                    if diff.length() > 0:
                        self.vel = diff.normalize() * (self.speed * 3)
                    else:
                        self.vel = pygame.Vector2(0,0)
                
                self.pos += self.vel
                if self.pos.distance_to(self.target_pos) < 15:
                    self.reached_target = True
            
            # Priority 2: Standard homing/special movement
            elif to_player.length() > 0:
                direction = to_player.normalize()
                
                if self.dive_type == "SQUIGGLE" and self.dive_timer < 120:
                    # Squiggle phase: add a perpendicular sine wave to the path
                    perp_vec = pygame.Vector2(-direction.y, direction.x)
                    wave = math.sin(self.dive_timer * 0.15) * 6
                    self.pos += (direction * self.speed) + (perp_vec * wave)
                else:
                    # Heat seek phase for NORMAL and SQUIGGLE (after squiggle phase)
                    self.pos += direction * self.speed
                
                # Level 10+ Shooting Logic
                if self.level >= 10 and boss_bullets is not None:
                    if self.fire_cooldown > 0:
                        self.fire_cooldown -= 1
                    else:
                        angle = to_player.angle_to(pygame.Vector2(1, 0))
                        eb = Bullet(self.rect.center, -angle, self.screen_w, self.screen_h, color=RED, size=6)
                        boss_bullets.add(eb)
                        kwargs.get('all_sprites').add(eb)
                        self.fire_cooldown = random.randint(120, 240)
            

            # Reset if it goes off screen (any side)
            if self.pos.y > self.screen_h + 100 or self.pos.y < -150 or \
               self.pos.x > self.screen_w + 150 or self.pos.x < -150:
                self.pos = pygame.Vector2(self.slot_pos)
                self.state = "FORMATION"
                self.dive_timer = 0

        self.rect.center = self.pos

class Boss(pygame.sprite.Sprite):
    def __init__(self, screen_w, screen_h, level, speed=BOSS_SPEED_BASE):
        super().__init__()
        self.screen_w, self.screen_h = screen_w, screen_h
        self.max_health = BOSS_HEALTH_BASE * (1.5 ** (level - 1))
        self.health = self.max_health
        self.speed = speed
        self.image = pygame.Surface((150, 80), pygame.SRCALPHA)
        # Design: A heavy armored carrier
        pygame.draw.rect(self.image, RED, (0, 0, 150, 50), border_radius=15)
        pygame.draw.rect(self.image, WHITE, (20, 50, 30, 30)) # Left Cannon
        pygame.draw.rect(self.image, WHITE, (100, 50, 30, 30)) # Right Cannon
        self.rect = self.image.get_rect()
        self.pos = pygame.Vector2(screen_w // 2, -100) # Start off-screen
        self.target_y = 120
        self.fire_cooldown = 0
        # Scale fire rate with level (shorter cooldown = faster firing)
        self.fire_rate_max = max(15, 45 - (level * 2))
        self.laser_cooldown = 300 # First laser after 5 seconds
        self.laser_warning_timer = 0
        self.laser_active_timer = 0
        self.hit_flash = 0

    def update(self, **kwargs):
        if self.hit_flash > 0:
            self.hit_flash -= 1

        ticks = pygame.time.get_ticks()
        # Entry movement then sway pattern
        if self.pos.y < self.target_y:
            self.pos.y += self.speed
        else:
            # Sway frequency scales with speed
            sway_freq = 0.001 * (self.speed / BOSS_SPEED_BASE)
            self.pos.x = self.screen_w // 2 + math.sin(ticks * sway_freq) * (self.screen_w // 4)
            
            # Laser Logic
            if self.laser_active_timer > 0:
                self.laser_active_timer -= 1
            elif self.laser_warning_timer > 0:
                self.laser_warning_timer -= 1
                if self.laser_warning_timer == 0:
                    self.laser_active_timer = BOSS_LASER_DURATION
            elif self.laser_cooldown > 0:
                self.laser_cooldown -= 1
            else:
                self.laser_warning_timer = BOSS_LASER_WARNING
                self.laser_cooldown = BOSS_LASER_COOLDOWN
                
        self.rect.center = self.pos
        if self.fire_cooldown > 0: self.fire_cooldown -= 1

class Boss2(pygame.sprite.Sprite):
    def __init__(self, screen_w, screen_h, level, speed=BOSS_SPEED_BASE):
        super().__init__()
        self.screen_w, self.screen_h = screen_w, screen_h
        # Scaling health similarly but adjusted for Boss 2
        self.max_health = (BOSS_HEALTH_BASE * (1.5 ** 2)) * (1.02 ** (level - 3))
        self.health = self.max_health
        self.speed = speed * 1.2  # Boss 2 is naturally faster
        self.image = pygame.Surface((180, 100), pygame.SRCALPHA)
        # Design: A purple heavy interceptor
        pygame.draw.rect(self.image, (150, 0, 255), (0, 0, 180, 60), border_radius=20)
        pygame.draw.rect(self.image, WHITE, (40, 60, 20, 40)) 
        pygame.draw.rect(self.image, WHITE, (80, 60, 20, 40))
        pygame.draw.rect(self.image, WHITE, (120, 60, 20, 40))
        self.rect = self.image.get_rect()
        self.pos = pygame.Vector2(screen_w // 2, -100)
        self.target_y = 150
        self.fire_cooldown = 0
        self.fire_rate_max = max(10, 30 - (level))
        self.laser_cooldown = 400 
        self.laser_warning_timer = 0
        self.laser_active_timer = 0
        self.bomb_cooldown = 180
        self.hit_flash = 0

    def update(self, **kwargs):
        if self.hit_flash > 0:
            self.hit_flash -= 1

        ticks = pygame.time.get_ticks()
        if self.pos.y < self.target_y:
            self.pos.y += self.speed
        else:
            # Figure-eight movement pattern
            self.pos.x = self.screen_w // 2 + math.sin(ticks * 0.0015) * (self.screen_w // 3)
            self.pos.y = self.target_y + math.cos(ticks * 0.003) * 50
            
            # Laser Logic for Boss 2
            if self.laser_active_timer > 0:
                self.laser_active_timer -= 1
            elif self.laser_warning_timer > 0:
                self.laser_warning_timer -= 1
                if self.laser_warning_timer == 0:
                    self.laser_active_timer = 180 # 3 seconds
            elif self.laser_cooldown > 0:
                self.laser_cooldown -= 1
            else:
                self.laser_warning_timer = 90 # 1.5s warning
                self.laser_cooldown = 400

        self.rect.center = self.pos
        if self.fire_cooldown > 0: self.fire_cooldown -= 1

class GravityBomb(pygame.sprite.Sprite):
    def __init__(self, pos, angle, screen_w, screen_h, target_dist):
        super().__init__()
        self.screen_w, self.screen_h = screen_w, screen_h
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(4, 0).rotate(angle)
        self.target_dist = target_dist
        self.dist_traveled = 0
        self.exploded = False

    def update(self, **kwargs):
        self.pos += self.vel
        self.dist_traveled += self.vel.length()
        self.rect.center = self.pos
        
        # Menacing pulse effect
        ticks = pygame.time.get_ticks()
        pulse = (math.sin(ticks * 0.01) + 1) * 4
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, (100, 0, 150), (20, 20), 14 + pulse, 3) # Outer Glow
        pygame.draw.circle(self.image, (30, 0, 50), (20, 20), 10) # Dark Core

        if self.dist_traveled >= self.target_dist:
            self.exploded = True
        
        if not (0 <= self.pos.x <= self.screen_w and 0 <= self.pos.y <= self.screen_h):
            self.kill()

def main():
    pygame.init()
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    
    global DEBUG_MODE
    # 1. Fullscreen Setup
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("Galaxy-roids")
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    # --- Audio Setup ---
    pygame.mixer.init()
    def load_sfx(filename):
        try:
            return pygame.mixer.Sound(filename)
        except (pygame.error, FileNotFoundError):
            return None

    sfx = {
        "pew": load_sfx("pew.wav"),
        "boom": load_sfx("boom.wav"),
        "poof": load_sfx("poof.wav"),
        "splat": load_sfx("splat.wav"),
        "tada": load_sfx("tada.wav")
    }

    def play_music(filename):
        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play(-1)
        except (pygame.error, FileNotFoundError):
            pass

    last_pew_time = 0
    
    player = Player(WIDTH, HEIGHT)
    all_sprites = pygame.sprite.Group(player)
    bullets = pygame.sprite.Group()
    shrapnel_grenades = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    trail_group = pygame.sprite.Group()
    boss_group = pygame.sprite.Group()
    boss_bullets = pygame.sprite.Group()
    gravity_bombs = pygame.sprite.Group()
    
    lives = INITIAL_LIVES
    score = 0
    level = 1
    current_enemy_speed = ENEMY_SPEED
    current_boss_speed = BOSS_SPEED_BASE
    enemies_per_side = 6 * DIFFICULTY_MULTIPLIER
    level_start_time = 0
    last_periodic_spawn = pygame.time.get_ticks()
    boss_spawned = False

    def start_level():
        nonlocal last_periodic_spawn, level_start_time, boss_spawned, last_pew_time
        boss_spawned = False

        # Clear all existing sprites from the screen except the player
        for sprite in all_sprites:
            if sprite != player:
                sprite.kill()

        # Explicitly empty all groups to ensure a fresh start for the level
        enemies.empty()
        asteroids.empty()
        trail_group.empty()
        bullets.empty()
        shrapnel_grenades.empty()
        boss_bullets.empty()
        boss_group.empty()
        gravity_bombs.empty()
        last_pew_time = 0
        
        # Create Side Rows of Enemies based on scaling
        for i in range(int(enemies_per_side)):
            en_left = Enemy((60, 100 + i * 80), WIDTH, HEIGHT, speed=current_enemy_speed, level=level)
            enemies.add(en_left); all_sprites.add(en_left)
            en_right = Enemy((WIDTH - 60, 100 + i * 80), WIDTH, HEIGHT, speed=current_enemy_speed, level=level)
            enemies.add(en_right); all_sprites.add(en_right)
        
        # Initial Asteroids
        while len(asteroids) < ASTEROID_START_COUNT:
            ast = Asteroid(WIDTH, HEIGHT)
            if ast.pos.distance_to(player.pos) > 150:
                asteroids.add(ast)
                all_sprites.add(ast)
        last_periodic_spawn = pygame.time.get_ticks()
        level_start_time = pygame.time.get_ticks()
        
        # Level music logic: 1-3 uses music 1, 4-6 uses music 2, etc. up to 5
        music_num = ((level - 1) // 3) % 5 + 1
        play_music(f"level-music-{music_num}.midi")

    # --- Start Screen ---
    waiting_for_start = True
    selected_start_level = 1
    while waiting_for_start:
        screen.fill(BLACK)
        start_text = font.render("Press ENTER to Start", True, WHITE)
        level_text = font.render(f"Starting Level: {selected_start_level} (Use Left/Right to change)", True, CYAN)
        
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 + 20))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting_for_start = False
                if event.key in [pygame.K_LEFT, pygame.K_a]:
                    selected_start_level = max(1, selected_start_level - 1)
                if event.key in [pygame.K_RIGHT, pygame.K_d]:
                    selected_start_level += 1
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); return

    # --- 3 Second Countdown ---
    for i in range(3, 0, -1):
        start_ticks = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_ticks < 1000:
            screen.fill(BLACK)
            count_text = font.render(str(i), True, GOLDEN_YELLOW)
            screen.blit(count_text, (WIDTH//2 - count_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); return

    # Initialize level parameters based on selection
    level = selected_start_level
    
    # Scaled Difficulty Logic
    if level <= 3:
        enemies_per_side = (6 * DIFFICULTY_MULTIPLIER) * (1.25 ** (level - 1))
        current_enemy_speed = ENEMY_SPEED * (1.15 ** (level - 1))
        current_boss_speed = BOSS_SPEED_BASE * (BOSS_SPEED_SCALE ** (level - 1))
    else:
        # Base ramp for levels 1-3, then 2% thereafter
        enemies_per_side = (6 * DIFFICULTY_MULTIPLIER * (1.25 ** 2)) * (1.02 ** (level - 3))
        current_enemy_speed = (ENEMY_SPEED * (1.15 ** 2)) * (1.02 ** (level - 3))
        current_boss_speed = (BOSS_SPEED_BASE * (BOSS_SPEED_SCALE ** 2)) * (1.02 ** (level - 3))

    # Mission Start: Populates asteroids and enemies for the first time
    start_level()
    
    def spawn_shrapnel_explosion(pos):
        for i in range(12):
            angle = (360 / 12) * i
            frag = Bullet(pos, angle, WIDTH, HEIGHT, color=ORANGE, size=10)
            bullets.add(frag)
            all_sprites.add(frag)

    def spawn_bomber_explosion(pos):
        # Large but weak explosion: many fragments, low damage
        if sfx["boom"]: sfx["boom"].play()
        for i in range(16):
            angle = (360 / 16) * i
            frag = Bullet(pos, angle, WIDTH, HEIGHT, color=YELLOW, size=6)
            frag.is_bomber_fragment = True # Flag for collision damage
            boss_bullets.add(frag); all_sprites.add(frag)

    def spawn_gravity_explosion(pos):
        if sfx["boom"]: sfx["boom"].play()
        for i in range(24): # "Great fury" - more fragments than shrapnel
            angle = (360 / 24) * i
            frag = Bullet(pos, angle, WIDTH, HEIGHT, color=(200, 0, 255), size=12)
            frag.vel *= 1.5 # Extra fast fragments
            boss_bullets.add(frag)
            all_sprites.add(frag)

    running = True
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Easy exit for fullscreen
                    running = False
                if event.key == pygame.K_d: # Toggle debug with 'D'
                    DEBUG_MODE = not DEBUG_MODE

                # Keyboard Weapon Controls
                if (event.key == pygame.K_SPACE or event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT):
                    # Sound delay logic (1.5s)
                    now = pygame.time.get_ticks()
                    if sfx["pew"] and now - last_pew_time > 1500:
                        sfx["pew"].play()
                        last_pew_time = now

                    if player.weapon_mode == "SPREAD":
                        for offset in [-15, 0, 15]:
                            b = Bullet(player.pos, player.angle + offset, WIDTH, HEIGHT)
                            bullets.add(b); all_sprites.add(b)
                    else:
                        b = Bullet(player.pos, player.angle, WIDTH, HEIGHT)
                        bullets.add(b); all_sprites.add(b)
                
                if (event.key == pygame.K_CAPSLOCK or event.key == pygame.K_RETURN) and player.shrapnel_cooldown == 0:
                    s = ShrapnelBullet(player.pos, player.angle, WIDTH, HEIGHT)
                    shrapnel_grenades.add(s); all_sprites.add(s)
                    player.shrapnel_cooldown = SHRAPNEL_COOLDOWN_MAX

            if event.type == pygame.JOYBUTTONDOWN:
                # Button 0: Primary Fire
                if event.button == 0:
                    # Sound delay logic (1.5s)
                    now = pygame.time.get_ticks()
                    if sfx["pew"] and now - last_pew_time > 1500:
                        sfx["pew"].play()
                        last_pew_time = now

                    if player.weapon_mode == "SPREAD":
                        for offset in [-15, 0, 15]:
                            b = Bullet(player.pos, player.angle + offset, WIDTH, HEIGHT)
                            bullets.add(b); all_sprites.add(b)
                    else:
                        b = Bullet(player.pos, player.angle, WIDTH, HEIGHT)
                        bullets.add(b); all_sprites.add(b)
                
                # Button 1: Shrapnel
                if event.button == 1 and player.shrapnel_cooldown == 0:
                    s = ShrapnelBullet(player.pos, player.angle, WIDTH, HEIGHT)
                    shrapnel_grenades.add(s); all_sprites.add(s)
                    player.shrapnel_cooldown = SHRAPNEL_COOLDOWN_MAX

        if random.random() < POWERUP_SPAWN_CHANCE:
            p = Powerup(WIDTH, HEIGHT)
            powerups.add(p); all_sprites.add(p)

        # Boss Warning UI
        time_to_boss = BOSS_SPAWN_TIME - (pygame.time.get_ticks() - level_start_time)
        if 0 < time_to_boss < 3000 and not boss_spawned:
            if (pygame.time.get_ticks() // 250) % 2 == 0:
                warn_txt = font.render("!!! WARNING: PLANET BREAKER DETECTED !!!", True, RED)
                screen.blit(warn_txt, (WIDTH // 2 - warn_txt.get_width() // 2, 150))

        # Boss Spawning Trigger
        current_ticks = pygame.time.get_ticks()
        if not boss_spawned and (current_ticks - level_start_time > BOSS_SPAWN_TIME):
            if 4 <= level <= 6:
                boss = Boss2(WIDTH, HEIGHT, level, speed=current_boss_speed)
            else:
                boss = Boss(WIDTH, HEIGHT, level, speed=current_boss_speed)
            boss_group.add(boss)
            all_sprites.add(boss)
            boss_spawned = True
            
            # Boss music logic: changes every level, cycles after 5
            boss_music_num = ((level - 1) % 5) + 1
            play_music(f"boss{boss_music_num}.midi")

        # Frequent reinforcement logic: 10 new enemies every 5 seconds until the Boss appears
        if not boss_spawned and current_ticks - last_periodic_spawn > 5000:
            for i in range(5):
                en_left = Enemy((60, random.randint(100, HEIGHT-100)), WIDTH, HEIGHT, speed=current_enemy_speed, level=level)
                enemies.add(en_left); all_sprites.add(en_left)
                en_right = Enemy((WIDTH - 60, random.randint(100, HEIGHT-100)), WIDTH, HEIGHT, speed=current_enemy_speed, level=level)
                enemies.add(en_right); all_sprites.add(en_right)
            last_periodic_spawn = current_ticks

        # Boss Combat Logic
        if boss_spawned and len(boss_group) > 0:
            b_ent = boss_group.sprites()[0]
            if b_ent.fire_cooldown == 0:
                # Boss fires downward spread
                for ox in [-40, 40]:
                    bb = Bullet((b_ent.rect.centerx + ox, b_ent.rect.bottom), 90, WIDTH, HEIGHT, color=RED, size=8)
                    boss_bullets.add(bb); all_sprites.add(bb)
                b_ent.fire_cooldown = b_ent.fire_rate_max

            # Boss 2 Gravity Bombs
            if isinstance(b_ent, Boss2):
                if b_ent.bomb_cooldown > 0:
                    b_ent.bomb_cooldown -= 1
                else:
                    dist = random.randint(200, 600) # Varying distances
                    angle = random.randint(60, 120) # Broadly downwards
                    gb = GravityBomb(b_ent.rect.center, angle, WIDTH, HEIGHT, dist)
                    gravity_bombs.add(gb); all_sprites.add(gb)
                    b_ent.bomb_cooldown = 180 # Every 3 seconds

        # Handle gravity bomb detonations
        for bomb in list(gravity_bombs):
            if bomb.exploded:
                spawn_gravity_explosion(bomb.rect.center)
                bomb.kill()

        # Handle shrapnel grenade timeout explosions
        for s in list(shrapnel_grenades):
            if s.exploded:
                spawn_shrapnel_explosion(s.rect.center)
                s.kill()

        if random.random() < ENEMY_DIVE_CHANCE:
            idle_enemies = [e for e in enemies if e.state == "FORMATION"]
            if idle_enemies:
                random.choice(idle_enemies).state = "DIVING"

        all_sprites.update(player_pos=player.pos, joysticks=joysticks, trail_group=trail_group)
        trail_group.update()

        # Check for Bomber arrival
        for en in list(enemies):
            if hasattr(en, 'reached_target') and en.reached_target:
                spawn_bomber_explosion(en.rect.center)
                en.kill()

        # 1. Bullets vs Enemies
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for en in hits:
            en.health -= len(hits[en]) * BULLET_DAMAGE
            if sfx["splat"]: sfx["splat"].play()
            if en.health <= 0:
                en.kill()
                score += 3
        
        # Boss Collisions
        boss_hits = pygame.sprite.groupcollide(boss_group, bullets, False, True)
        for b_hit in boss_hits:
            b_hit.health -= len(boss_hits[b_hit]) * BULLET_DAMAGE
            b_hit.hit_flash = 3
            if sfx["splat"]: sfx["splat"].play()
            if b_hit.health <= 0:
                b_hit.kill()
                score += 100

        # Boss vs Shrapnel
        boss_grenade = pygame.sprite.groupcollide(boss_group, shrapnel_grenades, False, True)
        for b_hit in boss_grenade:
            b_hit.health -= SHRAPNEL_DAMAGE
            b_hit.hit_flash = 5
            spawn_shrapnel_explosion(b_hit.rect.center)
            if sfx["boom"]: sfx["boom"].play()
            if b_hit.health <= 0:
                b_hit.kill()
                score += 100

        # Shrapnel hits
        grenade_hits = pygame.sprite.groupcollide(enemies, shrapnel_grenades, False, True)
        for en in grenade_hits:
            en.health -= SHRAPNEL_DAMAGE
            if sfx["boom"]: sfx["boom"].play()
            spawn_shrapnel_explosion(en.rect.center)
            if en.health <= 0:
                en.kill()
                score += 3

        grenade_ast_hits = pygame.sprite.groupcollide(asteroids, shrapnel_grenades, False, True)
        for ast in grenade_ast_hits:
            ast.health -= SHRAPNEL_DAMAGE
            if sfx["boom"]: sfx["boom"].play()
            spawn_shrapnel_explosion(ast.rect.center)
            if ast.health <= 0:
                score += 1
                if ast.size > 1:
                    for _ in range(2):
                        new_ast = Asteroid(WIDTH, HEIGHT, ast.pos, ast.size - 1)
                        asteroids.add(new_ast)
                        all_sprites.add(new_ast)
                ast.kill()
        
        ast_hits = pygame.sprite.groupcollide(asteroids, bullets, False, True)
        for ast in ast_hits:
            ast.health -= len(ast_hits[ast]) * BULLET_DAMAGE
            if sfx["poof"]: sfx["poof"].play()
            if ast.health <= 0:
                score += 1
                if ast.size > 1:
                    for _ in range(2):
                        new_ast = Asteroid(WIDTH, HEIGHT, ast.pos, ast.size - 1)
                        asteroids.add(new_ast)
                        all_sprites.add(new_ast)
                ast.kill()

        # Powerup Collection
        if pygame.sprite.spritecollide(player, powerups, True):
            player.weapon_mode = "SPREAD"
            player.powerup_hits = 0
            score += 2
            player.update_appearance()

        # Hazard Collision with Invulnerability Check
        if player.invulnerable_timer == 0:
            # Check if player hit the DOOOOOM LASER
            laser_hit = False
            if boss_spawned and len(boss_group) > 0:
                b_ent = boss_group.sprites()[0]
                if b_ent.laser_active_timer > 0:
                    laser_rect = pygame.Rect(b_ent.rect.centerx - 40, b_ent.rect.bottom, 80, HEIGHT)
                    if player.rect.colliderect(laser_rect):
                        laser_hit = True

            # 1. Check for Bomber Fragments first (3 damage)
            bomber_hits = pygame.sprite.spritecollide(player, boss_bullets, False)
            bomber_frag_hit = False
            for frag in bomber_hits:
                if hasattr(frag, 'is_bomber_fragment'):
                    player.health -= BOMBER_DAMAGE
                    player.lose_powerup_level()

                    frag.kill()
                    bomber_frag_hit = True

            # 2. Check for Heavy Hazards (50 damage / death)
            collided_enemies = pygame.sprite.spritecollide(player, enemies, False)
            collided_asteroids = pygame.sprite.spritecollide(player, asteroids, False)
            collided_bombs = pygame.sprite.spritecollide(player, gravity_bombs, True)
            # Only check for standard boss bullets (NOT fragments)
            boss_bullet_hits = pygame.sprite.spritecollide(player, boss_bullets, True)

            if collided_enemies or collided_asteroids or boss_bullet_hits or \
               collided_bombs or bomber_frag_hit or \
               pygame.sprite.spritecollide(player, boss_group, False) or laser_hit:

                if collided_bombs:
                    for b in collided_bombs:
                        spawn_gravity_explosion(b.rect.center)

                for ast in collided_asteroids:
                    ast.health -= PLAYER_COLLISION_DAMAGE
                    if ast.health <= 0:
                        score += 1
                        if ast.size > 1:
                            for _ in range(2):
                                new_ast = Asteroid(WIDTH, HEIGHT, ast.pos, ast.size - 1)
                                asteroids.add(new_ast)
                                all_sprites.add(new_ast)
                        ast.kill()

                if player.weapon_mode == "SPREAD":
                    player.powerup_hits += 1
                    if player.powerup_hits >= SPREAD_HITS_REVERT:
                        player.weapon_mode = "NORMAL"
                        player.update_appearance()
                
                # Handle Damage and Blobs
                blob_hit = any(en.dive_type == "BLOB" for en in collided_enemies)
                if bomber_frag_hit and not (collided_enemies or collided_asteroids or boss_bullet_hits or laser_hit):
                    # Damage already applied in fragment loop, skip hazard damage
                    pass
                elif blob_hit:
                    player.health -= BLOB_DAMAGE
                    player.lose_powerup_level()

                    player.stun_timer = BLOB_STUN_TIME
                    player.vel = pygame.Vector2(0, 0) # Halt momentum on capture
                else:
                    player.health -= HAZARD_DAMAGE
                    player.lose_powerup_level()

                    player.lose_powerup_level()

                
                # Give the player invulnerability on any hit to prevent instant death and unwanted resets
                player.invulnerable_timer = 120

                if player.health <= 0:
                    lives += 1
                    player.health = PLAYER_MAX_HEALTH
                    player.pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
                    player.vel = pygame.Vector2(0, 0)

        # Check for Level Complete (Now depends on Boss death)
        if boss_spawned and len(boss_group) == 0:
            # Victory Message
            if sfx["tada"]:
                sfx["tada"].play()

            screen.fill(BLACK)
            msg = f"Planet {level} Saved!"
            if level == 1:
                sub_msg = "Congratulations on saving your first planet from certain demise."
            else:
                sub_msg = "Congratulations on saving yet another planet from certain demise."
            prompt = "Press SPACE to continue to the next mission..."
            
            text_msg = font.render(msg, True, GOLDEN_YELLOW)
            text_sub = font.render(sub_msg, True, WHITE)
            text_prompt = font.render(prompt, True, CYAN)
            
            screen.blit(text_msg, (WIDTH//2 - text_msg.get_width()//2, HEIGHT//2 - 60))
            screen.blit(text_sub, (WIDTH//2 - text_sub.get_width()//2, HEIGHT//2))
            screen.blit(text_prompt, (WIDTH//2 - text_prompt.get_width()//2, HEIGHT//2 + 60))
            pygame.display.flip()
            
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        waiting = False
                    if event.type == pygame.QUIT:
                        pygame.quit(); return
            
            # Progression Scaling
            level += 1
            if level <= 3:
                enemies_per_side *= 1.25
                current_enemy_speed *= 1.15
                current_boss_speed *= BOSS_SPEED_SCALE
            else:
                # Much smaller difficulty jumps after level 3
                enemies_per_side *= 1.02
                current_enemy_speed *= 1.02
                current_boss_speed *= 1.02
            start_level()

        # Draw
        screen.fill(BLACK)
        # Draw trails before sprites so they appear behind the ship
        trail_group.draw(screen)
        all_sprites.draw(screen)

        # UI & Debug Overlay
        lives_text = font.render(f"LIFE: {lives}", True, WHITE)
        screen.blit(lives_text, (20, 20))
        score_text = font.render(f"SCORE: {score}", True, WHITE)
        screen.blit(score_text, (20, 50))
        
        # Player Health Value
        h_color = GREEN if player.health > 40 else RED
        health_text = font.render(f"HEALTH: {int(player.health)}", True, h_color)
        screen.blit(health_text, (20, 80))

        # Shrapnel Cooldown Bar
        bar_width = 150
        pygame.draw.rect(screen, (50, 50, 50), (20, 100, bar_width, 15))
        cd_ratio = 1 - (player.shrapnel_cooldown / SHRAPNEL_COOLDOWN_MAX)
        pygame.draw.rect(screen, ORANGE, (20, 100, int(bar_width * cd_ratio), 15))
        cd_label = font.render("GRENADE", True, WHITE)
        screen.blit(cd_label, (20, 120))

        # Boss Health Bar
        if boss_spawned and len(boss_group) > 0:
            b_ent = boss_group.sprites()[0]
            # Draw Laser Warning
            if b_ent.laser_warning_timer > 0:
                # Flickering thin line to warn the player
                if pygame.time.get_ticks() % 200 > 100:
                    pygame.draw.rect(screen, (150, 0, 0), (b_ent.rect.centerx - 2, b_ent.rect.bottom, 4, HEIGHT))

            # Draw DOOOOOM LASER
            if b_ent.laser_active_timer > 0:
                # Add some jitter for a more "unstable energy" feel
                jitter = random.randint(-4, 4)
                laser_rect = pygame.Rect(b_ent.rect.centerx - 40 + jitter, b_ent.rect.bottom, 80 - jitter*2, HEIGHT)
                pygame.draw.rect(screen, RED, laser_rect)
                # White-hot core
                pygame.draw.rect(screen, WHITE, (b_ent.rect.centerx - 15, b_ent.rect.bottom, 30, HEIGHT))
            
            # Boss Health Bar (Stationary Top Right)
            health_ratio = max(0, b_ent.health / b_ent.max_health)
            bar_x = WIDTH - 220
            pygame.draw.rect(screen, (50, 0, 0), (bar_x, 20, 200, 15))
            pygame.draw.rect(screen, RED, (bar_x, 20, int(200 * health_ratio), 15))
            boss_name = "PLANET BREAKER" if isinstance(b_ent, Boss) else "SECTOR GUARDIAN"
            boss_label = font.render(f"{boss_name} - LVL {level}", True, RED)
            screen.blit(boss_label, (bar_x, 40))
            
            # Hit Flash Effect
            if b_ent.hit_flash > 0:
                flash_surf = b_ent.image.copy()
                flash_surf.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
                screen.blit(flash_surf, b_ent.rect)

        if DEBUG_MODE:
            fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, YELLOW)
            entities_text = font.render(f"Entities: {len(all_sprites)}", True, YELLOW)
            pos_text = font.render(f"Player Pos: {int(player.pos.x)}, {int(player.pos.y)}", True, YELLOW)
            screen.blit(fps_text, (WIDTH - 150, 20))
            screen.blit(entities_text, (WIDTH - 150, 50))
            screen.blit(pos_text, (WIDTH - 250, 80))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
