"""Check if Fake Tool GUI is running"""
import psutil
import sys

def check_running_gui():
    """Check if main_gui.py or launch.py is running"""
    print("Checking for running Fake Tool processes...")
    print("=" * 60)
    
    found_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline:
                cmdline_str = ' '.join(cmdline)
                
                # Check for our scripts
                if 'main_gui.py' in cmdline_str or 'launch.py' in cmdline_str:
                    found_processes.append(proc)
                    print(f"\n✓ FOUND: {proc.info['name']}")
                    print(f"  PID: {proc.info['pid']}")
                    print(f"  Status: {proc.info['status']}")
                    print(f"  Command: {cmdline_str}")
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    print("\n" + "=" * 60)
    
    if found_processes:
        print(f"\n✓ Found {len(found_processes)} Fake Tool process(es) running")
        print("\nThe GUI should be visible. Check:")
        print("  1. Your taskbar for the window")
        print("  2. Alt+Tab to switch to it")
        print("  3. Other monitors if you have multiple displays")
    else:
        print("\n✗ No Fake Tool GUI processes found")
        print("  The GUI is not currently running")
    
    return len(found_processes) > 0

if __name__ == "__main__":
    # Make sure psutil is available
    try:
        import psutil
    except ImportError:
        print("ERROR: psutil not installed")
        print("Installing psutil...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil
    
    is_running = check_running_gui()
    sys.exit(0 if is_running else 1)
