from pathlib import Path

import setuptools

REQUIREMENTS = Path("./requirements/common.txt")

setuptools.setup(
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": [f"nominally = nominally:cli_parse"]},
    install_requires=REQUIREMENTS.read_text(),
)
