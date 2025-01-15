import sys
import os
import json
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from crewai import Agent, Task, Crew,LLM,Process
from tools.company_intelligence_tool import CompanyIntelligenceTool
from tools.market_research_tool import MarketResearchTool
class ResearchCrew:
    def __init__(self, task_callback=None):
        self.task_callback = task_callback
        
        # Initialize LLM
        self.llm = LLM(
            model="gpt-4",
            temperature=0.8,
            max_tokens=1000,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            stop=["END"],
            seed=42
        )
        
        # Initialize everything
        self._initialize_agents()
        self._initialize_tasks()

    def _on_task_complete(self, task_output) -> None:
        """Task completion callback handling both string outputs and task objects"""
        if self.task_callback:
            if isinstance(task_output, str):
                # If it's a direct string output
                self.task_callback("Task completed with output")
            else:
                # If it's a task object
                agent_name = getattr(task_output, 'agent', None)
                if agent_name and hasattr(agent_name, 'role'):
                    self.task_callback(f"{agent_name.role} has completed their task")
                else:
                    self.task_callback("Task completed")

    def _initialize_agents(self) -> None:
        """Initialize all agents"""
        # Supervisor Agent
        self.supervisor_agent = Agent(
            role="Research Supervisor",
            goal="Coordinate and oversee the research and outreach process",
            backstory=(
                "You are a seasoned project manager with expertise in coordinating "
                "complex research and outreach campaigns. You ensure all team members "
                "work efficiently and maintain high quality standards."
            ),
            llm=self.llm,
            allow_delegation=True,
            verbose=True
        )

        # Company Research Agent
        self.company_research_agent = Agent(
            role="Company Research Specialist",
            goal="Conduct comprehensive research on target companies",
            backstory=(
                "You are an expert business analyst with a keen eye for detail "
                "and a deep understanding of various industries. Your specialty "
                "lies in gathering and analyzing company information from multiple "
                "sources to provide actionable insights."
            ),
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
            tools=[CompanyIntelligenceTool()]
        )

        # Market Research Agent
        self.market_trends_agent = Agent(
            role="Market Trends Analyst",
            goal="Analyze current market trends and opportunities",
            backstory=(
                "You are an experienced market research analyst with deep knowledge "
                "of industry trends and market dynamics. Your expertise lies in "
                "identifying emerging patterns and market opportunities."
            ),
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
            tools=[MarketResearchTool()]
        )

        # Outreach Agent
        self.outreach_agent = Agent(
            role="Outreach Specialist",
            goal="Create compelling, personalized outreach emails",
            backstory=(
                "You are a skilled B2B communication expert who excels at crafting "
                "personalized, engaging outreach messages. You combine company research "
                "and market insights to create compelling value propositions."
            ),
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )

    def _initialize_tasks(self) -> None:
        """Initialize all tasks"""
        # Company Research Task
        self.company_research_task = Task(
            description=(
                "Research and analyze companies based on the following criteria:\n"
                "- Industry: {industry}\n"
                "- Company Stage: {company_stage}\n"
                "- Geography: {geography}\n"
                "- Funding Stage: {funding_stage}\n\n"
                "For the matching companies, analyze:\n"
                "1. Business model and market fit\n"
                "2. Growth potential and market opportunity\n"
                "3. Team composition and experience\n"
                "4. Financial health and funding history\n"
                "5. Competitive advantages and unique value propositions\n"
                "6. Search each company only once\n"
                "7. If direct information isn't available, note what is known from competitor data\n"
                "8. Move on to the next company after one search attempt"
            ),
            expected_output=(
                "A detailed analytical report containing:\n"
                "For each company:\n"
                "- Company Name\n"
                "- Website\n"
                "- Headquarters Location\n"
                "- Funding Type/Status\n"
                "- Business Overview\n"
                "- Market Position and Growth Potential\n"
                "- Competitive Advantages\n"
                "\nFormat as a structured list with clear headers for each company."
            ),
            agent=self.company_research_agent,
            callback=self._on_task_complete
        )

        # Market Research Task
        self.market_trends_task = Task(
            description=(
                "Analyze market trends based on these parameters:\n"
                "Industry: {industry}\n"
                "{product}"
                "\nProvide insights on:\n"
                "1. Current market trends\n"
                "2. Growth opportunities\n"
                "3. Key challenges\n"
                "4. Future outlook\n\n"
                "Format the output as a clear, structured analysis."
            ),
            expected_output=(
                "A comprehensive market analysis including:\n"
                "- Current market trends and dynamics\n"
                "- Growth opportunities and potential\n"
                "- Key challenges and considerations\n"
                "- Future market outlook"
            ),
            agent=self.market_trends_agent,
            callback=self._on_task_complete
        )

        # Outreach Task
        self.outreach_task = Task(
            description=(
                "Using the provided research, create personalized emails.\n"
                "Email body has to be elaborative with information from research and market trends\n"
                "Return a JSON array with company name, website, headquarters, funding status, email subject and body\n"
                "Email body has to be between 50 and 125 words\n "
                "provide only JSON array no other text"
                
            ),
            expected_output=(
                "JSON array of emails, each containing:\n"
                "- Company information from research\n"
                "- Personalized subject line\n"
                "- Customized email body"
            ),
            agent=self.outreach_agent,
            callback=self._on_task_complete
            
        )

        # Supervisor Task is not needed as the supervisor agent will manage tasks automatically in hierarchical process
        # self.supervisor_task = Task(...

    def execute_research(self, inputs: dict) -> dict:
        """Execute the complete research and outreach process"""
        try:
            # Prepare inputs with optional product info
            research_inputs = inputs.copy()
            product = inputs.get('product', '')
            research_inputs['product_info'] = f"Product/Technology focus: {product}\n" if product else ""
            
            # Setup task dependencies
            self.market_trends_task.context = [self.company_research_task]
            self.outreach_task.context = [self.company_research_task, self.market_trends_task]
            
            # Create the crew with hierarchical process
            research_crew = Crew(
                agents=[
                    self.company_research_agent,
                    self.market_trends_agent,
                    self.outreach_agent
                ],
                tasks=[
                    self.company_research_task,
                    self.market_trends_task,
                    self.outreach_task
                ],
                  # Set supervisor as manager
                verbose=True,
                process=Process.sequential,
                memory=False
            )

            # Execute the process
            results = research_crew.kickoff(inputs=research_inputs)
            return results

        except Exception as e:
            print(f"An error occurred during research: {str(e)}")
            raise

# Example usage for local testing
def example_task_callback(message):
    print(f"\n{message}")

def main():
    """Main function to test the research functionality"""
    crew = ResearchCrew(
        task_callback=example_task_callback
    )

    # Test inputs
    test_inputs = {
        "industry": "healthcare",
        "company_stage": "startup",
        "geography": "Texas",
        "funding_stage": "series A",
        "product": "AI"  # Optional
    }

    try:
        results = crew.execute_research(test_inputs)
        print(results)

    except Exception as e:
        print(f"Main execution error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
