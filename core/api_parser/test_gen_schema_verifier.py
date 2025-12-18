import json
import sys
from jsonschema import validate, ValidationError
from datetime import datetime
import core.api_parser.test_gen_schema_verifier_helper as helper
import ValidationReport as vr

# NEW: Main validator class
class ConfigValidator:
    """Main validator that ties everything together."""
    
    def __init__(self, schema_path):
        """
        Initialize validator with a schema.
        
        Args:
            schema_path: Path to the JSON schema file
        """
        self.schema_path = schema_path
        self.schema = None
    
    def load_schema(self):
        """Load the schema file."""
        try:
            self.schema = helper.load_json_file(self.schema_path)
            return True
        except Exception as e:
            print(f"Error loading schema: {e}")
            return False
    
    def validate_file(self, config_path, verbose=True):
        """
        Validate a configuration file.
        
        Args:
            config_path: Path to config file to validate
            verbose: If True, print detailed progress
            
        Returns:
            True if valid, False otherwise
        """
        report = vr.ValidationReport(config_path)
        
        # Load schema
        if not self.schema:
            if not self.load_schema():
                return False
        
        # Load config
        if verbose:
            print("Loading configuration...")
        
        try:
            config = helper.load_json_file(config_path)
            if verbose:
                print("✓ Configuration loaded")
        except Exception as e:
            print(f"✗ Error loading configuration: {e}")
            return False
        
        # Schema validation
        if verbose:
            print("\nValidating against schema...")
        
        is_valid, schema_errors = helper.validate_against_schema(config, self.schema)
        report.schema_errors = schema_errors
        
        if verbose:
            if is_valid:
                print("✓ Schema validation passed")
            else:
                print(f"✗ Schema validation failed ({len(schema_errors)} error(s))")
        
        # Custom validation
        if verbose:
            print("\nRunning custom validations...")
        
        custom_errors = helper.run_custom_validations(config)
        report.custom_errors = custom_errors
        
        if verbose:
            if not custom_errors:
                print("✓ Custom validations passed")
            else:
                print(f"✗ Custom validations failed ({len(custom_errors)} error(s))")
        
        # Final result
        report.is_valid = is_valid and not custom_errors
        
        # Print report
        print(report.generate())
        
        return report.is_valid


# NEW: Command-line interface
def main():
    """Command-line interface for the validator."""
    
    # Parse command-line arguments
    if len(sys.argv) < 3:
        print("Usage: python validator.py <config_file> <schema_file> [--quiet]")
        print("")
        print("Examples:")
        print("  python validator.py test_config.json schema.json")
        print("  python validator.py test_config.json schema.json --quiet")
        print("")
        sys.exit(1)
    
    config_file = sys.argv[1]
    schema_file = sys.argv[2]
    quiet = "--quiet" in sys.argv
    
    # Validate
    validator = ConfigValidator(schema_file)
    is_valid = validator.validate_file(config_file, verbose=not quiet)
    
    # Exit with appropriate code
    # 0 = success, 1 = failure
    sys.exit(0 if is_valid else 1)


# For importing as a library
def validate_config(config_path, schema_path):
    """
    Simple function to validate a config file.
    
    Args:
        config_path: Path to configuration file
        schema_path: Path to schema file
        
    Returns:
        True if valid, False otherwise
    """
    validator = ConfigValidator(schema_path)
    return validator.validate_file(config_path, verbose=True)


if __name__ == "__main__":
    main()