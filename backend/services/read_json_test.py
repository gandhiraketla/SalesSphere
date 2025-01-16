import json

class JSONFileReader:
    def __init__(self):
        """
        Initializes the JSONFileReader with the file path.
        :param file_path: Path to the JSON file
        """
        self.file_path = r"C:\\SalesSphere\\backend\\retail_startup.json"

    def read_json(self):
        """
        Reads a JSON file and returns its contents as a Python object.
        :return: Parsed JSON data or None if an error occurs
        """
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)  # Parse the JSON file
            return data
        except FileNotFoundError:
            print(f"Error: The file at {self.file_path} was not found.")
            return None
        except json.JSONDecodeError:
            print(f"Error: The file at {self.file_path} is not a valid JSON file.")
            return None

# Main method
if __name__ == "__main__":
    # Specify the file path
    file_path = r"C:\\SalesSphere\\backend\\retail_startup.json"

    # Create an instance of the JSONFileReader class
    reader = JSONFileReader()

    # Read the JSON file
    json_data = reader.read_json()

    # Print the JSON data
    if json_data is not None:
        print(json.dumps(json_data, indent=4))  # Pretty-print the JSON
