import argparse
import logging
import re
from pathlib import Path

LOGGER = logging.getLogger(__name__)


class CircularDependencyError(ValueError):
    """Raised when a circular dependency is detected."""

    pass


class UnresolvedDependencyError(ValueError):
    """Raised when a dependency cannot be found."""

    pass


def _normalize_table_name(name: str) -> str:
    """
    Normalize a table name by removing quotes and schema prefixes.

    Args:
        name: The raw table name (e.g., '"schema"."table"', 'schema.table', 'table').

    Returns:
        A simplified, lowercase table name.
    """
    # Strip quotes (double, single, backticks)
    name = name.strip("\"'`")
    # If it's schema.table, take the last part
    name = name.split(".")[-1]
    return name.lower()  # Convert to lowercase


def get_references(line: str) -> list[str]:
    """
    Extracts and normalizes foreign key references from a SQL line.

    Args:
        line: A line from a SQL file.

    Returns:
        A list of normalized table names that are referenced.
    """
    # This regex is still a bit simplified, but handles common quoted/unquoted names.
    # It will extract schema.table or just table, and then normalize it.
    found_refs = re.findall(r"references\s+([\"'`]?[\w\.]+[\"'`]?)", line, flags=re.I)
    return [_normalize_table_name(ref) for ref in found_refs]


def parse_sql_file(
    filename: Path,
) -> tuple[dict[str, list[str]], dict[str, str]]:
    """
    Parses a SQL file to extract table definitions and their dependencies.

    Args:
        filename: The path to the SQL file.

    Returns:
        A tuple containing two dictionaries:
        - table_to_refs: Maps each table to a list of its foreign key references.
        - table_definitions: Maps each table to its full `CREATE TABLE` statement.
    """
    table_to_refs: dict[str, list[str]] = {}
    table_definitions: dict[str, str] = {}
    with open(filename) as wfile:
        for line in wfile.readlines():
            line = re.sub(r"\s{2,}", " ", line)
            sobj = re.search(
                r"^create table\s+([\"'`]?[\w\.]+[\"'`]?)", line, flags=re.I
            )
            if not sobj:
                continue
            raw_table_name = sobj.group(1)
            table_name = _normalize_table_name(raw_table_name)
            refs = get_references(line)
            table_to_refs[table_name] = refs
            table_definitions[table_name] = line
    return table_to_refs, table_definitions


def sort_tables(
    table_to_refs: dict[str, list[str]], table_definitions: dict[str, str]
) -> list[str]:
    """
    Sorts tables based on their foreign key dependencies.

    Args:
        table_to_refs: A dictionary mapping table names to their dependencies.
        table_definitions: A dictionary mapping table names to their SQL definitions.

    Returns:
        A list of SQL table definitions, sorted by dependency.

    Raises:
        CircularDependencyError: If a circular dependency is detected.
    """
    sorted_tables = []
    printed_tables: list[str] = []

    while table_to_refs:
        newly_printed_tables = []
        for table_name, refs in list(table_to_refs.items()):
            all_refs_printed = all(i in printed_tables for i in refs)
            if all_refs_printed:
                sorted_tables.append(table_definitions[table_name])
                printed_tables.append(table_name)
                newly_printed_tables.append(table_name)
                del table_to_refs[table_name]

        if not newly_printed_tables:
            raise CircularDependencyError(
                "Cannot sort dependencies. The following tables have circular or unresolved dependencies: "
                + ", ".join(table_to_refs.keys())
            )
    return sorted_tables


def setup_logging(level: int = logging.INFO) -> None:
    """Configure logging."""
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def main(filename: str) -> None:
    """
    Main entry point for the SQL dependency sorter script.

    Args:
        filename: The path to the SQL file to process.
    """
    try:
        sql_file = Path(filename)
        if not sql_file.is_file():
            raise FileNotFoundError(f"File not found: {filename}")

        table_to_refs, table_definitions = parse_sql_file(sql_file)
        LOGGER.info(f"Found {len(table_definitions)} tables.")

        sorted_tables = sort_tables(table_to_refs, table_definitions)

        for table_sql in sorted_tables:
            print(table_sql.strip())

    except (FileNotFoundError, CircularDependencyError) as e:
        LOGGER.error(e)
        raise e


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Sort SQL CREATE TABLE statements based on foreign key dependencies."
    )
    parser.add_argument("filename", help="The SQL file to process.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging(level=logging.DEBUG if args.debug else logging.INFO)
    main(args.filename)
