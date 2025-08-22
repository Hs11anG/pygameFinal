# scenes/level_select_scene.py
import pygame
from settings import *
from scene_manager import Scene
from asset_manager import assets
from player import Player
from level_icon import LevelIcon
from save_manager import save_manager

class LevelSelectScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.background = assets.get_image('level_select_bg')
        self.walkable_mask = pygame.mask.from_surface(assets.get_image('level_select_mask'))
        
        # 這個場景有自己的玩家和 Sprite Group
        self.player = Player(start_pos=(156, 668), level_number=1) # level_number 暫時用1
        self.player_group = pygame.sprite.Group(self.player)
        self.level_icons = pygame.sprite.Group()

        self.can_interact = True

    def setup_level_icons(self):
        """根據存檔資料建立關卡圖標"""
        self.level_icons.empty()
        # 假設關卡圖標位置固定
        positions = {1: (630, 435), 2: (790, 360), 3: (930, 325)}
        for level_num, pos in positions.items():
            if level_num in LEVELS: # 確保 settings 中有這個關卡
                is_unlocked = save_manager.is_level_unlocked(level_num)
                icon = LevelIcon(pos, level_num, is_unlocked)
                self.level_icons.add(icon)

    def handle_events(self, events):
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walkable_mask)

        # 處理 E 鍵互動
        if keys[pygame.K_e]:
            if self.can_interact:
                for icon in self.level_icons:
                    if icon.interaction_text == "按E進入關卡":
                        gameplay_scene = self.manager.scenes['gameplay']
                        gameplay_scene.load_level(icon.level_number)
                        self.manager.switch_to_scene('gameplay')
                        break
                self.can_interact = False
        else:
            self.can_interact = True
            
        for event in events:
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.switch_to_scene('main_menu')

    def update(self):
        self.level_icons.update(self.player)

    def draw(self, screen):
        screen.blit(self.background, (0,0))
        
        self.level_icons.draw(screen)
        
        for icon in self.level_icons:
            icon.draw_ui(screen)
        self.player_group.draw(screen)