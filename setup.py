from setuptools import setup, find_packages

setup(
    name="sonalbot",
    version="1.0.0",
    description="Wikidata maintenance bot for dead link archiving and welcoming new users",
    author="SonalDahanayaka",
    url="https://github.com/SonalDahanayaka/sonalbot",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pywikibot>=8.0.0",
        "requests>=2.31.0",
        "waybackpy>=3.0.6",
        "colorlog>=6.8.0",
    ],
)
