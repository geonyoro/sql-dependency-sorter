import argparse
import re


def _normalize_table_name(name):
    # Strip quotes (double, single, backticks)
    name = name.strip("\"'`")
    # If it's schema.table, take the last part
    if "." in name:
        name = name.split(".")[-1]
    return name.lower()  # Convert to lowercase


def get_references(line) -> list:
    # This regex is still a bit simplified, but handles common quoted/unquoted names.
    # It will extract schema.table or just table, and then normalize it.
    found_refs = re.findall(r"references\s+([\"'`]?[\w\.]+[\"'`]?)", line, flags=re.I)
    return [_normalize_table_name(ref) for ref in found_refs]


def main(filename):
    """Assumes these things occur in lines."""
    with open(filename) as wfile:
        table_to_refs = {}
        table_definitions = {}
        printed_tables = []
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

        # 1, 2, 3: if 1 depends on 2, but 2 depends on 3
        # then we can only print each once the dependency is printed
        while table_to_refs:
            newly_printed_tables = []
            for table_name, refs in list(table_to_refs.items()):
                all_refs_printed = all(i in printed_tables for i in refs)
                if all_refs_printed:
                    print(table_definitions[table_name])
                    printed_tables.append(table_name)
                    newly_printed_tables.append(table_name)
                    del table_to_refs[table_name]

            if not newly_printed_tables:
                raise ValueError(
                    "Cannot sort dependencies. The following tables have circular or unresolved dependencies: "
                    + ", ".join(table_to_refs.keys())
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sort SQL CREATE TABLE statements based on foreign key dependencies."
    )
    parser.add_argument("filename", help="The SQL file to process.")
    args = parser.parse_args()
    main(args.filename)
