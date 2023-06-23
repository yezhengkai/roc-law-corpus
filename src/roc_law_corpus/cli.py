from argparse import ArgumentParser, Namespace


def get_args_parser() -> ArgumentParser:
    """Helper function parsing the command line options."""

    parser = ArgumentParser()
    subparsers = parser.add_subparsers(description="valid subcommands", dest="subcmd")

    # Instantiate julia
    subparsers.add_parser("jl-instantiate", help="Installs julia dependencies")

    # Judicial Yuan QA
    judicial_yuan_parser = subparsers.add_parser(
        "judicial-yuan-qa", help="Operating on corpus of Judicial Yuan QA"
    )
    judicial_yuan_subparser = judicial_yuan_parser.add_subparsers(
        description="valid subcommands", dest="judicial_yuan_subcmd"
    )
    judicial_yuan_scraping_parser = judicial_yuan_subparser.add_parser(
        "scraping", help="Scraping corpus"
    )
    judicial_yuan_scraping_parser.add_argument("json", help="Path of json to be saved")
    judicial_yuan_clean_parser = judicial_yuan_subparser.add_parser(
        "clean", help="Clean corpus"
    )
    judicial_yuan_clean_parser.add_argument(
        "source_json", help="Path of json to be cleaned"
    )
    judicial_yuan_clean_parser.add_argument(
        "destination_json", help="Path of json to be exported"
    )

    # MOEX exam
    moex_parser = subparsers.add_parser("moex", help="Operating on corpus of moex exam")
    moex_subparser = moex_parser.add_subparsers(
        description="valid subcommands", dest="moex_subcmd"
    )
    moex_scraping_parser = moex_subparser.add_parser("scraping", help="Scraping pdfs")
    moex_scraping_parser.add_argument("storage_dir", help="Directory for storing pdfs")
    moex_extract_parser = moex_subparser.add_parser(
        "extract", help="Extract pdf content"
    )
    moex_extract_parser.add_argument("pdf_dir", help="Directory with pdfs")
    moex_extract_parser.add_argument(
        "destination_json", help="Path of json to be exported"
    )

    return parser


def parse_args(args) -> Namespace:
    parser = get_args_parser()
    return parser.parse_args(args)


def main(args=None):
    args = parse_args(args)
    if args.subcmd == "jl-instantiate":
        from roc_law_corpus.julia_deps import instantiate

        instantiate()
    elif args.subcmd == "judicial-yuan-qa":
        if args.judicial_yuan_subcmd == "clean":
            from roc_law_corpus.judicial_yuan.clean import clean_json

            clean_json(args.source_json, args.destination_json)
        elif args.judicial_yuan_subcmd == "scraping":
            from roc_law_corpus.judicial_yuan.scraping import main

            main(args.json)
    elif args.subcmd == "moex":
        if args.moex_subcmd == "extract":
            from roc_law_corpus.moex.extract import extract_pdf_content

            extract_pdf_content(args.pdf_dir, args.destination_json)
        elif args.moex_subcmd == "scraping":
            from roc_law_corpus.moex.scraping import main

            main(args.storage_dir)


if __name__ == "__main__":
    main()
