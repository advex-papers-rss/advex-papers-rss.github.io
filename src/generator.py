from datetime import datetime
from typing import Generator
from xml.etree.ElementTree import Element, SubElement

from src.base import Paper
from src.utils import rss_add_dict, rss_add


class FeedGenerator(object):
    """
    Generate RSS feed from a list of papers.
    """

    def __init__(self, paper_list: list[Paper], config: dict, start_time: datetime):
        """
        Initialize a FeedGenerator object.

        Args:
            paper_list: A list of Paper dataclass instances.
            config: Configure for the generator.
        """
        super().__init__()

        # Extract important configs
        self.paper_list = paper_list
        self.start_time = start_time
        self.config = config
        self.by_days = {day: tag for tag, day in config['days'].items()}

        # Prepare RSS feed
        self.feed, self.channel = None, None

    def init_feed(self):
        """ Initialize RSS feed and set metadata. """
        self.feed = Element('rss', version='2.0')
        self.channel = SubElement(self.feed, 'channel')
        rss_add_dict(self.channel, self.config['rss'])
        rss_add(self.channel, 'lastBuildDate', self.start_time.isoformat(timespec='seconds'))

    def iter_feed_tags(self) -> Generator[str, None, None]:
        """ Add all papers and yield feed tags when matching desired conditions. """

        for paper in self.paper_list:

            # Yield if reaching a desired number of days
            nb_days = (self.start_time - paper.date).days
            for day in self.by_days.keys():
                if nb_days > day:
                    yield self.by_days.pop(day)
                    break

            # Format paper data
            paper_data = {
                'title': paper.title,
                'link': paper.link,
                'description': paper.abstract,
                'author': ','.join(paper.authors),
                'pubDate': paper.date.isoformat(timespec='seconds'),
            }

            # Add paper to the feed
            item = SubElement(self.channel, 'item')
            rss_add_dict(item, paper_data)

        # Yield the remaining tags
        yield from self.by_days.values()

    def __iter__(self) -> Generator[tuple[Element, str], None, None]:
        """ Return an iterator over the RSS feeds and tags. """
        self.init_feed()
        for tag in self.iter_feed_tags():
            yield self.feed, tag
