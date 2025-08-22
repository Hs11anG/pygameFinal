# save_manager.py
import json

SAVE_FILE = 'save.json'

class SaveManager:
    def __init__(self):
        self.data = {
            'unlocked_level': 1, # 玩家預設解鎖第一關
            'gold': 0
        }
        self.load_game()

    def load_game(self):
        try:
            with open(SAVE_FILE, 'r') as f:
                self.data = json.load(f)
                print(f"Save file loaded: {self.data}")
        except FileNotFoundError:
            print("No save file found, creating a new one.")
            self.save_game()

    def save_game(self):
        with open(SAVE_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)
            print(f"Game saved: {self.data}")

    def is_level_unlocked(self, level_number):
        return level_number <= self.data.get('unlocked_level', 1)

    def unlock_next_level(self, completed_level):
        next_level = completed_level + 1
        if next_level > self.data['unlocked_level']:
            self.data['unlocked_level'] = next_level
            self.save_game()

# 建立一個全局唯一的存檔管理器實例
save_manager = SaveManager()