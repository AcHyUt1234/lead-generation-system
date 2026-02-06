"""
Mock Contact Enricher for Testing
Generates realistic fake contact data when API access is not available

This is perfect for:
- Testing the pipeline end-to-end
- Demonstrating the system to stakeholders
- Getting a working CSV immediately

Once you have API access or scrape real data, you can replace this.
"""

import logging
from typing import List, Dict, Optional
import random

logger = logging.getLogger(__name__)


class ApolloEnricher:
    """
    Mock enricher that generates realistic fake contacts
    
    This allows you to:
    1. Test the entire pipeline
    2. Get a working CSV output
    3. Validate the HubSpot import process
    4. Demo the system
    
    Replace with real API when available.
    """
    
    # Realistic fake names for different roles
    FIRST_NAMES = [
        "Michael", "Sarah", "David", "Jennifer", "Robert", "Lisa",
        "James", "Maria", "John", "Patricia", "William", "Linda",
        "Richard", "Barbara", "Thomas", "Elizabeth", "Charles", "Susan",
        "Daniel", "Jessica", "Matthew", "Karen", "Christopher", "Nancy"
    ]
    
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
        "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
        "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson",
        "Martin", "Lee", "Thompson", "White", "Harris", "Sanchez"
    ]
    
    # Job titles by seniority
    CEO_TITLES = ["CEO", "Chief Executive Officer", "President", "Managing Director"]
    CRO_TITLES = ["CRO", "Chief Revenue Officer", "VP Sales", "Vice President of Sales"]
    DIRECTOR_TITLES = ["Sales Director", "Director of Sales", "Head of Sales", "Head of Business Development"]
    MANAGER_TITLES = ["Sales Manager", "Business Development Manager", "Regional Sales Manager"]
    
    def __init__(self, api_key: str = None):
        """Initialize mock enricher"""
        self.api_key = api_key
        logger.info("Initialized MOCK Apollo.io enrichment service (using fake data for testing)")
        logger.warning("⚠️ Using mock data - replace with real API when available")
    
    def enrich_company(self, company_domain: str, max_contacts: int = 5) -> List[Dict]:
        """
        Generate realistic fake contacts for a company
        
        Args:
            company_domain: Company domain (e.g., "salesforce.com")
            max_contacts: Number of contacts to generate
        
        Returns:
            List of realistic fake contact dictionaries
        """
        logger.info(f"Generating mock contacts for: {company_domain}")
        
        # Extract company name from domain
        company_name = self._domain_to_company_name(company_domain)
        
        # Generate realistic number of contacts (3-5)
        num_contacts = min(max_contacts, random.randint(3, 5))
        
        contacts = []
        used_names = set()  # Avoid duplicate names
        
        # Always include CEO
        contacts.append(self._generate_contact(company_domain, "C-Level", used_names))
        
        # Add CRO/VP Sales
        if num_contacts >= 2:
            contacts.append(self._generate_contact(company_domain, "VP", used_names))
        
        # Add Directors
        if num_contacts >= 3:
            contacts.append(self._generate_contact(company_domain, "Head/Director", used_names))
        
        # Add more if needed
        while len(contacts) < num_contacts:
            seniority = random.choice(["Head/Director", "Manager"])
            contacts.append(self._generate_contact(company_domain, seniority, used_names))
        
        logger.info(f"Generated {len(contacts)} mock contacts for {company_domain}")
        
        return contacts
    
    def _generate_contact(self, domain: str, seniority: str, used_names: set) -> Dict:
        """Generate a single realistic fake contact"""
        
        # Generate unique name
        while True:
            first_name = random.choice(self.FIRST_NAMES)
            last_name = random.choice(self.LAST_NAMES)
            full_name = f"{first_name}{last_name}"
            if full_name not in used_names:
                used_names.add(full_name)
                break
        
        # Generate title based on seniority
        if seniority == "C-Level":
            title = random.choice(self.CEO_TITLES)
        elif seniority == "VP":
            title = random.choice(self.CRO_TITLES)
        elif seniority == "Head/Director":
            title = random.choice(self.DIRECTOR_TITLES)
        else:
            title = random.choice(self.MANAGER_TITLES)
        
        # Generate email (realistic format)
        email_format = random.choice([
            f"{first_name.lower()}.{last_name.lower()}@{domain}",
            f"{first_name[0].lower()}{last_name.lower()}@{domain}",
            f"{first_name.lower()}{last_name[0].lower()}@{domain}"
        ])
        
        # Generate phone (realistic US format)
        area_code = random.randint(200, 999)
        exchange = random.randint(200, 999)
        number = random.randint(1000, 9999)
        phone = f"+1-{area_code}-{exchange}-{number}"
        
        # Generate LinkedIn URL
        linkedin = f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}-{random.randint(100,999)}"
        
        return {
            'first_name': first_name,
            'last_name': last_name,
            'email': email_format,
            'phone': phone,
            'title': title,
            'seniority': seniority,
            'linkedin_url': linkedin,
            'source': 'mock_data'
        }
    
    def _domain_to_company_name(self, domain: str) -> str:
        """Extract company name from domain"""
        # Remove common TLDs
        name = domain.replace('.com', '').replace('.de', '').replace('.io', '')
        # Capitalize
        return name.capitalize()
    
    def get_credits_remaining(self) -> Dict:
        """Mock credits check"""
        return {
            'healthy': True,
            'is_logged_in': True,
            'status': 'Mock enricher - unlimited fake contacts'
        }


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    enricher = ApolloEnricher()
    
    print("=" * 60)
    print("Testing Mock Enricher")
    print("=" * 60)
    
    # Test with salesforce.com
    print("\nGenerating contacts for: salesforce.com")
    contacts = enricher.enrich_company("salesforce.com", max_contacts=5)
    
    print(f"\n✅ Generated {len(contacts)} contacts:\n")
    for i, contact in enumerate(contacts, 1):
        print(f"Contact {i}:")
        print(f"  Name: {contact['first_name']} {contact['last_name']}")
        print(f"  Title: {contact['title']}")
        print(f"  Email: {contact['email']}")
        print(f"  Phone: {contact['phone']}")
        print(f"  Seniority: {contact['seniority']}")
        print()
    
    print("=" * 60)
    print("Mock enricher working perfectly!")
    print("=" * 60)
