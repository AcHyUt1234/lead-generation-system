"""
Job Summarization with Anthropic Claude API
Detailed implementation example for the lead generation system
"""

import os
from anthropic import Anthropic
from typing import Dict, List
import json

# Initialize the Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


# ============================================================================
# BASIC SUMMARIZATION
# ============================================================================

def generate_job_summary_basic(job_data: Dict) -> str:
    """
    Basic job summarization using Claude 3.5 Sonnet
    
    Args:
        job_data: Dictionary with job details (title, company, description, etc.)
        
    Returns:
        Formatted job summary string
    """
    
    prompt = f"""You are helping a recruitment agency create concise summaries for sales calls.

Given this job vacancy:
- Title: {job_data['title']}
- Company: {job_data['company_name']}
- Posted: {job_data['days_open']} days ago
- Description: {job_data['description'][:2000]}

Create a structured summary in this exact format:

**Must-Have Skills:**
- [Skill 1]
- [Skill 2]
- [Skill 3]

**Key Requirements:**
[2-3 sentences describing the role expectations]

**Special Features:**
[Any standout details like remote work, equity, unique perks, or reporting structure]

Keep it concise and focused on what a recruiter needs for an initial sales call."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        temperature=0.3,  # Lower temperature for more consistent formatting
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text


# ============================================================================
# STRUCTURED OUTPUT WITH JSON
# ============================================================================

def generate_job_summary_structured(job_data: Dict) -> Dict:
    """
    Generate structured job summary as JSON for easier parsing
    
    This is more robust for programmatic use and ensures consistent structure
    """
    
    prompt = f"""Extract key information from this job posting for a recruitment sales call.

Job Details:
Title: {job_data['title']}
Company: {job_data['company_name']}
Description: {job_data['description'][:2000]}

Return ONLY valid JSON with this structure (no markdown, no explanations):
{{
    "must_have_skills": [
        "skill 1",
        "skill 2",
        "skill 3"
    ],
    "key_requirements": "2-3 sentence summary of role expectations",
    "special_features": "Any standout details or leave empty if none",
    "seniority_level": "Junior/Mid/Senior/Lead/Executive",
    "tech_stack": ["technology 1", "technology 2"],
    "sales_type": "Enterprise/SMB/Transactional/Consultative"
}}"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        temperature=0.2,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Parse the JSON response
    try:
        result = json.loads(message.content[0].text)
        return result
    except json.JSONDecodeError:
        # Fallback if Claude returns malformed JSON
        return {
            "must_have_skills": [],
            "key_requirements": message.content[0].text,
            "special_features": "",
            "error": "Failed to parse JSON"
        }


# ============================================================================
# BATCH PROCESSING FOR COST EFFICIENCY
# ============================================================================

def generate_summaries_batch(jobs: List[Dict], model: str = "claude-3-5-haiku-20241022") -> List[str]:
    """
    Process multiple jobs in a single API call for better cost efficiency
    
    Uses Claude 3.5 Haiku (cheaper) for high-volume processing
    Can process 5-10 jobs per API call depending on description length
    
    Note: This approach trades some quality for significant cost savings
    """
    
    # Prepare batch prompt with multiple jobs
    jobs_text = ""
    for i, job in enumerate(jobs, 1):
        jobs_text += f"""
Job {i}:
Title: {job['title']}
Company: {job['company_name']}
Description: {job['description'][:1000]}

---
"""

    prompt = f"""Summarize these {len(jobs)} job postings for recruitment sales calls.

{jobs_text}

For EACH job, provide:
1. Top 3 must-have skills
2. 2-sentence key requirements
3. Any special features

Format:
JOB 1:
Skills: [comma-separated]
Requirements: [2 sentences]
Special: [1 line or "None"]

JOB 2:
[same format]

Keep each summary very concise."""

    message = client.messages.create(
        model=model,
        max_tokens=2048,
        temperature=0.3,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Parse the batch response
    response_text = message.content[0].text
    
    # Split by job markers
    summaries = []
    job_sections = response_text.split("JOB ")[1:]  # Skip first empty split
    
    for section in job_sections:
        summaries.append(section.strip())
    
    return summaries


# ============================================================================
# COST OPTIMIZATION STRATEGIES
# ============================================================================

def choose_model_by_pain_score(pain_score: int) -> str:
    """
    Select appropriate Claude model based on lead quality
    
    High-value leads get better quality (Sonnet)
    Lower-value leads use cheaper model (Haiku)
    """
    if pain_score >= 80:
        # High-pain leads: Use Sonnet for best quality
        return "claude-3-5-sonnet-20241022"
    else:
        # Standard leads: Use Haiku for cost efficiency
        return "claude-3-5-haiku-20241022"


def generate_summary_cost_optimized(job_data: Dict) -> str:
    """
    Cost-optimized summarization that balances quality and cost
    """
    
    # Select model based on job importance
    model = choose_model_by_pain_score(job_data.get('pain_score', 60))
    
    # Shorter prompt to reduce token usage
    prompt = f"""Summarize this sales job for recruiters:

{job_data['title']} at {job_data['company_name']}
{job_data['description'][:1500]}

Format:
Skills: [3 key skills]
Requirements: [2 sentences]
Special: [1 line]"""

    message = client.messages.create(
        model=model,
        max_tokens=512,  # Reduced from 1024 to save costs
        temperature=0.3,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text


# ============================================================================
# ERROR HANDLING AND RETRY LOGIC
# ============================================================================

from tenacity import retry, stop_after_attempt, wait_exponential
import anthropic

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def generate_summary_with_retry(job_data: Dict) -> str:
    """
    Generate summary with automatic retry on failures
    
    Handles:
    - Rate limiting (429 errors)
    - Network issues
    - Temporary API outages
    """
    try:
        return generate_job_summary_basic(job_data)
        
    except anthropic.RateLimitError:
        print(f"Rate limit hit for {job_data['title']}, retrying...")
        raise  # Trigger retry
        
    except anthropic.APIError as e:
        print(f"API error: {e}")
        raise  # Trigger retry
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Return fallback summary instead of failing
        return f"""**Must-Have Skills:**
- [Error generating skills]

**Key Requirements:**
{job_data['title']} role at {job_data['company_name']}. See full job description for details.

**Special Features:**
Manual review needed"""


# ============================================================================
# QUALITY VALIDATION
# ============================================================================

def validate_summary_quality(summary: str) -> bool:
    """
    Check if generated summary meets quality standards
    
    Returns True if summary is acceptable, False if needs regeneration
    """
    
    # Check for required sections
    required_sections = ["Must-Have Skills:", "Key Requirements:", "Special Features:"]
    has_all_sections = all(section in summary for section in required_sections)
    
    # Check minimum length
    min_length = 100
    is_long_enough = len(summary) >= min_length
    
    # Check for placeholder text
    placeholder_phrases = [
        "[Extract from description]",
        "[Error generating]",
        "[skill 1]",
        "[Fill in]"
    ]
    has_placeholders = any(phrase in summary for phrase in placeholder_phrases)
    
    return has_all_sections and is_long_enough and not has_placeholders


# ============================================================================
# COMPLETE PIPELINE INTEGRATION
# ============================================================================

def process_job_with_summary(job_data: Dict) -> Dict:
    """
    Complete processing: generate and validate summary
    
    This is the recommended function to use in the main pipeline
    """
    
    # Step 1: Generate summary
    try:
        summary = generate_summary_with_retry(job_data)
    except Exception as e:
        print(f"Failed to generate summary after retries: {e}")
        summary = create_fallback_summary(job_data)
    
    # Step 2: Validate quality
    if not validate_summary_quality(summary):
        print(f"Summary quality check failed for {job_data['title']}, regenerating...")
        try:
            # Try once more with higher quality model
            summary = generate_summary_structured(job_data)
            summary = format_structured_to_text(summary)
        except:
            summary = create_fallback_summary(job_data)
    
    # Step 3: Add to job data
    job_data['job_summary'] = summary
    
    return job_data


def create_fallback_summary(job_data: Dict) -> str:
    """
    Create a basic summary when API fails
    """
    return f"""**Must-Have Skills:**
- See full job description

**Key Requirements:**
{job_data['title']} position at {job_data['company_name']}. Posted {job_data.get('days_open', 'recently')} days ago. Review full posting for detailed requirements.

**Special Features:**
Manual review recommended for this vacancy."""


def format_structured_to_text(structured_data: Dict) -> str:
    """
    Convert structured JSON output to formatted text
    """
    skills = '\n'.join([f"- {skill}" for skill in structured_data.get('must_have_skills', [])])
    
    return f"""**Must-Have Skills:**
{skills}

**Key Requirements:**
{structured_data.get('key_requirements', 'See job description')}

**Special Features:**
{structured_data.get('special_features', 'None noted')}"""


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    
    # Example job data
    sample_job = {
        'title': 'Senior Sales Engineer',
        'company_name': 'TechCorp GmbH',
        'days_open': 45,
        'pain_score': 85,
        'description': """
        We are seeking an experienced Senior Sales Engineer to join our growing team.
        
        Requirements:
        - 5+ years in technical sales, preferably SaaS
        - Deep understanding of API integrations and cloud architecture
        - Experience with enterprise clients (€1M+ deals)
        - Fluent in German and English
        - Strong presentation and communication skills
        
        Responsibilities:
        - Lead technical pre-sales discussions
        - Create POCs and demos
        - Work closely with product team
        - Support sales team in complex deals
        
        We offer:
        - Competitive salary + uncapped commission
        - Remote-friendly (2 days/week in office)
        - Professional development budget
        - Modern tech stack
        """
    }
    
    print("=" * 60)
    print("EXAMPLE 1: Basic Summarization")
    print("=" * 60)
    summary = generate_job_summary_basic(sample_job)
    print(summary)
    
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Structured JSON Output")
    print("=" * 60)
    structured = generate_job_summary_structured(sample_job)
    print(json.dumps(structured, indent=2))
    
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Cost-Optimized (Haiku for low-priority)")
    print("=" * 60)
    sample_job['pain_score'] = 65  # Lower score = cheaper model
    cost_optimized = generate_summary_cost_optimized(sample_job)
    print(cost_optimized)
    
    print("\n" + "=" * 60)
    print("COST COMPARISON")
    print("=" * 60)
    print("Sonnet (high quality): ~$0.015-0.020 per job")
    print("Haiku (cost efficient): ~$0.005-0.010 per job")
    print("Batch processing: ~$0.003-0.005 per job")
    print("\nFor 1000 jobs/month:")
    print("  Sonnet only: $15-20/month")
    print("  Haiku only: $5-10/month")
    print("  Mixed (80% Haiku, 20% Sonnet): $6-12/month")
    print("  Batch processing: $3-5/month")
