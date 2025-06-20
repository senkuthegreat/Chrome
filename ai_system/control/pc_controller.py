import pyautogui
import subprocess
import os
import time
import webbrowser
from typing import Tuple, List, Optional

class PCController:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
    def move_mouse(self, x: int, y: int):
        pyautogui.moveTo(x, y)
        return f"Mouse moved to ({x}, {y})"
    
    def click(self, x: int = None, y: int = None):
        if x and y:
            pyautogui.click(x, y)
            return f"Clicked at ({x}, {y})"
        pyautogui.click()
        return "Clicked at current position"
    
    def type_text(self, text: str):
        pyautogui.write(text)
        return f"Typed: {text}"
    
    def press_key(self, key: str):
        pyautogui.press(key)
        return f"Pressed: {key}"
    
    def key_combo(self, keys: List[str]):
        pyautogui.hotkey(*keys)
        return f"Pressed: {'+'.join(keys)}"
    
    def scroll(self, clicks: int):
        pyautogui.scroll(clicks)
        return f"Scrolled {clicks}"
    
    def screenshot(self):
        filename = f"screen_{int(time.time())}.png"
        pyautogui.screenshot(filename)
        return filename
    
    def open_app(self, app: str):
        try:
            if os.name == 'nt':
                subprocess.Popen(app, shell=True)
            else:
                subprocess.Popen([app])
            return f"Opened {app}"
        except Exception as e:
            return f"Failed: {e}"
    
    def open_url(self, url: str):
        webbrowser.open(url)
        return f"Opened: {url}"
    
    def run_command(self, cmd: str):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"Error: {e}"