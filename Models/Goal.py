from datetime import date
from Models import Milestone
class Goal(Milestone):
    def __int__(self, description: str, deadline: date, iscomplete: bool, milestones: [Milestone]):
        super(description,deadline,iscomplete)
        self.milestones = milestones