import os

def run_command(user_input):
    os.system("ls " + user_input)  # os-system-injection, typically High severity