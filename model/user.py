# === MODELS ===

# model/user.py
import json
import os

USER_FILE_PATH = "user_data.json"

class Role:
    def __init__(self, name: str):
        self.name = name

    def to_dict(self):
        return {"name": self.name}

    @staticmethod
    def from_dict(data):
        return Role(name=data["name"])

class TeamMate:
    def __init__(self, ids: list, first_name: str, last_name: str, role: Role):
        self.ids = ids  # List[str]
        self.first_name = first_name
        self.last_name = last_name
        self.role = role

    def to_dict(self):
        return {
            "ids": self.ids,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role.name
        }

    @staticmethod
    def from_dict(data, roles):
        role_name = data["role"]
        role = next((r for r in roles if r.name == role_name), Role(role_name))
        return TeamMate(
            ids=data["ids"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            role=role
        )

class User:
    def __init__(self, id: str, name: str, email: str):
        self.id = id
        self._name = name
        self._email = email
        self.team_mates = []  # List[TeamMate]
        self.roles = []  # List[Role]

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.save_to_file(USER_FILE_PATH)

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value
        self.save_to_file(USER_FILE_PATH)

    def add_team_mate(self, mate: TeamMate):
        self.team_mates.append(mate)
        self.save_to_file(USER_FILE_PATH)

    def remove_team_mate_by_id(self, mate_id: str):
        self.team_mates = [m for m in self.team_mates if mate_id not in m.ids]
        self.save_to_file(USER_FILE_PATH)

    def add_role(self, role: Role):
        self.roles.append(role)
        self.save_to_file(USER_FILE_PATH)

    def force_save(self):
        self.save_to_file(USER_FILE_PATH)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "roles": [r.to_dict() for r in self.roles],
            "team_mates": [m.to_dict() for m in self.team_mates]
        }

    @staticmethod
    def from_dict(data):
        user = User(id=data["id"], name=data["name"], email=data["email"])
        user.roles = [Role.from_dict(r) for r in data.get("roles", [])]
        user.team_mates = [TeamMate.from_dict(m, user.roles) for m in data.get("team_mates", [])]
        return user

    def save_to_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    @staticmethod
    def load_from_file(path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return User.from_dict(data)
        return None
