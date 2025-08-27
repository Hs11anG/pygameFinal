# save_manager.py
import json
import os
from datetime import datetime
from settings import LEVELS, WEAPON_DATA # 引入 LEVELS

MAX_SAVES = 3

class SaveManager:
    def __init__(self, save_folder='saves'):
        self.save_folder = save_folder
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)
        
        self.current_save_slot = None
        self.unlocked_levels = {1}
        # --- ↓↓↓ 【【【本次新增：新增教學旗標】】】 ↓↓↓ ---
        self.tutorial_completed = False
        # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---

    def create_new_save(self):
        saves = self.get_all_saves()
        if len(saves) >= MAX_SAVES:
            print("存檔已滿！")
            return

        now = datetime.now().strftime("%y_%m_%d_%H_%M_save")
        file_path = os.path.join(self.save_folder, f"{now}.json")
        
        new_save_data = {
            'unlocked_levels': [1],
            'player_stats': None,
            # --- ↓↓↓ 【【【本次新增：建立新存檔時，預設為未完成教學】】】 ↓↓↓ ---
            'tutorial_completed': False
            # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---
        }
        
        with open(file_path, 'w') as f:
            json.dump(new_save_data, f, indent=4)
            
        self.current_save_slot = file_path
        self.unlocked_levels = {1}
        # --- ↓↓↓ 【【【本次新增：設定當前狀態】】】 ↓↓↓ ---
        self.tutorial_completed = False
        # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---
        print(f"已創建新存檔: {file_path}")

    def save_game(self, player_obj):
        """儲存當前的遊戲進度，包含玩家的強化狀態"""
        if not self.current_save_slot:
            print("錯誤：沒有選擇任何存檔槽！")
            return

        try:
            with open(self.current_save_slot, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        data['unlocked_levels'] = sorted(list(self.unlocked_levels))
        # --- ↓↓↓ 【【【本次新增：儲存教學狀態】】】 ↓↓↓ ---
        data['tutorial_completed'] = self.tutorial_completed
        # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---
        if player_obj:
            data['player_stats'] = player_obj.to_dict()

        with open(self.current_save_slot, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"遊戲已儲存至 {self.current_save_slot}")

    def load_save(self, file_path):
        """讀取存檔，並回傳整個存檔資料"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.current_save_slot = file_path
                self.unlocked_levels = set(data.get('unlocked_levels', [1]))
                # --- ↓↓↓ 【【【本次新增：讀取教學狀態】】】 ↓↓↓ ---
                # .get 的第二個參數是預設值，確保舊存檔也能正常運作
                self.tutorial_completed = data.get('tutorial_completed', False)
                # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---
                print(f"已讀取存檔: {file_path}")
                return data
        except FileNotFoundError:
            print(f"錯誤：找不到存檔 {file_path}")
            return None
    
    # --- ↓↓↓ 【【【本次新增：一個專門用來標記教學完成的方法】】】 ↓↓↓ ---
    def mark_tutorial_as_completed(self, player_obj):
        """將教學標記為已完成，並立即存檔"""
        if self.tutorial_completed:
            return
        print("標記教學為已完成並存檔。")
        self.tutorial_completed = True
        self.save_game(player_obj)
    # --- ↑↑↑ 【【【本次新增】】】 ↑↑↑ ---

    def unlock_next_level(self, completed_level):
        next_level = completed_level + 1
        if next_level in LEVELS:
            self.unlocked_levels.add(next_level)
            print(f"已解鎖關卡 {next_level}!")

    def get_all_saves(self):
        files = [f for f in os.listdir(self.save_folder) if f.endswith('.json')]
        saves = []
        for file in files:
            file_path = os.path.join(self.save_folder, file)
            try:
                mtime = os.path.getmtime(file_path)
                
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    unlocked_levels = data.get('unlocked_levels', [1])
                    highest_level = max(unlocked_levels) if unlocked_levels else 1
                
                saves.append({
                    'path': file_path, 
                    'time': mtime, 
                    'name': file, 
                    'highest_level': highest_level
                })
            except (FileNotFoundError, json.JSONDecodeError):
                continue
        return sorted(saves, key=lambda x: x['time'], reverse=True)

    def delete_save(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"已刪除存檔: {file_path}")
            if self.current_save_slot == file_path:
                self.current_save_slot = None

    def is_level_unlocked(self, level_number):
        return level_number in self.unlocked_levels

save_manager = SaveManager()