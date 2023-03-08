from datetime import datetime, timezone
from datetime import timedelta

from src import PaperCollector, PaperFeedGenerator, dump_feed


def main():
    # Configs
    url = 'https://nicholas.carlini.com/writing/2019/advex_papers.json'
    by_days = {1: 'daily', 7: 'weekly', 14: 'biweekly'}
    now = datetime.now(timezone.utc)
    no_earlier_than = now - timedelta(days=9)

    # Collect papers
    pc = PaperCollector(url, no_earlier_than)
    paper_list = pc.run()

    # Generate feeds
    for feed, tag in PaperFeedGenerator(paper_list, by_days=by_days):
        dump_feed(feed, f'advex_papers_{tag}.xml')


if __name__ == '__main__':
    main()
