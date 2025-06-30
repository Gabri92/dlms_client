import sys
import os
import traceback
import argparse
from gurux_serial import GXSerial
from gurux_dlms import GXDLMSClient, GXByteBuffer
from gurux_dlms.enums import InterfaceType, Authentication
from gurux_dlms.objects import GXDLMSClock

# Optional: allow running from any path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def read_clock(port_name, client_address, server_address):
    client = GXDLMSClient(
        useLogicalNameReferencing=True,
        clientAddress=client_address,
        serverAddress=server_address,
        interfaceType=InterfaceType.HDLC,
        forAuthentication=Authentication.NONE
    )

    connection = GXSerial(port_name)
    connection.baudRate = 9600
    connection.dataBits = 8
    connection.stopBits = 1
    connection.parity = "None"

    try:
        connection.open()
        client.initializeConnection()

        # SNRM & UA
        snrm = client.snrmRequest()
        if snrm:
            connection.send(snrm)
            bb = GXByteBuffer(connection.receive())
            client.parseUAResponse(bb)

        # AARQ & AARE
        connection.send(client.aarqRequest())
        bb = GXByteBuffer(connection.receive())
        client.parseAAREResponse(bb)

        # Read Clock object (attribute 2 = time)
        clock = GXDLMSClock()
        clock.logicalName = "0.0.1.0.0.255"

        request = client.read(clock, 2)[0]
        connection.send(request)
        bb = GXByteBuffer(connection.receive())
        result = client.parseReadResponse(clock, bb)[0]
        client.updateValue(clock, 2, result)

        print("Clock time:", clock.time)

        # Disconnect
        disc = client.disconnectRequest()
        if disc:
            connection.send(disc)

    except Exception as e:
        print("Error:", e)
        traceback.print_exc()
    finally:
        connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DLMS Client CLI")
    parser.add_argument("-p", "--port", type=str, required=True, help="Serial port (e.g., COM3 or /dev/ttyUSB0)")
    parser.add_argument("-c", "--client", type=int, default=16, help="Client address (default: 16)")
    parser.add_argument("-s", "--server", type=int, default=1, help="Server address (default: 1)")
    args = parser.parse_args()

    read_clock(args.port, args.client, args.server)
