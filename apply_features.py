import sys

def patch_file(filepath, is_tr):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update imports
    import_old = "from PyQt5.QtWidgets import (\n    QApplication, QWidget, QVBoxLayout, QHBoxLayout,\n    QLabel, QComboBox, QSpinBox, QFrame\n)"
    import_new = "from PyQt5.QtWidgets import (\n    QApplication, QWidget, QVBoxLayout, QHBoxLayout,\n    QLabel, QComboBox, QSpinBox, QFrame, QPushButton, QLineEdit\n)\nimport math"
    content = content.replace(import_old, import_new)

    # 2. Add calc_mode and mode_btn in __init__ right before band_count_selector
    mode_btn_text = "Ohms -> Colors Moduna Geç" if is_tr else "Switch to Ohms -> Colors"
    band_count_label = "Bant Sayısı:" if is_tr else "Band Count:"
    
    init_old = f"""        self.band_count_selector = QComboBox()
        self.band_count_selector.addItems(["4", "5", "6"])
        self.band_count_selector.currentTextChanged.connect(self.refresh_band_setup)
        ana_layout.addWidget(QLabel("{band_count_label}"))
        ana_layout.addWidget(self.band_count_selector)

        self.cb_layout = QHBoxLayout()
        ana_layout.addLayout(self.cb_layout)"""
    
    resistance_label = "Direnç:" if is_tr else "Resistance:"
    
    init_new = f"""        self.calc_mode = 0
        self.mode_btn = QPushButton("{mode_btn_text}")
        self.mode_btn.clicked.connect(self.toggle_mode)
        ana_layout.addWidget(self.mode_btn)

        self.band_count_selector = QComboBox()
        self.band_count_selector.addItems(["4", "5", "6"])
        self.band_count_selector.currentTextChanged.connect(self.refresh_band_setup)
        ana_layout.addWidget(QLabel("{band_count_label}"))
        ana_layout.addWidget(self.band_count_selector)

        self.cb_container = QWidget()
        self.cb_layout = QHBoxLayout(self.cb_container)
        self.cb_container.setContentsMargins(0, 0, 0, 0)
        ana_layout.addWidget(self.cb_container)

        self.ohms_container = QWidget()
        self.ohms_layout = QHBoxLayout(self.ohms_container)
        self.ohms_container.setContentsMargins(0, 0, 0, 0)
        self.ohm_input = QLineEdit()
        self.ohm_input.setPlaceholderText("e.g. 4.7")
        self.ohm_input.textChanged.connect(self.calculate_from_ohms)
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["Ω", "kΩ", "MΩ"])
        self.unit_combo.currentTextChanged.connect(self.calculate_from_ohms)
        self.ohms_layout.addWidget(QLabel("{resistance_label}"))
        self.ohms_layout.addWidget(self.ohm_input)
        self.ohms_layout.addWidget(self.unit_combo)
        ana_layout.addWidget(self.ohms_container)
        self.ohms_container.hide()"""
        
    content = content.replace(init_old, init_new)

    # 3. Update update_bands to check calc_mode
    update_bands_old = """    def update_bands(self):
        for i, cb in enumerate(self.combo_boxes):"""
    update_bands_new = """    def update_bands(self):
        if getattr(self, 'calc_mode', 0) == 1: return
        for i, cb in enumerate(self.combo_boxes):"""
    content = content.replace(update_bands_old, update_bands_new)
    
    # Also in refresh_band_setup, change `self.update_bands()`
    refresh_old_full = """        for i, cb in enumerate(self.combo_boxes):
            value = self.settings.value(f"band_{i}", "")
            if value in COLORS_HEX:
                cb.blockSignals(True)
                cb.setCurrentText(value)
                cb.blockSignals(False)

        self.update_bands()"""
    
    refresh_new = """        if getattr(self, 'calc_mode', 0) == 0:
            self.update_bands()
        else:
            self.calculate_from_ohms()"""
            
    if is_tr:
        refresh_old_full_tr = refresh_old_full.replace("COLORS_HEX", "RENKLER_HEX")
        refresh_new_full_tr = refresh_old_full_tr.replace("        self.update_bands()", refresh_new)
        content = content.replace(refresh_old_full_tr, refresh_new_full_tr)
    else:
        refresh_new_full = refresh_old_full.replace("        self.update_bands()", refresh_new)
        content = content.replace(refresh_old_full, refresh_new_full)
    
    # 4. Add toggle_mode and calculate_from_ohms at the end of the class
    
    mode_0_text = "Colors -> Ohms Moduna Geç" if is_tr else "Switch to Colors -> Ohms"
    mode_1_text = "Ohms -> Colors Moduna Geç" if is_tr else "Switch to Ohms -> Colors"
    
    colors_label = "Renkler: " if is_tr else "Colors: "
    error_msg = "Geçerli bir direnç değeri girin." if is_tr else "Enter valid resistance value."
    color_dict = "RENKLER_HEX" if is_tr else "COLORS_HEX"
    
    if is_tr:
        tol_5 = "Altın"
        tol_1 = "Kahverengi"
        tc_default = "Kahverengi"
        black = "Siyah"
    else:
        tol_5 = "Gold"
        tol_1 = "Brown"
        tc_default = "Brown"
        black = "Black"

    new_methods = f"""
    def toggle_mode(self):
        if self.calc_mode == 0:
            self.calc_mode = 1
            self.mode_btn.setText("{mode_0_text}")
            self.cb_container.hide()
            self.ohms_container.show()
            self.calculate_from_ohms()
        else:
            self.calc_mode = 0
            self.mode_btn.setText("{mode_1_text}")
            self.ohms_container.hide()
            self.cb_container.show()
            self.calculate_resistor()

    def calculate_from_ohms(self):
        if getattr(self, 'calc_mode', 0) != 1: return
        text = self.ohm_input.text().replace(',', '.')
        try:
            val = float(text)
            unit = self.unit_combo.currentText()
            if unit == "kΩ": val *= 1000
            elif unit == "MΩ": val *= 1000000

            band_count = int(self.band_count_selector.currentText())

            if val == 0:
                colors = ["{black}"] * band_count
            else:
                sig_digits_count = 2 if band_count == 4 else 3
                exponent = math.floor(math.log10(val))
                multiplier_exp = exponent - (sig_digits_count - 1)
                
                sig_val = round(val / (10**multiplier_exp))
                
                if sig_val >= 10**sig_digits_count:
                    sig_val //= 10
                    multiplier_exp += 1

                if multiplier_exp < -2 or multiplier_exp > 9:
                    raise ValueError("Value out of range")

                mult_color = ""
                for c, (_, m, _) in color_values.items():
                    if m is not None and abs(m - (10**multiplier_exp)) < 1e-7:
                        mult_color = c
                        break
                
                sig_str = str(int(sig_val)).zfill(sig_digits_count)
                colors = []
                for digit in sig_str:
                    for c, (d, _, _) in color_values.items():
                        if d == int(digit):
                            colors.append(c)
                            break
                colors.append(mult_color)
                
                if band_count >= 4:
                    colors.append("{tol_5}")
                if band_count >= 5:
                    colors[-1] = "{tol_1}" 
                if band_count == 6:
                    colors.append("{tc_default}") 
            
            for i, band in enumerate(self.bantlar):
                if i < len(colors):
                    c_hex = {color_dict}.get(colors[i], "#000000")
                    band.setStyleSheet(f"background-color: {{c_hex}}; border: 1px solid #222;")
                else:
                    band.setStyleSheet("background-color: #000000; border: 1px solid #222;")
            
            self.result_label.setText("{colors_label}" + ", ".join(colors))
            
        except Exception:
            self.result_label.setText("{error_msg}")
            for band in self.bantlar:
                band.setStyleSheet("background-color: #000000; border: 1px solid #222;")

if __name__ == "__main__":"""
    
    content = content.replace("if __name__ == \"__main__\":", new_methods)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

patch_file("R-calc-en.py", False)
patch_file("R-calc-tr.py", True)
print("Patch applied")
