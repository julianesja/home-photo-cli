from dataclasses import dataclass, field
from typing import List

from app.domain.models.people import People


@dataclass(frozen=True)
class Photo:
  id: str
  path: str
  path_web: str
  hash: str
  people: List[People] = field(default_factory=list)

  def to_dict(self):
    return {
      'id': self.id,
      'path': self.path,
      'hash': self.hash,
      'path_web': self.path_web,
      'people': [person.to_dict() for person in self.people]
    }