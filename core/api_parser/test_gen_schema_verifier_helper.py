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
