"""
This script generates Markdown syntax with sources documentation.
"""
import logging
from mycroft_holmes.sources.base import SourceBase


def main():
    """
    Prints out Markdown with sources documentation
    """
    logger = logging.getLogger('generate_source_docs')

    sources = SourceBase.sources()
    logger.info('Registered sources: %s', sources)

    sources_list = ''
    full_docs = ''

    for source in sources:
        class_name = source.__name__  # e.g. ConstSource
        source_name = source.NAME  # e.g. common/const

        if source_name is None:
            continue

        sources_list += "* `%s`: %s\n" % (source_name, source.get_short_description())

        full_docs += """
### %s

Source name: `%s`

> %s
""".strip() % (class_name, source_name, source.get_description()) + '\n\n'

    # print the list of sources
    print('## Available sources\n')
    print(sources_list.strip())
    print()

    # full docs
    print(full_docs.strip())
