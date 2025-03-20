from dataclasses import dataclass
from typing import Optional

@dataclass
class ContactInfo:
    """Data class for customer contact information."""
    full_name: str
    email: str
    phone_number: str
    # Fields for representatives
    name: Optional[str] = None
    phone: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    availability: Optional[str] = None 