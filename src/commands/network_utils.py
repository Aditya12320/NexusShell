import subprocess
import socket
import platform
import re
from typing import List, Tuple

class NetworkUtils:
    def __init__(self, shell):
        self.shell = shell
        self.is_windows = platform.system().lower() == "windows"

    def network_command(self, args):
        """Handle network-related commands"""
        if not args:
            return self._show_usage()
        
        subcommand = args[0]
        sub_args = args[1:]
        
        commands = {
            'ping': self._ping,
            'traceroute': self._traceroute,
            'dns': self._dns_lookup,
            'ports': self._check_ports,
            'ip': self._show_ip
        }
        
        if subcommand in commands:
            return commands[subcommand](sub_args)
        else:
            print(f"Unknown network command: {subcommand}")
            return self._show_usage()

    def _show_usage(self):
        """Show network utilities usage information"""
        print("\nNetwork Utilities Usage:")
        print("  network ping <host> [-c count]")
        print("  network traceroute <host>")
        print("  network dns <domain>")
        print("  network ports [port1,port2,...]")
        print("  network ip")

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
        


# network ping google.com
# network traceroute github.com
# network dns example.com
# network ports
# network ip