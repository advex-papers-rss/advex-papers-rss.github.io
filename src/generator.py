from datetime import datetime, timezone
from typing import Generator
from xml.etree.ElementTree import Element, SubElement

from loguru import logger

from src.base import Paper


def _setattr(parent: Element, key: str, value: str) -> None:
    """
    Shortcut for creating a sub-node in RSS.

    Args:
        parent: The parent xml node.
        key: The name of the sub node.
        value: The content of the sub node.

    Returns:
        None
    """
    SubElement(parent, key).text = value


class PaperFeedGenerator(object):
    """
    Generate RSS feed from a list of papers.
    """

    def __init__(self, paper_list: list[Paper], config: dict):
        """
        Initialize a PaperFeedGenerator object.

        Args:
            paper_list: A list of Paper dataclass instances.
            config: Configure for the generator.
        """
        super().__init__()

        # Set build time
        self.generated_on = datetime.now(timezone.utc)

        # Initialize feed and channel
        feed = Element('rss', version='2.0')
        channel = SubElement(feed, 'channel')
        for key, value in config['rss'].items():
            _setattr(channel, key, value)

        _setattr(channel, 'lastBuildDate', self.generated_on.isoformat(timespec='seconds'))
        _setattr(SubElement(channel, 'author'), 'name', config['data']['author'])
        self.feed, self.channel = feed, channel

        # Set paper data
        self.paper_list = paper_list
        self.by_days = {day: tag for tag, day in config['days'].items()}

    def iter_feeds(self) -> Generator[tuple[Element, str], None, None]:
        """
        Generate the RSS feeds.

        Yields:
            A feed node and its corresponding tag.
        """
        logger.info('Start generating feeds.')
        for paper in self.paper_list:

            # Check if this paper reaches a date where we can yield a feed
            nb_days = (self.generated_on - paper.date).days
            for day in self.by_days.keys():
                if nb_days > day:
                    yield self.feed, self.by_days.pop(day)
                    break

            # Collect this paper
            item = SubElement(self.channel, 'item')
            _setattr(item, 'title', paper.title)
            _setattr(item, 'link', paper.link)
            _setattr(item, 'description', paper.abstract)
            _setattr(item, 'author', ','.join(paper.authors))
            _setattr(item, 'pubDate', paper.date.isoformat(timespec='seconds'))

        # Yield the remaining feeds
        for tag in self.by_days.values():
            yield self.feed, tag

        logger.info('Done generating feeds.')

    def __iter__(self) -> Generator[tuple[Element, str], None, None]:
        """
        Return an iterator over the RSS feeds and tags.

        Returns:
            An iterator over the RSS feeds and tags.
        """
        yield from self.iter_feeds()
