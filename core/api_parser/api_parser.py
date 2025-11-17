from config import Config
import yaml 

class APIParser:
    def __init__(self):
        pass

    def load_config(self, config_file_path: str):
        with open(config_file_path, 'r') as file:
            config_data = yaml.safe_load(file)
            self.config = Config(**config_data["config"])  # unpacking dictionary to dataclass
    
    def load_OpenAPI_doc(self):
        pass
    
    def load_swagger_doc(self):
        pass
    
    def call_API_parser(self):
        pass
    