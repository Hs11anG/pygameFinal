# projectile.py
import pygame
import math
from settings import *
from asset_manager import assets

class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, weapon_type):
        super().__init__()
        self.data = WEAPON_DATA.get(weapon_type)
        if not self.data: self.kill(); return
        self.damage = self.data['damage']
        self.creation_time = pygame.time.get_ticks()

    def update(self):
        raise NotImplementedError

# --- 武器一：竹簡劍 ---
class BswordProjectile(Projectile):
    def __init__(self, start_pos, target_pos, weapon_type):
        super().__init__(start_pos, target_pos, weapon_type)
        
        # --- ↓↓↓ 【【【本次新增：穿透屬性】】】 ↓↓↓ ---
        self.piercing = False
        # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---

        original_image = assets.get_image(self.data['id'])
        size_multiplier = self.data['projectile_size_multiplier']
        new_size = (int(self.data['size'][0] * size_multiplier), int(self.data['size'][1] * size_multiplier))
        scaled_image = pygame.transform.scale(original_image, new_size)
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        angle = math.degrees(math.atan2(-dy, dx)) - 90

        self.image = pygame.transform.rotate(scaled_image, angle)
        self.rect = self.image.get_rect(center=start_pos)
        self.mask = pygame.mask.from_surface(self.image)
        
        self.direction = pygame.Vector2(dx, dy)
        if self.direction.length() > 0:
            self.direction.normalize_ip()
        self.speed = 15

    def update(self):
        self.rect.center += self.direction * self.speed
        if not pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).colliderect(self.rect):
            self.kill()

# --- 武器二：轉型正義板 (迴力鏢) ---
class BoardProjectile(Projectile):
    def __init__(self, start_pos, target_pos, weapon_type):
        super().__init__(start_pos, target_pos, weapon_type)
        
        self.original_image = assets.get_image(self.data['id'])
        size_multiplier = self.data['projectile_size_multiplier']
        self.size = (int(self.data['size'][0] * size_multiplier), int(self.data['size'][1] * size_multiplier))
        self.image = pygame.transform.scale(self.original_image, self.size)
        self.rect = self.image.get_rect(center=start_pos)
        self.state = 'outbound'
        self.origin_pos = pygame.Vector2(start_pos)
        self.direction = (pygame.Vector2(target_pos) - self.origin_pos)
        if self.direction.length() > 0: self.direction.normalize_ip()
        self.speed = 10
        self.angle = 0
        self.rotation_speed = 15
        self.spin_start_time = 0
        self.spin_duration = 1000
        self.hit_cooldowns = {}

    def update(self):
        now = pygame.time.get_ticks()
        self.angle = (self.angle + self.rotation_speed) % 360
        old_center = self.rect.center
        self.image = pygame.transform.scale(pygame.transform.rotate(self.original_image, self.angle), self.size)
        self.rect = self.image.get_rect(center=old_center)
        self.mask = pygame.mask.from_surface(self.image)
        if self.state == 'outbound':
            self.rect.center += self.direction * self.speed
            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH or self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
                self.start_spinning()
        elif self.state == 'spinning':
            if now - self.spin_start_time > self.spin_duration:
                self.state = 'returning'
        elif self.state == 'returning':
            return_direction = (self.origin_pos - pygame.Vector2(self.rect.center))
            if return_direction.length() < self.speed * 2:
                self.kill()
            else:
                self.rect.center += return_direction.normalize() * self.speed
                
    def start_spinning(self):
        if self.state == 'outbound':
            self.state = 'spinning'
            self.spin_start_time = pygame.time.get_ticks()