from network import LoRa
import socket
import time
import ubinascii
import datetime

from waveshare.epaperlopy import EPaper
from waveshare.epaperlopy import Handshake
from waveshare.epaperlopy import RefreshAndUpdate
from waveshare.epaperlopy import SetPallet
from waveshare.epaperlopy import FillRectangle
from waveshare.epaperlopy import DisplayText
from waveshare.epaperlopy import SetCurrentDisplayRotation
from waveshare.epaperlopy import SetEnFontSize
import time

lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868, device_class=LoRa.CLASS_A)

#OTAA Authentifizierung
app_eui = ubinascii.unhexlify('eui hier eintragen')
app_key = ubinascii.unhexlify('key hier eintragen')
authentication=(app_eui, app_key)

lora.join(activation=LoRa.OTAA, auth=authentication, timeout=0)

while not lora.has_joined():
    time.sleep(3)
    print('Noch nicht mit LoRa-Netzwerk verbunden')

print('Mit LoRa-Netzwerk verbunden')

#Grundeinstellungen für die LoRa Kommunikation werden gesetzt
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

#Senden der Aktualisierungsanfrage
s.setblocking(True)
s.send('request')

#Verarbeiten der empfangenen Daten
s.setblocking(False)
data = s.recv(64)
#Hier müssen die empfagenen Daten irgendwie in start, end und subject sortiert werden
start =''
end=''
subject=''

#Darstellen der erhaltenen Daten
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
    for x, y, z in zip(start, end, subject):
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