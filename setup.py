import setuptools

with open('README.md',  'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='transposcope_pkg',
    version='0.0.0',
    author='Mark Grivainis',
    author_email='mark.grivainis@fenyolab.org',
    # TODO - Update this to be more accurate
    description='A package for viewing read coverage of novel mobile' + \
                'elements notrepresented in the reference genome',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/FenyoLab/transposcope',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Licencse :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Unix"
    ],
    install_requires=[
        'pandas',
    ]
)
