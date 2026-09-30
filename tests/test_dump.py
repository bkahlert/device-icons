import json
from pathlib import Path

import pytest

from device_icons.coretypes import BUNDLE
from device_icons.dump import DROPPED, Layout, Placement, clear, dump, layout, write

XSERVE = Path("/w/com.apple.xserve.iconset/icon_512x512@2x.png")
MACPRO = Path("/w/com.apple.macpro-2019.iconset/icon_512x512@2x.png")
MACPRO_EMBEDDED_SIDEBAR = Path("/w/com.apple.macpro-2019.iconset/template_32x32@2x.png")
SIDEBAR_MACPRO = Path("/w/SidebarMacPro.iconset/icon_32x32@2x.png")


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


class TestClear:
    def test_creates_a_missing_directory(self, tmp_path):
        out = tmp_path / "out"

        clear(out)

        assert out.is_dir() and not any(out.iterdir())

    def test_accepts_an_empty_directory(self, tmp_path):
        clear(tmp_path)

        assert tmp_path.is_dir()

    def test_empties_an_earlier_dump(self, tmp_path):
        (tmp_path / "index.json").write_text("{}")
        (tmp_path / "icons").mkdir()
        (tmp_path / "icons" / "a.png").write_bytes(b"")
        (tmp_path / "by-sidebar").mkdir()
        (tmp_path / ".DS_Store").write_bytes(b"")

        clear(tmp_path)

        assert [path.name for path in tmp_path.iterdir()] == [".DS_Store"]

    def test_refuses_a_directory_with_foreign_content(self, tmp_path):
        (tmp_path / "index.json").write_text("{}")
        (tmp_path / "thesis.tex").write_text("")

        with pytest.raises(SystemExit, match="not an earlier dump"):
            clear(tmp_path)

        assert (tmp_path / "thesis.tex").is_file() and (tmp_path / "index.json").is_file()

    def test_refuses_a_file(self, tmp_path):
        file = tmp_path / "out"
        file.write_text("")

        with pytest.raises(SystemExit, match="not a directory"):
            clear(file)


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
        )

        write(out, laid)

        link = out / "by-sidebar" / "SidebarMacPro" / "com.apple.xserve.png"
        assert (out / "icons" / "com.apple.xserve.png").read_bytes() == b"icon"
        assert (out / "sidebar" / "SidebarMacPro.png").read_bytes() == b"sidebar"
        assert link.is_symlink() and link.readlink() == Path("../../icons/com.apple.xserve.png") and link.read_bytes() == b"icon"
        assert json.loads((out / "index.json").read_text()) == {"sidebars": laid.sidebars, "dropped": laid.dropped}


@pytest.mark.macos
class TestDump:
    def test_writes_the_given_types_with_the_model_identifiers_that_resolve_to_them(self, tmp_path):
        out = tmp_path / "out"

        result = dump(out, ["com.apple.xserve-xeon"])

        index = json.loads((out / "index.json").read_text())
        entry = index["sidebars"]["SidebarXserve"]["icons"]["com.apple.xserve"]
        assert entry["type_identifiers"] == ["com.apple.xserve-xeon"]
        assert "Xserve3,1" in entry["model_identifiers"]
        assert (out / "icons" / "com.apple.xserve.png").stat().st_size > 0
        assert (out / "sidebar" / "SidebarXserve.png").stat().st_size > 0
        assert (out / "by-sidebar" / "SidebarXserve" / "com.apple.xserve.png").is_symlink()
        assert (out / "by-sidebar" / "SidebarXserve" / "Icon\r").exists()
        assert result.startswith(f"{len(entry['model_identifiers'])} model identifiers")

    def test_refuses_a_type_that_is_not_declared(self, tmp_path):
        with pytest.raises(SystemExit, match="com.apple.no-such-device"):
            dump(tmp_path / "out", ["com.apple.no-such-device"])

    def test_refuses_a_type_without_sidebar_icon_naming_what_is_missing(self, tmp_path):
        with pytest.raises(SystemExit, match=r"^no sidebar icon in .*: com\.apple\.device$"):
            dump(tmp_path / "out", ["com.apple.device"])
