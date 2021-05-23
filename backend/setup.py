from pathlib import Path
from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

CWD = Path.cwd()
requirements = open(CWD / 'requirements.txt').read().split('\n')

dev_requirements = [
    'pylint==2.7.4',
    'mypy==0.812',
    'sqlalchemy[mypy]',
]

setup(
    name='ffxiv_dps_calc',
    version='0.0.1',
    description='dps calculations for the smart masses',
    long_description=long_description,
    python_requies='>=3.9',
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
    },
)
