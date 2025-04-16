from setuptools import setup, find_packages

setup(
    name="KnowlegeGraph",
    version="0.1.0",
    description="A system for managing and querying research papers using graph and vector databases",
    author="Jukka Salmenkyla",
    packages=find_packages(),
    install_requires=[
        "langchain-openai>=0.0.5",
        "langchain>=0.1.0",
        "neo4j>=5.0.0",
        "openai>=1.0.0",
        "pandas>=2.0.0",
        "PyPDF2>=3.0.0",
        "pytest>=7.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pylint>=3.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
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
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
) 