import uuid
import platform

def get_mac_address():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(5, -1, -1)])
    print(f"MAC Address: {mac}")
    return mac

def get_unique_identifier():
    node = uuid.getnode()
    if node == 0x000000000000:
        node = uuid.uuid1().node
    unique_id = uuid.uuid5(uuid.NAMESPACE_DNS, str(node))
    return str(unique_id)
#86442213-96e5-5770-9c5f-393d54b6093f

if platform.system().lower() == 'windows':
    mac_address = get_mac_address()
    print(f"MAC Address: {mac_address}")

unique_identifier = get_unique_identifier()
print(f"Unique Identifier: {unique_identifier}")
