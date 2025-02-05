import pychromecast
import zeroconf
import time
import json

def main():
    zconf = zeroconf.Zeroconf()
    
    try:
        chromecasts, browser = pychromecast.get_chromecasts(zeroconf_instance=zconf)
        
        if not chromecasts:
            print("No Chromecast devices found")
            return
            
        for cast in chromecasts:
            try:
                cast.wait(timeout=10)
                print(f"\nTesting with: {cast.cast_info.friendly_name}")
                
                # Launch app
                print("Launching app...")
                cast.start_app("A2614071")
                time.sleep(2)
                
                # Send test messages
                test_messages = [
                    {"type": "init", "message": "Initialize connection"},
                    {"type": "test", "message": "Test message 1"},
                    {"type": "status", "message": "Check status"}
                ]
                
                for msg in test_messages:
                    print(f"\nSending message: {msg}")
                    cast.send_message("urn:x-cast:com.example.cast.custom", msg)
                    time.sleep(1)  # Wait for response
                
            except Exception as e:
                print(f"Error: {str(e)}")
                print(f"Error type: {type(e)}")
                
    finally:
        browser.stop_discovery()
        zconf.close()

if __name__ == "__main__":
    main() 