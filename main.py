import io
import sys

from casino import Casino

# Налаштування UTF-8 для консолі Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

if __name__ == "__main__":
    casino = Casino()
    casino.menu()