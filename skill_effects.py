# skill_effects.py
import pygame
from asset_manager import assets
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class RescueSkill(pygame.sprite.Sprite):
    def __init__(self, y_position, player):
        super().__init__()
        
        self.animation_frames = [
            assets.get_image('skill3_a1'),
            assets.get_image('skill3_a2')
        ]
        self.frame_index = 0
        self.last_update_time = pygame.time.get_ticks()
        self.animation_speed_ms = 150

        original_image = self.animation_frames[self.frame_index]
        aspect_ratio = original_image.get_width() / original_image.get_height()
        new_height = 150
        new_width = int(new_height * aspect_ratio)
        
        for i, frame in enumerate(self.animation_frames):
            self.animation_frames[i] = pygame.transform.scale(frame, (new_width, new_height))

        self.image = self.animation_frames[self.frame_index]
        self.rect = self.image.get_rect(centery=y_position)
        self.rect.left = SCREEN_WIDTH
        
        # --- ↓↓↓ 【【【本次修改：速度機制】】】 ↓↓↓ ---
        self.phase = 'approaching' # 'approaching' 或 'departing'
        self.base_speed = 15
        self.current_speed = self.base_speed
        self.player_speed_multiplier = player.rescue_skill_speed_multiplier
        # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---

        fire_image = assets.get_image('skill3_damage')
        fire_height = self.rect.height
        self.fire_surface = pygame.transform.scale(fire_image, (SCREEN_WIDTH, fire_height))
        self.fire_surface.set_alpha(128)
        self.fire_rect = self.fire_surface.get_rect(centery=y_position)
        self.fire_rect.left = self.rect.right
        self.fire_mask = pygame.mask.from_surface(self.fire_surface)

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update_time > self.animation_speed_ms:
            self.last_update_time = now
            self.frame_index = (self.frame_index + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.frame_index]

    # --- ↓↓↓ 【【【本次新增：切換階段的方法】】】 ↓↓↓ ---
    def switch_to_departing_phase(self):
        """由外部呼叫，用來切換到第二階段速度"""
        if self.phase == 'approaching':
            self.phase = 'departing'
            self.current_speed = self.base_speed * self.player_speed_multiplier
            print(f"救援車輛進入第二階段，速度變為: {self.current_speed}")
    # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---

    def update(self):
        self.rect.x -= self.current_speed
        self.fire_rect.left = self.rect.right
        
        self.animate()
        
        if self.fire_rect.right < 0:
            self.kill()
            
    def draw_fire(self, screen):
        screen.blit(self.fire_surface, self.fire_rect)