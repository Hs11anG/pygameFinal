# monster_manager.py
import pygame
import random
from settings import *
from monster import Monster

class MonsterManager:
    def __init__(self, level_data, gameplay_scene):
        self.monsters = pygame.sprite.Group()
        self.scene = gameplay_scene # GameplayScene 的引用
        
        # 建立待生成怪物的列表
        self.spawn_list = []
        spawns = level_data.get('spawns', {})
        for monster_type, count in spawns.items():
            self.spawn_list.extend([monster_type] * count)
        
        random.shuffle(self.spawn_list)
        
        # 計算平均生成間隔
        self.total_monsters_to_spawn = len(self.spawn_list)
        level_duration_ms = level_data.get('duration', 60) * 1000
        
        if self.total_monsters_to_spawn > 0:
            self.spawn_interval = level_duration_ms / self.total_monsters_to_spawn
        else:
            self.spawn_interval = float('inf')

        # ↓↓↓ 【【【這就是補上的關鍵程式碼】】】 ↓↓↓
        # 初始化生成計時器
        self.last_spawn_time = pygame.time.get_ticks()

    def choose_spawn_pos(self):
        """在地圖四個邊緣外側隨機選擇一個生成點"""
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            return (random.randint(0, SCREEN_WIDTH), -50)
        elif side == 'bottom':
            return (random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 50)
        elif side == 'left':
            return (-50, random.randint(0, SCREEN_HEIGHT))
        else: # right
            return (SCREEN_WIDTH + 50, random.randint(0, SCREEN_HEIGHT))

    def update(self):
        now = pygame.time.get_ticks()
        
        # 現在這一行可以正常運作了
        if now - self.last_spawn_time > self.spawn_interval and self.spawn_list:
            self.last_spawn_time = now
            monster_to_spawn = self.spawn_list.pop()
            spawn_pos = self.choose_spawn_pos()
            # 建立怪物時，傳入攻擊目標 (protection_target)
            new_monster = Monster(spawn_pos, monster_to_spawn, self.scene.protection_target)
            self.monsters.add(new_monster)
    
        self.monsters.update()

    def draw(self, screen):
        self.monsters.draw(screen)
        for monster in self.monsters:
            monster.draw_health_bar(screen)
            # (驚嘆號的邏輯已被移除，因為怪物現在總是有目標)