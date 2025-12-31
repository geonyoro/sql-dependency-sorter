import pytest
from sorter import main
import os

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")

def get_sample_path(filename):
    return os.path.join(SAMPLES_DIR, filename)

def test_simple_no_dependencies(capsys):
    main(get_sample_path("simple.sql"))
    captured = capsys.readouterr()
    # The order of these is determined by their appearance in the file
    assert captured.out.find("`TABLE_A`") < captured.out.find('"table_b"')
    assert captured.out.find('"table_b"') < captured.out.find("'Table_C'")

def test_simple_dependencies(capsys):
    main(get_sample_path("dependencies.sql"))
    captured = capsys.readouterr()
    # Correct dependency order: TABLE_A -> TABLE_B -> Table_C
    assert captured.out.find("'TABLE_A'") < captured.out.find("`TABLE_B`")
    assert captured.out.find("`TABLE_B`") < captured.out.find('"Table_C"')
def test_multiple_dependencies(capsys):
    main(get_sample_path("multiple_dependencies.sql"))
    captured = capsys.readouterr()
    # Normalized: table_a, table_b, table_c, table_d. Order of a,b can vary.
    assert captured.out.find("'TABLE_A'") < captured.out.find('"Table_C"')
    assert captured.out.find("'TABLE_A'") < captured.out.find("`Table_D`")
    assert captured.out.find("`TABLE_B`") < captured.out.find("`Table_D`")
def test_circular_dependency():
    with pytest.raises(ValueError, match="Cannot sort dependencies"):
        main(get_sample_path("circular.sql"))

def test_missing_dependency():
    with pytest.raises(ValueError, match="Cannot sort dependencies"):
        main(get_sample_path("missing.sql"))

def test_schema_qualified(capsys):
    main(get_sample_path("schema_qualified.sql"))
    captured = capsys.readouterr()
    # Correct dependency order: table_x -> table_y -> table_z
    assert captured.out.find('"my_schema"."table_x"') < captured.out.find('public."table_y"')
    assert captured.out.find('public."table_y"') < captured.out.find('`another_schema`.`table_z`')

