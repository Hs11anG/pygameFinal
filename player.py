# player.py
import pygame
from asset_manager import assets
from settings import *
from projectile import Projectile

class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos, level_number):
        super().__init__()
        
        original_image = assets.get_image('player')
        player_size = LEVELS[level_number]['playersize']
        self.image = pygame.transform.scale(original_image, player_size)
        
        self.rect = self.image.get_rect(midbottom=start_pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 5
        
        # 【修改】不再儲存武器類型，而是直接引用正在操作的武器物件
        self.manning_weapon = None # Manning: 操縱
        self.can_interact = True
        self.offsetx = LEVELS[level_number]['offsetx']
        self.offsety = LEVELS[level_number]['offsety']
    def move(self, keys, walkable_mask):
        """【修改】如果正在操作武器，則無法移動"""
        if self.manning_weapon:
            return

        old_rect = self.rect.copy()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.rect.x += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]: self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.rect.y += self.speed
        
        # 碰撞檢測邏輯不變
        is_valid_move = False
        bottom_left_vec = pygame.Vector2(self.rect.bottomleft)
        bottom_right_vec = pygame.Vector2(self.rect.bottomright)
        point1 = bottom_left_vec + pygame.Vector2(self.offsetx, 0)
        point2 = bottom_right_vec - pygame.Vector2(self.offsetx, 0)
        corners = [point1, point2]
        for pos in corners:
            try:
                if walkable_mask.get_at(pos): is_valid_move = True; break
            except IndexError: continue
        if not is_valid_move: self.rect = old_rect

    def interact(self, weapon_group):
        """【修改】互動邏輯變為'操縱'或'解除操縱'"""
        if self.manning_weapon: # 如果正在操作武器，則解除
            self.manning_weapon.state = 'in_range' # 武器狀態變回 "在範圍內"
            self.manning_weapon = None
            print("解除武器操作")
            return

        # 如果沒有在操作武器，檢查附近是否有可操作的
        interaction_rect = self.rect.inflate(30, 30)
        nearby_weapons = [w for w in weapon_group if interaction_rect.colliderect(w.rect)]

        if nearby_weapons:
            weapon_to_man = min(nearby_weapons, key=lambda w: pygame.Vector2(self.rect.center).distance_to(w.rect.center))
            self.manning_weapon = weapon_to_man
            self.manning_weapon.state = 'active' # 將武器狀態設為 "使用中"
            print(f"開始操作: {self.manning_weapon.data['name']}")
            
    def shoot(self, target_pos, projectile_group):
        """【修改】射擊指令現在是傳遞給正在操作的武器"""
        if self.manning_weapon:
            self.manning_weapon.fire(target_pos, projectile_group)

    def update(self, keys, events, walkable_mask, weapon_group, projectile_group):
        self.move(keys, walkable_mask)

        if keys[pygame.K_e]:
            if self.can_interact:
                self.interact(weapon_group)
                self.can_interact = False
        else:
            self.can_interact = True

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.shoot(event.pos, projectile_group)
    
    # 【修改】玩家不再需要 draw_ui 方法
    # def draw_ui(self, screen):
    #     pass