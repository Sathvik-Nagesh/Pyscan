import socket
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional, Dict, List

from core.syn_scan import simulate_syn_scan
from core.banner import grab_banner
from core.resolver import resolve_service
from utils.helpers import parse_target, parse_ports

logger = logging.getLogger("PyScanPro.Scanner")

class Scanner:
    """
    Main scanner class that coordinates port scanning.
    Supports TCP Connect, SYN Scan Simulation, and Fast Scan modes.
    """
    def __init__(self, threads: int = 100, timeout: float = 1.0):
        self.threads = threads
        self.timeout = timeout
        self.is_running = False
        
        # Thread pool executor
        self.executor: Optional[ThreadPoolExecutor] = None
        self.futures = []

    def scan_tcp(self, ip: str, port: int) -> str:
        """
        Uses standard socket connection. Completes full 3-way handshake.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                # connect_ex returns 0 on success (OPEN), error indicator otherwise
                result = s.connect_ex((ip, port))
                if result == 0:
                    return 'OPEN'
                return 'CLOSED'
        except Exception:
            return 'CLOSED'
            
    def scan_fast(self, ip: str, port: int) -> str:
        """
        Same as TCP but faster timeout, primarily looks for quick OPENs.
        """
        self.timeout = 0.5
        return self.scan_tcp(ip, port)

    def start_scan(
        self,
        targets: str, 
        ports_str: str, 
        scan_type: str, 
        progress_callback: Callable[[int, int, str], None],
        result_callback: Callable[[Dict], None]
    ):
        """
        Initiates a multithreaded scan.
        Args:
            targets: The raw target string (IP, range, CIDR)
            ports_str: The raw port string (e.g. 1-100)
            scan_type: 'tcp', 'syn', 'fast'
            progress_callback: Callable that updates the UI progress (current, total, status)
            result_callback: Callable that adds a finding to the UI table
        """
        ip_list = parse_target(targets)
        port_list = parse_ports(ports_str)
        
        if not ip_list:
            progress_callback(0, 0, "Invalid Target.")
            return
            
        if not port_list:
            progress_callback(0, 0, "Invalid Port Range.")
            return

        total_tasks = len(ip_list) * len(port_list)
        completed_tasks = 0
        
        self.is_running = True
        self.executor = ThreadPoolExecutor(max_workers=self.threads)
        self.futures.clear()

        # Submit tasks
        for ip in ip_list:
            for port in port_list:
                if scan_type == 'syn':
                    future = self.executor.submit(self._scan_task_syn, ip, port)
                elif scan_type == 'fast':
                    future = self.executor.submit(self._scan_task_tcp_fast, ip, port)
                else: # Default to tcp
                    future = self.executor.submit(self._scan_task_tcp, ip, port)
                    
                self.futures.append(future)

        # Process future results as they complete
        try:
            for future in as_completed(self.futures):
                if not self.is_running:
                    break # Stop requested
                
                try:
                    result = future.result()
                    completed_tasks += 1
                    
                    if result:
                        status = result['status']
                        # Call result callback if OPEN or FILTERED (for SYN)
                        if status in ('OPEN', 'FILTERED'):
                            result_callback(result)
                            
                    progress_callback(completed_tasks, total_tasks, "Scanning...")
                    
                except Exception as e:
                    logger.error(f"Error in thread result: {e}")
                    completed_tasks += 1
                    progress_callback(completed_tasks, total_tasks, "Error occurred")
                    
        finally:
            self.stop_scan()
            progress_callback(completed_tasks, total_tasks, "Scan Complete")

    def stop_scan(self):
        """Gracefully stops all running threads."""
        self.is_running = False
        if self.executor:
            # cancel pending futures
            for future in self.futures:
                future.cancel()
            # Shutdown but let executing threads finish current timeout cycle
            self.executor.shutdown(wait=False, cancel_futures=True)

    def _collect_result(self, ip: str, port: int, status: str) -> Dict:
        """Helper to build result dictionary & grab banner if open."""
        service = resolve_service(port)
        banner = "N/A"
        
        if status == 'OPEN':
            # Attempt to grab a banner if open
            found_banner = grab_banner(ip, port, timeout=1.0)
            if found_banner:
                banner = found_banner

        return {
            'ip': ip,
            'port': port,
            'status': status,
            'service': service,
            'banner': banner
        }

    def _scan_task_tcp(self, ip: str, port: int) -> Dict:
        if not self.is_running: return None
        status = self.scan_tcp(ip, port)
        return self._collect_result(ip, port, status)
        
    def _scan_task_tcp_fast(self, ip: str, port: int) -> Dict:
        if not self.is_running: return None
        status = self.scan_fast(ip, port)
        return self._collect_result(ip, port, status)

    def _scan_task_syn(self, ip: str, port: int) -> Dict:
        if not self.is_running: return None
        status = simulate_syn_scan(ip, port, self.timeout)
        return self._collect_result(ip, port, status)
