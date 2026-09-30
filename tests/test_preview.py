import os
import signal
import stat
import subprocess
import sys
import time

import pytest

from device_icons.preview import registrations, start, stop


class TestRegistrations:
    def test_proxies_a_model_identifier_as_an_smb_server_with_a_device_info_record(self):
        result = registrations(["MacPro7,1"])

        assert result == [
            ["dns-sd", "-P", "MacPro7,1", "_smb._tcp", "local", "445", "device-icons-1.local", "192.0.2.1"],
            ["dns-sd", "-P", "MacPro7,1", "_device-info._tcp", "local", "1", "device-icons-1.local", "192.0.2.1", "model=MacPro7,1"],
        ]

    def test_gives_each_model_identifier_its_own_host(self):
        result = registrations(["MacPro7,1", "Xserve3,1"])

        assert [command[2] for command in result] == ["MacPro7,1", "MacPro7,1", "Xserve3,1", "Xserve3,1"]
        assert [command[6:8] for command in result[2:]] == [["device-icons-2.local", "192.0.2.2"]] * 2

    def test_refuses_more_model_identifiers_than_test_net_1_has_addresses(self):
        with pytest.raises(ValueError, match="254"):
            registrations([f"Mac{n},1" for n in range(255)])

    class TestOnName:
        def test_names_the_service_instance_after_it(self):
            result = registrations(["MacPro7,1@ECOLOR=226,226,224"], name="Rack")

            assert [command[2] for command in result] == ["Rack", "Rack"]
            assert result[1][-1] == "model=MacPro7,1@ECOLOR=226,226,224"

        def test_refuses_several_model_identifiers(self):
            with pytest.raises(ValueError, match="exactly one"):
                registrations(["MacPro7,1", "Xserve3,1"], name="Rack")


class TestStartAndStop:
    def test_start_runs_every_command_and_stop_ends_them(self, tmp_path, monkeypatch):
        log = fake_dns_sd(tmp_path, monkeypatch)
        commands = registrations(["MacPro7,1"])

        processes = start(commands)
        logged(log, lines=len(commands))
        running = [process.poll() for process in processes]
        stop(processes)

        assert running == [None, None]
        assert all(process.returncode is not None for process in processes)
        assert sorted(line.split(" ", 1)[1] for line in log.read_text().splitlines()) == sorted(" ".join(command[1:]) for command in commands)


class TestPreview:
    @pytest.mark.parametrize("signal_number", [signal.SIGINT, signal.SIGTERM], ids=["SIGINT", "SIGTERM"])
    def test_unregisters_when_signalled(self, tmp_path, monkeypatch, signal_number):
        log = fake_dns_sd(tmp_path, monkeypatch)
        process = subprocess.Popen([sys.executable, "-c", "from device_icons.preview import preview; preview(['MacPro7,1'])"])
        logged(log, lines=2)
        registrations_pids = [int(line.split()[0]) for line in log.read_text().splitlines()]

        process.send_signal(signal_number)
        result = process.wait(timeout=5)

        assert result == 0
        assert all(not alive(pid) for pid in registrations_pids)

    def test_returns_once_a_registration_ends(self, tmp_path, monkeypatch):
        script = fake_dns_sd(tmp_path, monkeypatch).parent / "bin" / "dns-sd"
        script.write_text("#!/bin/sh\nexit 1\n")
        process = subprocess.Popen([sys.executable, "-c", "from device_icons.preview import preview; preview(['MacPro7,1'])"])

        result = process.wait(timeout=5)

        assert result == 0


def fake_dns_sd(tmp_path, monkeypatch):
    log = tmp_path / "dns-sd.log"
    script = tmp_path / "bin" / "dns-sd"
    script.parent.mkdir()
    script.write_text(f'#!/bin/sh\nprintf "%s %s\\n" "$$" "$*" >> "{log}"\nexec sleep 30\n')
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{script.parent}{os.pathsep}{os.environ['PATH']}")
    return log


def logged(log, lines: int) -> None:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if log.exists() and len(log.read_text().splitlines()) >= lines:
            return
        time.sleep(0.01)
    raise TimeoutError(f"{lines} lines not logged within 5 s")


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True
