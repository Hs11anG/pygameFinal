# weapon.py
import pygame
from settings import *
from asset_manager import assets
from projectile import Projectile

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
        
        # ↓↓↓ 【【【這就是本次的核心修改】】】 ↓↓↓
        # 不再設為 0，而是設為一個「早已冷卻完畢」的時間點。
        # 這樣可以確保武器在關卡開始時，一定是處於 "Ready" 狀態。
        cooldown_ms = self.data['cooldown'] * 1000
        self.last_shot_time = pygame.time.get_ticks() - cooldown_ms

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
            
    def draw_ui(self, screen):
        font = assets.get_font('weapon_ui') 
        if not font: return

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
        
        if text:
            text_surf = font.render(text, True, color)
            bg_rect = text_surf.get_rect(midbottom=self.rect.midtop).inflate(20, 10)
            pygame.draw.rect(screen, UI_BG_COLOR, bg_rect, border_radius=5)
            pygame.draw.rect(screen, UI_BORDER_COLOR, bg_rect, width=1, border_radius=5)
            screen.blit(text_surf, text_surf.get_rect(center=bg_rect.center))