from typing import Dict, List, Optional
import json
from datetime import datetime
import os
import pathlib
from dotenv import load_dotenv
from openai import OpenAI

class CompanyIntelligenceService:
    def __init__(self):
        """Initialize the service with Perplexity API"""
        # Load environment variables
        env_path = pathlib.Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        
        # Get Perplexity API key
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError("Please set the PERPLEXITY_API_KEY environment variable")
            
        # Initialize Perplexity client
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai"
        )

    def get_company_intelligence(self, 
                               industry: Optional[str] = None,
                               company_name: Optional[str] = None,
                               product: Optional[str] = None,
                               company_stage: Optional[str] = None,
                               geography: Optional[str] = None,
                               funding_stage: Optional[str] = None
                               ) -> str:
        """Get detailed company intelligence based on provided criteria"""
        
        # Get company data from Perplexity
        prompt = self.construct_perplexity_prompt(
            industry, company_name, product, 
            company_stage, geography, funding_stage
        )
        companies_data = self.get_perplexity_data(prompt)
        
        # Parse and validate the response
        try:
            companies = json.loads(companies_data)
        except json.JSONDecodeError:
            print("Error: Received non-JSON response from Perplexity")
            companies = []
        
        return json.dumps({
            "companies": companies,
            "search_criteria": {
                "industry": industry,
                "company_name": company_name,
                "product": product,
                "company_stage": company_stage,
                "geography": geography,
                "funding_stage": funding_stage
            },
            "total_companies": len(companies),
            "generated_at": datetime.now().isoformat()
        }, indent=2)

    def construct_perplexity_prompt(self,
                                  industry: Optional[str],
                                  company_name: Optional[str],
                                  product: Optional[str],
                                  company_stage: Optional[str],
                                  geography: Optional[str],
                                  funding_stage: Optional[str]) -> str:
        """Construct a targeted prompt for Perplexity"""
        
        # Build search criteria
        criteria_parts = []
        
        # Industry criteria
        if industry:
            criteria_parts.append(f"in the {industry} industry")
            
        # Company name criteria
        if company_name:
            criteria_parts.append(f"including or similar to {company_name}")
            
        # Product criteria    
        if product:
            criteria_parts.append(f"related to {product}")
            
        # Company stage criteria
        if company_stage:
            stage_descriptions = {
                "startup": "early-stage startups",
                "smb": "small and medium-sized businesses",
                "enterprise": "large enterprise companies",
                "growing": "high-growth companies"
            }
            if company_stage in stage_descriptions:
                criteria_parts.append(f"focusing on {stage_descriptions[company_stage]}")
                
        # Geographic criteria
        if geography:
            criteria_parts.append(f"located in {geography}")
            
        # Funding stage criteria
        if funding_stage:
            criteria_parts.append(f"at {funding_stage} funding stage")
            
        criteria = " ".join(criteria_parts) if criteria_parts else "in the technology sector"
        
        # Construct the prompt
        prompt = f"""Return only a JSON array of companies {criteria}. Each company should be a flat object with these exact fields:

{{
  "name": "Example Company Inc",
  "website": "www.example.com",
  "description": "Brief company description",
  "headquarters": "San Francisco, USA",
  "employee_count": "500",
  "funding_status": "Series A",
  "product_list": "Product1, Product2, Product3",
  "competitor_list": "Competitor1, Competitor2, Competitor3",
  "founded_year": "2020",
  "revenue_range": "$10M-$50M"
}}

Important instructions:
1. Return ONLY a JSON array of objects with the exact structure shown above
2. Do not use nested arrays or objects
3. Use comma-separated strings for lists (product_list and competitor_list)
4. Return only factual, verifiable information
5. Limit to 5 most relevant companies
6. The response must be valid JSON with no additional text
7. Do not include any markdown formatting or explanation"""
        return prompt

    def get_perplexity_data(self, prompt: str) -> str:
        """Get company data from Perplexity API"""
        try:
            print(f"Calling Perplexity API with prompt: {prompt}")
            # Prepare the messages
            messages = [
                {
                    "role": "system",
                    "content": "You are a company research assistant. You MUST return ONLY valid JSON arrays with no additional text."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Make the API call
            response = self.client.chat.completions.create(
                model="llama-3.1-sonar-small-128k-online",
                messages=messages,
                temperature=0.1  # Lower temperature for more consistent JSON
            )
            
            # Extract the response content
            content = response.choices[0].message.content.strip()
            
            # Clean up the response to ensure it's valid JSON
            # Remove any markdown code block indicators
            content = content.replace("```json", "").replace("```", "").strip()
            
            # Validate JSON
            json.loads(content)  # This will raise an exception if invalid JSON
            
            return content
            
        except Exception as e:
            print(f"Error calling Perplexity API: {e}")
            return "[]"

if __name__ == "__main__":
    service = CompanyIntelligenceService()
    
    # Test different search scenarios
    test_cases = [
        {
            "industry": "retail",
            "company_name": None,
            "product": None,
            "company_stage": "startup",
            "geography": "Texas",
            "funding_stage": ""
        }
    ]
    
    for case in test_cases:
        print(f"\nTesting with parameters: {case}")
        result = service.get_company_intelligence(**case)
        print(result)