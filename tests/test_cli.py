import json
import re
from pathlib import Path

import pytest

from device_icons.cli import main, parser


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

        class TestNoOpen:
            def test_turns_opening_off(self):
                result = parser().parse_args(["dump", "--no-open"])

                assert result.open is False

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

            assert exit.value.code == 2
            assert "exactly one model identifier" in capsys.readouterr().err

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

