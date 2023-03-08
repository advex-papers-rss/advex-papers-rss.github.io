from xml.dom import minidom
from xml.etree.ElementTree import tostring, Element, SubElement

from loguru import logger


def rss_add(parent: Element, key: str, value: str | dict) -> None:
    """
    Shortcut for creating a sub-node in RSS.

    Args:
        parent: The parent node.
        key: The name of the sub-node.
        value: The content of the sub-node (nested by dict).

    Returns:
        None
    """
    while isinstance(value, dict):
        parent = SubElement(parent, key)
        key, value = next(iter(value.items()))

    SubElement(parent, key).text = value


def rss_add_dict(parent: Element, data: dict[str, str | dict]) -> None:
    """
    Shortcut for creating multiple sub-nodes in RSS.

    Args:
        parent: The parent node.
        data: A dict whose (key, value) pairs will be added.

    Returns:
        None
    """
    for k, v in data.items():
        rss_add(parent, k, v)


def save_feed(feed: Element, filename: str) -> None:
    """
    Save an RSS feed to xml file.

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
