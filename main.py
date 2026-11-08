import sys
import os
import io
from PIL import Image, ImageEnhance
from PyQt6.QtCore import Qt, QRectF, QSize, QSettings
from PyQt6.QtGui import (
    QAction, QIcon, QPixmap, QImage, QPainter, QColor, 
    QPen, QKeySequence, QBrush, QFont
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QSpinBox, QFileDialog, QSplitter,
    QListWidget, QListWidgetItem, QStatusBar, QMessageBox,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem,
    QGroupBox, QGridLayout, QComboBox, QCheckBox, QToolBar
)
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

# ----------------- RICH THEMES -----------------
THEMES = {
    "Cyber Neon (Dark)": """
        QMainWindow, QWidget { background-color: #0b0f19; color: #f1f5f9; font-family: 'Nunito', 'Segoe UI', sans-serif; font-size: 12px; }
        QMenuBar { background-color: #111827; color: #f1f5f9; border-bottom: 1px solid #1f2937; padding: 4px; }
        QMenuBar::item:selected { background-color: #1f2937; border-radius: 4px; color: #00f2fe; }
        QMenu { background-color: #111827; color: #f1f5f9; border: 1px solid #374151; }
        QMenu::item:selected { background-color: #0284c7; }
        QToolBar { background-color: #111827; border-bottom: 1px solid #1f2937; spacing: 6px; padding: 4px 8px; }
        QGroupBox { font-weight: bold; border: 1px solid #1f2937; border-radius: 8px; margin-top: 12px; padding-top: 14px; color: #00f2fe; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
        QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0284c7, stop:1 #0369a1); border: 1px solid rgba(255,255,255,0.1); color: white; padding: 7px 12px; border-radius: 6px; font-weight: 700; }
        QPushButton:hover { background: #00f2fe; color: #000; }
        QSlider::groove:horizontal { height: 4px; background: #1f2937; border-radius: 2px; }
        QSlider::handle:horizontal { background: #00f2fe; width: 14px; margin: -5px 0; border-radius: 7px; }
        QSpinBox, QComboBox { background-color: #111827; border: 1px solid #374151; border-radius: 6px; padding: 4px 8px; color: #f1f5f9; }
        QListWidget { background-color: #111827; border: 1px solid #1f2937; border-radius: 8px; }
        QCheckBox { color: #94a3b8; font-weight: 600; }
        QCheckBox::indicator:checked { background-color: #00f2fe; border: 1px solid #00f2fe; border-radius: 3px; }
    """,
    "OLED Midnight": """
        QMainWindow, QWidget { background-color: #000000; color: #e2e8f0; font-family: 'Nunito', 'Segoe UI', sans-serif; font-size: 12px; }
        QMenuBar { background-color: #0a0a0a; color: #e2e8f0; border-bottom: 1px solid #222; padding: 4px; }
        QMenuBar::item:selected { background-color: #1a1a1a; border-radius: 4px; color: #10b981; }
        QMenu { background-color: #0a0a0a; color: #e2e8f0; border: 1px solid #333; }
        QMenu::item:selected { background-color: #10b981; color: #000; }
        QToolBar { background-color: #0a0a0a; border-bottom: 1px solid #222; spacing: 6px; padding: 4px 8px; }
        QGroupBox { font-weight: bold; border: 1px solid #222; border-radius: 8px; margin-top: 12px; padding-top: 14px; color: #10b981; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
        QPushButton { background-color: #141414; border: 1px solid #333; color: #10b981; padding: 7px 12px; border-radius: 6px; font-weight: 700; }
        QPushButton:hover { background-color: #10b981; color: #000; }
        QSlider::groove:horizontal { height: 4px; background: #222; border-radius: 2px; }
        QSlider::handle:horizontal { background: #10b981; width: 14px; margin: -5px 0; border-radius: 7px; }
        QSpinBox, QComboBox { background-color: #121212; border: 1px solid #333; border-radius: 6px; padding: 4px 8px; color: #e2e8f0; }
        QListWidget { background-color: #0a0a0a; border: 1px solid #222; border-radius: 8px; }
        QCheckBox { color: #a1a1aa; font-weight: 600; }
    """,
    "Nordic Slate": """
        QMainWindow, QWidget { background-color: #1e293b; color: #f8fafc; font-family: 'Nunito', 'Segoe UI', sans-serif; font-size: 12px; }
        QMenuBar { background-color: #0f172a; color: #f8fafc; border-bottom: 1px solid #334155; padding: 4px; }
        QMenuBar::item:selected { background-color: #334155; border-radius: 4px; color: #38bdf8; }
        QMenu { background-color: #0f172a; color: #f8fafc; border: 1px solid #475569; }
        QToolBar { background-color: #0f172a; border-bottom: 1px solid #334155; spacing: 6px; padding: 4px 8px; }
        QGroupBox { font-weight: bold; border: 1px solid #334155; border-radius: 8px; margin-top: 12px; padding-top: 14px; color: #38bdf8; }
        QPushButton { background-color: #38bdf8; color: #0f172a; padding: 7px 12px; border-radius: 6px; font-weight: 700; }
        QPushButton:hover { background-color: #7dd3fc; }
        QSlider::groove:horizontal { height: 4px; background: #334155; border-radius: 2px; }
        QSlider::handle:horizontal { background: #38bdf8; width: 14px; margin: -5px 0; border-radius: 7px; }
        QSpinBox, QComboBox { background-color: #0f172a; border: 1px solid #334155; border-radius: 6px; padding: 4px 8px; color: #f8fafc; }
        QListWidget { background-color: #0f172a; border: 1px solid #334155; border-radius: 8px; }
    """,
    "Fluent Light": """
        QMainWindow, QWidget { background-color: #f1f5f9; color: #0f172a; font-family: 'Nunito', 'Segoe UI', sans-serif; font-size: 12px; }
        QMenuBar { background-color: #ffffff; color: #0f172a; border-bottom: 1px solid #cbd5e1; padding: 4px; }
        QMenuBar::item:selected { background-color: #e2e8f0; border-radius: 4px; }
        QMenu { background-color: #ffffff; color: #0f172a; border: 1px solid #cbd5e1; }
        QToolBar { background-color: #ffffff; border-bottom: 1px solid #cbd5e1; spacing: 6px; padding: 4px 8px; }
        QGroupBox { font-weight: bold; border: 1px solid #cbd5e1; border-radius: 8px; margin-top: 12px; padding-top: 14px; color: #0284c7; }
        QPushButton { background-color: #0284c7; color: white; padding: 7px 12px; border-radius: 6px; font-weight: 700; }
        QPushButton:hover { background-color: #0369a1; }
        QSlider::groove:horizontal { height: 4px; background: #cbd5e1; border-radius: 2px; }
        QSlider::handle:horizontal { background: #0284c7; width: 14px; margin: -5px 0; border-radius: 7px; }
        QSpinBox, QComboBox { background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 4px 8px; color: #0f172a; }
        QListWidget { background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; }
    """
}

# ----------------- SELECTION OVERLAY -----------------
class CropOverlay(QGraphicsRectItem):
    def __init__(self):
        super().__init__()
        self.setPen(QPen(QColor("#00f2fe"), 2, Qt.PenStyle.DashLine))
        self.setBrush(QBrush(QColor(0, 242, 254, 45)))
        self.setVisible(False)

# ----------------- INTERACTIVE VIEWER (ZOOM + PAN) -----------------
class InteractiveViewer(QGraphicsView):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        self.crop_box = CropOverlay()
        self.scene.addItem(self.crop_box)
        
        self.start_pos = None
        self.zoom_factor = 1.15

    def wheelEvent(self, event):
        if self.main.current_pil_image:
            if event.angleDelta().y() > 0:
                self.scale(self.zoom_factor, self.zoom_factor)
            else:
                self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.main.current_pil_image:
            pos = self.mapToScene(event.pos())
            self.start_pos = pos
            self.crop_box.setRect(QRectF(pos, pos))
            self.crop_box.setVisible(True)
        elif event.button() == Qt.MouseButton.RightButton:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.start_pos and self.main.current_pil_image:
            cur_pos = self.mapToScene(event.pos())
            rect = QRectF(self.start_pos, cur_pos).normalized()
            img_rect = self.pixmap_item.boundingRect()
            self.crop_box.setRect(rect.intersected(img_rect))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.start_pos = None
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)

# ----------------- MAIN WINDOW -----------------
class OMPictureManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("OMStudio", "OMPictureManager")
        self.current_image_path = None
        self.original_pil_image = None
        self.current_pil_image = None
        self.aspect_ratio_locked = True

        self.init_ui()
        self.load_persisted_settings()

    def init_ui(self):
        self.setWindowTitle("OM Picture Manager - Pro Studio")
        self.resize(1340, 840)

        # Title Bar और Taskbar पर लोगो सेट करें
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.png")
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)
            QApplication.setWindowIcon(app_icon)

        # Nunito Typography setup
        app_font = QFont("Nunito", 10)
        app_font.setStyleHint(QFont.StyleHint.SansSerif)
        self.setFont(app_font)

        # 1. Menubar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        
        open_act = QAction("&Open Photo...", self)
        open_act.setShortcut(QKeySequence.StandardKey.Open)
        open_act.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_act)

        save_act = QAction("&Save As...", self)
        save_act.setShortcut(QKeySequence.StandardKey.Save)
        save_act.triggered.connect(self.save_image)
        file_menu.addAction(save_act)

        print_act = QAction("&Print Photo...", self)
        print_act.setShortcut(QKeySequence.StandardKey.Print)
        print_act.triggered.connect(self.print_image)
        file_menu.addAction(print_act)

        file_menu.addSeparator()
        exit_act = QAction("E&xit", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        theme_menu = menubar.addMenu("&Theme")
        for t_name in THEMES.keys():
            act = QAction(t_name, self)
            act.triggered.connect(lambda ch, t=t_name: self.set_active_theme(t))
            theme_menu.addAction(act)

        # 2. Quick Toolbar
        toolbar = QToolBar("Quick Tools")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        btn_open = QPushButton("📂 Open Photo")
        btn_open.clicked.connect(self.open_file_dialog)
        toolbar.addWidget(btn_open)

        btn_save = QPushButton("💾 Save")
        btn_save.clicked.connect(self.save_image)
        toolbar.addWidget(btn_save)

        btn_print = QPushButton("🖨️ Print")
        btn_print.clicked.connect(self.print_image)
        toolbar.addWidget(btn_print)

        toolbar.addSeparator()

        btn_rotl = QPushButton("↺ 90° Left")
        btn_rotl.clicked.connect(lambda: self.rotate_quick(-90))
        toolbar.addWidget(btn_rotl)

        btn_rotr = QPushButton("↻ 90° Right")
        btn_rotr.clicked.connect(lambda: self.rotate_quick(90))
        toolbar.addWidget(btn_rotr)

        btn_reset = QPushButton("⟲ Reset All")
        btn_reset.clicked.connect(self.reset_all_transforms)
        toolbar.addWidget(btn_reset)

        # 3. Main Workspace
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        left_box = QWidget()
        left_layout = QVBoxLayout(left_box)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.viewer = InteractiveViewer(self)
        left_layout.addWidget(self.viewer, 4)

        self.filmstrip = QListWidget()
        self.filmstrip.setFixedHeight(105)
        self.filmstrip.setViewMode(QListWidget.ViewMode.IconMode)
        self.filmstrip.setIconSize(QSize(80, 80))
        self.filmstrip.setMovement(QListWidget.Movement.Static)
        self.filmstrip.itemClicked.connect(self.on_filmstrip_click)
        left_layout.addWidget(self.filmstrip, 1)

        splitter.addWidget(left_box)

        # Right Tool Box
        tool_box = QWidget()
        tool_box.setFixedWidth(330)
        box_layout = QVBoxLayout(tool_box)
        box_layout.setContentsMargins(6, 0, 0, 0)

        lbl_tools = QLabel("⚡ STUDIO TOOL BOX")
        lbl_tools.setStyleSheet("font-weight: 800; letter-spacing: 1px; color: #00f2fe; margin-bottom: 4px;")
        box_layout.addWidget(lbl_tools)

        # 1. Crop Setup
        grp_crop = QGroupBox("1. Crop Selection")
        lay_crop = QGridLayout(grp_crop)
        btn_do_crop = QPushButton("✂️ Crop Box")
        btn_do_crop.clicked.connect(self.execute_crop)
        btn_pass = QPushButton("👤 Passport (3.5×4.5)")
        btn_pass.clicked.connect(lambda: self.set_preset_crop(3.5/4.5))
        btn_sign = QPushButton("✍️ Auto Sign Crop")
        btn_sign.clicked.connect(self.auto_crop_signature)

        lay_crop.addWidget(btn_do_crop, 0, 0, 1, 2)
        lay_crop.addWidget(btn_pass, 1, 0)
        lay_crop.addWidget(btn_sign, 1, 1)
        box_layout.addWidget(grp_crop)

        # 2. Straighten & Colors
        grp_adj = QGroupBox("2. Straighten & Color Balance")
        lay_adj = QVBoxLayout(grp_adj)

        lay_adj.addWidget(QLabel("Fine Straighten (-45° to 45°):"))
        self.rot_slider = QSlider(Qt.Orientation.Horizontal)
        self.rot_slider.setRange(-45, 45)
        self.rot_slider.setValue(0)
        self.rot_slider.valueChanged.connect(self.update_live_adjustments)
        lay_adj.addWidget(self.rot_slider)

        lay_adj.addWidget(QLabel("Brightness:"))
        self.b_slider = QSlider(Qt.Orientation.Horizontal)
        self.b_slider.setRange(-50, 50)
        self.b_slider.setValue(0)
        self.b_slider.valueChanged.connect(self.update_live_adjustments)
        lay_adj.addWidget(self.b_slider)

        lay_adj.addWidget(QLabel("Contrast:"))
        self.c_slider = QSlider(Qt.Orientation.Horizontal)
        self.c_slider.setRange(-50, 50)
        self.c_slider.setValue(0)
        self.c_slider.valueChanged.connect(self.update_live_adjustments)
        lay_adj.addWidget(self.c_slider)
        box_layout.addWidget(grp_adj)

        # 3. Resize & Size Setup
        grp_size = QGroupBox("3. Resize & Size Setup")
        lay_size = QGridLayout(grp_size)

        lay_size.addWidget(QLabel("Width (px):"), 0, 0)
        self.spin_w = QSpinBox()
        self.spin_w.setRange(10, 10000)
        self.spin_w.valueChanged.connect(self.on_w_change)
        lay_size.addWidget(self.spin_w, 0, 1)

        lay_size.addWidget(QLabel("Height (px):"), 1, 0)
        self.spin_h = QSpinBox()
        self.spin_h.setRange(10, 10000)
        self.spin_h.valueChanged.connect(self.on_h_change)
        lay_size.addWidget(self.spin_h, 1, 1)

        self.chk_ratio = QCheckBox("Lock Aspect Ratio")
        self.chk_ratio.setChecked(True)
        lay_size.addWidget(self.chk_ratio, 2, 0, 1, 2)

        btn_resize = QPushButton("Apply Pixel Size")
        btn_resize.clicked.connect(self.apply_pixel_resize)
        lay_size.addWidget(btn_resize, 3, 0, 1, 2)
        box_layout.addWidget(grp_size)

        # 4. Target KB Optimizer
        grp_kb = QGroupBox("4. Target Output Size (KB)")
        lay_kb = QGridLayout(grp_kb)
        self.combo_kb = QComboBox()
        self.combo_kb.addItems(["10 KB", "20 KB", "50 KB", "100 KB", "200 KB", "500 KB"])
        self.combo_kb.setCurrentText("50 KB")
        lay_kb.addWidget(self.combo_kb, 0, 0, 1, 2)

        btn_export = QPushButton("🚀 Compress & Export at Exact KB")
        btn_export.setStyleSheet("background: #10b981; color: white; padding: 11px; font-weight: 800; font-size: 13px; border-radius: 8px;")
        btn_export.clicked.connect(self.export_target_kb)
        lay_kb.addWidget(btn_export, 1, 0, 1, 2)
        box_layout.addWidget(grp_kb)

        box_layout.addStretch()
        splitter.addWidget(tool_box)

        # Status Bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready • Open an image to begin")

    def set_active_theme(self, t_name):
        self.setStyleSheet(THEMES.get(t_name, THEMES["Cyber Neon (Dark)"]))
        self.settings.setValue("app_theme", t_name)
        self.status.showMessage(f"Theme switched to: {t_name}", 2000)

    def load_persisted_settings(self):
        saved = self.settings.value("app_theme", "Cyber Neon (Dark)")
        self.set_active_theme(saved)

    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Photo", "", "Images (*.jpg *.jpeg *.png *.bmp)")
        if path:
            self.load_image(path)

    def load_image(self, path):
        self.current_image_path = path
        self.original_pil_image = Image.open(path).convert("RGB")
        self.current_pil_image = self.original_pil_image.copy()

        self.spin_w.blockSignals(True)
        self.spin_h.blockSignals(True)
        self.spin_w.setValue(self.current_pil_image.width)
        self.spin_h.setValue(self.current_pil_image.height)
        self.spin_w.blockSignals(False)
        self.spin_h.blockSignals(False)

        self.render_canvas(self.current_pil_image)

        thumb = self.current_pil_image.copy()
        thumb.thumbnail((80, 80))
        t_io = io.BytesIO()
        thumb.save(t_io, format="PNG")
        qimg = QImage.fromData(t_io.getvalue())
        item = QListWidgetItem(QIcon(QPixmap.fromImage(qimg)), os.path.basename(path))
        item.setData(Qt.ItemDataRole.UserRole, path)
        self.filmstrip.addItem(item)
        self.status.showMessage(f"Loaded: {os.path.basename(path)} ({self.current_pil_image.width}×{self.current_pil_image.height} px)")

    def on_filmstrip_click(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        if path and os.path.exists(path):
            self.load_image(path)

    def render_canvas(self, pil_img):
        b = io.BytesIO()
        pil_img.save(b, format="PNG")
        qimg = QImage.fromData(b.getvalue())
        pix = QPixmap.fromImage(qimg)
        self.viewer.pixmap_item.setPixmap(pix)
        self.viewer.scene.setSceneRect(QRectF(pix.rect()))
        self.viewer.crop_box.setVisible(False)

    def on_w_change(self, val):
        if self.chk_ratio.isChecked() and self.current_pil_image and self.current_pil_image.width > 0:
            ratio = self.current_pil_image.height / self.current_pil_image.width
            self.spin_h.blockSignals(True)
            self.spin_h.setValue(max(10, int(val * ratio)))
            self.spin_h.blockSignals(False)

    def on_h_change(self, val):
        if self.chk_ratio.isChecked() and self.current_pil_image and self.current_pil_image.height > 0:
            ratio = self.current_pil_image.width / self.current_pil_image.height
            self.spin_w.blockSignals(True)
            self.spin_w.setValue(max(10, int(val * ratio)))
            self.spin_w.blockSignals(False)

    def apply_pixel_resize(self):
        if not self.current_pil_image:
            return
        nw, nh = self.spin_w.value(), self.spin_h.value()
        self.current_pil_image = self.current_pil_image.resize((nw, nh), Image.Resampling.LANCZOS)
        self.original_pil_image = self.current_pil_image.copy()
        self.render_canvas(self.current_pil_image)
        self.status.showMessage(f"Resized successfully to {nw}×{nh} px")

    def execute_crop(self):
        if not self.viewer.crop_box.isVisible() or not self.current_pil_image:
            return
        rect = self.viewer.crop_box.rect()
        box = (int(rect.left()), int(rect.top()), int(rect.right()), int(rect.bottom()))
        self.current_pil_image = self.current_pil_image.crop(box)
        self.original_pil_image = self.current_pil_image.copy()
        self.spin_w.setValue(self.current_pil_image.width)
        self.spin_h.setValue(self.current_pil_image.height)
        self.render_canvas(self.current_pil_image)
        self.status.showMessage("Image cropped")

    def set_preset_crop(self, ratio):
        if not self.current_pil_image:
            return
        w = self.current_pil_image.width * 0.7
        h = w / ratio
        self.viewer.crop_box.setRect(QRectF(20, 20, w, h))
        self.viewer.crop_box.setVisible(True)

    def auto_crop_signature(self):
        if not self.current_pil_image:
            return
        gray = self.current_pil_image.convert("L")
        bw = gray.point(lambda x: 0 if x > 195 else 255, '1')
        bbox = bw.getbbox()
        if bbox:
            pad = 12
            box = (
                max(0, bbox[0] - pad),
                max(0, bbox[1] - pad),
                min(self.current_pil_image.width, bbox[2] + pad),
                min(self.current_pil_image.height, bbox[3] + pad)
            )
            self.current_pil_image = self.current_pil_image.crop(box)
            self.original_pil_image = self.current_pil_image.copy()
            self.spin_w.setValue(self.current_pil_image.width)
            self.spin_h.setValue(self.current_pil_image.height)
            self.render_canvas(self.current_pil_image)
            self.status.showMessage("Signature auto-cropped successfully!")

    def rotate_quick(self, deg):
        if not self.current_pil_image:
            return
        self.current_pil_image = self.current_pil_image.rotate(-deg, expand=True)
        self.original_pil_image = self.current_pil_image.copy()
        self.render_canvas(self.current_pil_image)

    def update_live_adjustments(self):
        if not self.original_pil_image:
            return
        ang = self.rot_slider.value()
        img = self.original_pil_image.rotate(-ang, expand=True, resample=Image.Resampling.BICUBIC)
        b_val = 1.0 + (self.b_slider.value() / 50.0)
        img = ImageEnhance.Brightness(img).enhance(b_val)
        c_val = 1.0 + (self.c_slider.value() / 50.0)
        img = ImageEnhance.Contrast(img).enhance(c_val)
        self.current_pil_image = img
        self.render_canvas(self.current_pil_image)

    def reset_all_transforms(self):
        if not self.original_pil_image:
            return
        self.rot_slider.setValue(0)
        self.b_slider.setValue(0)
        self.c_slider.setValue(0)
        self.current_pil_image = self.original_pil_image.copy()
        self.render_canvas(self.current_pil_image)
        self.status.showMessage("Transforms reset")

    def print_image(self):
        if not self.current_pil_image:
            return
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            painter = QPainter(printer)
            b = io.BytesIO()
            self.current_pil_image.save(b, format="PNG")
            qimg = QImage.fromData(b.getvalue())
            pix = QPixmap.fromImage(qimg)
            rect = printer.pageLayout().paintRectPixels(printer.resolution())
            scaled_pix = pix.scaled(rect.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            x = (rect.width() - scaled_pix.width()) // 2
            y = (rect.height() - scaled_pix.height()) // 2
            painter.drawPixmap(x, y, scaled_pix)
            painter.end()
            self.status.showMessage("Sent to printer")

    def export_target_kb(self):
        if not self.current_pil_image:
            return
        target_kb = int(self.combo_kb.currentText().replace(" KB", ""))
        target_bytes = target_kb * 1024

        path, _ = QFileDialog.getSaveFileName(self, "Export Image", f"Optimized_{target_kb}KB.jpg", "JPEG Image (*.jpg)")
        if not path:
            return

        img = self.current_pil_image.copy()
        min_q, max_q = 5, 95
        best_data = None

        for _ in range(8):
            mid_q = (min_q + max_q) // 2
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=mid_q, optimize=True)
            if buf.tell() <= target_bytes:
                best_data = buf.getvalue()
                min_q = mid_q + 1
            else:
                max_q = mid_q - 1

        while (not best_data or len(best_data) > target_bytes) and img.width > 100:
            img = img.resize((int(img.width * 0.8), int(img.height * 0.8)), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=60, optimize=True)
            if buf.tell() <= target_bytes:
                best_data = buf.getvalue()
                break

        if best_data:
            with open(path, "wb") as f:
                f.write(best_data)
            actual_kb = len(best_data) / 1024
            QMessageBox.information(self, "Export Complete", f"File saved at: {actual_kb:.2f} KB\nTarget was: {target_kb} KB")

    def save_image(self):
        if not self.current_pil_image:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Image", "Untitled.jpg", "Images (*.jpg *.png)")
        if path:
            self.current_pil_image.save(path)
            self.status.showMessage(f"Saved: {path}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OMPictureManager()
    window.show()
    sys.exit(app.exec())
