
# NexusShell

NexusShell is a customizable and feature-rich shell application written in Python. This project is designed to enhance the traditional shell experience by providing additional utilities, plugins, and modern features for developers and system administrators.

## Features

### Core Features

- **Custom Command Execution**: Extend functionality with built-in and user-defined commands.
- **Advanced File Operations**: Perform file manipulations like viewing, editing, and encrypting files.
- **Script Interpretation**: Run custom scripts written for NexusShell.
- **Plugin System**: Add or remove plugins dynamically to extend shell functionality.

### Built-in Commands

- **Text Editor**: A lightweight built-in text editor.
- **File Encryption**: Encrypt and decrypt files securely.
- **Weather Command**: Fetch real-time weather data.
- **Tree View**: Display a hierarchical view of files and directories.
- **Disk Usage**: Analyze and display disk usage statistics.
- **Network Utilities**: Perform basic network diagnostics like ping and traceroute.
- **Process Manager**: Manage and monitor running processes.
- **Search Command**: Quickly search for files and directories.

### Utilities

- **Advanced `ls`**: Improved directory listing with additional metadata.
- **File Redirection**: Simplified file input/output redirection.
- **Prompt Customization**: Configure the shell prompt to suit your preferences.

## Project Structure

```
nexus_shell/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── shell.py
│   ├── completer.py
│   │
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── builtin_commands.py
│   │   ├── file_operations.py
│   │   ├── system_commands.py
│   │   ├── text_editor.py           # Built-in text editor
│   │   ├── file_encryption.py       # File encryption/decryption
│   │   ├── weather_command.py       # Weather command
│   │   ├── disk_usage.py            # Disk usage analysis
│   │   ├── network_utilities.py     # Network diagnostics
│   │   ├── process_manager.py       # Process management
│   │   └── search_command.py        # File search
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── advanced_ls.py
│   │   ├── file_redirection.py
│   │   ├── prompt_config.py
│   │   ├── plugin_manager.py        # Plugin management
│   │   └── script_interpreter.py    # Script interpretation
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   │
│   └── plugins/                     # Directory for user plugins
│       ├── __init__.py
│       └── sample_plugin.py
│
├── scripts/                         # Directory for shell scripts
│   ├── sample_script1.myshell
│   └── sample_script2.myshell
│
├── requirements.txt
├── README.md
└── setup.py
```

## Installation

### Prerequisites

- Python 3.7+
- pip

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/Aditya12320/NexusShell.git
   cd nexus_shell
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the shell:
   ```bash
   python src/main.py
   ```

## Usage

- Launch the shell using `python src/main.py`.
- Use built-in commands or extend functionality with custom plugins and scripts.
- View sample scripts in the `scripts/` directory.

## Plugin Development

- Add your custom plugins in the `src/plugins/` directory.
- Follow the structure of `sample_plugin.py` for creating new plugins.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
