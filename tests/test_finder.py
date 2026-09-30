from pathlib import Path

import pytest

from device_icons.coretypes import BUNDLE
from device_icons.finder import set_folder_icons, show
from device_icons.icns import iconset


class TestSetFolderIcons:
    @pytest.mark.macos
    def test_gives_each_folder_the_image_as_its_icon(self, tmp_path):
        sidebar = iconset(BUNDLE / "Contents" / "Resources" / "SidebarMacPro.icns", tmp_path) / "icon_32x32@2x.png"
        folders = [tmp_path / "one", tmp_path / "two"]
        for folder in folders:
            folder.mkdir()

        result = set_folder_icons({folder: sidebar for folder in folders})

        assert result == []
        assert all((folder / "Icon\r").exists() for folder in folders)

    @pytest.mark.macos
    def test_reports_a_folder_it_could_not_decorate(self, tmp_path):
        sidebar = iconset(BUNDLE / "Contents" / "Resources" / "SidebarMacPro.icns", tmp_path) / "icon_32x32@2x.png"
        missing = tmp_path / "missing"

        result = set_folder_icons({missing: sidebar})

        assert result == [missing]

    class TestOnNoFolders:
        def test_does_nothing(self):
            result = set_folder_icons({})

            assert result == []


class TestShow:
    def test_opens_the_path_with_open(self, fake_command):
        opening = fake_command("open")

        show(Path("out/device-icons"))

        assert [arguments for _, arguments in opening.calls()] == ["out/device-icons"]
