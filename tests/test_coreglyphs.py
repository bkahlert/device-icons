import pytest

from device_icons.coreglyphs import CLOSE, CURVE, LINE, MOVE, QUAD, Outline, outline, svg


class TestSvg:
    def test_writes_one_path_filled_with_current_color_in_a_tight_view_box(self):
        triangle = Outline([(MOVE, [(10.0, 20.0)]), (LINE, [(30.0, 20.0)]), (LINE, [(30.0, 60.0)]), (CLOSE, [])], (10.0, 20.0, 20.0, 40.0))

        result = svg(triangle)

        assert result == '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 40"><path fill="currentColor" d="M0 40L20 40L20 0Z"/></svg>\n'

    def test_maps_every_element_kind_to_its_command(self):
        every = Outline(
            [(MOVE, [(0.0, 0.0)]), (LINE, [(1.0, 0.0)]), (QUAD, [(1.0, 1.0), (2.0, 2.0)]), (CURVE, [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]), (CLOSE, [])],
            (0.0, 0.0, 2.0, 2.0),
        )

        result = svg(every)

        assert 'd="M0 2L1 2Q1 1 2 0C0 2 1 1 2 0Z"' in result

    def test_rounds_to_two_decimals_and_drops_trailing_zeros(self):
        curve = Outline([(MOVE, [(0.004, 1.5)]), (CURVE, [(0.0, 0.0), (1.234567, 2.5), (3.0, 3.999)])], (0.0, 0.0, 4.0, 4.0))

        result = svg(curve)

        assert 'd="M0 2.5C0 4 1.23 1.5 3 0"' in result

    def test_writes_a_negative_zero_as_zero(self):
        dot = Outline([(MOVE, [(0.0, 1.001)])], (0.0, 0.0, 1.0, 1.0))

        result = svg(dot)

        assert 'd="M0 0"' in result


@pytest.mark.macos
class TestOutline:
    def test_reads_the_outline_of_a_symbol(self):
        result = outline("macpro.gen3")

        assert result is not None
        assert result.elements[0][0] == MOVE
        assert result.elements[-1][0] == CLOSE
        assert result.bounds[3] > result.bounds[2] > 0

    def test_is_none_for_a_name_the_catalog_lacks(self):
        result = outline("no.such.symbol")

        assert result is None
