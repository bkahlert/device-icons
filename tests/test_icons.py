import json
import re
from pathlib import Path

import pytest

from device_icons import coretypes
from device_icons.icons import DROPPED, LEAD, Layout, Placement, Row, declared, icons, layout, markdown, write


class TestLayout:
    def test_groups_the_icons_under_their_sidebar_icon(self):
        placements = {
            "com.apple.xserve-xeon": Placement("com.apple.xserve-xeon", XSERVE, SIDEBAR_MACPRO),
            "com.apple.macpro-2019": Placement("com.apple.macpro-2019", MACPRO, SIDEBAR_MACPRO),
        }

        result = layout(placements, {"Xserve3,1": "com.apple.xserve-xeon", "MacPro7,1": "com.apple.macpro-2019"})

        assert result.sidebars == {
            "SidebarMacPro": {
                "sidebar_icon": "sidebar/SidebarMacPro.png",
                "icons": {
                    "com.apple.macpro-2019": {
                        "icon": "icons/com.apple.macpro-2019.png",
                        "type_identifiers": ["com.apple.macpro-2019"],
                        "model_identifiers": ["MacPro7,1"],
                    },
                    "com.apple.xserve": {
                        "icon": "icons/com.apple.xserve.png",
                        "type_identifiers": ["com.apple.xserve-xeon"],
                        "model_identifiers": ["Xserve3,1"],
                    },
                },
            }
        }

    def test_merges_types_that_share_an_icon(self):
        placements = {
            "com.apple.xserve-xeon": Placement("com.apple.xserve-xeon", XSERVE, SIDEBAR_MACPRO),
            "com.apple.xserve": Placement("com.apple.xserve", XSERVE, SIDEBAR_MACPRO),
        }

        result = layout(placements, {"Xserve3,1": "com.apple.xserve-xeon", "RackMac": "com.apple.xserve", "Xserve": "com.apple.xserve"})

        assert result.sidebars["SidebarMacPro"]["icons"]["com.apple.xserve"] == {
            "icon": "icons/com.apple.xserve.png",
            "type_identifiers": ["com.apple.xserve", "com.apple.xserve-xeon"],
            "model_identifiers": ["RackMac", "Xserve", "Xserve3,1"],
        }

    def test_maps_the_files_links_and_folders_to_write(self):
        placements = {"com.apple.xserve-xeon": Placement("com.apple.xserve-xeon", XSERVE, SIDEBAR_MACPRO)}

        result = layout(placements, {"Xserve3,1": "com.apple.xserve-xeon"})

        assert result.files == {Path("icons/com.apple.xserve.png"): XSERVE, Path("sidebar/SidebarMacPro.png"): SIDEBAR_MACPRO}
        assert result.links == {Path("by-sidebar/SidebarMacPro/com.apple.xserve.png"): Path("icons/com.apple.xserve.png")}
        assert result.folders == {Path("by-sidebar/SidebarMacPro"): Path("sidebar/SidebarMacPro.png")}

    def test_names_an_embedded_sidebar_icon_after_its_icon_file(self):
        placements = {"com.apple.macpro-2019": Placement("com.apple.macpro-2019", MACPRO, MACPRO_EMBEDDED_SIDEBAR)}

        result = layout(placements, {"MacPro7,1": "com.apple.macpro-2019"})

        assert set(result.sidebars) == {"com.apple.macpro-2019"}
        assert result.files[Path("sidebar/com.apple.macpro-2019.png")] == MACPRO_EMBEDDED_SIDEBAR

    def test_keeps_a_type_no_model_identifier_resolves_to(self):
        placements = {"com.apple.xserve-xeon": Placement("com.apple.xserve-xeon", XSERVE, SIDEBAR_MACPRO)}

        result = layout(placements, {})

        assert result.sidebars["SidebarMacPro"]["icons"]["com.apple.xserve"]["model_identifiers"] == []

    def test_lists_a_row_per_model_identifier(self):
        placements = {"com.apple.xserve-xeon": Placement("com.apple.xserve-xeon", XSERVE, SIDEBAR_MACPRO, kind="Mac")}

        result = layout(placements, {"Xserve3,1": "com.apple.xserve-xeon", "RackMac": "com.apple.xserve-xeon", "J120AP": None})

        assert result.rows == [
            Row("RackMac", "com.apple.xserve-xeon", "Mac", Path("icons/com.apple.xserve.png"), Path("sidebar/SidebarMacPro.png")),
            Row("Xserve3,1", "com.apple.xserve-xeon", "Mac", Path("icons/com.apple.xserve.png"), Path("sidebar/SidebarMacPro.png")),
        ]

    def test_groups_the_rows_by_sidebar_icon_then_sorts_by_model_identifier(self):
        placements = {
            "com.apple.xserve-xeon": Placement("com.apple.xserve-xeon", XSERVE, SIDEBAR_MACPRO),
            "com.apple.macpro-2019": Placement("com.apple.macpro-2019", MACPRO, MACPRO_EMBEDDED_SIDEBAR),
        }

        result = layout(placements, {"Xserve3,1": "com.apple.xserve-xeon", "MacPro7,1": "com.apple.macpro-2019", "RackMac": "com.apple.xserve-xeon"})

        assert [(row.sidebar_icon.stem, row.model_identifier) for row in result.rows] == [
            ("SidebarMacPro", "RackMac"),
            ("SidebarMacPro", "Xserve3,1"),
            ("com.apple.macpro-2019", "MacPro7,1"),
        ]

    class TestDropped:
        def test_lists_every_reason_even_when_empty(self):
            result = layout({}, {})

            assert result.dropped == {reason: [] for reason in DROPPED}

        def test_drops_a_model_identifier_without_type(self):
            result = layout({}, {"J120AP": None})

            assert result.dropped["no type"] == ["J120AP"]

        def test_drops_a_model_identifier_whose_type_has_no_icon(self):
            placements = {"com.apple.watch": Placement("com.apple.watch", None, SIDEBAR_MACPRO)}

            result = layout(placements, {"Watch8,2": "com.apple.watch"})

            assert result.dropped["no icon"] == ["Watch8,2"]
            assert result.sidebars == {}

        def test_drops_a_model_identifier_whose_type_has_no_sidebar_icon(self):
            placements = {"com.apple.watch": Placement("com.apple.watch", XSERVE, None)}

            result = layout(placements, {"Watch8,2": "com.apple.watch"})

            assert result.dropped["no sidebar icon"] == ["Watch8,2"]
            assert result.sidebars == {}

        def test_sorts_the_dropped(self):
            result = layout({}, {"b": None, "a": None})

            assert result.dropped["no type"] == ["a", "b"]


class TestDeclared:
    def test_maps_a_preferred_type_identifier_onto_the_declared_one_ignoring_case(self):
        result = declared({"J120AP": "com.apple.ipad-pro-a1670-1"}, ["com.apple.ipad-pro-A1670-1"])

        assert result == {"J120AP": "com.apple.ipad-pro-A1670-1"}

    def test_maps_an_undeclared_type_identifier_onto_none(self):
        result = declared({"Foo1,1": "dyn.age4d4vxtr62z2pbv"}, ["com.apple.mac"])

        assert result == {"Foo1,1": None}


class TestMarkdown:
    def test_starts_with_the_lead_that_marks_it_as_ours(self):
        result = markdown([])

        assert result.startswith(LEAD)

    def test_renders_a_table_with_a_row_per_model_identifier(self):
        rows = [Row("Xserve3,1", "com.apple.xserve-xeon", "Mac", Path("icons/com.apple.xserve.png"), Path("sidebar/SidebarXserve.png"))]

        result = markdown(rows)

        assert result.splitlines()[-3:] == [
            "| Model identifier | Type identifier | Kind | Icon | Sidebar icon |",
            "| --- | --- | --- | :-: | :-: |",
            '| `Xserve3,1` | `com.apple.xserve-xeon` | Mac | <img src="icons/com.apple.xserve.png" alt="com.apple.xserve" width="128"> | <img src="sidebar/SidebarXserve.png" alt="SidebarXserve" width="32"> |',
        ]

    class TestOnHorizontal:
        def test_lays_out_a_column_per_model_identifier(self):
            rows = [
                Row("Xserve3,1", "com.apple.xserve-xeon", "Mac", Path("icons/com.apple.xserve.png"), Path("sidebar/SidebarXserve.png")),
                Row(
                    "MacPro7,1@ECOLOR=226,226,224",
                    "com.apple.macpro-2019-rackmount",
                    "Mac",
                    Path("icons/com.apple.macpro-2019-rackmount.png"),
                    Path("sidebar/com.apple.macpro-2019-rackmount.png"),
                ),
            ]

            result = markdown(rows, horizontal=True)

            assert result.splitlines()[-6:] == [
                "| Model identifier | `Xserve3,1` | `MacPro7,1`<br/>`@ECOLOR=`<br/>`226,226,224` |",
                "| --- | :-: | :-: |",
                "| Type identifier | `com.apple.xserve-xeon` | `com.apple.macpro-2019-rackmount` |",
                "| Kind | Mac | Mac |",
                '| Icon | <img src="icons/com.apple.xserve.png" alt="com.apple.xserve" width="128"> | <img src="icons/com.apple.macpro-2019-rackmount.png" alt="com.apple.macpro-2019-rackmount" width="128"> |',
                '| Sidebar icon | <img src="sidebar/SidebarXserve.png" alt="SidebarXserve" width="32"> | <img src="sidebar/com.apple.macpro-2019-rackmount.png" alt="com.apple.macpro-2019-rackmount" width="32"> |',
            ]


class TestWrite:
    def test_writes_the_files_links_and_index(self, tmp_path):
        source = tmp_path / "w" / "com.apple.xserve.iconset" / "icon_512x512@2x.png"
        sidebar = tmp_path / "w" / "SidebarMacPro.iconset" / "icon_32x32@2x.png"
        for path, content in ((source, b"icon"), (sidebar, b"sidebar")):
            path.parent.mkdir(parents=True)
            path.write_bytes(content)
        out = tmp_path / "out"
        laid = Layout(
            sidebars={"SidebarMacPro": {"sidebar_icon": "sidebar/SidebarMacPro.png", "icons": {}}},
            dropped={"no type": ["J120AP"], "no icon": [], "no sidebar icon": []},
            files={Path("icons/com.apple.xserve.png"): source, Path("sidebar/SidebarMacPro.png"): sidebar},
            links={Path("by-sidebar/SidebarMacPro/com.apple.xserve.png"): Path("icons/com.apple.xserve.png")},
            folders={Path("by-sidebar/SidebarMacPro"): Path("sidebar/SidebarMacPro.png")},
            rows=[Row("Xserve3,1", "com.apple.xserve-xeon", "Mac", Path("icons/com.apple.xserve.png"), Path("sidebar/SidebarMacPro.png"))],
        )

        write(out, laid)

        link = out / "by-sidebar" / "SidebarMacPro" / "com.apple.xserve.png"
        assert (out / "icons" / "com.apple.xserve.png").read_bytes() == b"icon"
        assert (out / "sidebar" / "SidebarMacPro.png").read_bytes() == b"sidebar"
        assert link.is_symlink()
        assert link.readlink() == Path("../../icons/com.apple.xserve.png")
        assert link.read_bytes() == b"icon"
        assert json.loads((out / "index.json").read_text()) == {"sidebars": laid.sidebars, "dropped": laid.dropped}
        assert (out / "README.md").read_text() == markdown(laid.rows)

    class TestOnHorizontal:
        def test_lays_the_table_out_by_column(self, tmp_path):
            rows = [Row("Xserve3,1", "com.apple.xserve-xeon", "Mac", Path("icons/com.apple.xserve.png"), Path("sidebar/SidebarMacPro.png"))]

            write(tmp_path / "out", Layout(rows=rows), horizontal=True)

            assert (tmp_path / "out" / "README.md").read_text() == markdown(rows, horizontal=True)


@pytest.mark.macos
class TestDump:
    def test_writes_the_given_types_with_the_model_identifiers_that_resolve_to_them(self, tmp_path):
        out = tmp_path / "out"

        result = icons(out, ["com.apple.xserve-xeon"])

        index = json.loads((out / "index.json").read_text())
        entry = index["sidebars"]["SidebarXserve"]["icons"]["com.apple.xserve"]
        assert entry["type_identifiers"] == ["com.apple.xserve-xeon"]
        assert "Xserve3,1" in entry["model_identifiers"]
        assert (out / "icons" / "com.apple.xserve.png").stat().st_size > 0
        assert (out / "sidebar" / "SidebarXserve.png").stat().st_size > 0
        assert (out / "by-sidebar" / "SidebarXserve" / "com.apple.xserve.png").is_symlink()
        assert (out / "by-sidebar" / "SidebarXserve" / "Icon\r").exists()
        assert result.startswith(f"{len(entry['model_identifiers'])} model identifiers")

    def test_writes_the_table(self, tmp_path):
        out = tmp_path / "out"

        icons(out, ["com.apple.xserve-xeon"])

        assert "| `Xserve3,1` | `com.apple.xserve-xeon` | Mac | <img" in (out / "README.md").read_text()

    class TestOnModelIdentifiers:
        def test_writes_only_those_with_the_types_they_resolve_to(self, tmp_path):
            out = tmp_path / "out"

            result = icons(out, model_identifiers=["Xserve3,1", "MacPro7,1"])

            index = json.loads((out / "index.json").read_text())
            placed = sorted(name for group in index["sidebars"].values() for entry in group["icons"].values() for name in entry["model_identifiers"])
            assert placed == ["MacPro7,1", "Xserve3,1"]
            assert result.startswith("2 model identifiers: 2 placed under 2 sidebar icons and 2 icons")

        def test_refuses_one_that_is_not_declared(self, tmp_path):
            with pytest.raises(SystemExit, match=r"^not declared in .*: Foo1,1$"):
                icons(tmp_path / "out", model_identifiers=["Xserve3,1", "Foo1,1"])

        def test_refuses_a_display_as_its_type_is_no_device(self, tmp_path):
            # A display's type conforms to public.display, not to public.device as LaunchServices is asked; which
            # displays are declared differs between macOS versions.
            declarations = coretypes.read(coretypes.BUNDLE)
            displays = sorted(
                name
                for declaration in declarations.values()
                if "public.display" in coretypes.ancestors(declaration, declarations)
                for name in declaration.model_identifiers
            )
            if not displays:
                pytest.skip("no display declared on this macOS")

            with pytest.raises(SystemExit, match=rf"^no type in .*: {re.escape(displays[0])}$"):
                icons(tmp_path / "out", model_identifiers=[displays[0]])

        def test_refuses_one_whose_type_has_no_sidebar_icon(self, tmp_path):
            with pytest.raises(SystemExit, match=r"^no sidebar icon in .*: Watch7,1$"):
                icons(tmp_path / "out", model_identifiers=["Watch7,1"])

    def test_refuses_a_type_that_is_not_declared(self, tmp_path):
        with pytest.raises(SystemExit, match="com.apple.no-such-device"):
            icons(tmp_path / "out", ["com.apple.no-such-device"])

    def test_refuses_a_type_without_sidebar_icon_naming_what_is_missing(self, tmp_path):
        with pytest.raises(SystemExit, match=r"^no sidebar icon in .*: com\.apple\.device$"):
            icons(tmp_path / "out", ["com.apple.device"])


XSERVE = Path("/w/com.apple.xserve.iconset/icon_512x512@2x.png")
MACPRO = Path("/w/com.apple.macpro-2019.iconset/icon_512x512@2x.png")
MACPRO_EMBEDDED_SIDEBAR = Path("/w/com.apple.macpro-2019.iconset/template_32x32@2x.png")
SIDEBAR_MACPRO = Path("/w/SidebarMacPro.iconset/icon_32x32@2x.png")
