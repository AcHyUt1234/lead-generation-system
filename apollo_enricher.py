"""
Apollo.io Contact Enrichment Integration - Free Tier Compatible
Updated to use endpoints accessible on Apollo's free tier

FREE TIER: 50 credits/month
"""

import requests
import os
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ApolloEnricher:
    """
    Contact enrichment using Apollo.io API
    
    Updated to use free-tier compatible endpoints:
    - /organizations/enrich for company lookup
    - /people/search for contact search
    
    Free tier: 50 email credits/month
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Apollo enrichment service
        
        Args:
            api_key: Apollo API key from Settings → API
        """
        self.api_key = api_key or os.getenv("APOLLO_API_KEY")
        self.base_url = "https://api.apollo.io/v1"
        
        if not self.api_key:
            raise ValueError("Apollo API key not found. Set APOLLO_API_KEY environment variable.")
        
        logger.info("Initialized Apollo.io enrichment service")
    
    def enrich_company(self, company_domain: str, max_contacts: int = 5) -> List[Dict]:
        """
        Find decision-makers at a company using free-tier compatible method
        
        Strategy:
        1. First get organization info to validate the company exists
        2. Then search for people at that organization
        
        Args:
            company_domain: Company domain (e.g., "techcorp.de")
            max_contacts: Maximum number of contacts to return (default: 5)
        
        Returns:
            List of contact dictionaries
        """
        logger.info(f"Enriching contacts for: {company_domain}")
        
        # Step 1: Get organization ID
        org_id = self._get_organization_id(company_domain)
        
        if not org_id:
            logger.warning(f"Could not find organization for {company_domain}")
            return self._fallback_people_search(company_domain, max_contacts)
        
        # Step 2: Search for people at this organization
        contacts = self._search_people_by_org(org_id, max_contacts)
        
        logger.info(f"Found {len(contacts)} contacts for {company_domain}")
        
        return contacts
    
    def _get_organization_id(self, domain: str) -> Optional[str]:
        """
        Get Apollo organization ID from domain using /organizations/enrich
        This endpoint is available on free tier
        """
        url = f"{self.base_url}/organizations/enrich"
        
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": self.api_key
        }
        
        payload = {
            "domain": domain
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                org = data.get('organization', {})
                org_id = org.get('id')
                
                if org_id:
                    logger.info(f"Found organization ID: {org_id} for {domain}")
                    return org_id
            else:
                logger.warning(f"Organization enrich failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Organization lookup error for {domain}: {str(e)}")
        
        return None
    
    def _search_people_by_org(self, org_id: str, max_contacts: int) -> List[Dict]:
        """
        Search for people at an organization using /people/search
        Free tier compatible
        """
        url = f"{self.base_url}/people/search"
        
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": self.api_key
        }
        
        # Target decision-maker titles
        target_titles = [
            "CEO", "Chief Executive Officer", 
            "CRO", "Chief Revenue Officer",
            "VP Sales", "Vice President Sales",
            "Head of Sales", "Sales Director",
            "Head of Business Development",
        ]
        
        payload = {
            "organization_ids": [org_id],
            "person_titles": target_titles,
            "page": 1,
            "per_page": max_contacts
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            people = data.get('people', [])
            
            # Transform to standard format
            contacts = []
            for person in people:
                contact = self._transform_apollo_contact(person)
                if contact and contact.get('email'):
                    contacts.append(contact)
            
            return contacts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"People search error: {str(e)}")
            return []
    
    def _fallback_people_search(self, domain: str, max_contacts: int) -> List[Dict]:
        """
        Fallback: Search by domain without organization ID
        """
        url = f"{self.base_url}/people/search"
        
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": self.api_key
        }
        
        # Search using domain in organization
        payload = {
            "q_organization_domains": domain,
            "page": 1,
            "per_page": max_contacts
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                people = data.get('people', [])
                
                contacts = []
                for person in people:
                    contact = self._transform_apollo_contact(person)
                    if contact and contact.get('email'):
                        contacts.append(contact)
                
                logger.info(f"Fallback search found {len(contacts)} contacts")
                return contacts
            else:
                logger.error(f"Fallback search failed: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Fallback search error: {str(e)}")
            return []
    
    def _transform_apollo_contact(self, person: Dict) -> Optional[Dict]:
        """
        Transform Apollo API response to standardized contact format
        """
        # Extract phone number
        phone_numbers = person.get('phone_numbers', [])
        phone = None
        if phone_numbers:
            for pn in phone_numbers:
                if pn.get('type') in ['mobile', 'work']:
                    phone = pn.get('sanitized_number') or pn.get('number')
                    break
            if not phone and phone_numbers:
                phone = phone_numbers[0].get('sanitized_number') or phone_numbers[0].get('number')
        
        # Determine seniority
        title = person.get('title', '').lower()
        seniority = self._determine_seniority(title)
        
        return {
            'first_name': person.get('first_name'),
            'last_name': person.get('last_name'),
            'email': person.get('email'),
            'phone': phone,
            'title': person.get('title'),
            'seniority': seniority,
            'linkedin_url': person.get('linkedin_url'),
            'source': 'apollo.io'
        }
    
    def _determine_seniority(self, title: str) -> str:
        """Determine seniority level from job title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['ceo', 'chief', 'president', 'founder']):
            return 'C-Level'
        elif any(word in title_lower for word in ['vp', 'vice president', 'evp', 'svp']):
            return 'VP'
        elif any(word in title_lower for word in ['head', 'director']):
            return 'Head/Director'
        elif any(word in title_lower for word in ['manager', 'lead']):
            return 'Manager'
        else:
            return 'Other'
    
    def get_credits_remaining(self) -> Dict:
        """
        Check remaining API credits using health endpoint
        """
        url = f"{self.base_url}/auth/health"
        
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'healthy': data.get('healthy'),
                    'is_logged_in': data.get('is_logged_in'),
                    'status': 'API key is valid'
                }
            else:
                return {'error': f'Status {response.status_code}'}
                
        except Exception as e:
            return {'error': str(e)}


# ============================================================================
# TESTING & VALIDATION
# ============================================================================

if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    # Test with environment variable
    api_key = os.getenv("APOLLO_API_KEY")
    
    if not api_key:
        print("ERROR: APOLLO_API_KEY not set")
        print("Set it with: export APOLLO_API_KEY='your-key-here'")
        sys.exit(1)
    
    enricher = ApolloEnricher(api_key=api_key)
    
    print("=" * 60)
    print("Testing Apollo API Connection")
    print("=" * 60)
    
    # Test API health
    health = enricher.get_credits_remaining()
    print(f"\nAPI Health Check:")
    print(f"  Status: {health}")
    
    if health.get('is_logged_in'):
        print("  ✅ API key is valid and working!")
    else:
        print("  ❌ API key validation failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Testing Contact Enrichment")
    print("=" * 60)
    
    # Test with a well-known company
    test_domain = "salesforce.com"
    print(f"\nSearching for contacts at: {test_domain}")
    
    contacts = enricher.enrich_company(test_domain, max_contacts=3)
    
    if contacts:
        print(f"\n✅ Found {len(contacts)} contacts:")
        for i, contact in enumerate(contacts, 1):
            print(f"\nContact {i}:")
            print(f"  Name: {contact.get('first_name')} {contact.get('last_name')}")
            print(f"  Title: {contact.get('title')}")
            print(f"  Email: {contact.get('email')}")
            print(f"  Phone: {contact.get('phone') or 'Not available'}")
            print(f"  Seniority: {contact.get('seniority')}")
    else:
        print("\n❌ No contacts found")
        print("\nThis could mean:")
        print("1. Free tier doesn't have access to this company's data")
        print("2. Rate limit reached")
        print("3. Company domain not in Apollo database")
        print("\nTry a different company domain or check Apollo dashboard")
