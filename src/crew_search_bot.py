from crewai import Agent, Process, Task, Crew
from langchain.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper, GoogleSearchAPIWrapper
from langchain_community.tools import TavilySearchResults
from src.config import Config
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from models.model import get_uuid


class OutputFile(BaseModel):
    topic: list[str]
    summary: list[str]
    link: list[str] = None


class CrewAgent:
    def __init__(
        self,
        role,
        goal,
        backstory,
        expected_output,
        required_csv: bool = False,
        csv_file_name: str = None,
        model: str = Config.MODEL_NAME,
    ):
        self.model = ChatOpenAI(
            model=model,
            api_key=Config.OPENAI_API_KEY,
        )
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.search = TavilySearchResults(
            max_results=10,
            search_depth="advanced",
            include_answer=True,
            # include_raw_content=True,
        )
        self.expected_output = expected_output
        self.output_file = None
        self.required_csv = required_csv
        self.csv_file_name = (
            csv_file_name
            if required_csv and csv_file_name
            else get_uuid() + ".csv" if required_csv else None
        )
        self.create_tool()
        self.create_agent()
        self.initialize_task()
        self.create_crew()
        # self.google_search_wrapper = GoogleSearchAPIWrapper(
        #     google_api_key=Config.GOOGLE_API_KEY, google_cse_id=Config.GOOGLE_CSE_ID
        # )

    def create_tool(self) -> None:
        self.serper_tool = Tool(
            name="google_search",
            # func=self.search.run,
            func=lambda query: self.search.invoke(query),
            description="Search Google for recent results.",
        )

    def create_agent(self) -> None:

        self.research_agent = Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=self.model,
            tools=[self.serper_tool],
            verbose=True,
        )

        self.comment_agent = Agent(
            role="Comment agent",
            goal="Comment on the previous task completed by agents. For instance, if previous task was about fetching articles",
            backstory=self.backstory,
            llm=self.model,
            # tools=[self.serper_tool],
            verbose=True,
        )

    def initialize_task(self):
        prompt = """Conduct an web search on {description}, focusing on gathering the most recent and credible data available. Provide a detailed yet concise summary, emphasizing key points, trends, and any notable developments. Ensure that all information is gathered from authoritative, trustworthy sources. Include a valid and working link to each data source in the following format: [http://example.com/dataset], and verify that all insights are precise, relevant, and from reputable publications or datasets."""
        # self.expected_output = (
        #     self.expected_output
        #     + "If expected out put related to table form keep the output file in json format."
        # )
        self.research_task = Task(
            description=prompt,
            expected_output=self.expected_output,
            # expected_output="Summarize key insights and relevant data from the search results in 3-4 sentences. If multiple articles are referenced, provide a brief summary of each.",
            agent=self.research_agent,
            # output_file=self.csv_file_name,
            output_json=OutputFile if self.required_csv else None,
        )

        self.comment_task = Task(
            description="Provide a insightful comment on the previous task performed by another agent. The comment should assess the task's quality, relevance, and outcomes. If the task involved fetching data, summarize the data and offer thoughts on its significance or potential use. Keep output of max 3 sentance. and if task is completed you can start by saying Task is successfully completed and ..., here is the example: The task was successfully completed, and the data fetched is relevant. These articles/data provide valuable insights into the technological advancements in 2024, demonstrating their ongoing influence in the industry. Potential improvements or further analysis could include exploring the current impact of these innovations.",
            expected_output="Task reviewed: ",
            agent=self.comment_agent,
        )

    def create_crew(self):
        self.crew = Crew(
            agents=[self.research_agent, self.comment_agent],  # , self.writer_agent],
            tasks=[self.research_task, self.comment_task],  # , self.write_task],
            process=Process.sequential,
            verbose=True,
            # memory=True,
        )

    def main(self, description: str):
        response = self.crew.kickoff(inputs={"description": description})
        return response
