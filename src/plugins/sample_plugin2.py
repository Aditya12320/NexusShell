# time_plugin.py
from datetime import datetime
import time

def current_time(args):
    """Display current time"""
    print(f"Current time: {datetime.now().strftime('%H:%M:%S')}")

def timer(args):
    """Simple countdown timer"""
    if not args:
        print("Usage: timer <seconds>")
        return
        
    try:
        seconds = int(args[0])
        print(f"Timer started for {seconds} seconds")
        
        while seconds > 0:
            print(f"Time remaining: {seconds}s", end='\r')
            time.sleep(1)
            seconds -= 1
            
        print("\nTimer finished!")
    except ValueError:
        print("Please enter a valid number of seconds")

def register_plugin(shell):
    """Register plugin with the shell"""
    shell.command_handlers['time'] = current_time
    shell.command_handlers['timer'] = timer
    
    return {
        'name': 'Time Plugin',
        'description': 'Plugin for time-related commands',
        'version': '1.0',
        'commands': ['time', 'timer']
    }