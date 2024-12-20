import os
import tempfile
import subprocess
import platform
import shutil

class TextEditor:
    def __init__(self, shell):
        self.shell = shell
        self.system = platform.system()
        # List of possible editors to try on Windows
        self.windows_editors = [
            ('code', 'Visual Studio Code'),
            ('notepad++', 'Notepad++'),
            ('sublime_text', 'Sublime Text'),
            ('atom', 'Atom'),
            ('vim', 'Vim'),
            ('notepad.exe', 'Windows Notepad')  # Fallback option
        ]
        # Try to load preferred editor from config or environment
        self.preferred_editor = os.environ.get('ENHANCED_SHELL_EDITOR', None)

    def find_editor(self):
        """Find the first available editor on the system"""
        if self.preferred_editor:
            editor_path = shutil.which(self.preferred_editor)
            if editor_path:
                return self.preferred_editor

        for editor, name in self.windows_editors:
            editor_path = shutil.which(editor)
            if editor_path:
                print(f"Using {name} as text editor")
                return editor
        
        return 'notepad.exe'  # Final fallback

    def set_preferred_editor(self, editor_name):
        """Set the preferred editor for future use"""
        if shutil.which(editor_name):
            self.preferred_editor = editor_name
            os.environ['ENHANCED_SHELL_EDITOR'] = editor_name
            print(f"Set {editor_name} as preferred editor")
        else:
            print(f"Editor {editor_name} not found on system")

    def edit_command(self, args):
        """
        Enhanced text editor command with support for multiple editors
        Usage: 
            edit <filename> : Edit a file
            edit --set-editor <editor> : Set preferred editor
            edit --list-editors : List available editors
        """
        if not args:
            print("Usage: edit <filename> or edit --set-editor <editor>")
            return

        if args[0] == '--set-editor' and len(args) > 1:
            self.set_preferred_editor(args[1])
            return

        if args[0] == '--list-editors':
            print("Available editors found on your system:")
            for editor, name in self.windows_editors:
                if shutil.which(editor):
                    print(f"- {name} ({editor})")
            return

        filename = args[0]
        
        try:
            # Create file if it doesn't exist
            if not os.path.exists(filename):
                open(filename, 'a').close()
            
            editor = self.find_editor()
            
            try:
                if editor == 'code':  # VS Code needs special handling
                    subprocess.run([editor, '--wait', filename], check=True)
                else:
                    subprocess.run([editor, filename], check=True)
                print(f"Edited file: {filename}")
            except subprocess.CalledProcessError as e:
                print(f"Error running editor: {e}")
                print("Try setting a different editor with 'edit --set-editor <editor>'")
        
        except Exception as e:
            print(f"Error editing file: {e}")
            print("Make sure the file path is correct and you have write permissions.")

    def inline_edit(self, filename):
        """
        Inline text editing with a temporary file
        """
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            try:
                # If file exists, read its content
                if os.path.exists(filename):
                    with open(filename, 'r') as existing_file:
                        temp_file.write(existing_file.read())
                
                temp_file.flush()
                
                editor = self.find_editor()
                if editor == 'code':  # VS Code needs special handling
                    subprocess.run([editor, '--wait', temp_file.name], check=True)
                else:
                    subprocess.run([editor, temp_file.name], check=True)
                
                # Read edited content
                with open(temp_file.name, 'r') as edited_file:
                    content = edited_file.read()
                
                # Write back to original file
                with open(filename, 'w') as original_file:
                    original_file.write(content)
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
                
                
                
                
# List available editors:

# edit --list-editors

# Set your preferred editor (examples):

# edit --set-editor code        # For VS Code
# edit --set-editor notepad++   # For Notepad++
# edit --set-editor sublime_text # For Sublime Text

# Edit a file:

# bashCopyedit shell.py