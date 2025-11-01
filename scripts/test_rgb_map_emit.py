import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

os.environ.setdefault("KMK_SKIP_STARTUP_DIALOG", "1")
os.environ.setdefault("KMK_SKIP_DEP_CHECK", "1")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import KMKConfigurator, build_default_rgb_matrix_config

app = QApplication([])
win = KMKConfigurator()

# Configure a sample RGB matrix map
cfg = build_default_rgb_matrix_config()
cfg['key_colors'] = {'0': '#ff0000', '5': '#00ff00'}
cfg['underglow_colors'] = {'0': '#0000ff'}
cfg['num_underglow'] = 1
win.rgb_matrix_config = cfg
win.enable_rgb = True

print(win.get_generated_python_code())
    