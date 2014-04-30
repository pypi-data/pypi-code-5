import time
from alarmdecoder import AlarmDecoder
from alarmdecoder.devices import USBDevice

KEYPADS_TO_WATCH = [18, 19]

def main():
    """
    Example application that prints messages from the panel to the terminal.
    """
    try:
        # Retrieve the first USB device
        device = AlarmDecoder(USBDevice.find())

        # Set up an event handler and open the device
        device.on_message += handle_message
        with device.open():
            while True:
                time.sleep(1)

    except Exception, ex:
        print 'Exception:', ex

def handle_message(sender, message):
    """
    Handles message events from the AlarmDecoder.
    """
    mask = 0
    for kp in KEYPADS_TO_WATCH:
        mask += 0x10000000 >> kp

    print '{0:0<8x}'.format(message.mask)
    print 'kp mask {0:0<8x}'.format(mask)
    if message.mask & mask:
        print 'matched {0:0<8x}'.format(message.mask & mask)

    print sender, message.raw

if __name__ == '__main__':
    main()
