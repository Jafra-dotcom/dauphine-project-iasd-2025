from src.tools.data_tools import DataTools


class DataAgent:
    def __init__(self):
        self.data = DataTools()

    def run(self, question: str) -> str:
        return self.data.answer(question)
