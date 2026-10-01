import math
import re

import pytest

from device_icons.coreglyphs import CLOSE, CURVE, LINE, MOVE, QUAD, Layer, Outline, current, outline, resolve, svg


class TestSvg:
    def test_writes_a_path_filled_with_current_color_in_a_tight_view_box(self):
        triangle = Outline([Layer([(MOVE, [(10.0, 20.0)]), (LINE, [(30.0, 20.0)]), (LINE, [(30.0, 60.0)]), (CLOSE, [])])], (10.0, 20.0, 20.0, 40.0))

        result = svg(triangle)

        assert result == '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 40"><path fill="currentColor" d="M0 0L20 0L20 40Z"/></svg>\n'

    def test_keeps_the_orientation_of_the_outline(self):
        stand_below_screen = Outline([Layer([(MOVE, [(0.0, 0.0)]), (LINE, [(10.0, 0.0)]), (LINE, [(5.0, 8.0)]), (CLOSE, [])])], (0.0, 0.0, 10.0, 8.0))

        result = svg(stand_below_screen)

        assert 'd="M0 0L10 0L5 8Z"' in result

    def test_maps_every_element_kind_to_its_command(self):
        every = Outline(
            [Layer([(MOVE, [(0.0, 0.0)]), (LINE, [(1.0, 0.0)]), (QUAD, [(1.0, 1.0), (2.0, 2.0)]), (CURVE, [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]), (CLOSE, [])])],
            UNIT,
        )

        result = svg(every)

        assert 'd="M0 0L1 0Q1 1 2 2C0 0 1 1 2 2Z"' in result

    def test_rounds_to_two_decimals_and_drops_trailing_zeros(self):
        curve = Outline([Layer([(MOVE, [(0.004, 1.5)]), (CURVE, [(0.0, 0.0), (1.234567, 2.5), (3.0, 3.999)])])], (0.0, 0.0, 4.0, 4.0))

        result = svg(curve)

        assert 'd="M0 1.5C0 0 1.23 2.5 3 4"' in result

    def test_writes_a_negative_zero_as_zero(self):
        dot = Outline([Layer([(MOVE, [(-0.001, 0.0)])])], UNIT)

        result = svg(dot)

        assert 'd="M0 0"' in result

    def test_writes_a_path_per_layer_in_drawing_order(self):
        screen_then_frame = Outline([Layer(dot(1)), Layer(dot(2))], (0.0, 0.0, 3.0, 3.0))

        result = svg(screen_then_frame)

        assert result.count("<path") == 2
        assert result.index('d="M1 1"') < result.index('d="M2 2"')

    def test_gives_a_secondary_and_a_tertiary_layer_their_opacity(self):
        tertiary_secondary_primary = Outline([Layer(dot(1), level=2), Layer(dot(2), level=1), Layer(dot(3))], (0.0, 0.0, 4.0, 4.0))

        result = svg(tertiary_secondary_primary)

        assert (
            '<path fill="currentColor" fill-opacity="0.3" d="M1 1"/><path fill="currentColor" fill-opacity="0.5" d="M2 2"/><path fill="currentColor" d="M3 3"/>'
        ) in result

    def test_multiplies_a_layers_own_opacity_into_its_levels(self):
        half_secondary = Outline([Layer(dot(1), level=1, opacity=0.5)], (0.0, 0.0, 2.0, 2.0))

        result = svg(half_secondary)

        assert 'fill-opacity="0.25"' in result

    class TestOnHierarchy:
        def test_uses_the_given_opacities(self):
            tertiary_then_secondary = Outline([Layer(dot(1), level=2), Layer(dot(2), level=1)], (0.0, 0.0, 3.0, 3.0))

            result = svg(tertiary_then_secondary, hierarchy=(1.0, 0.6, 0.25))

            assert 'fill-opacity="0.25" d="M1 1"' in result
            assert 'fill-opacity="0.6" d="M2 2"' in result


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
class TestCurrent:
    def test_follows_a_legacy_name_to_the_current_one(self):
        result = current("ipad.homebutton")

        assert result == "ipad.gen1"

    def test_keeps_a_current_name(self):
        result = current("ipad")

        assert result == "ipad"


@pytest.mark.macos
class TestOutline:
    def test_reads_the_layers_of_a_symbol(self):
        result = outline("macpro.gen3")

        assert result is not None
        assert result.layers[0].elements[0][0] == MOVE
        assert result.layers[0].elements[-1][0] == CLOSE
        assert result.bounds[3] > result.bounds[2] > 0

    def test_keeps_the_stand_of_the_desktop_computer_below_the_screen(self):
        result = svg(outline("desktopcomputer"))

        points = [(float(match["x"]), float(match["y"])) for match in COORDINATES.finditer(" ".join(PATH_DATA.findall(result)))]
        height = max(y for _, y in points)
        top = [x for x, y in points if y <= 0.02 * height]
        bottom = [x for x, y in points if y >= 0.98 * height]
        assert max(bottom) - min(bottom) < 0.5 * (max(top) - min(top))

    def test_draws_the_screen_of_the_ipad_as_a_tertiary_layer_under_its_frame(self):
        result = outline("ipad")

        assert [(layer.level, layer.opacity) for layer in result.layers] == [(2, 1.0), (0, 1.0)]

    def test_cuts_the_stems_of_the_airpods_pro_back_to_the_lower_half_and_keeps_no_eraser(self):
        result = outline("airpods.pro.gen1")

        stems = result.layers[0]
        assert [layer.level for layer in result.layers] == [0, 0, 1]
        assert min(y for _, points in stems.elements for _, y in points) > result.bounds[1] + 0.5 * result.bounds[3]

    def test_knocks_the_bell_out_of_the_filled_circle_with_a_grouped_eraser(self):
        result = outline("bell.slash.circle.fill")

        assert len(result.layers) == 1
        assert sum(1 for kind, _ in result.layers[0].elements if kind == MOVE) > 1
        assert all(math.isfinite(value) for value in result.bounds)

    def test_draws_the_arms_of_the_snowflake_that_erase_one_another(self):
        result = outline("snowflake")

        assert len(result.layers) == 3
        assert all(layer.elements for layer in result.layers)

    def test_drops_a_layer_an_eraser_cuts_away_entirely(self):
        result = outline("squareshape.controlhandles.on.squareshape.controlhandles")

        assert all(layer.elements for layer in result.layers)
        assert all(math.isfinite(value) for value in result.bounds)

    def test_draws_a_symbol_that_prefers_monochrome_as_primary_layers(self):
        result = outline("appletv")

        assert len(result.layers) > 1
        assert {layer.level for layer in result.layers} == {0}

    def test_reads_a_symbol_by_a_legacy_name(self):
        result = outline("ipad.homebutton")

        assert result is not None

    def test_is_none_for_a_name_the_catalog_lacks(self):
        result = outline("no.such.symbol")

        assert result is None


UNIT = (0.0, 0.0, 1.0, 1.0)
COORDINATES = re.compile(r"(?P<x>-?\d+(?:\.\d+)?) (?P<y>-?\d+(?:\.\d+)?)")
PATH_DATA = re.compile(r'd="(?P<data>[^"]*)"')


def dot(at: float) -> list[tuple[int, list[tuple[float, float]]]]:
    return [(MOVE, [(float(at), float(at))])]
