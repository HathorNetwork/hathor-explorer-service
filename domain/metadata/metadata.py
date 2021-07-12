from dataclasses import dataclass, asdict


@dataclass
class Metadata:
    type: type
    id: str

    @property
    def data(self):
        raise NotImplementedError

    @classmethod
    def from_dict(cls):
        raise NotImplementedError

    def to_dict(self) -> dict:
        """ Convert a Metadata instance into dict

        :return: Dict representations of Metadata
        :rtype: dict
        """
        return asdict(self)
