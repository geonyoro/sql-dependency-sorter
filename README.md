# SQL Dependency Sorter

This script `sorter.py` sorts a file containing SQL `CREATE TABLE` statements based on their dependencies. It ensures that tables referenced by foreign keys are defined before the tables that reference them.

## Features

-   Parses `CREATE TABLE` statements and extracts table names and foreign key references.
-   Handles various SQL syntaxes for table names, including:
    -   Different casing (e.g., `table_name`, `TABLE_NAME`).
    -   Quoted identifiers (e.g., `"table_name"`, `'table_name'`, `` `table_name` ``).
    -   Schema-qualified names (e.g., `schema.table_name`, `"schema"."table_name"`).
-   Outputs `CREATE TABLE` statements in a valid order, respecting dependencies.
-   Detects and reports circular dependencies or unresolved dependencies.

## Usage

To use the script, run it with the SQL file as an argument:

```bash
python sorter.py your_sql_file.sql > sorted_output.sql
```

The sorted SQL statements will be printed to standard output, which you can redirect to a new file.

## Examples

You can find example SQL files demonstrating various scenarios in the `tests/samples/` directory, including:
-   `simple.sql`: Basic tables with no dependencies.
-   `dependencies.sql`: A simple chain of dependencies.
-   `multiple_dependencies.sql`: Tables with multiple foreign key references.
-   `circular.sql`: Demonstrates a circular dependency (will raise an error).
-   `missing.sql`: Demonstrates a missing dependency (will raise an error).
-   `schema_qualified.sql`: Examples of schema-qualified table names.

## Development and Testing

The project includes a comprehensive test suite using `pytest` to ensure the correct functionality of the dependency sorter.

### Running Tests

1.  **Install pytest:**
    If you don't have `pytest` installed, you can install it using pip:
    ```bash
    python3 -m pip install pytest
    ```

2.  **Execute tests:**
    Navigate to the project's root directory and run `pytest`:
    ```bash
    python3 -m pytest tests/
    ```

    All tests should pass, confirming the script's ability to handle various SQL syntax and dependency scenarios.
