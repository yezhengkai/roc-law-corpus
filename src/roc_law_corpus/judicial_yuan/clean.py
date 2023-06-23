import sys

from juliacall import Main as jl


def import_jl_packages() -> None:
    jl.seval("using JSON")
    jl.seval("using CorpusCleanerForTWLaws")


def load_corpus(source_json) -> list:
    """Load corpus as a CorpusType"""
    raw_corpus = jl.JSON.Parser.parsefile(str(source_json))
    list_cps = [jl.CorpusJudicalYuan(d) for d in raw_corpus]
    return list_cps


def jl_clean_bang(list_cps):
    """Clean the corpus"""
    jl.broadcast(jl.clean_b, list_cps)


def jl_to_dict(list_cps) -> list:
    return jl.broadcast(jl.CorpusCleanerForTWLaws.Dict, list_cps)


def save2json(destination_json, list_cps) -> None:
    """Save results as JSON file"""
    io = jl.open(str(destination_json), "w")
    jl.JSON.print(io, list_cps, 2)  # indent 2 spaces
    jl.close(io)


def clean_json(source_json, destination_json):
    import_jl_packages()
    list_cps = load_corpus(source_json)
    jl_clean_bang(list_cps)
    list_cps = jl_to_dict(list_cps)
    save2json(destination_json, list_cps)


if __name__ == "__main__":
    clean_json(sys.argv[1], sys.argv[2])
