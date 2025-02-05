import pychromecast
import zeroconf
import time
from pychromecast.config import get_app_config

def main():
    # Create a zeroconf instance
    zconf = zeroconf.Zeroconf()
    
    try:
        # Discover Chromecasts
        chromecasts, browser = pychromecast.get_chromecasts(zeroconf_instance=zconf)
        
        # Print discovered devices
        if not chromecasts:
            print("No Chromecast devices found")
            return
            
        for cast in chromecasts:
            try:
                cast.wait(timeout=10)  # Wait with timeout to avoid hanging
                print(f"Chromecast Found: {cast.cast_info.friendly_name} - {cast.cast_info.uuid} - {cast.cast_info.host}")
                
                # Get app configuration
                app_id = "A2614071"
                app_config = get_app_config(app_id)
                if not app_config:
                    print(f"Warning: No configuration found for app ID {app_id}")
                
                # Launch the app with ID A2614071
                print(f"Launching app on {cast.cast_info.friendly_name}...")
                print(f"Current app ID: {cast.app_id}")
                print(f"Connection status: {cast.socket_client.is_connected}")
                
                cast.start_app(app_id)
                time.sleep(2)  # Give it a moment to launch
                
                if cast.app_id == app_id:
                    print("App launched successfully!")
                else:
                    print(f"App launch failed. Current app ID: {cast.app_id}")
                
            except pychromecast.error.ChromecastConnectionError:
                print(f"Could not connect to device {cast.cast_info.host}")
            except pychromecast.error.RequestTimeout:
                print(f"Timeout while connecting to device {cast.cast_info.host}")
            except Exception as e:
                print(f"Error launching app: {str(e)}")
                print(f"Error type: {type(e)}")
                
    finally:
        # Clean up
        browser.stop_discovery()
        zconf.close()

if __name__ == "__main__":
    main()
