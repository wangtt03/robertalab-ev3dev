
from PIL import Image, ImageFont
import glob
import logging
import math
import os
import threading
import time

import brickpi3

LOG_PATH = '/var/log/robot/roberta.log'

logging.basicConfig(filename = LOG_PATH, level = logging.DEBUG)
logger = logging.getLogger('roberta.ev3')


def clamp(v, mi, ma):
    return mi if v < mi else ma if v > ma else v


class Hal(object):
    # class global, so that the front-end can cleanup on forced termination
    # popen objects
    cmds = []

    # usedSensors is unused, the code-generator for lab.openroberta > 1.4 wont
    # pass it anymore
    def __init__(self, brickConfiguration, usedSensors=None):
        self.cfg = brickConfiguration
        dir = os.path.dirname(__file__)

        # logger.info('char size: %d x %d -> num-chars: %f x %f',
        #     self.font_w, self.font_h, 178 / self.font_w, 128 / self.font_h)
        self.timers = {}

        self.BP = brickpi3.BrickPi3()

        self.portMapping = {
            'A': self.BP.PORT_A,
            'B': self.BP.PORT_B,
            'C': self.BP.PORT_C,
            'D': self.BP.PORT_D,
            '1': self.BP.PORT_1,
            '2': self.BP.PORT_2,
            '3': self.BP.PORT_3,
            '4': self.BP.PORT_4,
        }

        BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A)) # reset encoder A
        BP.offset_motor_encoder(BP.PORT_B, BP.get_motor_encoder(BP.PORT_B)) # reset encoder B
        BP.offset_motor_encoder(BP.PORT_C, BP.get_motor_encoder(BP.PORT_C)) # reset encoder C
        BP.offset_motor_encoder(BP.PORT_D, BP.get_motor_encoder(BP.PORT_D)) # reset encoder D

        sensors = self.cfg['sensors']
        for (k, v) in sensors.items():
            BP.set_sensor_type(self.portMapping[k], v)


    # factory methods
    @staticmethod
    def makeLargeMotor(port, regulated, direction, side):
        try:
            m = None
        except (AttributeError, OSError):
            logger.info('no large motor connected to port [%s]', port)
            logger.exception("HW Config error")
            m = None
        return m

    @staticmethod
    def makeMediumMotor(port, regulated, direction, side):
        try:
            m = None
        except (AttributeError, OSError):
            logger.info('no medium motor connected to port [%s]', port)
            logger.exception("HW Config error")
            m = None
        return m

    @staticmethod
    def makeColorSensor(port):
        try:
            s = BrickPi3.SENSOR_TYPE.EV3_COLOR_COLOR
        except (AttributeError, OSError):
            logger.info('no color sensor connected to port [%s]', port)
            s = None
        return s

    @staticmethod
    def makeGyroSensor(port):
        try:
            s = BrickPi3.SENSOR_TYPE.EV3_GYRO_ABS_DPS
        except (AttributeError, OSError):
            logger.info('no gyro sensor connected to port [%s]', port)
            s = None
        return s

    @staticmethod
    def makeI2cSensor(port):
        try:
            s = None
        except (AttributeError, OSError):
            logger.info('no i2c sensor connected to port [%s]', port)
            s = None
        return s

    @staticmethod
    def makeInfraredSensor(port):
        try:
            s = BrickPi3.SENSOR_TYPE.EV3_INFRARED_REMOTE
        except (AttributeError, OSError):
            logger.info('no infrared sensor connected to port [%s]', port)
            s = None
        return s

    @staticmethod
    def makeLightSensor(port):
        try:
            s = None
        except (AttributeError, OSError):
            logger.info('no light sensor connected to port [%s]', port)
            s = None
        return s

    @staticmethod
    def makeSoundSensor(port):
        try:
            s = None
        except (AttributeError, OSError):
            logger.info('no sound sensor connected to port [%s]', port)
            s = None
        return s

    @staticmethod
    def makeTouchSensor(port):
        try:
            s = BrickPi3.SENSOR_TYPE.TOUCH
        except (AttributeError, OSError):
            logger.info('no touch sensor connected to port [%s]', port)
            s = None
        return s

    @staticmethod
    def makeUltrasonicSensor(port):
        try:
            s = BrickPi3.SENSOR_TYPE.EV3_ULTRASONIC_CM
        except (AttributeError, OSError):
            logger.info('no ultrasonic sensor connected to port [%s]', port)
            s = None
        return s

    # state
    def resetState(self):
        self.stopAllMotors()
        logger.debug("terminate %d commands", len(Hal.cmds))
        for cmd in Hal.cmds:
            if cmd:
                logger.debug("terminate command: %s", str(cmd))
                cmd.terminate()
                cmd.wait()  # avoid zombie processes
        Hal.cmds = []

    # control
    def waitFor(self, ms):
        time.sleep(ms / 1000.0)

    def busyWait(self):
        '''Used as interrupptible busy wait.'''
        time.sleep(0.0)

    def waitCmd(self, cmd):
        '''Wait for a command to finish.'''
        Hal.cmds.append(cmd)
        # we're not using cmd.wait() since that is not interruptable
        while cmd.poll() is None:
            self.busyWait()
        Hal.cmds.remove(cmd)

    # actors
    # http://www.ev3dev.org/docs/drivers/tacho-motor-class/

    def rotateRegulatedMotor(self, port, speed_pct, mode, value):
        # mode: degree, rotations, distance
        if mode is 'degree':
            pass
        elif mode is 'rotations':
            pass

    def turnOnRegulatedMotor(self, port, value):
        self.BP.set_motor_dps(self.portMapping[port], value)

    def setRegulatedMotorSpeed(self, port, value):
        self.BP.set_motor_power(self.portMapping[port], value)

    def getRegulatedMotorSpeed(self, port):
        result = self.BP.get_motor_status(self.portMapping[port])
        if result:
            return [1]
        else:
            return 0

    def stopMotor(self, port, mode='float'):
        # mode: float, nonfloat
        # stop_actions: ['brake', 'coast', 'hold']
        self.set_motor_power(self.portMapping[port], self.BP.MOTOR_FLOAT)

    def stopMotors(self, left_port, right_port):
        self.set_motor_power(self.portMapping[left_port] + self.portMapping[right_port], self.BP.MOTOR_FLOAT)

    def stopAllMotors(self):
        # [m for m in [Motor(port) for port in ['outA', 'outB', 'outC', 'outD']] if m.connected]
        self.set_motor_power(self.BP.PORT_A + self.BP.PORT_B + self.BP.PORT_C + self.BP.PORT_D, self.BP.MOTOR_FLOAT)

    # touch sensor
    def isPressed(self, port):
        return self.BP.get_sensor(self.portMapping[port])

    # ultrasonic sensor
    def getUltraSonicSensorDistance(self, port):
        return self.BP.get_sensor(self.portMapping[port])

    def getUltraSonicSensorPresence(self, port):
        return self.BP.get_sensor(self.portMapping[port])

    # gyro
    # http://www.ev3dev.org/docs/sensors/lego-ev3-gyro-sensor/

    def getGyroSensorValue(self, port, mode):
        return self.BP.get_sensor(self.portMapping[port])

    # color
    # http://www.ev3dev.org/docs/sensors/lego-ev3-color-sensor/
    def getColorSensorAmbient(self, port):
        self.BP.set_sensor_type(self.portMapping[port], self.BP.SENSOR_TYPE.EV3_COLOR_AMBIENT)
        value = self.BP.get_sensor(self.portMapping[port])
        return value

    def getColorSensorColour(self, port):
        colors = ['none', 'black', 'blue', 'green', 'yellow', 'red', 'white', 'brown']
        self.BP.set_sensor_type(self.portMapping[port], self.BP.SENSOR_TYPE.EV3_COLOR_COLOR)
        value = self.BP.get_sensor(self.portMapping[port])
        return colors[value]

    def getColorSensorRed(self, port):
        self.BP.set_sensor_type(self.portMapping[port], self.BP.SENSOR_TYPE.EV3_COLOR_REFLECTED)
        value = self.BP.get_sensor(self.portMapping[port])
        return value

    def getColorSensorRgb(self, port):
        self.BP.set_sensor_type(self.portMapping[port], self.BP.SENSOR_TYPE.EV3_COLOR_COMPONENTS)
        value = self.BP.get_sensor(self.portMapping[port])
        return value

    # infrared
    # http://www.ev3dev.org/docs/sensors/lego-ev3-infrared-sensor/
    def getInfraredSensorSeek(self, port):
        self.BP.set_sensor_type(self.portMapping[port], self.BP.SENSOR_TYPE.EV3_INFRARED_REMOTE)
        return self.BP.get_sensor(self.portMapping[port])

    def getInfraredSensorDistance(self, port):
        self.BP.set_sensor_type(self.portMapping[port], self.BP.SENSOR_TYPE.EV3_INFRARED_PROXIMITY)
        return self.BP.get_sensor(self.portMapping[port])

    # timer
    def getTimerValue(self, timer):
        if timer in self.timers:
            return time.clock() - self.timers[timer]
        else:
            self.timers[timer] = time.clock()

    def resetTimer(self, timer):
        del self.timers[timer]

    # tacho-motor position
    def resetMotorTacho(self, actorPort):
        m = self.cfg['actors'][actorPort]
        m.position = 0

    def getMotorTachoValue(self, actorPort, mode):
        m = self.cfg['actors'][actorPort]
        tachoCount = m.position

        if mode == 'degree':
            return tachoCount * 360.0 / float(m.count_per_rot)
        elif mode in ['rotation', 'distance']:
            rotations = float(tachoCount) / float(m.count_per_rot)
            if mode == 'rotation':
                return rotations
            else:
                distance = round(math.pi * self.cfg['wheel-diameter'] * rotations)
                return distance
        else:
            raise ValueError('incorrect MotorTachoMode: %s' % mode)
