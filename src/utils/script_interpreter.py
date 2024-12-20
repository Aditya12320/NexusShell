import os
import re

class ScriptInterpreter:
    def __init__(self, shell):
        self.shell = shell
        self.variables = {}

    def run_script(self, script_path):
        """Run a .myshell script"""
        try:
            with open(script_path, 'r') as script_file:
                lines = script_file.readlines()

            line_num = 0
            while line_num < len(lines):
                line = lines[line_num].strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    line_num += 1
                    continue

                # Variable assignment
                if '=' in line and not line.startswith('if'):
                    self.handle_variable_assignment(line)
                    line_num += 1
                    continue

                # Conditional processing
                if line.startswith('if'):
                    line_num = self.handle_conditional(line_num, lines)
                    continue

                # Loop processing
                if line.startswith('for'):
                    line_num = self.handle_for_loop(line_num, lines)
                    continue

                # Command execution
                self.execute_line(line)
                line_num += 1

        except FileNotFoundError:
            print(f"Script not found: {script_path}")
        except Exception as e:
            print(f"Error running script at line {line_num + 1}: {e}")

    def execute_line(self, line):
        """Execute a single line of script"""
        try:
            # Replace variables
            line = self.replace_variables(line)
            
            # Execute through shell's run_command
            self.shell.run_command(line)
        except Exception as e:
            print(f"Error executing command '{line}': {e}")

    def replace_variables(self, line):
        """Replace variables in a line"""
        for var, value in self.variables.items():
            line = line.replace(f'${var}', str(value))
        return line

    def handle_variable_assignment(self, line):
        """Handle variable assignments"""
        try:
            var, value = line.split('=', 1)
            var = var.strip()
            value = value.strip()
            
            # Handle string literals
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            
            # Handle command substitution
            if value.startswith('$(') and value.endswith(')'):
                command = value[2:-1]
                # Execute command and capture output
                # This is a placeholder - actual implementation would depend on shell capabilities
                value = self.shell.run_command_capture_output(command)

            self.variables[var] = value
        except Exception as e:
            print(f"Error in variable assignment: {e}")

    def handle_conditional(self, current_line, lines):
        """Handle conditional logic with if/else blocks"""
        try:
            line = lines[current_line].strip()
            match = re.match(r'if\s+\[(.*?)\]', line)
            if not match:
                raise ValueError("Invalid if statement syntax")

            condition = match.group(1).strip()
            block_start = current_line + 1
            
            # Find matching 'fi' or 'else'
            nesting_level = 1
            else_line = None
            end_line = None
            
            for i in range(block_start, len(lines)):
                line = lines[i].strip()
                if line.startswith('if'):
                    nesting_level += 1
                elif line == 'else' and nesting_level == 1:
                    else_line = i
                elif line == 'fi':
                    nesting_level -= 1
                    if nesting_level == 0:
                        end_line = i
                        break

            if end_line is None:
                raise ValueError("Missing 'fi' statement")

            # Evaluate condition
            condition_met = self.evaluate_condition(condition)
            
            if condition_met:
                # Execute if block
                block_end = else_line if else_line else end_line
                self.execute_block(lines[block_start:block_end])
            elif else_line:
                # Execute else block
                self.execute_block(lines[else_line + 1:end_line])

            return end_line + 1
        except Exception as e:
            print(f"Error in conditional block: {e}")
            return current_line + 1

    def handle_for_loop(self, current_line, lines):
        """Handle for loop with proper block execution"""
        try:
            line = lines[current_line].strip()
            match = re.match(r'for\s+(\w+)\s+in\s+\[(.*?)\]', line)
            if not match:
                raise ValueError("Invalid for loop syntax")

            var_name = match.group(1)
            items = [item.strip().strip("'\"") for item in match.group(2).split(',')]
            
            # Find matching 'done'
            block_start = current_line + 1
            nesting_level = 1
            
            for i in range(block_start, len(lines)):
                line = lines[i].strip()
                if line.startswith('for'):
                    nesting_level += 1
                elif line == 'done':
                    nesting_level -= 1
                    if nesting_level == 0:
                        block_end = i
                        break
            else:
                raise ValueError("Missing 'done' statement")

            # Execute loop
            loop_block = lines[block_start:block_end]
            for item in items:
                self.variables[var_name] = item
                self.execute_block(loop_block)

            return block_end + 1
        except Exception as e:
            print(f"Error in for loop: {e}")
            return current_line + 1

    def execute_block(self, block_lines):
        """Execute a block of code"""
        for line in block_lines:
            line = line.strip()
            if line and not line.startswith('#'):
                self.execute_line(line)

    def evaluate_condition(self, condition):
        """Evaluate a conditional expression"""
        try:
            # Replace variables in condition
            condition = self.replace_variables(condition)
            
            # Handle different comparison operators
            if '==' in condition:
                left, right = condition.split('==')
                return left.strip() == right.strip()
            elif '!=' in condition:
                left, right = condition.split('!=')
                return left.strip() != right.strip()
            elif '-eq' in condition:
                left, right = condition.split('-eq')
                return int(left.strip()) == int(right.strip())
            elif '-lt' in condition:
                left, right = condition.split('-lt')
                return int(left.strip()) < int(right.strip())
            elif '-gt' in condition:
                left, right = condition.split('-gt')
                return int(left.strip()) > int(right.strip())
            elif '-f' in condition:
                # Check if file exists
                filename = condition.split('-f')[1].strip()
                return os.path.isfile(filename)
            elif '-d' in condition:
                # Check if directory exists
                dirname = condition.split('-d')[1].strip()
                return os.path.isdir(dirname)
            else:
                # Treat as boolean value
                return bool(condition.strip())
        except Exception as e:
            print(f"Error evaluating condition '{condition}': {e}")
            return False