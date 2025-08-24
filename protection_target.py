# protection_target.py
import pygame
from asset_manager import assets

class ProtectionTarget(pygame.sprite.Sprite):
    def __init__(self, position, level_number):
        super().__init__()
        
        # 根據關卡編號載入對應的保護目標圖片
        self.image = pygame.transform.scale(assets.get_image(f'protect_level{level_number}'), (100,100))
        self.rect = self.image.get_rect(center=position)
        
        # 保護目標的屬性
        self.max_health = 1000 # 假設最大血量
        self.current_health = self.max_health

    def take_damage(self, amount):
        self.current_health -= amount
        print(f"Target took {amount} damage, health: {self.current_health}")
        if self.current_health <= 0:
            self.current_health = 0
            print("Target has been destroyed!")
            # 可以在此處觸發遊戲失敗
            
    def draw_health_bar(self, screen):
        # (可選) 在此處為保護目標也加上血條
        pass