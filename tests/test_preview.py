import os
import signal
import subprocess
import sys

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
    def test_start_runs_every_command_and_stop_ends_them(self, fake_command):
        dns_sd = fake_command("dns-sd", then="exec sleep 30")
        commands = registrations(["MacPro7,1"])

        processes = start(commands)
        calls = dns_sd.calls(at_least=len(commands))
        running = [process.poll() for process in processes]
        stop(processes)

        assert running == [None, None]
        assert all(process.returncode is not None for process in processes)
        assert sorted(arguments for _, arguments in calls) == sorted(" ".join(command[1:]) for command in commands)


class TestPreview:
    @pytest.mark.parametrize("signal_number", [signal.SIGINT, signal.SIGTERM], ids=["SIGINT", "SIGTERM"])
    def test_unregisters_when_signalled(self, fake_command, signal_number):
        dns_sd = fake_command("dns-sd", then="exec sleep 30")
        process = subprocess.Popen([sys.executable, "-c", "from device_icons.preview import preview; preview(['MacPro7,1'])"])
        registration_pids = [pid for pid, _ in dns_sd.calls(at_least=2)]

        process.send_signal(signal_number)
        result = process.wait(timeout=5)

        assert result == 0
        assert all(not alive(pid) for pid in registration_pids)

    def test_returns_once_a_registration_ends(self, fake_command):
        fake_command("dns-sd", then="exit 1")
        process = subprocess.Popen([sys.executable, "-c", "from device_icons.preview import preview; preview(['MacPro7,1'])"])

        result = process.wait(timeout=5)

        assert result == 0


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True
