# monster.py
import pygame
import random
from settings import *
from asset_manager import assets

class Monster(pygame.sprite.Sprite):
    def __init__(self, spawn_pos, monster_type, target):
        super().__init__()
        
        self.data = MONSTER_DATA[monster_type]
        self.target = target # 【新增】儲存攻擊目標

        # 圖像與狀態
        original_image = assets.get_image(monster_type)
        size = (self.data['sizex'], self.data['sizey'])
        self.image_right = pygame.transform.scale(original_image, size)
        self.image_left = pygame.transform.flip(self.image_right, True, False)
        self.image = self.image_right
        self.rect = self.image.get_rect(center=spawn_pos)
        
        self.health = self.data['health']
        self.max_health = self.health
        self.speed = self.data['speed']
        self.direction = pygame.Vector2(1, 0)
        self.facing_right = True

    def attack_target(self):
        """計算朝向目標的方向並移動"""
        target_pos = pygame.Vector2(self.target.rect.center)
        current_pos = pygame.Vector2(self.rect.center)
        self.direction = (target_pos - current_pos)
        if self.direction.length() > 0:
            self.direction.normalize_ip()
        
        self.rect.center += self.direction * self.speed
        
    def knockback(self):
        """被擊退"""
        # 沿著移動的反方向被推開 50 像素
        knockback_vector = -self.direction * 50
        self.rect.center += knockback_vector
        print(f"'{self.data['name']}' was knocked back.")

    def update(self):
        self.attack_target()
        
        # 圖片翻轉
        if self.direction.x > 0 and not self.facing_right:
            self.image = self.image_right
            self.facing_right = True
        elif self.direction.x < 0 and self.facing_right:
            self.image = self.image_left
            self.facing_right = False
    

    def draw_health_bar(self, surface):
        # ... (此方法不變)
        if self.health < self.max_health:
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