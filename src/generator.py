import tomllib
from typing import Generator
from xml.etree.ElementTree import Element, SubElement

from src.collector import PaperCollector
from src.utils import rss_add_dict, rss_add


class FeedGenerator(object):
    """
    Generate RSS feed from a list of papers.
    """

    def __init__(self, config_file: str):
        """
        Initialize a FeedGenerator object.

        Args:
            config_file: Path to the generator's config file.
        """
        super().__init__()

        # Load config
        with open(config_file, 'rb') as f:
            self.config = tomllib.load(f)

        # Extract important configs
        self.by_days = {day: tag for tag, day in self.config['days'].items()}

        # Get paper list
        collector = PaperCollector(url=self.config['url'], num_days=max(self.by_days))
        self.start_time, self.paper_list = collector.run()

        # Prepare RSS feed
        self.feed, self.channel = None, None

    def _init_feed(self):
        """ Initialize RSS feed and set metadata. """
        self.feed = Element('rss', version='2.0')
        self.channel = SubElement(self.feed, 'channel')
        rss_add_dict(self.channel, self.config['rss'])
        rss_add(self.channel, 'lastBuildDate', self.start_time.isoformat(timespec='seconds'))

    def _iter_feed_tags(self) -> Generator[str, None, None]:
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
                'description': paper.abstract.replace('\n', ' '),
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
        self._init_feed()
        for tag in self._iter_feed_tags():
            yield self.feed, tag
