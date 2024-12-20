from datetime import datetime
import os
import shutil
import sys
from termcolor import colored
from src.utils.advanced_ls import AdvancedLS
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class FileOperations:
    def __init__(self, shell):
        self.shell = shell

    def ls_command(self, args):
        """Advanced ls command with multiple display options"""
        path = "."
        long_format = False
        human_readable = False
        all_files = False

        # Parse arguments
        for arg in args:
            if arg in ("-l", "-lh", "-la", "-al", "-lah", "-hal"):
                long_format = True
                if "h" in arg:
                    human_readable = True
                if "a" in arg:
                    all_files = True
            elif not arg.startswith("-"):
                path = arg

        try:
            items = os.listdir(path)
            if not all_files:
                items = [item for item in items if not item.startswith('.')]
            items.sort()

            if long_format:
                # Detailed list view
                for item in items:
                    full_path = os.path.join(path, item)
                    stats = os.stat(full_path)
                    permissions = AdvancedLS.get_file_permissions(stats.st_mode)
                    size = stats.st_size
                    if human_readable:
                        size = AdvancedLS.human_readable_size(size)
                    mtime = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    colorized_name = self.colorize_filename(path, item)
                    print(f"{permissions} {stats.st_nlink} {stats.st_uid} {stats.st_gid} {size:>8} {mtime} {colorized_name}")
            else:
                # Simple list view
                for item in items:
                    print(self.colorize_filename(path, item), end="  ")
                print()

        except FileNotFoundError:
            print(f"ls: cannot access '{path}': No such file or directory")
        except PermissionError:
            print(f"ls: cannot access '{path}': Permission denied")
        except Exception as e:
            print(f"ls: {e}")

    def rm_command(self, args):
        """Remove files or directories"""
        if not args:
            print("rm: missing operand")
            return

        recursive = "-r" in args
        force = "-f" in args

        args = [arg for arg in args if arg not in ["-r", "-f"]]

        for target in args:
            try:
                if os.path.isdir(target):
                    if recursive:
                        shutil.rmtree(target)
                        print(f"Removed directory: {target}")
                    else:
                        print(f"rm: cannot remove '{target}': Is a directory")
                elif os.path.isfile(target):
                    os.remove(target)
                    print(f"Removed file: {target}")
                else:
                    print(f"rm: cannot remove '{target}': No such file or directory")
            except PermissionError:
                if not force:
                    print(f"rm: cannot remove '{target}': Permission denied")

    def mkdir_command(self, args):
        """Create directories"""
        if not args:
            print("mkdir: missing operand")
            return

        for directory in args:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"Created directory: {directory}")
            except Exception as e:
                print(f"mkdir: cannot create directory '{directory}': {e}")

    def cat_command(self, args):
        """Display file contents"""
        if not args:
            print("cat: missing file operand")
            return

        for file_path in args:
            try:
                with open(file_path, 'r') as f:
                    print(f.read())
            except FileNotFoundError:
                print(f"cat: {file_path}: No such file or directory")
            except PermissionError:
                print(f"cat: {file_path}: Permission denied")
            except IsADirectoryError:
                print(f"cat: {file_path}: Is a directory")

    def touch_command(self, args):
        """Create empty files"""
        if not args:
            print("touch: missing file operand")
            return

        for file_path in args:
            try:
                os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
                with open(file_path, 'a'):
                    os.utime(file_path, None)
                print(f"Touched file: {file_path}")
            except Exception as e:
                print(f"touch: cannot touch '{file_path}': {e}")

    def colorize_filename(self, path, filename):
        """Apply color to filename based on file type"""
        full_path = os.path.join(path, filename)
        
        # Directories
        if os.path.isdir(full_path):
            return colored(filename + '/', 'blue', attrs=['bold'])
        
        # Executable files
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return colored(filename + '*', 'green', attrs=['bold'])
        
        # Symlinks
        if os.path.islink(full_path):
            return colored(filename + '@', 'cyan', attrs=['bold'])
        
        # Regular files
        return filename