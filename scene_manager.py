# scene_manager.py
import pygame
from player import Player

# --- ↓↓↓ 【【【新增缺失的 Scene 類別】】】 ↓↓↓ ---
class Scene:
    """
    所有場景的基礎類別 (模板)。
    """
    def __init__(self, manager):
        self.manager = manager

    def handle_events(self, events):
        """處理該場景的事件"""
        raise NotImplementedError

    def update(self):
        """更新該場景的狀態"""
        raise NotImplementedError

    def draw(self, screen):
        """將該場景繪製到螢幕上"""
        raise NotImplementedError
# --- ↑↑↑ 【【【新增缺失的 Scene 類別】】】 ↑↑↑ ---

class SceneManager:
    def __init__(self, initial_scene_name, scenes):
        self.scenes = scenes
        self.current_scene = self.scenes[initial_scene_name]
        self.player = None

    def switch_to_scene(self, scene_name):
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
        """開始一輪新遊戲時，創建一個新的玩家"""
        self.player = Player(start_pos=(0, 0), level_number=1) 
        
    def get_player(self):
        """提供一個取得玩家物件的接口"""
        return self.player