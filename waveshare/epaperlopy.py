from machine import UART
from machine import Pin
import time
import struct


class Command(object):
    '''
    Commands used by the e ink display have a certain format that easily lends
    itself to objectification, so this is the base class for those commands.

    Child classes should only need to call the constructor of this class and
    provide the new command and data content.
    '''

    FRAME_HEADER = b'\xa5'
    FRAME_FOOTER = b'\xcc\x33\xc3\x3c'
    HEADER_LENGTH = 1
    COMMAND_LENGTH = 1
    LENGTH_LENGTH = 2
    FOOTER_LENGTH = 4
    CHECK_LENGTH = 1
    COMMAND = b'\x00'
    RESPONSE_BYTES = 0

    def __init__(self, command=None, data=None):
        self.command = command or self.COMMAND
        self.bytes = data or []

    def calculate_length(self):
        '''
        Calculate the total length of the packet and returns it as a number
        (*NOT* formatted like the packet requires!).
        '''
        return (Command.HEADER_LENGTH + Command.LENGTH_LENGTH +
                Command.COMMAND_LENGTH + len(self.bytes) +
                Command.FOOTER_LENGTH + Command.CHECK_LENGTH)

    def calculate_checksum(self, data):
        '''
        Creates a checksum by xor-ing every byte of (byte string) data.
        '''
        checksum = 0
        for byte in data:
            checksum = checksum ^ byte
        return checksum.to_bytes(1, 'big')

    def convert_bytes(self):
        '''
        Conver the internal bytes into a string, not the human readable sort,
        but the sort to be used by the protocol.
        '''
        return (b''.join(self.bytes) if isinstance(self.bytes, list) else
                self.bytes)

    def _encode_packet(self):
        '''
        Encodes and returns the entire packet in a format that is suitable for
        transmitting over the serial connection.
        '''
        return (Command.FRAME_HEADER +
                struct.pack('>H', self.calculate_length()) + self.command +
                self.convert_bytes() + Command.FRAME_FOOTER)

    def encode(self):
        '''
        Encodes the packet and attaches the checksum.
        '''
        packet = self._encode_packet()
        #print(packet)
        return packet + self.calculate_checksum(packet)

    def __repr__(self):
        '''
        Returns a human readable string of hex digits corresponding to the
        encoded full packet content.
        '''
        return u' '.join([u'%02x' % ord(b) for b in self.encode()])


###############################################################################
# Configuration commands
###############################################################################


class Handshake(Command):
    '''
    Handshake or Null command.

    From the wiki:

    > Handshake command. If the module is ready, it will return an "OK".

    '''
    RESPONSE_BYTES = 0

class SetBaudrate(Command):
    '''
    From the wiki:

    Set the serial Baud rate.

    After powered[sic] up, the default Baud rate is 115200. This command is
    used to set the Baud rate. You may need to wait 100ms for the module to
    return the result after sending this command, since the host may take a
    period of time to change its Baud rate.
    '''
    COMMAND = b'\x01'
    RESPONSE_BYTES = 2

    def __init__(self, baud):
        super().__init__(SetBaudrate.COMMAND, struct.pack('>L', baud))


class ReadBaudrate(Command):
    '''
    From the wiki:

    Return the current Baud rate value in ASCII format.

    '''
    COMMAND = b'\x02'
    RESPONSE_BYTES = 6


class ReadStorageMode(Command):
    '''
    From the wiki:
    Return the information about the currently used storage area.

    0: NandFlash

    1: MicroSD
    '''
    COMMAND = b'\x06'


class SetStorageMode(Command):
    '''
    From the wiki:

    Set the storage area to select the storage locations of font library and
    images, either the external TF card or the internal NandFlash is available.
    '''
    COMMAND = b'\x07'
    NAND_MODE = b'\x00'
    TF_MODE = b'\x01'

    def __init__(self, target=NAND_MODE):
        super().__init__(SetStorageMode.COMMAND, data=[target])


class SleepMode(Command):
    '''
    GPIO must be used to wake it back up.

    From the wiki:
    The system will enter the sleep mode and reduce system power consumption by
    this command. Under sleep mode, the state indicator is off, and the system
    does not respond any commands. Only the rising edge on the pin WAKE_UP can
    wake up the system.
    '''
    COMMAND = b'\x08'


class RefreshAndUpdate(Command):
    '''
    From the wiki:
    Refresh and update the display at once.
    '''
    COMMAND = b'\x0a'
    RESPONSE_BYTES = 2


class CurrentDisplayRotation(Command):
    '''
    From the wiki:
    Return the current display direction

    0: Normal

    1 or 2: 180° rotation (depending on Firmware)
    '''
    COMMAND = b'\x0c'


class SetCurrentDisplayRotation(Command):
    '''
    From the wiki:
    Set the display direction, only 180° rotation display supported.

    0x00: Normal

    0x01 or 0x02: 180° rotation (depending on Firmware)
    '''
    COMMAND = b'\x0d'
    RESPONSE_BYTES = 2

    NORMAL = b'\x00'
    FLIP = b'\x01'
    FLIPB = b'\x02' # depending on firmware, value could be this...
    def __init__(self, rotation=NORMAL):
        super().__init__( SetCurrentDisplayRotation.COMMAND, rotation)


class ImportFontLibrary(Command):
    '''
    From the wiki:
    Import font library: 48MB

    Import the font library files from the TF card to the internal NandFlash.
    The font library files include GBK32.FON/GBK48.FON/GBK64.FON. The state
    indicator will flicker 3 times when the importation is start and ending.
    '''
    COMMAND = b'\x0e'


class ImportImage(Command):
    '''
    From the wiki:
    Import image: 80MB
    '''
    COMMAND = b'\x0f'
    def __init__(self):
        super().__init__(ImportImage.COMMAND)


class SetPallet(Command):
    '''
    From the wiki:
    Set the foreground color and the background color on drawing, in which the
    foreground color can be used to display the basic drawings and text, while
    the background color is used to clear the screen.
    '''
    COMMAND = b'\x10'
    RESPONSE_BYTES = 2

    BLACK = b'\x00'
    DARK_GRAY = b'\x01'
    LIGHT_GRAY = b'\x02'
    WHITE = b'\x03'
    def __init__(self, fg=BLACK, bg=WHITE):
        fg = fg or SetPallet.BLACK
        bg = bg or SetPallet.WHITE
        super().__init__(SetPallet.COMMAND, [fg, bg])


class GetPallet(Command):
    '''
    From the wiki:
    For example, when returns "03", "0" means the foreground color is Black and
    "3" means the background color is White.
    '''
    COMMAND = b'\x11'


class SetFontSize(Command):
    '''
    Common parent for font size setting commands.
    '''
    THIRTYTWO = b'\x01'
    FOURTYEIGHT = b'\x02'
    SIXTYFOUR = b'\x03'
    RESPONSE_BYTES = 2
    def __init__(self, command, size=THIRTYTWO):
        super().__init__(command, [size])


class SetEnFontSize(SetFontSize):
    '''
    From the wiki:
    Set the English font size (0x1E or 0x1F, may differ depending on version).
    '''
    COMMAND = b'\x1e'
    RESPONSE_BYTES = 2
    def __init__(self, size=SetFontSize.THIRTYTWO):
        super().__init__(SetEnFontSize.COMMAND, size)


class SetZhFontSize(SetFontSize):
    '''
    From the wiki:
    Set the Chinese font size (0x1F).
    '''
    COMMAND = b'\x1f'
    RESPONSE_BYTES = 2
    def __init__(self, size=SetEnFontSize.THIRTYTWO):
        super().__init__(SetZhFontSize.COMMAND, size)


###############################################################################
# Draw a pre-configured thing
###############################################################################

class DisplayText(Command):
    '''
    Any text to display needs to be GB2312 encoded.  For example:

        DisplayText(10, 10, u'你好World'.encode('gb2312'))

    From the wiki:
    Display a character string on a specified coordination position. Chinese
    and English mixed display is supported.
    '''
    COMMAND = b'\x30'
    RESPONSE_BYTES = 2
    def __init__(self, x, y, text):
        super().__init__(self.COMMAND,
                         struct.pack(">HH", x, y) + text + b'\x00')

class DisplayImage(DisplayText):
    '''
    From the wiki:
    Before executing this command, please make sure the bitmap file you want to
    display is stored in the storage area (either TF card or internal
    NandFlash).

    Example: A5 00 16 70 00 00 00 00 50 49 43 37 2E 42 4D 50 00 CC 33 C3 3C DF

    Descriptions: Image start coordination position: (0x00, 0x00)

    0x50 49 43 37 2E 42 4D 50: Bitmap name: PIC7.BMP

    Each character string should be end with a "0". So, you should add a "00"
    at the end of the string 50 49 43 37 2E 42 4D 50.

    The name of the bitmap file should be in uppercase English character(s).
    And the string length of the bitmap name should be less than 11 characters,
    in which the ending "0" is included. For example, PIC7.BMP and PIC789.BMP
    are correct bitmap names, while PIC7890.BMP is a wrong bitmap namem.
    '''
    COMMAND = b'\x70'
    RESPONSE_BYTES = 2


###############################################################################
# Draw shapes
###############################################################################


class DrawCircle(Command):
    '''
    From the wiki:
    Draw a circle based on the given center coordination and radius.
    '''
    COMMAND = b'\x26'
    RESPONSE_BYTES = 2
    def __init__(self, x, y, radius):
        super().__init__(self.COMMAND, struct.pack(">HHH", x, y, radius))


class FillCircle(DrawCircle):
    '''
    From the wiki:
    Fill a circle based on the given center coordination and radius.
    '''
    COMMAND = b'\x27'
    RESPONSE_BYTES = 2


class DrawTriangle(Command):
    '''
    From the wiki:
    Draw a tri-angle according to three given point coordinates.
    '''
    COMMAND = b'\x28'
    RESPONSE_BYTES = 2
    def __init__(self, x1, y1, x2, y2, x3, y3):
        super().__init__(self.COMMAND, struct.pack(">HHHHHH", x1, y1, x2, y2,
                                                   x3, y3))


class FillTriangle(DrawTriangle):
    '''
    From the wiki:
    Fill a tri-angle according to three given point coordinates.
    '''
    COMMAND = b'\x29'
    RESPONSE_BYTES = 2


class DrawRectangle(Command):
    '''
    From the wiki:
    Draw a rectangle according to two point coordinates with foreground color,
    in which these two points serve as the diagonal points of the rectangle.
    '''
    COMMAND = b'\x25'
    RESPONSE_BYTES = 2
    def __init__(self, x1, y1, x2, y2):
        super().__init__(self.COMMAND, struct.pack(">HHHH", x1, y1, x2, y2))


class FillRectangle(DrawRectangle):
    '''
    From the wiki:
    Draw a rectangle according to two point coordinates with foreground color,
    in which these two points serve as the diagonal points of the rectangle.
    '''
    COMMAND = b'\x24'
    RESPONSE_BYTES = 2


class ClearScreen(Command):
    '''
    From the wiki:
    Clear the screen with the background color.
    '''
    COMMAND = b'\x2e'
    RESPONSE_BYTES = 2



# Epaper Objekt, hier mit UART statt mit Serial Schnittstelle
ResetPin = Pin('P22', mode=Pin.OUT)
WakeUpPin = Pin('P23', mode=Pin.OUT)
uart = UART(1, 115200)
RESPONSE_READ_THRESHOLD = 600
class EPaper(object):
    def __init__(self):
        self.uart = uart
        uart.init(115200, bits=8, pins=('P20', 'P21', 'P22', 'P23'))
        self.bytes_expected = 0
    def __enter__(self):
        return self
    def __exit__(self ,type, value, traceback):
        print('exit')
    def reset(self):
        ResetPin.value(1)
        ResetPin.value(0)
    def wake(self):
        WakeUpPin.value(1)
        WakeUpPin.value(0)
    def update(self):
        self.uart.write(RefreshAndUpdate().encode())
    def send(self, command):
        self.bytes_expected += command.RESPONSE_BYTES
        self.uart.write(command.encode())
        self.uart.write(command.convert_bytes())
        #print(command.convert_bytes())
        if self.bytes_expected >= RESPONSE_READ_THRESHOLD:
            self.read_responses()
    def read(self, size=100, timeout=5):
        start_time = time.time()
        self.uart.wait_tx_done(timeout)
        b = self.uart.read(size)
        return b
    def read_responses(self, timeout=3):
        if self.bytes_expected == 0:
            print('no response expected')
            return
        start_time = time.time()
        b = self.read(size=self.bytes_expected, timeout=timeout)
        #self.bytes_expected -= len(b)
