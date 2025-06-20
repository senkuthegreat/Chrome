try:
    import numpy as np
    print("numpy imported successfully!")
    print(f"numpy version: {np.__version__}")
except ImportError as e:
    print(f"Failed to import numpy: {e}")

try:
    import sys
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
except Exception as e:
    print(f"Error: {e}")