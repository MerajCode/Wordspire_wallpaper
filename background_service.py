import os
import ctypes
import time
from fetch_data import FetchData
import sys
import threading

try:
    import win32gui
except ImportError:
    win32gui = None

gen = FetchData()

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.getenv("APPDATA"), "Wordspire_by_merajcode")
    else:
        return os.path.dirname(os.path.abspath(__file__))

def is_on_desktop():
    """Checks if the foreground window is the desktop using a more reliable method."""
    if not win32gui:
        return False
    try:
        hwnd = win32gui.GetForegroundWindow()
        class_name = win32gui.GetClassName(hwnd)
        return class_name in ['Progman', 'WorkerW'] or win32gui.GetWindowText(hwnd) == ""
    except Exception:
        return False

def change_wallpaper(image_path):
    """Changes the wallpaper and handles potential errors."""
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
    except Exception as e:
        print(f"❌ Failed to set wallpaper: {e}")

def cleanup_old_wallpapers(assets_folder):
    """Deletes old jpg files to save space."""
    try:
        for f in os.listdir(assets_folder):
            if f.lower().endswith('.jpg'):
                os.remove(os.path.join(assets_folder, f))
    except Exception as e:
        print(f"⚠️ Could not clean up old wallpapers: {e}")

def start_monitoring(folder_path, stop_event, interval=2):
    base_dir = get_base_path()
    assets_folder = os.path.join(base_dir, "assets")
    
    # Ensure the assets folder exists
    os.makedirs(assets_folder, exist_ok=True)

    last_state_is_desktop = False

    while not stop_event.is_set():
        try:
            if is_on_desktop():
                if not last_state_is_desktop:
                    # Generate a unique filename to avoid locking issues
                    timestamp = int(time.time())
                    new_wallpaper_path = os.path.join(assets_folder, f"wallpaper_{timestamp}.jpg")

                    # Clean up previous wallpapers *before* creating a new one
                    cleanup_old_wallpapers(assets_folder)

                    from generate_wallpaper import quote_image
                    data = gen.get_next_data()
                    print(f"Generating new wallpaper: {new_wallpaper_path}")
                    
                    quote_image(data, output_file=new_wallpaper_path, scale=1)
                    time.sleep(0.5)
                    change_wallpaper(new_wallpaper_path)
                    
                    print("✅ Wallpaper generated and applied.")
                
                last_state_is_desktop = True
            else:
                if last_state_is_desktop:
                    # Refresh data only once when moving away from the desktop
                    gen.refresh_data()
                last_state_is_desktop = False

        except Exception as e:
            # This is the most important part: catch any error to keep the thread alive
            print(f"🚨 An error occurred in the monitoring loop: {e}")
            # Optional: wait a bit longer after an error to avoid spamming logs
            time.sleep(5)

        time.sleep(interval)