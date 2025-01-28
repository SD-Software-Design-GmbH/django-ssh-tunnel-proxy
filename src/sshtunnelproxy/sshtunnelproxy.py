import random
from contextlib import contextmanager

import pexpect
from django.conf import settings


@contextmanager
def tunnel(remote_port: int = 0, local_port: int = 8000):
    """
    Create an SSH tunnel to a remote server
    """
    remote_port = remote_port or random.randint(*settings.SSH_TUNNEL_PORT_RANGE)  # noqa: S311
    ssh_tunnel = pexpect.spawn(
        f"ssh -NtR {remote_port}:localhost:{local_port} {settings.SSH_TUNNEL_USER}@{settings.SSH_TUNNEL_HOST}",
    )
    ssh_tunnel.expect("password:")
    ssh_tunnel.sendline(settings.SSH_TUNNEL_PASSWORD)

    # We need to expect something to keep the tunnel open
    # But expect("") doesn't work for some reason
    ssh_tunnel.expect(pexpect.TIMEOUT, timeout=1)

    try:
        yield settings.SSH_TUNNEL_URL_GENERATOR(remote_port)
    finally:
        ssh_tunnel.close()
