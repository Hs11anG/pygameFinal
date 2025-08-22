# weapon.py
import pygame
from settings import *
from asset_manager import assets
from projectile import BswordProjectile, BoardProjectile

PROJECTILE_CLASSES = {
    'BswordProjectile': BswordProjectile,
    'BoardProjectile': BoardProjectile,
}

class Weapon(pygame.sprite.Sprite):
    def __init__(self, position, weapon_type):
        super().__init__()
        
        self.data = WEAPON_DATA.get(weapon_type)
        if not self.data: self.kill(); return
            
        self.weapon_type = weapon_type
        
        original_image = assets.get_image(self.data['id'])
        self.image = pygame.transform.scale(original_image, self.data['size'])
        self.rect = self.image.get_rect(center=position)

        self.state = 'idle'
        
        cooldown_ms = self.data['cooldown'] * 1000
        self.last_shot_time = pygame.time.get_ticks() - cooldown_ms

        # 【新增】一個屬性，用來追蹤發射出去的飛行物
        self.active_projectile = None

    def update(self, player):
        # 【修改】加入檢查 active_projectile 的邏輯
        if self.state != 'active':
            distance_to_player = pygame.Vector2(self.rect.center).distance_to(player.rect.center)
            if distance_to_player < 60:
                self.state = 'in_range'
            else:
                self.state = 'idle'
        
        # 如果是「回來才CD」的武器，需要持續檢查它的飛行物是否還活著
        if self.data.get('cooldown_type') == 'on_return' and self.active_projectile:
            # .alive() 是 Sprite 的一個方法，用來檢查它是否還在任何 Group 中
            if not self.active_projectile.alive():
                # 如果飛行物消失了 (kill()被呼叫)，則開始計時
                self.last_shot_time = pygame.time.get_ticks()
                self.active_projectile = None
                print(f"'{self.data['name']}' returned, cooldown started.")

    def fire(self, target_pos, projectile_group):
        now = pygame.time.get_ticks()
        cooldown = self.data['cooldown'] * 1000
        cooldown_type = self.data.get('cooldown_type', 'on_fire')

        # 【修改】開火條件變得更複雜
        # 條件1: 正常的時間冷卻
        can_fire_by_time = now - self.last_shot_time > cooldown
        # 條件2: 如果是 on_return 類型，必須沒有現役的飛行物
        can_fire_by_return = cooldown_type == 'on_fire' or self.active_projectile is None
        
        if can_fire_by_time and can_fire_by_return:
            # 如果是「射出即CD」，則立刻重置計時器
            if cooldown_type == 'on_fire':
                self.last_shot_time = now
            
            class_name = self.data.get('projectile_class_name')
            ProjectileClass = PROJECTILE_CLASSES.get(class_name)
            
            if ProjectileClass:
                new_projectile = ProjectileClass(self.rect.center, target_pos, self.weapon_type)
                projectile_group.add(new_projectile)
                
                # 如果是「回來才CD」，則記錄下這個飛行物
                if cooldown_type == 'on_return':
                    self.active_projectile = new_projectile
            else:
                print(f"警告：找不到名為 '{class_name}' 的類別！")
            
    def draw_ui(self, screen):
        """繪製武器自身的 UI，包含名稱、提示和冷卻時間"""
        font = assets.get_font('weapon_ui') 
        if not font: return

        text = ""
        color = WHITE
        
        now = pygame.time.get_ticks()
        cooldown = self.data['cooldown'] * 1000
        elapsed_since_last_shot = now - self.last_shot_time
        
        # 優先顯示冷卻時間
        if elapsed_since_last_shot < cooldown:
            remaining_cd = (cooldown - elapsed_since_last_shot) / 1000
            text = f"{remaining_cd:.1f}s"
        # 冷卻完畢後，再根據狀態顯示
        else:
            if self.state == 'active':
                text = "Ready"
            elif self.state == 'in_range':
                text = "按E裝備"
            elif self.state == 'idle':
                text = self.data['name']
                color = HOVER_COLOR
        
        # 如果有文字需要顯示，才繪製背景和文字
        if text:
            text_surf = font.render(text, True, color)
            bg_rect = text_surf.get_rect(midbottom=self.rect.midtop).inflate(20, 10) # 加上邊距
            pygame.draw.rect(screen, UI_BG_COLOR, bg_rect, border_radius=5)
            pygame.draw.rect(screen, UI_BORDER_COLOR, bg_rect, width=1, border_radius=5)
            screen.blit(text_surf, text_surf.get_rect(center=bg_rect.center))