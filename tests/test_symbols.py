import json
from pathlib import Path

import pytest

from device_icons.coreglyphs import CLOSE, LINE, MOVE, Layer, Outline, svg
from device_icons.symbols import DROPPED, LEAD, Layout, Row, layout, markdown, symbols, write


class TestLayout:
    def test_places_a_symbol_with_the_types_and_model_identifiers_that_get_it(self):
        names = {"com.apple.macpro-2019": "macpro.gen3"}

        result = layout(names, {"MacPro7,1": "com.apple.macpro-2019"}, {"macpro.gen3": SQUARE}, [])

        assert result.symbols == {
            "macpro.gen3": {"symbol": "symbols/macpro.gen3.svg", "type_identifiers": ["com.apple.macpro-2019"], "model_identifiers": ["MacPro7,1"]}
        }

    def test_merges_types_that_share_a_symbol(self):
        names = {"com.apple.macpro-2019-rackmount": "macpro.gen3", "com.apple.macpro-2019": "macpro.gen3"}
        resolved = {"MacPro7,1@ECOLOR=226,226,224": "com.apple.macpro-2019-rackmount", "MacPro7,1": "com.apple.macpro-2019"}

        result = layout(names, resolved, {"macpro.gen3": SQUARE}, [])

        assert result.symbols["macpro.gen3"]["type_identifiers"] == ["com.apple.macpro-2019", "com.apple.macpro-2019-rackmount"]
        assert result.symbols["macpro.gen3"]["model_identifiers"] == ["MacPro7,1", "MacPro7,1@ECOLOR=226,226,224"]
        assert list(result.files) == [Path("symbols/macpro.gen3.svg")]

    def test_maps_the_file_to_write_onto_its_svg(self):
        result = layout({"com.apple.macpro-2019": "macpro.gen3"}, {}, {"macpro.gen3": SQUARE}, [])

        assert result.files == {Path("symbols/macpro.gen3.svg"): svg("macpro.gen3", SQUARE)}

    def test_keeps_a_type_no_model_identifier_resolves_to(self):
        result = layout({"com.apple.macpro-2019": "macpro.gen3"}, {}, {"macpro.gen3": SQUARE}, [])

        assert result.symbols["macpro.gen3"]["model_identifiers"] == []
        assert result.rows == []

    def test_lists_a_row_per_model_identifier(self):
        names = {"com.apple.xserve-xeon": "xserve"}

        result = layout(names, {"Xserve3,1": "com.apple.xserve-xeon", "RackMac": "com.apple.xserve-xeon", "J120AP": None}, {"xserve": SQUARE}, [])

        assert result.rows == [
            Row("RackMac", "com.apple.xserve-xeon", "xserve", Path("symbols/xserve.svg")),
            Row("Xserve3,1", "com.apple.xserve-xeon", "xserve", Path("symbols/xserve.svg")),
        ]

    def test_groups_the_rows_by_symbol_name_then_sorts_by_model_identifier(self):
        names = {"com.apple.xserve-xeon": "xserve", "com.apple.macpro-2019": "macpro.gen3"}
        resolved = {"Xserve3,1": "com.apple.xserve-xeon", "MacPro7,1": "com.apple.macpro-2019", "RackMac": "com.apple.xserve-xeon"}

        result = layout(names, resolved, {"xserve": SQUARE, "macpro.gen3": SQUARE}, [])

        assert [(row.symbol_name, row.model_identifier) for row in result.rows] == [
            ("macpro.gen3", "MacPro7,1"),
            ("xserve", "RackMac"),
            ("xserve", "Xserve3,1"),
        ]

    def test_sorts_the_symbols(self):
        names = {"com.apple.xserve-xeon": "xserve", "com.apple.macpro-2019": "macpro.gen3"}

        result = layout(names, {}, {"xserve": SQUARE, "macpro.gen3": SQUARE}, [])

        assert list(result.symbols) == ["macpro.gen3", "xserve"]

    class TestOnGivenNames:
        def test_places_a_given_name_no_type_declares_with_a_row_of_its_own(self):
            result = layout({}, {}, {"xserve.raid": SQUARE}, ["xserve.raid"])

            assert result.symbols == {"xserve.raid": {"symbol": "symbols/xserve.raid.svg", "type_identifiers": [], "model_identifiers": []}}
            assert result.rows == [Row(None, None, "xserve.raid", Path("symbols/xserve.raid.svg"))]
            assert result.files == {Path("symbols/xserve.raid.svg"): svg("xserve.raid", SQUARE)}

        def test_gives_a_given_name_a_model_identifier_gets_no_extra_row(self):
            names = {"com.apple.xserve-xeon": "xserve"}

            result = layout(names, {"Xserve3,1": "com.apple.xserve-xeon"}, {"xserve": SQUARE}, ["xserve"])

            assert result.rows == [Row("Xserve3,1", "com.apple.xserve-xeon", "xserve", Path("symbols/xserve.svg"))]

        def test_lists_a_given_name_once_however_often_it_is_given(self):
            result = layout({}, {}, {"pc": SQUARE}, ["pc", "pc"])

            assert len(result.rows) == 1
            assert list(result.symbols) == ["pc"]

    class TestDropped:
        def test_lists_every_reason_even_when_empty(self):
            result = layout({}, {}, {}, [])

            assert result.dropped == {reason: [] for reason in DROPPED}

        def test_drops_a_model_identifier_without_type(self):
            result = layout({}, {"J120AP": None}, {}, [])

            assert result.dropped["no type"] == ["J120AP"]

        def test_drops_a_model_identifier_whose_type_has_no_symbol_name(self):
            result = layout({"com.apple.powermac": None}, {"PowerMac7,2": "com.apple.powermac"}, {}, [])

            assert result.dropped["no symbol name"] == ["PowerMac7,2"]
            assert result.symbols == {}

        def test_drops_a_model_identifier_whose_symbol_name_has_no_symbol(self):
            names = {"com.apple.iphone-v68": "BA5F95BD205B47E982C16A26E541251A"}

            result = layout(names, {"iPhone18,3": "com.apple.iphone-v68"}, {"BA5F95BD205B47E982C16A26E541251A": None}, [])

            assert result.dropped["no symbol"] == ["iPhone18,3"]
            assert result.symbols == {}
            assert result.files == {}

        def test_sorts_the_dropped(self):
            result = layout({}, {"b": None, "a": None}, {}, [])

            assert result.dropped["no type"] == ["a", "b"]


class TestMarkdown:
    def test_starts_with_the_lead_that_marks_it_as_ours(self):
        result = markdown([])

        assert result.startswith(LEAD)

    def test_renders_a_table_with_a_row_per_model_identifier(self):
        rows = [Row("Xserve3,1", "com.apple.xserve-xeon", "xserve", Path("symbols/xserve.svg"))]

        result = markdown(rows)

        assert result.splitlines()[-3:] == [
            "| Model identifier | Type identifier | Symbol name | Symbol |",
            "| --- | --- | --- | :-: |",
            '| `Xserve3,1` | `com.apple.xserve-xeon` | `xserve` | <img src="symbols/xserve.svg" alt="xserve" width="64"> |',
        ]

    def test_leaves_the_identifier_cells_of_a_symbol_without_model_identifier_empty(self):
        rows = [Row(None, None, "xserve.raid", Path("symbols/xserve.raid.svg"))]

        result = markdown(rows)

        assert result.splitlines()[-1] == '|  |  | `xserve.raid` | <img src="symbols/xserve.raid.svg" alt="xserve.raid" width="64"> |'

    class TestOnHorizontal:
        def test_lays_out_a_column_per_model_identifier(self):
            rows = [
                Row("Xserve3,1", "com.apple.xserve-xeon", "xserve", Path("symbols/xserve.svg")),
                Row("MacPro7,1@ECOLOR=226,226,224", "com.apple.macpro-2019-rackmount", "macpro.gen3", Path("symbols/macpro.gen3.svg")),
            ]

            result = markdown(rows, horizontal=True)

            assert result.splitlines()[-5:] == [
                "| Model identifier | `Xserve3,1` | `MacPro7,1`<br/>`@ECOLOR=`<br/>`226,226,224` |",
                "| --- | :-: | :-: |",
                "| Type identifier | `com.apple.xserve-xeon` | `com.apple.macpro-2019-rackmount` |",
                "| Symbol name | `xserve` | `macpro.gen3` |",
                '| Symbol | <img src="symbols/xserve.svg" alt="xserve" width="64"> | <img src="symbols/macpro.gen3.svg" alt="macpro.gen3" width="64"> |',
            ]


class TestWrite:
    def test_writes_the_files_the_index_and_the_table(self, tmp_path):
        out = tmp_path / "out"
        laid = Layout(
            symbols={"xserve": {"symbol": "symbols/xserve.svg", "type_identifiers": ["com.apple.xserve-xeon"], "model_identifiers": ["Xserve3,1"]}},
            dropped={"no type": ["J120AP"], "no symbol name": [], "no symbol": []},
            files={Path("symbols/xserve.svg"): svg("xserve", SQUARE)},
            rows=[Row("Xserve3,1", "com.apple.xserve-xeon", "xserve", Path("symbols/xserve.svg"))],
        )

        write(out, laid)

        assert (out / "symbols" / "xserve.svg").read_text() == svg("xserve", SQUARE)
        assert json.loads((out / "index.json").read_text()) == {"symbols": laid.symbols, "dropped": laid.dropped}
        assert (out / "README.md").read_text() == markdown(laid.rows)

    def test_replaces_an_earlier_run(self, tmp_path):
        out = tmp_path / "out"
        write(out, Layout(files={Path("symbols/old.svg"): svg("old", SQUARE)}))

        write(out, Layout(files={Path("symbols/new.svg"): svg("new", SQUARE)}))

        assert [path.name for path in (out / "symbols").iterdir()] == ["new.svg"]

    def test_refuses_an_earlier_dump(self, tmp_path):
        out = tmp_path / "out"
        (out / "icons").mkdir(parents=True)
        (out / "index.json").write_text("{}")

        with pytest.raises(SystemExit, match="not an earlier run"):
            write(out, Layout())

        assert (out / "icons").is_dir()

    class TestOnHorizontal:
        def test_lays_the_table_out_by_column(self, tmp_path):
            rows = [Row("Xserve3,1", "com.apple.xserve-xeon", "xserve", Path("symbols/xserve.svg"))]

            write(tmp_path / "out", Layout(rows=rows), horizontal=True)

            assert (tmp_path / "out" / "README.md").read_text() == markdown(rows, horizontal=True)


@pytest.mark.macos
class TestSymbols:
    def test_writes_the_given_symbol_with_the_model_identifiers_that_get_it(self, tmp_path):
        out = tmp_path / "out"

        result = symbols(out, ["macpro.gen3"])

        index = json.loads((out / "index.json").read_text())
        entry = index["symbols"]["macpro.gen3"]
        assert "com.apple.macpro-2019" in entry["type_identifiers"]
        assert "MacPro7,1" in entry["model_identifiers"]
        assert list(index["symbols"]) == ["macpro.gen3"]
        assert (out / "symbols" / "macpro.gen3.svg").read_text().startswith('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ')
        assert result.startswith(f"{len(entry['model_identifiers'])} model identifiers: {len(entry['model_identifiers'])} placed under 1 symbols in ")

    def test_writes_the_table(self, tmp_path):
        out = tmp_path / "out"

        symbols(out, ["macpro.gen3"])

        assert "| `MacPro7,1` | `com.apple.macpro-2019` | `macpro.gen3` | <img" in (out / "README.md").read_text()

    def test_writes_a_given_symbol_no_device_type_declares(self, tmp_path):
        out = tmp_path / "out"

        result = symbols(out, ["xserve.raid"])

        assert json.loads((out / "index.json").read_text())["symbols"]["xserve.raid"]["model_identifiers"] == []
        assert "|  |  | `xserve.raid` | <img" in (out / "README.md").read_text()
        assert result.startswith("0 model identifiers: 0 placed under 1 symbols in ")

    def test_writes_a_symbol_declared_by_a_legacy_name_under_its_current_name(self, tmp_path):
        out = tmp_path / "out"

        symbols(out, ["visionpro"])

        index = json.loads((out / "index.json").read_text())
        assert list(index["symbols"]) == ["vision.pro"]
        assert index["symbols"]["vision.pro"]["model_identifiers"]
        assert (out / "symbols" / "vision.pro.svg").is_file()

    def test_lists_the_model_identifiers_of_a_renamed_symbol_under_its_current_name_too(self, tmp_path):
        out = tmp_path / "out"

        symbols(out, ["vision.pro"])

        assert json.loads((out / "index.json").read_text())["symbols"]["vision.pro"]["model_identifiers"]

    def test_refuses_a_symbol_name_the_catalog_lacks(self, tmp_path):
        out = tmp_path / "out"

        with pytest.raises(SystemExit, match=r"^no symbol in .*: no\.such\.symbol$"):
            symbols(out, ["macpro.gen3", "no.such.symbol"])

        assert not out.exists()

    def test_writes_every_device_type_by_default(self, tmp_path):
        out = tmp_path / "out"

        result = symbols(out)

        index = json.loads((out / "index.json").read_text())
        placed = sum(len(entry["model_identifiers"]) for entry in index["symbols"].values())
        dropped = sum(len(identifiers) for identifiers in index["dropped"].values())
        assert {"macpro.gen3", "pc", "applewatch"} <= set(index["symbols"])
        assert "PowerMac7,2" in index["dropped"]["no symbol name"]
        assert result.startswith(f"{placed + dropped} model identifiers: {placed} placed under {len(index['symbols'])} symbols in ")


SQUARE = Outline([Layer([(MOVE, [(0.0, 0.0)]), (LINE, [(1.0, 0.0)]), (LINE, [(1.0, 1.0)]), (LINE, [(0.0, 1.0)]), (CLOSE, [])])], (0.0, 0.0, 1.0, 1.0))
