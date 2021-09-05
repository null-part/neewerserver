#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NeewerServer is a small UDP server able to associate with a Neewer RGB LED
Light panel with BLE (Bluetooth Low Energy) based on his mac address. All UDP
messages will be passed to the bluetooth device.

You may need to be paired and trust the device before running this server.
We recommand using bluetoothctl.
"""

import argparse
import logging
import socket
import sys
import colorsys
from bluepy import btle

class NeewerServer:
    """
    A small UDP server to communicate with Neewer RGB 660 lights
    """

    def __init__(self, neewerAddress, listenAddress="0.0.0.0", listenPort=1664):
        """
        Init Neewer Server

        :param neewerAddress: Hardware address of the Neewer light
        :param listenAddress: Listening address for the server.
        :param listenPort: Listening port for the server.
        """
        self._btConnection = None
        self._btResponseDelegate = None
        self._udpSocket = None
        self.neewerAddress = neewerAddress
        self.listenAddress = listenAddress
        self.listenPort = listenPort


    def startUDPServer(self):
        """
        Open a listening socket to receive UDP messages.
        Each message is passed to the neewer device.
        """

        logging.info("Starting UDP server...")

        try:
            self._udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._udpSocket.bind((self.listenAddress, self.listenPort))
            logging.info("UDP Server started.")
            logging.info("Please send your messages to %s:%s",
                self.listenAddress, self.listenPort
            )
            while True:
                addr = self._udpSocket.recvfrom(1024)
                command = addr[0]
                address = addr[1]
                logging.debug("%s - %s", address, command)
                self.neewerSend(command, 14)

        except Exception as e:
            logging.error("UDP Server failed: %s", e)
            self._udpSocket = None
            return False

        return True


    def stopUDPServer(self):
        """
        Stop socket receiving UDP messages
        """

        logging.info("Stopping UDP Server...")

        try:
            self._udpSocket.close()

        except Exception:
            pass

        self._udpSocket = None


    def neewerConnect(self, btAdapter=0):
        """
        Connect to a Neewer RGB Lamp

        :param btAdapter: Bluetooth adapter ID. Defaults to 0
        """

        logging.debug("Connecting to Neewer device...")

        try:
            # Create connection and response delegate object
            connection = btle.Peripheral(self.neewerAddress,
                                         btle.ADDR_TYPE_RANDOM, btAdapter)

            self._btResponseDelegate = NeewerResponseDelegate()
            self._btConnection = connection.withDelegate(
                    self._btResponseDelegate
            )

            logging.info('Connected to Neewer device %s', self.neewerAddress)

        except RuntimeError as e:
            logging.error('Connection failed: %s', e)
            return False

        return True


    def neewerDisconnect(self):
        """
        Disconnect from Neewer Device
        """

        logging.debug("Disconnecting...")

        try:
            self._btConnection.disconnect()

        except btle.BTLEException:
            pass

        self._btConnection = None


    def neewerSend(self, message, cHandle=14):
        """
        Send bytes to Neewer Device

        :param message: bytes to pass to the device
        :param cHandle: handle (int) to use to communicate
        """

        # TODO: Properly interpret incoming bytes to add checksum
        #       + return error if message longer than 7 bytes?

        hsv = colorsys.rgb_to_hsv(message[0], message[1], message[2])

        # HUE
        # TODO: precision issue (e.g. 45 in touchdesigner => 44 here)
        hue360 = int(hsv[0]*360)

        hue_byte1 = bytes([0])
        hue_byte2 = bytes([0])

        if (hue360 < 256):
            hue_byte1 = hue360.to_bytes(1, 'big')
        else:
            hue_byte1 = (hue360%256).to_bytes(1, 'big')
            hue_byte2 = bytes([1])

        #print('Hue ====> {} _ {}'.format(hue_byte1, hue_byte2))

        # SATURATION
        sat_byte = int(hsv[1]*100).to_bytes(1, 'big')

        # VALUE
        # range/linear mapping to convert hsv[2] [0-255] to [0-100]
        val_byte = int((hsv[2]/255)*100).to_bytes(1, 'big')

        message = bytearray(b'\x78\x86\x04') + hue_byte1 + hue_byte2 + sat_byte + val_byte
        message = message + int(sum(message)%256).to_bytes(1, 'big')
        logging.info('msg+checksum={}'.format(message))

        try:
            self._btConnection.writeCharacteristic(cHandle, message)

            ## Should be already called on it's own, nothing to log here!
            # Deal with a potential response (aka Notification)
            #  notifTimeout = 0.01 # in seconds
            #  if self._btConnection.waitForNotifications(notifTimeout):
            #      # self.NeewerResponseDelegate.handleNotification() is called here
            #      logging.debug("Data received from notification: %s",
            #              self._btResponseDelegate.data
            #      )
            #  else:
            #      logging.debug('No response received in %s seconds',
            #              notifTimeout
            #      )

        except Exception as e:
            logging.error('Failed to send message: %s', e)


    def neewerScan(self):
        """
        Scan the Neewer device for Services and Characteristics
        """

        try:
            for service in self._btConnection.getServices():
                for charac in service.getCharacteristics():
                    logging.info("UUID: %s", charac.uuid)
                    logging.info("Properties: %s", charac.properties)
                    logging.info("Supports Read: %s", charac.supportsRead())
                    logging.info("Properties To String: %s", charac.propertiesToString())
                    logging.info("Handle: %s", charac.getHandle())
                    logging.info("")

        except Exception as e:
            logging.error('Failed to scan device: %s', e)


class NeewerResponseDelegate(btle.DefaultDelegate):
    """
    Listen for responses from Neewer Device

    Notifications are processed by bluepy's Delegate class
    which is registered with the Peripheral (_btConnection)
    """

    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self.data = None


    def handleNotification(self, cHandle, data):
        logging.debug('Received notification (cHandle=%s): %s', cHandle, data)
        self.data = data


def get_params():
    """
    Read parameters
    """
    parser = argparse.ArgumentParser(description='Python tool to control Neewer '
                                                 'RGB Lights over Bluetooth')
    parser.add_argument('-a', '--udp_listen_addr',
                        default='0.0.0.0',
                        dest='udp_listen_addr',
                        help='Address to use for the UDP server. '
                             'Default: 0.0.0.0')
    parser.add_argument('-p', '--udp_listen_port',
                        default='1664',
                        dest='udp_listen_port',
                        type=int,
                        help='Port to use for the UDP server '
                             'Default: 1664')
    parser.add_argument('-l', '--list_commands',
                        dest='list_commands',
                        help='List available commands',
                        action='store_true')
    parser.add_argument('-c', '--command',
                        default='serve',
                        dest='command',
                        help='Command to execute. '
                             'Available commands: scan, serve (default: serve)')
    parser.add_argument('-m', '--mac_address',
                        dest='mac_address',
                        required=True,
                        help='Device mac address. Must be set.')
    return parser.parse_args()


def main():
    """
    Connect to a Neewer RGB Light, listen to UDP messages
    """
    logging.basicConfig(
        format='%(levelname)s:%(message)s', level=logging.DEBUG
    )

    params = get_params()
    nee = NeewerServer(params.mac_address,
                       params.udp_listen_addr,
                       params.udp_listen_port)
    nee.neewerConnect()

    if params.command == "scan":
        nee.neewerScan()
    elif params.command == "serve":
        nee.startUDPServer()
    else:
        logging.error("Invalid argument")


if __name__ == '__main__':
    sys.exit(main())
