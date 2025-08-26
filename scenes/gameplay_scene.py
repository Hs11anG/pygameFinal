# scenes/gameplay_scene.py
import pygame
import random
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
        
        self.kill_count = 0
        self.kills_for_upgrade = 10
        self.current_upgrade_choices = []
        self.upgrade_choice_rects = []
        
        self.pause_start_time = 0 

    def load_level(self, level_number):
        self.current_level = level_number
        level_data = LEVELS.get(level_number)
        if not level_data: return
        
        print(f"載入關卡 {level_number}: {level_data['name']}")
        
        self.player_group.empty()
        self.target_group.empty()
        self.projectile_group.empty()
        
        self.player = self.manager.get_player()
        if not self.player:
            print("警告：找不到玩家物件，將創建一個新的")
            self.manager.start_new_run()
            self.player = self.manager.get_player()

        self.player.reset_cooldowns()

        spawn_point = level_data['player_spawn_point']
        self.player.rect.midbottom = spawn_point
        self.player_group.add(self.player)

        level_id = level_data['id']
        self.background_image = assets.get_image(f'{level_id}_bg')
        
        target_pos = level_data['protection_point']
        self.protection_target = ProtectionTarget(target_pos, level_number)
        self.target_group.add(self.protection_target)
        
        self.monster_manager = MonsterManager(level_data, self)
        
        self.level_duration = level_data.get('duration', 60) * 1000
        self.victory_monster_limit = level_data.get('victory_monster_limit', 20)
        self.level_start_time = pygame.time.get_ticks()
        self.escaped_monsters_count = 0
        self.game_state = 'playing'
        
        self.kill_count = 0
        self.current_upgrade_choices = []
        self.upgrade_choice_rects = []

    def handle_events(self, events):
        self.events = events
        for event in self.events:
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.switch_to_scene('main_menu')
            
            if self.game_state == 'choosing_upgrade' and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, rect in enumerate(self.upgrade_choice_rects):
                        if rect.collidepoint(event.pos):
                            pause_duration = pygame.time.get_ticks() - self.pause_start_time
                            self.player.adjust_timers_for_pause(pause_duration)
                            self.level_start_time += pause_duration

                            chosen_upgrade = self.current_upgrade_choices[i]
                            self.player.apply_upgrade(chosen_upgrade)
                            self.game_state = 'playing'
                            self.current_upgrade_choices = []
                            self.upgrade_choice_rects = []
                            break
                
    def check_collisions(self):
        if not self.monster_manager: return

        possible_hits = pygame.sprite.groupcollide(
            self.projectile_group, 
            self.monster_manager.monsters, 
            False, False
        )
        for projectile, monsters_hit in possible_hits.items():
            for monster in monsters_hit:
                if pygame.sprite.collide_mask(projectile, monster):
                    # 【【【BUG修正：檢查 take_damage 的回傳值】】】
                    just_died = monster.take_damage(projectile.damage)
                    if just_died:
                        self.kill_count += 1
                    
                    if not isinstance(projectile, BoardProjectile):
                         projectile.kill()
                    break

        if self.protection_target:
            hits = pygame.sprite.spritecollide(
                self.protection_target,
                self.monster_manager.monsters,
                False,
                pygame.sprite.collide_mask
            )
            for monster in hits:
                if monster.state == 'alive': 
                    self.protection_target.take_damage(10)
                    monster.knockback()

    def check_game_over(self):
        if self.protection_target and self.protection_target.current_health <= 0:
            self.game_state = 'defeat'
            end_scene = self.manager.scenes['end_level']
            end_scene.setup('defeat', self.current_level)
            self.manager.switch_to_scene('end_level')
            return

        elapsed_time = pygame.time.get_ticks() - self.level_start_time
        if elapsed_time > self.level_duration:
            remaining_monsters = sum(1 for m in self.monster_manager.monsters if m.state == 'alive') if self.monster_manager else 0
            
            end_scene = self.manager.scenes['end_level']
            if remaining_monsters < self.victory_monster_limit:
                self.game_state = 'victory'
                save_manager.unlock_next_level(self.current_level)
                save_manager.save_game(self.player)
                end_scene.setup('victory', self.current_level)
            else:
                self.game_state = 'defeat'
                end_scene.setup('defeat', self.current_level)
            
            self.manager.switch_to_scene('end_level')

    def trigger_upgrade_choice(self):
        self.game_state = 'choosing_upgrade'
        self.kill_count -= self.kills_for_upgrade
        
        self.pause_start_time = pygame.time.get_ticks()

        available_upgrades = list(UPGRADE_DATA.keys())
        k = min(3, len(available_upgrades))
        if k > 0:
            chosen_keys = random.sample(available_upgrades, k=k)
            self.current_upgrade_choices = [UPGRADE_DATA[key] for key in chosen_keys]
        else:
            self.current_upgrade_choices = []

    def update(self):
        if self.game_state == 'playing':
            keys = pygame.key.get_pressed()
            if self.player:
                self.player.update(keys, self.events, self.projectile_group)
            if self.monster_manager:
                self.monster_manager.update()
            self.projectile_group.update()
            self.check_collisions()
            self.check_game_over()
            if self.kill_count >= self.kills_for_upgrade:
                self.trigger_upgrade_choice()

    def draw_hud(self, screen):
        font = assets.get_font('ui')
        elapsed_time = pygame.time.get_ticks() - self.level_start_time
        remaining_time = max(0, self.level_duration - elapsed_time) / 1000
        time_text = f"Time: {remaining_time:.1f}"
        time_surf = font.render(time_text, True, WHITE)
        screen.blit(time_surf, (SCREEN_WIDTH - time_surf.get_width() - 20, 20))
        
        kills_text = f"Kills: {self.kill_count}"
        kills_surf = font.render(kills_text, True, WHITE)
        screen.blit(kills_surf, (SCREEN_WIDTH - kills_surf.get_width() - 20, 60))
        
        if self.protection_target:
            target_health_text = f"Target HP: {self.protection_target.current_health}"
            target_health_surf = font.render(target_health_text, True, (0, 255, 255))
            screen.blit(target_health_surf, (20, 20))

    def draw_upgrade_ui(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title_font = assets.get_font('ui')
        desc_font = assets.get_font('weapon_ui')
        
        title_surf = title_font.render("選擇一項強化", True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, 150))
        screen.blit(title_surf, title_rect)
        
        card_width, card_height = 300, 250
        total_width = 3 * card_width + 2 * 50
        start_x = (SCREEN_WIDTH - total_width) / 2
        card_y = SCREEN_HEIGHT / 2 - card_height / 2
        
        self.upgrade_choice_rects = []
        for i, upgrade in enumerate(self.current_upgrade_choices):
            card_x = start_x + i * (card_width + 50)
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            self.upgrade_choice_rects.append(card_rect)
            
            pygame.draw.rect(screen, UI_BG_COLOR, card_rect, border_radius=10)
            pygame.draw.rect(screen, UI_BORDER_COLOR, card_rect, width=2, border_radius=10)
            
            name_surf = title_font.render(upgrade['name'], True, HOVER_COLOR)
            name_rect = name_surf.get_rect(center=(card_rect.centerx, card_rect.top + 60))
            screen.blit(name_surf, name_rect)

            desc_surf = desc_font.render(upgrade['description'], True, WHITE)
            desc_rect = desc_surf.get_rect(center=(card_rect.centerx, card_rect.top + 150))
            screen.blit(desc_surf, desc_rect)

    def draw_skill_ui(self, screen):
        if not self.player: return
        font = assets.get_font('ui')
        if not font: return
        now = pygame.time.get_ticks()
        
        current_cooldown = self.player.base_skill_1_cooldown * self.player.skill_cooldown_multiplier

        skill_1_icon_id = WEAPON_DATA[self.player.skill_1_weapon_type]['id']
        icon_image = assets.get_image(skill_1_icon_id)
        icon_image = pygame.transform.scale(icon_image, (50, 50))
        
        ui_base_x = SCREEN_WIDTH // 2
        ui_base_y = SCREEN_HEIGHT - 80
        icon_rect = icon_image.get_rect(center=(ui_base_x, ui_base_y))
        
        text_below = ""
        border_color = UI_BORDER_COLOR
        
        bg_rect = icon_rect.inflate(10, 10)
        pygame.draw.rect(screen, UI_BG_COLOR, bg_rect, border_radius=5)
        
        if self.player.skill_1_active:
            border_color = (255, 255, 0)
            text_below = "Active"
        else:
            is_ready = now - self.player.skill_1_cooldown_start_time > current_cooldown
            if is_ready:
                text_below = "Ready"

        pygame.draw.rect(screen, border_color, bg_rect, width=2, border_radius=5)
        screen.blit(icon_image, icon_rect)

        key_font = assets.get_font('weapon_ui')
        key_surf = key_font.render("1", True, WHITE)
        key_rect = key_surf.get_rect(center=(icon_rect.centerx, icon_rect.top - 15))
        screen.blit(key_surf, key_rect)
        
        if text_below:
            text_surf = key_font.render(text_below, True, border_color)
            text_rect = text_surf.get_rect(center=(icon_rect.centerx, icon_rect.bottom + 15))
            screen.blit(text_surf, text_rect)

        is_on_cooldown = now - self.player.skill_1_cooldown_start_time < current_cooldown
        if not self.player.skill_1_active and is_on_cooldown:
            cooldown_overlay = pygame.Surface(bg_rect.size, pygame.SRCALPHA) 
            cooldown_overlay.fill((0, 0, 0, 180))
            screen.blit(cooldown_overlay, bg_rect.topleft)
            remaining_cd = (current_cooldown - (now - self.player.skill_1_cooldown_start_time)) / 1000
            if remaining_cd > 0:
                cd_text = f"{remaining_cd:.1f}"
                cd_surf = font.render(cd_text, True, WHITE)
                cd_rect = cd_surf.get_rect(center=bg_rect.center)
                screen.blit(cd_surf, cd_rect)

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
            self.draw_skill_ui(screen)
        elif self.game_state == 'choosing_upgrade':
            self.draw_upgrade_ui(screen)