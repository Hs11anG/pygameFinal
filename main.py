# main.py
import pygame
from settings import *
from scene_manager import SceneManager
from asset_manager import assets
from settings import MONSTER_DATA

# 引入所有場景類別
from scenes.main_menu_scene import MainMenuScene
from scenes.gameplay_scene import GameplayScene
from scenes.level_select_scene import LevelSelectScene
from scenes.end_level_scene import EndLevelScene
from scenes.save_slot_scene import SaveSlotScene
from scenes.story_scene import StoryScene 

class Game:
    """
    遊戲主迴圈與場景管理
    """

    def __init__(self):
        pygame.init()
        # Mixer 的初始化已經移到 AssetManager 中
        pygame.key.stop_text_input()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("府 城 淨 化 錄")
        self.clock = pygame.time.Clock()

        # 載入所有遊戲資源 (圖片、字體、音樂)
        self.load_assets()

        # 命令 AssetManager 播放背景音樂
        assets.play_music('background', loops=-1, volume=0.5)

        # 建立所有場景的實例
        scenes = {
            'main_menu': MainMenuScene(None),
            'gameplay': GameplayScene(None),
            'level_select': LevelSelectScene(None),
            'end_level': EndLevelScene(None),
            'save_slot': SaveSlotScene(None),
            'story': StoryScene(None)
        }
        
        # 建立場景管理器，並設定初始場景
        self.scene_manager = SceneManager('main_menu', scenes)

        # 將場景管理器的實例回傳給各個場景
        for scene in scenes.values():
            scene.manager = self.scene_manager

    def load_assets(self):
        """
        命令 AssetManager 載入所有遊戲資源
        """
        # 載入圖片
        assets.load_image('main_menu_bg', 'assets/images/GameStart.png')
        assets.load_image('level_select_bg', 'assets/images/level_choose_bg.png')
        assets.load_image('level_select_mask', 'assets/images/level_choose_mask.png')
        assets.load_image('pier_assault_bg', 'assets/images/pier_background.png')
        assets.load_image('pier_assault_2_bg', 'assets/images/pier2_background.png')
        assets.load_image('pier_assault_3_bg', 'assets/images/pier3_background.png')
        assets.load_image('player', 'assets/images/player.png')
        assets.load_image('bsword', 'assets/images/bsword.png')
        assets.load_image('board', 'assets/images/board.png')
        assets.load_image('bsword_heavy', 'assets/images/bsword.png')
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
        assets.load_image('skill1', 'assets/images/skill1.png')
        assets.load_image('skill2', 'assets/images/skill2.png')
        assets.load_image('skill3_icon', 'assets/images/skill3_a1.png')
        assets.load_image('skill3_a1', 'assets/images/skill3_a1.png')
        assets.load_image('skill3_a2', 'assets/images/skill3_a2.png')
        assets.load_image('skill3_damage', 'assets/images/skill3_damage.png')
        
        # 載入怪物動畫
        for monster_id, data in MONSTER_DATA.items():
            folder_name = monster_id
            if 'animation_frames' in data:
                for frame_name in data['animation_frames']:
                    path = f'assets/images/{folder_name}/{frame_name}.png'
                    assets.load_image(frame_name, path)
            if 'death_frames' in data:
                for frame_name in data['death_frames']:
                    path = f'assets/images/{folder_name}/{frame_name}.png'
                    assets.load_image(frame_name, path)
        
        # 載入字體
        assets.load_font('title', 'NotoSerifTC-ExtraBold.ttf', TITLE_FONT_SIZE)
        assets.load_font('menu', 'NotoSerifTC-Medium.ttf', MENU_FONT_SIZE)
        assets.load_font('des', 'NotoSerifTC-ExtraBold.ttf', 24)
        assets.load_font('ui', 'BoutiqueBitmap9x9_Bold_1.9.ttf', 40)
        assets.load_font('weapon_ui', 'BoutiqueBitmap9x9_Bold_1.9.ttf', 20)

        # 載入音樂
        assets.load_music('background', 'assets/sounds/BGmusic.mp3')

    def run(self):
            """
            遊戲主迴圈
            """
            running = True # <--- 新增一個 running 變數
            while running: # <--- 將 while True 改成 while running
                # 取得所有事件
                events = pygame.event.get()

                # --- ↓↓↓ 【【【修改部分】】】 ↓↓↓ ---
                # 將事件交給當前的場景處理
                # 讓 handle_events 可以回傳一個值來決定是否繼續執行
                running = self.scene_manager.handle_events(events)
                if not running:
                    break # 如果場景說要結束，就直接跳出迴圈
                # --- ↑↑↑ 【【【修改部分】】】 ↑↑↑ ---

                # 更新當前場景的狀態
                self.scene_manager.update()
                # 繪製當前的場景
                self.scene_manager.draw(self.screen)
                
                # 更新螢幕顯示
                pygame.display.flip()
                # 控制遊戲幀率
                self.clock.tick(FPS)
            
            # --- ↓↓↓ 【【【新增部分】】】 ↓↓↓ ---
            # 將退出邏輯統一放到迴圈外面
            pygame.quit()
            # exit() # 在 .py 檔中執行時可以不加，打包時 sys.exit() 比較保險
            import sys
            sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()