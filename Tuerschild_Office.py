# coding=utf-8
#from __future__ import print_function
import datetime
import os.path
from O365 import Account, MSGraphProtocol

CLIENT_ID = 'Add Client ID here'
SECRET_ID =  'Add Secret ID here'

credentials = (CLIENT_ID, SECRET_ID)

from waveshare.epaperlopy import EPaper
from waveshare.epaperlopy import Handshake
from waveshare.epaperlopy import RefreshAndUpdate
from waveshare.epaperlopy import SetPallet
from waveshare.epaperlopy import DrawCircle
from waveshare.epaperlopy import FillCircle
from waveshare.epaperlopy import DrawRectangle
from waveshare.epaperlopy import FillRectangle
from waveshare.epaperlopy import DrawTriangle
from waveshare.epaperlopy import FillTriangle
from waveshare.epaperlopy import DisplayText
from waveshare.epaperlopy import SetCurrentDisplayRotation
from waveshare.epaperlopy import SetEnFontSize
from waveshare.epaperlopy import SetZhFontSize
from waveshare.epaperlopy import ClearScreen
import RPi.GPIO as GPIO
import time

protocol = MSGraphProtocol()

scopes = ['Calendars.Read','Calendars.ReadWrite']
account = Account(credentials, protocol=protocol)

if not account.is_authenticated:
    if account.authenticate(scopes=scopes):
        print('Authenticated!')

if __name__ == '__main__':
    subject= []
    start = []
    end = []
    start1 = ""
    end1 = ""
    startconverted = []
    endconverted = []
        
    schedule = account.schedule()
    calendar = schedule.get_default_calendar()
    q = calendar.new_query('start').greater_equal(datetime.datetime.utcnow())
    q.chain('and').on_attribute('end').less_equal(datetime.datetime(2025, 12, 31))
    events = calendar.get_events(limit=3, query=q, include_recurring=True)
    
    if not events:
        print('No upcoming events found.')
    for event in events:
        subject.append(event.subject)
        start = event.start
        end =event.end        
        start1 = start.strftime('%d.%m.%Y %H:%M')
        end1 = end.strftime('%H:%M')
        startconverted.append(str(start1))
        endconverted.append(str(end1))
        
        print("Subject: ",subject)
        print("Start: ",startconverted)
        print("End: ",endconverted)
        
        
    with EPaper() as paper:
        
        paper.send(Handshake())
        time.sleep(2)
        paper.send(SetPallet(SetPallet.BLACK, SetPallet.WHITE))
        paper.send(SetCurrentDisplayRotation(SetCurrentDisplayRotation.FLIP))
        paper.send(SetEnFontSize(SetEnFontSize.FOURTYEIGHT))
        paper.send(DisplayText(20, 20, "Besprechungsraum CO.12".encode("gb2312")))
        paper.send(SetEnFontSize(SetEnFontSize.THIRTYTWO))
        paper.send(DisplayText(600, 510, "HAW".encode("gb2312")))
        paper.send(DisplayText(600, 540, "HAMBURG".encode("gb2312")))
        
        paper.send(DisplayText(20, 70, "Anstehende Besprechungen:".encode("gb2312")))
        ycoordinate = 150
        for x, y, z in zip(startconverted, endconverted, subject):
                paper.send(DisplayText(20, ycoordinate, x.encode("gb2312")))
                paper.send(DisplayText(245, ycoordinate, "-".encode("gb2312")))
                paper.send(DisplayText(270, ycoordinate, y.encode("gb2312")))
                paper.send(DisplayText(20, (ycoordinate+30), z.encode("gb2312")))
                ycoordinate = ycoordinate + 90

                #HAW Logo wird aus Rechtecken erstellt
        paper.send(FillRectangle(520, 510, 570, 515))
        paper.send(FillRectangle(520, 530, 570, 535))
        paper.send(FillRectangle(520, 550, 570, 555))
        paper.send(FillRectangle(520, 570, 570, 575))
        
        paper.send(SetPallet(SetPallet.LIGHT_GRAY, SetPallet.WHITE))
        
        paper.send(FillRectangle(500, 500, 550, 505))
        paper.send(FillRectangle(500, 520, 550, 525))
        paper.send(FillRectangle(500, 540, 550, 545))
        paper.send(FillRectangle(500, 560, 550, 565))
        
            
        paper.send(RefreshAndUpdate())
        paper.read_responses()        

        
