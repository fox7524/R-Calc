#by fox7524
#by Callisto1232

#Resistor value calculator

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QSpinBox, QFrame, QPushButton, QLineEdit
)
import math
from PyQt5.QtCore import Qt, QSettings, QStandardPaths
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QColor
import sys
import os
import platform
import json

# Detect the operating system
current_os = platform.system()  # Returns 'Windows', 'Darwin' (macOS), 'Linux', etc.

def detect_dark_mode():
    """Detect dark mode with fallbacks for different operating systems."""
    try:
        import darkdetect
        return darkdetect.isDark()
    except (ImportError, Exception):
        pass
    
    # Fallback: Check environment variables for Linux
    if current_os == 'Linux':
        # Check GTK theme (most common on Linux)
        gtk_theme = os.environ.get('GTK_THEME', '').lower()
        if 'dark' in gtk_theme:
            return True
        
        # Check Qt environment
        qt_style = os.environ.get('QT_STYLE_OVERRIDE', '').lower()
        if 'dark' in qt_style:
            return True
        
        # Check common theme config files
        theme_files = [
            os.path.expanduser('~/.config/gtk-3.0/settings.ini'),
            os.path.expanduser('~/.gtkrc-2.0')
        ]
        
        for theme_file in theme_files:
            try:
                with open(theme_file, 'r') as f:
                    content = f.read().lower()
                    if 'gtk-application-prefer-dark-theme=true' in content or 'theme-name' in content and 'dark' in content:
                        return True
            except (FileNotFoundError, IOError):
                pass
        
        # Default to dark for Kali/Debian-based dark distros
        try:
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    os_info = f.read().lower()
                    if 'kali' in os_info or 'parrot' in os_info:
                        return True
        except:
            pass
    
    # Default fallback
    return False

base_dir = os.path.dirname(os.path.abspath(__file__))

color_values = {
    "Black": (0, 1, None),
    "Brown": (1, 10, "±1%"),
    "Red": (2, 100, "±2%"),
    "Orange": (3, 1_000, None),
    "Yellow": (4, 10_000, None),
    "Green": (5, 100_000, "±0.5%"),
    "Blue": (6, 1_000_000, "±0.25%"),
    "Purple": (7, 10_000_000, "±0.1%"),
    "Gray": (8, 100_000_000, "±0.05%"),
    "White": (9, 1_000_000_000, None),
    "Gold": (-1, 0.1, "±5%"),
    "Silver": (-2, 0.01, "±10%"),
    "": (None, None, "")
}

COLORS_HEX = {
    "Black": "#000000",
    "Brown": "#8B4513",
    "Red": "#FF0000",
    "Orange": "#FFA500",
    "Yellow": "#FFFF00",
    "Green": "#008000",
    "Blue": "#0000FF",
    "Purple": "#800080",
    "Gray": "#808080",
    "White": "#FFFFFF",
    "Gold": "#FFD700",
    "Silver": "#C0C0C0"
}

band_names = ["1st Band", "2nd Band", "3rd Band", "Multiplier", "Tolerance", "Temperature Coefficient"]

class ResistorCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resistor Calculator")
        self.setFixedWidth(400)

        # Use portable QSettings path that works across all platforms
        if current_os == 'Linux':
            config_path = os.path.expanduser('~/.config/direnc_app')
            os.makedirs(config_path, exist_ok=True)
            self.settings = QSettings(os.path.join(config_path, 'settings.ini'), QSettings.IniFormat)
        else:
            self.settings = QSettings("fox&callisto", "direnc_app")

        ana_layout = QVBoxLayout()
        self.setLayout(ana_layout)

        self.custom_title = QLabel("Resistor Calculator")
        self.custom_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.custom_title.setAlignment(Qt.AlignCenter)
        ana_layout.addWidget(self.custom_title)

        self.calc_mode = 0
        self.mode_btn = QPushButton("Switch to Ohms -> Colors")
        self.mode_btn.clicked.connect(self.toggle_mode)
        ana_layout.addWidget(self.mode_btn)

        self.band_count_selector = QComboBox()
        self.band_count_selector.addItems(["4", "5", "6"])
        self.band_count_selector.currentTextChanged.connect(self.refresh_band_setup)
        ana_layout.addWidget(QLabel("Band Count:"))
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
        self.ohms_layout.addWidget(QLabel("Resistance:"))
        self.ohms_layout.addWidget(self.ohm_input)
        self.ohms_layout.addWidget(self.unit_combo)
        ana_layout.addWidget(self.ohms_container)
        self.ohms_container.hide()

        self.direnc_resmi = QLabel()
        self.direnc_resmi.setAlignment(Qt.AlignCenter)
        ana_layout.addWidget(self.direnc_resmi)

        self.result_label = QLabel("Resistor Value: -")
        ana_layout.addWidget(self.result_label)
        
        self.language_label = QLabel("En")
        self.language_label.setStyleSheet("font-size: 10px; color: gray;")
        self.language_label.setAlignment(Qt.AlignCenter)        

        self.author_label = QLabel("by fox&callisto")
        self.author_label.setStyleSheet("font-size: 11px; color: gray;")
        self.author_label.setAlignment(Qt.AlignCenter)


        ana_layout.addWidget(self.author_label, alignment=Qt.AlignBottom | Qt.AlignHCenter)
        ana_layout.addWidget(self.language_label, alignment=Qt.AlignBottom | Qt.AlignHCenter)

        self.bantlar = []
        self.combo_boxes = []

        self.refresh_band_setup()
        self.apply_system_theme()

    def apply_system_theme(self):
        from PyQt5.QtGui import QPalette
        is_dark = detect_dark_mode()

        palette = QPalette()
        if current_os == 'Darwin':  # macOS specific theme handling
            # On macOS, use system theme more closely or adjust as needed
            if is_dark:
                palette.setColor(QPalette.Window, QColor(30, 30, 30))  # Slightly different dark colors for macOS
                palette.setColor(QPalette.WindowText, Qt.white)
                palette.setColor(QPalette.Base, QColor(20, 20, 20))
                palette.setColor(QPalette.AlternateBase, QColor(30, 30, 30))
                palette.setColor(QPalette.ToolTipBase, Qt.white)
                palette.setColor(QPalette.ToolTipText, Qt.white)
                palette.setColor(QPalette.Text, Qt.white)
                palette.setColor(QPalette.Button, QColor(30, 30, 30))
                palette.setColor(QPalette.ButtonText, Qt.white)
                palette.setColor(QPalette.BrightText, Qt.red)
                palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
                palette.setColor(QPalette.HighlightedText, Qt.black)
            else:
                palette = self.style().standardPalette()  # Use native macOS light theme
        elif current_os == 'Linux':  # Linux specific theme handling
            if is_dark:
                palette.setColor(QPalette.Window, QColor(53, 53, 53))
                palette.setColor(QPalette.WindowText, Qt.black)
                palette.setColor(QPalette.Base, QColor(35, 35, 35))
                palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
                palette.setColor(QPalette.ToolTipBase, Qt.black)
                palette.setColor(QPalette.ToolTipText, Qt.black)
                palette.setColor(QPalette.Text, Qt.black)
                palette.setColor(QPalette.Button, QColor(53, 53, 53))
                palette.setColor(QPalette.ButtonText, Qt.black)
                palette.setColor(QPalette.BrightText, Qt.red)
                palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
                palette.setColor(QPalette.HighlightedText, Qt.black)
            else:
                palette = self.style().standardPalette()
        else:  # For Windows
            if is_dark:
                palette.setColor(QPalette.Window, QColor(53, 53, 53))
                palette.setColor(QPalette.WindowText, Qt.white)
                palette.setColor(QPalette.Base, QColor(35, 35, 35))
                palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
                palette.setColor(QPalette.ToolTipBase, Qt.white)
                palette.setColor(QPalette.ToolTipText, Qt.white)
                palette.setColor(QPalette.Text, Qt.white)
                palette.setColor(QPalette.Button, QColor(53, 53, 53))
                palette.setColor(QPalette.ButtonText, Qt.white)
                palette.setColor(QPalette.BrightText, Qt.red)
                palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
                palette.setColor(QPalette.HighlightedText, Qt.black)
            else:
                palette = self.style().standardPalette()

        self.setPalette(palette)

    def refresh_band_setup(self):
        band_count = int(self.band_count_selector.currentText())

        image_paths = {
            4: os.path.join(base_dir, "4band.png"),
            5: os.path.join(base_dir, "5band.png"),
            6: os.path.join(base_dir, "6band.png")
        }
        image_path = image_paths[band_count]
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(500, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.direnc_resmi.setPixmap(pixmap)
        else:
            self.direnc_resmi.setText(f"Image not found!\n{image_path}\n\n4/5/6band.png")

        for band in getattr(self, 'bands', []):
            band.deleteLater()
        self.bantlar = []

        for i in reversed(range(self.cb_layout.count())):
            layout_item = self.cb_layout.itemAt(i)
            while layout_item.count():
                widget = layout_item.takeAt(0).widget()
                if widget: widget.deleteLater()
            self.cb_layout.removeItem(layout_item)

        # Geometry map for positioning colored band overlays on the resistor image
        # Each tuple (x, y, width, height):
        # 1st number: horizontal position of the top-left corner (pixels from left edge of image)
        # 2nd number: vertical position of the top-left corner (pixels from top edge of image)
        # 3rd number: width of the band overlay rectangle (pixels)
        # 4th number: height of the band overlay rectangle (pixels)
        if current_os == 'Darwin':  # macOS
            band_geometry_map = {
                4: [(115, 15, 15, 79), (157, 15, 15, 79), (199, 15, 15, 79), (289, 10, 15, 92)],
                5: [(65, 16, 15, 81), (121, 22, 15, 67), (158, 22, 15, 67), (195, 22, 15, 67), (274, 16, 15, 81)],
                6: [(50, 10, 16, 89), (112, 16, 15, 75), (135, 16, 15, 75), (158, 16, 15, 75), (220, 16, 15, 75), (276, 10, 16, 89)]
            }
        elif current_os == 'Linux':  # Linux/Kali
            band_geometry_map = {
                4: [(124, 15, 15, 79), (166, 15, 15, 79), (208, 15, 15, 79), (298, 12, 15, 92)],
                5: [(74, 16, 15, 81), (131, 22, 15, 67), (168, 22, 15, 67), (205, 22, 15, 67), (284, 16, 15, 81)],
                6: [(60, 10, 16, 89), (121, 16, 15, 75), (144, 16, 15, 75), (167, 16, 15, 75), (229, 16, 15, 75), (286, 10, 16, 89)]
            }
        else:  # Windows
            band_geometry_map = {
                4: [(115, 15, 15, 79), (157, 15, 15, 79), (199, 15, 15, 79), (289, 10, 15, 92)],
                5: [(65, 16, 15, 81), (121, 22, 15, 67), (158, 22, 15, 67), (195, 22, 15, 67), (274, 16, 15, 81)],
                6: [(50, 10, 16, 89), (112, 16, 15, 75), (135, 16, 15, 75), (158, 16, 15, 75), (220, 16, 15, 75), (276, 10, 16, 89)]
            }
        band_geometries = band_geometry_map[band_count]
        for geom in band_geometries:
            x, y, w, h = geom
            renk_bandi = QFrame(self.direnc_resmi)
            renk_bandi.setParent(self.direnc_resmi)
            renk_bandi.setGeometry(x, y, w, h)
            renk_bandi.setStyleSheet("background-color: #000000; border: 1px solid #222;")
            renk_bandi.show()
            renk_bandi.raise_()
            self.bantlar.append(renk_bandi)

        band_names = ["1st Band", "2nd Band", "3rd Band", "Multiplier", "Tolerance", "Temperature Coefficient"]
        self.combo_boxes = []
        for i in range(band_count):
            dikey = QVBoxLayout()
            etiket = QLabel(band_names[i])
            cb = QComboBox()
            for renk_adi in color_values.keys():
                if renk_adi == "":
                    continue
                icon_pixmap = QPixmap(20, 20)
                icon_pixmap.fill(Qt.transparent)
                painter = QPainter(icon_pixmap)
                painter.setBrush(Qt.black)
                painter.setPen(Qt.black)
                renk_hex = COLORS_HEX.get(renk_adi, "#000000")
                painter.setBrush(QColor(renk_hex))
                painter.drawRect(0, 0, 20, 20)
                painter.end()
                cb.addItem(QIcon(icon_pixmap), renk_adi)
            cb.currentTextChanged.connect(self.update_bands)
            self.combo_boxes.append(cb)
            dikey.addWidget(etiket, alignment=Qt.AlignHCenter)
            dikey.addWidget(cb)
            self.cb_layout.addLayout(dikey)

        for i, cb in enumerate(self.combo_boxes):
            value = self.settings.value(f"band_{i}", "")
            if value in COLORS_HEX:
                cb.blockSignals(True)
                cb.setCurrentText(value)
                cb.blockSignals(False)

        if getattr(self, 'calc_mode', 0) == 0:
            self.update_bands()
        else:
            self.calculate_from_ohms()

    def update_bands(self):
        if getattr(self, 'calc_mode', 0) == 1: return
        for i, cb in enumerate(self.combo_boxes):
            renk = cb.currentText()
            if i < len(self.bantlar):
                renk_hex = COLORS_HEX.get(renk, "#000000")
                self.bantlar[i].setStyleSheet(f"background-color: {renk_hex}; border: 1px solid #222;")
            self.settings.setValue(f"band_{i}", renk)
        self.calculate_resistor()

    def calculate_resistor(self):
        try:
            bands = [cb.currentText() for cb in self.combo_boxes]
            significant_digits = ""
            multiplier = 1
            tolerance = ""
            temp_coeff = ""

            band_count = len(bands)

            if band_count == 4:
                significant_digits = f"{color_values[bands[0]][0]}{color_values[bands[1]][0]}"
                multiplier = color_values[bands[2]][1]
                tolerance = color_values[bands[3]][2] or ""
            elif band_count == 5:
                significant_digits = f"{color_values[bands[0]][0]}{color_values[bands[1]][0]}{color_values[bands[2]][0]}"
                multiplier = color_values[bands[3]][1]
                tolerance = color_values[bands[4]][2] or ""
            elif band_count == 6:
                significant_digits = f"{color_values[bands[0]][0]}{color_values[bands[1]][0]}{color_values[bands[2]][0]}"
                multiplier = color_values[bands[3]][1]
                tolerance = color_values[bands[4]][2] or ""
                temp_coeff = f", S.K: {bands[5]}"

            value = int(significant_digits) * multiplier

            if value >= 1e6:
                display_value = f"{value / 1e6:.2f} MΩ"
            elif value >= 1e3:
                display_value = f"{value / 1e3:.2f} kΩ"
            else:
                display_value = f"{value:.2f} Ω"

            self.result_label.setText(f"Resistor Value: {display_value} {tolerance}{temp_coeff}")
        except Exception:
            self.result_label.setText("Error: Invalid Input.")


    def toggle_mode(self):
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
                colors = ["Black"] * band_count
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
                    colors.append("Gold")
                if band_count >= 5:
                    colors[-1] = "Brown" 
                if band_count == 6:
                    colors.append("Brown") 
            
            for i, band in enumerate(self.bantlar):
                if i < len(colors):
                    c_hex = COLORS_HEX.get(colors[i], "#000000")
                    band.setStyleSheet(f"background-color: {c_hex}; border: 1px solid #222;")
                else:
                    band.setStyleSheet("background-color: #000000; border: 1px solid #222;")
            
            self.result_label.setText("Colors: " + ", ".join(colors))
            
        except Exception:
            self.result_label.setText("Enter valid resistance value.")
            for band in self.bantlar:
                band.setStyleSheet("background-color: #000000; border: 1px solid #222;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResistorCalculator()
    window.show()
    sys.exit(app.exec_())
