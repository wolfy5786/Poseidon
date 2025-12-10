"""
Part 1: Basic JSON Validator
Learn: How to load and validate JSON files
"""

import json


def load_json_file(file_path):
    """
    Load a JSON file and return its contents.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    # Open and read the file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    return data


def is_valid_json_file(file_path):
    """
    Check if a file contains valid JSON.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        True if valid JSON, False otherwise
    """
    try:
        load_json_file(file_path)
        print(f"✓ '{file_path}' is valid JSON")
        return True
    
    except FileNotFoundError:
        print(f"✗ File not found: {file_path}")
        return False
    
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in '{file_path}'")
        print(f"  Error: {e.msg} at line {e.lineno}")
        return False


# Example usage
if __name__ == "__main__":
    # Test with a file
    print("Testing JSON validation:")
    print("-" * 50)
    
    # This will check if your file is valid JSON
    is_valid = is_valid_json_file("test_config.json")
    
    if is_valid:
        # Load and print the data
        data = load_json_file("test_config.json")
        print(f"\nLoaded data has {len(data)} top-level keys")
        print(f"Keys: {list(data.keys())}")