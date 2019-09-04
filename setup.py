import setuptools

setuptools.setup(
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": [f"nominally = nominally:parse"]},
    install_requires=["unidecode"],
)
