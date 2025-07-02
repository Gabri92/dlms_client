#!/usr/bin/env python3
import sys
import traceback
from GXSettings import GXSettings
from GXDLMSReader import GXDLMSReader
from gurux_dlms.enums import ObjectType

# Usage: python read_single_obis.py <OBIS_CODE> [ATTRIBUTE_INDEX] [other connection params]
def main():
    if len(sys.argv) < 2:
        print("Usage: python read_single_obis.py <OBIS_CODE> [ATTRIBUTE_INDEX] [other connection params]")
        sys.exit(1)
    obis_code = sys.argv[1]
    try:
        attribute_index = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 2
        extra_args = sys.argv[3:] if len(sys.argv) > 2 and sys.argv[2].isdigit() else sys.argv[2:]
    except Exception:
        attribute_index = 2
        extra_args = sys.argv[2:]

    settings = GXSettings()
    try:
        ret = settings.getParameters([sys.argv[0]] + extra_args)
        if ret != 0:
            print("Failed to parse connection parameters.")
            sys.exit(1)
        if not settings.media:
            print("No media/connection type specified.")
            sys.exit(1)
        reader = GXDLMSReader(settings.client, settings.media, settings.trace, settings.invocationCounter)
        settings.media.open()
        reader.initializeConnection()
        # Get association view if needed
        reader.getAssociationView()
        obj = settings.client.objects.findByLN(ObjectType.NONE, obis_code)
        if obj is None:
            print(f"Unknown logical name: {obis_code}")
            sys.exit(1)
        val = reader.read(obj, attribute_index)
        print(f"Value for OBIS {obis_code} (attribute {attribute_index}): {val}")
    except Exception as ex:
        print("Error:", ex)
        traceback.print_exc()
    finally:
        try:
            if settings.media:
                settings.media.close()
        except Exception:
            pass

if __name__ == "__main__":
    main() 