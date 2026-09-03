from researchflow.sources.registry import build_search_engine
from researchflow.sources import (
    ArxivSource,
    CrossrefSource,
    OpenAlexSource,
)


def test_build_search_engine_registers_supported_sources():
    engine = build_search_engine()

    assert len(engine.sources) == 3

    source_types = {
        type(source)
        for source in engine.sources
    }

    assert source_types == {
        OpenAlexSource,
        CrossrefSource,
        ArxivSource,
    }