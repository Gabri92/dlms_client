import argparse
import traceback
from gurux_dlms import GXDLMSClient, GXByteBuffer
from gurux_dlms.enums import InterfaceType, Authentication
from gurux_dlms.objects import GXDLMSClock
from gurux_net import GXNet

def read_clock_tcp(host, port, client_address, server_address):
    client = GXDLMSClient(
        useLogicalNameReferencing=True,
        clientAddress=client_address,
        serverAddress=server_address,
        interfaceType=InterfaceType.HDLC,
        forAuthentication=Authentication.NONE
    )
    
    connection = GXNet(name=host, portNo=port,)

    try:
        connection.open()

        snrm = client.snrmRequest()
        if snrm:
            connection.send(snrm)
            bb = GXByteBuffer(connection.receive())
            client.parseUAResponse(bb)

        connection.send(client.aarqRequest())
        bb = GXByteBuffer(connection.receive())
        client.parseAAREResponse(bb)

        clock = GXDLMSClock()
        clock.logicalName = "0.0.1.0.0.255"
        readRequest = client.read(clock, 2)[0]

        connection.send(readRequest)
        bb = GXByteBuffer(connection.receive())
        value = client.parseReadResponse(clock, bb)[0]
        client.updateValue(clock, 2, value)

        print("[OK] Clock:", clock.time)

        # Disconnect
        disc = client.disconnectRequest()
        if disc:
            connection.send(disc)

    except Exception as e:
        print("[ERROR]", e)
        traceback.print_exc()
    finally:
        connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", type=str, default="127.0.0.1", help="DLMS server host")
    parser.add_argument("-p", "--port", type=int, default=1000, help="DLMS server port")
    parser.add_argument("-c", "--client", type=int, default=16, help="Client address")
    parser.add_argument("-s", "--server", type=int, default=1, help="Server address")
    args = parser.parse_args()

    #read_clock_tcp(args.host, args.port, args.client, args.server)
    read_clock_tcp("127.0.0.1", 1000, 16, 1)
