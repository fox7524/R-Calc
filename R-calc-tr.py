#by FOX
#by Callisto1232

# Direnç Hesaplayıcı Uygulaması
# Bu uygulama, direnç bant renklerini kullanarak direnç değerlerini hesaplar.

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QSpinBox, QFrame
)
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
    "Siyah": (0, 1, None),
    "Kahverengi": (1, 10, "±1%"),
    "Kırmızı": (2, 100, "±2%"),
    "Turuncu": (3, 1_000, None),
    "Sarı": (4, 10_000, None),
    "Yeşil": (5, 100_000, "±0.5%"),
    "Mavi": (6, 1_000_000, "±0.25%"),
    "Mor": (7, 10_000_000, "±0.1%"),
    "Gri": (8, 100_000_000, "±0.05%"),
    "Beyaz": (9, 1_000_000_000, None),
    "Altın": (-1, 0.1, "±5%"),
    "Gümüş": (-2, 0.01, "±10%"),
    "": (None, None, "")
}

RENKLER_HEX = {
    "Siyah": "#000000",
    "Kahverengi": "#8B4513",
    "Kırmızı": "#FF0000",
    "Turuncu": "#FFA500",
    "Sarı": "#FFFF00",
    "Yeşil": "#008000",
    "Mavi": "#0000FF",
    "Mor": "#800080",
    "Gri": "#808080",
    "Beyaz": "#FFFFFF",
    "Altın": "#FFD700",
    "Gümüş": "#C0C0C0"
}

band_names = ["1. Bant", "2. Bant", "3. Bant", "Çarpan", "Tolerans", "Sıcaklık Katsayısı"]

class ResistorCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Direnç Hesaplayıcı")
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

        self.custom_title = QLabel("Direnç Hesaplayıcı")
        self.custom_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.custom_title.setAlignment(Qt.AlignCenter)
        ana_layout.addWidget(self.custom_title)

        self.band_count_selector = QComboBox()
        self.band_count_selector.addItems(["4", "5", "6"])
        self.band_count_selector.currentTextChanged.connect(self.refresh_band_setup)
        ana_layout.addWidget(QLabel("Bant Sayısı:"))
        ana_layout.addWidget(self.band_count_selector)

        self.cb_layout = QHBoxLayout()
        ana_layout.addLayout(self.cb_layout)

        self.direnc_resmi = QLabel()
        self.direnc_resmi.setAlignment(Qt.AlignCenter)
        ana_layout.addWidget(self.direnc_resmi)

        self.result_label = QLabel("Direnç Değeri: -")
        ana_layout.addWidget(self.result_label)
        
        self.language_label = QLabel("Türkçe")
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
            4: os.path.join(base_dir, "4bant.png"),
            5: os.path.join(base_dir, "5bant.png"),
            6: os.path.join(base_dir, "6bant.png")
        }
        image_path = image_paths[band_count]
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(500, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.direnc_resmi.setPixmap(pixmap)
        else:
            self.direnc_resmi.setText(f"Resim bulunamadı\n{image_path}\n\n4/5/6bant.png")

        for band in getattr(self, 'bantlar', []):
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
                4: [(124, 15, 15, 79), (166, 15, 15, 79), (208, 15, 15, 79), (298, 11, 15, 92)],
                5: [(74, 16, 15, 81), (131, 22, 15, 67), (168, 22, 15, 67), (205, 22, 15, 67), (284, 16, 15, 81)],
                6: [(60, 10, 16, 89), (121, 16, 15, 75), (144, 16, 15, 75), (167, 16, 15, 75), (229, 16, 15, 75), (286, 10, 16, 89)]
            }
        else:  # Windows
            band_geometry_map = {
                4: [(112, 12, 16, 82), (154, 12, 16, 82), (196, 12, 16, 82), (286, 8, 16, 95)],
                5: [(62, 13, 16, 84), (118, 20, 16, 70), (155, 20, 16, 70), (192, 20, 16, 70), (271, 13, 16, 84)],
                6: [(47, 7, 17, 92), (109, 13, 16, 78), (132, 13, 16, 78), (155, 13, 16, 78), (217, 13, 16, 78), (273, 7, 17, 92)]
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

        etiketler = ["1. Bant", "2. Bant", "3. Bant", "Çarpan", "Tolerans", "Sıcaklık Katsayısı"]
        self.combo_boxes = []
        for i in range(band_count):
            dikey = QVBoxLayout()
            etiket = QLabel(etiketler[i])
            cb = QComboBox()
            for renk_adi in color_values.keys():
                if renk_adi == "":
                    continue
                icon_pixmap = QPixmap(20, 20)
                icon_pixmap.fill(Qt.transparent)
                painter = QPainter(icon_pixmap)
                painter.setBrush(Qt.black)
                painter.setPen(Qt.black)
                renk_hex = RENKLER_HEX.get(renk_adi, "#000000")
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
            if value in RENKLER_HEX:
                cb.blockSignals(True)
                cb.setCurrentText(value)
                cb.blockSignals(False)

        self.update_bands()

    def update_bands(self):
        for i, band in enumerate(self.bantlar):
            if i < len(self.combo_boxes):
                selected_color = self.combo_boxes[i].currentText()
                color_hex = RENKLER_HEX.get(selected_color, "#000000")
                band.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #222;")
            else:
                band.setStyleSheet("background-color: #000000; border: 1px solid #222;")

        self.calculate_resistor()

    def calculate_resistor(self):
        pass
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResistorCalculator()
    window.show()
    sys.exit(app.exec_())
