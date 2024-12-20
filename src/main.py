import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.shell import EnhancedShell

def main():
    """Main entry point for the Enhanced Shell"""
    try:
        shell = EnhancedShell()
        shell.interactive_shell()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
