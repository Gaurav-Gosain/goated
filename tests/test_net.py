"""Tests for goated.std.net module (net)."""

from goated.std import net


class TestIP:
    """Test IP class."""

    def test_ipv4_string(self):
        ip = net.IPv4(192, 168, 1, 1)
        assert ip.String() == "192.168.1.1"

    def test_ipv4_loopback(self):
        ip = net.IPv4(127, 0, 0, 1)
        assert ip.IsLoopback()

    def test_ipv4_not_loopback(self):
        ip = net.IPv4(192, 168, 1, 1)
        assert not ip.IsLoopback()

    def test_ipv4_private_10(self):
        ip = net.IPv4(10, 0, 0, 1)
        assert ip.IsPrivate()

    def test_ipv4_private_172(self):
        ip = net.IPv4(172, 16, 0, 1)
        assert ip.IsPrivate()

    def test_ipv4_private_192(self):
        ip = net.IPv4(192, 168, 1, 1)
        assert ip.IsPrivate()

    def test_ipv4_not_private(self):
        ip = net.IPv4(8, 8, 8, 8)
        assert not ip.IsPrivate()

    def test_ipv4_unspecified(self):
        ip = net.IPv4(0, 0, 0, 0)
        assert ip.IsUnspecified()

    def test_ipv4_to4(self):
        ip = net.IPv4(192, 168, 1, 1)
        assert ip.To4() is ip

    def test_ipv4_to16(self):
        ip = net.IPv4(192, 168, 1, 1)
        ip16 = ip.To16()
        assert ip16 is not None
        assert len(ip16._bytes) == 16

    def test_ip_equal(self):
        ip1 = net.IPv4(1, 2, 3, 4)
        ip2 = net.IPv4(1, 2, 3, 4)
        assert ip1.Equal(ip2)

    def test_ip_not_equal(self):
        ip1 = net.IPv4(1, 2, 3, 4)
        ip2 = net.IPv4(1, 2, 3, 5)
        assert not ip1.Equal(ip2)


class TestIPv6:
    """Test IPv6 addresses."""

    def test_ipv6_loopback(self):
        assert net.IPv6loopback.IsLoopback()

    def test_ipv6_zero_unspecified(self):
        assert net.IPv6zero.IsUnspecified()


class TestIPAddr:
    """Test IPAddr class."""

    def test_ip_addr_network(self):
        addr = net.IPAddr(IP=net.IPv4(192, 168, 1, 1))
        assert addr.Network() == "ip"

    def test_ip_addr_string(self):
        addr = net.IPAddr(IP=net.IPv4(192, 168, 1, 1))
        assert addr.String() == "192.168.1.1"

    def test_ip_addr_with_zone(self):
        addr = net.IPAddr(IP=net.IPv4(192, 168, 1, 1), Zone="eth0")
        assert "eth0" in addr.String()


class TestTCPAddr:
    """Test TCPAddr class."""

    def test_tcp_addr_network(self):
        addr = net.TCPAddr(IP=net.IPv4(127, 0, 0, 1), Port=8080)
        assert addr.Network() == "tcp"

    def test_tcp_addr_string(self):
        addr = net.TCPAddr(IP=net.IPv4(127, 0, 0, 1), Port=8080)
        assert addr.String() == "127.0.0.1:8080"


class TestUDPAddr:
    """Test UDPAddr class."""

    def test_udp_addr_network(self):
        addr = net.UDPAddr(IP=net.IPv4(127, 0, 0, 1), Port=53)
        assert addr.Network() == "udp"

    def test_udp_addr_string(self):
        addr = net.UDPAddr(IP=net.IPv4(127, 0, 0, 1), Port=53)
        assert addr.String() == "127.0.0.1:53"


class TestIPNet:
    """Test IPNet class."""

    def test_ip_net_string(self):
        ipnet = net.IPNet(IP=net.IPv4(192, 168, 1, 0), Mask=bytes([255, 255, 255, 0]))
        assert ipnet.String() == "192.168.1.0/24"

    def test_ip_net_contains(self):
        ipnet = net.IPNet(IP=net.IPv4(192, 168, 1, 0), Mask=bytes([255, 255, 255, 0]))
        assert ipnet.Contains(net.IPv4(192, 168, 1, 100))

    def test_ip_net_not_contains(self):
        ipnet = net.IPNet(IP=net.IPv4(192, 168, 1, 0), Mask=bytes([255, 255, 255, 0]))
        assert not ipnet.Contains(net.IPv4(192, 168, 2, 1))


class TestParseIP:
    """Test ParseIP function."""

    def test_parse_ipv4(self):
        ip = net.ParseIP("192.168.1.1")
        assert ip is not None
        assert ip.String() == "192.168.1.1"

    def test_parse_ipv4_loopback(self):
        ip = net.ParseIP("127.0.0.1")
        assert ip is not None
        assert ip.IsLoopback()

    def test_parse_invalid(self):
        ip = net.ParseIP("not an ip")
        assert ip is None

    def test_parse_empty(self):
        ip = net.ParseIP("")
        assert ip is None


class TestParseCIDR:
    """Test ParseCIDR function."""

    def test_parse_cidr_24(self):
        result = net.ParseCIDR("192.168.1.0/24")
        assert result.is_ok()
        ip, ipnet = result.unwrap()
        assert ip.String() == "192.168.1.0"
        assert "24" in ipnet.String()

    def test_parse_cidr_16(self):
        result = net.ParseCIDR("10.0.0.0/16")
        assert result.is_ok()
        ip, ipnet = result.unwrap()
        assert ip.String() == "10.0.0.0"

    def test_parse_cidr_invalid(self):
        result = net.ParseCIDR("invalid")
        assert result.is_err()


class TestSplitHostPort:
    """Test SplitHostPort function."""

    def test_split_simple(self):
        host, port = net.SplitHostPort("localhost:8080")
        assert host.unwrap() == "localhost"
        assert port.unwrap() == "8080"

    def test_split_ipv4(self):
        host, port = net.SplitHostPort("192.168.1.1:80")
        assert host.unwrap() == "192.168.1.1"
        assert port.unwrap() == "80"

    def test_split_ipv6_brackets(self):
        host, port = net.SplitHostPort("[::1]:8080")
        assert host.unwrap() == "::1"
        assert port.unwrap() == "8080"

    def test_split_no_port(self):
        host, port = net.SplitHostPort("localhost")
        assert host.unwrap() == "localhost"
        assert port.unwrap() == ""


class TestJoinHostPort:
    """Test JoinHostPort function."""

    def test_join_simple(self):
        result = net.JoinHostPort("localhost", "8080")
        assert result == "localhost:8080"

    def test_join_ipv4(self):
        result = net.JoinHostPort("192.168.1.1", "80")
        assert result == "192.168.1.1:80"

    def test_join_ipv6(self):
        result = net.JoinHostPort("::1", "8080")
        assert result == "[::1]:8080"


class TestResolveTCPAddr:
    """Test ResolveTCPAddr function."""

    def test_resolve_tcp_addr_ip(self):
        result = net.ResolveTCPAddr("tcp", "127.0.0.1:8080")
        assert result.is_ok()
        addr = result.unwrap()
        assert addr.Port == 8080

    def test_resolve_tcp_addr_no_port(self):
        result = net.ResolveTCPAddr("tcp", "127.0.0.1")
        assert result.is_ok()
        addr = result.unwrap()
        assert addr.Port == 0


class TestResolveUDPAddr:
    """Test ResolveUDPAddr function."""

    def test_resolve_udp_addr(self):
        result = net.ResolveUDPAddr("udp", "127.0.0.1:53")
        assert result.is_ok()
        addr = result.unwrap()
        assert addr.Port == 53


class TestResolveIPAddr:
    """Test ResolveIPAddr function."""

    def test_resolve_ip_addr(self):
        result = net.ResolveIPAddr("ip", "127.0.0.1")
        assert result.is_ok()
        addr = result.unwrap()
        assert addr.IP.IsLoopback()


class TestLookupHost:
    """Test LookupHost function."""

    def test_lookup_localhost(self):
        result = net.LookupHost("localhost")
        assert result.is_ok()
        addrs = result.unwrap()
        assert len(addrs) >= 1


class TestLookupIP:
    """Test LookupIP function."""

    def test_lookup_ip_localhost(self):
        result = net.LookupIP("localhost")
        assert result.is_ok()
        ips = result.unwrap()
        assert len(ips) >= 1


class TestLookupCNAME:
    """Test LookupCNAME function."""

    def test_lookup_cname_localhost(self):
        result = net.LookupCNAME("localhost")
        assert result.is_ok()


class TestConn:
    """Test Conn class."""

    def test_conn_methods_exist(self):
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = net.Conn(sock)

        assert hasattr(conn, "Read")
        assert hasattr(conn, "Write")
        assert hasattr(conn, "Close")
        assert hasattr(conn, "LocalAddr")
        assert hasattr(conn, "RemoteAddr")
        assert hasattr(conn, "SetDeadline")

        sock.close()


class TestTCPConn:
    """Test TCPConn class."""

    def test_tcp_conn_is_conn(self):
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = net.TCPConn(sock)
        assert isinstance(conn, net.Conn)
        sock.close()


class TestUDPConn:
    """Test UDPConn class."""

    def test_udp_conn_methods_exist(self):
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conn = net.UDPConn(sock)

        assert hasattr(conn, "ReadFrom")
        assert hasattr(conn, "WriteTo")
        assert hasattr(conn, "Close")

        sock.close()


class TestListener:
    """Test Listener class."""

    def test_listener_methods_exist(self):
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener = net.Listener(sock)

        assert hasattr(listener, "Accept")
        assert hasattr(listener, "Close")
        assert hasattr(listener, "Addr")

        sock.close()


class TestTCPListener:
    """Test TCPListener class."""

    def test_tcp_listener_is_listener(self):
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener = net.TCPListener(sock)
        assert isinstance(listener, net.Listener)
        sock.close()


class TestDialUnknownNetwork:
    """Test Dial with unknown network."""

    def test_dial_unknown_network(self):
        result = net.Dial("unknown", "localhost:8080")
        assert result.is_err()
        assert "unknown network" in str(result.err())


class TestListenUnknownNetwork:
    """Test Listen with unknown network."""

    def test_listen_unknown_network(self):
        result = net.Listen("unknown", ":8080")
        assert result.is_err()
        assert "unknown network" in str(result.err())


class TestModuleExports:
    """Test module exports."""

    def test_exports(self):
        assert hasattr(net, "Dial")
        assert hasattr(net, "DialTCP")
        assert hasattr(net, "DialUDP")
        assert hasattr(net, "DialTimeout")
        assert hasattr(net, "Listen")
        assert hasattr(net, "ListenTCP")
        assert hasattr(net, "ListenUDP")
        assert hasattr(net, "LookupHost")
        assert hasattr(net, "LookupIP")
        assert hasattr(net, "LookupAddr")
        assert hasattr(net, "LookupPort")
        assert hasattr(net, "LookupCNAME")
        assert hasattr(net, "SplitHostPort")
        assert hasattr(net, "JoinHostPort")
        assert hasattr(net, "ParseIP")
        assert hasattr(net, "ParseCIDR")
        assert hasattr(net, "ResolveIPAddr")
        assert hasattr(net, "ResolveTCPAddr")
        assert hasattr(net, "ResolveUDPAddr")
        assert hasattr(net, "Conn")
        assert hasattr(net, "Listener")
        assert hasattr(net, "TCPConn")
        assert hasattr(net, "UDPConn")
        assert hasattr(net, "TCPListener")
        assert hasattr(net, "IP")
        assert hasattr(net, "IPAddr")
        assert hasattr(net, "TCPAddr")
        assert hasattr(net, "UDPAddr")
        assert hasattr(net, "IPNet")
        assert hasattr(net, "IPv4")
        assert hasattr(net, "IPv6loopback")
        assert hasattr(net, "IPv6zero")
