from PyQt6.QtWidgets import QApplication
import sys
sys.path.append(r'c:/Users/daves/repos/WorkFlowX-Configtool')
from main import KMKConfigurator
app = QApplication([])
win = KMKConfigurator()
win.peg_rgb_colors = {'0': {'0': '#ff0000', '5': '#00ff00'}, '1': {'2': '#0000ff'}}
win.enable_rgb = True
print(win.get_generated_python_code())
