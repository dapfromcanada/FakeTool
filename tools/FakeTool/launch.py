"""Simple launcher with error output"""
import sys

try:
    print("Starting Fake Tool GUI...")
    print(f"Python: {sys.version}")
    print(f"Path: {sys.executable}")
    
    from main_gui import main
    main()
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
