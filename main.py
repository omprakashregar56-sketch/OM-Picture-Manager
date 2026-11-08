import sys
import os
import io
from PIL import Image, ImageEnhance
from PyQt6.QtCore import Qt, QRectF, QSize, QSettings
from PyQt6.QtGui import (
    QAction, QIcon, QPixmap, QImage, QPainter, QColor, 
    QPen, QKeySequence, QBrush
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QSpinBox, QFileDialog, QSplitter,
    QListWidget, QListWidgetItem, QStatusBar, QMessageBox,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem,
    QGroupBox, QGridLayout, QComboBox
)
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

THEMES = {
    "Cyber Dark": """
        QMainWindow, QWidget { background-color: #0b0f19; color: #f1f5f9; font-family: 'Segoe UI', sans-serif; }
        QMenuBar { background-color: #111827; color: #f1f5f9; border-bottom: 1px solid #1f2937; padding: 4px; }
        QMenuBar::item:selected { background-color: #1f2937; border-radius: 4px; }
        QMenu { background-color: #111827; color: #f1f5f9; border: 1px solid #374151; }
        QMenu::item:selected { background-color: #0284c7; }
        QGroupBox { font-weight: bold; border: 1px solid #1f2937; border-radius: 8px; margin-top: 10px; padding-top: 14px; color: #38bdf8; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
        QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0284c7, stop:1 #0369a1); border: none; color: white; padding: 8px 12px; border-radius: 6px; font-weight: 600; font-size: 11px; }
        QPushButton:hover { background: #38bdf8; color: #000; }
        QSlider::groove:horizontal { height: 4px; background: #1f2937; border-radius: 2px; }
        QSlider::handle:horizontal { background: #38bdf8; width: 14px; margin: -5px 0; border-radius: 7px; }
        QSpinBox, QComboBox { background-color: #111827; border: 1px solid #374151; border-radius: 4px; padding: 4px; color: #f1f5f9; }
        QListWidget { background-color: #111827; border: 1px solid #1f2937; border-radius: 8px; }
    """,
    "Modern Light": """
        QMainWindow, QWidget { background-color: #f8fafc; color: #0f172a; font-family: 'Segoe UI', sans-serif; }
        QMenuBar { background-color: #ffffff; color: #0f172a; border-bottom: 1px solid #e2e8f0; }
        QMenuBar::item:selected { background-color: #f1f5f9; border-radius: 4px; }
        QMenu { background-color: #ffffff; color: #0f172a; border: 1px solid #cbd5e1; }
        QMenu::item:selected { background-color: #0284c7; color: white; }
        QGroupBox { font-weight: bold; border: 1px solid #cbd5e1; border-radius: 8px; margin-top: 10px; padding-top: 14px; color: #0284c7; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
        QPushButton { background-color: #0284c7; color: white; padding: 8px 12px; border-radius: 6px; font-weight: 600; font-size: 11px; }
        QPushButton:hover { background-color: #0369a1; }
        QSlider::groove:horizontal { height: 4px; background: #cbd5e1; border-radius: 2px; }
        QSlider::handle:horizontal { background: #0284c7; width: 14px; margin: -5px 0; border-radius: 7px; }
        QSpinBox, QComboBox { background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px; padding: 4px; color: #0f172a; }
        QListWidget { background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; }
    """
}

class CropOverlay(QGraphicsRectItem):
    def __init__(self):
        super().__init__()
        self.setPen(QPen(QColor("#38bdf8"), 2, Qt.PenStyle.DashLine))
        self.setBrush(QBrush(QColor(56, 189, 248, 40)))
        self.setVisible(False)

class CanvasViewer(QGraphicsView):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        self.crop_box = CropOverlay()
        self.scene.addItem(self.crop_box)
        self.start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.main.current_pil_image:
            scene_pos = self.mapToScene(event.pos())
            self.start_pos = scene_pos
            self.crop_box.setRect(QRectF(scene_pos, scene_pos))
            self.crop_box.setVisible(True)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.start_pos and self.main.current_pil_image:
            cur_pos = self.mapToScene(event.pos())
            rect = QRectF(self.start_pos, cur_pos).normalized()
            img_rect = self.pixmap_item.boundingRect()
            rect = rect.intersected(img_rect)
            self.crop_box.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.start_pos = None
        super().mouseReleaseEvent(event)

class OMPictureManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("OMStudio", "OMPictureManager")
        self.current_image_path = None
        self.original_pil_image = None
        self.current_pil_image = None

        self.init_ui()
        self.load_persisted_settings()

    def init_ui(self):
        self.setWindowTitle("OM Picture Manager")
        self.resize(1280, 800)

        # Menubar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        
        open_act = QAction("&Open Image...", self)
        open_act.setShortcut(QKeySequence.StandardKey.Open)
        open_act.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_act)

        save_act = QAction("&Save As...", self)
        save_act.setShortcut(QKeySequence.StandardKey.Save)
        save_act.triggered.connect(self.save_image)
        file_menu.addAction(save_act)

        print_act = QAction("&Print...", self)
        print_act.setShortcut(QKeySequence.StandardKey.Print)
        print_act.triggered.connect(self.print_image)
        file_menu.addAction(print_act)

        file_menu.addSeparator()
        exit_act = QAction("E&xit", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        theme_menu = menubar.addMenu("&Theme")
        for theme_name in THEMES.keys():
            t_action = QAction(theme_name, self)
            t_action.triggered.connect(lambda ch, t=theme_name: self.set_active_theme(t))
            theme_menu.addAction(t_action)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.viewer = CanvasViewer(self)
        left_layout.addWidget(self.viewer, 4)

        self.filmstrip = QListWidget()
        self.filmstrip.setFixedHeight(95)
        self.filmstrip.setViewMode(QListWidget.ViewMode.IconMode)
        self.filmstrip.setIconSize(QSize(75, 75))
        self.filmstrip.setMovement(QListWidget.Movement.Static)
        self.filmstrip.itemClicked.connect(self.on_filmstrip_click)
        left_layout.addWidget(self.filmstrip, 1)

        splitter.addWidget(left_container)

        inspector = QWidget()
        inspector.setFixedWidth(320)
        ins_layout = QVBoxLayout(inspector)
        ins_layout.setContentsMargins(4, 0, 4, 0)

        # 1. Pixel Resize Box
        px_group = QGroupBox("Dimensions (Pixels)")
        px_layout = QGridLayout(px_group)
        px_layout.addWidget(QLabel("Width (px):"), 0, 0)
        self.w_spin = QSpinBox()
        self.w_spin.setRange(10, 10000)
        px_layout.addWidget(self.w_spin, 0, 1)

        px_layout.addWidget(QLabel("Height (px):"), 1, 0)
        self.h_spin = QSpinBox()
        self.h_spin.setRange(10, 10000)
        px_layout.addWidget(self.h_spin, 1, 1)

        btn_apply_px = QPushButton("Resize Pixels")
        btn_apply_px.clicked.connect(self.apply_pixel_resize)
        px_layout.addWidget(btn_apply_px, 2, 0, 1, 2)
        ins_layout.addWidget(px_group)

        # 2. Crop
        crop_group = QGroupBox("Crop Selection")
        c_layout = QGridLayout(crop_group)
        btn_crop = QPushButton("Crop Box")
        btn_crop.clicked.connect(self.execute_crop)
        btn_pass = QPushButton("Passport (3.5x4.5)")
        btn_pass.clicked.connect(lambda: self.set_preset_crop(3.5/4.5))
        btn_sign = QPushButton("Auto Sign Crop")
        btn_sign.clicked.connect(self.auto_crop_signature)

        c_layout.addWidget(btn_crop, 0, 0, 1, 2)
        c_layout.addWidget(btn_pass, 1, 0)
        c_layout.addWidget(btn_sign, 1, 1)
        ins_layout.addWidget(crop_group)

        # 3. Straighten & Colors
        adj_group = QGroupBox("Straighten & Adjustment")
        adj_layout = QVBoxLayout(adj_group)

        adj_layout.addWidget(QLabel("Straighten (-45° to 45°):"))
        self.rot_slider = QSlider(Qt.Orientation.Horizontal)
        self.rot_slider.setRange(-45, 45)
        self.rot_slider.setValue(0)
        self.rot_slider.valueChanged.connect(self.update_image_adjustments)
        adj_layout.addWidget(self.rot_slider)

        adj_layout.addWidget(QLabel("Brightness:"))
        self.bright_slider = QSlider(Qt.Orientation.Horizontal)
        self.bright_slider.setRange(-50, 50)
        self.bright_slider.setValue(0)
        self.bright_slider.valueChanged.connect(self.update_image_adjustments)
        adj_layout.addWidget(self.bright_slider)

        adj_layout.addWidget(QLabel("Contrast:"))
        self.cont_slider = QSlider(Qt.Orientation.Horizontal)
        self.cont_slider.setRange(-50, 50)
        self.cont_slider.setValue(0)
        self.cont_slider.valueChanged.connect(self.update_image_adjustments)
        adj_layout.addWidget(self.cont_slider)
        ins_layout.addWidget(adj_group)

        # 4. Target KB
        kb_group = QGroupBox("Exact Target Size (KB)")
        kb_layout = QGridLayout(kb_group)
        self.target_kb_combo = QComboBox()
        self.target_kb_combo.addItems(["10 KB", "20 KB", "50 KB", "100 KB", "200 KB", "500 KB"])
        self.target_kb_combo.setCurrentText("50 KB")
        kb_layout.addWidget(self.target_kb_combo, 0, 0, 1, 2)

        btn_export = QPushButton("Export at Exact KB")
        btn_export.setStyleSheet("background: #10b981; color: white; padding: 10px; font-weight: bold;")
        btn_export.clicked.connect(self.export_target_kb)
        kb_layout.addWidget(btn_export, 1, 0, 1, 2)
        ins_layout.addWidget(kb_group)

        ins_layout.addStretch()
        splitter.addWidget(inspector)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")

    def set_active_theme(self, theme_name):
        self.setStyleSheet(THEMES.get(theme_name, THEMES["Cyber Dark"]))
        self.settings.setValue("app_theme", theme_name)
        self.status.showMessage(f"Theme: {theme_name}", 2000)

    def load_persisted_settings(self):
        saved_theme = self.settings.value("app_theme", "Cyber Dark")
        self.set_active_theme(saved_theme)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Photo", "", "Images (*.jpg *.jpeg *.png *.bmp)")
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        self.current_image_path = file_path
        self.original_pil_image = Image.open(file_path).convert("RGB")
        self.current_pil_image = self.original_pil_image.copy()

        self.w_spin.setValue(self.current_pil_image.width)
        self.h_spin.setValue(self.current_pil_image.height)
        self.render_pil_to_canvas(self.current_pil_image)

        thumb = self.current_pil_image.copy()
        thumb.thumbnail((80, 80))
        thumb_bytes = io.BytesIO()
        thumb.save(thumb_bytes, format="PNG")
        q_img = QImage.fromData(thumb_bytes.getvalue())
        item = QListWidgetItem(QIcon(QPixmap.fromImage(q_img)), os.path.basename(file_path))
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        self.filmstrip.addItem(item)
        self.status.showMessage(f"Loaded: {os.path.basename(file_path)}")

    def on_filmstrip_click(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        if path and os.path.exists(path):
            self.load_image(path)

    def render_pil_to_canvas(self, pil_img):
        bytes_io = io.BytesIO()
        pil_img.save(bytes_io, format="PNG")
        qimg = QImage.fromData(bytes_io.getvalue())
        pix = QPixmap.fromImage(qimg)
        self.viewer.pixmap_item.setPixmap(pix)
        self.viewer.scene.setSceneRect(QRectF(pix.rect()))
        self.viewer.crop_box.setVisible(False)

    def apply_pixel_resize(self):
        if not self.current_pil_image:
            return
        nw, nh = self.w_spin.value(), self.h_spin.value()
        self.current_pil_image = self.current_pil_image.resize((nw, nh), Image.Resampling.LANCZOS)
        self.render_pil_to_canvas(self.current_pil_image)
        self.status.showMessage(f"Resized: {nw}x{nh} px")

    def execute_crop(self):
        if not self.viewer.crop_box.isVisible():
            return
        rect = self.viewer.crop_box.rect()
        box = (int(rect.left()), int(rect.top()), int(rect.right()), int(rect.bottom()))
        self.current_pil_image = self.current_pil_image.crop(box)
        self.w_spin.setValue(self.current_pil_image.width)
        self.h_spin.setValue(self.current_pil_image.height)
        self.render_pil_to_canvas(self.current_pil_image)

    def set_preset_crop(self, ratio):
        if not self.current_pil_image:
            return
        w = self.current_pil_image.width * 0.7
        h = w / ratio
        rect = QRectF(20, 20, w, h)
        self.viewer.crop_box.setRect(rect)
        self.viewer.crop_box.setVisible(True)

    def auto_crop_signature(self):
        if not self.current_pil_image:
            return
        gray = self.current_pil_image.convert("L")
        bw = gray.point(lambda x: 0 if x > 195 else 255, '1')
        bbox = bw.getbbox()
        if bbox:
            pad = 10
            crop_box = (
                max(0, bbox[0] - pad),
                max(0, bbox[1] - pad),
                min(self.current_pil_image.width, bbox[2] + pad),
                min(self.current_pil_image.height, bbox[3] + pad)
            )
            self.current_pil_image = self.current_pil_image.crop(crop_box)
            self.w_spin.setValue(self.current_pil_image.width)
            self.h_spin.setValue(self.current_pil_image.height)
            self.render_pil_to_canvas(self.current_pil_image)
            self.status.showMessage("Signature auto-cropped!")

    def update_image_adjustments(self):
        if not self.original_pil_image:
            return
        angle = self.rot_slider.value()
        img = self.original_pil_image.rotate(-angle, expand=True, resample=Image.Resampling.BICUBIC)
        b_val = 1.0 + (self.bright_slider.value() / 50.0)
        img = ImageEnhance.Brightness(img).enhance(b_val)
        c_val = 1.0 + (self.cont_slider.value() / 50.0)
        img = ImageEnhance.Contrast(img).enhance(c_val)
        self.current_pil_image = img
        self.render_pil_to_canvas(self.current_pil_image)

    def print_image(self):
        if not self.current_pil_image:
            return
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            painter = QPainter(printer)
            bytes_io = io.BytesIO()
            self.current_pil_image.save(bytes_io, format="PNG")
            qimg = QImage.fromData(bytes_io.getvalue())
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
        kb_text = self.target_kb_combo.currentText()
        target_kb = int(kb_text.replace(" KB", ""))
        target_bytes = target_kb * 1024

        save_path, _ = QFileDialog.getSaveFileName(self, "Export Target Image", f"Optimized_{target_kb}KB.jpg", "JPEG Image (*.jpg)")
        if not save_path:
            return

        img = self.current_pil_image.copy()
        min_q, max_q = 5, 95
        best_data = None

        for _ in range(8):
            mid_q = (min_q + max_q) // 2
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=mid_q, optimize=True)
            size = buf.tell()
            if size <= target_bytes:
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
            with open(save_path, "wb") as f:
                f.write(best_data)
            actual_kb = len(best_data) / 1024
            QMessageBox.information(self, "Export Success", f"Saved successfully!\nFile Size: {actual_kb:.2f} KB (Target: {target_kb} KB)")

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
