import socket
import subprocess
import platform
import re
import asyncio
import paramiko
import psutil
import requests
from typing import List, Tuple, Optional, Dict, Any
from scapy.all import sniff
import websockets
from datetime import datetime


class NetworkUtils:
    def __init__(self, shell):
        self.shell = shell
        self.is_windows = platform.system().lower() == "windows"
        self.connections = {}  # Store active connections
        
    def network_command(self, args: List[str]) -> None:
        """Handle network-related commands"""
        if not args:
            return self._show_usage()
        
        subcommand = args[0]
        sub_args = args[1:]
        
        commands = {
            'ping': self._ping,
            'traceroute': self._traceroute,
            'dns': self._dns_lookup,
            'ports': self._port_scan,
            'ip': self._show_ip,
            'monitor': self._monitor_network,
            'ssh': self._ssh_execute,
            'http': self._http_request,
            'transfer': self._file_transfer,
            'sniff': self._packet_sniffer,
            'websocket': self._websocket_client,
            'netstat': self._netstat,
            'bandwidth': self._bandwidth_monitor,
            'whois': self._whois_lookup
        }
        
        if subcommand in commands:
            return commands[subcommand](sub_args)
        else:
            print(f"Unknown network command: {subcommand}")
            return self._show_usage()


    def _show_usage(self) -> None:
        """Show enhanced network utilities usage information"""
        print("\nAdvanced Network Utilities Usage:")
        print("  network ping <host> [-c count]")
        print("  network traceroute <host>")
        print("  network dns <domain>")
        print("  network ports <host> [port1,port2,...]")
        print("  network ip")
        print("  network monitor [-t seconds]")
        print("  network ssh <host> <username> <password> <command>")
        print("  network http <url> [method] [data]")
        print("  network transfer send/receive <file> <host> <port>")
        print("  network sniff [-c count] [-f filter]")
        print("  network chat server/client [port]")
        print("  network websocket <url> <message>")

    async def _websocket_client(self, args: List[str]) -> None:
        """Handle WebSocket communication"""
        if len(args) < 2:
            print("Usage: network websocket <url> <message>")
            return
            
        url, message = args[0], args[1]
        try:
            async with websockets.connect(url) as websocket:
                await websocket.send(message)
                response = await websocket.recv()
                print(f"Server response: {response}")
        except Exception as e:
            print(f"WebSocket error: {e}")
            
    def _netstat(self, args: List[str]) -> None:
        """Display network connections"""
        try:
            print("\nActive Network Connections:")
            print("-" * 80)
            print("Proto\tLocal Address\t\tForeign Address\t\tStatus\tPID")
            print("-" * 80)
            
            for conn in psutil.net_connections(kind='inet'):
                try:
                    protocol = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
                    local = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "*:*"
                    remote = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "*:*"
                    status = conn.status if hasattr(conn, 'status') else "-"
                    pid = conn.pid or "*"
                    print(f"{protocol}\t{local:<15}\t{remote:<15}\t{status:<8}\t{pid}")
                except (AttributeError, IndexError):
                    continue
                    
        except Exception as e:
            print(f"Error getting network connections: {e}")

    def _bandwidth_monitor(self, args: List[str]) -> None:
        """Monitor bandwidth usage"""
        try:
            print("Monitoring bandwidth usage (Press Ctrl+C to stop)...")
            old_value = psutil.net_io_counters()
            while True:
                import time
                time.sleep(1)  # Update every second
                new_value = psutil.net_io_counters()
                
                # Calculate speeds
                bytes_sent = new_value.bytes_sent - old_value.bytes_sent
                bytes_recv = new_value.bytes_recv - old_value.bytes_recv
                
                print("\033[2J\033[H")  # Clear screen
                print("Bandwidth Monitor (Press Ctrl+C to stop)")
                print("-" * 50)
                print(f"Upload Speed: {self._format_bytes(bytes_sent)}/s")
                print(f"Download Speed: {self._format_bytes(bytes_recv)}/s")
                print(f"\nTotal Stats:")
                print(f"Total Uploaded: {self._format_bytes(new_value.bytes_sent)}")
                print(f"Total Downloaded: {self._format_bytes(new_value.bytes_recv)}")
                print(f"Packets Sent: {new_value.packets_sent}")
                print(f"Packets Received: {new_value.packets_recv}")
                
                old_value = new_value
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            print(f"Error monitoring bandwidth: {e}")

    def _whois_lookup(self, args: List[str]) -> None:
        """Perform WHOIS lookup for a domain"""
        if not args:
            print("Usage: network whois <domain>")
            return

        domain = args[0]
        whois_servers = {
            'com': 'whois.verisign-grs.com',
            'net': 'whois.verisign-grs.com',
            'org': 'whois.pir.org',
            'edu': 'whois.educause.edu'
        }
        
        # Get the TLD (top-level domain)
        tld = domain.split('.')[-1].lower()
        whois_server = whois_servers.get(tld, 'whois.iana.org')
        
        try:
            # Connect to the WHOIS server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((whois_server, 43))
                
                # Send the domain query
                s.send(f"{domain}\r\n".encode())
                
                # Receive and display the response
                response = b""
                while True:
                    data = s.recv(4096)
                    if not data:
                        break
                    response += data
                
                print("\nWHOIS Information:")
                print("-" * 50)
                print(response.decode('utf-8', errors='ignore'))
                
        except socket.timeout:
            print("Connection timed out while querying WHOIS server")
        except Exception as e:
            print(f"Error performing WHOIS lookup: {e}")

    def _format_bytes(self, bytes_: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_ < 1024:
                return f"{bytes_:.2f} {unit}"
            bytes_ /= 1024
        return f"{bytes_:.2f} TB"
    
    def _ssh_execute(self, args: List[str]) -> None:
        """Execute commands via SSH"""
        if len(args) < 4:
            print("Usage: network ssh <host> <username> <password> <command>")
            return
            
        host, username, password = args[0], args[1], args[2]
        command = ' '.join(args[3:])
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, 22, username, password)
            stdin, stdout, stderr = ssh.exec_command(command)
            print(stdout.read().decode())
            if stderr:
                print(f"Errors: {stderr.read().decode()}")
        except Exception as e:
            print(f"SSH error: {e}")
        finally:
            ssh.close()

    def _monitor_network(self, args: List[str]) -> None:
        """Monitor network statistics in real-time"""
        duration = 60  # default duration in seconds
        if len(args) > 1 and args[0] == '-t':
            try:
                duration = int(args[1])
            except ValueError:
                print("Invalid duration specified")
                return

        start_time = datetime.now()
        try:
            while (datetime.now() - start_time).seconds < duration:
                stats = psutil.net_io_counters()
                conns = len(psutil.net_connections())
                
                print("\033[2J\033[H")  # Clear screen
                print(f"Network Monitor - Press Ctrl+C to stop")
                print(f"Bytes Sent: {self._format_bytes(stats.bytes_sent)}")
                print(f"Bytes Received: {self._format_bytes(stats.bytes_recv)}")
                print(f"Packets Sent: {stats.packets_sent}")
                print(f"Packets Received: {stats.packets_recv}")
                print(f"Active Connections: {conns}")
                
                # Network interfaces info
                print("\nNetwork Interfaces:")
                for iface, addrs in psutil.net_if_addrs().items():
                    print(f"\n{iface}:")
                    for addr in addrs:
                        print(f"  {addr.family.name}: {addr.address}")
                
                asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")

    def _port_scan(self, args: List[str]) -> None:
        """Enhanced port scanner with service detection"""
        if not args:
            print("Usage: network ports <host> [port1,port2,...]")
            return

        host = args[0]
        if len(args) > 1:
            try:
                ports = [int(p) for p in args[1].split(',')]
            except ValueError:
                print("Error: Invalid port number")
                return
        else:
            ports = [20, 21, 22, 23, 25, 53, 80, 443, 3306, 3389, 5432, 8080]

        print(f"\nScanning ports on {host}:")
        print("-" * 60)
        print("PORT\tSTATE\tSERVICE")
        print("-" * 60)

        for port in ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((host, port))
                    state = "open" if result == 0 else "closed"
                    service = self._get_service_name(port)
                    print(f"{port}\t{state}\t{service}")
            except socket.gaierror:
                print(f"Hostname {host} could not be resolved")
                break
            except Exception as e:
                print(f"Error scanning port {port}: {e}")

    def _http_request(self, args: List[str]) -> None:
        """Make HTTP requests"""
        if not args:
            print("Usage: network http <url> [method] [data]")
            return

        url = args[0]
        method = args[1].upper() if len(args) > 1 else "GET"
        data = args[2] if len(args) > 2 else None

        try:
            response = requests.request(method, url, json=data)
            print(f"Status Code: {response.status_code}")
            print("\nHeaders:")
            for key, value in response.headers.items():
                print(f"{key}: {value}")
            print("\nResponse:")
            print(response.text)
        except Exception as e:
            print(f"HTTP request error: {e}")

    def _file_transfer(self, args: List[str]) -> None:
        """Handle file transfer operations"""
        if len(args) < 4:
            print("Usage: network transfer send/receive <file> <host> <port>")
            return

        mode, file_path, host, port = args[0], args[1], args[2], int(args[3])

        if mode == "send":
            self._send_file(file_path, host, port)
        elif mode == "receive":
            self._receive_file(file_path, port)
        else:
            print("Invalid transfer mode. Use 'send' or 'receive'")

    def _packet_sniffer(self, args: List[str]) -> None:
        """Capture and analyze network packets"""
        packet_count = 10
        packet_filter = "ip"

        if "-c" in args:
            try:
                idx = args.index("-c")
                packet_count = int(args[idx + 1])
            except (ValueError, IndexError):
                print("Invalid packet count")
                return

        if "-f" in args:
            try:
                idx = args.index("-f")
                packet_filter = args[idx + 1]
            except IndexError:
                print("Invalid filter")
                return

        print(f"Starting packet capture (count: {packet_count}, filter: {packet_filter})")
        try:
            sniff(filter=packet_filter, prn=self._process_packet, count=packet_count)
        except Exception as e:
            print(f"Packet sniffing error: {e}")

    def _process_packet(self, packet) -> None:
        """Process and display captured packet information"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] Packet captured:")
        print(packet.summary())
        if packet.haslayer("IP"):
            print(f"Source IP: {packet['IP'].src}")
            print(f"Destination IP: {packet['IP'].dst}")
        if packet.haslayer("TCP") or packet.haslayer("UDP"):
            layer = "TCP" if packet.haslayer("TCP") else "UDP"
            print(f"Source Port: {packet[layer].sport}")
            print(f"Destination Port: {packet[layer].dport}")

    @staticmethod
    def _format_bytes(bytes_: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_ < 1024:
                return f"{bytes_:.2f} {unit}"
            bytes_ /= 1024
        return f"{bytes_:.2f} TB"

    @staticmethod
    def _get_service_name(port: int) -> str:
        """Get service name for common ports"""
        common_ports = {
            20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "TELNET",
            25: "SMTP", 53: "DNS", 80: "HTTP", 443: "HTTPS",
            3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
            8080: "HTTP-ALT"
        }
        return common_ports.get(port, "unknown")
    
    
    def _ping(self, args):
        """Ping a host"""
        if not args:
            print("Usage: network ping <host> [-c count]")
            return
        
        host = args[0]
        count = 4  # default ping count
        
        if len(args) > 2 and args[1] == '-c':
            try:
                count = int(args[2])
            except ValueError:
                print("Error: Invalid count value")
                return

        try:
            if self.is_windows:
                cmd = ['ping', '-n', str(count), host]
            else:
                cmd = ['ping', '-c', str(count), host]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
                
        except subprocess.SubprocessError as e:
            print(f"Error executing ping: {e}")

    def _traceroute(self, args):
        """Perform traceroute to a host"""
        if not args:
            print("Usage: network traceroute <host>")
            return

        host = args[0]
        try:
            if self.is_windows:
                cmd = ['tracert', host]
            else:
                cmd = ['traceroute', host]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
                
        except subprocess.SubprocessError as e:
            print(f"Error executing traceroute: {e}")

    def _dns_lookup(self, args):
        """Perform DNS lookup"""
        if not args:
            print("Usage: network dns <domain>")
            return

        domain = args[0]
        try:
            info = socket.getaddrinfo(domain, None)
            print(f"\nDNS information for {domain}:")
            seen_ips = set()
            
            for item in info:
                ip = item[4][0]
                if ip not in seen_ips:
                    seen_ips.add(ip)
                    print(f"IP Address: {ip}")
                    try:
                        hostname = socket.gethostbyaddr(ip)[0]
                        print(f"Hostname: {hostname}")
                    except socket.herror:
                        pass
                    print()
                    
        except socket.gaierror as e:
            print(f"DNS lookup failed: {e}")

    def _check_ports(self, args):
        """Check if ports are open on localhost"""
        if not args:
            ports = [80, 443, 22, 21, 25, 3306]  # Default ports to check
        else:
            try:
                ports = [int(p) for p in args[0].split(',')]
            except ValueError:
                print("Error: Invalid port number")
                return

        print("\nChecking port status on localhost:")
        print("-" * 40)
        
        for port in ports:
            status = self._is_port_open('localhost', port)
            print(f"Port {port}: {'Open' if status else 'Closed'}")

    def _show_ip(self, args):
        """Show IP addresses"""
        try:
            # Get hostname and local IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            print(f"\nHostname: {hostname}")
            print(f"Local IP: {local_ip}")
            
            # Try to get public IP
            try:
                public_ip = self._get_public_ip()
                if public_ip:
                    print(f"Public IP: {public_ip}")
            except Exception:
                pass
                
        except Exception as e:
            print(f"Error retrieving IP information: {e}")

    def _is_port_open(self, host: str, port: int) -> bool:
        """Check if a port is open"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                return s.connect_ex((host, port)) == 0
        except Exception:
            return False

    def _get_public_ip(self) -> str:
        """Get public IP address using a public API"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("api.ipify.org", 80))
                s.send(b"GET /?format=text HTTP/1.1\r\nHost: api.ipify.org\r\n\r\n")
                response = s.recv(4096).decode()
                match = re.search(r'\r\n\r\n(\d+\.\d+\.\d+\.\d+)', response)
                if match:
                    return match.group(1)
        except Exception:
            return None
        


# 1. Basic Network Commands
# Ping test
# network ping google.com
# network ping google.com -c 4      # Ping with count

# # DNS lookup
# network dns google.com
# network dns github.com

# # Show IP information
# network ip

# # Traceroute
# network traceroute google.com


# 2. Port Scanning
# Scan common ports on localhost
# network ports localhost

# # Scan specific ports on a domain
# network ports google.com 80,443,8080

# # Scan a specific IP address
# network ports 192.168.1.1


# 3. Network Monitoring
# Monitor network for default duration (60 seconds)
# network monitor

# # Monitor for specific duration
# network monitor -t 30

# # Monitor bandwidth usage
# network bandwidth

# # View active network connections
# network netstat


# 4. HTTP Requests
# Basic GET request
# network http https://api.github.com

# # GET request to test endpoint
# network http https://httpbin.org/get

# # POST request with data
# network http https://httpbin.org/post POST {"test":"data"}

# # Test different HTTP methods
# network http https://httpbin.org/delete DELETE

# 5. File Transfer
# On receiving machine:
# network transfer receive output.txt localhost 12345

# # On sending machine:
# network transfer send input.txt localhost 12345

# 6. WHOIS Lookup
# Domain information lookup
# network whois google.com
# network whois github.com

# 7. Testing Multiple Features Together
# Test sequence for comprehensive check
# network ip                        # Check your IP first
# network ports localhost           # Check local ports
# network monitor -t 10            # Monitor for 10 seconds
# network bandwidth                # Check bandwidth
# network http google.com          # Test HTTP


# 8. Safe Testing Domains
# These domains are safe for testing
# network ping localhost
# network ping 8.8.8.8            # Google's DNS
# network dns example.com
# network http https://httpbin.org
# network ports localhost
# Important Notes:

# Error Testing:

# Test with invalid inputs
# network ping                     # Missing argument
# network ports                    # Missing host
# network http                     # Missing URL

# Common Parameters:

# Time duration tests
# network monitor -t 5            # 5 seconds
# network monitor -t 10           # 10 seconds

# # Port combinations
# network ports localhost 80,443
# network ports localhost 22,80,443,3306

# Safe Testing Sequence:

# Step by step safe testing
# network ip                      # 1. Check your IP
# network ping localhost          # 2. Test local connectivity
# network dns google.com          # 3. Test DNS resolution
# network ports localhost 80      # 4. Test single port
# network monitor -t 5            # 5. Brief monitoring
# network bandwidth               # 6. Check bandwidth
# network netstat                 # 7. Check connections

# Resource Monitoring Tests:

# Run these in sequence
# network bandwidth               # Start bandwidth monitor
# # (Download a file in another window)
# network netstat                 # Check active connections
# network monitor -t 30          # Monitor during file transfer