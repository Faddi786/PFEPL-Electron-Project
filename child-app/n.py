import sys

def save_to_notepad(data):
    # Save data to a text file
    with open('browse_paths.txt', 'w') as file:
        file.write(data)

if __name__ == "__main__":
    # Get data from command line arguments
    data = sys.argv[1]
    save_to_notepad(data)
