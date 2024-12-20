#sample plugin.py
def greet(args):
    """Simple greeting command"""
    name = args[0] if args else "World"
    print(f"Hello, {name}!")

def calc(args):
    """Simple calculator command"""
    if len(args) != 3:
        print("Usage: calc <number> <operator> <number>")
        return
    
    try:
        num1 = float(args[0])
        operator = args[1]
        num2 = float(args[2])
        
        if operator == '+':
            result = num1 + num2
        elif operator == '-':
            result = num1 - num2
        elif operator == '*':
            result = num1 * num2
        elif operator == '/':
            result = num1 / num2
        else:
            print("Invalid operator. Use +, -, *, /")
            return
            
        print(f"Result: {result}")
    except ValueError:
        print("Please enter valid numbers")
    except ZeroDivisionError:
        print("Cannot divide by zero")

def register_plugin(shell):
    """Register plugin with the shell"""
    # Register the plugin's commands with the shell's command_handlers
    shell.command_handlers['greet'] = greet
    shell.command_handlers['calc'] = calc
    
    return {
        'name': 'Sample Plugin',
        'description': 'A sample plugin with greeting and calculator functions',
        'version': '1.0',
        'commands': ['greet', 'calc']
    }