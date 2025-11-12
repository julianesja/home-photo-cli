from dataclasses import dataclass

@dataclass(frozen=True)
class DuplicatePhoto():
    photo_id: str
    duplicate_of_id: str
