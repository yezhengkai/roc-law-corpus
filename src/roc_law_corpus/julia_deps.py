from pathlib import Path

import juliapkg

# ref: https://github.com/cjdoris/pyjuliapkg
JULIA_COMPAT = "1.9"
JULIAPKG_JSON = Path(juliapkg.project()).joinpath("pyjuliapkg", "juliapkg.json")
JULIA_DEPS = [
    {
        "pkg": "JSON",
        "uuid": "682c06a0-de6a-54ab-a142-c8b1cf79cde6",
        "dev": False,
        "version": "0.21.4",
        "path": None,
        "url": None,
        "rev": None,
        "target": JULIAPKG_JSON,
    },
    {
        "pkg": "CorpusCleanerForTWLaws",
        "uuid": "32148328-147a-4c3a-aded-c727b77b4e74",
        "dev": False,
        "version": "0.1.1",
        "path": None,
        "url": "https://github.com/okatsn/CorpusCleanerForTWLaws.jl",
        "rev": None,
        "target": JULIAPKG_JSON,
    },
]


def instantiate() -> None:
    juliapkg.require_julia(JULIA_COMPAT, target=JULIAPKG_JSON)
    for dep in JULIA_DEPS:
        juliapkg.add(**dep)
    juliapkg.resolve()


if __name__ == "__main__":
    instantiate()
