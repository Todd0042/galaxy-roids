class Player(pygame.sprite.Sprite):
    def __init__(self, screen_w, screen_h):
        super().__init__()

        # --- Rapid-fire state ---
        self.fire_cooldown = 0
        self.fire_button_held = False

        # --- Asteroid collision cooldown ---
        self.last_asteroid_hit = 0
        self.asteroid_hit_cooldown = 1000

        # --- Screen size ---
        self.screen_w = screen_w
        self.screen_h = screen_h

        # --- Ship appearance ---
        self.base_image = pygame.image.load("assets/player/player_ship.png").convert_alpha()
        self.engine_glow = pygame.image.load("assets/player/engine_glow.png").convert_alpha()

        scale_factor = 0.10
        bw = int(self.base_image.get_width() * scale_factor)
        bh = int(self.base_image.get_height() * scale_factor)
        self.base_image = pygame.transform.smoothscale(self.base_image, (bw, bh))

        gw = int(self.engine_glow.get_width() * scale_factor)
        gh = int(self.engine_glow.get_height() * scale_factor)
        self.engine_glow = pygame.transform.smoothscale(self.engine_glow, (gw, gh))
        self.engine_glow_scaled = self.engine_glow.copy()

        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(screen_w // 2, screen_h // 2))

        # --- Movement state ---
        self.pos = pygame.Vector2(self.rect.center)
        self.vel = pygame.Vector2(0, 0)
        self.direction = pygame.Vector2(0, -1)
        self.angle = 0
        self.thrusting = False

        self.rotation_speed = PLAYER_ROT_SPEED
        self.thrust = PLAYER_THRUST
        self.friction = PLAYER_FRICTION

        # --- Combat state ---
        self.shrapnel_cooldown = 0
        self.weapon_mode = "NORMAL"
        self.powerup_hits = 0

        # --- Status effects ---
        self.invulnerable_timer = 0
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.stun_timer = 0

        # --- Hitbox ---
        self.hitbox_radius = 6.5
        self.hitbox_center = pygame.Vector2(self.pos)

        # ⭐ AUDIO: dedicated engine loop channel
        self.engine_channel = pygame.mixer.Channel(7)
        self.engine_active = False

        # ⭐ AUDIO: low health warning
        self.low_health_channel = pygame.mixer.Channel(8)
        self.low_health_active = False

    # -------------------------------------------------
    #   Engine Sound Logic
    # -------------------------------------------------
    def update_engine_sound(self, sfx):
        snd = sfx.get("player_engine")
        if snd is None:
            return

        if self.thrusting and not self.engine_active:
            self.engine_channel.play(snd, loops=-1, fade_ms=150)
            self.engine_active = True

        elif not self.thrusting and self.engine_active:
            self.engine_channel.fadeout(200)
            self.engine_active = False

    # -------------------------------------------------
    #   Low Health Warning
    # -------------------------------------------------
    def update_low_health_sound(self, sfx):
        snd = sfx.get("player_low_health")
        if snd is None:
            return

        health_ratio = self.health / self.max_health

        if health_ratio <= 0.25 and not self.low_health_active:
            self.low_health_channel.play(snd, loops=-1, fade_ms=200)
            self.low_health_active = True

        elif health_ratio > 0.25 and self.low_health_active:
            self.low_health_channel.fadeout(300)
            self.low_health_active = False

    # -------------------------------------------------
    #   Appearance
    # -------------------------------------------------
    def update_appearance(self):
        self.color = GOLDEN_YELLOW if self.weapon_mode == "SPREAD" else CYAN
        self.rotate(0)

    def rotate(self, angle_change):
        self.angle += angle_change
        self.direction = pygame.Vector2(0, -1).rotate(self.angle)
        self.image = pygame.transform.rotate(self.base_image, -self.angle)
        self.rect = self.image.get_rect(center=self.pos)

    # -------------------------------------------------
    #   Main Update
    # -------------------------------------------------
    def update(self, **kwargs):
        keys = pygame.key.get_pressed()
        joysticks = kwargs.get("joysticks", [])
        trail_group = kwargs.get("trail_group")
        state = kwargs.get("state")
        sfx = kwargs.get("sfx")  # ⭐ AUDIO

        # Dynamic screen size
        if state:
            self.screen_w = state["WIDTH"]
            self.screen_h = state["HEIGHT"]

        self.thrusting = False

        # --- Invulnerability flicker ---
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

        # --- Stun stops movement ---
        if self.stun_timer > 0:
            self.stun_timer -= 1
            self.vel = pygame.Vector2(0, 0)

        else:
            # Joystick rotation & thrust
            for joy in joysticks:
                if joy.get_axis(0) < -0.3:
                    self.rotate(-self.rotation_speed)
                elif joy.get_axis(0) > 0.3:
                    self.rotate(self.rotation_speed)

                if joy.get_axis(1) < -0.3:
                    self.vel += self.direction * self.thrust
                    self.thrusting = True
                elif joy.get_axis(1) > 0.3:
                    self.vel *= PLAYER_BRAKE_FRICTION
                    self.vel -= self.direction * PLAYER_REVERSE_THRUST

            # Keyboard rotation & thrust
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.rotate(-self.rotation_speed)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.rotate(self.rotation_speed)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.vel += self.direction * self.thrust
                self.thrusting = True
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.vel *= PLAYER_BRAKE_FRICTION
                self.vel -= self.direction * PLAYER_REVERSE_THRUST

        # --- Engine trail ---
        if self.thrusting and trail_group is not None:
            for side in [-1, 1]:
                offset = self.direction.rotate(90 * side) * 8 - self.direction * 10
                jitter = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                trail_group.add(TrailSegment(self.pos + offset + jitter))

        # --- Movement physics ---
        self.vel *= self.friction
        self.pos += self.vel
        self.pos.x %= self.screen_w
        self.pos.y %= self.screen_h
        self.rect.center = self.pos

        # --- Engine Glow Animation ---
        if self.thrusting:
            t = pygame.time.get_ticks() * 0.01
            pulse = 180 + int(75 * abs(math.sin(t)))
            self.engine_glow.set_alpha(pulse)

            scale = 1.0 + 0.05 * abs(math.sin(t * 0.5))
            speed = self.vel.length()
            stretch = 1.0 + min(speed / 12, 0.6)

            w = int(self.engine_glow.get_width() * scale)
            h = int(self.engine_glow.get_height() * stretch)
            self.engine_glow_scaled = pygame.transform.smoothscale(self.engine_glow, (w, h))
        else:
            self.engine_glow.set_alpha(0)
            self.engine_glow_scaled = self.engine_glow

        # --- Visual flicker ---
        if self.stun_timer > 0:
            self.image.set_alpha(150)
        elif self.invulnerable_timer % 10 > 5:
            self.image.set_alpha(0)
        else:
            self.image.set_alpha(255)

        # --- Cooldowns ---
        if self.shrapnel_cooldown > 0:
            self.shrapnel_cooldown -= 1
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

        # --- Sync hitbox ---
        self.hitbox_center = pygame.Vector2(self.pos)

        # ⭐ AUDIO: engine loop
        if sfx:
            self.update_engine_sound(sfx)
            self.update_low_health_sound(sfx)

    # -------------------------------------------------
    #   Draw
    # -------------------------------------------------
    def draw(self, surface):
        if self.thrusting:
            glow_img = self.engine_glow_scaled
            glow_rect = glow_img.get_rect(center=self.rect.center)
            surface.blit(glow_img, glow_rect)

        surface.blit(self.image, self.rect)

    # -------------------------------------------------
    #   Powerup Loss
    # -------------------------------------------------
    def lose_powerup_level(self):
        if self.powerup_hits > 0:
            self.powerup_hits -= 1

        lvl = self.powerup_hits
        self.weapon_mode = "NORMAL"
        self.has_laser = False
        self.homing_count = 0

        if lvl >= 1:
            self.weapon_mode = "SPREAD"
        if lvl >= 4:
            self.has_laser = True
        if lvl >= 5:
            self.homing_count = 1
        if lvl >= 6:
            self.homing_count = 2

        self.update_appearance()

    # -------------------------------------------------
    #   Damage
    # -------------------------------------------------
    def take_damage(self, amount):
        if self.invulnerable_timer > 0:
            return

        self.health -= amount
        self.invulnerable_timer = 60
        self.lose_powerup_level()
        self.stun_timer = 10

        # ⭐ AUDIO: player hit
        if hasattr(self, "sfx") and self.sfx.get("player_hit"):
            ch = pygame.mixer.find_channel()
            if ch:
                ch.play(self.sfx["player_hit"])

    def apply_explosion(self, damage):
        self.health -= damage
        self.lose_powerup_level()

        # ⭐ AUDIO: explosion damage
        if hasattr(self, "sfx") and self.sfx.get("player_hit"):
            ch = pygame.mixer.find_channel()
            if ch:
                ch.play(self.sfx["player_hit"])
