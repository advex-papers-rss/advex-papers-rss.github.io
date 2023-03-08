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


def _init_feed(build_date: datetime) -> tuple[Element, Element]:
    """
    Initialize RSS feed with meta data.

    Args:
        build_date: The datetime for this generation.

    Returns:
        The xml nodes for feed and channel.
    """
    # Make root nodes
    feed = Element('rss', version='2.0')
    channel = SubElement(feed, 'channel')

    # Add meta data
    _setattr(channel, 'title', 'Adversarial Example Papers')
    _setattr(channel, 'link', 'https://nicholas.carlini.com/writing/2019/all-adversarial-example-papers.html')
    _setattr(channel, 'description', 'Adversarial example papers collected by Nicholas Carlini.')
    _setattr(channel, 'language', 'en-us')
    _setattr(channel, 'lastBuildDate', build_date.isoformat(timespec='seconds'))
    _setattr(channel, 'generator', 'advex-papers-rss')
    _setattr(SubElement(channel, 'author'), 'name', 'Nicholas Carlini')

    return feed, channel


class PaperFeedGenerator(object):
    """
    Generate RSS feed from a list of papers.
    """

    def __init__(self, paper_list: list[Paper], by_days: dict[int, str]):
        """
        Initialize a PaperFeedGenerator object.

        Args:
            paper_list: A list of Paper dataclass instances.
            by_days: Output a feed for each specified number of day.
        """
        super().__init__()

        # Set meta data
        self.generated_on = datetime.now(timezone.utc)
        self.feed, self.channel = _init_feed(self.generated_on)

        # Set rss data
        self.paper_list = paper_list
        self.by_days = by_days

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
