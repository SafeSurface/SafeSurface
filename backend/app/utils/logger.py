import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    """Configure and return a professional logger instance."""
    logger = logging.getLogger(name)
    
    # Only configure if handlers are not already set up
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Standard output handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Prevent propagation to the root logger
        logger.propagate = False
        
    return logger

# Global default logger
logger = setup_logger("safesurface")
