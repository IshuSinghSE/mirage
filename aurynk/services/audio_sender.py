import socket
import ssl
import subprocess
from typing import Optional


class AudioSender:
    """
    Manages desktop audio streaming over TCP or TLS.
    """

    def __init__(self, device: Optional[str] = None):
        self.device = device or "default"
        self.buffer_size = 1024
        self.proc = None
        self.sock = None

    def _get_ffmpeg_cmd(self):
        return [
            "ffmpeg",
            "-f",
            "pulse",
            "-i",
            self.device,
            "-f",
            "s16le",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "44100",
            "-ac",
            "2",
            "-loglevel",
            "error",
            "-",
        ]

    def stream_tcp(self, host: str, port: int):
        """
        Stream audio over plain TCP.
        """
        self._stream(host, port, use_tls=False)

    def stream_tls(
        self,
        host: str,
        port: int,
        certfile: Optional[str] = None,
        keyfile: Optional[str] = None,
        cafile: Optional[str] = None,
    ):
        """
        Stream audio over TLS.
        """
        self._stream(
            host,
            port,
            use_tls=True,
            certfile=certfile,
            keyfile=keyfile,
            cafile=cafile,
        )

    def _stream(
        self,
        host: str,
        port: int,
        use_tls: bool = False,
        certfile: Optional[str] = None,
        keyfile: Optional[str] = None,
        cafile: Optional[str] = None,
    ):
        ffmpeg_cmd = self._get_ffmpeg_cmd()
        self.sock = None
        self.proc = None
        try:
            if use_tls:
                context = ssl.create_default_context(
                    ssl.Purpose.SERVER_AUTH if cafile else ssl.Purpose.CLIENT_AUTH
                )
                if certfile and keyfile:
                    context.load_cert_chain(certfile=certfile, keyfile=keyfile)
                if cafile:
                    context.load_verify_locations(cafile=cafile)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE if not cafile else ssl.CERT_REQUIRED
                raw_sock = socket.create_connection((host, int(port)))
                self.sock = context.wrap_socket(raw_sock, server_hostname=host)
                print(f"Streaming desktop audio to {host}:{port} over TLS in real-time ...")
            else:
                self.sock = socket.create_connection((host, int(port)))
                print(f"Streaming desktop audio to {host}:{port} in real-time ...")

            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, bufsize=0)
            silence = b"\x00" * self.buffer_size

            while True:
                data = self.proc.stdout.read(self.buffer_size)
                if not data:
                    self.sock.sendall(silence)
                    continue
                self.sock.sendall(data)

        except KeyboardInterrupt:
            print("\nStopped by user. Sending silence for smooth stop...")
            silence = b"\x00" * int(44100 * 2 * 2 * 0.1)
            try:
                if self.sock:
                    self.sock.sendall(silence)
            except Exception:
                pass
        except Exception as e:
            print(f"\nError: {e}")
        finally:
            if self.proc:
                try:
                    self.proc.terminate()
                    self.proc.wait(timeout=2)
                except Exception:
                    pass
            if self.sock:
                try:
                    self.sock.shutdown(socket.SHUT_RDWR)
                    self.sock.close()
                except Exception:
                    pass
            print("Done streaming.")
