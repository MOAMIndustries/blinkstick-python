from blinkstick import blinkstick
import logging
import queue
from enum import Enum
import threading
import time
import re
from math import log

'''
### States
AUDITING            blocks Green
READING w valid     Spin Green
READING w fault     Spin Organge    
FINISHED w fault    Pulse Organge
FINISHED            Pulse Green (whilst rewinding)
Drive idle          Solid yellow

DRIVE Identify      Flash White
DRIVE failure       Solid Red
'''

class mode(Enum):
    OFF = 0
    ON = 10
    FLASH = 20
    PULSE = 30
    SPIN = 40
    STACK = 50

class pattern():
    rColor = r'^#(?:[0-9a-fA-F]{2}){3}$'
    def __init__(self, mode = mode.OFF, frequency = 5.0, intensity = 100, cycles = 0, color = "#000000"):
        self.Color = color
        self.Mode = mode
        self.Frequency = frequency
        self.Intensity = intensity

        self.Cycles = cycles


    def period(self):
        if self.Frequency == 0:
            return 0
        else:
            return 1/self.Frequency
    
    def checkConfig(self):
        if not isinstance(self.Color, str):
            raise ValueError("Color should be a string object")
        if not re.match(self.rColor,self.Color):
            raise ValueError("Color should be a string in the format #xxxxxx where x is a hexadecimal number 0-f")
        if not isinstance(self.Mode, mode):
            raise ValueError("Mode should be an instance of the mode class")
        if not (isinstance(self.Frequency, float) or isinstance(self.Frequency, int)):
            raise ValueError("Frequency should be a number")
        if self.Frequency < 0:
            raise ValueError("Frequency should be a positive number")
        if self.Intensity < 0 or self.Intensity > 100:
            raise ValueError("Intensity should be a number between 1 and 100")

    
    def logIntensity(self):
        ''' returns an int between 1 and 255 based on the intensity from 0 to 100
        '''
        return int(255 * log(self.Intensity,100))


class indicator(threading.Thread):
    _logger = logging.getLogger(__name__)
    _fadeSteps = 16
    _cnt = 4
    _gamma = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 10, 11, 11, 11, 12, 12, 13, 13, 14, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18, 19, 19, 20, 21, 21, 22, 22, 23, 23, 24, 25, 25, 26, 27, 27, 28, 29, 29, 30, 31, 31, 32, 33, 33, 34, 35, 36, 36, 37, 38, 39, 40, 40, 41, 42, 43, 44, 45, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 74, 75, 76, 77, 78, 79, 81, 82, 83, 84, 86, 87, 88, 89,91, 92, 93, 95, 96, 97, 99, 100, 101, 103, 104, 105, 107, 108, 110, 111, 113, 114, 115, 117, 118, 120, 121, 123, 125, 126, 128, 129, 131, 132, 134, 136, 137, 139, 140, 142, 144, 145, 147, 149, 151, 152, 154, 156, 158, 159, 161, 163, 165, 166, 168, 170, 172, 174, 176, 178, 179, 181, 183, 185, 187, 189, 191, 193, 195, 197, 199, 201, 203, 205, 207, 209, 211, 213, 215, 217, 220, 222, 224, 226, 228,230, 232, 235, 237, 239, 241, 244, 246, 248, 250, 253, 255, 255]
    
    def __init__(self, control, ledCount=4):
        threading.Thread.__init__(self)

        self.stick = blinkstick.find_first()
        self.stick.set_mode = 2
        self.stick.set_led_count(ledCount)
        self.stick.set_max_rgb_value(255) # Handle intensity in this library

        self.Stop = False
        self.Queue = control
        
        self.Pattern = None
        self.modeOff()

        self._data = []

    def run(self):
        self._logger.info("Starting")
        while True:
            self.checkQueue()
            if self.Pattern is not None:
                if self.Pattern.Mode == mode.FLASH:
                    self.modeFlash()
                elif self.Pattern.Mode == mode.OFF:
                    self.modeOff()
                elif self.Pattern.Mode == mode.SPIN:
                    self.modeSpin()
                elif self.Pattern.Mode == mode.PULSE:
                    self.modePulse()
                elif self.Pattern.Mode == mode.ON:
                    self.modeOn()

    
    def modeOff(self):
        self.Stop = False
        data = [0] * (3 * self._cnt)
        self.stick.set_led_data(0,data)
        return

    def modeOn(self):
        self.Stop = False
        self.stick.turn_off()

        red, green, blue = self.stick._determine_rgb(hex=self.Pattern.Color)
        r = self._gamma[red]
        g = self._gamma[green]
        b = self._gamma[blue]

        data = []
        for p in range(0,self._cnt):
            data.append(g)  # For some reason data order in array is GRB 
            data.append(r)
            data.append(b)

        self.stick.set_led_data(0,data)
        while not self.Stop:
            if self.checkQueue(True, self.Pattern.period()):   # use this instead of sleep so that pattern changes are not missed by blocking time.sleep()
                break
     

    def modeFlash(self):
        self._logger.info("FLASHER")
        self.Stop = False
        self.stick.turn_off()

        red, green, blue = self.stick._determine_rgb(hex=self.Pattern.Color)

        r = self._gamma[red]
        g = self._gamma[green]
        b = self._gamma[blue]

        data = []
        for p in range(0,self._cnt):
            data.append(g)  # For some reason data order in array is GRB 
            data.append(r)
            data.append(b)


        while not self.Stop:
            self.stick.set_led_data(0,data)
            if self.checkQueue(True, self.Pattern.period()):   # use this instead of sleep so that pattern changes are not missed by blocking time.sleep()
                break
            self.modeOff()
            if self.checkQueue(True, self.Pattern.period()):   # use this instead of sleep so that pattern changes are not missed by blocking time.sleep()
                break

    def modeSpin(self):
        self._logger.info("SPIN SPIn SUGAR")
        self.Stop = False
        self.stick.turn_off()

        red, green, blue = self.stick._determine_rgb(hex=self.Pattern.Color)

        r = red
        g = green
        b = blue

        data = []
        for i in range(1,self._cnt):
            print(self._gamma[int((g*(self._cnt-i)/self._cnt))])
            data.append(self._gamma[int((g*(self._cnt-i)/self._cnt))])
            data.append(self._gamma[int((r*(self._cnt-i)/self._cnt))])
            data.append(self._gamma[int((b*(self._cnt-i)/self._cnt))])
        data.append(0)
        data.append(0)
        data.append(0)

        while not self.Stop:
            self.stick.set_led_data(0,data)
            if self.checkQueue(True, self.Pattern.period()):   # use this instead of sleep so that pattern changes are not missed by blocking time.sleep()
                break
            data = data[3:] + data[0:3]
            
    def modePulse(self):
        self._logger.info("PULSE")
        self.Stop = False
        self.stick.turn_off()

        red, green, blue = self.stick._determine_rgb(hex=self.Pattern.Color)
        self._logger.info(f"r: {red}, g: {green}, b: {blue}")
        while not self.Stop:
            for i in range(0,self._fadeSteps*2):
                if i <self._fadeSteps:
                    r = self._gamma[int((red * i)/self._fadeSteps)]
                    g = self._gamma[int((green * i)/self._fadeSteps)]
                    b = self._gamma[int((blue * i)/self._fadeSteps)]
                else:
                    r = self._gamma[int(red-(red * i)/(self._fadeSteps*2))]
                    g = self._gamma[int(green-(green * i)/(self._fadeSteps*2))]
                    b = self._gamma[int(blue-(blue * i)/(self._fadeSteps*2))]
                data = []
                for j in range(0,self._cnt):
                    data.append(g)
                    data.append(r)
                    data.append(b)
                self.stick.set_led_data(0,data)
                if self.checkQueue(True, self.Pattern.period()/self._fadeSteps):   # use this instead of sleep so that pattern changes are not missed by blocking time.sleep()
                    break
            




    def checkQueue(self, blk = False, tmt = 0):
        try:
            command = self.Queue.get(block=blk, timeout=tmt)

            self._logger.info(f"Received command {command}")
            if isinstance(command, pattern):
                self._logger.debug("queue object stop set")
                self.Stop = True
                self.Pattern = command
                return True
        except queue.Empty:
            pass
        return False

    def _intensity(self, col):
        '''returns integer of the color value based on the intensity percentage
        '''
        return int(col * log(self.Pattern.Intensity,100))

if __name__ == "__main__":
    print("starting")
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    logger.info("start")

    control = queue.Queue()
    bs = indicator(control)
    bs.start()

    # Valid Read
    control.put(pattern(mode = mode.SPIN, frequency= 12, color="#00dd00"))
    time.sleep(5)
    #Read with error
    control.put(pattern(mode = mode.SPIN, frequency= 11, color="#ff9900"))
    time.sleep(5)
    # Rewind success
    control.put(pattern(mode = mode.PULSE, frequency= 8, color="#00bb00"))
    time.sleep(5)
    # Rewind Fault
    control.put(pattern(mode = mode.PULSE, frequency= 8, color="#bb6600"))
    time.sleep(5)
    # Drive IDle
    control.put(pattern(mode = mode.ON, frequency= 1, color="#ffff00"))
    time.sleep(0)
    control.put(pattern(mode = mode.FLASH, frequency= 5, color="#004400"))
    time.sleep(0)

