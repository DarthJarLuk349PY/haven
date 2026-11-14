import pygame

from scripts.animation import load_strip
from scripts.combat import Combatant


class Player(Combatant):
    SPEED = 250
    RUN_SPEED = 370
    ATTACK_COOLDOWN = 0.15
    ATTACK_WINDUP = 0.10
    ATTACK_DURATION = 0.34
    ATTACK_RANGE = 125
    ATTACK_DAMAGE = 30

    def __init__(self, x, y, settings=None, world_size=(1280, 720)):
        if settings is None:
            super().__init__(x, y, max_health=120)
        else:
            super().__init__(x, y, max_health=settings.max_health)
            self.SPEED = settings.walk_speed
            self.RUN_SPEED = settings.run_speed
            self.ATTACK_DAMAGE = settings.attack_damage
            self.ATTACK_RANGE = settings.attack_range
            self.ATTACK_COOLDOWN = settings.attack_cooldown
            self.ATTACK_WINDUP = settings.attack_windup
            self.ATTACK_DURATION = settings.attack_duration
        self.animations = {
            "idle": load_strip(
                "player_assets/player_temp/male_hero_template-idle.png", 128, 128
            ),
            "walk": load_strip(
                "player_assets/player_temp/male_hero_template-walk.png", 128, 128
            ),
            "run": load_strip(
                "player_assets/player_temp/male_hero_template-run.png", 128, 128
            ),
            "jump": load_strip(
                "player_assets/player_temp/male_hero_template-jump.png", 128, 128
            ),
            "fall": load_strip(
                "player_assets/player_temp/male_hero_template-fall.png", 128, 128
            ),
            "attack": load_strip(
                "player_assets/player_temp/male_hero_template-combo_1.png", 128, 128
            ),
            "attack_end": load_strip(
                "player_assets/player_temp/male_hero_template-combo_1_end.png",
                128,
                128,
            ),
        }
        self.state = "idle"
        self._animation_state = self.state
        self.frame = 0
        self.animation_timer, self.attack_timer = 0,0
        self.attack_cooldown = 0
        self.attack_hit_timer = None
        self.attack_has_hit = False
        self.attack_chain,  self.damage_flash = 0, 0
        self.world_width, self.world_height = world_size
        self.jump_height = 0.0
        self.vertical_velocity = 0.0
        self.is_airborne = False

    def start_attack(self, aim_x=None):
        if not self.alive or self.attack_cooldown > 0:
            return False

        if aim_x is not None and aim_x != self.x:
            self.facing = 1 if aim_x > self.x else -1
        self.attack_cooldown = self.ATTACK_COOLDOWN
        self.attack_timer = self.ATTACK_DURATION
        self.attack_hit_timer = self.ATTACK_WINDUP
        self.attack_has_hit = False
        self.attack_chain = 1 - self.attack_chain
        self.state = "attack" if self.attack_chain == 0 else "attack_end"
        self.frame = 0
        self.animation_timer = 0
        return True

    def update(
        self, dt, keys, enemies, blocking=False, jump_pads=None, virtual_keys=()
    ):
        def pressed(key):
            return keys[key] or key in virtual_keys

        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.damage_flash = max(0, self.damage_flash - dt)
        self.blocking = blocking and self.alive

        move = pygame.Vector2()
        if self.alive:
            move = pygame.Vector2(
                int(pressed(pygame.K_d) or pressed(pygame.K_RIGHT))
                - int(pressed(pygame.K_a) or pressed(pygame.K_LEFT)),
                int(pressed(pygame.K_s) or pressed(pygame.K_DOWN))
                - int(pressed(pygame.K_w) or pressed(pygame.K_UP)),
            )
            if move.length_squared():
                move.normalize_ip()
                running = pressed(pygame.K_LSHIFT) or pressed(pygame.K_RSHIFT)
                speed = self.RUN_SPEED if running else self.SPEED
                self.x += move.x * speed * dt
                self.y += move.y * speed * dt
                if move.x:
                    self.facing = 1 if move.x > 0 else -1

            self.x = max(45, min(self.world_width - 45, self.x))
            self.y = max(55, min(self.world_height - 45, self.y))
            self._update_jump(dt, jump_pads)

            if self.attack_hit_timer is not None:
                self.attack_hit_timer -= dt
                if self.attack_hit_timer <= 0 and not self.attack_has_hit:
                    self._hit_enemies(enemies)
                    self.attack_has_hit = True
                    self.attack_hit_timer = None

        if not self.alive:
            self.state = "idle"
        elif self.attack_timer > 0:
            self.attack_timer = max(0, self.attack_timer - dt)
            self.state = "attack" if self.attack_chain == 0 else "attack_end"
        elif self.is_airborne:
            self.state = "jump" if self.vertical_velocity > 0 else "fall"
        elif self.blocking:
            self.state = "idle"
        elif move.length_squared():
            running = pressed(pygame.K_LSHIFT) or pressed(pygame.K_RSHIFT)
            self.state = "run" if running else "walk"
        else:
            self.state = "idle"

        self._advance_animation(dt)

    def _update_jump(self, dt, jump_pads):
        if jump_pads is None:
            return

        if self.is_airborne:
            self.vertical_velocity -= jump_pads.gravity * dt
            self.jump_height += self.vertical_velocity * dt
            if self.jump_height <= 0:
                self.jump_height = 0
                self.vertical_velocity = 0
                self.is_airborne = False
                if jump_pads.pad_at(self.x, self.y) is not None:
                    self._bounce(jump_pads.launch_velocity)
        elif jump_pads.pad_at(self.x, self.y) is not None:
            self._bounce(jump_pads.launch_velocity)

    def _bounce(self, launch_velocity):
        self.vertical_velocity = launch_velocity
        self.is_airborne = True

    def _hit_enemies(self, enemies):
        for enemy in enemies:
            if not enemy.alive:
                continue
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            if dx * dx + dy * dy > self.ATTACK_RANGE * self.ATTACK_RANGE:
                continue
            if dx * self.facing < -12:
                continue
            enemy.take_damage(self.ATTACK_DAMAGE, self.x)

    def _advance_animation(self, dt):
        if self.state != self._animation_state:
            self._animation_state = self.state
            self.frame = 0
            self.animation_timer = 0

        self.animation_timer += dt
        frames = self.animations[self.state]
        frame_time = 0.075 if self.state.startswith("attack") else 0.11
        if self.animation_timer >= frame_time:
            self.animation_timer %= frame_time
            if self.state.startswith("attack"):
                self.frame = min(self.frame + 1, len(frames) - 1)
            else:
                self.frame = (self.frame + 1) % len(frames)

    def take_damage(self, amount, attacker_x):
        damage = super().take_damage(amount, attacker_x)
        if damage:
            self.damage_flash = 0.15
        return damage

    def draw(self, surface):
        image = self.animations[self.state][self.frame]
        if self.facing < 0:
            image = pygame.transform.flip(image, True, False)
        image = pygame.transform.scale(image, (256, 256))
        render_y = round(self.y - self.jump_height)
        if self.is_airborne:
            shadow_width = max(28, round(82 - self.jump_height * 0.12))
            pygame.draw.ellipse(
                surface,
                (32, 31, 40),
                (
                    round(self.x - shadow_width / 2),
                    round(self.y + 48 - shadow_width / 5),
                    shadow_width,
                    max(8, round(shadow_width / 2.5)),
                ),
            )
        if self.damage_flash:
            image = image.copy()
            image.fill((255, 100, 100, 90), special_flags=pygame.BLEND_RGBA_ADD)
        surface.blit(image, image.get_rect(center=(round(self.x), render_y)))

        if self.blocking:
            pygame.draw.circle(
                surface, (105, 190, 255), (round(self.x), render_y), 52, 3
            )
