import pychromecast
import zeroconf
import time

def main():
    # Create a zeroconf instance
    zconf = zeroconf.Zeroconf()
    browser = None
    known_devices = {}  # Dict để lưu các thiết bị đã biết: uuid -> status
    
    try:
        while True:
            # Discover Chromecasts
            chromecasts, browser = pychromecast.get_chromecasts(zeroconf_instance=zconf)
            
            for cast in chromecasts:
                device_id = cast.cast_info.uuid
                
                # Nếu là thiết bị mới hoặc chưa start
                if device_id not in known_devices:
                    cast.wait()
                    print(f"\nNew Chromecast Found: {cast.cast_info.friendly_name} - {device_id} - {cast.cast_info.host}")
                    
                    # Force stop current app
                    print(f"Checking current app on {cast.cast_info.friendly_name}...")
                    if cast.app_id:
                        print(f"Stopping current app: {cast.app_id}")
                        cast.quit_app()
                        time.sleep(1)
                    
                    # Launch our app
                    print(f"Launching app on {cast.cast_info.friendly_name}...")
                    cast.start_app("A2614071")
                    time.sleep(1)
                    
                    print(f"Current app ID: {cast.app_id}")
                    if cast.app_id == "A2614071":
                        print("App launched successfully!")
                        known_devices[device_id] = True  # Đánh dấu đã start
                    else:
                        print(f"Failed to launch app. Current app ID: {cast.app_id}")
                        known_devices[device_id] = False  # Đánh dấu chưa start thành công
            
            # Kiểm tra thiết bị đã biết còn online không
            current_uuids = [cast.cast_info.uuid for cast in chromecasts]
            offline_devices = [uuid for uuid in known_devices.keys() if uuid not in current_uuids]
            
            # Xóa các thiết bị offline
            for uuid in offline_devices:
                print(f"\nDevice {uuid} went offline, removing from known devices")
                del known_devices[uuid]
            
            # Wait before next check
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nStopping discovery...")
    finally:
        # Clean up
        if browser:
            browser.stop_discovery()
        zconf.close()

if __name__ == "__main__":
    main()