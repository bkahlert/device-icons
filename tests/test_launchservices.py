import pytest

from device_icons.launchservices import preferred_type_identifiers


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
