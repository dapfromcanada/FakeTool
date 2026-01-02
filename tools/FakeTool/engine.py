"""
Fake Tool Engine - Headless Image Processing
This engine can be run from CLI without GUI dependencies
"""

import argparse
import logging
import json
import sys
from pathlib import Path
from datetime import datetime
from PIL import Image
import os


class FakeToolEngine:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.status_file = Path(__file__).parent / "logs" / "fake_tool_status.json"
        
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def setup_logging(self):
        """Setup twin-stream logging (console + file)"""
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"FakeTool_{timestamp}.log"
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Setup file handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # Setup console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        # Configure logger
        self.logger = logging.getLogger('FakeToolEngine')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info("FakeTool Engine initialized")
    
    def update_status(self, status, progress, message):
        """Write status to JSON file for GUI monitoring"""
        status_data = {
            "status": status,
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to update status: {e}")
    
    def get_image_info(self, image_path):
        """Get detailed information about an image"""
        try:
            img_path = Path(image_path)
            if not img_path.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            with Image.open(img_path) as img:
                info = {
                    "path": str(img_path),
                    "filename": img_path.name,
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "file_size": img_path.stat().st_size,
                    "file_size_mb": round(img_path.stat().st_size / (1024 * 1024), 2)
                }
                
                self.logger.info(f"Image analyzed: {img_path.name} - {img.size[0]}x{img.size[1]} - {info['file_size_mb']}MB")
                return info
                
        except Exception as e:
            self.logger.error(f"Error analyzing image: {e}")
            raise
    
    def process_folder(self, folder_path):
        """Scan folder for images and process them"""
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            raise ValueError(f"Invalid folder path: {folder_path}")
        
        supported_formats = self.config.get("options", {}).get("supported_formats", [])
        image_files = []
        
        self.logger.info(f"Scanning folder: {folder}")
        self.update_status("running", 0, f"Scanning {folder}")
        
        for ext in supported_formats:
            pattern = f"*.{ext}"
            found = list(folder.glob(pattern))
            image_files.extend(found)
            self.logger.info(f"Found {len(found)} {ext} files")
        
        self.logger.info(f"Total images found: {len(image_files)}")
        self.update_status("completed", 100, f"Found {len(image_files)} images")
        
        return image_files
    
    def run(self, test_mode=False):
        """Main execution method"""
        try:
            self.logger.info("="*50)
            self.logger.info("FakeTool Engine started")
            self.logger.info(f"Test mode: {test_mode}")
            self.logger.info("="*50)
            
            self.update_status("running", 0, "Engine started")
            
            if test_mode:
                self.logger.info("Running in TEST mode")
                self.logger.info("Configuration loaded successfully")
                self.logger.info(f"Supported formats: {self.config.get('options', {}).get('supported_formats', [])}")
                self.update_status("completed", 100, "Test completed successfully")
                return True
            
            # In normal mode, engine waits for commands
            self.logger.info("Engine ready for image processing")
            self.update_status("ready", 0, "Waiting for commands")
            
            return True
            
        except KeyboardInterrupt:
            self.logger.info("Engine stopped by user")
            self.update_status("stopped", 0, "Stopped by user")
            return False
        except Exception as e:
            self.logger.error(f"Engine error: {e}", exc_info=True)
            self.update_status("error", 0, f"Error: {str(e)}")
            raise


def main():
    parser = argparse.ArgumentParser(description='FakeTool Image Processing Engine')
    parser.add_argument('--config', required=True, help='Path to config.json')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--image', help='Path to image file to analyze')
    parser.add_argument('--folder', help='Path to folder to scan')
    
    args = parser.parse_args()
    
    try:
        engine = FakeToolEngine(args.config)
        
        if args.image:
            info = engine.get_image_info(args.image)
            print(json.dumps(info, indent=2))
        elif args.folder:
            images = engine.process_folder(args.folder)
            print(f"Found {len(images)} images")
            for img in images:
                print(f"  - {img.name}")
        else:
            engine.run(test_mode=args.test)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
