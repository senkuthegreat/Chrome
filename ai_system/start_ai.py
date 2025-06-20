#!/usr/bin/env python3
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run the main AI
try:
    from main_ai import main
    main()
except ImportError as e:
    print(f"Import error: {e}")
    print("Installing required packages...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "numpy", "requests", "pyautogui", "pillow"])
    print("Packages installed. Please run again.")