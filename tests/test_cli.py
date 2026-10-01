import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from device_icons.cli import main, parser
from device_icons.finder import NETWORK_VIEW


class TestParser:
    class TestIcons:
        def test_requires_an_action(self):
            with pytest.raises(SystemExit) as exit:
                parser().parse_args(["icons"])

            assert exit.value.code == 2

        class TestExport:
            def test_defaults_to_every_type_into_out(self):
                result = parser().parse_args(["icons", "export"])

                assert (result.command, result.action, result.out, result.type_identifiers, result.model_identifiers) == (
                    "icons",
                    "export",
                    Path("out"),
                    None,
                    None,
                )

            def test_collects_repeated_types_and_the_output_directory(self):
                result = parser().parse_args(["icons", "export", "--type", "com.apple.macpro-2019", "--type", "com.apple.xserve-xeon", "docs/icons"])

                assert result.type_identifiers == ["com.apple.macpro-2019", "com.apple.xserve-xeon"]
                assert result.out == Path("docs/icons")

            def test_collects_repeated_model_identifiers(self):
                result = parser().parse_args(["icons", "export", "--model", "MacPro7,1", "--model", "Xserve3,1"])

                assert result.model_identifiers == ["MacPro7,1", "Xserve3,1"]

            def test_refuses_type_and_model_together(self):
                with pytest.raises(SystemExit) as exit:
                    parser().parse_args(["icons", "export", "--type", "com.apple.macpro-2019", "--model", "Xserve3,1"])

                assert exit.value.code == 2

            def test_opens_the_output_directory_by_default(self):
                result = parser().parse_args(["icons", "export"])

                assert result.open is True

            def test_lays_the_table_out_vertically_by_default(self):
                result = parser().parse_args(["icons", "export"])

                assert result.horizontal is False

            class TestNoOpen:
                def test_turns_opening_off(self):
                    result = parser().parse_args(["icons", "export", "--no-open"])

                    assert result.open is False

            class TestHorizontal:
                def test_turns_the_table(self):
                    result = parser().parse_args(["icons", "export", "--horizontal"])

                    assert result.horizontal is True

        class TestPreview:
            def test_collects_the_model_identifiers_and_the_name(self):
                result = parser().parse_args(["icons", "preview", "--name", "Rack", "MacPro7,1@ECOLOR=226,226,224"])

                assert (result.command, result.action, result.model_identifiers, result.name) == (
                    "icons",
                    "preview",
                    ["MacPro7,1@ECOLOR=226,226,224"],
                    "Rack",
                )

            def test_defaults_the_name_to_none(self):
                result = parser().parse_args(["icons", "preview", "MacPro7,1", "Xserve3,1"])

                assert (result.model_identifiers, result.name) == (["MacPro7,1", "Xserve3,1"], None)

            def test_requires_a_model_identifier(self):
                with pytest.raises(SystemExit) as exit:
                    parser().parse_args(["icons", "preview"])

                assert exit.value.code == 2

            def test_opens_the_network_view_by_default(self):
                result = parser().parse_args(["icons", "preview", "MacPro7,1"])

                assert result.open is True

            class TestNoOpen:
                def test_turns_opening_off(self):
                    result = parser().parse_args(["icons", "preview", "--no-open", "MacPro7,1"])

                    assert result.open is False

    class TestSymbols:
        def test_requires_an_action(self):
            with pytest.raises(SystemExit) as exit:
                parser().parse_args(["symbols"])

            assert exit.value.code == 2

        class TestExport:
            def test_defaults_to_every_device_type_into_out(self):
                result = parser().parse_args(["symbols", "export"])

                assert (result.command, result.action, result.out, result.symbol_names, result.model_identifiers, result.open, result.horizontal) == (
                    "symbols",
                    "export",
                    Path("out"),
                    None,
                    None,
                    True,
                    False,
                )

            def test_collects_repeated_symbol_names_and_the_output_directory(self):
                result = parser().parse_args(["symbols", "export", "--symbol", "macpro.gen3", "--symbol", "xserve.raid", "docs/symbols"])

                assert result.symbol_names == ["macpro.gen3", "xserve.raid"]
                assert result.out == Path("docs/symbols")

            def test_collects_repeated_model_identifiers(self):
                result = parser().parse_args(["symbols", "export", "--model", "MacPro7,1", "--model", "Xserve3,1"])

                assert result.model_identifiers == ["MacPro7,1", "Xserve3,1"]

            def test_refuses_symbol_and_model_together(self):
                with pytest.raises(SystemExit) as exit:
                    parser().parse_args(["symbols", "export", "--symbol", "macpro.gen3", "--model", "MacPro7,1"])

                assert exit.value.code == 2

            def test_defaults_the_level_opacities_to_appkits(self):
                result = parser().parse_args(["symbols", "export"])

                assert (result.secondary, result.tertiary) == (0.5, 0.3)

            def test_takes_the_level_opacities(self):
                result = parser().parse_args(["symbols", "export", "--secondary", "0.6", "--tertiary", "0.25"])

                assert (result.secondary, result.tertiary) == (0.6, 0.25)

            class TestNoOpen:
                def test_turns_opening_off(self):
                    result = parser().parse_args(["symbols", "export", "--no-open"])

                    assert result.open is False

            class TestHorizontal:
                def test_turns_the_table(self):
                    result = parser().parse_args(["symbols", "export", "--horizontal"])

                    assert result.horizontal is True


class TestMain:
    def test_help_exits_zero(self):
        with pytest.raises(SystemExit) as exit:
            main(["--help"])

        assert exit.value.code == 0

    def test_refuses_to_run_off_macos(self, monkeypatch):
        monkeypatch.setattr("sys.platform", "linux")

        with pytest.raises(SystemExit, match="macOS only"):
            main(["icons", "export"])

    class TestIcons:
        class TestPreview:
            def test_rejects_a_name_for_several_model_identifiers_as_usage_error(self, capsys, monkeypatch):
                monkeypatch.setattr("sys.platform", "darwin")

                with pytest.raises(SystemExit) as exit:
                    main(["icons", "preview", "--name", "Rack", "MacPro7,1", "Xserve3,1"])

                error = capsys.readouterr().err
                assert exit.value.code == 2
                assert "usage: device-icons icons preview" in error
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
        class TestExport:
            def test_writes_the_icons_and_prints_the_summary(self, tmp_path, capsys, fake_command):
                fake_command("open")
                out = tmp_path / "out"

                result = main(["icons", "export", "--type", "com.apple.xserve-xeon", str(out)])

                assert result == 0
                assert re.match(r"\d+ model identifiers: \d+ placed under 1 sidebar icons and 1 icons in ", capsys.readouterr().out)
                assert "SidebarXserve" in json.loads((out / "index.json").read_text())["sidebars"]

            def test_opens_the_output_directory_in_finder(self, tmp_path, fake_command):
                opening = fake_command("open")
                out = tmp_path / "out"

                main(["icons", "export", "--type", "com.apple.xserve-xeon", str(out)])

                assert [arguments for _, arguments in opening.calls()] == [str(out)]

            class TestNoOpen:
                def test_leaves_finder_alone(self, tmp_path, fake_command):
                    opening = fake_command("open")

                    main(["icons", "export", "--no-open", "--type", "com.apple.xserve-xeon", str(tmp_path / "out")])

                    assert not opening.log.exists()

            class TestModel:
                def test_writes_only_that_model_identifier(self, tmp_path, fake_command):
                    fake_command("open")
                    out = tmp_path / "out"

                    main(["icons", "export", "--model", "Xserve3,1", str(out)])

                    readme = (out / "README.md").read_text()
                    assert "| `Xserve3,1` |" in readme
                    assert "RackMac" not in readme

            class TestHorizontal:
                def test_lays_the_table_out_by_column(self, tmp_path, fake_command):
                    fake_command("open")
                    out = tmp_path / "out"

                    main(["icons", "export", "--horizontal", "--type", "com.apple.xserve-xeon", str(out)])

                    assert "| Type identifier | `com.apple.xserve-xeon` |" in (out / "README.md").read_text()

    @pytest.mark.macos
    class TestSymbols:
        class TestExport:
            def test_writes_the_symbols_and_prints_the_summary(self, tmp_path, capsys, fake_command):
                fake_command("open")
                out = tmp_path / "out"

                result = main(["symbols", "export", "--symbol", "macpro.gen3", str(out)])

                assert result == 0
                assert re.match(r"\d+ model identifiers: \d+ placed under 1 symbols in ", capsys.readouterr().out)
                assert "macpro.gen3" in json.loads((out / "index.json").read_text())["symbols"]

            def test_opens_the_output_directory_in_finder(self, tmp_path, fake_command):
                opening = fake_command("open")
                out = tmp_path / "out"

                main(["symbols", "export", "--symbol", "macpro.gen3", str(out)])

                assert [arguments for _, arguments in opening.calls()] == [str(out)]

            class TestNoOpen:
                def test_leaves_finder_alone(self, tmp_path, fake_command):
                    opening = fake_command("open")

                    main(["symbols", "export", "--no-open", "--symbol", "macpro.gen3", str(tmp_path / "out")])

                    assert not opening.log.exists()

            class TestHorizontal:
                def test_lays_the_table_out_by_column(self, tmp_path, fake_command):
                    fake_command("open")
                    out = tmp_path / "out"

                    main(["symbols", "export", "--horizontal", "--symbol", "macpro.gen3", str(out)])

                    assert "| Symbol name | `macpro.gen3` |" in (out / "README.md").read_text()

            class TestModel:
                def test_writes_only_that_model_identifier(self, tmp_path, fake_command):
                    fake_command("open")
                    out = tmp_path / "out"

                    main(["symbols", "export", "--model", "MacPro7,1", str(out)])

                    readme = (out / "README.md").read_text()
                    assert "| `MacPro7,1` |" in readme
                    assert "Mac14,8" not in readme

            class TestTertiary:
                def test_sets_the_opacity_of_a_tertiary_layer(self, tmp_path, fake_command):
                    fake_command("open")
                    out = tmp_path / "out"

                    main(["symbols", "export", "--tertiary", "0.25", "--symbol", "ipad", str(out)])

                    assert 'fill-opacity="0.25"' in (out / "symbols" / "ipad.svg").read_text()


def preview_as_on_macos(*arguments: str) -> int:
    script = f"import sys; sys.platform = 'darwin'; from device_icons.cli import main; sys.exit(main(['icons', 'preview', *{list(arguments)!r}]))"
    return subprocess.run([sys.executable, "-c", script], timeout=5, check=False).returncode
