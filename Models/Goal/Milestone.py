from datetime import date


class Milestone:
    def __init__(self, description: str, deadline: date, iscomplete: bool = False):
        self.description = description
        self.deadline = deadline
        self.iscomplete = iscomplete