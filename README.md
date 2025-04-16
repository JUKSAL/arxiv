# KnowlegeGraph

A system for managing and querying research papers using graph and vector databases.

## Features

- Process PDF research papers and extract structured information
- Build a knowledge graph of papers, authors, citations, and research fields
- Perform semantic search across papers using vector embeddings
- Generate summaries and extract keywords using LLMs
- Import metadata from Zotero
- Natural language querying of the knowledge graph

## Installation

### Prerequisites

- Python 3.8 or higher
- Neo4j database
- OpenAI API key

### Install from source

1. Clone the repository:
```bash
git clone https://github.com/jukkasalmenkyla/arxiv.git
cd arxiv
```

2. Install in development mode:
```bash
pip install -e ".[dev]"
```

### Environment Variables

Create a `.env` file with the following variables:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
OPENAI_API_KEY=your_api_key
```

## Usage

### Basic Usage

```python
from KnowlegeGraph import ResearchPaperGraphRAG, Config

# Initialize the system
config = Config.from_env()
rag = ResearchPaperGraphRAG(config)

# Process a PDF file
paper_id = rag.process_pdf("path/to/paper.pdf")

# Generate a summary
summary = rag.generate_paper_summary(paper_id)
print(summary)

# Find similar papers
similar_papers = rag.find_similar_papers(paper_id)
for paper in similar_papers:
    print(f"- {paper.title} (Score: {paper.similarity_score:.2f})")

# Query the knowledge graph
answer = rag.query("What are the most cited papers about machine learning?")
print(answer)
```

### Process Multiple Papers

```python
# Process a directory of PDFs
paper_ids = rag.process_directory("papers/")

# Import from Zotero CSV export
paper_ids = rag.process_metadata_csv("zotero_export.csv")
```

### Add Relationships

```python
# Add citations
rag.add_citation(citing_paper_id, cited_paper_id)

# Add research fields
rag.add_research_field(paper_id, "Machine Learning")

# Add institution affiliations
rag.add_institution("John Doe", "Example University")
```

## Development

### Running Tests

```bash
pytest KnowlegeGraph/tests/
```

### Code Style

The project uses:
- pylint for linting
- black for code formatting
- isort for import sorting

To format code:
```bash
black KnowlegeGraph/
isort KnowlegeGraph/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

