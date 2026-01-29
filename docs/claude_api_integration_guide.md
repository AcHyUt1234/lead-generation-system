# Anthropic Claude API Integration Guide
## For Lead Generation System

---

## 🎯 Why Claude API?

**Advantages over OpenAI:**
- ✅ You already have Anthropic API credits
- ✅ Excellent at following structured formats (perfect for job summaries)
- ✅ Better at handling longer context (can process full job descriptions)
- ✅ More cost-effective with Haiku model for high-volume tasks
- ✅ Strong performance on extraction and summarization tasks

---

## 📦 Installation

```bash
pip install anthropic==0.39.0
```

---

## 🔑 API Key Setup

### Option 1: Environment Variable (Recommended)
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

### Option 2: In Code
```python
from anthropic import Anthropic

client = Anthropic(api_key="your-api-key-here")
```

### Option 3: .env File
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...
```

```python
from dotenv import load_dotenv
import os

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
```

---

## 🚀 Quick Start - Basic Job Summary

```python
from anthropic import Anthropic

client = Anthropic()

def summarize_job(job_title, company, description):
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""Summarize this job for a recruitment sales call:

Title: {job_title}
Company: {company}
Description: {description}

Format:
**Must-Have Skills:** (3-5 bullets)
**Key Requirements:** (2-3 sentences)
**Special Features:** (1 line)"""
            }
        ]
    )
    
    return message.content[0].text

# Usage
summary = summarize_job(
    "Senior Sales Engineer",
    "TechCorp GmbH",
    "Looking for experienced sales engineer with 5+ years..."
)
print(summary)
```

---

## 💰 Model Selection & Pricing

### Claude 3.5 Sonnet (Recommended for Quality)
- **Model:** `claude-3-5-sonnet-20241022`
- **Pricing:** ~$0.015-0.020 per job summary
- **Best for:** High-pain leads (score 80+), important clients
- **Strengths:** Highest quality, best formatting, detailed analysis

### Claude 3.5 Haiku (Recommended for Volume)
- **Model:** `claude-3-5-haiku-20241022`
- **Pricing:** ~$0.005-0.010 per job summary
- **Best for:** Standard leads (score 60-79), high-volume processing
- **Strengths:** Fast, cost-effective, still very good quality

### Cost Comparison for 1000 Jobs/Month

| Strategy | Model Mix | Monthly Cost |
|----------|-----------|--------------|
| All Sonnet | 100% Sonnet | $15-20 |
| All Haiku | 100% Haiku | $5-10 |
| **Mixed (Recommended)** | 80% Haiku, 20% Sonnet | $6-12 |
| Batch Processing | Haiku batches | $3-5 |

**Recommendation:** Use Haiku for most jobs, Sonnet only for high-priority leads (pain score 80+)

---

## 🎨 Prompt Engineering for Job Summaries

### Template 1: Basic Summary (Fast)

```python
def create_basic_prompt(job_data):
    return f"""Extract key details from this job posting:

{job_data['title']} at {job_data['company_name']}
{job_data['description'][:1500]}

Return:
Skills: [comma-separated list]
Requirements: [2 sentences]
Special: [1 line or "None"]

Be concise."""
```

### Template 2: Structured Format (Recommended)

```python
def create_structured_prompt(job_data):
    return f"""You're helping a recruitment agency. Create a call-ready summary.

Job: {job_data['title']}
Company: {job_data['company_name']}
Posted: {job_data['days_open']} days ago
Description:
{job_data['description'][:2000]}

Format exactly as:

**Must-Have Skills:**
- [skill 1]
- [skill 2]
- [skill 3]

**Key Requirements:**
[2-3 sentences about role expectations and responsibilities]

**Special Features:**
[Remote work, equity, unique perks, or "None noted"]

Keep it actionable for a 2-minute sales pitch."""
```

### Template 3: JSON Output (For Programmatic Use)

```python
def create_json_prompt(job_data):
    return f"""Extract job information as JSON (no markdown, no explanations):

Title: {job_data['title']}
Company: {job_data['company_name']}
Description: {job_data['description'][:2000]}

Return ONLY this JSON structure:
{{
    "must_have_skills": ["skill1", "skill2", "skill3"],
    "key_requirements": "2-3 sentence summary",
    "special_features": "details or empty string",
    "seniority": "Junior/Mid/Senior/Lead",
    "tech_stack": ["tech1", "tech2"]
}}"""
```

---

## ⚡ Performance Optimization

### 1. Dynamic Model Selection

```python
def get_model_for_job(pain_score: int) -> str:
    """
    High-value leads get Sonnet, others get Haiku
    """
    if pain_score >= 80:
        return "claude-3-5-sonnet-20241022"
    else:
        return "claude-3-5-haiku-20241022"

def summarize_with_smart_model(job_data):
    model = get_model_for_job(job_data['pain_score'])
    
    message = client.messages.create(
        model=model,
        max_tokens=512,  # Shorter for Haiku
        messages=[...]
    )
    
    return message.content[0].text
```

### 2. Batch Processing (3-5x Cost Reduction)

```python
def summarize_batch(jobs_list):
    """
    Process 5-10 jobs in one API call
    Reduces cost from $0.01/job to $0.002/job
    """
    
    # Combine multiple jobs in one prompt
    batch_prompt = "Summarize these jobs:\n\n"
    for i, job in enumerate(jobs_list, 1):
        batch_prompt += f"JOB {i}: {job['title']} at {job['company_name']}\n"
        batch_prompt += f"{job['description'][:800]}\n\n"
    
    batch_prompt += "For each job, return: Skills: | Requirements: | Special:"
    
    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=2048,
        messages=[{"role": "user", "content": batch_prompt}]
    )
    
    # Parse response by job markers
    return parse_batch_response(message.content[0].text)
```

### 3. Caching (For Similar Job Descriptions)

```python
import hashlib
import json

cache = {}

def summarize_with_cache(job_data):
    """
    Cache summaries to avoid re-processing similar jobs
    """
    
    # Create cache key from job content
    cache_key = hashlib.md5(
        f"{job_data['title']}{job_data['description'][:500]}".encode()
    ).hexdigest()
    
    # Check cache
    if cache_key in cache:
        return cache[cache_key]
    
    # Generate new summary
    summary = generate_summary(job_data)
    
    # Store in cache
    cache[cache_key] = summary
    
    return summary
```

---

## 🛡️ Error Handling & Retry Logic

### Robust Implementation

```python
from anthropic import Anthropic, APIError, RateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential
import time

client = Anthropic()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def summarize_with_retry(job_data):
    """
    Automatic retry on failures with exponential backoff
    """
    try:
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": create_prompt(job_data)
            }]
        )
        return message.content[0].text
        
    except RateLimitError as e:
        print(f"Rate limit hit, waiting...")
        raise  # Trigger retry with backoff
        
    except APIError as e:
        print(f"API error: {e.status_code}")
        raise  # Trigger retry
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Return fallback instead of crashing
        return create_fallback_summary(job_data)

def create_fallback_summary(job_data):
    """
    Basic summary when API fails
    """
    return f"""**Must-Have Skills:**
- See full job description

**Key Requirements:**
{job_data['title']} at {job_data['company_name']}

**Special Features:**
Manual review needed"""
```

---

## 📊 Quality Validation

### Automatic Quality Checks

```python
def validate_summary(summary: str) -> bool:
    """
    Check if summary meets quality standards
    """
    
    checks = {
        'has_skills_section': "Must-Have Skills:" in summary,
        'has_requirements': "Key Requirements:" in summary,
        'has_features': "Special Features:" in summary,
        'min_length': len(summary) >= 100,
        'no_placeholders': "[" not in summary and "TODO" not in summary.upper()
    }
    
    passed = all(checks.values())
    
    if not passed:
        print(f"Quality check failed: {checks}")
    
    return passed

def generate_with_validation(job_data):
    """
    Generate summary and validate quality
    """
    summary = summarize_with_retry(job_data)
    
    if not validate_summary(summary):
        print("Quality check failed, regenerating with Sonnet...")
        # Retry with higher quality model
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[...]
        )
        summary = message.content[0].text
    
    return summary
```

---

## 🔧 Integration with Main Pipeline

### Complete Pipeline Integration

```python
from anthropic import Anthropic
import os

class JobSummarizer:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.cache = {}
    
    def summarize(self, job_data: dict) -> str:
        """
        Main method called by pipeline
        """
        
        # Select appropriate model
        model = self._choose_model(job_data['pain_score'])
        
        # Generate summary
        summary = self._generate_with_retry(job_data, model)
        
        # Validate quality
        if not self._validate(summary):
            summary = self._generate_with_retry(job_data, "claude-3-5-sonnet-20241022")
        
        return summary
    
    def _choose_model(self, pain_score: int) -> str:
        return "claude-3-5-sonnet-20241022" if pain_score >= 80 else "claude-3-5-haiku-20241022"
    
    def _generate_with_retry(self, job_data: dict, model: str) -> str:
        # Implementation with retry logic
        pass
    
    def _validate(self, summary: str) -> bool:
        # Quality validation
        pass

# Usage in main pipeline
summarizer = JobSummarizer()

for job in qualified_jobs:
    job['summary'] = summarizer.summarize({
        'title': job.title,
        'company_name': job.company_name,
        'description': job.description,
        'pain_score': job.pain_score,
        'days_open': job.days_open
    })
```

---

## 📈 Monitoring & Analytics

### Track API Usage

```python
import time
from datetime import datetime

class APIMonitor:
    def __init__(self):
        self.calls = []
        self.total_cost = 0.0
    
    def log_call(self, model: str, input_tokens: int, output_tokens: int):
        """
        Log each API call for cost tracking
        """
        
        # Calculate cost (approximate)
        if "sonnet" in model:
            cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000
        else:  # haiku
            cost = (input_tokens * 0.00025 + output_tokens * 0.00125) / 1000
        
        self.total_cost += cost
        self.calls.append({
            'timestamp': datetime.now(),
            'model': model,
            'cost': cost
        })
    
    def get_stats(self):
        """
        Get usage statistics
        """
        return {
            'total_calls': len(self.calls),
            'total_cost': round(self.total_cost, 2),
            'avg_cost_per_call': round(self.total_cost / len(self.calls), 4) if self.calls else 0,
            'sonnet_calls': sum(1 for c in self.calls if 'sonnet' in c['model']),
            'haiku_calls': sum(1 for c in self.calls if 'haiku' in c['model'])
        }

# Usage
monitor = APIMonitor()

# After each API call
monitor.log_call(model, message.usage.input_tokens, message.usage.output_tokens)

# End of day
print(monitor.get_stats())
# {'total_calls': 150, 'total_cost': 2.45, 'avg_cost_per_call': 0.0163}
```

---

## 🎯 Best Practices

### 1. Temperature Settings

```python
# For consistent formatting (recommended)
temperature=0.3

# For more creative descriptions
temperature=0.7

# For maximum consistency
temperature=0.0
```

### 2. Token Limits

```python
# Short summaries (cost-effective)
max_tokens=512

# Standard summaries (recommended)
max_tokens=1024

# Detailed summaries
max_tokens=2048
```

### 3. Prompt Length

```python
# Keep descriptions under 2000 characters
description = job_data['description'][:2000]

# For very long descriptions, summarize first
if len(description) > 3000:
    description = f"{description[:1500]}... [truncated] ...{description[-500:]}"
```

---

## 🚨 Common Issues & Solutions

### Issue 1: Rate Limiting
```python
# Solution: Add exponential backoff
from tenacity import retry, wait_exponential
@retry(wait=wait_exponential(multiplier=1, min=2, max=30))
def api_call():
    return client.messages.create(...)
```

### Issue 2: Inconsistent Formatting
```python
# Solution: Use stricter prompts with examples
prompt = """Format EXACTLY like this example:

**Must-Have Skills:**
- Python programming
- 5+ years experience

**Key Requirements:**
Senior developer needed.

Now format this job:
{job_data}"""
```

### Issue 3: Missing API Key
```python
# Solution: Add validation
import os

if not os.getenv("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY not set in environment")
```

---

## 📚 Additional Resources

- **Anthropic Documentation:** https://docs.anthropic.com/
- **API Reference:** https://docs.anthropic.com/en/api/messages
- **Pricing:** https://www.anthropic.com/api#pricing
- **Rate Limits:** https://docs.anthropic.com/en/api/rate-limits

---

## ✅ Quick Checklist

Before going to production:

- [ ] API key configured in environment
- [ ] Model selection logic implemented (Haiku for volume, Sonnet for quality)
- [ ] Retry logic with exponential backoff
- [ ] Quality validation for all summaries
- [ ] Error handling with fallback summaries
- [ ] Cost monitoring and logging
- [ ] Caching for duplicate jobs (optional but recommended)
- [ ] Batch processing implemented (if processing 100+ jobs)
- [ ] Test with 10-20 sample jobs
- [ ] Verify costs are within budget ($30-100/month target)

---

**Version:** 1.0  
**Last Updated:** January 29, 2026  
**Status:** Ready for Integration

**Need Help?** See `claude_api_examples.py` for complete working examples
