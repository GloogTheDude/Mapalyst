import json
from pathlib import Path

class Role:
    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {"name": self.name}

    @classmethod
    def from_dict(cls, data):
        return cls(name=data.get("name", "</NA>"))


class TeamMate:
    def __init__(self, ids, first_name, last_name, role):
        self.ids = ids
        self.first_name = first_name
        self.last_name = last_name
        self.role = role

    def to_dict(self):
        return {
            "ids": self.ids,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role.to_dict() if self.role else None
        }

    @classmethod
    def from_dict(cls, data):
        role_data = data.get("role", {})
        if isinstance(role_data, str):
            role_obj = Role(role_data)
        else:
            role_obj = Role.from_dict(role_data)
        return cls(
            ids=data.get("ids", []),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            role=role_obj
        )


class User:
    def __init__(self, id, name, email, team_mates=None, roles=None):
        self.id = id
        self.name = name
        self.email = email
        self.team_mates = team_mates or []
        self.roles = roles or []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "team_mates": [mate.to_dict() for mate in self.team_mates],
            "roles": [role.to_dict() for role in self.roles],
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            email=data.get("email"),
            team_mates=[TeamMate.from_dict(d) for d in data.get("team_mates", [])],
            roles=[Role.from_dict(d) for d in data.get("roles", [])],
        )

    def force_save(self, path="user_data.json"):
        import json
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, path="user_data.json"):
        if Path(path).exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print('user_data.json correctly downloaded')
                    print(cls.from_dict(data).name)
                    return cls.from_dict(data)
            except Exception as e:
                print(f"Erreur lors du chargement du user: {e}")
        # Fallback si fichier absent ou invalide
        return cls(id="1", name="Admin", email="admin@example.com")
    
    def display(self):
        print(f"nom:{self.name}")
        print(f"mail: {self.email}")
        print(f"id: {self.id}")
