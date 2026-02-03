"""
Lead Generation System - Production Ready Implementation
High-Pain Sales Roles Scraper with Apollo.io Enrichment

This version includes:
- Apollo.io contact enrichment integration
- Claude API for job summarization
- Mock data for initial testing (replace with real scrapers)
- HubSpot-ready CSV export
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# IMPORT APOLLO ENRICHER
# ============================================================================

try:
    from apollo_enricher import ApolloEnricher
except ImportError:
    logger.error("apollo_enricher.py not found. Make sure it's in the same directory.")
    sys.exit(1)


# ============================================================================
# 1. CONFIGURATION
# ============================================================================

class Config:
    """Central configuration for the lead generation system"""
    
    # API Keys (loaded from environment variables)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
    HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
    
    # Target roles (Priority 1)
    TARGET_ROLES = [
        "Sales Engineer",
        "Solution Consultant",
        "Cyber Security Sales",
        "SAP Consultant Sales",
        "Security Consultant",
        "IT Security Consultant",
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
    
    # Pain scoring thresholds
    MIN_PAIN_SCORE = 60
    HIGH_PAIN_THRESHOLD = 80
    
    # Enrichment settings
    MIN_CONTACTS_PER_COMPANY = 3
    
    # Output settings
    OUTPUT_DIR = "outputs"  # Changed for GitHub Actions compatibility
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
        self.source = data.get('source', 'Mock')
        
        # Derived fields
        self.days_open = self._calculate_days_open()
        self.pain_score = 0  # Calculated later
        
    def _calculate_days_open(self) -> int:
        """Calculate how many days the job has been open"""
        if not self.posted_date:
            return 0
        
        if isinstance(self.posted_date, str):
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
        }


class Contact:
    """Represents a decision-maker contact"""
    
    def __init__(self, data: Dict):
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.email = data.get('email')
        self.phone = data.get('phone')
        self.title = data.get('title')
        self.seniority = data.get('seniority')
        self.linkedin_url = data.get('linkedin_url')
        
    def to_dict(self, prefix: str = "") -> Dict:
        """Convert to dictionary with optional prefix for CSV columns"""
        return {
            f'{prefix}first_name': self.first_name,
            f'{prefix}last_name': self.last_name,
            f'{prefix}email': self.email,
            f'{prefix}phone': self.phone,
            f'{prefix}title': self.title,
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
        self.company_domain = self._extract_domain(job.company_website)
        self.job_summary = ""
        
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        if not url:
            return None
        pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
        match = re.search(pattern, url)
        return match.group(1) if match else None
        
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
        row['company_domain'] = self.company_domain
        row['job_summary'] = self.job_summary
        
        # Add contacts (up to 5)
        for i, contact in enumerate(self.contacts[:5], 1):
            row.update(contact.to_dict(prefix=f'contact_{i}_'))
            
        return row


# ============================================================================
# 3. MOCK DATA FOR TESTING (Replace with real scrapers later)
# ============================================================================

def generate_mock_jobs() -> List[JobListing]:
    """
    Generate mock job listings for testing
    Replace this with real StepStone/LinkedIn scrapers
    """
    logger.info("Generating mock job data for testing...")
    
    mock_data = [
        {
            'title': 'Senior Sales Engineer (IT)',
            'company_name': 'Salesforce',
            'company_website': 'https://salesforce.com',
            'location': 'Munich, Germany',
            'posted_date': (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d"),
            'job_url': 'https://salesforce.com/careers/job123',
            'description': '''We are seeking an experienced Senior Sales Engineer to join our growing team.
            
            Requirements:
            - 5+ years in technical sales, preferably SaaS/Cloud
            - Deep understanding of API integrations and enterprise architecture
            - Experience with Fortune 500 clients
            - Fluent in German and English
            - Strong presentation and communication skills
            
            Responsibilities:
            - Lead technical pre-sales discussions
            - Create POCs and demos for enterprise clients
            - Work closely with product and sales teams
            - Support complex deals with technical expertise''',
            'source': 'Mock (StepStone)'
        },
        {
            'title': 'Cyber Security Sales Consultant',
            'company_name': 'Palo Alto Networks',
            'company_website': 'https://paloaltonetworks.com',
            'location': 'Frankfurt, Germany',
            'posted_date': (datetime.now() - timedelta(days=32)).strftime("%Y-%m-%d"),
            'job_url': 'https://paloaltonetworks.com/careers/job456',
            'description': '''Join our cybersecurity team as a Sales Consultant.
            
            Requirements:
            - 3+ years in cybersecurity sales
            - Understanding of network security, firewalls, threat detection
            - Experience selling to enterprise clients
            - German language required
            
            We offer competitive compensation and professional development.''',
            'source': 'Mock (LinkedIn)'
        },
        {
            'title': 'SAP Sales Consultant',
            'company_name': 'SAP',
            'company_website': 'https://sap.com',
            'location': 'Berlin, Germany',
            'posted_date': (datetime.now() - timedelta(days=67)).strftime("%Y-%m-%d"),
            'job_url': 'https://sap.com/careers/job789',
            'description': '''Looking for an experienced SAP Sales Consultant.
            
            Requirements:
            - Deep SAP product knowledge (S/4HANA, ERP, Cloud)
            - 5+ years enterprise software sales
            - Experience with large deals (€1M+)
            - Consultative selling approach
            - Fluent German and English
            
            This role requires travel across DACH region.''',
            'source': 'Mock (StepStone)'
        },
    ]
    
    jobs = [JobListing(data) for data in mock_data]
    logger.info(f"Generated {len(jobs)} mock jobs")
    return jobs


# ============================================================================
# 4. PAIN SCORING
# ============================================================================

class JobFilter:
    """Filter and score jobs based on pain signals"""
    
    @staticmethod
    def calculate_pain_score(job: JobListing) -> int:
        """Calculate pain score based on multiple signals"""
        score = 50
        
        # Days open scoring
        if job.days_open > 60:
            score += 15
        elif job.days_open > 30:
            score += 20
            
        # Seniority in title
        senior_keywords = ['senior', 'lead', 'principal', 'sr.', 'sr ']
        if any(kw in job.title.lower() for kw in senior_keywords):
            score += 10
            
        # Technical complexity
        tech_keywords = ['sap', 'security', 'cybersecurity', 'cyber security', 'cloud', 'enterprise']
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
            
        return max(0, score)
    
    @staticmethod
    def should_exclude(job: JobListing) -> bool:
        """Check if job should be excluded"""
        title_lower = job.title.lower()
        
        # Exclude junior/trainee roles
        if any(kw in title_lower for kw in ['junior', 'trainee', 'intern', 'entry']):
            return True
            
        # Exclude SDR/BDR
        if any(kw in title_lower for kw in ['sdr', 'bdr']):
            return True
            
        return False
    
    def filter_and_score(self, jobs: List[JobListing]) -> List[JobListing]:
        """Filter jobs and add pain scores"""
        qualified_jobs = []
        
        for job in jobs:
            if self.should_exclude(job):
                logger.debug(f"Excluded: {job.title} at {job.company_name}")
                continue
                
            job.pain_score = self.calculate_pain_score(job)
            
            if job.pain_score >= Config.MIN_PAIN_SCORE:
                qualified_jobs.append(job)
                logger.info(f"Qualified: {job.title} (score: {job.pain_score})")
                
        logger.info(f"Filtered {len(jobs)} jobs down to {len(qualified_jobs)} qualified leads")
        return qualified_jobs


# ============================================================================
# 5. JOB SUMMARIZATION WITH CLAUDE
# ============================================================================

class JobSummarizer:
    """Generate call-ready job summaries using Claude"""
    
    def __init__(self):
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            self.has_api = True
            logger.info("Initialized Claude API for summarization")
        except Exception as e:
            logger.warning(f"Claude API not available: {e}. Will use template summaries.")
            self.has_api = False
    
    def generate_summary(self, job: JobListing) -> str:
        """Generate structured job summary"""
        if self.has_api:
            return self._generate_with_claude(job)
        else:
            return self._generate_template(job)
    
    def _generate_with_claude(self, job: JobListing) -> str:
        """Generate summary using Claude API"""
        prompt = f"""You are helping a recruitment agency create concise summaries for sales calls.

Given this job vacancy:
- Title: {job.title}
- Company: {job.company_name}
- Posted: {job.days_open} days ago
- Description: {job.description[:2000]}

Create a structured summary in this exact format:

**Must-Have Skills:**
- [Skill 1]
- [Skill 2]
- [Skill 3]

**Key Requirements:**
[2-3 sentences describing the role expectations]

**Special Features:**
[Any standout details like remote work, equity, unique perks, or "None noted"]

Keep it concise and focused on what a recruiter needs for an initial sales call."""

        try:
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",  # Cost-effective model
                max_tokens=512,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return self._generate_template(job)
    
    def _generate_template(self, job: JobListing) -> str:
        """Fallback template-based summary"""
        return f"""**Must-Have Skills:**
- See full job description
- {job.days_open}+ days open position
- {job.location} location

**Key Requirements:**
{job.title} position at {job.company_name}. Review full posting for detailed requirements.

**Special Features:**
Manual review recommended for this vacancy."""


# ============================================================================
# 6. MAIN PIPELINE
# ============================================================================

class LeadGenerationPipeline:
    """Main orchestration pipeline"""
    
    def __init__(self):
        self.job_filter = JobFilter()
        self.enricher = ApolloEnricher(api_key=Config.APOLLO_API_KEY)
        self.summarizer = JobSummarizer()
        
        # Create output directory
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        
    def run(self) -> pd.DataFrame:
        """Execute complete lead generation pipeline"""
        logger.info("=" * 60)
        logger.info("Starting Lead Generation Pipeline")
        logger.info("=" * 60)
        
        # Step 1: Get jobs (using mock data for now)
        logger.info("Step 1: Fetching job listings...")
        all_jobs = generate_mock_jobs()
        logger.info(f"Total jobs fetched: {len(all_jobs)}")
        
        # Step 2: Filter and score
        logger.info("Step 2: Filtering and scoring jobs...")
        qualified_jobs = self.job_filter.filter_and_score(all_jobs)
        logger.info(f"Qualified jobs: {len(qualified_jobs)}")
        
        if not qualified_jobs:
            logger.warning("No qualified jobs found. Exiting.")
            return pd.DataFrame()
        
        # Step 3: Enrich with contacts
        logger.info("Step 3: Enriching with decision-maker contacts...")
        enriched_leads = []
        
        for job in qualified_jobs:
            lead = EnrichedLead(job)
            
            if lead.company_domain:
                try:
                    # Get contacts from Apollo
                    contact_data = self.enricher.enrich_company(
                        lead.company_domain,
                        max_contacts=5
                    )
                    
                    for contact_dict in contact_data:
                        contact = Contact(contact_dict)
                        lead.add_contact(contact)
                    
                    logger.info(f"Found {len(lead.contacts)} contacts for {job.company_name}")
                    
                except Exception as e:
                    logger.error(f"Enrichment failed for {job.company_name}: {e}")
            
            # Generate summary
            try:
                lead.job_summary = self.summarizer.generate_summary(job)
            except Exception as e:
                logger.error(f"Summary generation failed for {job.title}: {e}")
                lead.job_summary = "Summary generation failed"
            
            # Only keep leads that meet criteria
            if lead.is_qualified():
                enriched_leads.append(lead)
                logger.info(f"✓ Qualified lead: {job.company_name} ({len(lead.contacts)} contacts)")
            else:
                logger.info(f"✗ Not qualified: {job.company_name} (only {len(lead.contacts)} contacts)")
                
        logger.info(f"Total enriched leads: {len(enriched_leads)}")
        
        # Step 4: Export to CSV
        logger.info("Step 4: Exporting to CSV...")
        df = self._leads_to_dataframe(enriched_leads)
        
        if len(df) == 0:
            logger.warning("No leads to export!")
            return df
        
        # Save CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"leads_export_{timestamp}.csv"
        output_path = os.path.join(Config.OUTPUT_DIR, filename)
        df.to_csv(output_path, index=False, encoding=Config.CSV_ENCODING)
        
        logger.info(f"✓ Pipeline complete! Exported {len(df)} leads to {output_path}")
        logger.info("=" * 60)
        
        # Print summary
        self._print_summary(df)
        
        return df
    
    def _leads_to_dataframe(self, leads: List[EnrichedLead]) -> pd.DataFrame:
        """Convert enriched leads to DataFrame"""
        rows = [lead.to_csv_row() for lead in leads]
        return pd.DataFrame(rows)
    
    def _print_summary(self, df: pd.DataFrame):
        """Print summary statistics"""
        print("\n" + "=" * 60)
        print("PIPELINE SUMMARY")
        print("=" * 60)
        print(f"Total leads generated: {len(df)}")
        if len(df) > 0:
            print(f"Average pain score: {df['pain_score'].mean():.1f}")
            print(f"High-pain leads (80+): {len(df[df['pain_score'] >= 80])}")
            print(f"Sources: {df['source'].value_counts().to_dict()}")
        print("=" * 60 + "\n")


# ============================================================================
# 7. MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point"""
    
    # Check for required API keys
    required_keys = {
        'APOLLO_API_KEY': Config.APOLLO_API_KEY,
    }
    
    missing_keys = [key for key, value in required_keys.items() if not value]
    
    if missing_keys:
        logger.error(f"Missing required API keys: {', '.join(missing_keys)}")
        logger.error("Please set these as environment variables or GitHub Secrets")
        sys.exit(1)
    
    logger.info("All required API keys found ✓")
    
    # Initialize and run pipeline
    try:
        pipeline = LeadGenerationPipeline()
        results_df = pipeline.run()
        
        if len(results_df) > 0:
            logger.info("✓ SUCCESS: Pipeline completed successfully!")
            logger.info(f"✓ CSV file created in {Config.OUTPUT_DIR}/ directory")
        else:
            logger.warning("⚠ WARNING: Pipeline completed but no leads qualified")
        
    except Exception as e:
        logger.error(f"✗ Pipeline failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()