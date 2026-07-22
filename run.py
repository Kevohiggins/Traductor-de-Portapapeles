import sys
import os

# Asegurar que la raíz del proyecto esté en PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import main

if __name__ == '__main__':
    main()
