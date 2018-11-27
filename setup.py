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
            'pylint==2.2.0',
            'pytest==4.0.1',
        ]
    },
    install_requires=[
        'jira==2.0.0',
        'PyYAML==3.13',
    ],
    entry_points={
        'console_scripts': [
            'collect_metrics=mycroft_holmes.bin.collect_metrics:main',
        ],
    }
)
