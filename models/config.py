import os


def get_database_config():
    """
    Retrieve the configuration dictionary for SQLAlchemy.

    Fetches the database URL from the environment variable 'DATABASE_URL'.
    If 'DATABASE_URL' is not set, defaults to a local SQLite database.

    Returns:
        dict: A dictionary containing SQLAlchemy configuration options:
            - SQLALCHEMY_DATABASE_URI (str): Database connection URL.
            - SQLALCHEMY_TRACK_MODIFICATIONS (bool): Flag to disable track modifications.
            - SQLALCHEMY_ENGINE_OPTIONS (dict): Additional engine options like
              connection pool recycling and pre-ping.
    """
    database_url = os.environ.get('DATABASE_URL')

    return {
        'SQLALCHEMY_DATABASE_URI': database_url or 'sqlite:///local.db',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'pool_recycle': 300,
            'pool_pre_ping': True,
        }
    }
