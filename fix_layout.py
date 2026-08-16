import sys

def patch_layout(filepath, is_tr):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update imports to include QStackedWidget if not there
    if "QStackedWidget" not in content:
        import_old = "from PyQt5.QtWidgets import (\n    QApplication, QWidget, QVBoxLayout, QHBoxLayout,\n    QLabel, QComboBox, QSpinBox, QFrame, QPushButton, QLineEdit\n)"
        import_new = "from PyQt5.QtWidgets import (\n    QApplication, QWidget, QVBoxLayout, QHBoxLayout,\n    QLabel, QComboBox, QSpinBox, QFrame, QPushButton, QLineEdit, QStackedWidget\n)"
        content = content.replace(import_old, import_new)

    # 2. Modify layout in __init__
    init_old = """        self.cb_container = QWidget()
        self.cb_layout = QHBoxLayout(self.cb_container)
        self.cb_container.setContentsMargins(0, 0, 0, 0)
        ana_layout.addWidget(self.cb_container)

        self.ohms_container = QWidget()
        self.ohms_layout = QHBoxLayout(self.ohms_container)
        self.ohms_container.setContentsMargins(0, 0, 0, 0)"""
    
    init_new = """        self.input_stack = QStackedWidget()
        ana_layout.addWidget(self.input_stack)

        self.cb_container = QWidget()
        self.cb_layout = QHBoxLayout(self.cb_container)
        self.cb_container.setContentsMargins(0, 0, 0, 0)
        self.input_stack.addWidget(self.cb_container)

        self.ohms_container = QWidget()
        self.ohms_layout = QHBoxLayout(self.ohms_container)
        self.ohms_container.setContentsMargins(0, 0, 0, 0)"""
    
    content = content.replace(init_old, init_new)
    
    # Remove adding ohms_container to ana_layout and hide()
    hide_old = """        ana_layout.addWidget(self.ohms_container)
        self.ohms_container.hide()"""
    hide_new = """        self.input_stack.addWidget(self.ohms_container)"""
    content = content.replace(hide_old, hide_new)

    # 3. Modify toggle_mode
    if is_tr:
        toggle_old = """    def toggle_mode(self):
        if self.calc_mode == 0:
            self.calc_mode = 1
            self.mode_btn.setText("Colors -> Ohms Moduna Geç")
            self.cb_container.hide()
            self.ohms_container.show()
            self.calculate_from_ohms()
        else:
            self.calc_mode = 0
            self.mode_btn.setText("Ohms -> Colors Moduna Geç")
            self.ohms_container.hide()
            self.cb_container.show()
            self.calculate_resistor()"""
        
        toggle_new = """    def toggle_mode(self):
        if self.calc_mode == 0:
            self.calc_mode = 1
            self.mode_btn.setText("Colors -> Ohms Moduna Geç")
            self.input_stack.setCurrentIndex(1)
            self.calculate_from_ohms()
        else:
            self.calc_mode = 0
            self.mode_btn.setText("Ohms -> Colors Moduna Geç")
            self.input_stack.setCurrentIndex(0)
            self.calculate_resistor()"""
    else:
        toggle_old = """    def toggle_mode(self):
        if self.calc_mode == 0:
            self.calc_mode = 1
            self.mode_btn.setText("Switch to Colors -> Ohms")
            self.cb_container.hide()
            self.ohms_container.show()
            self.calculate_from_ohms()
        else:
            self.calc_mode = 0
            self.mode_btn.setText("Switch to Ohms -> Colors")
            self.ohms_container.hide()
            self.cb_container.show()
            self.calculate_resistor()"""
        
        toggle_new = """    def toggle_mode(self):
        if self.calc_mode == 0:
            self.calc_mode = 1
            self.mode_btn.setText("Switch to Colors -> Ohms")
            self.input_stack.setCurrentIndex(1)
            self.calculate_from_ohms()
        else:
            self.calc_mode = 0
            self.mode_btn.setText("Switch to Ohms -> Colors")
            self.input_stack.setCurrentIndex(0)
            self.calculate_resistor()"""
            
    content = content.replace(toggle_old, toggle_new)
    
    # 4. Add stretch to prevent overall jumping
    stretch_old = """        self.result_label = QLabel("Resistor Value: -" if not is_tr else "Direnç Değeri: -")"""
    # Wait, the string is literal in the code. Let's just find `self.result_label = QLabel("`
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

patch_layout("R-calc-en.py", False)
patch_layout("R-calc-tr.py", True)
print("Layout patched.")
