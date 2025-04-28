from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai_tools import SerperDevTool, DallETool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from media_crew.tools.eleven_tts import ElevenTTSTool


@CrewBase
class MediaCrew():
    """MediaCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def script_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['script_writer'],
            verbose=True,
            tools=[SerperDevTool()]
        )
    
    @agent
    def thumbnail_designer(self) -> Agent:
        return Agent(
            config=self.agents_config['thumbnail_designer'],
            verbose=True,
            tools=[DallETool(model='dall-e-3', size='1024x1024')]
        )

    @agent
    def video_narrator(self) -> Agent:
        return Agent(
            config=self.agents_config['video_narrator'],
            verbose=True,
            llm   = "gpt-3.5-turbo",
            tools = [ElevenTTSTool()]
        )
    
    @task
    def script_task(self) -> Task:
        return Task(
            config=self.tasks_config['script_task'],
            output_file='out/report.md'
        )

    @task
    def thumbnail_task(self) -> Task:
        return Task(
            config=self.tasks_config['thumbnail_task'],
            output_file='out/thumb_output.md',
            depends_on=[self.script_task]
        )
    
    @task
    def narrative_task(self) -> Task:
        return Task(
            config=self.tasks_config['narrative_task'],
            output_file="out/voice_output.mp3"
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the MediaCrew crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
