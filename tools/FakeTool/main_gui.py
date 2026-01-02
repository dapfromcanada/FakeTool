"""
Fake Tool - Image Viewer GUI
Loads interface.ui dynamically and displays images with folder browsing
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QFileDialog, 
                               QListWidgetItem, QMessageBox)
from PySide6.QtCore import QTimer, QFile, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
import json


class FakeToolGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load UI file
        self.load_ui()
        
        # Initialize variables
        self.current_folder = None
        self.current_image = None
        self.engine_process = None
        self.config_path = Path(__file__).parent / "config.json"
        self.status_file = Path(__file__).parent / "logs" / "fake_tool_status.json"
        
        # Load configuration
        self.load_config()
        
        # Connect UI signals
        self.connect_signals()
        
        # Setup status monitoring
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_engine_status)
        
        # Initialize UI
        self.log_message("FakeTool initialized and ready")
        self.update_status("Ready")
    
    def load_ui(self):
        """Load the UI file dynamically using QUiLoader"""
        ui_path = Path(__file__).parent / "interface.ui"
        
        if not ui_path.exists():
            raise FileNotFoundError(f"UI file not found: {ui_path}")
        
        # Load UI with QUiLoader
        ui_file = QFile(str(ui_path))
        if not ui_file.open(QFile.ReadOnly):
            raise RuntimeError(f"Cannot open UI file: {ui_path}")
            
        loader = QUiLoader()
        loaded_window = loader.load(ui_file, None)
        ui_file.close()
        
        if loaded_window is None:
            raise RuntimeError("Failed to load UI")
        
        # The loaded UI is a QMainWindow, so we need to extract its central widget
        central_widget = loaded_window.centralWidget()
        
        # Set it as our central widget
        self.setCentralWidget(central_widget)
        
        # Get references to UI widgets from the central widget
        from PySide6.QtWidgets import QPushButton, QLineEdit, QListWidget, QLabel, QPlainTextEdit
        
        self.btn_browse_folder = central_widget.findChild(QPushButton, "btn_browse_folder")
        self.btn_browse_image = central_widget.findChild(QPushButton, "btn_browse_image")
        self.btn_clear_log = central_widget.findChild(QPushButton, "btn_clear_log")
        self.list_images = central_widget.findChild(QListWidget, "list_images")
        self.txt_folder_path = central_widget.findChild(QLineEdit, "txt_folder_path")
        self.lbl_image_display = central_widget.findChild(QLabel, "lbl_image_display")
        self.lbl_image_info = central_widget.findChild(QLabel, "lbl_image_info")
        self.txt_log_display = central_widget.findChild(QPlainTextEdit, "txt_log_display")
        self.lbl_status = central_widget.findChild(QLabel, "lbl_status")
        
        # Set window properties
        self.setWindowTitle("Fake Tool - Image Viewer")
        self.resize(900, 700)
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            self.log_message(f"Configuration loaded from {self.config_path.name}")
        except Exception as e:
            self.log_message(f"Error loading config: {e}")
            # Use default config
            self.config = {
                "options": {
                    "supported_formats": ["jpg", "jpeg", "png", "bmp", "gif", "tiff"]
                }
            }
    
    def connect_signals(self):
        """Connect UI widget signals to methods"""
        self.btn_browse_folder.clicked.connect(self.browse_folder)
        self.btn_browse_image.clicked.connect(self.browse_image)
        self.btn_clear_log.clicked.connect(self.clear_log)
        self.list_images.itemClicked.connect(self.on_image_selected)
    
    def browse_folder(self):
        """Open folder dialog and load images from selected folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Image Folder",
            str(Path.home()),
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.current_folder = Path(folder)
            self.txt_folder_path.setText(str(self.current_folder))
            self.log_message(f"Folder selected: {self.current_folder}")
            self.load_images_from_folder()
    
    def browse_image(self):
        """Open file dialog to select a single image"""
        supported_formats = self.config.get("options", {}).get("supported_formats", [])
        filter_str = "Images (" + " ".join([f"*.{fmt}" for fmt in supported_formats]) + ")"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image File",
            str(Path.home()),
            filter_str
        )
        
        if file_path:
            self.load_single_image(Path(file_path))
    
    def load_images_from_folder(self):
        """Load all images from the current folder into the list"""
        if not self.current_folder:
            return
        
        self.list_images.clear()
        self.update_status("Loading images...")
        
        supported_formats = self.config.get("options", {}).get("supported_formats", [])
        image_files = []
        
        # Find all image files
        for ext in supported_formats:
            pattern = f"*.{ext}"
            found = list(self.current_folder.glob(pattern))
            image_files.extend(found)
        
        # Add to list widget
        for img_path in sorted(image_files):
            item = QListWidgetItem(img_path.name)
            item.setData(Qt.UserRole, str(img_path))
            self.list_images.addItem(item)
        
        count = len(image_files)
        self.log_message(f"Loaded {count} images from folder")
        self.update_status(f"Ready - {count} images found")
    
    def on_image_selected(self, item):
        """Handle image selection from list"""
        image_path = Path(item.data(Qt.UserRole))
        self.load_single_image(image_path)
    
    def load_single_image(self, image_path):
        """Load and display a single image"""
        try:
            if not image_path.exists():
                self.log_message(f"Error: Image not found - {image_path}")
                return
            
            # Load image
            pixmap = QPixmap(str(image_path))
            
            if pixmap.isNull():
                self.log_message(f"Error: Failed to load image - {image_path.name}")
                return
            
            # Scale image to fit label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.lbl_image_display.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.lbl_image_display.setPixmap(scaled_pixmap)
            self.current_image = image_path
            
            # Update image info
            file_size_mb = image_path.stat().st_size / (1024 * 1024)
            info_text = f"{image_path.name} | {pixmap.width()}x{pixmap.height()} | {file_size_mb:.2f} MB"
            self.lbl_image_info.setText(info_text)
            
            # Log the action
            self.log_message(f"Loaded: {image_path.name} ({pixmap.width()}x{pixmap.height()})")
            self.update_status(f"Image loaded: {image_path.name}")
            
            # Call engine to process image info (demonstration of subprocess)
            self.call_engine_analyze(image_path)
            
        except Exception as e:
            self.log_message(f"Error loading image: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load image:\n{e}")
    
    def call_engine_analyze(self, image_path):
        """Call engine.py as subprocess to analyze image"""
        try:
            # Get python executable from venv
            venv_python = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
            engine_script = Path(__file__).parent / "engine.py"
            
            if not venv_python.exists():
                # Fallback to system python
                venv_python = "python"
            
            # Run engine in background to analyze image
            result = subprocess.run(
                [str(venv_python), str(engine_script), 
                 "--config", str(self.config_path),
                 "--image", str(image_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse JSON output from engine
                try:
                    info = json.loads(result.stdout)
                    self.log_message(f"Engine analysis: {info['format']} format, {info['mode']} mode")
                except Exception:
                    pass
            
        except subprocess.TimeoutExpired:
            self.log_message("Engine analysis timed out")
        except Exception:
            self.log_message("Engine call failed")
    
    def check_engine_status(self):
        """Check engine status from JSON file"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
                    message = status.get('message', 'Unknown')
                    self.update_status(f"Engine: {message}")
        except Exception as e:
            pass  # Silent fail for status checks
    
    def log_message(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.txt_log_display.appendPlainText(log_entry)
    
    def clear_log(self):
        """Clear the log display"""
        self.txt_log_display.clear()
        self.log_message("Log cleared")
    
    def update_status(self, message):
        """Update status label"""
        self.lbl_status.setText(f"Status: {message}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Cleanup: stop engine process if running
        if self.engine_process and self.engine_process.poll() is None:
            self.engine_process.terminate()
        
        self.log_message("FakeTool closed")
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    try:
        window = FakeToolGUI()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error starting FakeTool: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
