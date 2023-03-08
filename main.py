from src.generator import FeedGenerator
from src.utils import save_feed

if __name__ == '__main__':
    for feed, tag in FeedGenerator('config.toml'):
        save_feed(feed, f'{tag}.xml')
