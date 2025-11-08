import re

# Read the file
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the position to insert (right before setup_macropad_grid_ui)
pattern = r'(\n\n    def setup_macropad_grid_ui\(self, parent_layout\):)'
new_method = '''
    def setup_grid_actions_bar(self, parent_layout):
        """
        Setup grid actions bar with quick action buttons and selection display.
        
        Features:
        - Clear Layer: Resets all keys in current layer to KC.NO
        - Copy Layer: Copies current layer to clipboard
        - Paste Layer: Pastes clipboard layer data to current layer
        - Selection Display: Shows currently selected key coordinates and assignment
        
        Note:
            Actions bar provides quick access to common layer operations.
        """
        actions_frame = QFrame()
        actions_frame.setObjectName("card")
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setContentsMargins(12, 8, 12, 8)
        actions_layout.setSpacing(8)
        
        # Action buttons row
        buttons_layout = QHBoxLayout()
        
        clear_layer_btn = QPushButton("🗑 Clear Layer")
        clear_layer_btn.clicked.connect(self.clear_current_layer)
        clear_layer_btn.setToolTip("Clear all keys in the current layer (set to KC.NO)")
        buttons_layout.addWidget(clear_layer_btn)
        
        copy_layer_btn = QPushButton("📋 Copy")
        copy_layer_btn.clicked.connect(self.copy_current_layer)
        copy_layer_btn.setToolTip("Copy current layer to clipboard")
        buttons_layout.addWidget(copy_layer_btn)
        
        paste_layer_btn = QPushButton("📌 Paste")
        paste_layer_btn.clicked.connect(self.paste_to_current_layer)
        paste_layer_btn.setToolTip("Paste layer from clipboard")
        buttons_layout.addWidget(paste_layer_btn)
        
        buttons_layout.addStretch()
        actions_layout.addLayout(buttons_layout)
        
        # Selection display label
        self.grid_selection_label = QLabel("Selected: None")
        self.grid_selection_label.setStyleSheet("font-size: 9pt; color: #888; padding: 4px;")
        actions_layout.addWidget(self.grid_selection_label)
        
        parent_layout.addWidget(actions_frame)

'''

# Insert the new method before setup_macropad_grid_ui
new_content = re.sub(pattern, new_method + r'\1', content)

# Write back
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Method inserted successfully')
