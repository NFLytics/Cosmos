"""
SPARC Radial-Dependent RAR Analysis - Setup Configuration
Project: Testing SDH+ vs ΛCDM with existing data
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sparc-rar-analysis",
    version="1.0.0",
    author="CDM Alternative Model Analysis Team",
    description="Radial-dependent RAR analysis of SPARC galaxies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sparc-rar-analysis",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sparc-analyze=src.main:main",
        ],
    },
)