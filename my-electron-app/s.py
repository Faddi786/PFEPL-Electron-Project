import sys
import subprocess
import os

def run_npm_and_save_to_file():
    if len(sys.argv) != 5:
        print("Usage: python script.py email password name id")
        return

    email = sys.argv[1]
    password = sys.argv[2]
    name = sys.argv[3]
    id = sys.argv[4]

    # Directory path where the script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Path to the "child-app" directory
    directory_path = os.path.join(script_dir, 'child-app')
    
    # Path to the second directory
    directory_path2 = os.path.join(script_dir, 'Electron-Apps', name)
    
    # Save data to the first text file
    data_to_save = f"Name: {name}\nID: {id}\nEmail: {email}\nPassword: {password}"
    file_path = os.path.join(directory_path, 'data.txt')
    try:
        with open(file_path, 'w') as file:
            file.write(data_to_save)
        print("Data saved to file:", file_path)
        
        # Save data to the second text file
        file_path2 = os.path.join(directory_path2, 'data.txt')
        os.makedirs(directory_path2, exist_ok=True)
        with open(file_path2, 'w') as file:
            file.write(data_to_save)
        print("Data saved to file:", file_path2)
        
        # Execute the npm command
        npm_path = r''  # Use the path to npm here
        subprocess.run([npm_path, 'run', 'package-windows'], cwd=directory_path, check=True)
        print("npm command executed successfully.")
        
    except subprocess.CalledProcessError as e:
        log_error(e)
    except Exception as e:
        log_error(e)

def log_error(error):
    log_file = "error.txt"
    with open(log_file, 'a') as file:
        file.write(f"An error occurred: {error}\n")

if __name__ == "__main__":
    run_npm_and_save_to_file()
