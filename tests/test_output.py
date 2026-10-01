import pytest

from device_icons.output import clear, code, stacked, table


class TestTable:
    def test_renders_a_header_a_rule_and_a_row_per_entry(self):
        result = table(("Model identifier", "Kind"), ("---", ":-:"), [("Xserve3,1", "Mac")], horizontal=False)

        assert result == ["| Model identifier | Kind |", "| --- | :-: |", "| `Xserve3,1` | Mac |"]

    def test_leaves_the_first_cell_empty_for_none(self):
        result = table(("Model identifier", "Kind"), ("---", ":-:"), [(None, "Mac")], horizontal=False)

        assert result[-1] == "|  | Mac |"

    class TestOnHorizontal:
        def test_lays_out_a_column_per_entry(self):
            rows = [("Xserve3,1", "Mac"), ("MacPro7,1@ECOLOR=226,226,224", "Mac")]

            result = table(("Model identifier", "Kind"), ("---", ":-:"), rows, horizontal=True)

            assert result == [
                "| Model identifier | `Xserve3,1` | `MacPro7,1`<br/>`@ECOLOR=`<br/>`226,226,224` |",
                "| --- | :-: | :-: |",
                "| Kind | Mac | Mac |",
            ]

        def test_leaves_the_header_cell_empty_for_none(self):
            result = table(("Model identifier", "Kind"), ("---", ":-:"), [(None, "Mac")], horizontal=True)

            assert result[0] == "| Model identifier |  |"


class TestCode:
    def test_sets_text_in_backticks(self):
        result = code("com.apple.xserve")

        assert result == "`com.apple.xserve`"

    def test_is_empty_for_none(self):
        result = code(None)

        assert result == ""


class TestStacked:
    def test_keeps_a_plain_identifier_on_one_line(self):
        result = stacked("Xserve3,1")

        assert result == "`Xserve3,1`"

    def test_breaks_a_colour_variant_onto_three_lines(self):
        result = stacked("MacPro7,1@ECOLOR=226,226,224")

        assert result == "`MacPro7,1`<br/>`@ECOLOR=`<br/>`226,226,224`"

    def test_is_empty_for_none(self):
        result = stacked(None)

        assert result == ""


class TestClear:
    def test_creates_a_missing_directory(self, tmp_path):
        out = tmp_path / "out"

        clear(out, OURS, LEAD)

        assert out.is_dir()
        assert not any(out.iterdir())

    def test_accepts_an_empty_directory(self, tmp_path):
        clear(tmp_path, OURS, LEAD)

        assert tmp_path.is_dir()

    def test_empties_an_earlier_run(self, tmp_path):
        (tmp_path / "index.json").write_text("{}")
        (tmp_path / "README.md").write_text(f"{LEAD}\n\n| a |\n")
        (tmp_path / "icons").mkdir()
        (tmp_path / "icons" / "a.png").write_bytes(b"")
        (tmp_path / ".DS_Store").write_bytes(b"")

        clear(tmp_path, OURS, LEAD)

        assert [path.name for path in tmp_path.iterdir()] == [".DS_Store"]

    def test_refuses_a_readme_without_the_lead(self, tmp_path):
        (tmp_path / "index.json").write_text("{}")
        (tmp_path / "README.md").write_text("# Icons\n")

        with pytest.raises(SystemExit, match="not an earlier run"):
            clear(tmp_path, OURS, LEAD)

        assert (tmp_path / "README.md").read_text() == "# Icons\n"

    def test_refuses_a_directory_with_foreign_content(self, tmp_path):
        (tmp_path / "index.json").write_text("{}")
        (tmp_path / "thesis.tex").write_text("")

        with pytest.raises(SystemExit, match="not an earlier run"):
            clear(tmp_path, OURS, LEAD)

        assert (tmp_path / "thesis.tex").is_file()
        assert (tmp_path / "index.json").is_file()

    def test_refuses_a_file(self, tmp_path):
        file = tmp_path / "out"
        file.write_text("")

        with pytest.raises(SystemExit, match="not a directory"):
            clear(file, OURS, LEAD)


OURS = ("index.json", "README.md", "icons")
LEAD = "The icons, written by a test."
