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

    def create_new_save(self):
        saves = self.get_all_saves()
        if len(saves) >= MAX_SAVES:
            print("存檔已滿！")
            return

        now = datetime.now().strftime("%y_%m_%d_%H_%M_save")
        file_path = os.path.join(self.save_folder, f"{now}.json")
        
        new_save_data = {
            'unlocked_levels': [1],
            'player_stats': None
        }
        
        with open(file_path, 'w') as f:
            json.dump(new_save_data, f, indent=4)
            
        self.current_save_slot = file_path
        self.unlocked_levels = {1}
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
                print(f"已讀取存檔: {file_path}")
                return data
        except FileNotFoundError:
            print(f"錯誤：找不到存檔 {file_path}")
            return None
    
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
                saves.append({'path': file_path, 'time': mtime, 'name': file})
            except FileNotFoundError:
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