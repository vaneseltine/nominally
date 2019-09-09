from pathlib import Path

import setuptools

install_requires = Path("./requirements/common.txt").read_text()

setuptools.setup(
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": [f"nominally = nominally:cli_parse"]},
    install_requires=install_requires,
)
