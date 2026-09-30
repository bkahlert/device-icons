import plistlib
from pathlib import Path

from device_icons.coretypes import TypeDeclaration, bundles, inherit, read, resource


class TestRead:
    def test_reads_every_field_of_a_declaration(self, tmp_path):
        root = bundle(tmp_path / "CoreTypes.bundle", [MACPRO_2019])

        result = read(root)

        assert result == {
            "com.apple.macpro-2019": TypeDeclaration(
                type_identifier="com.apple.macpro-2019",
                model_identifiers=("MacPro7,1", "MacPro7,1@ECOLOR=225,225,223"),
                conforms_to=("com.apple.macpro", "com.apple.mac.tower"),
                icon_file="com.apple.macpro-2019.icns",
                sidebar_icon_file="SidebarMacPro.icns",
                symbol_name="macpro.gen3",
                kind="Mac Pro",
            )
        }

    def test_reads_the_description_as_kind(self, tmp_path):
        root = bundle(tmp_path / "b", [declaration("com.apple.time-capsule", kind="Time Capsule")])

        result = read(root)

        assert result["com.apple.time-capsule"].kind == "Time Capsule"

    def test_reads_a_single_string_tag_as_one_model_identifier(self, tmp_path):
        root = bundle(tmp_path / "b", [declaration("com.apple.mac", model_identifiers="Mac", conforms_to="public.device")])

        result = read(root)

        assert result["com.apple.mac"].model_identifiers == ("Mac",)
        assert result["com.apple.mac"].conforms_to == ("public.device",)

    def test_reads_a_top_level_icon_file(self, tmp_path):
        root = bundle(tmp_path / "b", [{"UTTypeIdentifier": "public.device", "UTTypeIconFile": "GenericQuestionMarkIcon.icns"}])

        result = read(root)

        assert result["public.device"].icon_file == "GenericQuestionMarkIcon.icns"

    def test_leaves_missing_fields_empty(self, tmp_path):
        root = bundle(tmp_path / "b", [{"UTTypeIdentifier": "com.apple.device"}])

        result = read(root)

        assert result["com.apple.device"] == TypeDeclaration(type_identifier="com.apple.device")

    class TestOnNestedBundles:
        def test_reads_declarations_of_bundles_in_contents_library(self, tmp_path):
            root = bundle(tmp_path / "b", [], nested={"MobileDevices.bundle": [declaration("com.apple.ipad")]})

            result = read(root)

            assert set(result) == {"com.apple.ipad"}

        def test_keeps_the_root_declaration_of_a_duplicate_type_identifier(self, tmp_path):
            root = bundle(
                tmp_path / "b",
                [declaration("com.apple.mac", icon_file="root.icns")],
                nested={"Other.bundle": [declaration("com.apple.mac", icon_file="nested.icns")]},
            )

            result = read(root)

            assert result["com.apple.mac"].icon_file == "root.icns"

        def test_skips_a_bundle_without_info_plist(self, tmp_path):
            root = bundle(tmp_path / "b", [declaration("com.apple.mac")])
            (root / "Contents" / "Library" / "Empty.bundle").mkdir(parents=True)

            result = read(root)

            assert set(result) == {"com.apple.mac"}


class TestInherit:
    def test_returns_a_complete_declaration_unchanged(self):
        complete = TypeDeclaration("a", conforms_to=("b",), icon_file="a.icns", sidebar_icon_file="Sa.icns")
        parent = TypeDeclaration("b", icon_file="b.icns", sidebar_icon_file="Sb.icns")

        result = inherit(complete, {"a": complete, "b": parent})

        assert result == complete

    def test_takes_the_icon_file_of_the_nearest_parent(self):
        child = TypeDeclaration("c", conforms_to=("p",))
        parent = TypeDeclaration("p", conforms_to=("g",), icon_file="p.icns")
        grandparent = TypeDeclaration("g", icon_file="g.icns")

        result = inherit(child, {"c": child, "p": parent, "g": grandparent})

        assert result.icon_file == "p.icns"

    def test_takes_the_kind_of_the_nearest_parent(self):
        child = TypeDeclaration("c", conforms_to=("p",), icon_file="c.icns", sidebar_icon_file="Sc.icns")
        parent = TypeDeclaration("p", conforms_to=("g",))
        grandparent = TypeDeclaration("g", kind="Mac")

        result = inherit(child, {"c": child, "p": parent, "g": grandparent})

        assert result.kind == "Mac"

    def test_takes_the_sidebar_icon_file_from_a_farther_parent_than_the_icon_file(self):
        child = TypeDeclaration("c", conforms_to=("p",))
        parent = TypeDeclaration("p", conforms_to=("g",), icon_file="p.icns")
        grandparent = TypeDeclaration("g", icon_file="g.icns", sidebar_icon_file="Sg.icns")

        result = inherit(child, {"c": child, "p": parent, "g": grandparent})

        assert (result.icon_file, result.sidebar_icon_file) == ("p.icns", "Sg.icns")

    def test_searches_direct_parents_before_grandparents(self):
        child = TypeDeclaration("c", conforms_to=("p1", "p2"))
        p1 = TypeDeclaration("p1", conforms_to=("g",))
        p2 = TypeDeclaration("p2", icon_file="p2.icns")
        grandparent = TypeDeclaration("g", icon_file="g.icns")

        result = inherit(child, {"c": child, "p1": p1, "p2": p2, "g": grandparent})

        assert result.icon_file == "p2.icns"

    def test_ignores_unknown_parents(self):
        child = TypeDeclaration("c", conforms_to=("nowhere", "p"))
        parent = TypeDeclaration("p", icon_file="p.icns")

        result = inherit(child, {"c": child, "p": parent})

        assert result.icon_file == "p.icns"

    def test_terminates_on_a_cycle(self):
        a = TypeDeclaration("a", conforms_to=("b",))
        b = TypeDeclaration("b", conforms_to=("a",))

        result = inherit(a, {"a": a, "b": b})

        assert result == a


class TestBundles:
    def test_lists_the_root_then_the_nested_bundles_sorted(self, tmp_path):
        root = bundle(tmp_path / "b", [], nested={"Z.bundle": [], "A.bundle": []})
        (root / "Contents" / "Library" / "notes.txt").write_text("")

        result = bundles(root)

        assert result == [root, root / "Contents" / "Library" / "A.bundle", root / "Contents" / "Library" / "Z.bundle"]

    def test_lists_only_the_root_without_a_library(self, tmp_path):
        root = bundle(tmp_path / "b", [])

        result = bundles(root)

        assert result == [root]


class TestResource:
    def test_finds_the_file_in_the_first_bundle_that_has_it(self, tmp_path):
        first, second = tmp_path / "first.bundle", tmp_path / "second.bundle"
        for path in (first, second):
            (path / "Contents" / "Resources").mkdir(parents=True)
        (second / "Contents" / "Resources" / "X.icns").write_bytes(b"")

        result = resource([first, second], "X.icns")

        assert result == second / "Contents" / "Resources" / "X.icns"

    def test_is_none_when_no_bundle_has_it(self, tmp_path):
        result = resource([tmp_path], "X.icns")

        assert result is None


MACPRO_2019 = {
    "UTTypeIdentifier": "com.apple.macpro-2019",
    "UTTypeConformsTo": ["com.apple.macpro", "com.apple.mac.tower"],
    "UTTypeTagSpecification": {"com.apple.device-model-code": ["MacPro7,1", "MacPro7,1@ECOLOR=225,225,223"]},
    "UTTypeIcons": {
        "UTTypeIconFile": "com.apple.macpro-2019.icns",
        "_UTTypeTemplateIconFile": "SidebarMacPro.icns",
        "UTTypeSymbolName": "macpro.gen3",
    },
    "UTTypeDescription": "Mac Pro",
}


def declaration(type_identifier: str, **fields) -> dict:
    entry = {"UTTypeIdentifier": type_identifier}
    if "model_identifiers" in fields:
        entry["UTTypeTagSpecification"] = {"com.apple.device-model-code": fields["model_identifiers"]}
    if "conforms_to" in fields:
        entry["UTTypeConformsTo"] = fields["conforms_to"]
    if "icon_file" in fields:
        entry["UTTypeIcons"] = {"UTTypeIconFile": fields["icon_file"]}
    if "kind" in fields:
        entry["UTTypeDescription"] = fields["kind"]
    return entry


def bundle(root: Path, declarations: list[dict], nested: dict[str, list[dict]] | None = None) -> Path:
    (root / "Contents").mkdir(parents=True)
    with (root / "Contents" / "Info.plist").open("wb") as file:
        plistlib.dump({"UTExportedTypeDeclarations": declarations}, file)
    for name, entries in (nested or {}).items():
        bundle(root / "Contents" / "Library" / name, entries)
    return root
