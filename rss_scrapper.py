from argparse import ArgumentParser
from typing import List, Optional, Sequence
import requests
from json import dumps
import xml.etree.ElementTree as ElT


class UnhandledException(Exception):
    pass


def rss_parser(
    xml: str,
    limit: Optional[int] = None,
    json: bool = False,
) -> List[str]:
    """
    RSS parser.

    Args:
        xml: XML document as a string.
        limit: Number of the news to return. if None, returns all news.
        json: If True, format output as JSON.

    Returns:
        List of strings.
        Which then can be printed to stdout or written to file as a separate lines.
    """
    channel = {}
    item = []
    output = []
    tree = ElT.fromstring(xml)

    for elem in tree.find('channel'):
        if elem.tag == 'title':
            channel['title'] = elem.text
        elif elem.tag == 'link':
            channel['link'] = elem.text
        elif elem.tag == 'lastBuildDate':
            channel['lastBuildDate'] = elem.text
        elif elem.tag == 'pudDate':
            channel['pubDate'] = elem.text
        elif elem.tag == 'language':
            channel['language'] = elem.text
        elif elem.tag == 'category':
            if 'category' not in channel:
                channel['category'] = []
            channel['category'].append(elem.text.strip() if elem.text else None)
        elif elem.tag == 'managingEditor':
            channel['managingEditor'] = elem.text
        elif elem.tag == 'description':
            channel['description'] = elem.text

    for itm in tree.findall('channel/item'):
        item_dict = {}
        for el in itm:
            if el.tag == 'title':
                item_dict['title'] = el.text
            if el.tag == 'author':
                item_dict['author'] = el.text
            if el.tag == 'pubDate':
                item_dict['pubDate'] = el.text
            if el.tag == 'link':
                item_dict['link'] = el.text
            if el.tag == 'category':
                if 'category' not in item_dict:
                    item_dict['category'] = []
                item_dict['category'].append(el.text.strip() if el.text else None)
            if el.tag == 'description':
                item_dict['description'] = el.text
        item.append(item_dict)

    if json:
        data = {}
        if 'title' in channel:
            data['title'] = channel['title']
        if 'link' in channel:
            data['link'] = channel['link']
        if 'lastBuildDate' in channel:
            data['lastBuildDate'] = channel['lastBuildDate']
        if 'pubDate' in channel:
            data['pubDate'] = channel['pubDate']
        if 'language' in channel:
            data['language'] = channel['language']
        if 'category' in channel:
            data['category'] = ''.join(channel["category"])
        if 'managingEditor' in channel:
            data['managingEditor'] = channel['managingEditor']
        if 'description' in channel:
            data['description'] = channel['description']
        data['items'] = item[:limit] if limit else item
        output.append(dumps(data, indent=2, ensure_ascii=False))
    else:
        output.append(f'Feed: {channel["title"]}')
        output.append(f'Link: {channel["link"]}')
        if 'lastBuildDate' in channel:
            output.append(f'Last Build Date: {channel["lastBuildDate"]}')
        if 'pubDate' in channel:
            output.append(f'Publish Date: {channel["pubDate"]}')
        if 'language' in channel:
            output.append(f'Language: {channel["language"]}')
        if 'category' in channel:
            output.append(f'Categories: {channel["category"]}')
        if 'managingEditor' in channel:
            output.append(f'Editor: {channel["managingEditor"]}')
        if 'description' in channel:
            output.append(f'Description: {channel["description"]}')
        for itm in item[:limit] if limit else item:
            output.append(' ')
            output.append(f'Title: {itm["title"]}')
            if 'author' in itm:
                output.append(f'Author: {itm["author"]}')
            if 'pubDate' in itm:
                output.append(f'Published: {itm["pubDate"]}')
            if 'link' in itm:
                output.append(f'Link: {itm["link"]}')
            if 'category' in itm:
                output.append(f'Categories: {", ".join(itm["category"])}')
            output.append(' ')
            if 'description' in itm:
                output.append(itm["description"])
            output.append(' ')

    return output


def main(argv: Optional[Sequence] = None):
    parser = ArgumentParser(
        prog="rss_reader",
        description="Pure Python command-line RSS reader.",
    )
    parser.add_argument("source", help="RSS URL", type=str, nargs="?")
    parser.add_argument(
        "--json", help="Print result as JSON in stdout", action="store_true"
    )
    parser.add_argument(
        "--limit", help="Limit news topics if this parameter provided", type=int
    )

    args = parser.parse_args(argv)
    xml = requests.get(args.source).text
    try:
        print("\n".join(rss_parser(xml, args.limit, args.json)))
        return 0
    except Exception as e:
        raise UnhandledException(e)


if __name__ == "__main__":
    main()
