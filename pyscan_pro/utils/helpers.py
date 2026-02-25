import ipaddress
import socket
from typing import List

def parse_target(target: str) -> List[str]:
    """
    Parses the target string which could be a single IP, a domain, or a CIDR subnet.
    Returns a list of IP addresses as strings to be scanned.
    """
    targets = []
    
    # Check if it's a CIDR network
    if '/' in target:
        try:
            network = ipaddress.ip_network(target, strict=False)
            targets = [str(ip) for ip in network.hosts()]
        except ValueError:
            pass # Not a valid CIDR
            
    # Check if it's a single IP or Domain
    if not targets:
        try:
            # Resolves domain to IP if a domain is passed, otherwise validates IP
            ip = socket.gethostbyname(target)
            targets.append(ip)
        except socket.gaierror:
            pass # Could not resolve hostname
            
    return targets

def parse_ports(port_range: str) -> List[int]:
    """
    Parses a string of ports (e.g., '80,443', '1-100', or '80').
    Returns a list of integer ports.
    """
    ports = set()
    parts = [p.strip() for p in port_range.split(',')]
    
    for part in parts:
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                ports.update(range(start, end + 1))
            except ValueError:
                pass
        else:
            try:
                ports.add(int(part))
            except ValueError:
                pass
                
    return sorted(list(ports))
