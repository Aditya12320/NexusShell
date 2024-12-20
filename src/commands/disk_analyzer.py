import os
import psutil
from pathlib import Path
import humanize

class DiskAnalyzer:
    def __init__(self, shell):
        self.shell = shell

    def disk_usage_command(self, args):
        """Analyze disk usage of directories and files"""
        if not args:
            # Show overall disk usage
            return self._show_system_disk_usage()
        
        path = args[0]
        if not os.path.exists(path):
            print(f"Error: Path '{path}' does not exist")
            return
        
        if os.path.isfile(path):
            self._show_file_size(path)
        else:
            self._analyze_directory(path)

    def _show_system_disk_usage(self):
        """Display system-wide disk usage"""
        partitions = psutil.disk_partitions()
        
        print("\nDisk Usage Summary:")
        print("-" * 80)
        print(f"{'Device':15} {'Mount Point':15} {'Total':10} {'Used':10} {'Free':10} {'Use%':8}")
        print("-" * 80)
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                print(f"{partition.device[:15]:15} "
                      f"{partition.mountpoint[:15]:15} "
                      f"{humanize.naturalsize(usage.total):10} "
                      f"{humanize.naturalsize(usage.used):10} "
                      f"{humanize.naturalsize(usage.free):10} "
                      f"{usage.percent:>6.1f}%")
            except PermissionError:
                continue

    def _show_file_size(self, path):
        """Show size information for a single file"""
        size = os.path.getsize(path)
        print(f"\nFile: {path}")
        print(f"Size: {humanize.naturalsize(size)}")

    def _analyze_directory(self, path, depth=1):
        """Analyze directory size recursively"""
        total_size = 0
        entries = []
        
        try:
            for entry in os.scandir(path):
                try:
                    if entry.is_file(follow_symlinks=False):
                        size = entry.stat().st_size
                        total_size += size
                        entries.append((entry.name, size, True))
                    elif entry.is_dir(follow_symlinks=False):
                        dir_size = self._get_dir_size(entry.path)
                        total_size += dir_size
                        entries.append((entry.name, dir_size, False))
                except (PermissionError, OSError):
                    continue

            # Sort entries by size (largest first)
            entries.sort(key=lambda x: x[1], reverse=True)
            
            # Print results
            print(f"\nDirectory Analysis: {path}")
            print(f"Total Size: {humanize.naturalsize(total_size)}")
            print("\nLargest Items:")
            print("-" * 60)
            print(f"{'Name':40} {'Size':10} {'Type':8}")
            print("-" * 60)
            
            for name, size, is_file in entries[:10]:  # Show top 10 items
                print(f"{name[:40]:40} {humanize.naturalsize(size):10} "
                      f"{'File' if is_file else 'Dir':8}")

        except PermissionError:
            print(f"Error: Permission denied for {path}")
        except Exception as e:
            print(f"Error analyzing directory: {e}")

    def _get_dir_size(self, path):
        """Calculate total size of a directory"""
        total = 0
        try:
            for entry in os.scandir(path):
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat().st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total += self._get_dir_size(entry.path)
                except (PermissionError, OSError):
                    continue
        except PermissionError:
            pass
        return total
    
    
# disk              # Show system-wide disk usage
# disk /path        # Analyze specific directory