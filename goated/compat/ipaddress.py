"""Drop-in replacement for Python's ipaddress module, backed by Go's net package.

Uses Go FFI for IP validation and parsing. Falls back to Python for full
IPv4Address/IPv6Address/ip_network objects.

Usage:
    from goated.compat import ipaddress
    addr = ipaddress.ip_address("192.168.1.1")
    valid = ipaddress.is_valid("10.0.0.1")
    results = ipaddress.batch_validate_ips(["10.0.0.1", "bad", "::1"])
"""

from __future__ import annotations

import ctypes
import ipaddress as _ipaddress

# Re-export everything from Python's ipaddress
from ipaddress import (  # noqa: F401
    AddressValueError,
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
    NetmaskValueError,
    collapse_addresses,
    ip_interface,
    ip_network,
    summarize_address_range,
)
from typing import Sequence, Union

from goated._core import _USE_GO_LIB, get_lib

_lib_setup = False


def _setup_lib() -> None:
    global _lib_setup
    if _lib_setup or not _USE_GO_LIB:
        return
    try:
        lib = get_lib().lib
        lib.goated_ip_is_valid.argtypes = [ctypes.c_char_p]
        lib.goated_ip_is_valid.restype = ctypes.c_bool
        lib.goated_ip_parse.argtypes = [ctypes.c_char_p]
        lib.goated_ip_parse.restype = ctypes.c_char_p
        lib.goated_cidr_contains.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        lib.goated_cidr_contains.restype = ctypes.c_bool
        _lib_setup = True
    except Exception:
        pass


def ip_address(address: Union[str, int, bytes]) -> Union[IPv4Address, IPv6Address]:
    """Construct an IPv4 or IPv6 address.

    Uses Go for fast validation when the input is a string, then delegates
    to Python for object creation.
    """
    if isinstance(address, str) and _USE_GO_LIB:
        # Prefer cffi
        from goated._core import get_cffi_lib

        cffi_lib = get_cffi_lib()
        if cffi_lib is not None:
            try:
                valid = cffi_lib.goated_ip_is_valid(address.encode("utf-8"))
                if not valid:
                    raise ValueError(f"{address!r} does not appear to be an IPv4 or IPv6 address")
            except ValueError:
                raise
            except Exception:
                pass
            else:
                return _ipaddress.ip_address(address)

        # Fallback to ctypes
        _setup_lib()
        if _lib_setup:
            try:
                lib = get_lib().lib
                valid = lib.goated_ip_is_valid(address.encode("utf-8"))
                if not valid:
                    raise ValueError(f"{address!r} does not appear to be an IPv4 or IPv6 address")
            except ValueError:
                raise
            except Exception:
                pass
            else:
                return _ipaddress.ip_address(address)

    return _ipaddress.ip_address(address)


def is_valid(address: str) -> bool:
    """Check if a string is a valid IP address. Go-accelerated.

    This is a goated extension -- not part of Python's ipaddress module.
    """
    if _USE_GO_LIB:
        from goated._core import get_cffi_lib

        cffi_lib = get_cffi_lib()
        if cffi_lib is not None:
            try:
                return bool(cffi_lib.goated_ip_is_valid(address.encode("utf-8")))
            except Exception:
                pass

        _setup_lib()
        if _lib_setup:
            try:
                lib = get_lib().lib
                return bool(lib.goated_ip_is_valid(address.encode("utf-8")))
            except Exception:
                pass

    try:
        _ipaddress.ip_address(address)
        return True
    except ValueError:
        return False


def batch_validate_ips(addresses: Sequence[str]) -> list[bool]:
    """Validate multiple IP addresses. Go-accelerated for batch processing.

    This is a goated extension -- not part of Python's ipaddress module.

    Returns:
        List of booleans, True if corresponding address is valid.
    """
    if _USE_GO_LIB:
        from goated._core import get_cffi_lib

        cffi_lib = get_cffi_lib()
        if cffi_lib is not None:
            try:
                results = []
                for addr in addresses:
                    results.append(bool(cffi_lib.goated_ip_is_valid(addr.encode("utf-8"))))
                return results
            except Exception:
                pass

        _setup_lib()
        if _lib_setup:
            try:
                lib = get_lib().lib
                results = []
                for addr in addresses:
                    results.append(bool(lib.goated_ip_is_valid(addr.encode("utf-8"))))
                return results
            except Exception:
                pass

    # Python fallback
    results = []
    for addr in addresses:
        try:
            _ipaddress.ip_address(addr)
            results.append(True)
        except ValueError:
            results.append(False)
    return results


def cidr_contains(cidr: str, ip: str) -> bool:
    """Check if an IP address is within a CIDR network. Go-accelerated.

    This is a goated extension -- not part of Python's ipaddress module.
    """
    if _USE_GO_LIB:
        from goated._core import get_cffi_lib

        cffi_lib = get_cffi_lib()
        if cffi_lib is not None:
            try:
                return bool(cffi_lib.goated_cidr_contains(
                    cidr.encode("utf-8"), ip.encode("utf-8"),
                ))
            except Exception:
                pass

        _setup_lib()
        if _lib_setup:
            try:
                lib = get_lib().lib
                return bool(lib.goated_cidr_contains(
                    cidr.encode("utf-8"), ip.encode("utf-8"),
                ))
            except Exception:
                pass

    # Python fallback
    network = _ipaddress.ip_network(cidr, strict=False)
    addr = _ipaddress.ip_address(ip)
    return addr in network


__all__ = [
    "ip_address",
    "ip_network",
    "ip_interface",
    "is_valid",
    "batch_validate_ips",
    "cidr_contains",
    "IPv4Address",
    "IPv4Network",
    "IPv4Interface",
    "IPv6Address",
    "IPv6Network",
    "IPv6Interface",
    "AddressValueError",
    "NetmaskValueError",
    "collapse_addresses",
    "summarize_address_range",
]
