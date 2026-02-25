import socket
import logging

try:
    from scapy.all import sr1, IP, TCP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
except Exception:
    SCAPY_AVAILABLE = False

logger = logging.getLogger("PyScanPro.SYN")

def simulate_syn_scan(ip: str, port: int, timeout: float = 2.0) -> str:
    """
    Simulates a TCP SYN scan.
    Returns: 'OPEN', 'CLOSED', or 'FILTERED'.
    
    Educational Explanation:
    In a true SYN scan (half-open scan), we send a SYN packet.
    - If the port is OPEN, the server responds with SYN-ACK. We then send an RST to close it.
    - If CLOSED, the server responds with RST.
    - If FILTERED (e.g., by a firewall), we receive no response or an ICMP unreachable error.
    """
    if SCAPY_AVAILABLE:
        # Note: Scapy usually requires root/administrative privileges on most systems to craft raw packets.
        # This is Option A from the specification.
        try:
            # Craft a TCP SYN packet
            syn_pkt = IP(dst=ip)/TCP(dport=port, flags='S')
            
            # Send packet and wait for a single response
            # sr1 = Send and receive 1 packet
            response = sr1(syn_pkt, timeout=timeout, verbose=0)
            
            if response is None:
                return 'FILTERED' # No response implies filtered
                
            elif response.haslayer(TCP):
                if response.getlayer(TCP).flags == 0x12: # SYN-ACK
                    # It's open. Should send RST here to tear down gracefully.
                    # rst_pkt = IP(dst=ip)/TCP(dport=port, flags='R')
                    # send(rst_pkt, verbose=0)
                    return 'OPEN'
                elif response.getlayer(TCP).flags == 0x14: # RST-ACK
                    return 'CLOSED'
                    
            return 'FILTERED' # Other conditions like ICMP error
            
        except PermissionError:
            # Fallback will trigger if Scapy fails due to permissions without crashing it 
            logger.warning("Scapy SYN scan requires elevated privileges. Falling back to simulation mode.")
            return _fallback_syn_scan(ip, port, timeout)
            
        except Exception as e:
            logger.error(f"Error in Scapy SYN scan: {e}")
            return _fallback_syn_scan(ip, port, timeout)
    else:
        # Option B from specification: Fallback Simulation via connection timing
        return _fallback_syn_scan(ip, port, timeout)
        
def _fallback_syn_scan(ip: str, port: int, timeout: float) -> str:
    """
    Option B (Fallback Simulation):
    Simulates half-open logic using timing behavior.
    
    Limitations:
    This is not a true half-open scan at the packet level. It uses the OS's 
    standard full-connect mechanism (connect_ex). A real SYN scan does not 
    complete the 3-way handshake, avoiding logs on the target system. 
    This simulation completes the handshake if the port is open but 
    tears it down immediately.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            
            if result == 0:
                return 'OPEN'
            elif result == 111 or result == 10061: # Connection Refused (Linux/Win)
                return 'CLOSED'
            elif result == 110 or result == 10060: # Connection Timed Out
                return 'FILTERED'
            else:
                return 'CLOSED'
    except socket.timeout:
        return 'FILTERED'
    except Exception:
        return 'CLOSED'
