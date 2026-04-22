
#by FOX
#by Callisto1232

# Direnç Hesaplayıcı Uygulaması
# Bu uygulama, direnç bant renklerini kullanarak direnç değerlerini hesaplar.

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QSpinBox, QFrame
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QColor
import sys
import os

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
        try:
            import darkdetect
            is_dark = darkdetect.isDark()
        except: 
            is_dark = False

        palette = QPalette()
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
        band_geometry_map = {
            4: [(120, 15, 15, 79), (162, 15, 15, 79), (204, 15, 15, 79), (294, 10, 15, 92)],  # 4-band resistor geometries
            5: [(65, 16, 15, 81), (121, 22, 15, 67), (158, 22, 15, 67), (195, 22, 15, 67), (274, 16, 15, 81)],  # 5-band resistor geometries
            6: [(50, 10, 16, 89), (112, 16, 15, 75), (135, 16, 15, 75), (158, 16, 15, 75), (220, 16, 15, 75), (276, 10, 16, 89)]  # 6-band resistor geometries
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
        for i, cb in enumerate(self.combo_boxes):
            renk = cb.currentText()
            if i < len(self.bantlar):
                renk_hex = RENKLER_HEX.get(renk, "#000000")
                self.bantlar[i].setStyleSheet(f"background-color: {renk_hex}; border: 1px solid #222;")
            self.settings.setValue(f"bant_{i}", renk)
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
                temp_coeff = f", T.C: {bands[5]}"

            value = int(significant_digits) * multiplier

            if value >= 1e6:
                display_value = f"{value / 1e6:.2f} MΩ"
            elif value >= 1e3:
                display_value = f"{value / 1e3:.2f} kΩ"
            else:
                display_value = f"{value:.2f} Ω"

            self.result_label.setText(f"Direnç Değeri: {display_value} {tolerance}{temp_coeff}")
        except Exception as e:
            self.result_label.setText("Hata: Geçersiz giriş.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResistorCalculator()
    window.show()
    sys.exit(app.exec_())
