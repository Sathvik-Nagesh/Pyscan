import argparse
import sys
import time
from gui.app import run_gui
from core.scanner import Scanner
from core.reporter import Reporter
from utils.logger import main_logger
import os

def display_banner():
    """Displays the CLI Banner and Ethical Disclaimer."""
    banner = """
    ╔════════════════════════════════════════════════════════════╗
    ║                 PyScan Pro - Advanced Scanner              ║
    ║------------------------------------------------------------║
    ║  ⚠️ ETHICAL USE DISCLAIMER ⚠️                              ║
    ║  Use only on systems you own or have permission to test.   ║
    ║  Unauthorized scanning may be illegal.                     ║
    ╚════════════════════════════════════════════════════════════╝
    """
    print(banner)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="PyScan Pro - Advanced Port Scanner")
    parser.add_argument('target', nargs='?', help="Target IP, Domain, or CIDR (e.g. 192.168.1.1, example.com)")
    parser.add_argument('-p', '--ports', default='1-1000', help="Ports to scan (e.g. 80,443 or 1-1000)")
    parser.add_argument('--scan', choices=['tcp', 'syn', 'fast'], default='tcp', help="Scan type to perform")
    parser.add_argument('-t', '--threads', type=int, default=100, help="Number of threads (default: 100)")
    parser.add_argument('-g', '--gui', action='store_true', help="Launch Desktop GUI Dashboard")
    parser.add_argument('--export', choices=['json', 'txt', 'html'], help="Export results to format")
    
    args = parser.parse_args()

    # If --gui flag is present OR no arguments are passed, launch GUI
    if args.gui or len(sys.argv) == 1:
        print("Launching PyScan Pro GUI...")
        run_gui()
        sys.exit(0)
        
    if not args.target:
        print("Error: Target is required for CLI scanning.")
        parser.print_help()
        sys.exit(1)

    display_banner()
    
    # Run CLI Scanner
    scanner = Scanner(threads=args.threads)
    results = []
    
    def cli_progress(current, total, status):
        # Overwrite line in terminal for progress
        if total > 0:
            percent = (current / total) * 100
            sys.stdout.write(f"\r[{status}] {current}/{total} Ports scanned ({percent:.1f}%)")
            sys.stdout.flush()
            if current == total:
                print() # Newline when done
                
    def cli_result(result):
        # We append to results list, print details at end
        results.append(result)

    print(f"[*] Starting {args.scan.upper()} scan on {args.target} for ports {args.ports}...")
    start_t = time.time()
    
    try:
        scanner.start_scan(args.target, args.ports, args.scan, cli_progress, cli_result)
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user. Stopping threads...")
        scanner.stop_scan()
        sys.exit(0)
        
    end_t = time.time()
    
    print("\n\n" + "="*70)
    print(f"{'PORT':<8} | {'STATUS':<10} | {'SERVICE':<15} | {'BANNER'}")
    print("="*70)
    
    for r in sorted(results, key=lambda x: x['port']):
        print(f"{r['port']:<8} | {r['status']:<10} | {r['service']:<15} | {r['banner']}")
        
    print("="*70)
    print(f"[*] Scan completed in {end_t - start_t:.2f} seconds.")
    print(f"[*] Total open/filtered ports found: {len(results)}")
    
    if args.export:
        reporter = Reporter(args.target, args.export, results)
        path = reporter.generate()
        print(f"[*] Report saved to: {os.path.abspath(path)}")
