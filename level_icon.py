# level_icon.py
import pygame
from asset_manager import assets
from settings import WHITE

class LevelIcon(pygame.sprite.Sprite):
    def __init__(self, position, level_number, is_unlocked):
        super().__init__()
        self.level_number = level_number
        self.is_unlocked = is_unlocked

        # 載入原始圖片
        original_image = assets.get_image(f'level{self.level_number}')

        # 【【【在這裡設定你想要的大小】】】
        new_size = (100, 100)  # 例如：寬 100 像素，高 100 像素，你可以改成你想要的大小

        # 縮放圖片
        self.image = pygame.transform.scale(original_image, new_size)
        self.rect = self.image.get_rect(midbottom=position)

        self.interaction_text = ""

    def update(self, player):
        """檢查與玩家的距離，並設定提示文字"""
        distance = pygame.Vector2(self.rect.center).distance_to(player.rect.center)
        if distance < 60: # 互動範圍
            if self.is_unlocked:
                self.interaction_text = "按E進入關卡"
            else:
                self.interaction_text = "尚未解鎖"
        else:
            self.interaction_text = ""
            
    def draw_ui(self, screen):
        """繪製提示文字"""
        if self.interaction_text:
            font = assets.get_font('ui')
            text_surf = font.render(self.interaction_text, True, WHITE)
            text_rect = text_surf.get_rect(midbottom=self.rect.midtop)
            screen.blit(text_surf, text_rect)