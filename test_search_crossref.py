from researchflow.sources import CrossrefSource


def main():
    source = CrossrefSource()

    query = "cybersecurity knowledge graph"

    papers = list(
        source.search(
            query,
            max_results=5,
        )
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