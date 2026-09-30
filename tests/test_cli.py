import pytest

from device_icons.cli import main


class TestMain:
    def test_help_exits_zero(self):
        with pytest.raises(SystemExit) as exit:
            main(["--help"])
        assert exit.value.code == 0
