from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class EngineeringTeam():
    """EngineeringTeam crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'


    @agent
    def engineering_lead(self) -> Agent:
        return Agent(
            config=self.agents_config['engineering_lead'],
            verbose=True
        )

    @agent
    def backend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['backend_engineer'],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=1000,
            max_retries=5
        )

    @agent
    def frontend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['frontend_engineer'],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=1000,
            max_retries=5
        )

    @agent
    def test_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['test_engineer'],
            verbose=True,
                allow_code_execution=True,
                code_execution_mode="safe",
            max_execution_time=1000,
            max_retries=5
        )

    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config['design_task']
        )
    
    @task
    def code_task(self) -> Task:
        return Task(
            config=self.tasks_config['code_task']
        )
    
    @task
    def test_task(self) -> Task:
        return Task(
            config=self.tasks_config['test_task']
        )
    
    @task
    def frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config['frontend_task']
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
    
