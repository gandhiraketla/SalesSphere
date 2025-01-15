from crewai.tools import BaseTool
from typing import Dict, Any, Optional
from pydantic import Field, ConfigDict
import sys
import os
import json

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from services.company_research_service import CompanyIntelligenceService

class CompanyIntelligenceTool(BaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = "Company Intelligence Search"
    description: str = (
        "Search for company intelligence using Perplexity AI. "
        "Can search by industry, company name, product, company stage, geography, and funding stage. "
        "Returns detailed company information including description, headquarters, funding status, and more."
    )
    service: CompanyIntelligenceService = Field(default_factory=CompanyIntelligenceService)

    def _run(
        self, 
        industry: Optional[str] = None,
        company_stage: Optional[str] = None,
        geography: Optional[str] = None,
        funding_stage: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute the company intelligence search using Perplexity AI.
        
        Args:
            industry (str, optional): The industry to search in (e.g., "healthcare", "retail")
            company_stage (str, optional): Stage of company ("startup", "smb", "enterprise", "growing")
            geography (str, optional): Location to search in (e.g., "Texas", "Europe")
            funding_stage (str, optional): Funding stage to search for (e.g., "seed", "series A")
        
        Returns:
            Dict[str, Any]: The formatted company intelligence results.
        """
        try:
            # Validate company_stage if provided
            valid_stages = ["startup", "smb", "enterprise", "growing"]
            if company_stage and company_stage.lower() not in valid_stages:
                raise ValueError(
                    f"Invalid company_stage. Must be one of: {', '.join(valid_stages)}"
                )

            # Clean and prepare parameters
            clean_params = {
                "industry": industry,
                "company_stage": company_stage.lower() if company_stage else None,
                "geography": geography,
                "funding_stage": funding_stage,
                "company_name": None,  # Not used in this version
                "product": None        # Not used in this version
            }

            # Ensure at least one search parameter is provided
            if not any(clean_params.values()):
                raise ValueError(
                    "At least one search parameter must be provided "
                    "(industry, company_stage, geography, or funding_stage)"
                )

            # Perform the company intelligence search
            result = self.service.get_company_intelligence(**clean_params)
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "search_params": clean_params if 'clean_params' in locals() else {
                    "industry": industry,
                    "company_stage": company_stage,
                    "geography": geography,
                    "funding_stage": funding_stage
                }
            }

    def _format_result(self, result: str) -> Dict[str, Any]:
        """Format the result for better readability"""
        try:
            # Parse JSON string to dict if it's a string
            if isinstance(result, str):
                result = json.loads(result)
            return result
        except Exception as e:
            return {"error": f"Error formatting result: {str(e)}", "raw_result": result}

if __name__ == "__main__":
    # Example usage
    tool = CompanyIntelligenceTool()
    
    # Test cases
    test_cases = [
        {
            "industry": "retail",
            "company_stage": "startup",
            "geography": "California",
            "funding_stage": ""
        }
    ]
    
    for case in test_cases:
        print(f"\nTesting with parameters: {case}")
        result = tool._run(**case)  # Note the ** to unpack the dictionary
        print("Company Intelligence Results:")
        print(result)