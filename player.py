# player.py
import pygame
from asset_manager import assets
from settings import *
from weapon import PROJECTILE_CLASSES
from projectile import BswordProjectile
from save_manager import save_manager

class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos, level_number):
        super().__init__()
        
        original_image = assets.get_image('player')
        player_size = LEVELS[level_number]['playersize']
        self.image = pygame.transform.scale(original_image, player_size)
        self.rect = self.image.get_rect(midbottom=start_pos)
        
        self.base_speed = 5
        self.base_skill_1_duration = SKILL_DATA[1]['duration']
        self.base_skill_1_cooldown = SKILL_DATA[1]['cooldown']
        self.base_skill_2_duration = SKILL_DATA[2]['duration']
        self.base_skill_2_cooldown = SKILL_DATA[2]['cooldown']
        self.base_skill_3_cooldown = SKILL_DATA[3]['cooldown']

        self.speed_multiplier = 1.0
        self.skill_duration_bonus = 0
        self.skill_cooldown_multipliers = {1: 1.0, 2: 1.0, 3: 1.0}
        self.global_cooldown_multiplier = 1.0
        self.rescue_skill_speed_multiplier = 1.0
        
        self.tactical_duration_bonus = {1: 0, 2: 0}
        self.tactical_damage_multiplier = {1: 1.0, 2: 1.0, 3: 1.0}

        self.weapon_data = {k: v.copy() for k, v in WEAPON_DATA.items()}
        self.speed = self.base_speed
        self.default_weapon_type = 1
        self.last_shot_time = {}
        
        self.skill_1_weapon_type = 2
        self.skill_1_active = False
        self.skill_1_activation_time = 0
        
        self.skill_2_active = False
        self.skill_2_activation_time = 0
        
        self.reset_cooldowns()
        self.can_move = True

    def reset_cooldowns(self):
        print("所有技能冷卻時間與狀態已重置！")
        now = pygame.time.get_ticks()
        
        self.skill_1_cooldown_start_time = now - (self.base_skill_1_cooldown * self.skill_cooldown_multipliers[1])
        self.skill_2_cooldown_start_time = now - (self.base_skill_2_cooldown * self.skill_cooldown_multipliers[2])
        self.skill_3_cooldown_start_time = now - (self.base_skill_3_cooldown * self.skill_cooldown_multipliers[3])
        self.last_shot_time = {}

        self.skill_1_active = False
        self.skill_1_activation_time = 0
        self.skill_2_active = False
        self.skill_2_activation_time = 0

        self.tactical_duration_bonus = {1: 0, 2: 0}

    def reset_tactical_bonuses(self):
        self.tactical_duration_bonus = {1: 0, 2: 0}
        self.tactical_damage_multiplier = {1: 1.0, 2: 1.0, 3: 1.0}
        print("已重置所有戰術性(臨時)加成。")

    def adjust_timers_for_pause(self, pause_duration):
        if self.skill_1_activation_time > 0: self.skill_1_activation_time += pause_duration
        if self.skill_2_activation_time > 0: self.skill_2_activation_time += pause_duration
        if self.skill_1_cooldown_start_time != float('inf'): self.skill_1_cooldown_start_time += pause_duration
        if self.skill_2_cooldown_start_time != float('inf'): self.skill_2_cooldown_start_time += pause_duration
        if self.skill_3_cooldown_start_time != float('inf'): self.skill_3_cooldown_start_time += pause_duration
        for weapon_type in self.last_shot_time: self.last_shot_time[weapon_type] += pause_duration

    def to_dict(self):
        return {
            'speed_multiplier': self.speed_multiplier,
            'skill_duration_bonus': self.skill_duration_bonus,
            'skill_cooldown_multipliers': {str(k): v for k, v in self.skill_cooldown_multipliers.items()},
            'global_cooldown_multiplier': self.global_cooldown_multiplier,
            'weapon_data': self.weapon_data,
            'rescue_skill_speed_multiplier': self.rescue_skill_speed_multiplier
        }

    def from_dict(self, data):
        self.speed_multiplier = data.get('speed_multiplier', 1.0)
        self.skill_duration_bonus = data.get('skill_duration_bonus', 0)
        
        saved_multipliers = data.get('skill_cooldown_multipliers', {})
        self.skill_cooldown_multipliers = {int(k): v for k, v in saved_multipliers.items()}
        for i in range(1, 4):
            if i not in self.skill_cooldown_multipliers:
                self.skill_cooldown_multipliers[i] = 1.0

        self.global_cooldown_multiplier = data.get('global_cooldown_multiplier', 1.0)
        self.rescue_skill_speed_multiplier = data.get('rescue_skill_speed_multiplier', 1.0)
        
        weapon_data_from_json = data.get('weapon_data', {})
        self.weapon_data = {int(k): v for k, v in weapon_data_from_json.items()}
        
        if not self.weapon_data: self.weapon_data = {k: v.copy() for k, v in WEAPON_DATA.items()}
        self.speed = self.base_speed * self.speed_multiplier

    def apply_upgrade(self, upgrade_data):
        upgrade_type = upgrade_data['type']
        print(f"套用升級: {upgrade_data['name']}")

        if upgrade_data['category'] == 'tactical':
            if upgrade_type == 'reset_cooldown':
                skill_id = upgrade_data['skill_id']
                now = pygame.time.get_ticks()
                if skill_id == 1 or skill_id == 'all': self.skill_1_cooldown_start_time = now - (self.base_skill_1_cooldown * self.skill_cooldown_multipliers[1])
                if skill_id == 2 or skill_id == 'all': self.skill_2_cooldown_start_time = now - (self.base_skill_2_cooldown * self.skill_cooldown_multipliers[2])
                if skill_id == 3 or skill_id == 'all': self.skill_3_cooldown_start_time = now - (self.base_skill_3_cooldown * self.skill_cooldown_multipliers[3])
            
            elif upgrade_type == 'add_duration':
                skill_id = upgrade_data['skill_id']
                value = upgrade_data['value']
                if skill_id in self.tactical_duration_bonus:
                    self.tactical_duration_bonus[skill_id] += value

            elif 'weapon_id' in upgrade_data and upgrade_type == 'multiply':
                weapon_id = upgrade_data['weapon_id']
                if weapon_id in self.tactical_damage_multiplier:
                    self.tactical_damage_multiplier[weapon_id] *= upgrade_data['value']

        elif upgrade_data['category'] == 'permanent':
            stat = upgrade_data['stat']
            value = upgrade_data['value']
            if stat == 'skill_cooldown':
                skill_id = upgrade_data['skill_id']
                if skill_id in self.skill_cooldown_multipliers:
                    self.skill_cooldown_multipliers[skill_id] *= value
            elif 'weapon_id' in upgrade_data:
                if upgrade_type == 'add': self.weapon_data[upgrade_data['weapon_id']][stat] += value
            elif stat == 'rescue_skill_speed':
                self.rescue_skill_speed_multiplier *= value

    def move(self, keys, mask=None):
        if not self.can_move: 
            return
        
        dx, dy = 0, 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += self.speed
        if mask:
            if dx != 0:
                self.rect.x += dx
                if not (mask.get_at(self.rect.bottomleft) > 0 and mask.get_at(self.rect.bottomright) > 0): self.rect.x -= dx 
            if dy != 0:
                self.rect.y += dy
                if not (mask.get_at(self.rect.bottomleft) > 0 and mask.get_at(self.rect.bottomright) > 0): self.rect.y -= dy
        else:
            self.rect.x += dx; self.rect.y += dy
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def shoot(self, target_pos, projectile_group):
        now = pygame.time.get_ticks()
        current_weapon_type = self.skill_1_weapon_type if self.skill_1_active else self.default_weapon_type
        weapon_data = self.weapon_data.get(current_weapon_type)
        if not weapon_data: return
        cooldown = (weapon_data['cooldown'] * 1000) * self.global_cooldown_multiplier
        last_shot = self.last_shot_time.get(current_weapon_type, 0)
        if now - last_shot > cooldown:
            self.last_shot_time[current_weapon_type] = now
            ProjectileClass = PROJECTILE_CLASSES.get(weapon_data.get('projectile_class_name'))
            if ProjectileClass:
                new_projectile = ProjectileClass(self.rect.center, target_pos, current_weapon_type)
                
                base_damage = weapon_data['damage']
                tactical_multiplier = self.tactical_damage_multiplier.get(current_weapon_type, 1.0)
                new_projectile.damage = base_damage * tactical_multiplier
                
                if self.skill_2_active and isinstance(new_projectile, BswordProjectile):
                    new_projectile.piercing = True
                projectile_group.add(new_projectile)
    
    def activate_skill_1(self):
        if self.skill_2_active: return
        now = pygame.time.get_ticks()
        cooldown = self.base_skill_1_cooldown * self.skill_cooldown_multipliers[1]
        if now - self.skill_1_cooldown_start_time >= cooldown:
            self.skill_1_active = True
            self.skill_1_activation_time = now
            self.skill_1_cooldown_start_time = float('inf') 
            print("技能 1 已啟用: 轉型正義！")

    def activate_skill_2(self):
        if self.skill_1_active: return
        now = pygame.time.get_ticks()
        cooldown = self.base_skill_2_cooldown * self.skill_cooldown_multipliers[2]
        if now - self.skill_2_cooldown_start_time >= cooldown:
            self.skill_2_active = True
            self.skill_2_activation_time = now
            self.skill_2_cooldown_start_time = float('inf') 
            print("技能 2 已啟用: 融會貫通！")
            
    def activate_skill_3(self, gameplay_scene):
        if self.skill_1_active or self.skill_2_active: return
        if not save_manager.is_level_unlocked(3): return
        now = pygame.time.get_ticks()
        cooldown = self.base_skill_3_cooldown * self.skill_cooldown_multipliers[3]
        if now - self.skill_3_cooldown_start_time >= cooldown:
            if gameplay_scene.spawn_rescue_skill():
                self.skill_3_cooldown_start_time = now
                print("技能 3 已啟用: 搏命救援！")

    def update_skills(self):
        now = pygame.time.get_ticks()
        if self.skill_1_active:
            duration = self.base_skill_1_duration + self.skill_duration_bonus + self.tactical_duration_bonus[1]
            if now - self.skill_1_activation_time > duration:
                self.skill_1_active = False
                self.skill_1_cooldown_start_time = now
                self.tactical_duration_bonus[1] = 0
        if self.skill_2_active:
            duration = self.base_skill_2_duration + self.tactical_duration_bonus[2]
            if now - self.skill_2_activation_time > duration:
                self.skill_2_active = False
                self.skill_2_cooldown_start_time = now
                self.tactical_duration_bonus[2] = 0

    def update(self, keys, events, gameplay_scene, projectile_group, mask=None):
        self.move(keys, mask)
        
        if keys[pygame.K_1]: self.activate_skill_1()
        if keys[pygame.K_2]: self.activate_skill_2()
        if keys[pygame.K_3]: self.activate_skill_3(gameplay_scene)
        self.update_skills()
        if pygame.mouse.get_pressed()[0]: self.shoot(pygame.mouse.get_pos(), projectile_group)

    def draw_ui(self, screen):
        font = assets.get_font('weapon_ui')
        if not font: return
        if self.skill_1_active:
            now = pygame.time.get_ticks()
            duration = self.base_skill_1_duration + self.skill_duration_bonus + self.tactical_duration_bonus[1]
            remaining = (duration - (now - self.skill_1_activation_time)) / 1000
            if remaining < 0: return
            text_surf = font.render(f"{remaining:.1f}s", True, (255, 255, 0))
            bg_rect = text_surf.get_rect(midbottom=self.rect.midtop, y=self.rect.top - 40, x=self.rect.centerx - 50).inflate(8, 4)
            pygame.draw.rect(screen, UI_BG_COLOR, bg_rect, border_radius=3); pygame.draw.rect(screen, UI_BORDER_COLOR, bg_rect, width=1, border_radius=3)
            screen.blit(text_surf, text_surf.get_rect(center=bg_rect.center))
        if self.skill_2_active:
            now = pygame.time.get_ticks()
            duration = self.base_skill_2_duration + self.tactical_duration_bonus[2]
            remaining = (duration - (now - self.skill_2_activation_time)) / 1000
            if remaining < 0: return
            text_surf = font.render(f"{remaining:.1f}s", True, (0, 255, 255))
            bg_rect = text_surf.get_rect(midbottom=self.rect.midtop, y=self.rect.top - 40, x=self.rect.centerx + 10).inflate(8, 4)
            pygame.draw.rect(screen, UI_BG_COLOR, bg_rect, border_radius=3); pygame.draw.rect(screen, UI_BORDER_COLOR, bg_rect, width=1, border_radius=3)
            screen.blit(text_surf, text_surf.get_rect(center=bg_rect.center))