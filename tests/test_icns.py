from pathlib import Path

import pytest

from device_icons.coretypes import BUNDLE
from device_icons.icns import iconset, largest, pixels, sidebar_icon


class TestPixels:
    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("icon_16x16.png", 16),
            ("icon_32x32@2x.png", 64),
            ("icon_512x512@2x.png", 1024),
            ("template_32x32@2x.png", 0),
            ("icon_[selected]16x16.png", 0),
            ("icon_16x32.png", 0),
        ],
    )
    def test_is_the_pixel_width_of_an_icon_image_and_zero_otherwise(self, name, expected):
        result = pixels(name)

        assert result == expected


class TestLargest:
    def test_picks_the_image_with_the_most_pixels(self, tmp_path):
        folder = images(tmp_path / "x.iconset", "icon_16x16.png", "icon_512x512@2x.png", "icon_256x256@2x.png", "template_32x32@2x.png")

        result = largest(folder)

        assert result == folder / "icon_512x512@2x.png"

    def test_is_none_without_icon_images(self, tmp_path):
        folder = images(tmp_path / "x.iconset", "template_32x32@2x.png")

        result = largest(folder)

        assert result is None


class TestSidebarIcon:
    def test_prefers_the_template_image_of_the_types_own_iconset(self, tmp_path):
        own = images(tmp_path / "own.iconset", "template_32x32@2x.png")
        sidebar_file = images(tmp_path / "SidebarMacPro.iconset", "icon_32x32@2x.png")

        result = sidebar_icon(own, sidebar_file)

        assert result == own / "template_32x32@2x.png"

    def test_falls_back_to_the_image_of_the_sidebar_icon_file(self, tmp_path):
        own = images(tmp_path / "own.iconset", "icon_512x512@2x.png")
        sidebar_file = images(tmp_path / "SidebarMacPro.iconset", "icon_32x32@2x.png")

        result = sidebar_icon(own, sidebar_file)

        assert result == sidebar_file / "icon_32x32@2x.png"

    def test_is_none_when_neither_has_a_64_px_image(self, tmp_path):
        own = images(tmp_path / "own.iconset", "icon_512x512@2x.png")
        sidebar_file = images(tmp_path / "SidebarMacPro.iconset", "icon_16x16.png")

        result = sidebar_icon(own, sidebar_file)

        assert result is None

    def test_accepts_a_missing_iconset_on_either_side(self, tmp_path):
        sidebar_file = images(tmp_path / "SidebarMacPro.iconset", "icon_32x32@2x.png")

        result = (sidebar_icon(None, sidebar_file), sidebar_icon(None, None))

        assert result == (sidebar_file / "icon_32x32@2x.png", None)


@pytest.mark.macos
class TestIconset:
    def test_unpacks_the_icon_file_into_work(self, tmp_path):
        result = iconset(BUNDLE / "Contents" / "Resources" / "SidebarMacPro.icns", tmp_path)

        assert result == tmp_path / "SidebarMacPro.iconset"
        assert (result / "icon_32x32@2x.png").is_file()

    def test_keeps_an_iconset_already_unpacked(self, tmp_path):
        first = iconset(BUNDLE / "Contents" / "Resources" / "SidebarMacPro.icns", tmp_path)
        marker = first / "marker"
        marker.write_text("")

        result = iconset(BUNDLE / "Contents" / "Resources" / "SidebarMacPro.icns", tmp_path)

        assert result == first
        assert marker.is_file()


def images(folder: Path, *names: str) -> Path:
    folder.mkdir()
    for name in names:
        (folder / name).write_bytes(b"")
    return folder
