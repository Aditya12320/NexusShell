import os
import shlex
import shutil
import subprocess
import json
import sys
from pathlib import Path
import time
from typing import Iterable
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from src.commands.file_search import FileSearch
from src.commands.file_encryption import FileEncryption
from src.commands.text_editor import TextEditor
from src.commands.tree_view import TreeView
from src.commands.weather_command import WeatherCommand
from src.utils.plugin_manager import PluginManager
from src.utils.script_interpreter import ScriptInterpreter
from src.commands.disk_analyzer import DiskAnalyzer
from src.commands.network_utils import NetworkUtils
from src.commands.process_manager import ProcessManager

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.commands.builtin_commands import BuiltinCommands
from src.commands.file_operations import FileOperations
from src.commands.system_commands import SystemCommands
from src.utils.file_redirection import handle_file_redirection
from src.utils.prompt_config import PromptConfigManager

class EnhancedShell:
    def __init__(self):
        self.config_dir = Path.home() / ".mycmd"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.history_file = self.config_dir / "history.json"
        self.interactive_history_file = self.config_dir / "interactive_history.txt"
        
        # Ensure history files exist
        self.history_file.touch(exist_ok=True)
        self.interactive_history_file.touch(exist_ok=True)
        
        # Create command handlers after initializing command_handlers
        self.builtin_commands = BuiltinCommands(self)
        self.file_operations = FileOperations(self)
        self.system_commands = SystemCommands(self)
        self.prompt_config_manager = PromptConfigManager(self)
        self.text_editor = TextEditor(self)
        self.file_encryption = FileEncryption(self)
        self.weather_command = WeatherCommand(self)
        self.tree_view = TreeView(self)
        self.plugin_manager = PluginManager(self)
        self.script_interpreter = ScriptInterpreter(self)
        self.disk_analyzer = DiskAnalyzer(self)
        self.network_utils = NetworkUtils(self)
        self.process_manager = ProcessManager(self)
        self.file_search = FileSearch(self)

        # Initialize command_handlers dictionary
        self.command_handlers = {
            'help': self.builtin_commands.help_command,
            'whoami': self.builtin_commands.whoami_command,
            'system': self.builtin_commands.system_command,
            'date': self.builtin_commands.date_command,
            'history': self.builtin_commands.history_command,
            'alias': self.builtin_commands.alias_command,
            'ls': self.file_operations.ls_command,
            'rm': self.file_operations.rm_command,
            'mkdir': self.file_operations.mkdir_command,
            'cat': self.file_operations.cat_command,
            'touch': self.file_operations.touch_command,
            'echo': self.builtin_commands.echo_command,
            'pwd': self.builtin_commands.pwd_command,
            'cd': self.builtin_commands.cd_command,
            'type': self.builtin_commands.type_command,
            'create': self.builtin_commands.create_command,
            'exit': self.builtin_commands.exit_command,
            'prompt_config': self.prompt_config_manager.prompt_config_command,
            'sysinfo': self.system_commands.sysinfo_command,
            'edit': self.text_editor.edit_command,
            'encrypt': self.file_encryption.encrypt_command,
            'decrypt': self.file_encryption.decrypt_command,
            'weather': self.weather_command.weather_command,
            'tree': self.tree_view.tree_command,
            'plugin': self.plugin_manager.plugin_command,
            'run': self.script_interpreter.run_script,
            'disk': self.disk_analyzer.disk_usage_command,
            'network': self.network_utils.network_command,
            'process': self.process_manager.process_command,
            'search': self.file_search.search_command
        }
        
        # Load history and initialize other attributes
        self.command_history = self.load_history()
        self.shell_builtins = [
            "echo", "exit", "type", "pwd", "cd", "create", "ls", 
            "mkdir", "rm", "cat", "touch", "whoami", "date", 
            "system", "help", "alias", "history", "sysinfo",
            "encrypt","decrypt","edit","weather","tree","plugin"
        ]
        self.aliases = self.load_aliases()
        
        # Initialize key bindings
        self.kb = KeyBindings()
        self.setup_key_bindings()
        
        # Cache for executables to improve performance
        self._executable_cache = None
        self._last_cache_update = 0
        self._cache_ttl = 60  # Cache TTL in seconds

    def get_completions(self, document: Document, complete_event) -> Iterable[Completion]:
        """Implementation of the Completer interface"""
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        text_before_cursor = document.text_before_cursor

        # Split the input into words
        words = text_before_cursor.split()
        
        # If we're at the start or it's the first word, complete commands
        if not words or (len(words) == 1 and not text_before_cursor.endswith(' ')):
            yield from self._get_command_completions(word_before_cursor)
        # Otherwise, do path completion
        else:
            yield from self._get_path_completions(word_before_cursor)

    def _get_command_completions(self, word_before_cursor: str) -> Iterable[Completion]:
        """Get completions for commands, including builtins and aliases"""
        # Update executable cache if needed
        self._update_executable_cache()
        
        # Complete shell builtins
        for cmd in self.shell_builtins:
            if cmd.startswith(word_before_cursor):
                yield Completion(
                    cmd,
                    start_position=-len(word_before_cursor),
                    display_meta='Shell builtin'
                )

        # Complete aliases
        for alias in self.aliases:
            if alias.startswith(word_before_cursor):
                yield Completion(
                    alias,
                    start_position=-len(word_before_cursor),
                    display_meta=f'Alias: {self.aliases[alias]}'
                )

        # Complete executables from cache
        for executable in self._executable_cache or set():
            if executable.startswith(word_before_cursor):
                yield Completion(
                    executable,
                    start_position=-len(word_before_cursor),
                    display_meta='Executable'
                )

    def _get_path_completions(self, word_before_cursor: str) -> Iterable[Completion]:
        """Get completions for paths (files and directories)"""
        try:
            # Handle empty word case
            if not word_before_cursor:
                word_before_cursor = '.'

            # Expand user home directory if necessary
            path = os.path.expanduser(word_before_cursor)
            dirname = os.path.dirname(path) or '.'
            prefix = os.path.basename(path)

            # List directory contents
            for name in os.listdir(dirname):
                if name.startswith(prefix):
                    full_path = os.path.join(dirname, name)
                    try:
                        is_dir = os.path.isdir(full_path)
                        display_name = name + ('/' if is_dir else '')
                        
                        # Handle paths with spaces
                        completion_text = f'"{display_name}"' if ' ' in display_name else display_name
                        
                        yield Completion(
                            completion_text,
                            start_position=-len(prefix),
                            display_meta='Directory' if is_dir else 'File'
                        )
                    except (OSError, PermissionError):
                        continue

        except (OSError, PermissionError):
            return

    def _update_executable_cache(self):
        """Update the cache of executable files if it's expired"""
        current_time = time.time()
        if (self._executable_cache is None or 
            current_time - self._last_cache_update > self._cache_ttl):
            self._executable_cache = self._get_executables()
            self._last_cache_update = current_time

    def _get_executables(self) -> set:
        """Get executable files from PATH"""
        executables = set()
        for path in os.environ.get("PATH", "").split(os.pathsep):
            if not path:
                continue
            try:
                for item in os.listdir(path):
                    full_path = os.path.join(path, item)
                    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                        executables.add(item)
            except (FileNotFoundError, PermissionError):
                continue
        return executables
    
    def setup_key_bindings(self):
        @self.kb.add('up')
        def _(event):
            buffer = event.current_buffer
            if buffer.complete_state:
                buffer.complete_previous()
            else:
                buffer.history_backward()

        @self.kb.add('down')
        def _(event):
            buffer = event.current_buffer
            if buffer.complete_state:
                buffer.complete_next()
            else:
                buffer.history_forward()               
    def load_aliases(self):
        """Load aliases from configuration file"""
        alias_file = self.config_dir / "aliases.json"
        try:
            if alias_file.exists():
                with alias_file.open('r') as f:
                    return json.load(f)
            return {
                'll': 'ls -l',
                'la': 'ls -a',
                'cls': 'clear'
            }
        except Exception as e:
            print(f"Error loading aliases: {e}")
            return {}

    def save_history(self, command):
        """Save command to history"""
        try:
            history = self.load_history()
            history.append(command)
            with self.history_file.open('w') as f:
                json.dump(history[-1000:], f)  # Keep last 1000 commands
        except Exception as e:
            print(f"Error saving history: {e}")


    def load_history(self):
        """Load command history from file with proper error handling"""
        combined_history = []
        
        # Load JSON history
        try:
            if self.history_file.exists():
                with self.history_file.open('r') as f:
                    json_history = json.load(f)
                    if isinstance(json_history, list):
                        combined_history.extend(json_history)
        except json.JSONDecodeError:
            print("Warning: History file is corrupted. Starting fresh.")
        except Exception as e:
            print(f"Error loading JSON history: {e}")

        # Load text history
        try:
            if self.interactive_history_file.exists():
                with self.interactive_history_file.open('r') as f:
                    text_history = [line.strip() for line in f if line.strip()]
                    combined_history.extend(text_history)
        except Exception as e:
            print(f"Error loading text history: {e}")

        # Deduplicate while maintaining order
        seen = set()
        return [x for x in combined_history if not (x in seen or seen.add(x))]

    def save_history(self):
        """Save command history to files with proper error handling"""
        recent_history = self.command_history[-500:]  # Keep last 500 commands
        
        # Save JSON history
        try:
            with self.history_file.open('w') as f:
                json.dump(recent_history, f, indent=2)
        except Exception as e:
            print(f"Error saving JSON history: {e}")
            
        # Save text history
        try:
            with self.interactive_history_file.open('w') as f:
                f.write('\n'.join(recent_history))
        except Exception as e:
            print(f"Error saving text history: {e}")

    def parse_history_shortcut(self, command):
        """Parse and execute history shortcuts with bounds checking"""
        if not command:
            return None
            
        if command == '!!':
            return self.command_history[-1] if self.command_history else None
            
        if command.startswith('!') and command[1:].isdigit():
            index = int(command[1:]) - 1
            if 0 <= index < len(self.command_history):
                return self.command_history[index]
            print(f"History index {index + 1} out of range")
        
        return None

    def run_command(self, command):
        """Execute commands with proper error handling"""
        if not command or not command.strip():
            return

        # Add to history and save
        self.command_history.append(command)
        self.save_history()

        # Handle aliases
        parts = command.split(maxsplit=1)
        if parts[0] in self.aliases:
            alias_cmd = self.aliases[parts[0]]
            remaining = parts[1] if len(parts) > 1 else ''
            command = f"{alias_cmd} {remaining}".strip()

        try:
            parts = shlex.split(command)
        except ValueError as e:
            print(f"Error parsing command: {e}")
            return

        if not parts:
            return

        program = parts[0]
        args = parts[1:]

        # Handle file redirection
        if any(redirect in parts for redirect in ['>', '>>']):
            try:
                return handle_file_redirection(parts)
            except Exception as e:
                print(f"Error handling file redirection: {e}")
                return

        # Execute command using command_handlers
        if program in self.command_handlers:
            try:
                return self.command_handlers[program](args)
            except Exception as e:
                print(f"Error executing {program}: {e}")
        else:
            return self.execute_external_command(program, args)


    def execute_external_command(self, program, args):
        """Execute external commands with proper path resolution and error handling"""
        try:
            # Use shutil.which to find executable in PATH
            executable = shutil.which(program)
            if executable:
                result = subprocess.run(
                    [executable] + args,
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    print(result.stdout, end='')
                if result.stderr:
                    print(result.stderr, end='', file=sys.stderr)
                return result.returncode
            else:
                print(f"{program}: command not found")
                return 127  # Command not found exit code
        except subprocess.SubprocessError as e:
            print(f"Error executing {program}: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error executing {program}: {e}", file=sys.stderr)
            return 1

    def interactive_shell(self):
        """Interactive shell with integrated completion and key bindings"""
        print("Welcome to Enhanced Python Shell!")
        print("Type 'help' for a list of commands.")
        print("History shortcuts: !! (last command), !n (nth command)")

        while True:
            try:
                current_dir = os.getcwd()
                prompt_text = HTML(f'<ansired>➜</ansired> <ansigreen>{current_dir}</ansigreen> $ ')
                
                command = prompt(
                    prompt_text,
                    completer=self,
                    complete_in_thread=True,
                    key_bindings=self.kb,  # Use the configured key bindings
                    history=FileHistory(str(self.interactive_history_file)),
                    multiline=False,
                    validate_while_typing=False,
                    complete_while_typing=True
                )

                if not command.strip():
                    continue

                # Handle history shortcuts
                shortcut_command = self.parse_history_shortcut(command)
                if shortcut_command:
                    print(f"Executing: {shortcut_command}")
                    command = shortcut_command

                # Handle exit commands
                if command.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break

                # Execute command
                self.run_command(command)

            except KeyboardInterrupt:
                print("\nInterrupted. Press Ctrl+D or type 'exit' to quit.")
                continue
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Shell error: {e}")
                continue

