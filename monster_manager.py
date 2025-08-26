# monster_manager.py
import pygame
import random
from settings import *
from monster import Monster

class MonsterManager:
    def __init__(self, level_data, gameplay_scene):
        self.monsters = pygame.sprite.Group()
        self.scene = gameplay_scene
        # --- ↓↓↓ 【【【本次修改：儲存關卡加權】】】 ↓↓↓ ---
        self.level_multiplier = level_data.get('level_multiplier', 1.0)
        # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---
        
        self.spawn_list = []
        spawns = level_data.get('spawns', {})
        for monster_type, count in spawns.items():
            self.spawn_list.extend([monster_type] * count)
        
        random.shuffle(self.spawn_list)
        
        self.total_monsters_to_spawn = len(self.spawn_list)
        level_duration_ms = level_data.get('duration', 60) * 1000
        
        if self.total_monsters_to_spawn > 0:
            self.spawn_interval = level_duration_ms / self.total_monsters_to_spawn
        else:
            self.spawn_interval = float('inf')

        self.last_spawn_time = pygame.time.get_ticks()

    def choose_spawn_pos(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            return (random.randint(0, SCREEN_WIDTH), -50)
        elif side == 'bottom':
            return (random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 50)
        elif side == 'left':
            return (-50, random.randint(0, SCREEN_HEIGHT))
        else:
            return (SCREEN_WIDTH + 50, random.randint(0, SCREEN_HEIGHT))

    def update(self):
        now = pygame.time.get_ticks()
        
        if now - self.last_spawn_time > self.spawn_interval and self.spawn_list:
            self.last_spawn_time = now
            monster_to_spawn = self.spawn_list.pop()
            spawn_pos = self.choose_spawn_pos()
            # --- ↓↓↓ 【【【本次修改：建立怪物時傳入關卡加權】】】 ↓↓↓ ---
            new_monster = Monster(spawn_pos, monster_to_spawn, self.scene.protection_target, self.level_multiplier)
            # --- ↑↑↑ 【【【本次修改】】】 ↑↑↑ ---
            self.monsters.add(new_monster)
    
        self.monsters.update()

    def draw(self, screen):
        self.monsters.draw(screen)
        for monster in self.monsters:
            monster.draw_health_bar(screen)