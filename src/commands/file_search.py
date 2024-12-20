import os
import fnmatch
import re
from datetime import datetime
from typing import List, Dict, Generator
from pathlib import Path
import time

class FileSearch:
    def __init__(self, shell):
        self.shell = shell

    def search_command(self, args):
        """Handle file search commands"""
        if not args:
            return self._show_usage()
            
        # Parse arguments
        try:
            options = self._parse_search_args(args)
        except ValueError as e:
            print(f"Error: {e}")
            return self._show_usage()
            
        # Perform search
        try:
            results = list(self._search_files(**options))
            self._display_results(results, options)
        except Exception as e:
            print(f"Error during search: {e}")

    def _show_usage(self):
        """Show search command usage information"""
        print("\nFile Search Usage:")
        print("  search <pattern> [options]")
        print("\nOptions:")
        print("  -p, --path <path>     Search in specific path (default: current directory)")
        print("  -t, --type f|d        Search for files (f) or directories (d)")
        print("  -s, --size <size>     Search by size (e.g., +1M, -500K)")
        print("  -d, --date <date>     Search by modification date (e.g., +7d, -30d)")
        print("  -r, --regex           Use regular expression pattern")
        print("  -c, --content <text>  Search file contents")
        print("\nExamples:")
        print("  search *.txt")
        print("  search -p /home -t f -s +1M")
        print("  search -r \".*\\.py$\" -d -7d")
        print("  search -c \"TODO\" *.py")

    def _parse_search_args(self, args) -> Dict:
        """Parse search command arguments"""
        options = {
            'pattern': None,
            'path': '.',
            'type': None,
            'size': None,
            'date': None,
            'regex': False,
            'content': None
        }
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            if arg.startswith('-'):
                if arg in ['-p', '--path'] and i + 1 < len(args):
                    options['path'] = args[i + 1]
                    i += 2
                elif arg in ['-t', '--type'] and i + 1 < len(args):
                    if args[i + 1] not in ['f', 'd']:
                        raise ValueError("Type must be 'f' for files or 'd' for directories")
                    options['type'] = args[i + 1]
                    i += 2
                elif arg in ['-s', '--size'] and i + 1 < len(args):
                    options['size'] = self._parse_size(args[i + 1])
                    i += 2
                elif arg in ['-d', '--date'] and i + 1 < len(args):
                    options['date'] = self._parse_date(args[i + 1])
                    i += 2
                elif arg in ['-r', '--regex']:
                    options['regex'] = True
                    i += 1
                elif arg in ['-c', '--content'] and i + 1 < len(args):
                    options['content'] = args[i + 1]
                    i += 2
                else:
                    raise ValueError(f"Invalid option or missing value: {arg}")
            else:
                options['pattern'] = arg
                i += 1
        
        if not options['pattern'] and not options['content']:
            raise ValueError("Search pattern or content is required")
            
        return options

    def _parse_size(self, size_str: str) -> tuple:
        """Parse size string (e.g., +1M, -500K) into bytes"""
        units = {'K': 1024, 'M': 1024**2, 'G': 1024**3}
        match = re.match(r'^([+-])(\d+)([KMG])?$', size_str)
        if not match:
            raise ValueError("Invalid size format")
            
        op, size, unit = match.groups()
        multiplier = units.get(unit, 1) if unit else 1
        size_bytes = int(size) * multiplier
        return (op, size_bytes)

    def _parse_date(self, date_str: str) -> float:
        """Parse date string (e.g., +7d, -30d) into timestamp"""
        match = re.match(r'^([+-])(\d+)d$', date_str)
        if not match:
            raise ValueError("Invalid date format")
            
        op, days = match.groups()
        seconds = int(days) * 24 * 60 * 60
        reference_time = time.time()
        
        if op == '+':
            return reference_time - seconds
        else:
            return reference_time + seconds

    def _search_files(self, **options) -> Generator:
        """Search for files matching the given criteria"""
        for root, dirs, files in os.walk(options['path']):
            items = dirs if options['type'] == 'd' else files if options['type'] == 'f' else dirs + files
            
            for item in items:
                path = os.path.join(root, item)
                
                # Check pattern match
                if options['pattern']:
                    if options['regex']:
                        if not re.match(options['pattern'], item):
                            continue
                    elif not fnmatch.fnmatch(item, options['pattern']):
                        continue
                
                try:
                    stat = os.stat(path)
                    
                    # Check size
                    if options['size']:
                        op, size = options['size']
                        if op == '+' and stat.st_size < size:
                            continue
                        if op == '-' and stat.st_size > size:
                            continue
                    
                    # Check date
                    if options['date']:
                        if stat.st_mtime < options['date']:
                            continue
                    
                    # Check content
                    if options['content']:
                        if os.path.isfile(path):
                            try:
                                with open(path, 'r', encoding='utf-8') as f:
                                    if options['content'] not in f.read():
                                        continue
                            except (UnicodeDecodeError, IOError):
                                continue
                        else:
                            continue
                    
                    yield {
                        'path': path,
                        'size': stat.st_size,
                        'mtime': stat.st_mtime,
                        'type': 'dir' if os.path.isdir(path) else 'file'
                    }
                    
                except (OSError, PermissionError):
                    continue

    def _display_results(self, results: List[Dict], options: Dict):
        """Display search results"""
        if not results:
            print("No matches found")
            return
            
        print(f"\nFound {len(results)} matches:")
        print("-" * 80)
        
        for result in results:
            mtime = datetime.fromtimestamp(result['mtime']).strftime('%Y-%m-%d %H:%M')
            size = '' if result['type'] == 'dir' else self._format_size(result['size'])
            print(f"{result['type']:4} {mtime:16} {size:10} {result['path']}")

    def _format_size(self, size: int) -> str:
        """Format size in human readable format"""
        for unit in ['', 'K', 'M', 'G', 'T']:
            if size < 1024:
                return f"{size:3.1f}{unit}"
            size /= 1024
        return f"{size:.1f}P"
    
    
    
# search *.txt                         # Find all .txt files
# search -p /home -t f -s +1M         # Find files larger than 1MB in /home
# search -r ".*\.py$" -d -7d          # Find Python files modified in last 7 days
# search -c "TODO" *.py               # Search Python files containing "TODO"