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
            
        cast = chromecasts[0]
        cast.wait()
        print(f"Chromecast Found: {cast.cast_info.friendly_name} - {cast.cast_info.uuid} - {cast.cast_info.host}")
        
        # Force stop current app
        print("Checking current app...")
        if cast.app_id:
            print(f"Stopping current app: {cast.app_id}")
            cast.quit_app()
            time.sleep(2)  # Wait for app to stop
        
        # Launch our app
        print("Launching app on {}...".format(cast.cast_info.friendly_name))
        cast.start_app("A2614071")
        time.sleep(2)  # Wait for app to start
        
        print(f"Current app ID: {cast.app_id}")
        print(f"Status: {'Connected' if cast.socket_client.connecting else 'Disconnected'}")
        
        if cast.app_id == "A2614071":
            print("App launched successfully!")
        else:
            print(f"Failed to launch app. Current app ID: {cast.app_id}")
            
    finally:
        # Clean up
        browser.stop_discovery()
        zconf.close()

if __name__ == "__main__":
    main()
