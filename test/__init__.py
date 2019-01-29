from os import getcwd, path

from dotenv import load_dotenv

# try to parse .env file to use development
load_dotenv(dotenv_path=path.join(getcwd(), '.env'), verbose=True)


def get_fixtures_directory():
    """
    :rtype: str
    """
    return path.join(
        path.abspath(path.dirname(__file__)),
        'fixtures'
    )
