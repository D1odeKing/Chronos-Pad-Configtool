import board
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
print(dir(board))

keyboard = KMKKeyboard()

keyboard.col_pins = (board.GP2, board.GP3)
keyboard.row_pins = (board.GP0, board.GP1)
keyboard.diode_orientation = DiodeOrientation.ROW2COL

keyboard.keymap = [
    [
     KC.N1, KC.N2,
     KC.N3, KC.N4,
    ]
]

if __name__ == '__main__':
    keyboard.go()
