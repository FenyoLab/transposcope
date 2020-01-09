import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

files = ["web/web.zip", "config/logging.json"]

setuptools.setup(
    name="transposcope",
    version="2.0.0",
    author="Mark Grivainis",
    author_email="mark.grivainis@fenyolab.org",
    description="A package for visualizing read coverage in areas surrounding novel mobile element insertions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FenyoLab/transposcope",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Licencse :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Unix",
    ],
    packages=["transposcope", "transposcope.viewer", "transposcope.parsers"],
    package_data={"transposcope": files},
    entry_points={"console_scripts": ["transposcope = transposcope.cli:main"]},
)
