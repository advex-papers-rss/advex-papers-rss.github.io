from datetime import datetime, timezone

import json_stream.requests
import requests
from loguru import logger

from src.base import Paper


class StopCollectingPapers(StopIteration):
    """ Signal the end of collecting streaming papers. """
    pass


class PaperCollector(object):
    """
    Collect papers by streaming a json url.
    """

    def __init__(self, url: str, until: datetime):
        """
        Initialize a PaperCollector object.

        Args:
            url: Link to the json data.
            until: Only collect papers until a given date
        """
        super().__init__()

        # Core data
        self.url = url
        self.until = until

        # Collected papers
        self.paper_list = []

        # Running paper
        self.paper = None

    def run(self) -> list[Paper]:
        """
        Start the collection.

        Returns:
            A list of Paper dataclass instances.
        """
        # Streaming json data until StopCollectingPapers
        logger.info('Start collecting papers.')
        try:
            with requests.get(self.url, stream=True) as response:
                json_stream.requests.visit(response, self._collect_item)
        except StopCollectingPapers as err:
            logger.info(err)
            logger.info('Done collecting papers.')

        return self.paper_list

    def _collect_item(self, item: str, path: tuple[int, int, ...]) -> None:
        """
        Collect items returned by json_stream's `visit` method.

        Args:
            item: The collected item.
            path: The path to the collected item, usually a tuple of (item_id, sub_id, sub_sub_id, ...).

        Returns:
            None

        Raises:
            RuntimeError: If an unexpected path is received.
        """
        # Check which item is being collected
        match path[1]:

            # date (first item of a paper)
            case 0:
                # Reset the running paper
                self.paper = Paper()

                # Convert to datetime
                date = datetime.strptime(item, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                self.paper.date = date

                # Stop if reached an old paper
                if date < self.until:
                    raise StopCollectingPapers(f'Found paper on {date}, earlier than {self.until}.')

            # url
            case 1:
                self.paper.link = item

            # title
            case 2:
                self.paper.title = item

            # author list
            case 3:
                self.paper.authors.append(item)

            # abstract (last item of a paper)
            case 4:
                self.paper.abstract = item.replace('\n', ' ')

                # Done collecting items of this paper
                self.paper_list.append(self.paper)
                logger.info(f'Collected paper\n{self.paper!r}.')

            # error
            case _:
                raise RuntimeError(f'Unexpected path {path!r} with item {item!r}.')
