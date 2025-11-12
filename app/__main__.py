import sys
from app.main_cli import cli_main
from app.main_api import api_main

def main():
    if len(sys.argv) < 2:
        print("Invalid argument")
        return
    
    command = sys.argv[1].lower()
    if command == "cli":
        if len(sys.argv) < 3:
            print("Invalid argument")
            return
        file_path = sys.argv[2]
        cli_main(file_path)
    elif command == "api":
        api_main()
    else:
        print("Invalid argument")


if __name__ == "__main__":
    main()