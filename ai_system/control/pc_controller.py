import subprocess
import os
import time
import webbrowser
from typing import Tuple, List, Optional

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    GUI_AVAILABLE = True
except Exception:
    GUI_AVAILABLE = False

class PCController:
    def __init__(self):
        self.gui_available = GUI_AVAILABLE
        
    def move_mouse(self, x: int, y: int):
        if self.gui_available:
            pyautogui.moveTo(x, y)
            return f"Mouse moved to ({x}, {y})"
        return f"[SIMULATED] Mouse moved to ({x}, {y})"
    
    def click(self, x: int = None, y: int = None):
        if self.gui_available:
            if x and y:
                pyautogui.click(x, y)
                return f"Clicked at ({x}, {y})"
            pyautogui.click()
            return "Clicked at current position"
        return f"[SIMULATED] Clicked at ({x}, {y})" if x and y else "[SIMULATED] Clicked"
    
    def type_text(self, text: str):
        if self.gui_available:
            pyautogui.write(text)
            return f"Typed: {text}"
        return f"[SIMULATED] Typed: {text}"
    
    def press_key(self, key: str):
        if self.gui_available:
            pyautogui.press(key)
            return f"Pressed: {key}"
        return f"[SIMULATED] Pressed: {key}"
    
    def key_combo(self, keys: List[str]):
        if self.gui_available:
            pyautogui.hotkey(*keys)
            return f"Pressed: {'+'.join(keys)}"
        return f"[SIMULATED] Pressed: {'+'.join(keys)}"
    
    def scroll(self, clicks: int):
        if self.gui_available:
            pyautogui.scroll(clicks)
            return f"Scrolled {clicks}"
        return f"[SIMULATED] Scrolled {clicks}"
    
    def screenshot(self):
        if self.gui_available:
            filename = f"screen_{int(time.time())}.png"
            pyautogui.screenshot(filename)
            return filename
        return "[SIMULATED] Screenshot taken"
    
    def open_app(self, app: str):
        try:
            if os.name == 'nt':
                subprocess.Popen(app, shell=True)
            else:
                subprocess.Popen([app])
            return f"Opened {app}"
        except Exception as e:
            return f"[SIMULATED] Opened {app} (GUI not available)"
    
    def open_url(self, url: str):
        try:
            webbrowser.open(url)
            return f"Opened: {url}"
        except Exception:
            return f"[SIMULATED] Opened: {url}"
    
    def run_command(self, cmd: str):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"Error: {e}"