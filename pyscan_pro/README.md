# PyScan Pro — Advanced Port Scanner

PyScan Pro is a resume-level, educational alternative to Nmap. It demonstrates core networking concepts, socket programming, packet-level interactions, multithreading, and security theory through a rich Python implementation containing both a robust CLI and a modern Desktop GUI dashboard.

## ⚠️ Ethical Use Disclaimer

**This tool is for educational purposes only.**
Use PyScan Pro strictly on systems and networks you own or have explicit written permission to test. Unauthorized port scanning can cause unintended disruptions or trigger intrusion detection systems, and may be illegal in some jurisdictions.

---

## 🏗️ Architecture

PyScan Pro uses a clean, modular structure emphasizing separate concerns:

- **`core/`**: Networking and scanning logic.
  - `scanner.py`: ThreadManager for performing multi-threaded port scans.
  - `syn_scan.py`: Logic for crafting half-open scans (via Scapy) and falling back gracefully.
  - `banner.py`: Protocol-specific banner grabbing to identify running services.
  - `resolver.py`: Port-to-service mapping dictionary.
  - `reporter.py`: Generating structured reports (JSON, TXT, HTML).
- **`gui/`**: Dashboard frontend via CustomTkinter.
  - `app.py`: Entry point for GUI application.
  - `dashboard.py`: Layout, state, and multithreaded GUI updates.
  - `components.py`: Reusable custom UI widgets.
- **`utils/`**: Helpers and logging setup.
- **`main.py`**: Unified entry point (CLI and GUI bridging).

---

## 📚 Network Theory Explained

### TCP Connect Scan (Full Handshake)

When analyzing ports using the standard TCP scan (`--scan tcp`), PyScan Pro utilizes the operating system's `socket.connect_ex()` call. This initiates a complete TCP 3-way handshake:

1.  **Scanner sending:** `SYN` (Synchronize)
2.  **Target sending:** `SYN-ACK` (Acknowledge)
3.  **Scanner sending:** `ACK` (Connection Established!)

_Pros:_ Highly reliable, no special privileges required.
_Cons:_ Extremely "noisy" and highly visible in system logs.

### SYN Scan Simulation (Half-Open)

A true SYN scan (`--scan syn`) is faster and stealthier. Instead of completing the handshake, it aborts it before the final step.

1.  **Scanner sending:** `SYN`
2.  **Target sending:** `SYN-ACK` (If Open)
3.  **Scanner sending:** `RST` (Reset) to tear down the connection instantly.

_Educational Notes:_
PyScan Pro implements this via **Scapy** (capable of raw packet injection). However, OS kernels heavily restrict crafting raw packets (usually requiring Root / Admin permissions).
If Scapy encounters permission limitations, PyScan Pro **gracefully falls back to a timing-based simulation**. It explains in its source code the networking theories, demonstrating how standard sockets behave versus raw sockets.

---

## 🚀 Installation & Usage

### Prerequisites

- Python 3.11+
- _(Optional but recommended)_ Administrator/Root privileges for authentic SYN scans.

### Setup

```bash
git clone https://github.com/yourusername/pyscan-pro.git
cd pyscan-pro
pip install -r requirements.txt
```

### Launching the Graphical User Interface (GUI)

To start the modern, dark-themed Desktop Dashboard, simply run:

```bash
python main.py
# or explicitly:
python main.py --gui
```

### Command-Line Interface (CLI) Examples

**Basic TCP Scan:**

```bash
python main.py scanme.nmap.org -p 80,443 --scan tcp
```

**SYN Scan on an IP Range (Requires privileges for full capability):**

```bash
python main.py 192.168.1.0/24 -p 1-100 --scan syn -t 200
```

**Fast Scan with JSON Export:**

```bash
python main.py 10.0.0.1 -p 1-1000 --scan fast --export json
```

---

## 📸 Screenshots

_(Placeholder: Add screenshots of the GUI dashboard, the CLI interface scanning, and an HTML report output here)_

## 🛡️ Security & Performance Enhancements

- **Rate Limiting & Thread Pools:** Uses `concurrent.futures.ThreadPoolExecutor` to efficiently throttle traffic, preventing network congestions.
- **Graceful Interruptions:** Safely catches `Ctrl+C` in CLI and handles thread cancellations to cleanly stop scans without memory leaks.
- **Intelligent Banner Grabbing:** Proactively sends protocol-specific probes (like `HEAD` for HTTP or `HELO` for SMTP) rather than just waiting passively for banners, decreasing timeouts.
