import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

os.environ.setdefault("KMK_SKIP_STARTUP_DIALOG", "1")
os.environ.setdefault("KMK_SKIP_DEP_CHECK", "1")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import KMKConfigurator, build_default_rgb_matrix_config

app_qt = QApplication([])
app = KMKConfigurator()
app.enable_encoder = True
app.enable_analogin = True
app.enable_rgb = True

# populate a sample encoder entry
app.encoder_config_str = ''
app.analogin_config_str = ''
app.rgb_matrix_config = build_default_rgb_matrix_config()

print(app.get_generated_python_code()[:2000])
