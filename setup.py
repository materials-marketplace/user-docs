import os
import subprocess
from setuptools import setup

from packageinfo import VERSION, NAME


def generate_pdf(self):
    path = os.path.join("docs", "build", "latex")
    subprocess.check_call(["make", "-C", path])


# Read description
with open("README.md", "r") as readme:
    README_TEXT = readme.read()

# main setup configuration class
setup(
    name=NAME,
    version=VERSION,
    author="The MarketPlace Consortium",
    description="MarketPlace user docs",
    keywords="MarketPlace, documentation, sphinx",
    long_description=README_TEXT,
)
