# Lead Generation System - Technical Implementation Plan
## High-Pain Sales Roles Lead Sourcing & Scraping

---

## Executive Summary

This document outlines the technical implementation for an automated lead generation system targeting companies with high-pain sales vacancies in IT-related roles. The system will scrape job boards, identify pain signals, enrich with decision-maker contacts, and deliver HubSpot-ready leads on a recurring basis.

**Timeline:** Phase 1 test delivery this week, full automation within 2-3 weeks  
**Expected Output:** 50-200 qualified leads per week with 3+ contacts each  
**Tech Stack:** Python scraping + enrichment APIs + HubSpot integration

---

## 1. Target Roles (Priority Order)

### Priority 1 - Implement Immediately:
1. **Sales Engineer (IT)**
2. **Solution Consultant (IT)**
3. **Cyber Security Sales**
4. **SAP Consultant Sales**
5. **Security Consultant / IT Security Consultant**

### Fallback (if volume insufficient):
- Cloud Sales
- Industry 4.0 / IoT Sales

---

## 2. Data Sources & Scraping Strategy

### 2.1 Primary Source: StepStone
**Priority:** Primary (German market focus)

**Scraping Approach:**
- Use Selenium/Playwright for JavaScript rendering
- Rotate proxies for rate limiting (German residential proxies preferred)
- User-agent rotation to mimic real browsers
- Session management to avoid detection

**Target URLs:**
```
Base: https://www.stepstone.de/work
Filters: IT & Internet sector, DACH region, specific role keywords
```

**Data Points to Extract:**
- Job title
- Company name
- Location
- Publication date (calculate "days open")
- Job description (full text for skill extraction)
- Number of employees (if available)
- Company website/domain
- Application URL

**Pain Signal Indicators:**
- Jobs open >30 days
- Jobs reposted multiple times
- Detailed requirement lists (indicates complexity)
- Senior/Lead/Principal in title (harder to fill)

### 2.2 Secondary Source: LinkedIn Jobs
**Priority:** Secondary validation + additional signals

**Scraping Approach:**
- LinkedIn scraping requires careful rate limiting (high ban risk)
- Consider using LinkedIn API (limited) or third-party data providers
- Alternative: Bright Data's LinkedIn Jobs dataset

**Additional Data Points:**
- Total applications received
- Applications in last 24 hours
- Hiring manager/recruiter information
- Company size and industry tags

**Pain Signal Indicators:**
- High application count (>100) but still open
- "Actively recruiting" tag with old post date
- Multiple similar roles open simultaneously

### 2.3 Scraping Schedule
- **Frequency:** Daily (preferred) or twice weekly minimum
- **Runtime:** Off-peak hours (2-6 AM CET) to reduce detection risk
- **Volume:** Estimate 200-500 raw jobs per run
- **After filtering:** 50-150 qualified leads per week

---

## 3. Filtering Logic - High-Pain Identification

### 3.1 Must-Have Criteria (AND logic)

**Experience Level:**
- Senior / Lead / Principal level roles
- 3+ years experience mentioned
- Exclude: Junior, Trainee, Entry-level

**Technical Depth:**
- Keywords: SAP, Security, Cybersecurity, Cloud platforms, Solutions architecture
- Complex product indicators: Enterprise, B2B, Consultative selling

**Business Model:**
- B2B companies only
- Complex products/Enterprise segment
- Exclude: B2C, retail, call centers, door-to-door

**Company Profile:**
- Industry: IT, SaaS, IT service providers, cybersecurity, ERP/CRM partners
- Size: 50+ employees (optional, not mandatory filter)
- Region: DACH (Germany, Austria, Switzerland)

### 3.2 Exclusion Criteria (Remove immediately)

**Role Types:**
- SDR / BDR (too junior)
- Pure inside sales
- Call center positions
- Retail sales
- Door-to-door sales

**Job Characteristics:**
- Trainee programs
- Internships
- Part-time only positions

### 3.3 Pain Score Calculation

Assign scores to create priority ranking:

```
Base Score: 50 points

ADD points for:
+20: Job open >30 days
+15: Job open >60 days
+10: Senior/Lead/Principal in title
+10: 100+ applications (LinkedIn)
+10: SAP/Security/Complex tech mentioned
+10: Enterprise/Consultative selling mentioned
+5: Multiple similar roles open at same company
+5: Job reposted (detected by URL patterns)

SUBTRACT points for:
-30: Inside sales mentioned
-20: SDR/BDR in description
-15: Junior/Entry level

Threshold: Keep only jobs scoring 60+
```

---

## 4. Company & Contact Enrichment

### 4.1 Company Data Enrichment

**Goal:** Build complete company profile for each vacancy

**Data Sources:**
1. **Company website scraping** (extract from job posting)
2. **Clearbit/Similar services** (company firmographics)
3. **LinkedIn Company pages** (validation + employee count)

**Required Fields:**
- Company name (normalized)
- Website/Domain
- Industry (from LinkedIn taxonomy)
- Employee count
- Location/HQ
- Company LinkedIn URL

### 4.2 Contact Discovery & Enrichment

**Requirement:** Minimum 3 decision-makers per company

**Target Roles (Priority Order):**
1. CEO / Managing Director / Geschäftsführer
2. CRO / VP Sales / Head of Sales
3. Sales Director
4. Head of Business Development
5. Head of Human Resources (fallback only)

**Data Sources:**
- **Primary:** Leap.ai, Cognizant, Lucia APIs
- **Backup:** Apollo.io, RocketReach, ContactOut
- **LinkedIn:** Direct scraping (careful rate limiting)

**Required Contact Fields:**
- First name
- Last name
- Email (verified if possible)
- Phone number (critical - mobile preferred)
- LinkedIn URL
- Role/Title
- Seniority level (C-Level/VP/Head/Director)

**Enrichment Process:**
1. Extract company domain from job posting
2. Query enrichment API with domain + target titles
3. Return top 3-5 contacts matching criteria
4. Verify email deliverability (use Hunter.io or similar)
5. Prioritize contacts with phone numbers

### 4.3 Quality Thresholds

**Minimum viable lead:**
- Company name + website
- At least 1 contact with email OR phone
- Job still active (checked within 48 hours)

**Target quality lead:**
- Company name + website + employee count
- 3+ contacts with email AND phone
- Job open 30+ days
- Pain score 70+

---

## 5. Job Summary Generation (For Call Scripts)

### 5.1 Summary Template

For each job, generate structured summary in this format:

```markdown
**Role:** [Job Title]
**Company:** [Company Name] ([Employee Count])
**Open Since:** [Days] days
**Pain Signals:** [List indicators, e.g., "60+ days open, 150+ applications"]

**Must-Have Skills:**
- [Skill 1, e.g., SAP S/4HANA experience]
- [Skill 2, e.g., 5+ years enterprise sales]
- [Skill 3, e.g., Fluent German + English]

**Key Requirements:**
[2-3 sentence summary of role expectations, using client-friendly language]

**Special Features:**
[Any standout details: remote work, equity, unusual perks, reporting structure]
```

### 5.2 Implementation Approach

**Option A: Rule-Based Extraction**
- Parse job descriptions with regex patterns
- Identify skills from predefined taxonomy
- Extract years of experience with NLP
- Pros: Fast, predictable, no API costs
- Cons: May miss nuanced requirements

**Option B: LLM-Based Summarization (Recommended)**
- Use Anthropic Claude API to generate summaries
- Provide template and instructions
- Extract structured data in one pass
- Pros: High quality, adapts to variations, excellent at following structured formats
- Cons: API costs (~$0.01-0.02 per job with Claude 3.5 Sonnet)

**Recommendation:** Use Option B (Claude) for test phase, evaluate cost/benefit for production

---

## 6. Deliverable Format - HubSpot Ready

### 6.1 File Structure

**Format:** CSV with UTF-8 encoding  
**Alternative:** Google Sheets with auto-sync  
**Naming:** `leads_stepstone_YYYYMMDD.csv`

### 6.2 Column Schema

**Company-Level Fields:**
```
company_name
company_website
company_domain
company_industry
company_employee_count
company_location
company_linkedin_url
```

**Job-Level Fields:**
```
job_title
job_url
job_source (StepStone/LinkedIn)
job_open_since_days
job_summary (formatted as above)
job_must_have_skills (comma-separated)
job_special_features
job_pain_score
```

**Contact-Level Fields (repeating, 3+ per company):**
```
contact_1_first_name
contact_1_last_name
contact_1_email
contact_1_phone
contact_1_role
contact_1_seniority
contact_1_linkedin_url

contact_2_first_name
...
(repeat for contact_2, contact_3, etc.)
```

### 6.3 HubSpot Import Mapping

**Company Object:**
- Map `company_domain` as unique identifier
- Import company_* fields to Company properties

**Contact Objects:**
- Create 3+ contacts per company
- Link to Company via domain
- Map contact_* fields to Contact properties

**Deal/Job Object (Custom):**
- Create custom object "Job Opportunity"
- Link to Company
- Store job_* fields

### 6.4 Duplicate Prevention

**Before delivery:**
1. Check against previous weeks' exports
2. Query HubSpot API for existing companies (by domain)
3. Mark duplicates with flag in CSV
4. Include "new_lead" boolean column

**In HubSpot:**
- Use workflows to prevent duplicate contact creation
- Update existing records if newer data available

---

## 7. Technical Architecture

### 7.1 System Components

```
┌─────────────────────────────────────────────────────────┐
│                   Scheduling Layer                       │
│              (Airflow / GitHub Actions)                  │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│  StepStone   │          │  LinkedIn    │
│   Scraper    │          │   Scraper    │
└──────┬───────┘          └──────┬───────┘
       │                         │
       └────────────┬────────────┘
                    │
                    ▼
         ┌────────────────────┐
         │  Raw Data Storage  │
         │   (PostgreSQL)     │
         └─────────┬──────────┘
                   │
                   ▼
         ┌────────────────────┐
         │  Filter & Scoring  │
         │      Engine        │
         └─────────┬──────────┘
                   │
                   ▼
         ┌────────────────────┐
         │   Enrichment API   │
         │  (Leap/Cognizant)  │
         └─────────┬──────────┘
                   │
                   ▼
         ┌────────────────────┐
         │  LLM Summarization │
         │   (GPT-4/Claude)   │
         └─────────┬──────────┘
                   │
                   ▼
         ┌────────────────────┐
         │  CSV Generation &  │
         │ Duplicate Check    │
         └─────────┬──────────┘
                   │
                   ▼
         ┌────────────────────┐
         │  HubSpot Import    │
         │   (API/Manual)     │
         └────────────────────┘
```

### 7.2 Technology Stack

**Scraping Layer:**
- Python 3.10+
- Selenium or Playwright (JavaScript rendering)
- BeautifulSoup4 (HTML parsing)
- Scrapy (optional, for scale)
- Bright Data or Oxylabs (proxy rotation)

**Data Processing:**
- Pandas (data manipulation)
- PostgreSQL or SQLite (raw data storage)
- Redis (caching, deduplication)

**Enrichment:**
- Leap.ai API / Cognizant API / Lucia API
- Apollo.io (backup)
- Hunter.io (email verification)

**LLM Integration:**
- Anthropic Claude API (3.5 Sonnet or 3.5 Haiku for cost optimization)
- LangChain (optional, for structured extraction)

**Automation:**
- Apache Airflow (preferred) or GitHub Actions (simpler)
- Docker containers for reproducibility

**HubSpot Integration:**
- HubSpot Python SDK
- REST API for custom object creation

### 7.3 Infrastructure

**Development Environment:**
- Local machine for testing
- Docker Compose for local services

**Production Environment:**
- AWS EC2 or DigitalOcean Droplet (4GB RAM minimum)
- Managed PostgreSQL (AWS RDS or similar)
- S3 for CSV storage and backups
- CloudWatch or Datadog for monitoring

**Cost Estimate (Monthly):**
- Compute: $50-100
- Proxies: $100-200
- Enrichment APIs: $200-500 (usage-based)
- Claude API: $30-100 (Claude 3.5 Haiku: ~$0.01/job, Sonnet: ~$0.02/job)
- **Total: $380-900/month**

---

## 8. Implementation Phases

### Phase 1: Test Delivery (This Week)

**Goal:** Deliver small test dataset to validate approach

**Tasks:**
1. Set up scraping for StepStone (25-50 jobs)
2. Apply filtering logic manually
3. Enrich 5-10 companies with contacts
4. Generate job summaries
5. Create CSV in specified format
6. Review with Zeynel before scaling

**Deliverable:** 
- 10-20 qualified companies
- 30-60 contacts (3 per company)
- Job summaries for call scripts
- CSV file for HubSpot import

**Timeline:** 3-5 days

### Phase 2: Full Automation (Week 2-3)

**Goal:** Productionize system for recurring weekly delivery

**Tasks:**
1. Build robust scraping pipeline for both sources
2. Implement pain score calculation
3. Automate enrichment with error handling
4. Set up LLM summarization
5. Configure duplicate detection
6. Deploy to cloud infrastructure
7. Set up monitoring and alerts
8. Create admin dashboard for tracking

**Deliverable:**
- Fully automated weekly lead delivery
- 50-200 companies per week
- 150-600 contacts per week
- Self-healing error recovery

**Timeline:** 2-3 weeks

### Phase 3: HubSpot Automation (Future)

**Goal:** Close the loop with automated workflows

**Triggers:**
- Sales rep logs "no contact" → LinkedIn connection request
- Sales rep logs "lost opportunity" → Nurture sequence
- New lead created → Auto-assign to rep + first touch email

**Tasks:**
1. Build HubSpot workflows for each trigger
2. Integrate LinkedIn automation (Phantombuster or similar)
3. Create email templates for sequences
4. Set up reporting dashboard

**Timeline:** 1-2 weeks (after Phase 2 validation)

---

## 9. Quality Assurance & Validation

### 9.1 Data Quality Checks

**Automated Validation:**
- Email format validation (regex)
- Phone number format validation (international formats)
- URL accessibility checks (HTTP 200 response)
- Duplicate detection (by domain + job title)

**Manual Validation (Sample-Based):**
- Review 10% of leads each week
- Verify contact accuracy (LinkedIn cross-check)
- Confirm job still active
- Check pain score accuracy

### 9.2 Success Metrics

**Lead Quality:**
- Target: 80%+ have 3+ contacts with phone numbers
- Target: 90%+ pain score accuracy (validated by sales feedback)
- Target: <5% duplicate rate

**Lead Quantity:**
- Week 1-4: 50-100 companies/week (ramp-up)
- Steady state: 100-200 companies/week
- Contacts: 300-600/week (3+ per company)

**System Reliability:**
- 95%+ uptime for scheduled runs
- <5% scraping failure rate
- 24-hour max delay for delivery

### 9.3 Feedback Loop

**Weekly Review:**
1. Sales team rates lead quality (1-5 scale)
2. Track conversion rates by lead source
3. Identify false positives in pain scoring
4. Adjust filters based on feedback

**Monthly Optimization:**
1. Retrain pain score model
2. Update enrichment source priorities
3. Refine job title keyword lists
4. Add new data sources if needed

---

## 10. Risk Management

### 10.1 Technical Risks

**Risk: Scraping detection/blocking**
- Mitigation: Proxy rotation, user-agent diversity, rate limiting
- Backup: Use official APIs or third-party data providers

**Risk: Enrichment API rate limits**
- Mitigation: Queue-based processing, spread across multiple APIs
- Backup: Manual enrichment for high-priority leads

**Risk: HubSpot import failures**
- Mitigation: Validation before import, error logging, manual fallback
- Backup: Google Sheets import option

### 10.2 Data Quality Risks

**Risk: Outdated contact information**
- Mitigation: Cross-validation across multiple sources
- Backup: Email verification services, phone number validation

**Risk: False positive pain signals**
- Mitigation: Multi-factor scoring, sales feedback loop
- Backup: Manual review for high-value targets

### 10.3 Operational Risks

**Risk: Key person dependency (Zeynel)**
- Mitigation: Documentation, code comments, video walkthroughs
- Backup: Training for backup administrator

**Risk: Legal/compliance issues (GDPR)**
- Mitigation: Use legitimate business contact data sources only
- Backup: Legal review of enrichment providers

---

## 11. Compliance & Legal Considerations

### 11.1 GDPR Compliance

**Data Collection:**
- Collect only business contact data (legitimate interest)
- Avoid personal emails (@gmail, @yahoo, etc.)
- Document legal basis for processing

**Data Storage:**
- Store data in EU region (or with GDPR-compliant provider)
- Implement data retention policy (delete after 12 months)
- Enable "right to be forgotten" workflow

**Consent:**
- Not required for B2B business contacts in sales context
- Provide opt-out mechanism in all communications

### 11.2 Terms of Service Compliance

**StepStone:**
- Review TOS for scraping restrictions
- Use respectful rate limiting
- Consider API access if available

**LinkedIn:**
- High risk of account suspension for aggressive scraping
- Prefer third-party data providers with LinkedIn licensing
- Alternative: LinkedIn Sales Navigator + manual export

---

## 12. Scalability & Future Enhancements

### 12.1 Scaling Opportunities

**Geographic Expansion:**
- Add UK/US job boards (Indeed, Monster, Dice)
- Localize pain signals by market
- Hire multilingual enrichment

**Role Expansion:**
- Add more technical sales roles (DevOps, Data Sales)
- Expand to non-tech (Finance, Healthcare) if successful
- Create role-specific pain scoring models

**Signal Sophistication:**
- Add company funding events (signal of growth)
- Monitor layoff news (signal of restructuring)
- Track competitor job postings (signal of market trend)

### 12.2 Advanced Features (Phase 4+)

**Predictive Scoring:**
- ML model to predict lead conversion probability
- Train on historical sales outcomes
- Prioritize leads by expected value

**Real-Time Alerts:**
- Slack/email notification for super high-pain leads
- Daily digest of top 10 opportunities
- Trigger immediate outreach for "hot" leads

**CRM Deep Integration:**
- Bi-directional sync with HubSpot
- Auto-log sales activities back to lead source
- Close loop on lead attribution

**Competitive Intelligence:**
- Track which competitors are hiring similar roles
- Identify market expansion signals
- Benchmark against industry hiring trends

---

## 13. Next Steps & Action Items

### Immediate (This Week):

**For Client (Zeynel):**
1. ✅ Confirm priority role titles and keywords
2. ✅ Provide HubSpot access for import testing
3. ✅ Select enrichment API provider (Leap/Cognizant/Lucia)
4. ⏳ Review and approve filter logic
5. ⏳ Set up feedback mechanism for lead quality

**For Implementation Team:**
1. ✅ Document review complete
2. ⏳ Build StepStone scraper prototype
3. ⏳ Test enrichment API integration
4. ⏳ Generate first test dataset (10-20 companies)
5. ⏳ Schedule validation call with Zeynel

### Week 2-3:

**Technical:**
- Complete LinkedIn scraper
- Deploy to cloud infrastructure
- Set up automated scheduling
- Build monitoring dashboard

**Business:**
- Validate Phase 1 results with sales team
- Refine filters based on feedback
- Finalize pricing/contract for recurring service

### Month 2:

**Optimization:**
- Analyze first month's conversion data
- Optimize pain score algorithm
- Expand to additional data sources

**Automation:**
- Implement HubSpot workflow triggers
- Add LinkedIn automation
- Create email nurture sequences

---

## 14. Pricing & Commercials (For Discussion)

### Service Model Options:

**Option A: Per-Lead Pricing**
- $5-10 per qualified company (with 3+ contacts)
- ~$500-1500/week revenue at 100-200 companies/week

**Option B: Monthly Retainer**
- Fixed fee: $2,000-4,000/month
- Guaranteed: 200-400 companies/month
- Includes: Weekly delivery + support + optimizations

**Option C: Revenue Share**
- Base fee: $1,000/month
- Plus: 5-10% of closed revenue from leads
- Requires CRM integration for attribution

### Cost Structure (For Internal Planning):

**Fixed Costs:**
- Infrastructure: $400-950/month
- Developer time: 40-80 hours/month (maintenance)

**Variable Costs:**
- Enrichment APIs: ~$1-3 per company
- LLM summarization: ~$0.02-0.05 per job

**Break-Even:** ~150 companies/month at $10/company pricing

---

## 15. Appendices

### A. Sample Job Titles (Full List)

**Primary Roles:**
- Sales Engineer (IT)
- Solution Consultant (IT)
- Technical Sales Consultant
- Pre-Sales Consultant
- Cyber Security Sales
- IT Security Sales Consultant
- SAP Consultant Sales
- SAP Sales Specialist
- Security Consultant
- IT Security Consultant

**Fallback Roles:**
- Cloud Sales Engineer
- Cloud Solution Architect (Sales)
- Industry 4.0 Sales
- IoT Sales Consultant

### B. German Keywords (For StepStone)

**Job Titles:**
- Vertriebsingenieur
- Sales Engineer
- Lösungsberater
- Solution Consultant
- IT-Sicherheitsberater
- Cyber Security Vertrieb
- SAP Vertriebsberater
- Sicherheitsberater

**Industries:**
- IT & Internet
- Software & IT-Services
- Cybersecurity
- ERP/CRM
- SaaS

### C. Contact Title Variations

**CEO/Managing Director:**
- CEO, Chief Executive Officer
- Managing Director, Geschäftsführer
- Founder, Co-Founder, Mitgründer
- President, Präsident

**CRO/VP Sales:**
- CRO, Chief Revenue Officer
- VP Sales, Vice President Sales
- Head of Sales, Leiter Vertrieb
- Sales Director, Vertriebsleiter

**HR/People:**
- Head of HR, Leiter Personal
- CHRO, Chief Human Resources Officer
- Head of People, Leiter People & Culture
- Talent Acquisition Lead

### D. Sample Pain Score Calculation

**Example Job:**
```
Title: Senior SAP Sales Consultant
Company: TechCorp GmbH (250 employees)
Open Since: 45 days
Applications: 120
Industry: IT Services
```

**Scoring:**
- Base: 50
- 30-60 days open: +15
- Senior in title: +10
- SAP mentioned: +10
- 100+ applications: +10
- IT Services industry: +5
- **Total: 100 (HIGH PRIORITY)**

---

## Document Control

**Version:** 1.0  
**Created:** January 28, 2026  
**Author:** Claude (AI Assistant)  
**Status:** Draft for Review  
**Next Review:** After Phase 1 test delivery  
**Approval Required:** Zeynel (Client)

**Change Log:**
- v1.0 (2026-01-28): Initial comprehensive plan based on briefing document and problem statement

---

## Contact & Support

**Project Lead:** Zeynel  
**Implementation Team:** TBD  
**Review Cadence:** Weekly during Phase 1, Bi-weekly thereafter  
**Escalation Path:** Technical issues → Implementation Lead → Zeynel

