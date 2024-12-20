import os
import platform
import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BuiltinCommands:
    def __init__(self, shell):
        self.shell = shell

    def help_command(self, args=None):
        """Display help information"""
        help_text = """
Available Commands:
  help     - Show this help message
  ls       - List directory contents
  cd       - Change directory
  pwd      - Print working directory
  echo     - Print arguments
  create   - Create file or directory
  rm       - Remove files or directories
  mkdir    - Make directories
  cat      - Display file contents
  touch    - Create an empty file
  type     - Display command type
  whoami   - Show current user
  date     - Show current date and time
  system   - Show system information
  history  - Show command history
  alias    - Manage command aliases
  exit     - Exit the shell

Use 'command --help' for more information about specific commands.
"""
        print(help_text)

    def whoami_command(self, args=None):
        """Show current user"""
        print(os.getlogin())
        
    def pwd_command(self, args=None):
        """Print current working directory"""
        print(os.getcwd())
        
    def exit_command(self, args=None):
        # Exit the shell
        print("Goodbye!")
        sys.exit(0)  # Exit the program gracefully
    
    def cd_command(self, args):
        # If no argument or '~', go to the HOME directory
        if not args or args[0] == "~":
            target_dir = os.path.expanduser("~")
        else:
            target_dir = args[0]  # Take the first argument as the target directory

        try:
            # Change the current working directory
            os.chdir(target_dir)
            print(f"Changed directory to {target_dir}")
        except FileNotFoundError:
            print(f"cd: {target_dir}: No such file or directory")
        except NotADirectoryError:
            print(f"cd: {target_dir}: Not a directory")
        except PermissionError:
            print(f"cd: {target_dir}: Permission denied")
            
    def type_command(self, args):
        if not args:
            print("type: missing argument")
            return

        arg = args[0]

        # Check if the command is a shell builtin
        if arg in self.shell_builtins:
            print(f"{arg} is a shell builtin")
        else:
            # Search for the command in PATH
            found = False
            for path in os.environ.get("PATH", "").split(os.pathsep):
                executable_path = os.path.join(path, arg)
                if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
                    print(f"{arg} is {executable_path}")
                    found = True
                    break
            if not found:
                print(f"{arg}: not found")
                
    def create_command(self, args):
        if not args:
            print("create: missing argument")
            return

        # Take the first argument as the target (either a file or directory name)
        target = args[0]

        if len(args) > 1:
            print("create: too many arguments")
            return

        # Check if it's a directory or a file creation request
        if target.endswith('/'):  # If it ends with a '/', treat it as a directory
            try:
                os.makedirs(target, exist_ok=True)  # Create the directory
                print(f"Directory '{target}' created successfully")
            except Exception as e:
                print(f"create: failed to create directory '{target}': {e}")
        else:  # Treat it as a file creation request
            try:
                with open(target, 'w') as f:  # Create the file
                    print(f"File '{target}' created successfully")
            except Exception as e:
                print(f"create: failed to create file '{target}': {e}")
                    
    def echo_command(self, args):
        """Print arguments to the console"""
        if not args:
            print()  # Print a blank line if no arguments
        else:
            # Join arguments and handle quotes
            message = " ".join(args)
            # Remove surrounding quotes if present
            message = message.strip('"\'')
            print(message)
        
    def system_command(self, args=None):
        """Display system information"""
        print(f"Operating System: {platform.system()}")
        print(f"Release: {platform.release()}")
        print(f"Machine: {platform.machine()}")
        print(f"Processor: {platform.processor()}")

    def date_command(self, args=None):
        """Show current date and time"""
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def history_command(self, args=None):
        """Enhanced history command with more options"""
        # Display recent history
        start = max(0, len(self.command_history) - 50)
        for i, cmd in enumerate(self.command_history[start:], start+1):
            print(f"{i}: {cmd}")

        # Additional history management options
        if args:
            if args[0] == 'clear':
                self.command_history.clear()
                self.save_history()
                print("History cleared.")
            elif args[0] == 'save':
                # Option to manually save history
                self.save_history()
                print("History saved.")

    def alias_command(self, args=None):
        """Manage command aliases"""
        if not args:
            # Display current aliases
            for alias, command in self.aliases.items():
                print(f"{alias}='{command}'")
            return
        
        if len(args) == 1:
            print(f"Current alias: {args[0]} = '{self.aliases.get(args[0], 'Not defined')}'")
        elif len(args) >= 2:
            # Set or update alias
            alias = args[0]
            command = " ".join(args[1:])
            self.aliases[alias] = command
            print(f"Alias set: {alias}='{command}'")