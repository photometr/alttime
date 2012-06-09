#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 09 17:10:44 2012

@author: Dmitriy Blinov
"""
import ConfigParser
import numpy
from datetime import datetime
import math
import sidereal
import matplotlib.pyplot as plt

class Config():
  def __init__(self):
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')
    self.longitude = config.getfloat('location', 'longitude')
    self.latitude  = config.getfloat('location', 'latitude')
    self.altitude  = config.getfloat('location', 'altitude')
    self.tabobpath = config.get('location', 'tabobpath')
    self.timebins = config.getfloat('misc', 'timebins')

def ReadTabob(conf):
  objects = {}
  fop = open(conf.tabobpath)
  for line in fop.readlines():
    sl = line.split(",")
    RA = sl[1].strip()
    DEC = sl[2].strip()
    objects[sl[0]] = [RA,DEC]
  fop.close()
  return objects

def red_to_pos(hourang):
    #receives hourang in degrees
    #returns reduced to positive in hours
    if hourang < 0:
        hourang = 24 + hourang/15.0
    else:
        hourang = hourang/15.0
    return hourang

def ToSingleValue(strval):
  #accept 'HH MM SS' or 'DD MM SS' 
  #returns float value of degrees or hours
  sl = strval.split()
  single = abs(int(sl[0]))+int(sl[1])/60.0+float(sl[2])/3600
  return math.copysign(single, int(sl[0]))
  
def CalcAlt(conf,eqcoords,timebins):
  Altitudes = []
  hmsSystem = sidereal.MixedUnits((60,60))
  RA, DEC = eqcoords
  RA = ToSingleValue(RA)*15 #RA in degrees
  DEC = ToSingleValue(DEC)
  year = datetime.now().year
  month = datetime.now().month
  day = datetime.now().day
  for time in timebins:
    hour,minute,second = hmsSystem.singleToMix(time)
    curtime = datetime(year,month,day,hour,minute,int(second))
    Gst = sidereal.SiderealTime.fromDatetime(curtime)#FIXME
    Lst = Gst.lst(math.radians(conf.longitude))
    Lst = Lst.hours * 15 #local siderial time - in degrees
    Hourangle = red_to_pos(Lst-RA)
    RADec = sidereal.RADec(math.radians(RA), math.radians(DEC))
    AltAz = RADec.altAz(math.radians(Hourangle*15.0), math.radians(conf.latitude))
    Altitudes.append(math.degrees(AltAz.alt))
  return Altitudes

def GetAlt(conf,objects):
  #timebins = numpy.concatenate((numpy.arange(12,24,conf.timebins),numpy.arange(0,12,conf.timebins)),axis=0)
  timebins = numpy.arange(0.0, 24.0, conf.timebins)
  for obj in objects.keys():
    objects[obj] = CalcAlt(conf,objects[obj],timebins)
  return objects,timebins

def GetMax(x,y):
  ymax = max(y)
  ymaxindex = y.index(ymax)
  xmax = x[ymaxindex]
  return xmax,ymax

def Plot(objects, timebins):
  fig = plt.figure(figsize=(15,12))
  ax = fig.add_subplot(111)
  ax.set_ylabel('Altitude (deg)')
  ax.set_xlabel('UTC')
  ax.set_xlim((0,24))
  ax.set_ylim((0,95))
  for obj in objects.keys():
    alt = objects[obj]
    xmax, ymax = GetMax(timebins,alt)
    plt.text(xmax, ymax+1, obj, ha='center', va='center')
    plt.plot( timebins, alt, 'g')
    
  plt.show()
  return

def main():
  conf = Config()
  objects = ReadTabob(conf)
  objects, timebins = GetAlt(conf,objects)
  Plot(objects, timebins)

if __name__ == '__main__':
  main()
