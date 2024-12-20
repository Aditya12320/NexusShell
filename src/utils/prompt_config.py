import os
import platform
import datetime
import sys
import psutil
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class PromptConfigManager:
    def __init__(self, shell):
        self.shell = shell
        self.prompt_config = {
            'show_username': True,
            'show_hostname': True,
            'show_directory': True,
            'show_time': True,
            'show_cpu_usage': True,
            'show_git_branch': True,
            'time_format': '%H:%M',
            'max_directory_depth': 2
        }
        
    def prompt_config_command(self, args):
        """Manage prompt configuration"""
        if not args:
            # Display current configuration
            print("Current Prompt Configuration:")
            for key, value in self.prompt_config.items():
                print(f"{key}: {value}")
            return

        # Parse configuration updates
        try:
            for arg in args:
                key, value = arg.split('=')
                # Convert value to appropriate type
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                
                self.set_prompt_config(**{key: value})
            
            print("Prompt configuration updated successfully.")
        except ValueError:
            print("Invalid configuration format. Use 'key=value'.")
            
    def set_prompt_config(self, **kwargs):
        """Update prompt configuration"""
        for key, value in kwargs.items():
            if key in self.prompt_config:
                self.prompt_config[key] = value
            else:
                print(f"Invalid prompt configuration key: {key}")

    def get_git_branch(self):
        """Get current Git branch name if in a Git repository"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                capture_output=True, 
                text=True, 
                cwd=os.getcwd()
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def truncate_path(self, path, max_depth=2):
        """Truncate path to specified max depth"""
        parts = path.split(os.path.sep)
        if len(parts) <= max_depth:
            return path
        
        if parts[0] == '':  # Absolute path
            return os.path.sep + os.path.join('..', *parts[-max_depth:])
        else:
            return os.path.join('..', *parts[-max_depth:])

    def generate_prompt(self):
        """Generate a dynamic, configurable prompt"""
        from prompt_toolkit.formatted_text import HTML

        prompt_parts = []
        
        # Username
        if self.prompt_config['show_username']:
            prompt_parts.append(f'<ansiblue>{os.getlogin()}</ansiblue>')
        
        # Hostname
        if self.prompt_config['show_hostname']:
            prompt_parts.append(f'<ansicyan>@{platform.node()}</ansicyan>')
        
        # Current Directory
        if self.prompt_config['show_directory']:
            current_dir = self.truncate_path(
                os.getcwd(), 
                self.prompt_config['max_directory_depth']
            )
            prompt_parts.append(f'<ansigreen>{current_dir}</ansigreen>')
        
        # Time
        if self.prompt_config['show_time']:
            time_str = datetime.datetime.now().strftime(
                self.prompt_config['time_format']
            )
            prompt_parts.append(f'<ansiyellow>{time_str}</ansiyellow>')
        
        # CPU Usage
        if self.prompt_config['show_cpu_usage']:
            cpu_usage = psutil.cpu_percent()
            cpu_color = 'ansired' if cpu_usage > 70 else 'ansigreen'
            prompt_parts.append(f'<{cpu_color}>CPU:{cpu_usage}%</{cpu_color}>')
        
        # Git Branch
        if self.prompt_config['show_git_branch']:
            git_branch = self.get_git_branch()
            if git_branch:
                prompt_parts.append(f'<ansimagenta>({git_branch})</ansimagenta>')
        
        # Combine parts with separators
        prompt_text = ' | '.join(prompt_parts)
        
        # Add final prompt symbol
        full_prompt = HTML(f'{prompt_text} $ ')
        return full_prompt