# weapon.py
import pygame
from settings import * # 引入所有設定，包含新顏色
from asset_manager import assets
from projectile import Projectile

class Weapon(pygame.sprite.Sprite):
    # __init__, update, fire 方法與上一版完全相同
    def __init__(self, position, weapon_type):
        super().__init__()
        self.data = WEAPON_DATA.get(weapon_type)
        if not self.data: self.kill(); return
        self.weapon_type = weapon_type
        original_image = assets.get_image(self.data['id'])
        self.image = pygame.transform.scale(original_image, self.data['size'])
        self.rect = self.image.get_rect(center=position)
        self.state = 'idle'
        self.last_shot_time = 0

    def update(self, player):
        if self.state != 'active':
            distance_to_player = pygame.Vector2(self.rect.center).distance_to(player.rect.center)
            if distance_to_player < 50:
                self.state = 'in_range'
            else:
                self.state = 'idle'

    def fire(self, target_pos, projectile_group):
        now = pygame.time.get_ticks()
        cooldown = self.data['cooldown'] * 1000
        if now - self.last_shot_time > cooldown:
            self.last_shot_time = now
            new_projectile = Projectile(self.rect.center, target_pos, self.weapon_type)
            projectile_group.add(new_projectile)
            
    # ↓↓↓ 【【【這是修改後的 draw_ui 方法】】】 ↓↓↓
    def draw_ui(self, screen):
        """繪製武器自身的 UI，包含較小字體和背景色"""
        # 1. 使用我們新載入的、較小的 'weapon_ui' 字體
        font = assets.get_font('weapon_ui') 
        if not font: return # 如果字體還沒載入好，就先不畫

        text = ""
        color = WHITE
        
        now = pygame.time.get_ticks()
        cooldown = self.data['cooldown'] * 1000
        elapsed_since_last_shot = now - self.last_shot_time
        
        if elapsed_since_last_shot < cooldown:
            remaining_cd = (cooldown - elapsed_since_last_shot) / 1000
            text = f"{remaining_cd:.1f}s"
        else:
            if self.state == 'active':
                text = "Ready"
            elif self.state == 'in_range':
                text = "按E裝備"
            elif self.state == 'idle':
                text = self.data['name']
                color = HOVER_COLOR
        
        # 2. 如果有文字需要顯示，才繪製背景和文字
        if text:
            # 渲染文字
            text_surf = font.render(text, True, color)
            
            # 建立一個比文字框稍大的背景矩形 (上下各多 5 像素，左右各多 10 像素)
            bg_rect = text_surf.get_rect(midbottom=self.rect.midtop).inflate(20, 10)

            # 繪製背景矩形
            pygame.draw.rect(screen, UI_BG_COLOR, bg_rect, border_radius=5)
            # 繪製邊框
            pygame.draw.rect(screen, UI_BORDER_COLOR, bg_rect, width=1, border_radius=5)

            # 最後，將文字繪製在背景之上
            screen.blit(text_surf, text_surf.get_rect(center=bg_rect.center))