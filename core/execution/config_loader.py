class ConfigLoader:
    """
    A class to load and manage configuration from .env files.
    """
    
    def __init__(self, filepath):
        """
        Initialize the ConfigLoader with a filepath.
        
        Args:
            filepath (str): Path to the .env file. Defaults to '.env'
        """
        self.filepath = filepath
        self.config = {}
    
    def load(self):
        """
        Read the .env file and store its contents in a dictionary.
        Parses KEY=VALUE pairs and handles comments and empty lines.
        
        Returns:
            bool: True if load was successful, False otherwise
        """
        self.config = {}
        
        try:
            with open(self.filepath, 'r') as file:
                for line in file:
                    # Strip whitespace
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Split on first '=' only
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        self.config[key] = value
            
            return True
            
        except FileNotFoundError:
            print(f"Error: File '{self.filepath}' not found.")
            return False
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
    
    def get(self, key, default=None):
        """
        Retrieve a value from the configuration dictionary.
        
        Args:
            key (str): The configuration key to retrieve
            default: Default value to return if key doesn't exist. Defaults to None
        
        Returns:
            The value associated with the key, or default if key doesn't exist
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        Temporarily add or update a key-value pair in the configuration dictionary.
        This does NOT write to the .env file, only updates the in-memory dict.
        
        Args:
            key (str): The configuration key to set
            value: The value to associate with the key
        """
        self.config[key] = value