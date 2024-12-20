# plugin_manager.py

import os
import importlib.util
import sys
class PluginManager:
    def __init__(self, shell):
        self.shell = shell
        self.loaded_plugins = {}
        self.plugin_dir = os.path.join(os.path.dirname(__file__), '..', 'plugins')

    def plugin_command(self, args):
        """Handle plugin commands"""
        if not args:
            print("Usage: plugin <command> <plugin_path>")
            return

        command = args[0]
        if command == "load":
            if len(args) < 2:
                print("Usage: plugin load <plugin_path>")
                return
            self.load_plugin(args[1])
        elif command == "list":
            self.list_plugins()
        else:
            print(f"Unknown plugin command: {command}")

    def load_plugin(self, plugin_path):
        """Dynamically load a Python plugin"""
        try:
            # Resolve absolute path
            abs_path = os.path.abspath(plugin_path)
            
            # Check if file exists
            if not os.path.exists(abs_path):
                print(f"Plugin not found: {abs_path}")
                return False

            # Load the plugin module
            module_name = os.path.splitext(os.path.basename(abs_path))[0]
            spec = importlib.util.spec_from_file_location(module_name, abs_path)
            module = importlib.util.module_from_spec(spec)
            
            # Add to sys.modules to allow imports within the plugin
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Check for plugin registration
            if hasattr(module, 'register_plugin'):
                plugin_info = module.register_plugin(self.shell)
                self.loaded_plugins[module_name] = plugin_info
                print(f"Plugin loaded: {module_name}")
                return True
            else:
                print(f"Invalid plugin format: {module_name}")
                return False

        except Exception as e:
            print(f"Error loading plugin {plugin_path}: {e}")
            return False

    def list_plugins(self):
        """List currently loaded plugins"""
        if not self.loaded_plugins:
            print("No plugins loaded.")
        else:
            print("\nLoaded plugins:")
            for name, info in self.loaded_plugins.items():
                print(f"\nPlugin: {name}")
                print(f"Description: {info.get('description', 'N/A')}")
                print(f"Version: {info.get('version', 'N/A')}")
                if 'commands' in info:
                    print("Commands:", ', '.join(info['commands']))