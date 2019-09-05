import setuptools
from pathlib import Path

REQUIREMENTS = Path("./requirements.txt")

setuptools.setup(
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": [f"nominally = nominally:parse"]},
    install_requires=REQUIREMENTS.read_text(),
)
