"""Transport utilities for ZMQ communication."""
from __future__ import annotations

import platform
from pathlib import Path
from typing import Optional

from zmqruntime.config import TransportMode, ZMQConfig

_default_config = ZMQConfig()


def get_default_transport_mode() -> TransportMode:
    """Get platform-appropriate transport mode."""
    return TransportMode.TCP if platform.system() == "Windows" else TransportMode.IPC


def get_ipc_socket_path(port: int, config: ZMQConfig | None = None) -> Optional[Path]:
    """Get IPC socket path for a given port (Unix/Mac only)."""
    config = config or _default_config
    if platform.system() == "Windows":
        return None
    ipc_dir = Path.home() / f".{config.app_name}" / config.ipc_socket_dir
    socket_name = f"{config.ipc_socket_prefix}-{port}{config.ipc_socket_extension}"
    return ipc_dir / socket_name


def get_zmq_transport_url(
    port: int,
    host: str = "localhost",
    mode: TransportMode | None = None,
    config: ZMQConfig | None = None,
) -> str:
    """Get ZMQ transport URL for given port/host/mode."""
    config = config or _default_config
    mode = mode or get_default_transport_mode()
    if mode == TransportMode.IPC:
        if platform.system() == "Windows":
            raise ValueError(
                "IPC transport mode is not supported on Windows. "
                "Use TransportMode.TCP instead, or use get_default_transport_mode()."
            )
        socket_path = get_ipc_socket_path(port, config)
        if socket_path is None:
            raise ValueError("IPC socket path could not be determined.")
        socket_path.parent.mkdir(parents=True, exist_ok=True)
        return f"ipc://{socket_path}"
    if mode == TransportMode.TCP:
        return f"tcp://{host}:{port}"
    raise ValueError(f"Invalid transport mode: {mode}")


def remove_ipc_socket(port: int, config: ZMQConfig | None = None) -> bool:
    """Remove stale IPC socket file."""
    socket_path = get_ipc_socket_path(port, config)
    if socket_path and socket_path.exists():
        socket_path.unlink()
        return True
    return False
