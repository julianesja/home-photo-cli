from dataclasses import dataclass


@dataclass(frozen=True)
class PhotoPeople:
    photo_id: str
    people_id: str

    def to_dict(self):
        return {
            'photo_id': self.photo_id,
            'people_id': self.people_id,
        }