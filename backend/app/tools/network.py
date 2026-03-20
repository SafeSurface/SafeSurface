import urllib.request
from urllib.error import HTTPError, URLError
from langchain_core.tools import tool
from typing import Dict, Any, Optional
import json

from app.utils.logger import setup_logger

logger = setup_logger("tools.network")

@tool
def http_request_probe(url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None, body: Optional[str] = None, timeout: int = 10) -> str:
    """
    Perform an HTTP request for security probing or reconnaissance.
    Avoids high-level libraries like 'requests' to prevent unwanted redirects or default headers.
    
    Args:
        url: The target URL to probe.
        method: HTTP method to use (e.g., GET, POST, HEAD, OPTIONS).
        headers: A dictionary of HTTP headers to inject.
        body: Raw HTTP body to send with the request.
        timeout: Request timeout in seconds.
    """
    logger.info(f"Probing {url} with method {method}")
    
    req_headers = headers or {}
    if "User-Agent" not in req_headers:
        req_headers["User-Agent"] = "Mozilla/5.0 (compatible; SafeSurface-Recon/1.0)"
        
    req_data = body.encode('utf-8') if body else None
    
    req = urllib.request.Request(
        url, 
        data=req_data, 
        headers=req_headers, 
        method=method.upper()
    )
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_body = resp.read().decode(errors="ignore")
            result = {
                "status": resp.status,
                "length": len(resp_body),
                "headers": dict(resp.headers),
                "body": resp_body[:2000] # Truncate to save context window
            }
            logger.info(f"Probe successful: {resp.status}")
            return json.dumps(result, indent=2)
            
    except HTTPError as e:
        # In security probing, 4xx and 5xx are common and often exactly what we want to analyze.
        error_body = e.read().decode(errors="ignore") if e.fp else ""
        result = {
            "status": e.code,
            "length": len(error_body),
            "headers": dict(e.headers) if hasattr(e, 'headers') else {},
            "body": error_body[:2000]
        }
        logger.info(f"Probe returned HTTP error: {e.code}")
        return json.dumps(result, indent=2)
    except URLError as e:
        logger.warning(f"Probe failed to reach target: {e.reason}")
        return f"ERROR: Could not reach {url} - {e.reason}"
    except Exception as e:
        logger.error(f"Unexpected probe error: {e}")
        return f"ERROR: {str(e)}"