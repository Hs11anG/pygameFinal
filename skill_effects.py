# skill_effects.py
import pygame
from asset_manager import assets
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class RescueSkill(pygame.sprite.Sprite):
    def __init__(self, y_position):
        super().__init__()
        
        # 載入動畫影格
        self.animation_frames = [
            assets.get_image('skill3_a1'),
            assets.get_image('skill3_a2')
        ]
        self.frame_index = 0
        self.last_update_time = pygame.time.get_ticks()
        self.animation_speed_ms = 150 # 每 150 毫秒換一張圖

        # 設定尺寸 (比保護目標 100x100 大 1.5 倍)
        original_image = self.animation_frames[self.frame_index]
        aspect_ratio = original_image.get_width() / original_image.get_height()
        new_height = 150
        new_width = int(new_height * aspect_ratio)
        
        # 縮放所有影格
        for i, frame in enumerate(self.animation_frames):
            self.animation_frames[i] = pygame.transform.scale(frame, (new_width, new_height))

        self.image = self.animation_frames[self.frame_index]
        self.rect = self.image.get_rect(centery=y_position)
        self.rect.left = SCREEN_WIDTH # 從畫面右邊外面開始
        
        self.speed = 15 # 設定為一個較快的速度

        # 創建火焰特效
        fire_image = assets.get_image('skill3_damage')
        # 火焰高度與車子相同，寬度為螢幕寬度
        fire_height = self.rect.height
        self.fire_surface = pygame.transform.scale(fire_image, (SCREEN_WIDTH, fire_height))
        self.fire_surface.set_alpha(128) # 設定約 50% 透明度 (255 * 0.5)
        self.fire_rect = self.fire_surface.get_rect(centery=y_position)
        # 火焰跟在車子後面
        self.fire_rect.left = self.rect.right
        self.fire_mask = pygame.mask.from_surface(self.fire_surface)

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update_time > self.animation_speed_ms:
            self.last_update_time = now
            self.frame_index = (self.frame_index + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.frame_index]

    def update(self):
        # 向左移動
        self.rect.x -= self.speed
        # 火焰跟在車子後面
        self.fire_rect.left = self.rect.right
        
        self.animate()
        
        # --- ↓↓↓ 【【【本次修正：將銷毀條件改為判斷火焰的位置】】】 ↓↓↓ ---
        # 如果火焰的右邊界完全移出畫面左邊，才自我銷毀
        if self.fire_rect.right < 0:
            self.kill()
        # --- ↑↑↑ 【【【本次修正】】】 ↑↑↑ ---
            
    def draw_fire(self, screen):
        """一個額外的繪製方法，用來繪製火焰"""
        screen.blit(self.fire_surface, self.fire_rect)