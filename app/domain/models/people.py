from dataclasses import dataclass


@dataclass(frozen=True)
class People:
    id: str
    label: str
    web_path: str

    def to_dict(self):
        return {
            'id': self.id,
            'label': self.label,
            'web_path': self.web_path,
        }