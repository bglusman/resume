#!/usr/bin/env python3
"""
Advanced AI Resume Customizer
Integrates with the existing resume generator to create job-specific customizations
"""

import json
import os
import sys
import yaml
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import openai
import argparse
from datetime import datetime

class AIResumeCustomizer:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key"""
        self.client = openai.OpenAI(
            api_key=api_key or os.getenv('OPENAI_API_KEY')
        )
        if not self.client.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
    
    def load_resume_data(self, data_dir: Path) -> Dict[str, Any]:
        """Load all resume data from markdown files"""
        data = {}
        
        # Load each section
        sections = ['meta', 'work_experience', 'projects', 'skills', 'education']
        
        for section in sections:
            section_file = data_dir / f"{section}.md"
            if section_file.exists():
                with open(section_file, 'r') as f:
                    content = f.read()
                    # Extract YAML frontmatter
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 2:
                            data[section] = yaml.safe_load(parts[1])
        
        return data
    
    def analyze_job_description(self, job_desc: str) -> Dict[str, Any]:
        """Analyze job description and extract key information"""
        prompt = f"""
        Analyze this job description and extract key information for resume optimization:
        
        Job Description:
        {job_desc}
        
        Extract and return as JSON:
        {{
            "required_skills": ["skill1", "skill2", ...],
            "preferred_skills": ["skill1", "skill2", ...],
            "key_responsibilities": ["resp1", "resp2", ...],
            "company_values": ["value1", "value2", ...],
            "experience_level": "entry/mid/senior/executive",
            "industry_keywords": ["keyword1", "keyword2", ...],
            "role_focus": "technical/leadership/management/individual_contributor"
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert resume optimizer. Extract key information from job descriptions to help tailor resumes effectively."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        return json.loads(response.choices[0].message.content)
    
    def customize_work_experience(self, work_exp: List[Dict], job_analysis: Dict) -> List[Dict]:
        """Customize work experience descriptions to match job requirements"""
        customized = []
        
        for exp in work_exp:
            prompt = f"""
            Rewrite this work experience to better align with the target job requirements.
            Keep all facts accurate but emphasize relevant aspects.
            
            Original Role: {exp.get('role', '')}
            Company: {exp.get('company', '')}
            Original Description: {exp.get('description', '')}
            
            Target Job Requirements:
            - Required Skills: {', '.join(job_analysis.get('required_skills', []))}
            - Key Responsibilities: {', '.join(job_analysis.get('key_responsibilities', []))}
            - Role Focus: {job_analysis.get('role_focus', '')}
            
            Return a JSON object with:
            {{
                "description": "customized description",
                "suggested_tags": ["tag1", "tag2", ...]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional resume writer. Optimize work experiences to match job requirements while keeping them truthful."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            customization = json.loads(response.choices[0].message.content)
            
            # Create customized experience entry
            custom_exp = exp.copy()
            custom_exp['description'] = customization['description']
            
            # Merge existing tags with suggested tags
            existing_tags = set(exp.get('tags', []))
            suggested_tags = set(customization.get('suggested_tags', []))
            custom_exp['tags'] = list(existing_tags.union(suggested_tags))
            
            customized.append(custom_exp)
        
        return customized
    
    def generate_custom_summary(self, current_summary: str, job_analysis: Dict) -> str:
        """Generate a customized professional summary"""
        prompt = f"""
        Customize this professional summary to align with the target job:
        
        Current Summary: {current_summary}
        
        Target Job Focus:
        - Required Skills: {', '.join(job_analysis.get('required_skills', [])[:5])}
        - Role Focus: {job_analysis.get('role_focus', '')}
        - Experience Level: {job_analysis.get('experience_level', '')}
        
        Create a 2-3 sentence professional summary that emphasizes relevant skills and experience.
        Keep it authentic and professional.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional resume writer specializing in compelling summary statements."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        
        return response.choices[0].message.content.strip()
    
    def suggest_skill_optimization(self, skills: Dict, job_analysis: Dict) -> Dict:
        """Suggest skill reorganization and additions based on job requirements"""
        prompt = f"""
        Analyze these current skills and suggest optimizations for the target job:
        
        Current Skills: {json.dumps(skills, indent=2)}
        
        Target Job Requirements:
        - Required Skills: {', '.join(job_analysis.get('required_skills', []))}
        - Preferred Skills: {', '.join(job_analysis.get('preferred_skills', []))}
        
        Return JSON with:
        {{
            "skills_to_emphasize": ["skill1", "skill2", ...],
            "missing_relevant_skills": ["skill1", "skill2", ...],
            "recommended_categories": [
                {{
                    "name": "category_name",
                    "items": ["skill1", "skill2", ...]
                }}
            ]
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a resume optimization expert. Analyze skills and suggest improvements for job targeting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    def create_custom_resume_variant(self, data_dir: Path, job_desc_file: Path, output_tag: str):
        """Create a customized resume variant for a specific job"""
        # Load existing resume data
        resume_data = self.load_resume_data(data_dir)
        
        # Load job description
        with open(job_desc_file, 'r') as f:
            job_description = f.read()
        
        # Analyze job
        print("Analyzing job description...")
        job_analysis = self.analyze_job_description(job_description)
        
        # Create custom directory for this job
        custom_dir = data_dir / f"custom_{output_tag}"
        custom_dir.mkdir(exist_ok=True)
        
        # Save job analysis
        with open(custom_dir / "job_analysis.json", 'w') as f:
            json.dump(job_analysis, f, indent=2)
        
        # Customize work experience
        if 'work_experience' in resume_data:
            print("Customizing work experience...")
            original_items = resume_data['work_experience'].get('items', [])
            customized_items = self.customize_work_experience(original_items, job_analysis)
            
            # Add custom tag to all items
            for item in customized_items:
                item['tags'] = item.get('tags', []) + [output_tag]
            
            # Create custom work experience file
            custom_work_exp = {
                'work_experience': {
                    'items': customized_items
                }
            }
            
            with open(custom_dir / "work_experience.md", 'w') as f:
                f.write("---\n")
                yaml.dump(custom_work_exp, f, default_flow_style=False)
                f.write("---\n")
        
        # Customize summary
        if 'meta' in resume_data:
            print("Generating custom summary...")
            current_summary = resume_data['meta'].get('summary', '')
            custom_summary = self.generate_custom_summary(current_summary, job_analysis)
            
            # Create custom meta file
            custom_meta = resume_data['meta'].copy()
            custom_meta['summary'] = custom_summary
            
            with open(custom_dir / "meta.md", 'w') as f:
                f.write("---\n")
                yaml.dump(custom_meta, f, default_flow_style=False)
                f.write("---\n")
        
        # Copy other files (education, skills, projects) with custom tags
        for section in ['education', 'skills', 'projects']:
            if section in resume_data:
                section_data = resume_data[section].copy()
                
                # Add custom tags to projects if they exist
                if section == 'projects' and 'items' in section_data:
                    for item in section_data['items']:
                        item['tags'] = item.get('tags', []) + [output_tag]
                
                with open(custom_dir / f"{section}.md", 'w') as f:
                    f.write("---\n")
                    yaml.dump({section: section_data}, f, default_flow_style=False)
                    f.write("---\n")
        
        # Generate skill suggestions
        if 'skills' in resume_data:
            skill_suggestions = self.suggest_skill_optimization(resume_data['skills'], job_analysis)
            with open(custom_dir / "skill_suggestions.json", 'w') as f:
                json.dump(skill_suggestions, f, indent=2)
        
        print(f"Custom resume variant created in: {custom_dir}")
        print(f"To generate resume: ./generate_resume.sh --focus {output_tag} {custom_dir} resume_{output_tag}.pdf templates/")
        print(f"To generate ATS version: ./generate_ats.sh --focus {output_tag} {custom_dir} resume_{output_tag}.txt")
        
        return custom_dir

def main():
    parser = argparse.ArgumentParser(description="AI-powered resume customizer")
    parser.add_argument("data_dir", help="Directory containing resume data")
    parser.add_argument("job_description", help="File containing job description")
    parser.add_argument("output_tag", help="Tag name for the custom variant (e.g., 'company_role')")
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    job_desc_file = Path(args.job_description)
    
    if not data_dir.exists():
        print(f"Error: Data directory {data_dir} not found")
        sys.exit(1)
    
    if not job_desc_file.exists():
        print(f"Error: Job description file {job_desc_file} not found")
        sys.exit(1)
    
    try:
        customizer = AIResumeCustomizer(api_key=args.api_key)
        customizer.create_custom_resume_variant(data_dir, job_desc_file, args.output_tag)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()