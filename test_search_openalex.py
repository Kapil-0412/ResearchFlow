from researchflow.search import SearchEngine
from researchflow.sources import OpenAlexSource


def main():
    source = OpenAlexSource()

    engine = SearchEngine(
        [source]
    )

    query = "cybersecurity knowledge graph"

    papers = engine.search(
        query,
        max_results_per_source=5,
    )

    print(f"\nFound {len(papers)} papers\n")

    for index, paper in enumerate(
        papers,
        start=1,
    ):
        print("=" * 70)
        print(f"Paper #{index}")
        print(f"Title:   {paper.title}")
        print(f"Authors: {paper.authors}")
        print(f"Year:    {paper.year}")
        print(f"Source:  {paper.source}")
        print(f"DOI:     {paper.doi}")
        print(f"URL:     {paper.paper_url}")


if __name__ == "__main__":
    main()