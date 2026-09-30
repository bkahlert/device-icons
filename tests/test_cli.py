import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from device_icons.cli import main, parser
from device_icons.finder import NETWORK_VIEW


class TestParser:
    class TestDump:
        def test_defaults_to_every_type_into_out(self):
            result = parser().parse_args(["dump"])

            assert (result.command, result.out, result.type_identifiers) == ("dump", Path("out"), None)

        def test_collects_repeated_types_and_the_output_directory(self):
            result = parser().parse_args(["dump", "--type", "com.apple.macpro-2019", "--type", "com.apple.xserve-xeon", "docs/icons"])

            assert result.type_identifiers == ["com.apple.macpro-2019", "com.apple.xserve-xeon"]
            assert result.out == Path("docs/icons")

        def test_opens_the_output_directory_by_default(self):
            result = parser().parse_args(["dump"])

            assert result.open is True

        def test_lays_the_table_out_vertically_by_default(self):
            result = parser().parse_args(["dump"])

            assert result.horizontal is False

        class TestNoOpen:
            def test_turns_opening_off(self):
                result = parser().parse_args(["dump", "--no-open"])

                assert result.open is False

        class TestHorizontal:
            def test_turns_the_table(self):
                result = parser().parse_args(["dump", "--horizontal"])

                assert result.horizontal is True

    class TestPreview:
        def test_collects_the_model_identifiers_and_the_name(self):
            result = parser().parse_args(["preview", "--name", "Rack", "MacPro7,1@ECOLOR=226,226,224"])

            assert (result.command, result.model_identifiers, result.name) == ("preview", ["MacPro7,1@ECOLOR=226,226,224"], "Rack")

        def test_defaults_the_name_to_none(self):
            result = parser().parse_args(["preview", "MacPro7,1", "Xserve3,1"])

            assert (result.model_identifiers, result.name) == (["MacPro7,1", "Xserve3,1"], None)

        def test_requires_a_model_identifier(self):
            with pytest.raises(SystemExit) as exit:
                parser().parse_args(["preview"])

            assert exit.value.code == 2

        def test_opens_the_network_view_by_default(self):
            result = parser().parse_args(["preview", "MacPro7,1"])

            assert result.open is True

        class TestNoOpen:
            def test_turns_opening_off(self):
                result = parser().parse_args(["preview", "--no-open", "MacPro7,1"])

                assert result.open is False


class TestMain:
    def test_help_exits_zero(self):
        with pytest.raises(SystemExit) as exit:
            main(["--help"])

        assert exit.value.code == 0

    def test_refuses_to_run_off_macos(self, monkeypatch):
        monkeypatch.setattr("sys.platform", "linux")

        with pytest.raises(SystemExit, match="macOS only"):
            main(["dump"])

    class TestPreview:
        def test_rejects_a_name_for_several_model_identifiers_as_usage_error(self, capsys, monkeypatch):
            monkeypatch.setattr("sys.platform", "darwin")

            with pytest.raises(SystemExit) as exit:
                main(["preview", "--name", "Rack", "MacPro7,1", "Xserve3,1"])

            error = capsys.readouterr().err
            assert exit.value.code == 2
            assert "usage: device-icons preview" in error
            assert "exactly one model identifier" in error

        def test_opens_the_network_view_in_finder(self, fake_command):
            fake_command("dns-sd", then="exit 1")
            opening = fake_command("open")

            result = preview_as_on_macos("MacPro7,1")

            assert result == 0
            assert [arguments for _, arguments in opening.calls()] == [str(NETWORK_VIEW)]

        class TestNoOpen:
            def test_leaves_finder_alone(self, fake_command):
                fake_command("dns-sd", then="exit 1")
                opening = fake_command("open")

                result = preview_as_on_macos("--no-open", "MacPro7,1")

                assert result == 0
                assert not opening.log.exists()

    @pytest.mark.macos
    class TestDump:
        def test_writes_the_dump_and_prints_the_summary(self, tmp_path, capsys, fake_command):
            fake_command("open")
            out = tmp_path / "out"

            result = main(["dump", "--type", "com.apple.xserve-xeon", str(out)])

            assert result == 0
            assert re.match(r"\d+ model identifiers: \d+ placed under 1 sidebar icons and 1 icons in ", capsys.readouterr().out)
            assert "SidebarXserve" in json.loads((out / "index.json").read_text())["sidebars"]

        def test_opens_the_output_directory_in_finder(self, tmp_path, fake_command):
            opening = fake_command("open")
            out = tmp_path / "out"

            main(["dump", "--type", "com.apple.xserve-xeon", str(out)])

            assert [arguments for _, arguments in opening.calls()] == [str(out)]

        class TestNoOpen:
            def test_leaves_finder_alone(self, tmp_path, fake_command):
                opening = fake_command("open")

                main(["dump", "--no-open", "--type", "com.apple.xserve-xeon", str(tmp_path / "out")])

                assert not opening.log.exists()

        class TestHorizontal:
            def test_lays_the_table_out_by_column(self, tmp_path, fake_command):
                fake_command("open")
                out = tmp_path / "out"

                main(["dump", "--horizontal", "--type", "com.apple.xserve-xeon", str(out)])

                assert "| Type identifier | `com.apple.xserve-xeon` |" in (out / "README.md").read_text()



def preview_as_on_macos(*arguments: str) -> int:
    script = f"import sys; sys.platform = 'darwin'; from device_icons.cli import main; sys.exit(main(['preview', *{list(arguments)!r}]))"
    return subprocess.run([sys.executable, "-c", script], timeout=5).returncode
