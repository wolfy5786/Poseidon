import os
from typing import Dict, Any
from abc import ABC, abstractmethod


# ==============================================================================
# BASE CLASS
# ==============================================================================

class CredentialSource(ABC):
    """Abstract base class for credential sources."""
    
    @abstractmethod
    def fetch(self, config: Dict[str, Any]) -> str:
        """Fetch credential from the source."""
        pass
