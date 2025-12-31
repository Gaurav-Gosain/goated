from __future__ import annotations

import socket as _socket
from dataclasses import dataclass

from goated.result import Err, GoError, Ok, Result

__all__ = [
    "Dial",
    "DialTCP",
    "DialUDP",
    "DialTimeout",
    "Listen",
    "ListenTCP",
    "ListenUDP",
    "LookupHost",
    "LookupIP",
    "LookupAddr",
    "LookupPort",
    "LookupCNAME",
    "LookupMX",
    "LookupTXT",
    "SplitHostPort",
    "JoinHostPort",
    "ParseIP",
    "ParseCIDR",
    "ResolveIPAddr",
    "ResolveTCPAddr",
    "ResolveUDPAddr",
    "Conn",
    "Listener",
    "TCPConn",
    "UDPConn",
    "TCPListener",
    "UDPConn",
    "IP",
    "IPAddr",
    "TCPAddr",
    "UDPAddr",
    "IPNet",
    "IPv4",
    "IPv6loopback",
    "IPv6zero",
]


@dataclass
class IP:
    """IP address."""

    _bytes: bytes

    def String(self) -> str:
        """String returns the string form of the IP address."""
        if len(self._bytes) == 4:
            return ".".join(str(b) for b in self._bytes)
        elif len(self._bytes) == 16:
            parts = []
            for i in range(0, 16, 2):
                parts.append(f"{self._bytes[i]:02x}{self._bytes[i + 1]:02x}")
            return ":".join(parts)
        return ""

    def To4(self) -> IP | None:
        """To4 converts the IP address to 4-byte representation."""
        if len(self._bytes) == 4:
            return self
        if len(self._bytes) == 16:
            if self._bytes[:12] == bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xFF, 0xFF]):
                return IP(self._bytes[12:])
        return None

    def To16(self) -> IP | None:
        """To16 converts the IP address to 16-byte representation."""
        if len(self._bytes) == 16:
            return self
        if len(self._bytes) == 4:
            return IP(bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xFF, 0xFF]) + self._bytes)
        return None

    def IsLoopback(self) -> bool:
        """IsLoopback reports whether ip is a loopback address."""
        ip4 = self.To4()
        if ip4:
            return ip4._bytes[0] == 127
        return self._bytes == bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])

    def IsPrivate(self) -> bool:
        """IsPrivate reports whether ip is a private address."""
        ip4 = self.To4()
        if ip4:
            b = ip4._bytes
            return b[0] == 10 or (b[0] == 172 and 16 <= b[1] <= 31) or (b[0] == 192 and b[1] == 168)
        return False

    def IsUnspecified(self) -> bool:
        """IsUnspecified reports whether ip is an unspecified address."""
        return self._bytes == bytes(4) or self._bytes == bytes(16)

    def Equal(self, other: IP) -> bool:
        """Equal reports whether ip and other are the same IP address."""
        return self._bytes == other._bytes


def IPv4(a: int, b: int, c: int, d: int) -> IP:
    """IPv4 returns the IP address a.b.c.d."""
    return IP(bytes([a, b, c, d]))


IPv6loopback = IP(bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]))
IPv6zero = IP(bytes(16))


@dataclass
class IPAddr:
    """IPAddr represents the address of an IP end point."""

    IP: IP
    Zone: str = ""

    def Network(self) -> str:
        return "ip"

    def String(self) -> str:
        if self.Zone:
            return f"{self.IP.String()}%{self.Zone}"
        return self.IP.String()


@dataclass
class TCPAddr:
    """TCPAddr represents the address of a TCP end point."""

    IP: IP
    Port: int
    Zone: str = ""

    def Network(self) -> str:
        return "tcp"

    def String(self) -> str:
        ip_str = self.IP.String()
        if ":" in ip_str:
            ip_str = f"[{ip_str}]"
        if self.Zone:
            ip_str = f"{ip_str}%{self.Zone}"
        return f"{ip_str}:{self.Port}"


@dataclass
class UDPAddr:
    """UDPAddr represents the address of a UDP end point."""

    IP: IP
    Port: int
    Zone: str = ""

    def Network(self) -> str:
        return "udp"

    def String(self) -> str:
        ip_str = self.IP.String()
        if ":" in ip_str:
            ip_str = f"[{ip_str}]"
        if self.Zone:
            ip_str = f"{ip_str}%{self.Zone}"
        return f"{ip_str}:{self.Port}"


_IP = IP


@dataclass
class IPNet:
    """IPNet represents an IP network."""

    IP: _IP
    Mask: bytes

    def String(self) -> str:
        prefix_len = sum(bin(b).count("1") for b in self.Mask)
        return f"{self.IP.String()}/{prefix_len}"

    def Contains(self, ip: _IP) -> bool:
        """Contains reports whether the network includes ip."""
        net_ip = self.IP
        if net_ip is None:
            return False
        if len(ip._bytes) != len(net_ip._bytes):
            return False
        for _i, (a, b, m) in enumerate(zip(ip._bytes, net_ip._bytes, self.Mask, strict=False)):
            if a & m != b & m:
                return False
        return True


class Conn:
    """Conn is a generic network connection."""

    def __init__(self, sock: _socket.socket):
        self._sock = sock

    def Read(self, b: bytearray) -> tuple[int, GoError | None]:
        """Read reads data into b."""
        try:
            data = self._sock.recv(len(b))
            n = len(data)
            b[:n] = data
            if n == 0:
                return 0, GoError("EOF", "io.EOF")
            return n, None
        except Exception as e:
            return 0, GoError(str(e), "net.Error")

    def Write(self, b: bytes) -> tuple[int, GoError | None]:
        """Write writes data from b."""
        try:
            n = self._sock.send(b)
            return n, None
        except Exception as e:
            return 0, GoError(str(e), "net.Error")

    def Close(self) -> Result[None, GoError]:
        """Close closes the connection."""
        try:
            self._sock.close()
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "net.Error"))

    def LocalAddr(self) -> str:
        """LocalAddr returns the local network address."""
        try:
            addr = self._sock.getsockname()
            return f"{addr[0]}:{addr[1]}"
        except Exception:
            return ""

    def RemoteAddr(self) -> str:
        """RemoteAddr returns the remote network address."""
        try:
            addr = self._sock.getpeername()
            return f"{addr[0]}:{addr[1]}"
        except Exception:
            return ""

    def SetDeadline(self, t: float) -> Result[None, GoError]:
        """SetDeadline sets the read and write deadlines."""
        try:
            self._sock.settimeout(t)
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "net.Error"))


class TCPConn(Conn):
    """TCPConn is an implementation of the Conn interface for TCP connections."""

    pass


class UDPConn:
    """UDPConn is the implementation of the Conn interface for UDP connections."""

    def __init__(self, sock: _socket.socket):
        self._sock = sock

    def ReadFrom(self, b: bytearray) -> tuple[int, str, GoError | None]:
        """ReadFrom reads a packet from the connection."""
        try:
            data, addr = self._sock.recvfrom(len(b))
            n = len(data)
            b[:n] = data
            return n, f"{addr[0]}:{addr[1]}", None
        except Exception as e:
            return 0, "", GoError(str(e), "net.Error")

    def WriteTo(self, b: bytes, addr: str) -> tuple[int, GoError | None]:
        """WriteTo writes a packet to addr."""
        try:
            host, port = SplitHostPort(addr)
            if host.is_err():
                return 0, host.err()
            n = self._sock.sendto(b, (host.unwrap(), int(port.unwrap())))
            return n, None
        except Exception as e:
            return 0, GoError(str(e), "net.Error")

    def Close(self) -> Result[None, GoError]:
        """Close closes the connection."""
        try:
            self._sock.close()
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "net.Error"))


class Listener:
    """Listener is a generic network listener."""

    def __init__(self, sock: _socket.socket):
        self._sock = sock

    def Accept(self) -> Result[Conn, GoError]:
        """Accept waits for and returns the next connection."""
        try:
            conn, addr = self._sock.accept()
            return Ok(Conn(conn))
        except Exception as e:
            return Err(GoError(str(e), "net.Error"))

    def Close(self) -> Result[None, GoError]:
        """Close closes the listener."""
        try:
            self._sock.close()
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "net.Error"))

    def Addr(self) -> str:
        """Addr returns the listener's network address."""
        try:
            addr = self._sock.getsockname()
            return f"{addr[0]}:{addr[1]}"
        except Exception:
            return ""


class TCPListener(Listener):
    """TCPListener is a TCP network listener."""

    def Accept(self) -> Result[Conn, GoError]:
        """Accept waits for and returns the next connection."""
        try:
            conn, addr = self._sock.accept()
            return Ok(TCPConn(conn))
        except Exception as e:
            return Err(GoError(str(e), "net.Error"))


def Dial(network: str, address: str) -> Result[Conn, GoError]:
    """Dial connects to the address on the named network."""
    try:
        host, port = _parse_address(address)

        if network in ("tcp", "tcp4", "tcp6"):
            family = (
                _socket.AF_INET
                if network == "tcp4"
                else _socket.AF_INET6
                if network == "tcp6"
                else _socket.AF_INET
            )
            sock = _socket.socket(family, _socket.SOCK_STREAM)
            sock.connect((host, port))
            return Ok(TCPConn(sock))
        elif network in ("udp", "udp4", "udp6"):
            family = (
                _socket.AF_INET
                if network == "udp4"
                else _socket.AF_INET6
                if network == "udp6"
                else _socket.AF_INET
            )
            sock = _socket.socket(family, _socket.SOCK_DGRAM)
            sock.connect((host, port))
            # Note: UDPConn doesn't inherit from Conn but we return it as a generic connection
            return Ok(UDPConn(sock))  # type: ignore[arg-type]
        else:
            return Err(GoError(f"unknown network {network}", "net.UnknownNetworkError"))
    except Exception as e:
        return Err(GoError(str(e), "net.Error"))


def DialTCP(network: str, laddr: TCPAddr | None, raddr: TCPAddr) -> Result[TCPConn, GoError]:
    """DialTCP connects to the remote address on the network."""
    result = Dial(network, raddr.String())
    if result.is_err():
        err = result.err()
        assert err is not None
        return Err(err)
    conn = result.unwrap()
    return Ok(TCPConn(conn._sock))


def DialUDP(network: str, laddr: UDPAddr | None, raddr: UDPAddr) -> Result[UDPConn, GoError]:
    """DialUDP connects to the remote address on the network."""
    result = Dial(network, raddr.String())
    if result.is_err():
        err = result.err()
        assert err is not None
        return Err(err)
    return Ok(UDPConn(result.unwrap()._sock))


def DialTimeout(network: str, address: str, timeout: float) -> Result[Conn, GoError]:
    """DialTimeout acts like Dial but takes a timeout."""
    try:
        host, port = _parse_address(address)
        sock = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        return Ok(TCPConn(sock))
    except TimeoutError:
        return Err(GoError("connection timed out", "net.Error"))
    except Exception as e:
        return Err(GoError(str(e), "net.Error"))


def Listen(network: str, address: str) -> Result[Listener, GoError]:
    """Listen announces on the local network address."""
    try:
        host, port = _parse_address(address)

        if network in ("tcp", "tcp4", "tcp6"):
            family = (
                _socket.AF_INET
                if network == "tcp4"
                else _socket.AF_INET6
                if network == "tcp6"
                else _socket.AF_INET
            )
            sock = _socket.socket(family, _socket.SOCK_STREAM)
            sock.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            sock.listen(128)
            return Ok(TCPListener(sock))
        else:
            return Err(GoError(f"unknown network {network}", "net.UnknownNetworkError"))
    except Exception as e:
        return Err(GoError(str(e), "net.Error"))


def ListenTCP(network: str, laddr: TCPAddr | None) -> Result[TCPListener, GoError]:
    """ListenTCP announces on the local network address."""
    addr = laddr.String() if laddr else ":0"
    result = Listen(network, addr)
    if result.is_err():
        err = result.err()
        assert err is not None
        return Err(err)
    return Ok(TCPListener(result.unwrap()._sock))


def ListenUDP(network: str, laddr: UDPAddr | None) -> Result[UDPConn, GoError]:
    """ListenUDP listens for incoming UDP packets."""
    try:
        host = laddr.IP.String() if laddr else ""
        port = laddr.Port if laddr else 0

        family = (
            _socket.AF_INET
            if network == "udp4"
            else _socket.AF_INET6
            if network == "udp6"
            else _socket.AF_INET
        )
        sock = _socket.socket(family, _socket.SOCK_DGRAM)
        sock.bind((host, port))
        return Ok(UDPConn(sock))
    except Exception as e:
        return Err(GoError(str(e), "net.Error"))


def LookupHost(host: str) -> Result[list[str], GoError]:
    """LookupHost looks up the given host."""
    try:
        _, _, addrs = _socket.gethostbyname_ex(host)
        return Ok(addrs)
    except Exception as e:
        return Err(GoError(str(e), "net.DNSError"))


def LookupIP(host: str) -> Result[list[IP], GoError]:
    """LookupIP looks up the IP addresses for the given host."""
    result = LookupHost(host)
    if result.is_err():
        err = result.err()
        assert err is not None
        return Err(err)
    ips: list[IP] = []
    for addr in result.unwrap():
        ip = ParseIP(addr)
        if ip is not None:
            ips.append(ip)
    return Ok(ips)


def LookupAddr(addr: str) -> Result[list[str], GoError]:
    """LookupAddr performs a reverse lookup for the given address."""
    try:
        names, _, _ = _socket.gethostbyaddr(addr)
        return Ok([names] if isinstance(names, str) else list(names))
    except Exception as e:
        return Err(GoError(str(e), "net.DNSError"))


def LookupPort(network: str, service: str) -> Result[int, GoError]:
    """LookupPort looks up the port for a network and service."""
    try:
        return Ok(_socket.getservbyname(service, network))
    except Exception as e:
        return Err(GoError(str(e), "net.Error"))


def LookupCNAME(host: str) -> Result[str, GoError]:
    """LookupCNAME returns the canonical name for the given host."""
    try:
        return Ok(_socket.getfqdn(host))
    except Exception as e:
        return Err(GoError(str(e), "net.DNSError"))


def LookupMX(name: str) -> Result[list[tuple[str, int]], GoError]:
    """LookupMX returns the MX records for the given domain name."""
    try:
        import dns.resolver

        answers = dns.resolver.resolve(name, "MX")
        return Ok([(str(r.exchange), r.preference) for r in answers])
    except ImportError:
        return Err(GoError("dnspython not installed", "net.Error"))
    except Exception as e:
        return Err(GoError(str(e), "net.DNSError"))


def LookupTXT(name: str) -> Result[list[str], GoError]:
    """LookupTXT returns the TXT records for the given domain name."""
    try:
        import dns.resolver

        answers = dns.resolver.resolve(name, "TXT")
        return Ok([str(r) for r in answers])
    except ImportError:
        return Err(GoError("dnspython not installed", "net.Error"))
    except Exception as e:
        return Err(GoError(str(e), "net.DNSError"))


def SplitHostPort(hostport: str) -> tuple[Result[str, GoError], Result[str, GoError]]:
    """SplitHostPort splits a network address into host and port."""
    try:
        if hostport.startswith("["):
            bracket = hostport.find("]")
            if bracket == -1:
                return Err(GoError("missing ']' in address", "net.AddrError")), Err(GoError("", ""))
            host = hostport[1:bracket]
            rest = hostport[bracket + 1 :]
            if rest.startswith(":"):
                return Ok(host), Ok(rest[1:])
            return Ok(host), Ok("")

        colon = hostport.rfind(":")
        if colon == -1:
            return Ok(hostport), Ok("")
        return Ok(hostport[:colon]), Ok(hostport[colon + 1 :])
    except Exception as e:
        return Err(GoError(str(e), "net.AddrError")), Err(GoError(str(e), "net.AddrError"))


def JoinHostPort(host: str, port: str) -> str:
    """JoinHostPort combines host and port into a network address."""
    if ":" in host:
        return f"[{host}]:{port}"
    return f"{host}:{port}"


def ParseIP(s: str) -> IP | None:
    """ParseIP parses s as an IP address."""
    try:
        parts = s.split(".")
        if len(parts) == 4:
            return IP(bytes(int(p) for p in parts))

        if ":" in s:
            parts = s.split(":")
            result = []
            for part in parts:
                if part == "":
                    result.extend([0, 0])
                else:
                    val = int(part, 16)
                    result.extend([val >> 8, val & 0xFF])
            while len(result) < 16:
                result.insert(len(result) // 2, 0)
            return IP(bytes(result[:16]))
    except Exception:
        pass
    return None


def ParseCIDR(s: str) -> Result[tuple[IP, IPNet], GoError]:
    """ParseCIDR parses s as a CIDR notation IP address and prefix length."""
    try:
        addr, prefix = s.split("/")
        ip = ParseIP(addr)
        if ip is None:
            return Err(GoError(f"invalid CIDR address: {s}", "net.ParseError"))

        prefix_len = int(prefix)
        ip_len = len(ip._bytes)
        mask = bytearray(ip_len)

        for i in range(prefix_len):
            mask[i // 8] |= 0x80 >> (i % 8)

        net_ip = IP(bytes(a & m for a, m in zip(ip._bytes, mask, strict=False)))
        return Ok((ip, IPNet(IP=net_ip, Mask=bytes(mask))))
    except Exception:
        return Err(GoError(f"invalid CIDR address: {s}", "net.ParseError"))


def ResolveIPAddr(network: str, address: str) -> Result[IPAddr, GoError]:
    """ResolveIPAddr resolves address as an IP address."""
    ip = ParseIP(address)
    if ip:
        return Ok(IPAddr(IP=ip))

    result = LookupHost(address)
    if result.is_err():
        err = result.err()
        assert err is not None
        return Err(err)

    addrs = result.unwrap()
    if not addrs:
        return Err(GoError(f"no addresses found for {address}", "net.DNSError"))

    ip = ParseIP(addrs[0])
    if ip is None:
        return Err(GoError(f"invalid address: {addrs[0]}", "net.ParseError"))
    return Ok(IPAddr(IP=ip))


def ResolveTCPAddr(network: str, address: str) -> Result[TCPAddr, GoError]:
    """ResolveTCPAddr resolves address as a TCP address."""
    host_result, port_result = SplitHostPort(address)
    if host_result.is_err():
        err = host_result.err()
        assert err is not None
        return Err(err)

    host = host_result.unwrap()
    port_str = port_result.unwrap() if port_result.is_ok() else "0"

    try:
        port = int(port_str) if port_str else 0
    except ValueError:
        return Err(GoError(f"invalid port: {port_str}", "net.AddrError"))

    ip = ParseIP(host)
    if ip is None:
        result = LookupHost(host)
        if result.is_err():
            err = result.err()
            assert err is not None
            return Err(err)
        addrs = result.unwrap()
        if addrs:
            ip = ParseIP(addrs[0])

    if ip is None:
        ip = IPv4(0, 0, 0, 0)

    return Ok(TCPAddr(IP=ip, Port=port))


def ResolveUDPAddr(network: str, address: str) -> Result[UDPAddr, GoError]:
    """ResolveUDPAddr resolves address as a UDP address."""
    result = ResolveTCPAddr(network, address)
    if result.is_err():
        err = result.err()
        assert err is not None
        return Err(err)
    tcp = result.unwrap()
    return Ok(UDPAddr(IP=tcp.IP, Port=tcp.Port, Zone=tcp.Zone))


def _parse_address(address: str) -> tuple[str, int]:
    """Parse an address string into host and port."""
    host_result, port_result = SplitHostPort(address)
    host = host_result.unwrap() if host_result.is_ok() else ""
    port_str = port_result.unwrap() if port_result.is_ok() else "0"
    port = int(port_str) if port_str else 0
    return host, port
