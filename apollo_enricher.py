"""
Apollo.io Contact Enrichment Integration
Drop-in replacement for Leap/Cognizant/Lucia in the lead generation pipeline

FREE TIER: 50 credits/month (perfect for prototype testing)
PAID TIER: $49/month for 1,200 credits (400 companies @ 3 contacts each)
"""

import requests
import os
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ApolloEnricher:
    """
    Contact enrichment using Apollo.io API
    
    Free tier: 50 email credits/month
    Paid tiers: Starting at $49/month for 1,200 credits
    
    Sign up: https://apollo.io
    API Docs: https://apolloio.github.io/apollo-api-docs/
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Apollo enrichment service
        
        Args:
            api_key: Apollo API key (get from Settings → API in Apollo dashboard)
                    Format: api_xxxxxxxxxxxxxxxxxxxxx
        """
        self.api_key = api_key or os.getenv("APOLLO_API_KEY")
        self.base_url = "https://api.apollo.io/v1"
        
        if not self.api_key:
            raise ValueError("Apollo API key not found. Set APOLLO_API_KEY environment variable.")
        
        logger.info("Initialized Apollo.io enrichment service")
    
    def enrich_company(self, company_domain: str, max_contacts: int = 5) -> List[Dict]:
        """
        Find decision-makers at a company
        
        Args:
            company_domain: Company domain (e.g., "techcorp.de")
            max_contacts: Maximum number of contacts to return (default: 5)
        
        Returns:
            List of contact dictionaries with standardized format:
            [
                {
                    'first_name': str,
                    'last_name': str,
                    'email': str,
                    'phone': str,
                    'title': str,
                    'seniority': str,  # C-Level, VP, Director, etc.
                    'linkedin_url': str
                },
                ...
            ]
        """
        logger.info(f"Enriching contacts for: {company_domain}")
        
        # Search for people at this company
        url = f"{self.base_url}/mixed_people/search"
        
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": self.api_key
        }
        
        # Target decision-maker titles
        target_titles = [
            # C-Level
            "CEO", "Chief Executive Officer", "Geschäftsführer",
            "CRO", "Chief Revenue Officer",
            "COO", "Chief Operating Officer",
            
            # VP / Head of Sales
            "VP Sales", "Vice President Sales",
            "Head of Sales", "Leiter Vertrieb",
            "Sales Director", "Vertriebsleiter",
            "Head of Business Development",
            
            # Fallback: HR
            "Head of HR", "Head of People",
            "CHRO", "Chief Human Resources Officer",
            "Talent Acquisition Lead"
        ]
        
        # Apollo search payload
        payload = {
            "organization_domains": [company_domain],
            "person_titles": target_titles,
            "page": 1,
            "per_page": max_contacts
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            people = data.get('people', [])
            
            # Transform to standardized format
            contacts = []
            for person in people:
                contact = self._transform_apollo_contact(person)
                if contact and contact.get('email'):  # Only include if has email
                    contacts.append(contact)
            
            logger.info(f"Found {len(contacts)} contacts for {company_domain}")
            
            # Log credit usage
            credits_info = response.headers.get('x-credits-remaining')
            if credits_info:
                logger.info(f"Apollo credits remaining: {credits_info}")
            
            return contacts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo API error for {company_domain}: {str(e)}")
            return []
    
    def _transform_apollo_contact(self, person: Dict) -> Optional[Dict]:
        """
        Transform Apollo API response to standardized contact format
        """
        # Extract phone number (Apollo can return multiple)
        phone_numbers = person.get('phone_numbers', [])
        phone = None
        if phone_numbers:
            # Prefer mobile, then work numbers
            for pn in phone_numbers:
                if pn.get('type') == 'mobile' or pn.get('type') == 'work':
                    phone = pn.get('sanitized_number') or pn.get('number')
                    break
            if not phone:  # If no mobile/work, take first available
                phone = phone_numbers[0].get('sanitized_number') or phone_numbers[0].get('number')
        
        # Determine seniority level
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
        """
        Determine seniority level from job title
        """
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['ceo', 'chief', 'president', 'founder', 'geschäftsführer']):
            return 'C-Level'
        elif any(word in title_lower for word in ['vp', 'vice president', 'evp', 'svp']):
            return 'VP'
        elif any(word in title_lower for word in ['head', 'director', 'leiter']):
            return 'Head/Director'
        elif any(word in title_lower for word in ['manager', 'lead']):
            return 'Manager'
        else:
            return 'Other'
    
    def verify_email(self, email: str) -> bool:
        """
        Verify email deliverability using Apollo
        
        Note: This uses additional credits. Use sparingly.
        """
        url = f"{self.base_url}/email_verifications"
        
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }
        
        payload = {"email": email}
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            # Apollo returns: 'valid', 'invalid', 'unknown', 'accept_all'
            status = result.get('status')
            
            return status in ['valid', 'accept_all']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Email verification error for {email}: {str(e)}")
            return True  # Assume valid if verification fails
    
    def get_credits_remaining(self) -> Dict:
        """
        Check remaining API credits
        
        Returns:
            {
                'credits_remaining': int,
                'credits_limit': int,
                'reset_date': str
            }
        """
        # Apollo doesn't have a dedicated credits endpoint
        # Credits info is in response headers after any API call
        # Make a minimal call to get credit info
        
        url = f"{self.base_url}/mixed_people/search"
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }
        
        # Minimal search just to get headers
        payload = {
            "organization_domains": ["example.com"],
            "per_page": 1
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            return {
                'credits_remaining': response.headers.get('x-credits-remaining'),
                'credits_limit': response.headers.get('x-credits-limit'),
                'reset_date': response.headers.get('x-credits-reset')
            }
        except:
            return {'error': 'Could not fetch credits info'}


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize enricher (uses APOLLO_API_KEY from environment)
    enricher = ApolloEnricher(api_key="api_your_key_here")
    
    print("=" * 60)
    print("EXAMPLE 1: Enrich Single Company")
    print("=" * 60)
    
    # Get contacts for a company
    contacts = enricher.enrich_company("techcrunch.com", max_contacts=3)
    
    print(f"\nFound {len(contacts)} contacts:\n")
    for i, contact in enumerate(contacts, 1):
        print(f"Contact {i}:")
        print(f"  Name: {contact['first_name']} {contact['last_name']}")
        print(f"  Title: {contact['title']}")
        print(f"  Email: {contact['email']}")
        print(f"  Phone: {contact['phone'] or 'Not available'}")
        print(f"  Seniority: {contact['seniority']}")
        print(f"  LinkedIn: {contact['linkedin_url']}")
        print()
    
    print("=" * 60)
    print("EXAMPLE 2: Check Credits Remaining")
    print("=" * 60)
    
    credits_info = enricher.get_credits_remaining()
    print(f"\nCredits remaining: {credits_info.get('credits_remaining')}")
    print(f"Credits limit: {credits_info.get('credits_limit')}")
    print(f"Reset date: {credits_info.get('reset_date')}")
    
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Integration with Pipeline")
    print("=" * 60)
    
    # How to use in your pipeline
    class EnrichedLead:
        def __init__(self, job_data):
            self.job = job_data
            self.contacts = []
            self.company_domain = self._extract_domain(job_data['company_website'])
        
        def _extract_domain(self, url):
            # Simple domain extraction
            if not url:
                return None
            import re
            match = re.search(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})', url)
            return match.group(1) if match else None
        
        def enrich(self, enricher):
            """Enrich this lead with contacts"""
            if self.company_domain:
                self.contacts = enricher.enrich_company(self.company_domain)
            return len(self.contacts) >= 3  # Is qualified?
    
    # Example job
    sample_job = {
        'title': 'Senior Sales Engineer',
        'company_name': 'TechCorp',
        'company_website': 'https://techcrunch.com',
        'pain_score': 85
    }
    
    lead = EnrichedLead(sample_job)
    is_qualified = lead.enrich(enricher)
    
    print(f"\nJob: {sample_job['title']}")
    print(f"Company: {sample_job['company_name']}")
    print(f"Contacts found: {len(lead.contacts)}")
    print(f"Qualified lead: {is_qualified}")


# ============================================================================
# FREE TIER OPTIMIZATION
# ============================================================================

class ApolloEnricherWithCache(ApolloEnricher):
    """
    Extended version with caching to save API credits
    
    Caches enrichment results to avoid duplicate lookups
    Useful when processing same companies multiple times
    """
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key)
        self.cache = {}
        self.cache_hits = 0
        self.api_calls = 0
    
    def enrich_company(self, company_domain: str, max_contacts: int = 5) -> List[Dict]:
        """
        Enrich with caching - saves credits for repeated lookups
        """
        # Check cache first
        cache_key = f"{company_domain}:{max_contacts}"
        
        if cache_key in self.cache:
            self.cache_hits += 1
            logger.info(f"Cache hit for {company_domain} (saved 1 credit)")
            return self.cache[cache_key]
        
        # Call API
        self.api_calls += 1
        contacts = super().enrich_company(company_domain, max_contacts)
        
        # Store in cache
        self.cache[cache_key] = contacts
        
        return contacts
    
    def get_stats(self):
        """Get cache statistics"""
        return {
            'cache_hits': self.cache_hits,
            'api_calls': self.api_calls,
            'credits_saved': self.cache_hits,
            'cache_size': len(self.cache)
        }


# ============================================================================
# BATCH PROCESSING FOR FREE TIER
# ============================================================================

def enrich_batch_with_free_tier(companies: List[str], enricher: ApolloEnricher, 
                                 free_tier_limit: int = 50):
    """
    Process companies within free tier limits
    
    Args:
        companies: List of company domains
        enricher: ApolloEnricher instance
        free_tier_limit: Max credits to use (default: 50 for free tier)
    
    Returns:
        List of enriched results
    """
    results = []
    credits_used = 0
    
    for i, company_domain in enumerate(companies):
        # Stop if we hit free tier limit
        if credits_used >= free_tier_limit:
            logger.warning(f"Reached free tier limit ({free_tier_limit} credits). "
                         f"Processed {i} companies. Remaining: {len(companies) - i}")
            break
        
        # Enrich company
        contacts = enricher.enrich_company(company_domain, max_contacts=3)
        
        if contacts:
            results.append({
                'company_domain': company_domain,
                'contacts': contacts,
                'contact_count': len(contacts)
            })
            credits_used += 1  # Apollo charges 1 credit per company search
        
        # Show progress
        if (i + 1) % 10 == 0:
            logger.info(f"Processed {i + 1}/{len(companies)} companies. "
                       f"Credits used: {credits_used}/{free_tier_limit}")
    
    logger.info(f"Batch complete: {len(results)} companies enriched, "
               f"{credits_used} credits used")
    
    return results


# ============================================================================
# INTEGRATION GUIDE
# ============================================================================

"""
HOW TO INTEGRATE INTO YOUR PIPELINE:

1. Install Apollo dependency:
   pip install requests

2. Get API key:
   - Sign up at https://apollo.io
   - Go to Settings → API
   - Create new key
   - Copy key (format: api_xxxxxxxxxxxxx)

3. Add to environment:
   export APOLLO_API_KEY="api_xxxxxxxxxxxxx"
   
   Or add to .env file:
   APOLLO_API_KEY=api_xxxxxxxxxxxxx

4. Replace in lead_generation_pipeline.py:

   # OLD:
   from enrichment.contact_enricher import ContactEnricher
   enricher = ContactEnricher(api_key=LEAP_API_KEY, provider="leap")
   
   # NEW:
   from apollo_enricher import ApolloEnricher  # This file
   enricher = ApolloEnricher()  # Auto-loads from environment

5. Use in pipeline:
   
   contacts = enricher.enrich_company(company_domain)
   
   # Same interface as before!

6. Monitor usage:
   
   credits_info = enricher.get_credits_remaining()
   print(f"Credits left: {credits_info['credits_remaining']}")

COST OPTIMIZATION:

- Free tier: 50 credits/month (50 companies)
- Each company search = 1 credit
- Use ApolloEnricherWithCache to save credits
- Process in batches with batch size = free tier limit

For 100 companies/month:
- Use 50 free credits
- Upgrade to Basic ($49) for remaining 50
- Or split across 2 accounts (not recommended)
"""
