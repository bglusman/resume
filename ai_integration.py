#!/usr/bin/env python3
"""
AI Integration for Resume Customization
Helps tailor resume content based on job descriptions using LLMs
"""

import json
import os
import sys
from typing import Dict, List, Optional
import openai
from pathlib import Path

class ResumeCustomizer:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key (or use environment variable)"""
        self.client = openai.OpenAI(
            api_key=api_key or os.getenv('OPENAI_API_KEY')
        )
    
    def analyze_job_description(self, job_desc: str) -> Dict[str, List[str]]:
        """Extract key skills, requirements, and keywords from job description"""
        prompt = f"""
        Analyze this job description and extract:
        1. Required technical skills
        2. Soft skills mentioned
        3. Key responsibilities/duties
        4. Industry keywords
        5. Experience level indicators
        
        Job Description:
        {job_desc}
        
        Return as JSON with keys: technical_skills, soft_skills, responsibilities, keywords, experience_level
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a resume optimization expert. Extract key information from job descriptions to help tailor resumes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    def customize_bullet_points(self, current_bullets: List[str], job_analysis: Dict, role_context: str) -> List[str]:
        """Customize bullet points to better match job requirements"""
        prompt = f"""
        Given these current resume bullet points for {role_context} and the job analysis, 
        rewrite the bullet points to better match the job requirements while keeping them truthful.
        Focus on highlighting relevant keywords and experiences.
        
        Current bullet points:
        {chr(10).join(f'• {bullet}' for bullet in current_bullets)}
        
        Job requirements focus on:
        - Technical skills: {', '.join(job_analysis.get('technical_skills', []))}
        - Responsibilities: {', '.join(job_analysis.get('responsibilities', []))}
        - Keywords: {', '.join(job_analysis.get('keywords', []))}
        
        Return 3-5 optimized bullet points that emphasize relevant experience.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional resume writer. Optimize bullet points to match job requirements while keeping them truthful and impactful."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        
        # Parse bullet points from response
        content = response.choices[0].message.content
        bullets = [line.strip('• ').strip() for line in content.split('\n') if line.strip().startswith('•')]
        return bullets
    
    def generate_custom_summary(self, current_summary: str, job_analysis: Dict) -> str:
        """Generate a customized summary/objective based on job requirements"""
        prompt = f"""
        Customize this professional summary to better align with the job requirements:
        
        Current summary: {current_summary}
        
        Job focuses on:
        - Technical skills: {', '.join(job_analysis.get('technical_skills', [])[:5])}
        - Key responsibilities: {', '.join(job_analysis.get('responsibilities', [])[:3])}
        - Experience level: {job_analysis.get('experience_level', 'Not specified')}
        
        Rewrite the summary to emphasize relevant skills and experience while keeping it authentic.
        Keep it to 2-3 sentences, professional tone.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional resume writer. Create compelling summaries that align with job requirements."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        
        return response.choices[0].message.content.strip()

def main():
    if len(sys.argv) < 2:
        print("Usage: python ai_integration.py <job_description_file>")
        sys.exit(1)
    
    job_desc_file = sys.argv[1]
    
    if not os.path.exists(job_desc_file):
        print(f"Job description file not found: {job_desc_file}")
        sys.exit(1)
    
    with open(job_desc_file, 'r') as f:
        job_description = f.read()
    
    customizer = ResumeCustomizer()
    analysis = customizer.analyze_job_description(job_description)
    
    print("Job Analysis:")
    print(json.dumps(analysis, indent=2))
    
    # Example of how to use with existing data
    print("\nTo integrate with your resume generator:")
    print("1. Run this script on a job description")
    print("2. Use the analysis to create custom tags")
    print("3. Generate tailored bullet points")
    print("4. Create job-specific resume variants")

if __name__ == "__main__":
    main()