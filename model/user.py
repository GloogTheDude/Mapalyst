class Role:
    def __init__(self, name: str):
        self.name = name

class TeamMate:
    def __init__(self, id: str, first_name: str, last_name: str, role: Role):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.role = role

class User:
    def __init__(self, id: str, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email
        self.team_mates = []  # List[TeamMate]

    def add_team_mate(self, mate: TeamMate):
        self.team_mates.append(mate)
