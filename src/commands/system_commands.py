import platform
import sys
import psutil
import os
import datetime
import getpass
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SystemCommands:
    def __init__(self, shell):
        self.shell = shell

    def system_command(self, args=None):
        """Display basic system information"""
        print(f"Operating System: {platform.system()}")
        print(f"Release: {platform.release()}")
        print(f"Machine: {platform.machine()}")
        print(f"Processor: {platform.processor()}")

    def date_command(self, args=None):
        """Show current date and time"""
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def sysinfo_command(self, args=None):
        """Display comprehensive system and shell information"""
        print("System Information:")
        print(f"Hostname:       {platform.node()}")
        print(f"OS:             {platform.system()} {platform.release()}")
        print(f"Machine:        {platform.machine()}")
        print(f"Processor:      {platform.processor()}")
        
        # User Information
        print("\nUser Details:")
        print(f"Username:       {getpass.getuser()}")
        print(f"Home Directory: {os.path.expanduser('~')}")
        
        # Current Shell Details
        print("\nShell Details:")
        print(f"Current Dir:    {os.getcwd()}")
        print(f"Shell Version:  Enhanced Python Shell v1.0")
        
        # Resource Usage
        print("\nSystem Resources:")
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        print(f"CPU Usage:      {cpu_usage}%")
        print(f"Memory Total:   {memory.total / (1024*1024*1024):.2f} GB")
        print(f"Memory Used:    {memory.used / (1024*1024*1024):.2f} GB ({memory.percent}%)")
        
        # Disk Information
        print("\nDisk Information:")
        disk = psutil.disk_usage(os.path.expanduser('~'))
        print(f"Disk Total:     {disk.total / (1024*1024*1024):.2f} GB")
        print(f"Disk Used:      {disk.used / (1024*1024*1024):.2f} GB ({disk.percent}%)")