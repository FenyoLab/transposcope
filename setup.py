import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="transposcope",
    version="0.1.0",
    author="Mark Grivainis",
    author_email="mark.grivainis@fenyolab.org",
    description="A package for visualizing read coverage in areas surrounding novel mobile element insertions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FenyoLab/transposcope",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Licencse :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Unix",
    ],
)
