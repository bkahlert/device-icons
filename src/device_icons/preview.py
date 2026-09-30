"""The preview: a model identifier shown as a device in Finder's Network view, through dns-sd proxy registrations."""

from __future__ import annotations

import signal
import subprocess
import time

SMB_PORT = 445
# Port 0 marks a placeholder in mDNS, and Finder ignores the record; the proxied host never answers anyway.
DEVICE_INFO_PORT = 1
# TEST-NET-1 (RFC 5737): addresses that route nowhere, one per model identifier.
ADDRESSES = 254


def registrations(model_identifiers: list[str], name: str | None = None) -> list[list[str]]:
    """Return the dns-sd commands that proxy each model identifier as an SMB server carrying it in _device-info._tcp.

    Both records of a model identifier share a service instance name, the identifier itself or name, which Finder
    pairs them by; each identifier gets its own host name and TEST-NET-1 address.

    Raises ValueError if name is given for other than exactly one model identifier, or for more than 254 identifiers.
    """
    if name is not None and len(model_identifiers) != 1:
        raise ValueError("a name needs exactly one model identifier")
    if len(model_identifiers) > ADDRESSES:
        raise ValueError(f"at most {ADDRESSES} model identifiers at once")
    commands = []
    for number, model_identifier in enumerate(model_identifiers, start=1):
        instance = name or model_identifier
        host, address = f"device-icons-{number}.local", f"192.0.2.{number}"
        commands.append(["dns-sd", "-P", instance, "_smb._tcp", "local", str(SMB_PORT), host, address])
        commands.append(["dns-sd", "-P", instance, "_device-info._tcp", "local", str(DEVICE_INFO_PORT), host, address, f"model={model_identifier}"])
    return commands


def start(commands: list[list[str]]) -> list[subprocess.Popen]:
    """Start every command and return the processes."""
    return [subprocess.Popen(command) for command in commands]


def stop(processes: list[subprocess.Popen]) -> None:
    """Terminate the processes and wait for them to end."""
    for process in processes:
        process.terminate()
    for process in processes:
        process.wait()


def preview(model_identifiers: list[str], name: str | None = None) -> None:
    """Register the proxies for the model identifiers and keep them until Ctrl-C, SIGTERM, or one of them ending."""
    processes = start(registrations(model_identifiers, name))
    previous = signal.signal(signal.SIGTERM, _interrupt)
    try:
        while all(process.poll() is None for process in processes):
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        stop(processes)
        signal.signal(signal.SIGTERM, previous)


def _interrupt(signal_number: int, frame: object) -> None:
    raise KeyboardInterrupt
