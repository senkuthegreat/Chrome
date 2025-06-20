from .pc_controller import PCController
import time
import random

class AIActions:
    def __init__(self):
        self.pc = PCController()
        self.action_history = []
        
    def interpret_command(self, command: str) -> str:
        cmd = command.lower()
        
        if "click" in cmd:
            return self._handle_click(cmd)
        elif "type" in cmd or "write" in cmd:
            return self._handle_typing(cmd)
        elif "open" in cmd:
            return self._handle_open(cmd)
        elif "move mouse" in cmd or "cursor" in cmd:
            return self._handle_mouse_move(cmd)
        elif "press" in cmd:
            return self._handle_key_press(cmd)
        elif "scroll" in cmd:
            return self._handle_scroll(cmd)
        elif "screenshot" in cmd:
            return self.pc.screenshot()
        else:
            return self._smart_action(cmd)
    
    def _handle_click(self, cmd: str) -> str:
        # Extract coordinates if present
        words = cmd.split()
        coords = []
        for word in words:
            if word.isdigit():
                coords.append(int(word))
        
        if len(coords) >= 2:
            return self.pc.click(coords[0], coords[1])
        return self.pc.click()
    
    def _handle_typing(self, cmd: str) -> str:
        # Extract text after "type" or "write"
        if "type " in cmd:
            text = cmd.split("type ", 1)[1]
        elif "write " in cmd:
            text = cmd.split("write ", 1)[1]
        else:
            text = cmd
        return self.pc.type_text(text)
    
    def _handle_open(self, cmd: str) -> str:
        target = cmd.replace("open ", "")
        
        if "http" in target or "www" in target:
            return self.pc.open_url(target)
        elif "." in target and "/" in target:
            return self.pc.open_app(f"xdg-open {target}")
        else:
            return self.pc.open_app(target)
    
    def _handle_mouse_move(self, cmd: str) -> str:
        words = cmd.split()
        coords = [int(w) for w in words if w.isdigit()]
        
        if len(coords) >= 2:
            return self.pc.move_mouse(coords[0], coords[1])
        
        # Random movement if no coords
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        return self.pc.move_mouse(x, y)
    
    def _handle_key_press(self, cmd: str) -> str:
        key = cmd.replace("press ", "").strip()
        
        # Handle combinations
        if "+" in key:
            keys = key.split("+")
            return self.pc.key_combo([k.strip() for k in keys])
        
        return self.pc.press_key(key)
    
    def _handle_scroll(self, cmd: str) -> str:
        if "up" in cmd:
            return self.pc.scroll(3)
        elif "down" in cmd:
            return self.pc.scroll(-3)
        else:
            return self.pc.scroll(-1)
    
    def _smart_action(self, cmd: str) -> str:
        """AI decides what to do based on context"""
        smart_actions = {
            "browse internet": lambda: self.pc.open_url("https://google.com"),
            "take screenshot": lambda: self.pc.screenshot(),
            "open browser": lambda: self.pc.open_app("firefox"),
            "open terminal": lambda: self.pc.open_app("gnome-terminal"),
            "open files": lambda: self.pc.open_app("nautilus"),
            "minimize": lambda: self.pc.key_combo(["alt", "F9"]),
            "maximize": lambda: self.pc.key_combo(["alt", "F10"]),
            "close": lambda: self.pc.key_combo(["alt", "F4"]),
            "copy": lambda: self.pc.key_combo(["ctrl", "c"]),
            "paste": lambda: self.pc.key_combo(["ctrl", "v"]),
            "save": lambda: self.pc.key_combo(["ctrl", "s"]),
        }
        
        for action, func in smart_actions.items():
            if action in cmd:
                result = func()
                self.action_history.append(f"{action}: {result}")
                return result
        
        return f"Unknown command: {cmd}"
    
    def autonomous_browse(self):
        """AI browses autonomously"""
        actions = [
            lambda: self.pc.open_url("https://news.google.com"),
            lambda: time.sleep(2),
            lambda: self.pc.scroll(-3),
            lambda: time.sleep(1),
            lambda: self.pc.click(400, 300),
            lambda: time.sleep(2),
            lambda: self.pc.scroll(-5),
        ]
        
        results = []
        for action in actions:
            try:
                result = action()
                if result:
                    results.append(str(result))
            except:
                pass
        
        return "Autonomous browsing completed"
    
    def get_action_history(self):
        return self.action_history[-10:]  # Last 10 actions