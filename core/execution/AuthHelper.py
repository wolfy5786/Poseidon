import os
from typing import Dict, Any
from abc import ABC, abstractmethod
import CredentialSource as cr


# ==============================================================================
# BASE CLASS
# ==============================================================================

class AuthHelper(ABC):
    """Abstract base class for Authentication."""
    
    def __init__(self):
        self.credentialSource = cr.CredentialSource()
