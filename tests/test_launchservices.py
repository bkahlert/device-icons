import pytest

from device_icons.launchservices import declared, preferred_type_identifiers


class TestPreferredTypeIdentifiers:
    @pytest.mark.macos
    def test_resolves_a_model_identifier_as_finder_does(self):
        result = preferred_type_identifiers(["MacPro7,1", "Xserve3,1"])

        assert result == {"MacPro7,1": "com.apple.macpro-2019", "Xserve3,1": "com.apple.xserve-xeon"}

    @pytest.mark.macos
    def test_resolves_an_unclaimed_model_identifier_to_a_dynamic_type(self):
        result = preferred_type_identifiers(["NoSuchDevice99,9"])

        assert result["NoSuchDevice99,9"].startswith("dyn.")

    @pytest.mark.macos
    def test_resolves_a_colour_variant_to_its_own_type(self):
        result = preferred_type_identifiers(["MacPro7,1@ECOLOR=226,226,224"])

        assert result == {"MacPro7,1@ECOLOR=226,226,224": "com.apple.macpro-2019-rackmount"}

    class TestOnNoInput:
        def test_is_empty(self):
            result = preferred_type_identifiers([])

            assert result == {}


class TestDeclared:
    def test_maps_a_preferred_type_identifier_onto_the_declared_one_ignoring_case(self):
        result = declared({"J120AP": "com.apple.ipad-pro-a1670-1"}, ["com.apple.ipad-pro-A1670-1"])

        assert result == {"J120AP": "com.apple.ipad-pro-A1670-1"}

    def test_maps_an_undeclared_type_identifier_onto_none(self):
        result = declared({"Foo1,1": "dyn.age4d4vxtr62z2pbv"}, ["com.apple.mac"])

        assert result == {"Foo1,1": None}
