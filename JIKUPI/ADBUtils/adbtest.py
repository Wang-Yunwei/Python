import os
import socket
import weakref
from typing import Union

_OKAY = "OKAY"
_FAIL = "FAIL"


class AdbConnection(object):
    def __init__(self, host: str, port: int):
        self.__host = host
        self.__port = port
        self.__conn = self._safe_connect()

        self._finalizer = weakref.finalize(self, self.conn.close)

    def _create_socket(self):
        adb_host = self.__host
        adb_port = self.__port
        s = socket.socket()
        try:
            s.connect((adb_host, adb_port))
            return s
        except:
            s.close()
            raise

    def _safe_connect(self):
        try:
            return self._create_socket()
        except ConnectionRefusedError:
            return self._create_socket()

    @property
    def closed(self) -> bool:
        return not self._finalizer.alive

    def close(self):
        self._finalizer()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()

    @property
    def conn(self) -> socket.socket:
        return self.__conn

    def send(self, data: bytes) -> int:
        return self.conn.send(data)

    def read(self, n: int) -> bytes:
        try:
            return self._read_fully(n)
        except socket.timeout:
            raise Exception("adb read timeout")

    def _read_fully(self, n: int) -> bytes:
        t = n
        buffer = b''
        while t > 0:
            chunk = self.conn.recv(t)
            if not chunk:
                break
            buffer += chunk
            t = n - len(buffer)
        return buffer

    def send_command(self, cmd: str):
        self.conn.send("{:04x}{}".format(len(cmd), cmd).encode("utf-8"))

    def read_string(self, n: int) -> str:
        data = self.read(n).decode()
        return data

    def read_string_block(self) -> str:
        """
        Raises:
            AdbError
        """
        length = self.read_string(4)
        if not length:
            raise Exception("connection closed")
        size = int(length, 16)
        return self.read_string(size)

    def read_until_close(self) -> str:
        content = b""
        while True:
            chunk = self.read(4096)
            if not chunk:
                break
            content += chunk
        return content.decode('utf-8', errors='ignore')

    def check_okay(self):
        data = self.read_string(4)
        if data == _FAIL:
            raise Exception(self.read_string_block())
        elif data == _OKAY:
            return
        raise Exception("Unknown data: %r" % data)


class AndroidClient(object):
    def __init__(self, host: str = "127.0.0.1", port: int = 5037, socket_timeout: float = None):
        """
        Args:
            host (str): default value from env:ANDROID_ADB_SERVER_HOST
            port (int): default value from env:ANDROID_ADB_SERVER_PORT
        """
        if not host:
            host = os.environ.get("ANDROID_ADB_SERVER_HOST", "127.0.0.1")
        if not port:
            port = int(os.environ.get("ANDROID_ADB_SERVER_PORT", 5037))
        self.__host = host
        self.__port = port
        self._serial = None
        self._transport_id = None
        self.__socket_timeout = socket_timeout

    @property
    def host(self) -> str:
        return self.__host

    @property
    def port(self) -> int:
        return self.__port

    def _connect(self, timeout: float = None) -> AdbConnection:
        """ connect to adb server

        Raises:
            AdbTimeout
        """
        timeout = timeout or self.__socket_timeout
        try:
            _conn = AdbConnection(self.__host, self.__port)
            if timeout:
                _conn.conn.settimeout(timeout)
            return _conn
        except TimeoutError:
            raise Exception("connect to adb server timeout")

    def server_version(self):
        """ 40 will match 1.0.40
        Returns:
            int
        """
        with self._connect() as c:
            c.send_command("host:version")
            c.check_okay()
            return int(c.read_string_block(), 16)

    def wait_for(self, serial: str = None, transport: str = 'any', state: str = "device", timeout: float = 60):
        """ Same as wait-for-TRANSPORT-STATE
        Args:
            serial (str): device serial [default None]
            transport (str): {any,usb,local} [default any]
            state (str): {device,recovery,rescue,sideload,bootloader,disconnect} [default device]
            timeout (float): max wait time [default 60]

        Raises:
            AdbError, AdbTimeout
        """
        with self._connect(timeout=timeout) as c:
            cmds = []
            if serial:
                cmds.extend(['host-serial', serial])
            else:
                cmds.append('host')
            cmds.append("wait-for-" + transport + "-" + state)
            c.send_command(":".join(cmds))
            c.check_okay()
            c.check_okay()

    def connect(self, addr: str, timeout: float = None) -> str:
        """ adb connect $addr
        Args:
            addr (str): adb remote address [eg: 191.168.0.1:5555]
            timeout (float): connect timeout
        Returns:
            content adb server returns

        Raises:
            AdbTimeout
        Example returns:
            - "already connected to 192.168.190.101:5555"
            - "unable to connect to 192.168.190.101:5551"
            - "failed to connect to '1.2.3.4:4567': Operation timed out"
        """
        with self._connect(timeout=timeout) as c:
            self._serial = addr
            c.send_command("host:connect:" + addr)
            c.check_okay()
            return c.read_string_block()

    def disconnect(self, addr: str, raise_error: bool = False) -> str:
        """ adb disconnect $addr
        Returns:
            content adb server returns
        Raises:
            when raise_error set to True
                AdbError("error: no such device '1.2.3.4:5678')
        Example returns:
            - "disconnected 192.168.190.101:5555"
        """
        try:
            with self._connect() as c:
                c.send_command("host:disconnect:" + addr)
                c.check_okay()
                return c.read_string_block()
        except Exception:
            if raise_error:
                raise Exception("[-] disconnect error...")

    def forward(self, serial, local, remote, norebind=False):
        """
        Args:
            serial (str): device serial
            local, remote (str): tcp:<port> or localabstract:<name>
            norebind (bool): fail if already forwarded when set to true
        Raises:
            AdbError
        """
        with self._connect() as c:
            cmds = ["host-serial", serial, "forward"]
            if norebind:
                cmds.append("norebind")
            cmds.append(local + ";" + remote)
            c.send_command(":".join(cmds))
            c.check_okay()

    def open_transport(self, command: str = None, timeout: float = None) -> AdbConnection:
        # connect has it own timeout
        c = self._connect()
        if timeout:
            c.conn.settimeout(timeout)

        if command:
            if self._transport_id:
                c.send_command(f"host-transport-id:{self._transport_id}:{command}")
            elif self._serial:
                c.send_command(f"host-serial:{self._serial}:{command}")
            else:
                raise RuntimeError
            c.check_okay()
        else:
            if self._transport_id:
                c.send_command(f"host:transport-id:{self._transport_id}")
            elif self._serial:
                # host:tport:serial:xxx is also fine, but receive 12 bytes
                # recv: 4f 4b 41 59 14 00 00 00 00 00 00 00              OKAY........
                # so here use host:transport
                c.send_command(f"host:transport:{self._serial}")
            else:
                raise RuntimeError
            c.check_okay()
        return c

    def shell(self,
              cmdargs: Union[str, list, tuple],
              stream: bool = False,
              timeout: float = None,
              rstrip=True) -> Union[AdbConnection, str]:
        """Run shell inside device and get it's content
        Args:
            rstrip (bool): strip the last empty line (Default: True)
            stream (bool): return stream instead of string output (Default: False)
            timeout (float): set shell timeout
        Returns:
            string of output when stream is False
            AdbConnection when stream is True
        Raises:
            AdbTimeout
        Examples:
            shell("ls -l")
            shell(["ls", "-l"])
            shell("ls | grep data")
        """
        if isinstance(cmdargs, (list, tuple)):
            raise Exception("not suport")
        if stream:
            timeout = None
        c = self.open_transport(timeout=timeout)
        c.send_command("shell:" + cmdargs)
        c.check_okay()
        if stream:
            return c
        output = c.read_until_close()
        return output.rstrip() if rstrip else output


if __name__ == "__main__":
    c = AndroidClient()
    # out1=c.shell("adb shell devices")
    # print(out1)
    #out1 = c.connect("10.3.13.170", 5555)
    #out = c.shell("su -c ls /data/local/tmp/")
    out=c.shell("adb shell am start com.zyhk.uav.android/.Controller.FlyDetailActivity")
    print(out)
