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

    sources = SourceBase.__subclasses__()
    logger.info('Registered sources: %s', sources)

    sources_list = ''
    full_docs = ''

    for source in sources:
        name = source.NAME

        sources_list += "* `%s` %s\n" % (name, source.get_short_description())

        full_docs += """
## `%s`

%s
""".strip() % (name, source.get_description()) + '\n\n'

    # print the list of sources
    print('## Available sources\n')
    print(sources_list.strip())
    print()

    # full docs
    print(full_docs.strip())
