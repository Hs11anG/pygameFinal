# main.py
import pygame
from settings import *
from scene_manager import SceneManager
from asset_manager import assets
from settings import MONSTER_DATA

# 【【【修正：引入所有場景類別】】】
from scenes.main_menu_scene import MainMenuScene
from scenes.gameplay_scene import GameplayScene
from scenes.level_select_scene import LevelSelectScene
from scenes.end_level_scene import EndLevelScene
from scenes.save_slot_scene import SaveSlotScene


class Game:
    """
    遊戲主迴圈與場景管理
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("府 城 淨 化 錄")
        self.clock = pygame.time.Clock()

        # 【【【修正：載入資源】】】
        # 遊戲開始前，先載入所有資源
        self.load_assets()

        # 【【【修正：建立場景管理器】】】
        # 建立所有場景的實例
        scenes = {
            'main_menu': MainMenuScene(None),
            'gameplay': GameplayScene(None),
            'level_select': LevelSelectScene(None),
            'end_level': EndLevelScene(None),
            'save_slot': SaveSlotScene(None)
        }
        
        # --- ↓↓↓ 【【【本次修改】】】 ↓↓↓ ---
        # 將參數的順序對調，使其符合 SceneManager 的 __init__ 定義
        self.scene_manager = SceneManager('main_menu', scenes)
        # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---

        # 將場景管理器的實例回傳給各個場景，以便他們可以呼叫 switch_to_scene
        for scene in scenes.values():
            scene.manager = self.scene_manager

    def load_assets(self):
        """
        載入所有遊戲資源
        """
        # 載入圖片
        assets.load_image('main_menu_bg', 'assets/images/GameStart.png')
        assets.load_image('level_select_bg', 'assets/images/level_choose_bg.png')
        assets.load_image('level_select_mask', 'assets/images/level_choose_mask.png')
        assets.load_image('pier_assault_bg', 'assets/images/pier_background.png')
        assets.load_image('pier_assault_2_bg', 'assets/images/pier2_background.png')
        assets.load_image('player', 'assets/images/player.png')
        assets.load_image('bsword', 'assets/images/bsword.png')
        assets.load_image('board', 'assets/images/board.png')
        assets.load_image('bsword_heavy', 'assets/images/bsword.png') # 重型竹簡劍暫用同個圖
        assets.load_image('gbird_alpha', 'assets/images/gbird_alpha.png')
        assets.load_image('gbird_beta', 'assets/images/gbird_beta.png')
        assets.load_image('solarpanel_beta', 'assets/images/solarPanel_beta.png')
        assets.load_image('protect_level1', 'assets/images/protect_level1.png')
        assets.load_image('protect_level2', 'assets/images/protect_level2.png')
        assets.load_image('protect_level3', 'assets/images/protect_level3.png')
        assets.load_image('level1_icon', 'assets/images/level1.png')
        assets.load_image('level2_icon', 'assets/images/level2.png')
        assets.load_image('level3_icon', 'assets/images/level3.png')
        assets.load_image('exclamation', 'assets/images/exclamation.png')
        # --- ↓↓↓ 【【【本次新增：載入技能圖示】】】 ↓↓↓ ---
        assets.load_image('skill1', 'assets/images/skill1.png')
        assets.load_image('skill2', 'assets/images/skill2.png')
        # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---
        
        # 載入怪物動畫
        for monster_id, data in MONSTER_DATA.items():
            folder_name = monster_id
            # 載入移動動畫
            if 'animation_frames' in data:
                for frame_name in data['animation_frames']:
                    path = f'assets/images/{folder_name}/{frame_name}.png'
                    assets.load_image(frame_name, path)
            # 載入死亡動畫
            if 'death_frames' in data:
                for frame_name in data['death_frames']:
                    path = f'assets/images/{folder_name}/{frame_name}.png'
                    assets.load_image(frame_name, path)
        
        # 載入字體
        assets.load_font('title', 'NotoSerifTC-ExtraBold.ttf', TITLE_FONT_SIZE)
        assets.load_font('menu', 'NotoSerifTC-Medium.ttf', MENU_FONT_SIZE)
        assets.load_font('ui', 'BoutiqueBitmap9x9_Bold_1.9.ttf', 40)
        assets.load_font('weapon_ui', 'BoutiqueBitmap9x9_Bold_1.9.ttf', 24)


    def run(self):
        while True:
            events = pygame.event.get()
            
            self.scene_manager.handle_events(events)
            self.scene_manager.update()
            self.scene_manager.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()