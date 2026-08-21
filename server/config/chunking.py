from langchain_text_splitters import RecursiveCharacterTextSplitter
from .subjects import GROUPS

GROUP_CHUNK_CONFIG: dict[str, dict[str]] ={
    "stem": {
        "chunk_size": 800,"overlap": 150,"split_on":"section"
    },
    "pros": {
        "chunk_size": 1200,"overlap": 100,"split_on":"paragraph"
    },
    "math": {
        "chunk_size": 600,"overlap": 200,"split_on":"theorem_example"
    },
}

DEFAULT_CHUNK_CONFIG : dict = {
    "chunk_size": 1000, 
    "overlap": 150,
    "split_on": "paragraph"
}

SEPARATORS_BY_SPLIT_ON: dict[str, list[str]] = {
    # Section breaks: blank lines, then headings, then sentence, then word.
    "section": ["\n\n\n", "\n\n", "\n", ". ", " ", ""],
    # Theorem/example boundaries first, then normal paragraph/sentence breaks.
    "theorem_example": [
        "\nTheorem", "\nExample", "\nProof", "\nDefinition",
        "\n\n", "\n", ". ", " ", "",
    ],
    # Plain paragraph-first splitting for prose subjects.
    "paragraph": ["\n\n", "\n", ". ", " ", ""],
}
DEFAULT_SEPARATORS = SEPARATORS_BY_SPLIT_ON["paragraph"]

def get_chunk_config(group:str) -> dict:
    """
    Returns the chunking configuration for a given group. If the group is not recognized, it defaults to DEFAULT_CHUNK_CONFIG.
    """
    return GROUP_CHUNK_CONFIG.get(group, DEFAULT_CHUNK_CONFIG) 


def get_splitter(group:str) -> RecursiveCharacterTextSplitter:
    """
    Returns a RecursiveCharacterTextSplitter configured for the given group.
    If the group is not recognized, it defaults to a generic splitter configuration.
    """
    chunk_config = get_chunk_config(group)
    separators = SEPARATORS_BY_SPLIT_ON.get(chunk_config["split_on"], DEFAULT_SEPARATORS)

    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_config["chunk_size"],
        chunk_overlap=chunk_config["overlap"],
        separators=separators
    )

_uncovered = GROUPS - set(GROUP_CHUNK_CONFIG)
if _uncovered:
    import warnings
    warnings.warn( f"Chunking configuration is missing for the following groups: {_uncovered}."
                  f" Default chunking configuration will be used for these groups.", UserWarning    )