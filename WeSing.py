import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import os
import random
import wave
from pitchshifter import main as pitch_shifting_main
import pygame
from multiprocessing import Process


import time
from neopixel import *
import argparse

# LED strip configuration:
LED_COUNT = 30  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Init Pygame to play different soundbits
#pygame.mixer.pre_init(22050, -16, 10, 1024)
#pygame.init()
#pygame.mixer.quit()
pygame.mixer.init(22050, -16, 10, 1024)

# Buttons initialization
buttonRecord = 16

# Potentiometer Initialization
CLK = 6
MISO = 13
MOSI = 19
CS = 26
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# General Pin initialization
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(buttonRecord, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# status booleans
can_record = True
started_playing = False
random_effect = True
can_pitch_shift = False
pitch_shift_parameters = [-3, -2, -1, 0, 2, 4, 6]
# Loading the currently recorded file and the soundbit
RECORDING_FILE_NAME = "Audio/recording.wav"
PITCH_SHIFTED_FILE_NAME = "Audio/recording_p0.wav"

RECORDING_DURATION = 10

def pitchToColor(strip, pitch):
    """light the entire strip in a color that matches the pitch"""
    current_color = strip.getPixelColor(0)
    color = wheel((int(pitch * 256 / 7)) & 255)
    if color != current_color:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
            strip.show()

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def fastColorWipe(strip,color):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()


def colorWipe(strip, color, duration, LED_COUNT):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep((float(duration) / float(LED_COUNT)))

def theaterChase(strip, color):
    """Movie theater light style chaser animation."""
    while True:
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(1)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

print("starting main loop... red is record, green is main track, black is effect")


while True:
    if GPIO.input(buttonRecord) == GPIO.HIGH and can_record:
        # recording phase
        time.sleep(0.3)
        can_record = False
        # turn off recording led
        print("recording a {} sec song".format(RECORDING_DURATION))
        # turn on recording proccess leds colorWipe in a thread
        t_record_light=Process(target=colorWipe, args=(strip, Color(255, 0, 0), RECORDING_DURATION, LED_COUNT))
        t_record_light.start()
        # play the music and record
	# os.system("aplay -d {} Audio/PLAYBACK_HARPATKAOT.wav &".format(RECORDING_DURATION))
	pygame.mixer.Channel(7).play(pygame.mixer.Sound('Audio/zahav.wav'))
	pygame.mixer.Channel(7).set_volume(0.1)
	os.system("arecord -d {} --format S16_LE --rate 22050 -c1 {}".format(
            RECORDING_DURATION, RECORDING_FILE_NAME))
	print("finished recording")
	pygame.mixer.Channel(7).set_volume(0.0)
        # pitch shifting phase
        print("start file procesing")
        t1=Process(target=pitch_shifting_main, args=(RECORDING_FILE_NAME,
                                    PITCH_SHIFTED_FILE_NAME.replace('0', str(6)), float(8),
                                    1, 4096, 0.9, False, False))
        t2=Process(target=pitch_shifting_main, args=(RECORDING_FILE_NAME,
                                    PITCH_SHIFTED_FILE_NAME.replace('0', str(4)), float(5),
                                    1, 4096, 0.9, False, False))
        t3=Process(target=pitch_shifting_main, args=(RECORDING_FILE_NAME,
                                    PITCH_SHIFTED_FILE_NAME.replace('0', str(2)), float(3),
                                    1, 4096, 0.9, False, False))
        t4=Process(target=pitch_shifting_main, args=(RECORDING_FILE_NAME,
                                    PITCH_SHIFTED_FILE_NAME.replace('0', str(-1)), float(-1),
                                    1, 4096, 0.9, False, False))
        t5=Process(target=pitch_shifting_main, args=(RECORDING_FILE_NAME,
                                    PITCH_SHIFTED_FILE_NAME.replace('0', str(-2)), float(-2),
                                    1, 4096, 0.9, False, False))
        t6=Process(target=pitch_shifting_main, args=(RECORDING_FILE_NAME,
                                    PITCH_SHIFTED_FILE_NAME.replace('0', str(-3)), float(-3),
                                    1, 4096, 0.9, False, False))

        t_proccesing_light=Process(target=theaterChase, args=(strip, Color(0, 0, 127)))
        t_proccesing_light.start()
        start = time.time()
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()
        t6.start()
        print("started threads")
        t1.join()
        t2.join()
        t3.join()
        t4.join()
        t5.join()
        t6.join()

        end = time.time()
        print(end - start)
        print("finished running threads")
        t_proccesing_light.terminate()
        # play with effects phase, switch this to pygame and potentsiometer
        if GPIO.input(buttonRecord) == GPIO.HIGH and can_record:
        # recording phase
        time.sleep(0.3)
        can_record = False

            print("playing recording")
            start_playing_timestamp = time.time()
            started_playing = True
            pygame.mixer.Channel(0).play(pygame.mixer.Sound('Audio/recording_p-3.wav'))
            pygame.mixer.Channel(1).play(pygame.mixer.Sound('Audio/recording_p-2.wav'))
            pygame.mixer.Channel(2).play(pygame.mixer.Sound('Audio/recording_p-1.wav'))
            pygame.mixer.Channel(3).play(pygame.mixer.Sound('Audio/recording.wav'))
            pygame.mixer.Channel(4).play(pygame.mixer.Sound('Audio/recording_p2.wav'))
            pygame.mixer.Channel(5).play(pygame.mixer.Sound('Audio/recording_p4.wav'))
            pygame.mixer.Channel(6).play(pygame.mixer.Sound('Audio/recording_p6.wav'))

            #     if started_playing and time() - start_playing_timestamp > RECORDING_DURATION:
            while started_playing and time.time() - start_playing_timestamp < RECORDING_DURATION:
                if mcp.read_adc(0) <= 146:
                    pygame.mixer.Channel(0).set_volume(1.0)
                    pygame.mixer.Channel(1).set_volume(0)
                    pygame.mixer.Channel(2).set_volume(0)
                    pygame.mixer.Channel(3).set_volume(0)
                    pygame.mixer.Channel(4).set_volume(0)
                    pygame.mixer.Channel(5).set_volume(0)
                    pygame.mixer.Channel(6).set_volume(0)
                    pitchToColor(strip, 0)

                elif mcp.read_adc(0) <= 292:
                    pygame.mixer.Channel(0).set_volume(0)
                    pygame.mixer.Channel(1).set_volume(1.0)
                    pygame.mixer.Channel(2).set_volume(0)
                    pygame.mixer.Channel(3).set_volume(0)
                    pygame.mixer.Channel(4).set_volume(0)
                    pygame.mixer.Channel(5).set_volume(0)
                    pygame.mixer.Channel(6).set_volume(0)
                    pitchToColor(strip, 1)

                elif mcp.read_adc(0) <= 438:
                    pygame.mixer.Channel(0).set_volume(0)
                    pygame.mixer.Channel(1).set_volume(0)
                    pygame.mixer.Channel(2).set_volume(1.0)
                    pygame.mixer.Channel(3).set_volume(0)
                    pygame.mixer.Channel(4).set_volume(0)
                    pygame.mixer.Channel(5).set_volume(0)
                    pygame.mixer.Channel(6).set_volume(0)
                    pitchToColor(strip, 2)

                elif mcp.read_adc(0) <= 584:
                    pygame.mixer.Channel(0).set_volume(0)
                    pygame.mixer.Channel(1).set_volume(0)
                    pygame.mixer.Channel(2).set_volume(0)
                    pygame.mixer.Channel(3).set_volume(1.0)
                    pygame.mixer.Channel(4).set_volume(0)
                    pygame.mixer.Channel(5).set_volume(0)
                    pygame.mixer.Channel(6).set_volume(0)
                    pitchToColor(strip, 3)

                elif mcp.read_adc(0) <= 730:
                    pygame.mixer.Channel(0).set_volume(0)
                    pygame.mixer.Channel(1).set_volume(0)
                    pygame.mixer.Channel(2).set_volume(0)
                    pygame.mixer.Channel(3).set_volume(0)
                    pygame.mixer.Channel(4).set_volume(1.0)
                    pygame.mixer.Channel(5).set_volume(0)
                    pygame.mixer.Channel(6).set_volume(0)
                    pitchToColor(strip, 4)

                elif mcp.read_adc(0) <= 876:
                    pygame.mixer.Channel(0).set_volume(0)
                    pygame.mixer.Channel(1).set_volume(0)
                    pygame.mixer.Channel(2).set_volume(0)
                    pygame.mixer.Channel(3).set_volume(0)
                    pygame.mixer.Channel(4).set_volume(0)
                    pygame.mixer.Channel(5).set_volume(1.0)
                    pygame.mixer.Channel(6).set_volume(0)
                    pitchToColor(strip, 5)

                else:
                    pygame.mixer.Channel(0).set_volume(0)
                    pygame.mixer.Channel(1).set_volume(0)
                    pygame.mixer.Channel(2).set_volume(0)
                    pygame.mixer.Channel(3).set_volume(0)
                    pygame.mixer.Channel(4).set_volume(0)
                    pygame.mixer.Channel(5).set_volume(0)
                    pygame.mixer.Channel(6).set_volume(1.0)
                    pitchToColor(strip, 6)


            print("finished playing, can record again")
            started_playing = False
            can_record = True
            fastColorWipe(strip, Color(0, 0, 0))
        else:
            print("recording doesn't exist yet")

