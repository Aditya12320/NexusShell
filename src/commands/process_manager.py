import psutil
import time
from datetime import datetime
import humanize
from typing import List, Dict

class ProcessManager:
    def __init__(self, shell):
        self.shell = shell

    def process_command(self, args):
        """Handle process-related commands"""
        if not args:
            return self._show_usage()
        
        subcommand = args[0]
        sub_args = args[1:]
        
        commands = {
            'list': self._list_processes,
            'kill': self._kill_process,
            'info': self._process_info,
            'top': self._show_top,
            'tree': self._process_tree
        }
        
        if subcommand in commands:
            return commands[subcommand](sub_args)
        else:
            print(f"Unknown process command: {subcommand}")
            return self._show_usage()

    def _show_usage(self):
        """Show process manager usage information"""
        print("\nProcess Manager Usage:")
        print("  process list [--sort cpu|mem]")
        print("  process kill <pid>")
        print("  process info <pid>")
        print("  process top")
        print("  process tree [pid]")

    def _list_processes(self, args):
        """List running processes"""
        sort_by = 'cpu'
        if args and args[0] == '--sort':
            if len(args) > 1 and args[1] in ['cpu', 'mem']:
                sort_by = args[1]
            else:
                print("Invalid sort option. Using default (cpu)")

        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                info['cpu_percent'] = proc.cpu_percent(interval=0.1)
                processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort processes
        processes.sort(key=lambda x: x['cpu_percent' if sort_by == 'cpu' else 'memory_percent'],
                      reverse=True)

        # Print header
        print(f"\n{'PID':>7} {'CPU%':>7} {'MEM%':>7} {'Name':<30}")
        print("-" * 55)

        # Print processes
        for proc in processes[:20]:  # Show top 20 processes
            try:
                print(f"{proc['pid']:>7} {proc['cpu_percent']:>7.1f} "
                      f"{proc.get('memory_percent', 0):>7.1f} "
                      f"{proc['name']:<30}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def _kill_process(self, args):
        """Kill a process by PID"""
        if not args:
            print("Usage: process kill <pid>")
            return

        try:
            pid = int(args[0])
            proc = psutil.Process(pid)
            proc.terminate()
            print(f"Process {pid} terminated")
        except ValueError:
            print("Error: Invalid PID")
        except psutil.NoSuchProcess:
            print(f"Error: Process {pid} not found")
        except psutil.AccessDenied:
            print(f"Error: Permission denied to kill process {pid}")

    def _process_info(self, args):
        """Show detailed information about a process"""
        if not args:
            print("Usage: process info <pid>")
            return

        try:
            pid = int(args[0])
            proc = psutil.Process(pid)
            
            # Collect process information
            info = {
                'pid': proc.pid,
                'name': proc.name(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(interval=0.1),
                'memory_percent': proc.memory_percent(),
                'memory_info': proc.memory_info(),
                'create_time': datetime.fromtimestamp(proc.create_time()),
                'username': proc.username(),
                'cmdline': ' '.join(proc.cmdline()),
                'num_threads': proc.num_threads(),
                'connections': proc.connections(),
                'open_files': proc.open_files()
            }
            
            # Print information
            print(f"\nProcess Information for PID {pid}:")
            print("-" * 50)
            print(f"Name: {info['name']}")
            print(f"Status: {info['status']}")
            print(f"User: {info['username']}")
            print(f"CPU Usage: {info['cpu_percent']:.1f}%")
            print(f"Memory Usage: {info['memory_percent']:.1f}%")
            print(f"Memory Info:")
            print(f"  - RSS: {humanize.naturalsize(info['memory_info'].rss)}")
            print(f"  - VMS: {humanize.naturalsize(info['memory_info'].vms)}")
            print(f"Created: {info['create_time']}")
            print(f"Threads: {info['num_threads']}")
            print(f"Command Line: {info['cmdline']}")
            
            # Print open files
            if info['open_files']:
                print("\nOpen Files:")
                for file in info['open_files'][:5]:  # Show first 5 files
                    print(f"  - {file.path}")
            
            # Print network connections
            if info['connections']:
                print("\nNetwork Connections:")
                for conn in info['connections'][:5]:  # Show first 5 connections
                    print(f"  - {conn.laddr} -> {conn.raddr or '*'} ({conn.status})")
                    
        except ValueError:
            print("Error: Invalid PID")
        except psutil.NoSuchProcess:
            print(f"Error: Process {pid} not found")
        except psutil.AccessDenied:
            print(f"Error: Permission denied to access process {pid}")

    def _show_top(self, args):
        """Show real-time process information (similar to top command)"""
        try:
            while True:
                # Clear screen
                print("\033[2J\033[H", end="")
                
                # Get system information
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                # Print system overview
                print(f"CPU Usage: {cpu_percent}%")
                print(f"Memory Usage: {memory.percent}% of {humanize.naturalsize(memory.total)}")
                print("\n" + "=" * 80)
                print(f"{'PID':>7} {'CPU%':>7} {'MEM%':>7} {'Name':<30}")
                print("-" * 80)
                
                # Get process information
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        info = proc.info
                        info['cpu_percent'] = proc.cpu_percent()
                        processes.append(info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # Sort by CPU usage and print top processes
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
                for proc in processes[:15]:  # Show top 15 processes
                    print(f"{proc['pid']:>7} {proc['cpu_percent']:>7.1f} "
                          f"{proc.get('memory_percent', 0):>7.1f} "
                          f"{proc['name'][:30]:<30}")
                
                print("\nPress Ctrl+C to exit")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\nExiting top view")

    def _process_tree(self, args):
        """Display process tree"""
        def get_children(pid):
            try:
                proc = psutil.Process(pid)
                children = proc.children(recursive=True)
                return {
                    'name': proc.name(),
                    'pid': pid,
                    'cpu_percent': proc.cpu_percent(),
                    'memory_percent': proc.memory_percent(),
                    'children': [get_children(child.pid) for child in children]
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return None

        def print_tree(node, level=0):
            if not node:
                return
            print(f"{'  ' * level}├─ {node['name']} (PID: {node['pid']}, "
                  f"CPU: {node['cpu_percent']:.1f}%, MEM: {node['memory_percent']:.1f}%)")
            for child in node['children']:
                print_tree(child, level + 1)

        try:
            if args:
                pid = int(args[0])
            else:
                pid = 1  # Root process

            tree = get_children(pid)
            if tree:
                print(f"\nProcess Tree (starting from PID {pid}):")
                print_tree(tree)
            else:
                print(f"Error: Unable to access process {pid}")
                
        except ValueError:
            print("Error: Invalid PID")
        except Exception as e:
            print(f"Error creating process tree: {e}")
            
            
# process list --sort cpu
# process kill 1234
# process info 5678
# process top
# process tree