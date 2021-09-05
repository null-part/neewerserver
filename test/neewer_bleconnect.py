#!/usr/bin/env python3
from bluepy import btle

macaddr='D1:28:C0:6B:32:34'

connection = btle.Peripheral(macaddr, btle.ADDR_TYPE_RANDOM, 0)

# Discovery
for service in connection.getServices():
    for charac in service.getCharacteristics():
        print("UUID: " + str(charac.uuid))
        print("Properties: " + str(charac.properties))
        print("Supports Read: " + str(charac.supportsRead()))
        print("Properties To String: " + str(charac.propertiesToString()))
        print("Handle: " + str(charac.getHandle()))
        print("")

# Change color (handle 14)
connection.writeCharacteristic(14, b"\x78\x87\x02\x62\x26\x89")
