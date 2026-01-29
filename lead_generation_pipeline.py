"""
Lead Generation System - Starter Implementation
High-Pain Sales Roles Scraper for StepStone & LinkedIn

This is a modular starter template showing the architecture.
Each component should be expanded based on the full implementation plan.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# 1. CONFIGURATION
# ============================================================================

class Config:
    """Central configuration for the lead generation system"""
    
    # Target roles (Priority 1)
    TARGET_ROLES = [
        "Sales Engineer",
        "Solution Consultant",
        "Cyber Security Sales",
        "SAP Consultant Sales",
        "Security Consultant",
        "IT Security Consultant",
    ]
    
    # Fallback roles
    FALLBACK_ROLES = [
        "Cloud Sales",
        "Industry 4.0 Sales",
        "IoT Sales"
    ]
    
    # German translations for StepStone
    GERMAN_ROLES = [
        "Vertriebsingenieur",
        "Lösungsberater",
        "IT-Sicherheitsberater",
        "Cyber Security Vertrieb",
        "SAP Vertriebsberater",
        "Sicherheitsberater"
    ]
    
    # Filter criteria
    MIN_EMPLOYEE_COUNT = 50
    REGIONS = ["Germany", "Austria", "Switzerland", "DACH"]
    
    # Pain scoring thresholds
    MIN_PAIN_SCORE = 60
    HIGH_PAIN_THRESHOLD = 80
    
    # Enrichment settings
    MIN_CONTACTS_PER_COMPANY = 3
    CONTACT_PRIORITY = [
        "CEO", "Managing Director", "Geschäftsführer",
        "CRO", "VP Sales", "Head of Sales",
        "Sales Director", "Vertriebsleiter",
        "Head of Business Development",
        "Head of HR", "CHRO"
    ]
    
    # Output settings
    OUTPUT_DIR = "/mnt/user-data/outputs"
    CSV_ENCODING = "utf-8"


# ============================================================================
# 2. DATA MODELS
# ============================================================================

class JobListing:
    """Represents a job listing from StepStone or LinkedIn"""
    
    def __init__(self, data: Dict):
        self.title = data.get('title')
        self.company_name = data.get('company_name')
        self.company_website = data.get('company_website')
        self.location = data.get('location')
        self.posted_date = data.get('posted_date')
        self.job_url = data.get('job_url')
        self.description = data.get('description', '')
        self.source = data.get('source')  # 'StepStone' or 'LinkedIn'
        
        # LinkedIn-specific
        self.total_applications = data.get('total_applications', 0)
        self.applications_last_24h = data.get('applications_last_24h', 0)
        
        # Derived fields
        self.days_open = self._calculate_days_open()
        self.pain_score = 0  # Calculated later
        
    def _calculate_days_open(self) -> int:
        """Calculate how many days the job has been open"""
        if not self.posted_date:
            return 0
        
        if isinstance(self.posted_date, str):
            # Parse date string (adjust format as needed)
            try:
                posted = datetime.strptime(self.posted_date, "%Y-%m-%d")
            except ValueError:
                return 0
        else:
            posted = self.posted_date
            
        return (datetime.now() - posted).days
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for DataFrame"""
        return {
            'job_title': self.title,
            'company_name': self.company_name,
            'company_website': self.company_website,
            'location': self.location,
            'job_url': self.job_url,
            'source': self.source,
            'days_open': self.days_open,
            'pain_score': self.pain_score,
            'total_applications': self.total_applications,
        }


class Contact:
    """Represents a decision-maker contact"""
    
    def __init__(self, data: Dict):
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.email = data.get('email')
        self.phone = data.get('phone')
        self.role = data.get('role')
        self.seniority = data.get('seniority')  # C-Level, VP, Head, Director
        self.linkedin_url = data.get('linkedin_url')
        
    def to_dict(self, prefix: str = "") -> Dict:
        """Convert to dictionary with optional prefix for CSV columns"""
        return {
            f'{prefix}first_name': self.first_name,
            f'{prefix}last_name': self.last_name,
            f'{prefix}email': self.email,
            f'{prefix}phone': self.phone,
            f'{prefix}role': self.role,
            f'{prefix}seniority': self.seniority,
            f'{prefix}linkedin_url': self.linkedin_url,
        }
    
    def is_complete(self) -> bool:
        """Check if contact has minimum required information"""
        return bool(self.first_name and self.last_name and (self.email or self.phone))


class EnrichedLead:
    """Represents a complete lead with job, company, and contacts"""
    
    def __init__(self, job: JobListing):
        self.job = job
        self.contacts: List[Contact] = []
        self.company_data = {}
        self.job_summary = ""
        
    def add_contact(self, contact: Contact):
        """Add a contact to the lead"""
        if contact.is_complete():
            self.contacts.append(contact)
            
    def is_qualified(self) -> bool:
        """Check if lead meets minimum qualification criteria"""
        return (
            len(self.contacts) >= Config.MIN_CONTACTS_PER_COMPANY and
            self.job.pain_score >= Config.MIN_PAIN_SCORE
        )
    
    def to_csv_row(self) -> Dict:
        """Convert to flat dictionary for CSV export"""
        row = self.job.to_dict()
        row.update(self.company_data)
        row['job_summary'] = self.job_summary
        
        # Add contacts (up to 5)
        for i, contact in enumerate(self.contacts[:5], 1):
            row.update(contact.to_dict(prefix=f'contact_{i}_'))
            
        return row


# ============================================================================
# 3. SCRAPING COMPONENTS
# ============================================================================

class StepStoneScraper:
    """Scraper for StepStone job board"""
    
    def __init__(self):
        self.base_url = "https://www.stepstone.de/work"
        logger.info("Initialized StepStone scraper")
        
    def scrape_jobs(self, role_keywords: List[str], max_jobs: int = 100) -> List[JobListing]:
        """
        Scrape jobs from StepStone
        
        NOTE: This is a placeholder. Actual implementation requires:
        - Selenium/Playwright for JavaScript rendering
        - Proxy rotation for avoiding blocks
        - Robust error handling
        """
        logger.info(f"Scraping StepStone for roles: {role_keywords}")
        
        # TODO: Implement actual scraping logic
        # For now, return mock data for testing
        mock_jobs = []
        
        logger.warning("Using mock data - implement actual scraping")
        return mock_jobs
    
    def _parse_job_page(self, html: str) -> Dict:
        """Parse individual job page HTML"""
        # TODO: Implement HTML parsing
        pass


class LinkedInScraper:
    """Scraper for LinkedIn Jobs"""
    
    def __init__(self):
        self.base_url = "https://www.linkedin.com/jobs/search"
        logger.info("Initialized LinkedIn scraper")
        
    def scrape_jobs(self, role_keywords: List[str], max_jobs: int = 100) -> List[JobListing]:
        """
        Scrape jobs from LinkedIn
        
        NOTE: LinkedIn scraping is high-risk. Consider alternatives:
        - LinkedIn API (limited)
        - Third-party data providers (Bright Data, etc.)
        """
        logger.info(f"Scraping LinkedIn for roles: {role_keywords}")
        
        # TODO: Implement actual scraping or API integration
        mock_jobs = []
        
        logger.warning("Using mock data - implement actual scraping")
        return mock_jobs


# ============================================================================
# 4. FILTERING & SCORING
# ============================================================================

class JobFilter:
    """Filter and score jobs based on pain signals"""
    
    @staticmethod
    def calculate_pain_score(job: JobListing) -> int:
        """
        Calculate pain score based on multiple signals
        
        Scoring logic:
        - Base: 50 points
        - +20: Job open >30 days
        - +15: Job open >60 days
        - +10: Senior/Lead/Principal in title
        - +10: 100+ applications (LinkedIn)
        - +10: SAP/Security/Complex tech mentioned
        - +10: Enterprise/Consultative selling mentioned
        - -30: Inside sales mentioned
        - -20: SDR/BDR in description
        """
        score = 50
        
        # Days open scoring
        if job.days_open > 60:
            score += 15
        elif job.days_open > 30:
            score += 20
            
        # Seniority in title
        senior_keywords = ['senior', 'lead', 'principal', 'sr.']
        if any(kw in job.title.lower() for kw in senior_keywords):
            score += 10
            
        # Application volume (LinkedIn)
        if job.total_applications > 100:
            score += 10
            
        # Technical complexity
        tech_keywords = ['sap', 'security', 'cybersecurity', 'cloud', 'enterprise']
        description_lower = job.description.lower()
        if any(kw in description_lower for kw in tech_keywords):
            score += 10
            
        # Sales complexity
        complex_keywords = ['consultative', 'enterprise', 'b2b', 'solution']
        if any(kw in description_lower for kw in complex_keywords):
            score += 10
            
        # Negative signals
        if 'inside sales' in description_lower:
            score -= 30
        if any(kw in description_lower for kw in ['sdr', 'bdr', 'business development rep']):
            score -= 20
            
        return max(0, score)  # Don't go negative
    
    @staticmethod
    def should_exclude(job: JobListing) -> bool:
        """Check if job should be excluded based on criteria"""
        description_lower = job.description.lower()
        title_lower = job.title.lower()
        
        # Exclude junior/trainee roles
        if any(kw in title_lower for kw in ['junior', 'trainee', 'intern', 'entry']):
            return True
            
        # Exclude SDR/BDR
        if any(kw in title_lower for kw in ['sdr', 'bdr', 'business development rep']):
            return True
            
        # Exclude B2C/retail
        if any(kw in description_lower for kw in ['b2c', 'retail', 'call center', 'door-to-door']):
            return True
            
        return False
    
    def filter_and_score(self, jobs: List[JobListing]) -> List[JobListing]:
        """Filter jobs and add pain scores"""
        qualified_jobs = []
        
        for job in jobs:
            # Skip excluded jobs
            if self.should_exclude(job):
                logger.debug(f"Excluded: {job.title} at {job.company_name}")
                continue
                
            # Calculate pain score
            job.pain_score = self.calculate_pain_score(job)
            
            # Keep only high-pain jobs
            if job.pain_score >= Config.MIN_PAIN_SCORE:
                qualified_jobs.append(job)
                logger.info(f"Qualified: {job.title} (score: {job.pain_score})")
                
        logger.info(f"Filtered {len(jobs)} jobs down to {len(qualified_jobs)} qualified leads")
        return qualified_jobs


# ============================================================================
# 5. ENRICHMENT
# ============================================================================

class ContactEnricher:
    """Enrich companies with decision-maker contacts"""
    
    def __init__(self, api_key: str = None, provider: str = "leap"):
        """
        Initialize enrichment service
        
        Supported providers:
        - leap: Leap.ai
        - cognizant: Cognizant API
        - lucia: Lucia API
        - apollo: Apollo.io (backup)
        """
        self.api_key = api_key
        self.provider = provider
        logger.info(f"Initialized {provider} enrichment service")
        
    def enrich_company(self, company_domain: str) -> List[Contact]:
        """
        Find decision-makers at a company
        
        NOTE: This is a placeholder. Actual implementation requires:
        - API integration with chosen provider
        - Error handling for rate limits
        - Contact verification
        """
        logger.info(f"Enriching contacts for: {company_domain}")
        
        # TODO: Implement actual API calls
        # For now, return mock data
        mock_contacts = []
        
        logger.warning("Using mock data - implement actual enrichment")
        return mock_contacts
    
    def verify_email(self, email: str) -> bool:
        """Verify email deliverability"""
        # TODO: Integrate with Hunter.io or similar
        # Basic format check for now
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


# ============================================================================
# 6. JOB SUMMARIZATION
# ============================================================================

class JobSummarizer:
    """Generate call-ready job summaries using Claude"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize Claude summarization
        
        Uses Anthropic Claude API (3.5 Sonnet recommended)
        """
        self.api_key = api_key
        logger.info("Initialized Anthropic Claude summarization service")
        
    def generate_summary(self, job: JobListing) -> str:
        """
        Generate structured job summary for call scripts
        
        NOTE: This is a placeholder. Actual implementation requires:
        - Anthropic Claude API integration
        - Structured prompt engineering
        - Cost optimization (use Haiku for high volume, Sonnet for quality)
        """
        logger.info(f"Generating summary for: {job.title}")
        
        # TODO: Implement actual Claude API call
        # For now, return template
        summary = f"""
**Role:** {job.title}
**Company:** {job.company_name}
**Open Since:** {job.days_open} days
**Pain Signals:** {self._get_pain_signals(job)}

**Must-Have Skills:**
- [Extract from job description]

**Key Requirements:**
[2-3 sentence summary]

**Special Features:**
[Any standout details]
        """.strip()
        
        return summary
    
    def _get_pain_signals(self, job: JobListing) -> str:
        """Extract pain signals as human-readable string"""
        signals = []
        
        if job.days_open > 60:
            signals.append(f"{job.days_open}+ days open")
        if job.total_applications > 100:
            signals.append(f"{job.total_applications}+ applications")
            
        return ", ".join(signals) if signals else "Standard vacancy"


# ============================================================================
# 7. MAIN PIPELINE
# ============================================================================

class LeadGenerationPipeline:
    """Main orchestration pipeline"""
    
    def __init__(self):
        self.stepstone_scraper = StepStoneScraper()
        self.linkedin_scraper = LinkedInScraper()
        self.job_filter = JobFilter()
        self.enricher = ContactEnricher()
        self.summarizer = JobSummarizer()
        
    def run(self, target_roles: List[str] = None) -> pd.DataFrame:
        """
        Execute complete lead generation pipeline
        
        Steps:
        1. Scrape jobs from StepStone and LinkedIn
        2. Filter and score based on pain signals
        3. Enrich with decision-maker contacts
        4. Generate job summaries
        5. Export to HubSpot-ready CSV
        """
        logger.info("=" * 60)
        logger.info("Starting Lead Generation Pipeline")
        logger.info("=" * 60)
        
        if target_roles is None:
            target_roles = Config.TARGET_ROLES
            
        # Step 1: Scrape jobs
        logger.info("Step 1: Scraping job listings...")
        stepstone_jobs = self.stepstone_scraper.scrape_jobs(target_roles)
        linkedin_jobs = self.linkedin_scraper.scrape_jobs(target_roles)
        all_jobs = stepstone_jobs + linkedin_jobs
        logger.info(f"Total jobs scraped: {len(all_jobs)}")
        
        # Step 2: Filter and score
        logger.info("Step 2: Filtering and scoring jobs...")
        qualified_jobs = self.job_filter.filter_and_score(all_jobs)
        logger.info(f"Qualified jobs: {len(qualified_jobs)}")
        
        # Step 3: Enrich with contacts
        logger.info("Step 3: Enriching with decision-maker contacts...")
        enriched_leads = []
        
        for job in qualified_jobs:
            lead = EnrichedLead(job)
            
            # Extract company domain from website
            domain = self._extract_domain(job.company_website)
            
            if domain:
                # Get contacts
                contacts = self.enricher.enrich_company(domain)
                for contact in contacts:
                    lead.add_contact(contact)
                    
                # Generate summary
                lead.job_summary = self.summarizer.generate_summary(job)
                
                # Only keep leads that meet criteria
                if lead.is_qualified():
                    enriched_leads.append(lead)
                    
        logger.info(f"Enriched leads: {len(enriched_leads)}")
        
        # Step 4: Export to CSV
        logger.info("Step 4: Exporting to CSV...")
        df = self._leads_to_dataframe(enriched_leads)
        
        # Save CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"leads_export_{timestamp}.csv"
        output_path = f"{Config.OUTPUT_DIR}/{filename}"
        df.to_csv(output_path, index=False, encoding=Config.CSV_ENCODING)
        
        logger.info(f"Pipeline complete! Exported {len(df)} leads to {output_path}")
        logger.info("=" * 60)
        
        return df
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from company website URL"""
        if not url:
            return None
            
        # Simple regex extraction
        pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
        match = re.search(pattern, url)
        return match.group(1) if match else None
    
    def _leads_to_dataframe(self, leads: List[EnrichedLead]) -> pd.DataFrame:
        """Convert enriched leads to DataFrame"""
        rows = [lead.to_csv_row() for lead in leads]
        return pd.DataFrame(rows)


# ============================================================================
# 8. MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point for the lead generation system"""
    
    # Initialize pipeline
    pipeline = LeadGenerationPipeline()
    
    # Run pipeline
    try:
        results_df = pipeline.run()
        
        # Print summary statistics
        print("\n" + "=" * 60)
        print("PIPELINE SUMMARY")
        print("=" * 60)
        print(f"Total leads generated: {len(results_df)}")
        print(f"Average pain score: {results_df['pain_score'].mean():.1f}")
        print(f"High-pain leads (80+): {len(results_df[results_df['pain_score'] >= 80])}")
        print(f"Sources: {results_df['source'].value_counts().to_dict()}")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
