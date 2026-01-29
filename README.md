# Lead Generation System for High-Pain Sales Roles

Automated pipeline for identifying, enriching, and qualifying IT sales vacancies with high business pain signals.

---

## 📋 Project Overview

**Purpose:** Build a recurring lead generation machine that identifies companies with difficult-to-fill IT sales positions and enriches them with decision-maker contact information.

**Key Insight:** Companies with long-standing, complex sales vacancies have genuine pain and higher purchase intent for premium staffing solutions.

**Delivery:** Weekly batches of HubSpot-ready leads (100-200 companies, 300-600 contacts) with pain scores, job summaries, and actionable intelligence.

---

## 🎯 Target Roles (Priority Order)

1. **Sales Engineer (IT)**
2. **Solution Consultant (IT)**  
3. **Cyber Security Sales**
4. **SAP Consultant Sales**
5. **Security Consultant / IT Security Consultant**

**Fallback:** Cloud Sales, Industry 4.0 Sales, IoT Sales

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATION LAYER                       │
│              (Airflow / Cron / GitHub Actions)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌───────────────────┐           ┌───────────────────┐
│   STEPSTONE       │           │   LINKEDIN JOBS   │
│    SCRAPER        │           │     SCRAPER       │
│  (Selenium)       │           │   (Playwright)    │
└─────────┬─────────┘           └─────────┬─────────┘
          │                               │
          │   ┌────────────────────┐     │
          └──→│  RAW JOB STORAGE   │←────┘
              │   (PostgreSQL)     │
              └──────────┬─────────┘
                         │
                         ▼
              ┌────────────────────┐
              │  FILTER & SCORE    │
              │      ENGINE        │
              │                    │
              │ • Exclusion rules  │
              │ • Pain scoring     │
              │ • Deduplication    │
              └──────────┬─────────┘
                         │
                         ▼
              ┌────────────────────┐
              │   QUALIFICATION    │
              │      FILTER        │
              │                    │
              │ Score ≥60 only     │
              └──────────┬─────────┘
                         │
                         ▼
              ┌────────────────────┐
              │   ENRICHMENT API   │
              │                    │
              │ • Leap.ai          │
              │ • Cognizant        │
              │ • Lucia            │
              │                    │
              │ Find 3+ contacts:  │
              │ CEO, CRO, Sales    │
              └──────────┬─────────┘
                         │
                         ▼
              ┌────────────────────┐
              │  LLM SUMMARIZER    │
              │   (GPT-4/Claude)   │
              │                    │
              │ Generate call-ready│
              │ job summaries      │
              └──────────┬─────────┘
                         │
                         ▼
              ┌────────────────────┐
              │   CSV GENERATOR    │
              │                    │
              │ • HubSpot format   │
              │ • Duplicate check  │
              │ • UTF-8 encoding   │
              └──────────┬─────────┘
                         │
                         ▼
              ┌────────────────────┐
              │  HUBSPOT IMPORT    │
              │                    │
              │ • Companies        │
              │ • Contacts         │
              │ • Associations     │
              └────────────────────┘
```

---

## 🔄 Data Flow

### 1. Job Discovery
**Input:** Target role keywords, DACH region, IT industry  
**Sources:** StepStone (primary), LinkedIn Jobs (secondary)  
**Output:** 200-500 raw job listings per week

### 2. Pain Signal Detection
**Signals:**
- Days open (30+ days = high pain)
- Application volume (100+ apps = desperation)
- Seniority level (Senior/Lead = harder to fill)
- Technical complexity (SAP/Security = scarce talent)
- Sales complexity (Enterprise/Consultative = long cycles)

**Scoring:**
```
Base: 50 points
+20: Job open >30 days
+15: Job open >60 days
+10: Senior/Lead/Principal in title
+10: 100+ applications
+10: SAP/Security/Complex tech
+10: Enterprise/Consultative selling
-30: Inside sales mentioned
-20: SDR/BDR in description

Threshold: Keep only ≥60 points
```

**Output:** 100-200 qualified jobs per week

### 3. Contact Enrichment
**Input:** Company domain from job posting  
**Process:** API calls to find decision-makers  
**Target Titles:**
- CEO / Managing Director
- CRO / VP Sales / Head of Sales
- Sales Director
- Head of Business Development
- Head of HR (fallback)

**Output:** 3-5 contacts per company with email + phone

### 4. Summary Generation
**Input:** Job description + company data  
**Process:** LLM extracts structured information  
**Output:** Call-ready summary with:
- Must-have skills (3-5 bullets)
- Key requirements (2-3 sentences)
- Special features (remote, equity, etc.)

### 5. HubSpot Delivery
**Format:** CSV with flat structure  
**Objects:** Company + 3-5 Contacts per company  
**Custom Fields:** Pain score, job summary, days open

---

## 📊 Sample Lead Structure

```csv
company_name,company_domain,job_title,job_url,source,days_open,pain_score,job_summary,contact_1_first_name,contact_1_last_name,contact_1_email,contact_1_phone,contact_1_role,...

"TechCorp GmbH","techcorp.de","Senior Sales Engineer","https://...","StepStone",45,90,"**Role:** Senior Sales Engineer...",
"Klaus","Müller","k.mueller@techcorp.de","+49 89 12345678","CEO",...
```

---

## 🛠️ Technology Stack

### Core Components
- **Python 3.10+** - Main programming language
- **Selenium / Playwright** - Web scraping with JavaScript rendering
- **BeautifulSoup4** - HTML parsing
- **Pandas** - Data manipulation
- **PostgreSQL** - Raw data storage
- **Redis** - Caching and deduplication

### External Services
- **Proxies:** Bright Data / Oxylabs (residential IPs)
- **Enrichment:** Leap.ai / Cognizant / Lucia APIs
- **LLM:** Anthropic Claude (3.5 Sonnet or 3.5 Haiku)
- **Email Verification:** Hunter.io
- **HubSpot API:** CRM integration

### Infrastructure
- **Compute:** AWS EC2 / DigitalOcean (4GB RAM)
- **Scheduling:** Cron / Airflow
- **Monitoring:** CloudWatch / Custom dashboard
- **Storage:** S3 for CSV backups

---

## 💰 Cost Structure

### Monthly Recurring Costs
| Category | Amount | Notes |
|----------|--------|-------|
| Infrastructure | $50-100 | EC2/Droplet + database |
| Proxies | $100-200 | Residential IPs for scraping |
| Enrichment APIs | $200-500 | Usage-based, ~$1-3 per company |
| Claude API | $30-100 | Haiku: ~$0.01/job, Sonnet: ~$0.02/job |
| **Total** | **$380-900** | Scales with volume |

### Cost per Lead
- **Target:** $3-5 per company
- **Break-even:** ~150 companies/month at $10 pricing

---

## 📈 Success Metrics

### Phase 1 (Week 1 - Test)
- ✅ 10-20 companies delivered
- ✅ 80%+ quality approval
- ✅ All data fields complete

### Phase 2 (Month 1 - Ramp-up)
- 🎯 200-400 companies/month
- 🎯 600-1200 contacts/month
- 🎯 <5% duplicate rate
- 🎯 90%+ lead quality rating

### Phase 3 (Month 3+ - Steady State)
- 🎯 400-800 companies/month
- 🎯 15-20% leads convert to calls
- 🎯 5-8% leads convert to opportunities
- 🎯 Positive ROI demonstrated

---

## 🚀 Quick Start

### Development Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd lead-generation

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Initialize database (optional)
python manage.py init_db

# 6. Run test scraper
python lead_generation_pipeline.py --test --max-jobs 10
```

### Environment Variables

```bash
# .env file
STEPSTONE_PROXY_URL=http://proxy:port
LEAP_API_KEY=your_leap_key
ANTHROPIC_API_KEY=your_anthropic_key
HUBSPOT_API_KEY=your_hubspot_key
DATABASE_URL=postgresql://user:pass@localhost/leadgen
LOG_LEVEL=INFO
```

### Running the Pipeline

```bash
# Full production run
python lead_generation_pipeline.py

# With specific roles
python lead_generation_pipeline.py --roles "Sales Engineer,Solution Consultant"

# Test mode (limited jobs)
python lead_generation_pipeline.py --test --max-jobs 50

# Export only (skip scraping)
python lead_generation_pipeline.py --export-only --input-file raw_jobs.csv
```

---

## 📁 Project Structure

```
lead-generation/
├── lead_generation_pipeline.py      # Main orchestration
├── scrapers/
│   ├── stepstone_scraper.py         # StepStone scraping logic
│   └── linkedin_scraper.py          # LinkedIn scraping logic
├── filters/
│   └── job_filter.py                # Filtering and scoring
├── enrichment/
│   ├── contact_enricher.py          # API integrations
│   └── email_verifier.py            # Email validation
├── summarization/
│   └── job_summarizer.py            # LLM-based summaries
├── exporters/
│   └── hubspot_exporter.py          # CSV generation + API
├── models/
│   ├── job_listing.py               # Data models
│   ├── contact.py
│   └── enriched_lead.py
├── utils/
│   ├── config.py                    # Configuration
│   ├── logger.py                    # Logging setup
│   └── validators.py                # Data validation
├── tests/
│   └── test_*.py                    # Unit tests
├── docs/
│   ├── lead_generation_implementation_plan.md
│   ├── quick_start_guide.md
│   └── validation_checklist.md
├── requirements.txt
├── .env.example
└── README.md                        # This file
```

---

## 🔍 Quality Assurance

### Automated Validation (Every Run)
- ✅ All contacts have email OR phone
- ✅ Company domains are valid URLs
- ✅ Pain scores within 60-100 range
- ✅ No duplicate companies
- ✅ UTF-8 encoding (German characters)

### Manual Review (Weekly Sample)
- Check 10% of leads for accuracy
- Verify jobs still active
- LinkedIn cross-check contacts
- Validate pain score alignment

### Sales Feedback Loop
- Weekly quality rating (1-5 scale)
- Track conversion rates
- Adjust filters based on results
- Continuous improvement cycles

---

## 🐛 Troubleshooting

### Common Issues

**Scraping Blocked:**
- Switch to better proxies (residential IPs)
- Increase delays between requests
- Use CAPTCHA solving service
- Consider third-party data providers

**Low Contact Quality:**
- Try different enrichment API
- Cross-validate across multiple sources
- Use email verification service
- Accept 2 contacts for high-pain leads

**HubSpot Import Fails:**
- Validate CSV format
- Check special characters
- Use import preview feature
- Import in smaller batches

---

## 📞 Support & Documentation

### Key Documents
1. **Implementation Plan** (`lead_generation_implementation_plan.md`)  
   Complete 15-section technical specification

2. **Quick Start Guide** (`quick_start_guide.md`)  
   Day-by-day implementation checklist

3. **Validation Checklist** (`validation_checklist.md`)  
   QA procedures and success criteria

4. **This README**  
   System overview and quick reference

### Contact
- **Project Lead:** Zeynel
- **Technical Support:** Implementation Team
- **Documentation:** See `/docs` folder

---

## 🔄 Roadmap

### Phase 1: Test Delivery (Week 1) ✅
- Build StepStone scraper
- Implement core filtering
- Test enrichment API
- Deliver 10-20 test companies

### Phase 2: Full Automation (Week 2-3) 🚧
- Add LinkedIn scraper
- Deploy to production
- Set up monitoring
- Scale to 100-200 companies/week

### Phase 3: HubSpot Workflows (Week 4+) 📅
- Automated follow-up sequences
- LinkedIn connection requests
- Nurture campaigns for lost leads

### Future Enhancements 🔮
- Predictive lead scoring with ML
- Real-time alerts for hot leads
- Competitive intelligence tracking
- Geographic expansion (UK, US)

---

## 📄 License & Compliance

### Data Usage
- Business contact data only (GDPR-compliant)
- Legitimate interest for B2B sales
- Opt-out mechanism provided
- Data retention: 12 months

### Terms of Service
- Respectful scraping (rate limiting)
- No aggressive anti-detection tactics
- Prefer official APIs when available

---

## 🙏 Acknowledgments

**Built with best practices from:**
- Anthropic's prompt engineering guides
- HubSpot API documentation
- Web scraping community standards
- Sales automation playbooks

---

**Version:** 1.0  
**Last Updated:** January 28, 2026  
**Status:** Ready for Implementation

---

## Quick Links

- 📖 [Full Implementation Plan](./lead_generation_implementation_plan.md)
- 🚀 [Quick Start Guide](./quick_start_guide.md)
- ✅ [Validation Checklist](./validation_checklist.md)
- 🐍 [Python Pipeline](./lead_generation_pipeline.py)
- 📦 [Requirements](./requirements.txt)

**Ready to start? Run:** `python lead_generation_pipeline.py --test`
