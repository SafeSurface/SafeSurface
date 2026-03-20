import subprocess
from typing import Dict
from langchain_core.tools import tool
from app.utils.logger import setup_logger

logger = setup_logger("tools.system")

@tool
def execute_system_command(command: str, os_type: str = "windows", timeout: int = 30) -> str:
    """
    Execute a local system command. Useful for network reconnaissance, file manipulation, etc.
    
    Args:
        command: The actual shell command to execute.
        os_type: The operating system type. Options are "windows", "linux". Default is "windows".
        timeout: Execution timeout in seconds.
    """
    logger.info(f"Executing command: {command} on {os_type}")
    try:
        if os_type == "windows":
            # Execute on Windows using cmd.exe
            cmd_command = f'cmd /c "{command}"'
            result = subprocess.run(
                cmd_command,
                shell=False,  
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="ignore"
            )
        else:
            # Execute on Linux/macOS
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                executable="/bin/bash"
            )
        
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        output = []
        if stdout:
            output.append(f"STDOUT:\n{stdout}")
        if stderr:
            output.append(f"STDERR:\n{stderr}")
            
        if not output:
            return "Command executed successfully with no output."
            
        return "\n\n".join(output)
        
    except subprocess.TimeoutExpired:
        logger.warning(f"Command execution timed out after {timeout} seconds.")
        return "ERROR: Command execution timed out."
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        return f"ERROR: Failed to execute command - {str(e)}"