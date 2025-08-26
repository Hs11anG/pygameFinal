# level_icon.py
import pygame
from settings import *
from asset_manager import assets

class LevelIcon(pygame.sprite.Sprite):
    def __init__(self, position, level_number, is_unlocked):
        super().__init__()
        self.level_number = level_number
        self.is_unlocked = is_unlocked
        
        image_id = f'level{self.level_number}_icon'
        original_image = assets.get_image(image_id)
        
        if original_image is None:
            print(f"警告：找不到關卡圖示 '{image_id}'！將使用替代圖像。")
            original_image = pygame.Surface((80, 80))
            original_image.fill((255, 0, 255))

        if not self.is_unlocked:
            grayscale_image = original_image.copy()
            grayscale_image.fill((128, 128, 128), special_flags=pygame.BLEND_RGB_MULT)
            grayscale_image.set_alpha(150)
            original_image = grayscale_image
        
        new_size = (LEVEL_ICON_SIZE, LEVEL_ICON_SIZE)
        self.image = pygame.transform.scale(original_image, new_size)
        
        self.rect = self.image.get_rect(midbottom=position)
        self.rect.y += 30
        self.interaction_text = ""

    def update(self, player):
        if self.is_unlocked:
            distance_to_player = pygame.Vector2(self.rect.center).distance_to(player.rect.center)
            if distance_to_player < 80:
                self.interaction_text = "按E進入關卡"
            else:
                self.interaction_text = ""
        else:
            self.interaction_text = "尚未解鎖"

    def draw_ui(self, screen):
        font = assets.get_font('weapon_ui')
        if not font or not self.interaction_text:
            return
            
        color = GREY if not self.is_unlocked else HOVER_COLOR if self.interaction_text == "按E進入關卡" else WHITE
            
        text_surf = font.render(self.interaction_text, True, color)
        bg_rect = text_surf.get_rect(midtop=self.rect.midbottom, y=self.rect.bottom + 10).inflate(20, 10)
        
        pygame.draw.rect(screen, UI_BG_COLOR, bg_rect, border_radius=5)
        pygame.draw.rect(screen, UI_BORDER_COLOR, bg_rect, width=1, border_radius=5)
        screen.blit(text_surf, text_surf.get_rect(center=bg_rect.center))