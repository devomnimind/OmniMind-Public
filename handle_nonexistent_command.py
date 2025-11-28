from error_handler import handle_exception

def nonexistent_command_xyz(arg):
    try:
        # Call the function for existing commands
        return existing_command(arg)
    except NameError:
        # Handle non-existing command
        handle_exception('nonexistent_command_xyz')
