# player.py
import pygame
from asset_manager import assets
from settings import *
# 【修正】引入 PROJECTILE_CLASSES 以便查找
from weapon import PROJECTILE_CLASSES

class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos, level_number):
        super().__init__()
        
        original_image = assets.get_image('player') # 修正了您之前指出的 'playe' 筆誤
        player_size = LEVELS[level_number]['playersize']
        self.image = pygame.transform.scale(original_image, player_size)
        self.rect = self.image.get_rect(midbottom=start_pos)
        self.speed = 5
        
        # 新的武器庫系統
        self.unlocked_weapons = LEVELS[level_number].get('unlocked_weapons', [1])
        self.current_weapon_index = 0
        self.current_weapon_type = self.unlocked_weapons[self.current_weapon_index]
        self.last_shot_time = {} # 為每種武器儲存獨立的冷卻時間
        self.can_switch = True

    def switch_weapon(self, direction):
        """根據方向 (+1 或 -1) 切換武器"""
        if not self.can_switch or len(self.unlocked_weapons) <= 1:
            return
        
        self.current_weapon_index = (self.current_weapon_index + direction) % len(self.unlocked_weapons)
        self.current_weapon_type = self.unlocked_weapons[self.current_weapon_index]
        print(f"Switched to weapon: {WEAPON_DATA[self.current_weapon_type]['name']}")
        self.can_switch = False

    def move(self, keys):
        # 移動邏輯簡化，不再需要 mask
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.rect.x += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]: self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.rect.y += self.speed
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def shoot(self, target_pos, projectile_group):
        now = pygame.time.get_ticks()
        weapon_data = WEAPON_DATA[self.current_weapon_type]
        cooldown = weapon_data['cooldown'] * 1000
        
        # 讀取該武器上次的開火時間，如果沒有則視為 0
        last_shot = self.last_shot_time.get(self.current_weapon_type, 0)

        if now - last_shot > cooldown:
            self.last_shot_time[self.current_weapon_type] = now # 更新該武器的開火時間
            
            class_name = weapon_data.get('projectile_class_name')
            ProjectileClass = PROJECTILE_CLASSES.get(class_name)

            if ProjectileClass:
                new_projectile = ProjectileClass(self.rect.center, target_pos, self.current_weapon_type)
                projectile_group.add(new_projectile)

    def update(self, keys, events, projectile_group):
        """【【【修正後的 update，只接收必要的參數】】】"""
        self.move(keys)

        # 武器切換邏輯
        if keys[pygame.K_q]:
            self.switch_weapon(-1)
        elif keys[pygame.K_e]:
            self.switch_weapon(1)
        else:
            self.can_switch = True
            
        # 按住滑鼠連續射擊
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]: # 左鍵
            self.shoot(pygame.mouse.get_pos(), projectile_group)

    def draw_ui(self, screen):
        """在頭頂繪製當前武器圖標和名稱"""
        weapon_data = WEAPON_DATA[self.current_weapon_type]
        
        icon_image = assets.get_image(weapon_data['id'])
        icon_image = pygame.transform.scale(icon_image, (40, 40))
        icon_rect = icon_image.get_rect(midbottom=self.rect.midtop)
        screen.blit(icon_image, icon_rect)

        font = assets.get_font('weapon_ui')
        text_surf = font.render(weapon_data['name'], True, WHITE)
        text_rect = text_surf.get_rect(midbottom=icon_rect.midtop)
        screen.blit(text_surf, text_rect)