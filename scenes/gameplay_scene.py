# scenes/gameplay_scene.py
import pygame
from settings import *
from scene_manager import Scene
from asset_manager import assets
from player import Player
from monster_manager import MonsterManager
from save_manager import save_manager
from projectile import BswordProjectile, BoardProjectile
from protection_target import ProtectionTarget

class GameplayScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.game_state = 'inactive'
        
        self.player_group = pygame.sprite.GroupSingle()
        self.target_group = pygame.sprite.GroupSingle()
        self.projectile_group = pygame.sprite.Group()
        self.monster_manager = None
        
        self.player = None
        self.protection_target = None
        self.background_image = None
        self.level_duration = 0
        self.level_start_time = 0
        self.victory_monster_limit = 0
        self.escaped_monsters_count = 0
        self.events = []
        self.current_level = 0

    def load_level(self, level_number):
        self.current_level = level_number
        level_data = LEVELS.get(level_number)
        if not level_data: return
        
        print(f"載入關卡 {level_number}: {level_data['name']}")
        
        self.player_group.empty()
        self.target_group.empty()
        self.projectile_group.empty()
        
        level_id = level_data['id']
        self.background_image = assets.get_image(f'{level_id}_bg')
        
        target_pos = level_data['protection_point']
        self.protection_target = ProtectionTarget(target_pos, level_number)
        self.target_group.add(self.protection_target)
        
        self.monster_manager = MonsterManager(level_data, self)

        spawn_point = level_data['player_spawn_point']
        self.player = Player(start_pos=spawn_point, level_number=level_number)
        self.player_group.add(self.player)
        
        self.level_duration = level_data.get('duration', 60) * 1000
        self.victory_monster_limit = level_data.get('victory_monster_limit', 20)
        self.level_start_time = pygame.time.get_ticks()
        self.escaped_monsters_count = 0
        self.game_state = 'playing'

    def handle_events(self, events):
        self.events = events
        for event in self.events:
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.switch_to_scene('main_menu')
                
    def check_collisions(self):
        if not self.monster_manager: return
        now = pygame.time.get_ticks()

        # 飛行物 vs 怪物
        possible_hits = pygame.sprite.groupcollide(
            self.projectile_group, 
            self.monster_manager.monsters, 
            False, False
        )
        for projectile, monsters_hit in possible_hits.items():
            for monster in monsters_hit:
                if pygame.sprite.collide_mask(projectile, monster):
                    if isinstance(projectile, BswordProjectile):
                        monster.health -= projectile.damage
                        projectile.kill() 
                        if monster.health <= 0: monster.kill()
                        break
                    elif isinstance(projectile, BoardProjectile):
                        if projectile.state == 'outbound':
                            projectile.start_spinning()
                        last_hit_time = projectile.hit_cooldowns.get(monster, 0)
                        if now - last_hit_time > 1000:
                            monster.health -= projectile.damage
                            projectile.hit_cooldowns[monster] = now
                            if monster.health <= 0: monster.kill()

        # 怪物 vs 保護目標
        if self.protection_target:
            hits = pygame.sprite.spritecollide(
                self.protection_target,
                self.monster_manager.monsters,
                False,
                pygame.sprite.collide_mask
            )
            for monster in hits:
                self.protection_target.take_damage(10)
                monster.knockback()

    def check_game_over(self):
        # 條件1: 保護目標被摧毀
        if self.protection_target and self.protection_target.current_health <= 0:
            self.game_state = 'defeat'
            end_scene = self.manager.scenes['end_level']
            end_scene.setup('defeat', self.current_level)
            self.manager.switch_to_scene('end_level')
            return

        # 條件2: 時間到
        elapsed_time = pygame.time.get_ticks() - self.level_start_time
        if elapsed_time > self.level_duration:
            remaining_monsters = len(self.monster_manager.monsters)
            total_failed_monsters = self.escaped_monsters_count + remaining_monsters
            
            end_scene = self.manager.scenes['end_level']
            if total_failed_monsters < self.victory_monster_limit:
                self.game_state = 'victory'
                save_manager.unlock_next_level(self.current_level)
                end_scene.setup('victory', self.current_level)
            else:
                self.game_state = 'defeat'
                end_scene.setup('defeat', self.current_level)
            
            self.manager.switch_to_scene('end_level')

    def draw_hud(self, screen):
        font = assets.get_font('ui')
        # (時間)
        elapsed_time = pygame.time.get_ticks() - self.level_start_time
        remaining_time = max(0, self.level_duration - elapsed_time) / 1000
        time_text = f"Time: {remaining_time:.1f}"
        time_surf = font.render(time_text, True, WHITE)
        screen.blit(time_surf, (SCREEN_WIDTH - time_surf.get_width() - 20, 20))
        # (剩餘怪物)
        remaining_monsters = len(self.monster_manager.monsters) if self.monster_manager else 0
        monsters_text = f"Remaining: {remaining_monsters}"
        monsters_surf = font.render(monsters_text, True, WHITE)
        screen.blit(monsters_surf, (SCREEN_WIDTH - monsters_surf.get_width() - 20, 60))
        # (逃跑數量)
        escaped_text = f"Escaped: {self.escaped_monsters_count}"
        escaped_surf = font.render(escaped_text, True, WHITE)
        screen.blit(escaped_surf, (SCREEN_WIDTH - escaped_surf.get_width() - 20, 100))
        # (保護目標血量)
        if self.protection_target:
            target_health_text = f"Target HP: {self.protection_target.current_health}"
            target_health_surf = font.render(target_health_text, True, (0, 255, 255))
            screen.blit(target_health_surf, (20, 20))

    def update(self):
        if self.game_state == 'playing':
            keys = pygame.key.get_pressed()
            
            if self.player:
                # ↓↓↓ 【【【這就是本次的核心修改】】】 ↓↓↓
                # 玩家不再需要 walkable_mask 和 weapon_group
                self.player.update(keys, self.events, self.projectile_group)
            
            if self.monster_manager:
                self.monster_manager.update()
                
            self.projectile_group.update()
            
            self.check_collisions()
            self.check_game_over()

    def draw(self, screen):
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill((10, 20, 50))
        
        self.target_group.draw(screen)
        if self.monster_manager:
            self.monster_manager.draw(screen)
        self.projectile_group.draw(screen)
        self.player_group.draw(screen)

        if self.player:
            self.player.draw_ui(screen)
        
        if self.game_state == 'playing':
            self.draw_hud(screen)