import setuptools 

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bacdive",
    version="0.3.1",
    description="BacDive-API - Programmatic Access to the BacDive Database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Julia Koblitz",
    author_email="julia.koblitz@dsmz.de",
    url='https://bacdive.dsmz.de/',
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    keywords="microbiology bacteria strains phenotypes",
    install_requires=[
        "python-keycloak",
        "requests>=2.25.1",
        "urllib3>=1.26.5"
    ]
)
