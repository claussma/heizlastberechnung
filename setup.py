from setuptools import setup, find_packages

setup(
    name="heizlast",
    version="0.1",
    packages=find_packages(include=['heizlast', 'heizlast.*']),
    install_requires=[],
    description="A module for calculating heat load",
    author="Markus Clauß",
    author_email="ihre_email@example.com",
)