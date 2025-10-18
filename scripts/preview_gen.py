import sys
sys.path.append(r'c:\Users\daves\repos\WorkFlowX-Configtool')
from PyQt6.QtWidgets import QApplication
from main import KMKConfigurator
app_qt = QApplication([])
app = KMKConfigurator()
app.enable_encoder = True
app.enable_analogin = True
app.enable_rgb = True
# populate a sample encoder entry
app.encoder_config_str = ''
app.analogin_config_str = ''
app.rgb_config_str = ''
print(app.get_generated_python_code()[:2000])
