from os import path


def get_fixtures_directory():
    """
    :rtype: str
    """
    return path.join(
        path.abspath(path.dirname(__file__)),
        'fixtures'
    )
