import tomllib
from datetime import datetime, timezone
from datetime import timedelta

from src import PaperCollector, PaperFeedGenerator, dump_feed


def main():
    # Load configs
    with open('config.toml', 'rb') as f:
        config = tomllib.load(f)

    # Get the number of days to collect
    now = datetime.now(timezone.utc)
    max_days = max(config['days'].values())
    no_earlier_than = now - timedelta(days=max_days + 2)

    # Collect papers
    collector = PaperCollector(url=config['data']['url'], no_earlier_than=no_earlier_than)
    paper_list = collector.run()

    # Generate feeds
    for feed, tag in PaperFeedGenerator(paper_list=paper_list, config=config):
        dump_feed(feed, f'advex_papers_{tag}.xml')


if __name__ == '__main__':
    main()