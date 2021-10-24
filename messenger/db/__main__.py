import argparse
import logging
import sys

from alembic.config import CommandLine, Config as AlembicConfig

from messenger.settings import Config


def main():
    logging.basicConfig(level=Config.Logging.level)

    alembic = CommandLine()
    alembic.parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter

    options = alembic.parser.parse_args()
    config = AlembicConfig(
        file_=options.config, ini_section=options.name, cmd_opts=options
    )

    config.set_main_option("sqlalchemy.url", f"postgresql://{Config.DB.url}")
    config.set_main_option("script_location", str(Config.base_path / "db" / "alembic"))

    sys.exit(alembic.run_cmd(config, options))


if __name__ == "__main__":
    main()
