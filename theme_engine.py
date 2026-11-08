# ========================================================
# OM Picture Manager - Material You / Fluent Theme Engine
# ========================================================

ACCENT_PALETTES = {
    "Lavender": {
        "primary": "#7567e6",
        "primary_hover": "#6555db",
        "bg_gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f8faff, stop:0.5 #f3f5fd, stop:1 #edeefc)",
        "card_bg": "#ffffff",
        "border": "#e2e6f0",
        "text": "#1e293b",
        "text_sub": "#64748b"
    },
    "Mint": {
        "primary": "#10b981",
        "primary_hover": "#059669",
        "bg_gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f4fbf7, stop:0.5 #ecfdf5, stop:1 #e0f8ed)",
        "card_bg": "#ffffff",
        "border": "#d1fae5",
        "text": "#064e3b",
        "text_sub": "#047857"
    },
    "Sky Blue": {
        "primary": "#0284c7",
        "primary_hover": "#0369a1",
        "bg_gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f0f9ff, stop:0.5 #e0f2fe, stop:1 #bae6fd)",
        "card_bg": "#ffffff",
        "border": "#e0f2fe",
        "text": "#0c4a6e",
        "text_sub": "#0369a1"
    },
    "Rose": {
        "primary": "#e11d48",
        "primary_hover": "#be123c",
        "bg_gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fff1f2, stop:0.5 #ffe4e6, stop:1 #fecdd3)",
        "card_bg": "#ffffff",
        "border": "#ffe4e6",
        "text": "#881337",
        "text_sub": "#9f1239"
    },
    "OLED Dark": {
        "primary": "#818cf8",
        "primary_hover": "#6366f1",
        "bg_gradient": "#09090b",
        "card_bg": "#18181b",
        "border": "#27272a",
        "text": "#fafafa",
        "text_sub": "#a1a1aa"
    }
}

def generate_qss(palette_name="Lavender"):
    p = ACCENT_PALETTES.get(palette_name, ACCENT_PALETTES["Lavender"])
    return f"""
        #RootWidget {{
            background: {p['bg_gradient']};
            border: 1px solid rgba(255, 255, 255, 0.7);
            border-radius: 22px;
        }}
        QWidget {{
            font-family: 'Nunito', 'Segoe UI Variable Display', 'Segoe UI', sans-serif;
            color: {p['text']};
            font-size: 12px;
        }}
        #TopHeaderBar {{
            background: transparent;
            border-top-left-radius: 22px;
            border-top-right-radius: 22px;
            padding: 8px 16px 2px 16px;
        }}
        #AppHeaderTitle {{
            font-size: 19px;
            font-weight: 900;
            color: {p['primary']};
            letter-spacing: 0.8px;
        }}
        .WinBtn {{
            background: transparent;
            border: none;
            border-radius: 12px;
            font-size: 13px;
            font-weight: bold;
            color: {p['text_sub']};
            min-width: 30px;
            max-width: 30px;
            min-height: 30px;
            max-height: 30px;
        }}
        .WinBtn:hover {{
            background: rgba(0, 0, 0, 0.06);
            color: {p['text']};
        }}
        #CloseBtn:hover {{
            background: #ef4444;
            color: #ffffff;
        }}
        QMenuBar {{
            background: transparent;
            border: none;
            padding: 2px 10px;
            font-weight: 700;
            font-size: 13px;
            color: {p['text']};
        }}
        QMenuBar::item {{
            background: transparent;
            padding: 6px 14px;
            border-radius: 10px;
        }}
        QMenuBar::item:selected {{
            background: rgba(0, 0, 0, 0.05);
            color: {p['primary']};
        }}
        QMenu {{
            background: {p['card_bg']};
            border: 1px solid {p['border']};
            border-radius: 12px;
            padding: 6px;
        }}
        QMenu::item {{
            padding: 6px 20px;
            border-radius: 8px;
        }}
        QMenu::item:selected {{
            background: {p['primary']};
            color: #ffffff;
        }}
        QPushButton {{
            background: {p['primary']};
            border: none;
            color: #ffffff;
            padding: 8px 18px;
            border-radius: 16px;
            font-weight: 700;
            font-size: 12px;
        }}
        QPushButton:hover {{
            background: {p['primary_hover']};
        }}
        QPushButton.secondary {{
            background: {p['card_bg']};
            color: {p['text']};
            border: 1px solid {p['border']};
            border-radius: 14px;
        }}
        QPushButton.secondary:hover {{
            background: rgba(0, 0, 0, 0.04);
            border-color: {p['primary']};
        }}
        QGroupBox {{
            background: {p['card_bg']};
            border: 1px solid {p['border']};
            border-radius: 16px;
            margin-top: 14px;
            padding-top: 16px;
            font-weight: 800;
            color: {p['text_sub']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 14px;
            padding: 0 6px;
        }}
        QSlider::groove:horizontal {{
            height: 6px;
            background: {p['border']};
            border-radius: 3px;
        }}
        QSlider::sub-page:horizontal {{
            background: {p['primary']};
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: #ffffff;
            border: 2px solid {p['primary']};
            width: 16px;
            margin: -6px 0;
            border-radius: 9px;
        }}
        QSpinBox, QComboBox {{
            background: {p['card_bg']};
            border: 1px solid {p['border']};
            border-radius: 10px;
            padding: 5px 10px;
            color: {p['text']};
        }}
        QSpinBox:focus, QComboBox:focus {{
            border: 1.5px solid {p['primary']};
        }}
        QGraphicsView {{
            background: {p['card_bg']};
            border: 1px solid {p['border']};
            border-radius: 18px;
        }}
        QListWidget {{
            background: {p['card_bg']};
            border: 1px solid {p['border']};
            border-radius: 14px;
            padding: 4px;
        }}
        QCheckBox {{
            color: {p['text_sub']};
            font-weight: 600;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1px solid {p['border']};
        }}
        QCheckBox::indicator:checked {{
            background: {p['primary']};
            border: 1px solid {p['primary']};
        }}
    """
