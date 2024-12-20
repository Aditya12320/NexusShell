import os
import math
import stat
from datetime import datetime
import sys
from termcolor import colored
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AdvancedLS:
    @staticmethod
    def human_readable_size(size_bytes):
        """Convert bytes to human-readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_units = ['B', 'KB', 'MB', 'GB', 'TB']
        
        # Calculate appropriate unit
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        size = round(size_bytes / p, 2)
        
        return f"{size} {size_units[i]}"

    @staticmethod
    def is_executable(path):
        """Check if file is executable"""
        return os.access(path, os.X_OK)

    @staticmethod
    def get_file_permissions(mode):
        """Convert file mode to readable permission string"""
        is_dir = 'd' if stat.S_ISDIR(mode) else '-'
        owner = 'r' if mode & stat.S_IRUSR else '-'
        owner += 'w' if mode & stat.S_IWUSR else '-'
        owner += 'x' if mode & stat.S_IXUSR else '-'
        group = 'r' if mode & stat.S_IRGRP else '-'
        group += 'w' if mode & stat.S_IWGRP else '-'
        group += 'x' if mode & stat.S_IXGRP else '-'
        others = 'r' if mode & stat.S_IROTH else '-'
        others += 'w' if mode & stat.S_IWOTH else '-'
        others += 'x' if mode & stat.S_IXOTH else '-'
        
        return f"{is_dir}{owner}{group}{others}"