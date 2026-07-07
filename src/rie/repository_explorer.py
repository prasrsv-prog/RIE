from rie.composition import create_repository_explorer_engine


def main() -> None:
    engine = create_repository_explorer_engine()
    engine.run()


if __name__ == "__main__":
    main()
