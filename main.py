import sys
import os
import io
from PIL import Image, ImageEnhance
from PyQt6.QtCore import Qt, QRectF, QSize, QPoint, QSettings
from PyQt6.QtGui import (
    QAction, QIcon, QPixmap, QImage, QPainter, QColor, 
    QPen, QKeySequence, QBrush, QFont
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QSpinBox, QFileDialog, QSplitter,
    QListWidget, QListWidgetItem, QMessageBox,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem,
    QGroupBox, QGridLayout, QComboBox, QCheckBox, QGraphicsDropShadowEffect,
    QMenuBar
)
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

import config
import theme_engine

def get_resource_path(relative_path):
    """ PyInstaller exe aur local development dono ke liye sahi path dhundhta hai """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

class CropOverlay(QGraphicsRectItem):
    def __init__(self):
        super().__init__()
        self.setPen(QPen(QColor("#7567e6"), 2, Qt.PenStyle.DashLine))
        self.setBrush(QBrush(QColor(117, 103, 230, 45)))
        self.setVisible(False)

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

class OMPictureManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("OMStudio", "OMPictureManager")
        self.current_image_path = None
        self.original_pil_image = None
        self.current_pil_image = None
        self.old_pos = None

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        self.init_ui()
        self.load_persisted_palette()

    def init_ui(self):
        # Window Icon Setup (uses uploaded icon.ico)
        icon_path = get_resource_path("icon.ico")
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)
            QApplication.setWindowIcon(app_icon)

        # Main Root Container
        root_container = QWidget(self)
        root_container.setObjectName("RootWidget")
        self.setCentralWidget(root_container)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setColor(QColor(0, 0, 0, 45))
        shadow.setOffset(0, 8)
        root_container.setGraphicsEffect(shadow)

        root_layout = QVBoxLayout(root_container)
        root_layout.setContentsMargins(14, 10, 14, 14)
        root_layout.setSpacing(4)

        # ----------------- 1. TOP HEADER (CENTER TITLE, RIGHT CONTROLS) -----------------
        top_header = QWidget()
        top_header.setObjectName("TopHeaderBar")
        header_lay = QHBoxLayout(top_header)
        header_lay.setContentsMargins(10, 4, 10, 0)

        # Left Dummy Spacer to perfectly center the title
        left_dummy = QWidget()
        left_dummy.setFixedWidth(100)
        header_lay.addWidget(left_dummy)
        header_lay.addStretch()

        # Center Bold Title
        self.title_lbl = QLabel(config.APP_NAME)
        self.title_lbl.setObjectName("AppHeaderTitle")
        header_lay.addWidget(self.title_lbl)

        header_lay.addStretch()

        # Right Controls: Minimise, Maximise/Restore & Close Buttons
        right_box = QWidget()
        right_lay = QHBoxLayout(right_box)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(6)

        btn_min = QPushButton("—")
        btn_min.setProperty("class", "WinBtn")
        btn_min.clicked.connect(self.showMinimized)
        right_lay.addWidget(btn_min)

        self.btn_max = QPushButton("◻")
        self.btn_max.setProperty("class", "WinBtn")
        self.btn_max.clicked.connect(self.toggle_maximize)
        right_lay.addWidget(self.btn_max)

        btn_close = QPushButton("✕")
        btn_close.setObjectName("CloseBtn")
        btn_close.setProperty("class", "WinBtn")
        btn_close.clicked.connect(self.close)
        right_lay.addWidget(btn_close)

        header_lay.addWidget(right_box)
        root_layout.addWidget(top_header)

        # ----------------- 2. LEFT-ALIGNED MENU BAR -----------------
        menu_container = QWidget()
        menu_lay = QHBoxLayout(menu_container)
        menu_lay.setContentsMargins(8, 0, 8, 4)
        
        self.nav_menu = QMenuBar()
        menu_lay.addWidget(self.nav_menu)
        menu_lay.addStretch()

        # File Menu
        file_menu = self.nav_menu.addMenu("File")
        act_open = QAction("Open Photo...", self)
        act_open.setShortcut(QKeySequence.StandardKey.Open)
        act_open.triggered.connect(self.open_file_dialog)
        file_menu.addAction(act_open)

        act_save = QAction("Save As...", self)
        act_save.setShortcut(QKeySequence.StandardKey.Save)
        act_save.triggered.connect(self.save_image)
        file_menu.addAction(act_save)

        act_print = QAction("Print Photo...", self)
        act_print.setShortcut(QKeySequence.StandardKey.Print)
        act_print.triggered.connect(self.print_image)
        file_menu.addAction(act_print)

        file_menu.addSeparator()
        act_exit = QAction("Exit", self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # Edit Menu
        edit_menu = self.nav_menu.addMenu("Edit")
        act_crop = QAction("Crop Selection", self)
        act_crop.triggered.connect(self.execute_crop)
        edit_menu.addAction(act_crop)

        act_rotl = QAction("Rotate 90° Left", self)
        act_rotl.triggered.connect(lambda: self.rotate_quick(-90))
        edit_menu.addAction(act_rotl)

        act_rotr = QAction("Rotate 90° Right", self)
        act_rotr.triggered.connect(lambda: self.rotate_quick(90))
        edit_menu.addAction(act_rotr)

        act_reset = QAction("Reset All Edits", self)
        act_reset.triggered.connect(self.reset_all_transforms)
        edit_menu.addAction(act_reset)

        # Theme Menu
        theme_menu = self.nav_menu.addMenu("Theme")
        for pal_name in theme_engine.ACCENT_PALETTES.keys():
            t_action = QAction(pal_name, self)
            t_action.triggered.connect(lambda ch, p=pal_name: self.apply_palette(p))
            theme_menu.addAction(t_action)

        # Tools Menu
        tools_menu = self.nav_menu.addMenu("Tools")
        act_pass = QAction("Passport Crop (3.5x4.5)", self)
        act_pass.triggered.connect(lambda: self.set_preset_crop(3.5/4.5))
        tools_menu.addAction(act_pass)

        act_sign = QAction("Auto Signature Crop", self)
        act_sign.triggered.connect(self.auto_crop_signature)
        tools_menu.addAction(act_sign)

        act_kb = QAction("Target KB Exporter", self)
        act_kb.triggered.connect(self.export_target_kb)
        tools_menu.addAction(act_kb)

        # Help Menu
        help_menu = self.nav_menu.addMenu("Help")
        act_guide = QAction("Quick Instructions", self)
        act_guide.triggered.connect(self.show_help_dialog)
        help_menu.addAction(act_guide)

        # About Menu
        about_menu = self.nav_menu.addMenu("About")
        act_about = QAction("About OM Picture Manager", self)
        act_about.triggered.connect(self.show_about_dialog)
        about_menu.addAction(act_about)

        root_layout.addWidget(menu_container)

        # ----------------- 3. CENTRAL WORKSPACE (VIEWER + TOOLBOX) -----------------
        splitter = QSplitter(Qt.Orientation.Horizontal)
        root_layout.addWidget(splitter)

        # Left Canvas View + Filmstrip
        left_box = QWidget()
        left_layout = QVBoxLayout(left_box)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.viewer = InteractiveViewer(self)
        left_layout.addWidget(self.viewer, 4)

        self.filmstrip = QListWidget()
        self.filmstrip.setFixedHeight(95)
        self.filmstrip.setViewMode(QListWidget.ViewMode.IconMode)
        self.filmstrip.setIconSize(QSize(75, 75))
        self.filmstrip.setMovement(QListWidget.Movement.Static)
        self.filmstrip.itemClicked.connect(self.on_filmstrip_click)
        left_layout.addWidget(self.filmstrip, 1)

        splitter.addWidget(left_box)

        # Right Tool Box Cards
        tool_box = QWidget()
        tool_box.setFixedWidth(320)
        box_layout = QVBoxLayout(tool_box)
        box_layout.setContentsMargins(4, 0, 0, 0)

        # Tool 1: Crop Presets
        grp_crop = QGroupBox("Crop Selection")
        lay_crop = QGridLayout(grp_crop)
        btn_do_crop = QPushButton("Crop Selection")
        btn_do_crop.clicked.connect(self.execute_crop)
        btn_pass = QPushButton("Passport (3.5×4.5)")
        btn_pass.setProperty("class", "secondary")
        btn_pass.clicked.connect(lambda: self.set_preset_crop(3.5/4.5))
        btn_sign = QPushButton("Auto Sign Crop")
        btn_sign.setProperty("class", "secondary")
        btn_sign.clicked.connect(self.auto_crop_signature)

        lay_crop.addWidget(btn_do_crop, 0, 0, 1, 2)
        lay_crop.addWidget(btn_pass, 1, 0)
        lay_crop.addWidget(btn_sign, 1, 1)
        box_layout.addWidget(grp_crop)

        # Tool 2: Straighten & Adjustments
        grp_adj = QGroupBox("Straighten & Adjustment")
        lay_adj = QVBoxLayout(grp_adj)

        lay_adj.addWidget(QLabel("Straighten (-45° to 45°):"))
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

        # Tool 3: Pixel Dimensions
        grp_size = QGroupBox("Dimensions (Pixels)")
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

        btn_resize = QPushButton("Resize Pixels")
        btn_resize.setProperty("class", "secondary")
        btn_resize.clicked.connect(self.apply_pixel_resize)
        lay_size.addWidget(btn_resize, 3, 0, 1, 2)
        box_layout.addWidget(grp_size)

        # Tool 4: Exact KB Target
        grp_kb = QGroupBox("Target File Size (KB)")
        lay_kb = QGridLayout(grp_kb)
        self.combo_kb = QComboBox()
        self.combo_kb.addItems(config.KB_PRESETS)
        self.combo_kb.setCurrentText("50 KB")
        lay_kb.addWidget(self.combo_kb, 0, 0, 1, 2)

        btn_export = QPushButton("Export at Exact KB")
        btn_export.clicked.connect(self.export_target_kb)
        lay_kb.addWidget(btn_export, 1, 0, 1, 2)
        box_layout.addWidget(grp_kb)

        box_layout.addStretch()
        splitter.addWidget(tool_box)

    # ----------------- DRAGGING WINDOW LOGIC -----------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 60:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None and not self.isMaximized():
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    # ----------------- MAXIMIZE / RESTORE LOGIC -----------------
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.btn_max.setText("◻") 
            self.centralWidget().layout().setContentsMargins(14, 10, 14, 14)
        else:
            self.showMaximized()
            self.btn_max.setText("❐")
            self.centralWidget().layout().setContentsMargins(0, 0, 0, 0)

    # ----------------- THEMES -----------------
    def apply_palette(self, name):
        self.setStyleSheet(theme_engine.generate_qss(name))
        self.settings.setValue("active_palette", name)

    def load_persisted_palette(self):
        saved = self.settings.value("active_palette", config.DEFAULT_PALETTE)
        self.apply_palette(saved)

    # ----------------- CORE ENGINE -----------------
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
            QMessageBox.information(self, "Export Complete", f"Saved successfully!\nFile Size: {actual_kb:.2f} KB (Target: {target_kb} KB)")

    def save_image(self):
        if not self.current_pil_image:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Image", "Untitled.jpg", "Images (*.jpg *.png)")
        if path:
            self.current_pil_image.save(path)

    def show_help_dialog(self):
        QMessageBox.information(
            self, "Quick Guide",
            "• Use Mouse Wheel to Zoom In/Out.\n"
            "• Right Click & Drag to Pan (move) canvas.\n"
            "• Left Click & Drag to make a Crop Selection.\n"
            "• Pick Passport or Auto Sign crop presets from the toolbox."
        )

    def show_about_dialog(self):
        QMessageBox.information(
            self, "About",
            f"<b>{config.APP_NAME}</b><br>"
            "Professional Windows Image & Document Studio<br><br>"
            "Crafted with Material Soft UI & PyQt6 Native C++ Framework."
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OMPictureManager()
    window.show()
    sys.exit(app.exec())
