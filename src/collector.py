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

    def __init__(self, url: str, num_days: int):
        """
        Initialize a PaperCollector object.

        Args:
            url: Link to the json data.
            num_days: Only collect papers till a few days from now.
        """
        super().__init__()

        # Core data
        self.url = url
        self.num_days = num_days
        self.start_time = None

        # Collected papers
        self.paper_list = []
        self.paper = None

    def run(self) -> tuple[datetime, list[Paper]]:
        """
        Start the collection.

        Returns:
            Started time of collection.
            A list of Paper dataclass instances.
        """
        logger.info('Start collecting papers.')
        self.start_time = datetime.now(timezone.utc)

        # Streaming json data until StopCollectingPapers
        try:
            with requests.get(self.url, stream=True) as response:
                json_stream.requests.visit(response, self._collect_item)
        except StopCollectingPapers as err:
            logger.info(err)
        finally:
            logger.info('Done collecting papers.')

        return self.start_time, self.paper_list

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
                if (self.start_time - date).days > self.num_days:
                    raise StopCollectingPapers(f'Found paper on {date}, earlier than {self.num_days} days.')

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
                self.paper.abstract = item

                # Done collecting items of this paper
                self.paper_list.append(self.paper)
                logger.info(f'Collected paper\n{self.paper!r}.')

            # error
            case _:
                raise RuntimeError(f'Unexpected path {path!r} with item {item!r}.')
