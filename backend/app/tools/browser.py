import json
import time
from typing import Dict, Optional, List
from langchain_core.tools import tool
from bs4 import BeautifulSoup
from app.utils.logger import setup_logger

logger = setup_logger("tools.browser")

# Playwright setup
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    logger.error("Playwright is not installed. Please install it with 'pip install playwright' and 'playwright install'")

@tool
def execute_browser_automation(
    url: str, 
    actions: List[Dict] = [], 
    extract_html: bool = True, 
    capture_packets: bool = False
) -> str:
    """
    Advanced Browser Automation Tool. Navigates to a URL, optionally performs actions (click, type),
    and can capture resulting HTML and network packets.
    
    Args:
        url: The starting URL to navigate to.
        actions: A list of dicts specifying actions. Example: 
                 [{"type": "fill", "selector": "#username", "value": "admin"},
                  {"type": "click", "selector": "button[type='submit']"}]
        extract_html: Whether to return the parsed DOM text (useful for crawling).
        capture_packets: Whether to intercept and return the HTTP requests made during the session.
    """
    logger.info(f"Starting browser automation for {url}")
    results = {}
    packets = []

    try:
        with sync_playwright() as p:
            # Fallback to local chrome if playwright fails to install headless browser correctly
            browser = p.chromium.launch(headless=True, channel="chrome")
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            
            # --- Network Interception (抓包) ---
            if capture_packets:
                def record_request(request):
                    pass # Only record basic info to avoid flooding context window
                def record_response(response):
                    try:
                        # Log the response of potential target endpoints
                        packets.append({
                            "url": response.url,
                            "status": response.status,
                            "method": response.request.method,
                        })
                    except Exception:
                        pass
                page.on("response", record_response)

            # --- Navigation ---
            page.goto(url, wait_until="networkidle", timeout=15000)

            # --- Actions (点击、输入) ---
            for action in actions:
                act_type = action.get("type")
                selector = action.get("selector")
                
                try:
                    if act_type == "fill":
                        val = action.get("value", "")
                        page.fill(selector, val)
                        logger.info(f"Filled {selector} with ***")
                    elif act_type == "click":
                        page.click(selector)
                        logger.info(f"Clicked {selector}")
                        # Wait a little for any resulting navigation or ajax
                        page.wait_for_timeout(1500)
                    elif act_type == "wait":
                        ms = action.get("value", 1000)
                        page.wait_for_timeout(ms)
                except PlaywrightTimeout:
                    logger.warning(f"Timeout performing action: {action}")
                    results["warning"] = f"Action timeout on {selector}"
                    break

            # Let JS settle
            page.wait_for_timeout(1000)
            
            # --- Extraction (爬虫提取) ---
            new_url = page.url
            results["final_url"] = new_url
            
            if extract_html:
                raw_html = page.content()
                soup = BeautifulSoup(raw_html, "html.parser")
                # Extract text heavily compressed
                text_content = soup.get_text(separator=" | ", strip=True)
                # Cap the output to save LLM context
                results["page_text"] = text_content[:3000] 
                
                # Extract inputs (forms) - extremely useful for Recon and Brute Force!
                forms_info = []
                for form in soup.find_all("form"):
                    f_info = {"action": form.get("action"), "method": form.get("method")}
                    inputs = []
                    for inp in form.find_all(["input", "textarea"]):
                        inputs.append({"name": inp.get("name"), "type": inp.get("type"), "value": inp.get("value")})
                    f_info["inputs"] = inputs
                    forms_info.append(f_info)
                results["forms_found"] = forms_info

            if capture_packets:
                results["captured_packets"] = packets[:20] # Take max 20 to avoid token bloat

            browser.close()
            return json.dumps(results, indent=2)

    except Exception as e:
        logger.error(f"Browser automation failed: {e}")
        return json.dumps({"error": str(e)})