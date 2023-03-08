from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Paper(object):
    """ Dataclass for one paper. """
    date: datetime = field(init=False)
    link: str = ''
    title: str = ''
    abstract: str = ''
    authors: list[str] = field(default_factory=list)

    def __repr__(self):
        s = 'Paper('
        s += f'\n  title = {self.title}'
        s += f'\n  link = {self.link}'
        s += '\n)'
        return s
