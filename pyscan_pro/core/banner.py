import socket
from typing import Optional

def grab_banner(ip: str, port: int, timeout: float = 2.0) -> Optional[str]:
    """
    Attempts to connect to a port and receive its banner.
    It can send protocol-specific probes if no data is received immediately.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((ip, port))
            
            # For HTTP/HTTPS, we usually need to send a request first
            if port in (80, 443, 8080):
                probe = b"HEAD / HTTP/1.0\r\n\r\n"
                s.sendall(probe)
            elif port == 25: # SMTP 
                 probe = b"HELO default\r\n"
                 s.sendall(probe)
            
            banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
            if banner:
                # Return the first line of the banner to keep it clean
                return banner.split('\n')[0].strip()
    except Exception:
        pass
    
    return None
