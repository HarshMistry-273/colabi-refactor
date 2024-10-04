from crewai import Agent, Process, Task, Crew
from langchain.tools import Tool
from langchain_community.tools import TavilySearchResults
from src.config import Config
from langchain_openai import ChatOpenAI
from src.crew_agents.prompts import get_comment_task_prompt, get_task_prompt
from src.crew_search_bot import OutputFile
from src.utils.utils import get_uuid


class CustomAgent:
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        tools: list[Tool],
        description: str,
        expected_output: str,
        model: str = Config.MODEL_NAME,
    ):
        self.model = ChatOpenAI(
            model=model,
            api_key=Config.OPENAI_API_KEY,
        )
        # Agents
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools
        self.agents = self.create_agent()

        # Tasks
        self.expected_output = expected_output
        self.description = description
        self.tasks = self.create_tasks()

        # Crew
        self.crew = self.create_crew()

    def create_agent(self) -> list[Agent]:

        custome_agent = Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=self.model,
            tools=self.tools,
            verbose=True,
        )

        comment_agent = Agent(
            role="Comment agent",
            goal="Comment on the previous task completed by agents.",
            backstory="You are obeserver of task being completed by Agents and you look for if task is being completed and as expexted",
            llm=self.model,
            verbose=True,
        )

        agents = [custome_agent, comment_agent]
        return agents

    def create_tasks(self):
        prompt = get_task_prompt()
        custom_task = Task(
            description=prompt,
            expected_output=self.expected_output,
            agent=self.agents[0],
            output_json=OutputFile,
        )

        comment_prompt = get_comment_task_prompt()
        comment_task = Task(
            description=comment_prompt,
            expected_output="Task reviewed: ",
            agent=self.agents[1],
        )

        return [custom_task, comment_task]

    def create_crew(self):
        crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
        return crew

    def main(self):
        response = self.crew.kickoff(inputs={"description": self.description})
        output = response.tasks_output

        custom_task_output = output[0]
        comment_task_output = output[1]

        return custom_task_output, comment_task_output
