from xml.dom import minidom
from xml.etree.ElementTree import tostring, Element

from loguru import logger


def dump_feed(feed: Element, filename: str) -> None:
    """
    Dump an RSS feed to xml file.

    Args:
        feed: Feed node.
        filename: Output file name.

    Returns:
        None
    """
    feed_string = tostring(feed, encoding='utf-8')
    feed_string = minidom.parseString(feed_string).toprettyxml(indent='  ')
    logger.info(f'Dumping feed to "{filename}".')
    with open(filename, 'w') as f:
        f.write(feed_string)
