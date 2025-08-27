# scene_manager.py
import pygame
from player import Player
from save_manager import save_manager
# --- ↓↓↓ 【【【本次修改：引入 assets】】】 ↓↓↓ ---
from asset_manager import assets
# --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---

class Scene:
    def __init__(self, manager):
        self.manager = manager
    def handle_events(self, events):
        raise NotImplementedError
    def update(self):
        raise NotImplementedError
    def draw(self, screen):
        raise NotImplementedError

class SceneManager:
    def __init__(self, initial_scene_name, scenes):
        self.scenes = scenes
        self.current_scene = self.scenes[initial_scene_name]
        self.player = None

    def switch_to_scene(self, scene_name):
        if scene_name == 'main_menu':
            print("Returning to Main Menu, resetting states.")
            self.player = None 
            save_manager.current_save_slot = None
            save_manager.unlocked_levels = {1}
            save_manager.tutorial_completed = False

            # --- ↓↓↓ 【【【本次修改：透過 AssetManager 重播音樂】】】 ↓↓↓ ---
            # 直接命令 AssetManager 重新播放背景音樂
            assets.play_music('background', loops=-1)
            # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---

        self.current_scene = self.scenes[scene_name]
        
    def get_scene(self):
        return self.current_scene

    def update(self):
        self.current_scene.update()
        
    def draw(self, screen):
        self.current_scene.draw(screen)

    def handle_events(self, events):
        self.current_scene.handle_events(events)
        
    def start_new_run(self):
        self.player = Player(start_pos=(0, 0), level_number=1) 
        
    def get_player(self):
        return self.player
    
    def handle_events(self, events):
        # 讓 scene 的 handle_events 回傳布林值
        return self.current_scene.handle_events(events)