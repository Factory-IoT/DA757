#Ver 0.0.0　差分ADCトライ

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_bme280 import basic
import adafruit_ssd1306
import datetime
import time
import pymysql.cursors

timesecond = 1 #測定間隔(sec)

#i2c setting
i2c = busio.I2C(board.SCL,board.SDA)

#bme280 instance
try:
    bme280 = basic.Adafruit_BME280_I2C(board.I2C(),address =0x76)
except:
    print("BME280 not found")

#display インスタンス
try:
    display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
    display.fill(0)
    display.text("initializing....",0,0,1)
    display.show()
except:
    print("display not found")

#ADS1115 instance differencial
ADS0 = ADS.ADS1115(i2c,gain = 1,address = 0x48)
Diff1 = AnalogIn(ADS0, ADS.P0, ADS.P1)
Single1 = AnalogIn(ADS0,ADS.P2)

#DB init
connection  = pymysql.connect(
    user    = "root",
    passwd  = "minoru0869553434",
    host    = "127.0.0.1",
    db      = "DA757",
    charset = "utf8mb4",
    )

class DB:
    def __init__(self):
        print("DB init")
        
    def WriteParison(self):
        print("WriteParison")
        cur = connection.cursor()
        cur.execute("INSERT INTO Parison (Time,Paricon,Injection) VALUES(%s,%s,%s)",
            (Encoder.TimeStamp,Encoder.Paricon,Encoder.Injection))
        connection.commit()



class Encoder:
    def __init__(self):
        self.TimeStamp = datetime.datetime.now()
        self.PariconRaw = Diff1.voltage
        self.InjectionRaw = Single1.voltage
        self.Paricon = round(self.PariconRaw * 1.0 + 0.0)
        self.Injection = round(self.InjectionRaw * 1.0 - 1.0)

    def Read(self):
        try:
            self.TimeStamp    = datetime.datetime.now()
            self.PariconRaw   = Diff1.voltage
            self.InjectionRaw = Single1.voltage
            self.Paricon   = round(self.PariconRaw * 1.0 + 0.0)
            self.Injection = round(self.InjectionRaw * 1.0 - 1.0)

        except:
            self.Paricon   = ""
            self.Injection = ""

Encoder = Encoder()
DB = DB()

def printData():
    print("=======================================")
    print("TimeStamp     : %s" % Encoder.TimeStamp)
    print("Paricon Raw   : %0.3f" % Encoder.PariconRaw)
    print("Injection Raw : %0.3f" % Encoder.InjectionRaw)
    print("Paricon       : %0.2f" % Encoder.Paricon)
    print("Injection     : %0.2f" % Encoder.InjectionRaw)

lastMesure = 0
lastSecond = 0

while True:
    if (datetime.datetime.now().second % timesecond == 0) & (datetime.datetime.now().second != lastSecond):
        lastSecond = datetime.datetime.now().second
#        print(datetime.datetime.now().second)
#        print(datetime.datetime.now())
        Encoder.Read()
        printData()
        DB.WriteParison()
    
    time.sleep(0.01)

