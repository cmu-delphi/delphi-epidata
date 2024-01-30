import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="delphi_epidata",
    version="4.1.17",
    author="David Farrow",
    author_email="dfarrow0@gmail.com",
    description="A programmatic interface to Delphi's Epidata API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cmu-delphi/delphi-epidata",
    project_urls={
        "Changelog": "https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/packaging/pypi/CHANGELOG.md",
    },
    packages=setuptools.find_packages(),
    install_requires=["aiohttp", "requests>=2.7.0", "tenacity"],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
