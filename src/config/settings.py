# Configuration settings for the enhanced shell

# Default shell configuration
DEFAULT_CONFIG = {
    'history_limit': 500,
    'config_directory': '~/.mycmd',
    'default_aliases': {
        'll': 'ls -l',
        'la': 'ls -a',
        'cls': 'clear'
    },
    'prompt_settings': {
        'show_username': True,
        'show_hostname': True,
        'show_directory': True,
        'show_time': True
    }
}

# Add more configuration options as needed
SHELL_VERSION = "Enhanced Python Shell v1.0"