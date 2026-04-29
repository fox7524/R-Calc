import os
import re
from importlib.machinery import SourceFileLoader


def _extract_display_value(text: str) -> tuple[float, str]:
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(MΩ|kΩ|Ω)", text)
    if not m:
        raise ValueError(f"Could not parse value from: {text!r}")
    return float(m.group(1)), m.group(2)


def _run_en(app):
    m = SourceFileLoader("r_calc_en", "R-calc-en.py").load_module()
    w = m.ResistorCalculator()
    w.band_count_selector.setCurrentText("4")
    w.refresh_band_setup()
    w.combo_boxes[0].setCurrentText("Brown")
    w.combo_boxes[1].setCurrentText("Black")
    w.combo_boxes[2].setCurrentText("Red")
    w.combo_boxes[3].setCurrentText("Gold")
    w.calculate_resistor()
    return w.result_label.text()


def _run_tr(app):
    m = SourceFileLoader("r_calc_tr", "R-calc-tr.py").load_module()
    w = m.ResistorCalculator()
    w.band_count_selector.setCurrentText("4")
    w.refresh_band_setup()
    w.combo_boxes[0].setCurrentText("Kahverengi")
    w.combo_boxes[1].setCurrentText("Siyah")
    w.combo_boxes[2].setCurrentText("Kırmızı")
    w.combo_boxes[3].setCurrentText("Altın")
    w.calculate_resistor()
    return w.result_label.text()


def main() -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    try:
        en_text = _run_en(app)
        tr_text = _run_tr(app)
        en_value = _extract_display_value(en_text)
        tr_value = _extract_display_value(tr_text)
        if en_value != tr_value:
            raise SystemExit(f"Mismatch: en={en_text!r} tr={tr_text!r}")
        if "±5%" not in en_text or "±5%" not in tr_text:
            raise SystemExit(f"Tolerance missing: en={en_text!r} tr={tr_text!r}")
        print("ok", en_text, "|", tr_text)
        return 0
    finally:
        app.quit()


if __name__ == "__main__":
    raise SystemExit(main())
