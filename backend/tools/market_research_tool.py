from crewai.tools import BaseTool
from typing import Dict, Any, Optional
from pydantic import Field, ConfigDict
import sys
import os

# Ensure parent directory is in the path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the Market Research Service
from services.market_research_service import MarketResearchService

class MarketResearchTool(BaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = "Market Research Intelligence"
    description: str = (
        "Conduct comprehensive market research using Perplexity AI. "
        "Can search by industry, product, or specific technology. "
        "Returns detailed market insights as a string."
    )
    service: MarketResearchService = Field(default_factory=MarketResearchService)

    def _run(
        self, 
        industry: Optional[str] = None,
        product: Optional[str] = None
    ) -> str:
        """
        Execute the market research intelligence search.
        
        Args:
            industry (str, optional): The target industry
            product (str, optional): Specific product or technology
        
        Returns:
            str: Market research insights
        """
        # Validate input
        if not industry and not product:
            raise ValueError(
                "At least one search parameter must be provided "
                "(industry or product)"
            )

        # Perform market research
        return self.service.generate_market_research(
            industry=industry, 
            product=product
        )

if __name__ == "__main__":
    # Example usage
    tool = MarketResearchTool()
    
    # Test cases
    test_cases = [
        
        {
            "industry": "retail",
            "product": "AI In Customer analytics"
        }
    ]
    
    for case in test_cases:
        print(f"\nTesting with parameters: {case}")
        result = tool._run(**case)  # Note the ** to unpack the dictionary
        print("Market Research Results:")
        print(result)