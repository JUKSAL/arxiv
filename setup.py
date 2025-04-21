from setuptools import setup, find_packages

setup(
    name="arxiv-scraper",
    version="0.1.0",
    description="A system for scheduled scraping and summarization of ArXiv papers",
    author="Jukka Salmenkyla",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.9.0",
        "PyPDF2>=3.0.0",
        "pandas>=1.0.0",
        "reportlab>=3.5.0",
        "requests>=2.25.0",
        "schedule>=1.0.0",
        "python-dotenv>=0.15.0",
    ],
    extras_require={
        "ai": [
            "openai>=0.27.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pylint>=3.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "arxiv-scraper=arxiv.__main__:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Retrieval",
        "Topic :: Text Processing :: Markup :: XML",
    ],
) 