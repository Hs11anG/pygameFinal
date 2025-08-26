# monster.py
import pygame
import random
from settings import *
from asset_manager import assets

class Monster(pygame.sprite.Sprite):
    def __init__(self, spawn_pos, monster_type, target, level_multiplier=1.0):
        super().__init__()
        
        self.data = MONSTER_DATA[monster_type]
        self.target = target
        self.state = 'alive' 

        self.health = self.data['health'] * level_multiplier
        self.max_health = self.health
        self.damage = self.data['damage'] * level_multiplier

        # --- ↓↓↓ 【【【本次新增：僵直計時器】】】 ↓↓↓ ---
        self.stun_end_time = 0 
        # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---

        # 載入移動動畫影格
        self.animation_frames = []
        if 'animation_frames' in self.data:
            for frame_name in self.data['animation_frames']:
                frame_image = assets.get_image(frame_name)
                if frame_image:
                    self.animation_frames.append(frame_image)
        
        # 載入死亡動畫影格
        self.death_frames = []
        if 'death_frames' in self.data:
            for frame_name in self.data['death_frames']:
                frame_image = assets.get_image(frame_name)
                if frame_image:
                    self.death_frames.append(frame_image)

        self.alive_frame_index = 0
        self.death_frame_index = 0
        self.last_update_time = pygame.time.get_ticks()
        self.animation_speed_ms = 150 

        self.death_animation_start_time = 0
        self.fade_start_time = 0
        self.fade_duration = 100 

        if self.animation_frames:
            original_image = self.animation_frames[self.alive_frame_index]
        else:
            original_image = assets.get_image(monster_type)
        
        size = (self.data['sizex'], self.data['sizey'])
        self.image_right = pygame.transform.scale(original_image, size).convert_alpha()
        self.image_left = pygame.transform.flip(self.image_right, True, False)
        self.image = self.image_right
        self.rect = self.image.get_rect(center=spawn_pos)
        
        self.speed = self.data['speed']
        self.direction = pygame.Vector2(1, 0)
        self.facing_right = True

    def take_damage(self, amount):
        if self.state != 'alive':
             return False
        
        self.health -= amount
        if self.health <= 0 and self.state == 'alive':
            self.die()
            return True
        return False

    def die(self):
        self.state = 'dying'
        self.death_frame_index = 0
        self.death_animation_start_time = pygame.time.get_ticks()
        self.speed = 0

    def animate_alive(self):
        if not self.animation_frames:
            return

        now = pygame.time.get_ticks()
        if now - self.last_update_time > self.animation_speed_ms:
            self.last_update_time = now
            self.alive_frame_index = (self.alive_frame_index + 1) % len(self.animation_frames)
            
            new_original_image = self.animation_frames[self.alive_frame_index]
            size = (self.data['sizex'], self.data['sizey'])
            
            self.image_right = pygame.transform.scale(new_original_image, size).convert_alpha()
            self.image_left = pygame.transform.flip(self.image_right, True, False)

    def animate_death(self):
        if not self.death_frames:
            self.kill()
            return
            
        now = pygame.time.get_ticks()
        
        if self.death_frame_index < len(self.death_frames) - 1:
            if now - self.death_animation_start_time > self.animation_speed_ms:
                self.death_frame_index += 1
                self.death_animation_start_time = now
        
        if self.death_frame_index == len(self.death_frames) - 1:
            if self.fade_start_time == 0:
                self.fade_start_time = now
            
            elapsed = now - self.fade_start_time
            if elapsed < self.fade_duration:
                alpha = 255 * (1 - (elapsed / self.fade_duration))
                self.image.set_alpha(alpha)
            else:
                self.kill()

        death_image_original = self.death_frames[self.death_frame_index]
        size = (self.data['sizex'], self.data['sizey'])
        new_image = pygame.transform.scale(death_image_original, size).convert_alpha()
        
        if not self.facing_right:
            new_image = pygame.transform.flip(new_image, True, False)
        
        current_alpha = self.image.get_alpha()
        self.image = new_image
        if current_alpha is not None:
             self.image.set_alpha(current_alpha)

    def attack_target(self):
        target_pos = pygame.Vector2(self.target.rect.center)
        current_pos = pygame.Vector2(self.rect.center)
        self.direction = (target_pos - current_pos)
        if self.direction.length() > 0:
            self.direction.normalize_ip()
        
        self.rect.center += self.direction * self.speed
        
    def knockback(self):
        knockback_vector = -self.direction * 50
        self.rect.center += knockback_vector
        print(f"'{self.data['name']}' was knocked back.")
        # --- ↓↓↓ 【【【本次新增：設定僵直結束的時間點】】】 ↓↓↓ ---
        self.stun_end_time = pygame.time.get_ticks() + 100 # 100 毫秒 = 0.1 秒
        # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---


    def update(self):
        if self.state == 'alive':
            # --- ↓↓↓ 【【【本次新增：檢查是否在僵直狀態】】】 ↓↓↓ ---
            now = pygame.time.get_ticks()
            if now < self.stun_end_time:
                return # 如果還在僵直時間內，直接跳過後續所有動作
            # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---

            self.animate_alive()
            self.attack_target()
            
            if self.direction.x > 0:
                self.facing_right = True
            elif self.direction.x < 0:
                self.facing_right = False
            
            if self.facing_right:
                self.image = self.image_right
            else:
                self.image = self.image_left

        elif self.state == 'dying':
            self.animate_death()
    
    def draw_health_bar(self, surface):
        if self.state != 'alive' or self.health >= self.max_health:
            return
            
        WHITE = (255, 255, 255)
        RED = (255, 0, 0)
        health_percent = self.health / self.max_health
        bar_width = self.rect.width * 0.8
        bar_height = 7
        bar_x = self.rect.centerx - bar_width / 2
        bar_y = self.rect.bottom + 5
        background_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        health_rect = pygame.Rect(bar_x, bar_y, bar_width * health_percent, bar_height)
        pygame.draw.rect(surface, WHITE, background_rect)
        pygame.draw.rect(surface, RED, health_rect)