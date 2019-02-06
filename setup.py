from setuptools import setup, find_packages

from mycroft_holmes import VERSION

# @see https://github.com/pypa/sampleproject/blob/master/setup.py
setup(
    name='mycroft_holmes',
    version=VERSION,
    author='Maciej Brencz',
    author_email='maciej.brencz@gmail.com',
    license='MIT',
    description='Mycroft Holmes (High-Optional, Logical, Multi-Evaluating Supervisor) aka Mike',
    keywords='',
    url='https://github.com/Wikia/Mike',
    packages=find_packages(),
    extras_require={
        'dev': [
            'coverage==4.5.2',
            'pylint>=1.9.2, <=2.3.0',  # 2.x branch is for Python 3
            'pytest==4.1.0',
        ]
    },
    install_requires=[
        'elasticsearch-query==2.4.0',
        'google-api-python-client==1.7.7',
        'mysql-connector-python==8.0.13',
        'oauthlib[signedtoken]>=2.1.0, <3.0.0',
        'requests-oauthlib==1.1.0',
        'jira==2.0.0',
        'PyAthena==1.4.4',
        'pyyaml>=4.2b1',
        'python-dotenv==0.10.1',
        'lxml==4.3.0',
        # UI
        'flask==1.0.2',
        'gunicorn==19.9.0',
    ],
    entry_points={
        'console_scripts': [
            'collect_metrics=mycroft_holmes.bin.collect_metrics:main',
            'generate_source_docs=mycroft_holmes.bin.generate_source_docs:main',
        ],
    }
)
