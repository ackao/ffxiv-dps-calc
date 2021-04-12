from pathlib import Path
from setuptools import setup, find_packages

doc_requirements = [
    'pdoc3',
]

with open('README.md', 'r') as f:
    long_description = f.read()

CWD = Path.cwd()
requirements = open(CWD / 'backend' / 'requirements.txt').read().split('\n')

setup(
    name='ffxiv_dps_calc',
    version='0.0.1',
    description='dps calculations for the smart masses',
    long_description=long_description,
    python_requies='>=3.9',
    packages=find_packages('backend'),
    package_dir={'': 'backend'},
    install_requires=requirements,
    extras_require={
        'docs': doc_requirements,
    }
)
