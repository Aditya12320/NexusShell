import os

class TreeView:
    def __init__(self, shell):
        self.shell = shell

    def tree_command(self, args):
        """Display directory structure in a tree-like format"""
        # Determine root directory
        root_dir = args[0] if args else '.'

        # Limit depth to prevent infinite recursion
        max_depth = 3
        if '-d' in args:
            try:
                max_depth = int(args[args.index('-d') + 1])
            except (ValueError, IndexError):
                print("Invalid depth specified")
                return

        def list_files(directory, prefix='', depth=0):
            if depth > max_depth:
                return

            try:
                contents = os.listdir(directory)
                contents.sort()

                for i, item in enumerate(contents):
                    path = os.path.join(directory, item)
                    is_last = (i == len(contents) - 1)
                    
                    # Determine prefix based on last item
                    current_prefix = prefix + ('└── ' if is_last else '├── ')
                    print(current_prefix + item)

                    # Recurse into subdirectories
                    if os.path.isdir(path) and not os.path.islink(path):
                        extension = '    ' if is_last else '│   '
                        list_files(path, prefix + extension, depth + 1)
            
            except PermissionError:
                print(f"Permission denied: {directory}")
            except Exception as e:
                print(f"Error listing directory: {e}")

        print(os.path.abspath(root_dir))
        list_files(root_dir)