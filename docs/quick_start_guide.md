# Quick Start Guide - Lead Generation System
## Implementation Checklist & Action Plan

---

## Phase 1: Test Delivery (This Week - Days 1-5)

### Day 1: Setup & Planning

**Tasks:**
- [ ] Review implementation plan with Zeynel
- [ ] Confirm target role keywords and priorities
- [ ] Select enrichment API provider (Leap/Cognizant/Lucia)
- [ ] Get API credentials for enrichment service
- [ ] Set up HubSpot sandbox for testing
- [ ] Create project repository

**Deliverables:**
- Approved filter criteria
- API access confirmed
- Development environment ready

---

### Day 2-3: Build Core Scraper

**StepStone Scraper Implementation:**

```python
# Priority tasks:
1. Set up Selenium/Playwright with German proxies
2. Navigate to StepStone job search with filters
3. Extract job listing URLs
4. Parse individual job pages for:
   - Title, company, location
   - Job description (full text)
   - Posted date
   - Company website
5. Handle pagination
6. Save raw data to CSV/database

# Sample scraping code structure:
from selenium import webdriver
from selenium.webdriver.common.by import By

def scrape_stepstone():
    driver = setup_driver_with_proxy()
    
    # Build search URL
    search_url = build_search_url(
        keywords=["Sales Engineer", "IT"],
        location="Deutschland",
        radius=100
    )
    
    # Get job listings
    driver.get(search_url)
    job_cards = driver.find_elements(By.CSS_SELECTOR, ".job-listing-card")
    
    for card in job_cards:
        job_url = card.find_element(By.TAG_NAME, "a").get_attribute("href")
        jobs.append(scrape_job_page(job_url))
    
    return jobs
```

**Testing:**
- [ ] Scrape 50 test jobs from StepStone
- [ ] Verify data quality (no missing fields)
- [ ] Check for anti-scraping blocks
- [ ] Validate German character encoding

---

### Day 3-4: Implement Filtering & Enrichment

**Filtering Implementation:**

```python
# Apply filter logic
def filter_jobs(jobs):
    qualified = []
    
    for job in jobs:
        # Exclusion checks
        if is_junior_role(job.title):
            continue
        if is_sdr_bdr(job.description):
            continue
            
        # Pain score calculation
        score = calculate_pain_score(job)
        
        if score >= 60:
            job.pain_score = score
            qualified.append(job)
    
    return qualified

# Priority scoring factors:
# 1. Days open (check posted_date)
# 2. Seniority keywords in title
# 3. Technical complexity keywords
# 4. B2B/Enterprise indicators
```

**Enrichment Integration:**

```python
# Choose your provider and get API key
# Option A: Leap.ai
import requests

def enrich_with_leap(company_domain):
    response = requests.post(
        "https://api.leap.ai/v1/contacts/search",
        headers={"Authorization": f"Bearer {LEAP_API_KEY}"},
        json={
            "domain": company_domain,
            "titles": ["CEO", "CRO", "VP Sales", "Head of Sales"],
            "limit": 5
        }
    )
    return response.json()['contacts']

# Option B: Apollo.io
# Option C: Cognizant/Lucia (get docs from provider)
```

**Testing:**
- [ ] Filter 50 scraped jobs
- [ ] Verify filter accuracy (manual spot-check)
- [ ] Test enrichment API with 5 sample companies
- [ ] Confirm contact data quality

---

### Day 5: Generate Test Dataset

**Job Summarization:**

```python
# Option 1: Simple template-based (fast, cheap)
def generate_summary_template(job):
    summary = f"""
    **Role:** {job.title}
    **Company:** {job.company_name}
    **Open Since:** {job.days_open} days
    
    **Must-Have Skills:**
    {extract_skills(job.description)}
    
    **Key Requirements:**
    {extract_requirements(job.description)}
    """
    return summary

# Option 2: LLM-based (better quality)
from anthropic import Anthropic

client = Anthropic(api_key=ANTHROPIC_API_KEY)

def generate_summary_llm(job):
    prompt = f"""Create a concise summary for a sales call about this job vacancy:
    
    Title: {job.title}
    Company: {job.company_name}
    Description: {job.description[:1000]}
    
    Format the output as:
    - Must-Have Skills (3-5 bullets)
    - Key Requirements (2-3 sentences)
    - Special Features (any standout details)
    """
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # or claude-3-5-haiku-20241022 for lower cost
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text
```

**CSV Export:**

```python
import pandas as pd

def export_to_csv(enriched_leads, filename):
    rows = []
    
    for lead in enriched_leads:
        row = {
            # Company level
            'company_name': lead.job.company_name,
            'company_website': lead.job.company_website,
            'company_domain': lead.company_domain,
            
            # Job level
            'job_title': lead.job.title,
            'job_url': lead.job.job_url,
            'source': lead.job.source,
            'days_open': lead.job.days_open,
            'pain_score': lead.job.pain_score,
            'job_summary': lead.job_summary,
            
            # Contacts (flattened)
            'contact_1_first_name': lead.contacts[0].first_name,
            'contact_1_last_name': lead.contacts[0].last_name,
            'contact_1_email': lead.contacts[0].email,
            'contact_1_phone': lead.contacts[0].phone,
            # ... repeat for contact_2, contact_3
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False, encoding='utf-8')
    return df
```

**Final Tasks:**
- [ ] Run complete pipeline on 20 companies
- [ ] Generate CSV with all required columns
- [ ] Manual QA: verify 100% of test data
- [ ] Share with Zeynel for review
- [ ] Incorporate feedback

**Test Deliverable:**
- CSV with 10-20 companies
- 30-60 contacts (3+ per company)
- Job summaries for each
- Pain scores calculated
- Ready for HubSpot import

---

## Phase 2: Full Automation (Week 2-3)

### Week 2: Production Pipeline

**Tasks:**
- [ ] Expand to 100+ companies per run
- [ ] Add LinkedIn scraper (secondary source)
- [ ] Implement duplicate detection
- [ ] Build error handling & retry logic
- [ ] Set up logging and monitoring
- [ ] Create admin dashboard (simple Flask app)

**LinkedIn Scraper:**

```python
# Option A: Use third-party data provider (recommended)
# - Bright Data LinkedIn Jobs dataset
# - Safer, more reliable

# Option B: Careful scraping with rate limiting
def scrape_linkedin_carefully():
    # Use residential proxies
    # 1-2 second delays between requests
    # Rotate accounts
    # Monitor for blocks
    pass

# Option C: LinkedIn API (limited data)
# - Requires partnership application
# - Very restricted access
```

**Duplicate Detection:**

```python
import hashlib

def check_duplicates(new_leads, previous_exports):
    """
    Check against previous week's exports
    Uses company domain + job title as unique key
    """
    seen = set()
    
    # Load previous exports
    for export in previous_exports:
        df = pd.read_csv(export)
        for _, row in df.iterrows():
            key = f"{row['company_domain']}_{row['job_title']}"
            seen.add(hashlib.md5(key.encode()).hexdigest())
    
    # Filter new leads
    unique_leads = []
    for lead in new_leads:
        key = f"{lead.company_domain}_{lead.job.title}"
        hash_key = hashlib.md5(key.encode()).hexdigest()
        
        if hash_key not in seen:
            unique_leads.append(lead)
    
    return unique_leads
```

---

### Week 3: Deploy to Production

**Infrastructure Setup:**

```bash
# 1. Provision server
# AWS EC2 t3.medium (4GB RAM) or DigitalOcean Droplet

# 2. Install dependencies
sudo apt update
sudo apt install python3.10 python3-pip postgresql redis-server

# 3. Clone repository
git clone <repo-url>
cd lead-generation

# 4. Install Python packages
pip install -r requirements.txt

# 5. Set up environment variables
cat > .env << EOF
STEPSTONE_PROXY_URL=...
LEAP_API_KEY=...
OPENAI_API_KEY=...
HUBSPOT_API_KEY=...
DATABASE_URL=postgresql://...
EOF

# 6. Set up database
python manage.py init_db

# 7. Test scraping
python lead_generation_pipeline.py --test

# 8. Set up cron job for daily runs
crontab -e
# Add: 0 3 * * * cd /path/to/project && python lead_generation_pipeline.py
```

**Monitoring Setup:**

```python
# Use loguru for structured logging
from loguru import logger

logger.add(
    "logs/pipeline_{time}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO"
)

# Add Slack/email alerts for failures
def notify_on_failure(error):
    requests.post(
        SLACK_WEBHOOK_URL,
        json={"text": f"Pipeline failed: {error}"}
    )
```

**Admin Dashboard (Optional):**

```python
# Simple Flask app to monitor pipeline
from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def dashboard():
    # Show recent runs
    runs = get_recent_pipeline_runs()
    stats = {
        'total_leads_this_week': len(get_current_week_leads()),
        'avg_pain_score': calculate_avg_pain_score(),
        'top_companies': get_top_companies_by_score()
    }
    return render_template('dashboard.html', runs=runs, stats=stats)

# Run with: flask run --host=0.0.0.0 --port=5000
```

---

## Phase 3: HubSpot Integration (Week 4+)

### HubSpot Setup

**1. Create Custom Objects:**

```python
from hubspot import HubSpot
from hubspot.crm.objects import PublicObjectSearchRequest

api_client = HubSpot(access_token=HUBSPOT_API_KEY)

# Create "Job Opportunity" custom object
# (Do this in HubSpot UI first)

# Import companies
def import_to_hubspot(leads_df):
    for _, row in leads_df.iterrows():
        # Create/update company
        company = api_client.crm.companies.basic_api.create(
            simple_public_object_input={
                "properties": {
                    "name": row['company_name'],
                    "domain": row['company_domain'],
                    "website": row['company_website'],
                    "numberofemployees": row['company_employee_count']
                }
            }
        )
        
        # Create contacts
        for i in range(1, 4):
            if pd.notna(row.get(f'contact_{i}_email')):
                contact = api_client.crm.contacts.basic_api.create(
                    simple_public_object_input={
                        "properties": {
                            "firstname": row[f'contact_{i}_first_name'],
                            "lastname": row[f'contact_{i}_last_name'],
                            "email": row[f'contact_{i}_email'],
                            "phone": row[f'contact_{i}_phone'],
                            "jobtitle": row[f'contact_{i}_role']
                        }
                    }
                )
                
                # Associate contact with company
                api_client.crm.associations.batch_api.create(
                    from_object_type="contacts",
                    to_object_type="companies",
                    batch_input_public_association={
                        "inputs": [{
                            "from": {"id": contact.id},
                            "to": {"id": company.id},
                            "type": "contact_to_company"
                        }]
                    }
                )
```

**2. Create Workflows:**

```yaml
# Workflow 1: Auto-assign leads
Trigger: New Job Opportunity created
Actions:
  - Assign to sales rep (round-robin)
  - Send internal notification
  - Create task: "Initial outreach"

# Workflow 2: No contact made
Trigger: Deal marked "No contact made"
Actions:
  - Send LinkedIn connection request (via Phantombuster)
  - Wait 3 days
  - Send follow-up email
  - Wait 7 days
  - Move to nurture sequence

# Workflow 3: Lost opportunity
Trigger: Deal marked "Lost"
Actions:
  - Tag contact as "Past prospect"
  - Add to 90-day nurture campaign
  - Set reminder to re-engage
```

---

## Quality Assurance Checklist

### Before Every Delivery:

- [ ] All contacts have at least email OR phone
- [ ] Company websites are valid URLs
- [ ] Job summaries are complete (no "[Extract from description]" placeholders)
- [ ] Pain scores are within expected range (60-100)
- [ ] No duplicate companies from previous weeks
- [ ] CSV encoding is UTF-8 (no garbled German characters)
- [ ] Column headers match HubSpot import mapping

### Weekly Review:

- [ ] Sales team feedback on lead quality (1-5 rating)
- [ ] Conversion rate tracking (calls → meetings → deals)
- [ ] False positive analysis (leads marked as unqualified)
- [ ] Enrichment accuracy (contact title verification)

---

## Troubleshooting Guide

### Issue: Scraping gets blocked

**Solutions:**
1. Switch to better residential proxies (Bright Data, Oxylabs)
2. Increase delays between requests (3-5 seconds)
3. Rotate user agents more frequently
4. Use CAPTCHA solving service (2Captcha)
5. Consider third-party data providers as alternative

### Issue: Enrichment API rate limits

**Solutions:**
1. Spread requests over longer time window
2. Use multiple API providers in parallel
3. Cache results to avoid re-enriching same companies
4. Prioritize high-pain-score leads first

### Issue: Low contact quality (missing phones/emails)

**Solutions:**
1. Try different enrichment providers
2. Cross-validate data across multiple sources
3. Use email verification service (Hunter.io)
4. Accept leads with 2 contacts if high pain score

### Issue: HubSpot import failures

**Solutions:**
1. Validate CSV format before upload
2. Check for special characters in data
3. Use HubSpot's import preview feature
4. Import in smaller batches (50 companies at a time)

---

## Cost Optimization Tips

1. **Scraping:**
   - Use shared proxies for testing, dedicated for production
   - Implement intelligent rate limiting (don't scrape faster than needed)
   - Cache job listings to avoid re-scraping same pages

2. **Enrichment:**
   - Batch requests when API allows
   - Use cheaper providers for lower-priority leads
   - Implement tiered enrichment (basic for all, premium for high-pain)

3. **LLM Summarization:**
   - Use GPT-3.5 instead of GPT-4 if quality is acceptable
   - Batch multiple jobs in single API call
   - Consider fine-tuned models for higher volume

4. **Infrastructure:**
   - Start with smaller server, scale up if needed
   - Use spot instances (AWS) for non-critical workloads
   - Optimize database queries to reduce compute time

---

## Success Metrics

### Week 1 (Test Phase):
- ✅ 10-20 qualified companies delivered
- ✅ 80%+ have 3+ contacts with phone numbers
- ✅ Pain scores validated by manual review

### Month 1 (Ramp-up):
- 🎯 200-400 companies delivered
- 🎯 600-1200 contacts delivered
- 🎯 <5% duplicate rate
- 🎯 90%+ lead quality rating from sales team

### Month 3 (Steady State):
- 🎯 400-800 companies/month
- 🎯 15-20% of leads convert to initial call
- 🎯 5-8% of leads convert to qualified opportunity
- 🎯 Full automation running with minimal manual intervention

---

## Next Actions (Start Now)

### For Zeynel:
1. ✅ Review and approve implementation plan
2. ⏳ Provide API credentials for enrichment service
3. ⏳ Grant HubSpot access for testing
4. ⏳ Confirm budget for proxies and APIs
5. ⏳ Set up weekly review call time

### For Implementation Team:
1. ⏳ Set up development environment
2. ⏳ Build StepStone scraper prototype (Day 2-3)
3. ⏳ Test enrichment API integration (Day 3-4)
4. ⏳ Generate test dataset (Day 5)
5. ⏳ Schedule validation call with Zeynel

---

## Contact & Support

**Project Questions:** Contact Zeynel  
**Technical Issues:** [Implementation team contact]  
**Emergency Escalation:** [Emergency contact]

**Documentation:**
- Full Implementation Plan: `lead_generation_implementation_plan.md`
- Python Pipeline: `lead_generation_pipeline.py`
- This Guide: `quick_start_guide.md`

---

**Last Updated:** January 28, 2026  
**Version:** 1.0  
**Status:** Ready for Phase 1 Implementation
