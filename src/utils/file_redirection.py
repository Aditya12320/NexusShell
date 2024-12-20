import os
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def handle_file_redirection(parts):
    """Handle file redirection"""
    try:
        if ">" in parts:
            operator_index = parts.index(">")
            command_args = parts[:operator_index]
            file_name = parts[operator_index + 1]
            mode = "w"  # Overwrite mode
        elif ">>" in parts:
            operator_index = parts.index(">>")
            command_args = parts[:operator_index]
            file_name = parts[operator_index + 1]
            mode = "a"  # Append mode

        file_name = file_name.strip().strip('"')
        os.makedirs(os.path.dirname(file_name) or ".", exist_ok=True)

        with open(file_name, mode) as f:
            result = subprocess.run(command_args, capture_output=True, text=True, shell=True)
            f.write(result.stdout)

    except Exception as e:
        print(f"Redirection error: {e}")