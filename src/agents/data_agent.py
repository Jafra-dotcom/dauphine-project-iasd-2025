from src.tools.data_tools import DataTools
from langfuse import observe



class DataAgent:
    def __init__(self):
        self.data = DataTools()

    @observe(name="data_agent")
    def run(self, question: str) -> str:
        return self.data.answer(question)
