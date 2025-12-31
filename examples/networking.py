#!/usr/bin/env python3
"""Networking examples using goated.std.net.

Demonstrates:
- IP address handling
- TCP/UDP address parsing
- Network lookups (DNS)
- Address manipulation
- CIDR notation
"""

from goated.std import net


def demo_ip_addresses():
    """Demonstrate IP address operations."""
    print("=== IP Addresses ===\n")

    # Create IPv4 addresses
    localhost = net.IPv4(127, 0, 0, 1)
    private = net.IPv4(192, 168, 1, 100)
    public = net.IPv4(8, 8, 8, 8)

    print("IPv4 addresses:")
    print(f"  localhost: {localhost.String()}")
    print(f"  private:   {private.String()}")
    print(f"  public:    {public.String()}")

    # IP properties
    print("\nIP properties:")
    print(f"  {localhost.String()} is loopback: {localhost.IsLoopback()}")
    print(f"  {private.String()} is private: {private.IsPrivate()}")
    print(f"  {public.String()} is private: {public.IsPrivate()}")

    # Unspecified address
    unspec = net.IPv4(0, 0, 0, 0)
    print(f"  {unspec.String()} is unspecified: {unspec.IsUnspecified()}")

    # IPv6
    print("\nIPv6 addresses:")
    print(f"  IPv6 loopback: {net.IPv6loopback.String()}")
    print(f"  IPv6 zero:     {net.IPv6zero.String()}")
    print(f"  IPv6 loopback is loopback: {net.IPv6loopback.IsLoopback()}")
    print()


def demo_parse_ip():
    """Demonstrate IP parsing."""
    print("=== Parsing IP Addresses ===\n")

    addresses = [
        "192.168.1.1",
        "10.0.0.1",
        "127.0.0.1",
        "255.255.255.255",
        "invalid",
        "",
    ]

    for addr in addresses:
        ip = net.ParseIP(addr)
        if ip:
            print(
                f"  '{addr}' -> {ip.String()} (loopback={ip.IsLoopback()}, private={ip.IsPrivate()})"
            )
        else:
            print(f"  '{addr}' -> Invalid")
    print()


def demo_ip_conversion():
    """Demonstrate IP address conversion."""
    print("=== IP Address Conversion ===\n")

    ipv4 = net.IPv4(192, 168, 1, 1)
    print(f"Original IPv4: {ipv4.String()}")

    # Convert to IPv6 mapped address
    ipv6 = ipv4.To16()
    if ipv6:
        print(f"As IPv6 (mapped): {ipv6.String()}")

    # Convert back to IPv4
    back_to_v4 = ipv6.To4()
    if back_to_v4:
        print(f"Back to IPv4: {back_to_v4.String()}")

    # Compare addresses
    ipv4_2 = net.IPv4(192, 168, 1, 1)
    print("\nEquality check:")
    print(f"  {ipv4.String()} == {ipv4_2.String()}: {ipv4.Equal(ipv4_2)}")

    ipv4_3 = net.IPv4(192, 168, 1, 2)
    print(f"  {ipv4.String()} == {ipv4_3.String()}: {ipv4.Equal(ipv4_3)}")
    print()


def demo_cidr():
    """Demonstrate CIDR notation."""
    print("=== CIDR Notation ===\n")

    cidrs = [
        "192.168.1.0/24",
        "10.0.0.0/8",
        "172.16.0.0/16",
    ]

    for cidr in cidrs:
        result = net.ParseCIDR(cidr)
        if result.is_ok():
            ip, ipnet = result.unwrap()
            print(f"CIDR: {cidr}")
            print(f"  IP: {ip.String()}")
            print(f"  Network: {ipnet.String()}")

            # Check what IPs are in the network
            test_ips = [
                net.IPv4(192, 168, 1, 100),
                net.IPv4(192, 168, 2, 1),
                net.IPv4(10, 0, 0, 1),
            ]
            print("  Contains:")
            for test_ip in test_ips:
                print(f"    {test_ip.String()}: {ipnet.Contains(test_ip)}")
            print()


def demo_tcp_udp_addresses():
    """Demonstrate TCP and UDP address handling."""
    print("=== TCP/UDP Addresses ===\n")

    # TCP address
    tcp_addr = net.TCPAddr(
        IP=net.IPv4(127, 0, 0, 1),
        Port=8080,
    )
    print("TCP Address:")
    print(f"  Network: {tcp_addr.Network()}")
    print(f"  String:  {tcp_addr.String()}")

    # UDP address
    udp_addr = net.UDPAddr(
        IP=net.IPv4(127, 0, 0, 1),
        Port=53,
    )
    print("\nUDP Address:")
    print(f"  Network: {udp_addr.Network()}")
    print(f"  String:  {udp_addr.String()}")

    # IP address
    ip_addr = net.IPAddr(IP=net.IPv4(192, 168, 1, 1))
    print("\nIP Address:")
    print(f"  Network: {ip_addr.Network()}")
    print(f"  String:  {ip_addr.String()}")

    # With zone (for IPv6 link-local)
    ip_addr_zone = net.IPAddr(IP=net.IPv4(192, 168, 1, 1), Zone="eth0")
    print("\nIP Address with Zone:")
    print(f"  String:  {ip_addr_zone.String()}")
    print()


def demo_split_join():
    """Demonstrate SplitHostPort and JoinHostPort."""
    print("=== SplitHostPort / JoinHostPort ===\n")

    addresses = [
        "localhost:8080",
        "192.168.1.1:443",
        "[::1]:8080",
        "example.com:80",
        "localhost",  # No port
    ]

    print("Splitting addresses:")
    for addr in addresses:
        host_result, port_result = net.SplitHostPort(addr)
        if host_result.is_ok() and port_result.is_ok():
            host = host_result.unwrap()
            port = port_result.unwrap()
            print(f"  '{addr}' -> host='{host}', port='{port}'")

    print("\nJoining addresses:")
    pairs = [
        ("localhost", "8080"),
        ("192.168.1.1", "443"),
        ("::1", "8080"),  # IPv6 gets brackets
    ]
    for host, port in pairs:
        joined = net.JoinHostPort(host, port)
        print(f"  host='{host}', port='{port}' -> '{joined}'")
    print()


def demo_resolve_addresses():
    """Demonstrate address resolution."""
    print("=== Address Resolution ===\n")

    # Resolve TCP address
    result = net.ResolveTCPAddr("tcp", "127.0.0.1:8080")
    if result.is_ok():
        addr = result.unwrap()
        print("ResolveTCPAddr('127.0.0.1:8080'):")
        print(f"  IP: {addr.IP.String()}")
        print(f"  Port: {addr.Port}")

    # Resolve UDP address
    result = net.ResolveUDPAddr("udp", "127.0.0.1:53")
    if result.is_ok():
        addr = result.unwrap()
        print("\nResolveUDPAddr('127.0.0.1:53'):")
        print(f"  IP: {addr.IP.String()}")
        print(f"  Port: {addr.Port}")

    # Resolve IP address
    result = net.ResolveIPAddr("ip", "127.0.0.1")
    if result.is_ok():
        addr = result.unwrap()
        print("\nResolveIPAddr('127.0.0.1'):")
        print(f"  IP: {addr.IP.String()}")
    print()


def demo_dns_lookups():
    """Demonstrate DNS lookups."""
    print("=== DNS Lookups ===\n")

    # Lookup host
    result = net.LookupHost("localhost")
    if result.is_ok():
        addrs = result.unwrap()
        print(f"LookupHost('localhost'): {addrs}")

    # Lookup IP
    result = net.LookupIP("localhost")
    if result.is_ok():
        ips = result.unwrap()
        print(f"LookupIP('localhost'): {[ip.String() for ip in ips]}")

    # Lookup CNAME
    result = net.LookupCNAME("localhost")
    if result.is_ok():
        cname = result.unwrap()
        print(f"LookupCNAME('localhost'): {cname}")

    print("\nNote: LookupMX and LookupTXT require dnspython package")
    print()


def demo_dial_patterns():
    """Demonstrate dial patterns (without actually connecting)."""
    print("=== Dial Patterns ===\n")

    print("TCP connection patterns:")
    print('  conn = net.Dial("tcp", "example.com:80")')
    print('  conn = net.DialTCP("tcp", None, tcpAddr)')
    print('  conn = net.DialTimeout("tcp", "example.com:80", 5.0)')

    print("\nUDP connection patterns:")
    print('  conn = net.Dial("udp", "8.8.8.8:53")')
    print('  conn = net.DialUDP("udp", None, udpAddr)')

    print("\nListener patterns:")
    print('  listener = net.Listen("tcp", ":8080")')
    print('  listener = net.ListenTCP("tcp", tcpAddr)')
    print('  conn = net.ListenUDP("udp", udpAddr)')

    print("\nConnection methods:")
    print("  n, err = conn.Read(buffer)")
    print("  n, err = conn.Write(data)")
    print("  conn.Close()")
    print("  conn.LocalAddr()")
    print("  conn.RemoteAddr()")
    print("  conn.SetDeadline(timeout)")
    print()


def demo_ip_network():
    """Demonstrate IPNet operations."""
    print("=== IP Networks ===\n")

    # Create network manually
    ipnet = net.IPNet(
        IP=net.IPv4(192, 168, 0, 0),
        Mask=bytes([255, 255, 0, 0]),  # /16
    )

    print(f"Network: {ipnet.String()}")

    # Test containment
    test_ips = [
        ("192.168.1.1", net.IPv4(192, 168, 1, 1)),
        ("192.168.255.255", net.IPv4(192, 168, 255, 255)),
        ("192.169.0.1", net.IPv4(192, 169, 0, 1)),
        ("10.0.0.1", net.IPv4(10, 0, 0, 1)),
    ]

    print("\nContainment tests:")
    for name, ip in test_ips:
        print(f"  {name}: {ipnet.Contains(ip)}")
    print()


def main():
    print("=" * 60)
    print("  goated.std.net - Go's net package for Python")
    print("=" * 60)
    print()

    demo_ip_addresses()
    demo_parse_ip()
    demo_ip_conversion()
    demo_cidr()
    demo_tcp_udp_addresses()
    demo_split_join()
    demo_resolve_addresses()
    demo_dns_lookups()
    demo_dial_patterns()
    demo_ip_network()

    print("=" * 60)
    print("  Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
