# import os
# from typing import Iterable
# from prompt_toolkit.completion import Completer, Completion
# from prompt_toolkit.document import Document

# class EnhancedCompleter(Completer):
#     def __init__(self, shell):
#         """Initialize the completer with a reference to the shell instance"""
#         self.shell = shell

#     def get_completions(self, document: Document, complete_event) -> Iterable[Completion]:
#         """Get completions for the current input."""
#         word_before_cursor = document.get_word_before_cursor(WORD=True)
#         text_before_cursor = document.text_before_cursor

#         # Default to command completion
#         yield from self._get_command_completions(word_before_cursor)

#         # If we're not at the start of a command, do path completion
#         if ' ' in text_before_cursor:
#             yield from self._get_path_completions(word_before_cursor)

#     def _get_command_completions(self, word_before_cursor: str) -> Iterable[Completion]:
#         """Get completions for commands, including builtins and aliases"""
#         # Add shell builtins from the shell instance
#         for cmd in self.shell.shell_builtins:
#             if cmd.startswith(word_before_cursor):
#                 yield Completion(
#                     cmd,
#                     start_position=-len(word_before_cursor),
#                     display_meta='Shell builtin'
#                 )

#         # Add aliases from the shell instance
#         for alias in self.shell.aliases:
#             if alias.startswith(word_before_cursor):
#                 yield Completion(
#                     alias,
#                     start_position=-len(word_before_cursor),
#                     display_meta=f'Alias: {self.shell.aliases[alias]}'
#                 )

#         # Add executables from PATH
#         for executable in self._get_executables():
#             if executable.startswith(word_before_cursor):
#                 yield Completion(
#                     executable,
#                     start_position=-len(word_before_cursor),
#                     display_meta='Executable'
#                 )

#     def _get_path_completions(self, word_before_cursor: str) -> Iterable[Completion]:
#         """Get completions for paths (files and directories)"""
#         try:
#             # Expand user home directory if necessary
#             path = os.path.expanduser(word_before_cursor)
#             dirname = os.path.dirname(path) or '.'
#             prefix = os.path.basename(path)

#             # List directory contents
#             for name in os.listdir(dirname):
#                 if name.startswith(prefix):
#                     full_path = os.path.join(dirname, name)
#                     is_dir = os.path.isdir(full_path)
                    
#                     # Add trailing slash for directories
#                     display_name = name + ('/' if is_dir else '')
#                     completion_text = f'"{display_name}"' if ' ' in display_name else display_name

#                     yield Completion(
#                         completion_text,
#                         start_position=-len(prefix),
#                         display_meta='Directory' if is_dir else 'File'
#                     )
#         except (OSError, PermissionError):
#             pass

#     def _get_executables(self) -> set:
#         """Get executable files from PATH"""
#         executables = set()
#         for path in os.environ.get("PATH", "").split(os.pathsep):
#             if not path:
#                 continue
#             try:
#                 for item in os.listdir(path):
#                     full_path = os.path.join(path, item)
#                     if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
#                         executables.add(item)
#             except (FileNotFoundError, PermissionError):
#                 continue
#         return executables