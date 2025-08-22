# scenes/gameplay_scene.py
import pygame
from settings import *
from scene_manager import Scene
from asset_manager import assets
from player import Player
from monster_manager import MonsterManager
from weapon import Weapon
from save_manager import save_manager

class GameplayScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.game_state = 'inactive'
        self.player = None
        self.monster_manager = None
        self.all_sprites = pygame.sprite.Group()
        self.weapon_group = pygame.sprite.Group()
        self.projectile_group = pygame.sprite.Group()
        self.background_image = None
        self.walkable_mask = None
        self.level_duration = 0
        self.level_start_time = 0
        self.victory_monster_limit = 0
        self.escaped_monsters_count = 0
        self.events = []
        self.current_level = 0 # 【新增】記錄當前關卡編號

    def load_level(self, level_number):
        self.current_level = level_number # 記錄當前關卡
        level_data = LEVELS.get(level_number)
        if not level_data: return
        
        level_id = level_data['id']
        self.background_image = assets.get_image(f'{level_id}_bg')
        
        walkable_area_image = assets.get_image(f'{level_id}_walkable_mask')
        if walkable_area_image:
            self.walkable_mask = pygame.mask.from_surface(walkable_area_image)
            self.monster_manager = MonsterManager(self.walkable_mask, level_data, self)
        
        spawn_point = level_data['spawn_point']
        self.player = Player(start_pos=spawn_point, level_number=level_number)
        self.all_sprites.empty(); self.projectile_group.empty() # 清空舊物件
        self.all_sprites.add(self.player)
        
        self.weapon_group.empty()
        weapon_spawns = level_data.get('weapon_spawns', [])
        for weapon_type, position in weapon_spawns:
            self.weapon_group.add(Weapon(position, weapon_type))

        self.level_duration = level_data.get('duration', 60) * 1000
        self.victory_monster_limit = level_data.get('victory_monster_limit', 20)
        self.level_start_time = pygame.time.get_ticks()
        self.escaped_monsters_count = 0
        self.game_state = 'playing'

    def handle_events(self, events):
        # ... (此方法不變)
        self.events = events
        for event in self.events:
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.switch_to_scene('main_menu')
                
    def check_collisions(self):
        # ... (此方法不變)
        if not self.monster_manager: return
        possible_hits = pygame.sprite.groupcollide(self.projectile_group, self.monster_manager.monsters, False, False)
        for projectile, monsters_hit in possible_hits.items():
            for monster in monsters_hit:
                if pygame.sprite.collide_mask(projectile, monster):
                    monster.health -= projectile.damage
                    projectile.kill()
                    if monster.health <= 0: monster.kill()
                    break

    def check_game_over(self):
        elapsed_time = pygame.time.get_ticks() - self.level_start_time
        if elapsed_time > self.level_duration:
            remaining_monsters = len(self.monster_manager.monsters)
            total_failed_monsters = self.escaped_monsters_count + remaining_monsters
            
            end_scene = self.manager.scenes['end_level']
            if total_failed_monsters < self.victory_monster_limit:
                # 勝利時，更新當前存檔
                save_manager.unlock_next_level(self.current_level)
                # (注意：金幣功能尚未實作，所以暫時不更新金幣)
                # save_manager.update_current_save(...) 
                
                # 轉到結束畫面
                end_scene = self.manager.scenes['end_level']
                end_scene.setup('victory', self.current_level)
                self.manager.switch_to_scene('end_level')
            else:
                self.game_state = 'defeat'
                end_scene.setup('defeat', self.current_level)
            
            self.manager.switch_to_scene('end_level')

    def draw_hud(self, screen):
        # ... (此方法不變)
        font = assets.get_font('ui')
        elapsed_time = pygame.time.get_ticks() - self.level_start_time
        remaining_time = max(0, self.level_duration - elapsed_time) / 1000
        time_text = f"Time: {remaining_time:.1f}"
        time_surf = font.render(time_text, True, WHITE)
        screen.blit(time_surf, (SCREEN_WIDTH - time_surf.get_width() - 20, 20))
        remaining_monsters = len(self.monster_manager.monsters) if self.monster_manager else 0
        monsters_text = f"Remaining: {remaining_monsters}"
        monsters_surf = font.render(monsters_text, True, WHITE)
        screen.blit(monsters_surf, (SCREEN_WIDTH - monsters_surf.get_width() - 20, 60))
        escaped_text = f"Escaped: {self.escaped_monsters_count}"
        escaped_surf = font.render(escaped_text, True, WHITE)
        screen.blit(escaped_surf, (SCREEN_WIDTH - escaped_surf.get_width() - 20, 100))

    def update(self):
        """每幀更新所有遊戲物件的邏輯"""
        if self.game_state == 'playing':
            keys = pygame.key.get_pressed()
            
            # 【修改】將 player 傳給 weapon_group.update()
            if self.player:
                self.player.update(keys, self.events, self.walkable_mask, self.weapon_group, self.projectile_group)
                self.weapon_group.update(self.player) # 讓每個武器都能檢查與玩家的距離
            
            if self.monster_manager:
                self.monster_manager.update()
                
            self.projectile_group.update()
            
            self.check_collisions()
            self.check_game_over()

    def draw(self, screen):
        """將所有遊戲物件繪製到螢幕上"""
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill((10, 20, 50))
        
        self.weapon_group.draw(screen)
        
        if self.monster_manager:
            self.monster_manager.draw(screen)
        self.projectile_group.draw(screen)

        # 【修改】移除 player.draw_ui()，改為呼叫每個武器的 draw_ui()
        for weapon in self.weapon_group:
            weapon.draw_ui(screen)

        if self.game_state == 'playing':
            self.draw_hud(screen)
        self.all_sprites.draw(screen) # 畫玩家
        # (勝利/失敗畫面邏輯不變)