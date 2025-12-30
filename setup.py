"""
Setup script for ConvoScope
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="convoscope",
    version="2.0.0",
    author="Herman Harp",
    author_email="your.email@example.com",  # Update this
    description="Privacy-first conversation analytics for Claude AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/convoscope",  # Update this
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "openpyxl>=3.1.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "viz": [
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
        ],
        "ml": [
            "scikit-learn>=1.3.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "convoscope=src.advanced_analyzer:main",
        ],
    },
    keywords="claude ai conversation analysis privacy nlp",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/convoscope/issues",
        "Source": "https://github.com/yourusername/convoscope",
        "Documentation": "https://github.com/yourusername/convoscope/tree/main/docs",
    },
)
