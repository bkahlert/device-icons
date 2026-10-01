import re

import pytest

from device_icons.coreglyphs import CLOSE, CURVE, LINE, MOVE, QUAD, Outline, outline, resolve, svg


class TestSvg:
    def test_keeps_the_orientation_of_the_outline(self):
        stand_below_screen = Outline([(MOVE, [(0.0, 0.0)]), (LINE, [(10.0, 0.0)]), (LINE, [(5.0, 8.0)]), (CLOSE, [])], (0.0, 0.0, 10.0, 8.0))

        result = svg(stand_below_screen)

        assert 'd="M0 0L10 0L5 8Z"' in result

    def test_writes_one_path_filled_with_current_color_in_a_tight_view_box(self):
        triangle = Outline([(MOVE, [(10.0, 20.0)]), (LINE, [(30.0, 20.0)]), (LINE, [(30.0, 60.0)]), (CLOSE, [])], (10.0, 20.0, 20.0, 40.0))

        result = svg(triangle)

        assert result == '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 40"><path fill="currentColor" d="M0 0L20 0L20 40Z"/></svg>\n'

    def test_maps_every_element_kind_to_its_command(self):
        every = Outline(
            [(MOVE, [(0.0, 0.0)]), (LINE, [(1.0, 0.0)]), (QUAD, [(1.0, 1.0), (2.0, 2.0)]), (CURVE, [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]), (CLOSE, [])],
            (0.0, 0.0, 2.0, 2.0),
        )

        result = svg(every)

        assert 'd="M0 0L1 0Q1 1 2 2C0 0 1 1 2 2Z"' in result

    def test_rounds_to_two_decimals_and_drops_trailing_zeros(self):
        curve = Outline([(MOVE, [(0.004, 1.5)]), (CURVE, [(0.0, 0.0), (1.234567, 2.5), (3.0, 3.999)])], (0.0, 0.0, 4.0, 4.0))

        result = svg(curve)

        assert 'd="M0 1.5C0 0 1.23 2.5 3 4"' in result

    def test_writes_a_negative_zero_as_zero(self):
        dot = Outline([(MOVE, [(-0.001, 0.0)])], (0.0, 0.0, 1.0, 1.0))

        result = svg(dot)

        assert 'd="M0 0"' in result


class TestResolve:
    def test_follows_an_alias_to_the_current_name(self):
        result = resolve("visionpro", {"visionpro": "vision.pro"})

        assert result == "vision.pro"

    def test_follows_a_chain_of_aliases(self):
        result = resolve("a", {"a": "b", "b": "c"})

        assert result == "c"

    def test_keeps_a_name_without_alias(self):
        result = resolve("macpro.gen3", {"visionpro": "vision.pro"})

        assert result == "macpro.gen3"

    def test_terminates_on_a_cycle(self):
        result = resolve("a", {"a": "b", "b": "a"})

        assert result in {"a", "b"}


@pytest.mark.macos
class TestOutline:
    def test_reads_the_outline_of_a_symbol(self):
        result = outline("macpro.gen3")

        assert result is not None
        assert result.elements[0][0] == MOVE
        assert result.elements[-1][0] == CLOSE
        assert result.bounds[3] > result.bounds[2] > 0

    def test_keeps_the_stand_of_the_desktop_computer_below_the_screen(self):
        result = svg(outline("desktopcomputer"))

        points = [(float(match["x"]), float(match["y"])) for match in COORDINATES.finditer(result.split('d="')[1])]
        height = max(y for _, y in points)
        top = [x for x, y in points if y <= 0.02 * height]
        bottom = [x for x, y in points if y >= 0.98 * height]
        assert max(bottom) - min(bottom) < 0.5 * (max(top) - min(top))

    def test_reads_a_symbol_by_a_legacy_name(self):
        result = outline("ipad.homebutton")

        assert result is not None

    def test_is_none_for_a_name_the_catalog_lacks(self):
        result = outline("no.such.symbol")

        assert result is None


COORDINATES = re.compile(r"(?P<x>-?\d+(?:\.\d+)?) (?P<y>-?\d+(?:\.\d+)?)")
