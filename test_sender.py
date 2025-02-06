import pychromecast
import zeroconf
import time

def main():
    zconf = zeroconf.Zeroconf()
    
    try:
        # Discover Chromecasts
        chromecasts, browser = pychromecast.get_chromecasts(zeroconf_instance=zconf)
        
        if not chromecasts:
            print("No Chromecast devices found")
            return
            
        for cast in chromecasts:
            try:
                cast.wait(timeout=10)
                print(f"\nFound device: {cast.cast_info.friendly_name}")
                print(f"Current app ID: {cast.app_id}")
                
                # Check if any app is running
                if cast.app_id is not None:
                    print("Stopping current app...")
                    cast.quit_app()
                    time.sleep(2)  # Wait for app to close
                    print("Current app stopped")
                
                # Launch our app
                print("\nLaunching receiver app...")
                cast.start_app("A2614071")
                time.sleep(2)  # Wait for app to start
                
                if cast.app_id == "A2614071":
                    print("Receiver app launched successfully!")
                    
                    # Send test message
                    print("Sending test message...")
                    cast.send_message("urn:x-cast:com.example.cast.custom", {
                        "type": "test",
                        "message": "Hello from sender!",
                        "timestamp": time.time()
                    })
                else:
                    print(f"Failed to launch app. Current app ID: {cast.app_id}")
                
            except pychromecast.error.ChromecastConnectionError:
                print(f"Could not connect to device {cast.cast_info.host}")
            except pychromecast.error.RequestTimeout:
                print(f"Timeout while connecting to device {cast.cast_info.host}")
            except Exception as e:
                print(f"Error: {str(e)}")
                print(f"Error type: {type(e)}")
                
    finally:
        browser.stop_discovery()
        zconf.close()

if __name__ == "__main__":
    main() 