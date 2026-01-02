from core.api_parser import specs_validator as spv

class Orchestrator:
    def __init__(self, input_specs_path):
        self.input_specs_path = input_specs_path
        self.specs_schema_path = "./config/specs_schema_v2.json"
    
    def test_fun(self):
        print("Orchestrator test function called")
    
    def specs_validation(self):
        return spv.validate_config(self.input_specs_path, self.specs_schema_path)
    
    def generate_tests(self):
        pass

    def execute(self):
        pass

    def report(self):
        pass

    def cleanup(self):
        pass
    

    