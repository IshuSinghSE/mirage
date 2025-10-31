import random
import string
import subprocess
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange, IPVersion

def get_code(n):
	return ''.join(random.choices(string.ascii_letters, k=n))

def pair_device(address, port, password, status_cb=None):
	if status_cb:
		status_cb("Pairing device...")
	args = ["adb", "pair", f"{address}:{port}", password]
	proc = subprocess.run(args, capture_output=True)
	if proc.returncode == 0:
		if status_cb:
			status_cb(f"[Paired] {address}:{port}")
		return True
	else:
		if status_cb:
			status_cb(f"Pairing failed: {proc.stderr.decode()}")
		return False

def connect_device(address, port, status_cb=None):
	if status_cb:
		status_cb("Connecting device...")
	args = ["adb", "connect", f"{address}:{port}"]
	proc = subprocess.run(args, capture_output=True)
	if proc.returncode == 0:
		if status_cb:
			status_cb("Done!")
		return True
	else:
		if status_cb:
			status_cb(f"Connect failed: {proc.stderr.decode()}")
		return False

def start_mdns_pairing(password, on_pair_and_connect, device_ports=None):
	"""
	Starts mDNS ServiceBrowser for ADB pairing. Calls on_pair_and_connect(addr, pair_port, connect_port) when ready.
	Returns Zeroconf instance and device_ports list.
	"""
	if device_ports is None:
		device_ports = []
	zc = Zeroconf(ip_version=IPVersion.V4Only)

	def on_service_state_change(zeroconf, service_type, name, state_change):
		if state_change is ServiceStateChange.Added:
			info = zeroconf.get_service_info(service_type, name)
			if not info:
				return
			addr = info.parsed_addresses()[0]
			if service_type == "_adb-tls-pairing._tcp.local.":
				if not device_ports:
					return
				pair_port = info.port or 5555
				connect_port = device_ports[0]
				on_pair_and_connect(addr, pair_port, connect_port)
			elif service_type == "_adb-tls-connect._tcp.local.":
				device_ports.append(info.port)

	ServiceBrowser(zc, "_adb-tls-pairing._tcp.local.", handlers=[on_service_state_change])
	ServiceBrowser(zc, "_adb-tls-connect._tcp.local.", handlers=[on_service_state_change])
	return zc, device_ports
