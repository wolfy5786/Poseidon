import json
import sys
from jsonschema import validate, ValidationError
from datetime import datetime
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