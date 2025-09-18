from enum import Enum

class IGenderEnum(str, Enum):
    female = "female"
    male = "male"
    other = "other"

class TokenType(str, Enum):
    ACCESS = "access_token"
    REFRESH = "refresh_token"

class KanbanType(str, Enum):
    CHORE = "chore"
    URGENT = "urgent"
    TASK = "task"

