from pathlib import Path

import setuptools

import nominally

setuptools.setup(
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": [f"nominally = nominally:cli_parse"]},
    install_requires=Path("./requirements/common.txt").read_text(),
    version=nominally.__version__,
)
