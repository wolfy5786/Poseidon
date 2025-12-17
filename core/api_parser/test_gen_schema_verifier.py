"""
Part 4: Nice Reports and Command-Line Interface
Learn: How to make a professional validator tool
"""

import json
import sys
from jsonschema import validate, ValidationError
from datetime import datetime


def load_json_file(file_path):
    """Load a JSON file and return its contents."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def validate_against_schema(data, schema):
    """Check if data matches the schema rules."""
    try:
        validate(instance=data, schema=schema)
        return True, []
    except ValidationError as e:
        error_message = f"{e.message}"
        if e.path:
            path = " -> ".join(str(p) for p in e.path)
            error_message = f"At '{path}': {error_message}"
        return False, [error_message]


def check_unique_orders(config):
    """Rule: Test order numbers must be unique."""
    errors = []
    all_tests = []
    
    if 'tests' in config:
        all_tests = config['tests']
    
    if 'test_suites' in config:
        for suite in config['test_suites']:
            if 'tests' in suite:
                all_tests.extend(suite['tests'])
    
    orders = [t['order'] for t in all_tests if 'order' in t]
    
    seen = set()
    duplicates = set()
    for order in orders:
        if order in seen:
            duplicates.add(order)
        seen.add(order)
    
    if duplicates:
        errors.append(f"Duplicate test orders: {sorted(duplicates)}")
    
    return errors


def check_test_dependencies(config):
    """Rule: Test dependencies must reference existing tests."""
    errors = []
    all_tests = []
    
    if 'tests' in config:
        all_tests = config['tests']
    
    if 'test_suites' in config:
        for suite in config['test_suites']:
            if 'tests' in suite:
                all_tests.extend(suite['tests'])
    
    all_test_names = {t.get('name') for t in all_tests if 'name' in t}
    
    for test in all_tests:
        test_name = test.get('name', 'unnamed test')
        
        if 'depends_on' in test:
            for dependency in test['depends_on']:
                if dependency not in all_test_names:
                    errors.append(f"Test '{test_name}' depends on non-existent '{dependency}'")
        
        if 'use_response_from' in test:
            referenced = test['use_response_from'].get('test_name')
            if referenced and referenced not in all_test_names:
                errors.append(f"Test '{test_name}' references non-existent '{referenced}'")
    
    return errors


def check_required_auth_fields(config):
    """Rule: Auth configuration must have required fields for its type."""
    errors = []
    
    if 'global_auth' not in config:
        return errors
    
    auth = config['global_auth']
    auth_type = auth.get('type')
    
    if auth_type == 'bearer' and 'bearer' not in auth:
        errors.append("Bearer auth missing 'bearer' configuration")
    elif auth_type == 'basic' and 'basic' not in auth:
        errors.append("Basic auth missing 'basic' configuration")
    elif auth_type == 'api_key' and 'api_key' not in auth:
        errors.append("API key auth missing 'api_key' configuration")
    
    return errors


def check_circular_dependencies(config):
    """
    Rule: Tests cannot have circular dependencies (loops).
    
    Example of a loop:
    - Test A depends on Test B
    - Test B depends on Test C  
    - Test C depends on Test A  <-- This creates a loop!
    
    Why this matters:
    If there's a loop, we can't determine the order to run tests.
    
    Args:
        config: Your test configuration
        
    Returns:
        List of error messages describing any loops found
    """
    errors = []
    
    # Step 1: Collect all tests and their dependencies
    all_tests = []
    
    if 'tests' in config:
        all_tests = config['tests']
    
    if 'test_suites' in config:
        for suite in config['test_suites']:
            if 'tests' in suite:
                all_tests.extend(suite['tests'])
    
    # Step 2: Build the dependency graph
    # Graph structure: {test_name: [list of tests it depends on]}
    graph = {}
    
    for test in all_tests:
        test_name = test.get('name')
        if not test_name:
            continue
        
        dependencies = []
        
        # Add depends_on dependencies
        if 'depends_on' in test:
            dependencies.extend(test['depends_on'])
        
        # Add use_response_from dependencies
        if 'use_response_from' in test:
            referenced = test['use_response_from'].get('test_name')
            if referenced:
                dependencies.append(referenced)
        
        graph[test_name] = dependencies
    
    # Step 3: Detect cycles using Depth-First Search (DFS)
    def find_cycle(node, visited, path):
        """
        Use DFS to find cycles in the graph.
        
        Args:
            node: Current test we're checking
            visited: Set of tests we've completely checked
            path: Current path we're exploring (to detect cycles)
            
        Returns:
            List representing the cycle if found, None otherwise
        """
        # If we've seen this node in our current path, we found a cycle!
        if node in path:
            # Return the cycle
            cycle_start = path.index(node)
            return path[cycle_start:] + [node]
        
        # If we've already fully explored this node, skip it
        if node in visited:
            return None
        
        # Add to current path
        path.append(node)
        
        # Check all dependencies
        if node in graph:
            for dependency in graph[node]:
                cycle = find_cycle(dependency, visited, path)
                if cycle:
                    return cycle
        
        # Remove from path (backtrack)
        path.remove(node)
        
        # Mark as fully visited
        visited.add(node)
        
        return None
    
    # Step 4: Check each test for cycles
    visited = set()
    
    for test_name in graph:
        if test_name not in visited:
            cycle = find_cycle(test_name, visited, [])
            
            if cycle:
                # Format the cycle nicely
                cycle_str = " → ".join(cycle)
                errors.append(f"Circular dependency detected: {cycle_str}")
    
    return errors


def run_custom_validations(config):
    """Run all custom validation checks."""
    all_errors = []
    
    all_errors.extend(check_unique_orders(config))
    all_errors.extend(check_test_dependencies(config))
    all_errors.extend(check_required_auth_fields(config))
    all_errors.extend(check_circular_dependencies(config))
    
    return all_errors


# NEW: Report generator
class ValidationReport:
    """Creates nice-looking validation reports."""
    
    def __init__(self, config_path):
        self.config_path = config_path
        self.schema_errors = []
        self.custom_errors = []
        self.is_valid = False
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate(self):
        """Generate a formatted report."""
        lines = []
        
        # Header
        lines.append("")
        lines.append("╔" + "═" * 68 + "╗")
        lines.append("║" + " " * 68 + "║")
        lines.append("║" + "  API TEST CONFIGURATION VALIDATION REPORT".center(68) + "║")
        lines.append("║" + " " * 68 + "║")
        lines.append("╚" + "═" * 68 + "╝")
        lines.append("")
        
        # File info
        lines.append(f"Configuration File: {self.config_path}")
        lines.append(f"Validation Time:    {self.timestamp}")
        lines.append("")
        
        # Overall result
        if self.is_valid:
            lines.append("┌" + "─" * 68 + "┐")
            lines.append("│  " + "✓ VALIDATION PASSED".ljust(66) + "│")
            lines.append("│" + " " * 68 + "│")
            lines.append("│  " + "Your configuration is valid and ready to use!".ljust(66) + "│")
            lines.append("└" + "─" * 68 + "┘")
        else:
            total_errors = len(self.schema_errors) + len(self.custom_errors)
            lines.append("┌" + "─" * 68 + "┐")
            lines.append("│  " + "✗ VALIDATION FAILED".ljust(66) + "│")
            lines.append("│" + " " * 68 + "│")
            lines.append("│  " + f"Found {total_errors} error(s) that need to be fixed".ljust(66) + "│")
            lines.append("└" + "─" * 68 + "┘")
            lines.append("")
            
            # Schema errors
            if self.schema_errors:
                lines.append("Schema Validation Errors:")
                lines.append("─" * 70)
                for i, error in enumerate(self.schema_errors, 1):
                    lines.append(f"{i}. {error}")
                lines.append("")
            
            # Custom errors
            if self.custom_errors:
                lines.append("Business Logic Errors:")
                lines.append("─" * 70)
                for i, error in enumerate(self.custom_errors, 1):
                    lines.append(f"{i}. {error}")
                lines.append("")
        
        lines.append("")
        return "\n".join(lines)


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
            self.schema = load_json_file(self.schema_path)
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
        report = ValidationReport(config_path)
        
        # Load schema
        if not self.schema:
            if not self.load_schema():
                return False
        
        # Load config
        if verbose:
            print("Loading configuration...")
        
        try:
            config = load_json_file(config_path)
            if verbose:
                print("✓ Configuration loaded")
        except Exception as e:
            print(f"✗ Error loading configuration: {e}")
            return False
        
        # Schema validation
        if verbose:
            print("\nValidating against schema...")
        
        is_valid, schema_errors = validate_against_schema(config, self.schema)
        report.schema_errors = schema_errors
        
        if verbose:
            if is_valid:
                print("✓ Schema validation passed")
            else:
                print(f"✗ Schema validation failed ({len(schema_errors)} error(s))")
        
        # Custom validation
        if verbose:
            print("\nRunning custom validations...")
        
        custom_errors = run_custom_validations(config)
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