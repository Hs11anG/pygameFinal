# main.py
import pygame
from settings import *
from scene_manager import SceneManager
from scenes.main_menu_scene import MainMenuScene
from scenes.gameplay_scene import GameplayScene
from scenes.end_level_scene import EndLevelScene # <--- 1. 引入新場景
from asset_manager import assets

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Coast Guardian")

        print("--- Loading Assets ---")
        
        assets.load_font('title', "NotoSerifTC-Medium.ttf", TITLE_FONT_SIZE)
        assets.load_font('menu', "NotoSerifTC-Medium.ttf", MENU_FONT_SIZE)
        assets.load_font('ui',  "NotoSerifTC-Medium.ttf", 36)
        assets.load_font('weapon_ui', "NotoSerifTC-ExtraBold.ttf", 14)
        assets.load_image('main_menu_bg', 'assets/images/GameStart.png')
        
        # 2. 【修改】自動載入所有關卡資源
        for level_num, level_data in LEVELS.items():
            level_id = level_data['id']
            if 'background_image' in level_data:
                assets.load_image(f'{level_id}_bg', level_data['background_image'])
            if 'walkable_mask_image' in level_data:
                assets.load_image(f'{level_id}_walkable_mask', level_data['walkable_mask_image'])
        
        assets.load_image('player', 'assets/images/player.png')
        
        # 3. 【修改】自動載入所有怪物和武器圖片
        for monster_type, monster_data in MONSTER_DATA.items():
            assets.load_image(monster_type, monster_data['image_path'])
        
        assets.load_image('exclamation', 'assets/images/exclamation.png')

        for weapon_num, weapon_data in WEAPON_DATA.items():
            assets.load_image(weapon_data['id'], weapon_data['image_path'])

        print("--- Asset Loading Complete ---")

        self.clock = pygame.time.Clock()
        self.running = True

        scenes = {
            'main_menu': MainMenuScene,
            'gameplay': GameplayScene,
            'end_level': EndLevelScene # <--- 4. 註冊新場景
        }
        
        self.scene_manager = SceneManager(scenes, 'main_menu')

    def run(self):
        # ... (此方法不變)
        while self.running:
            self.clock.tick(FPS)
            events = pygame.event.get()
            self.scene_manager.handle_events(events)
            self.scene_manager.update()
            self.scene_manager.draw(self.screen)
            pygame.display.flip()
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()