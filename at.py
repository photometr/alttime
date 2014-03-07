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
import matplotlib.transforms as mtransforms
import ephem

date = '2014-05-01 00:00:00' #UTC
figname = '05.eps'

skinakas = ephem.Observer()
skinakas.lat, skinakas.lon = '24.89', '35.23'
skinakas.date = date
skinakas.horizon = '-12'
end = skinakas.previous_rising(ephem.Sun(), use_center=True).tuple()
start = skinakas.next_setting(ephem.Sun(), use_center=True).tuple()
night_end = end[3]+end[3]/60.+end[3]/3600.
night_start = start[3]+start[3]/60.+start[3]/3600.

class Config():
  def __init__(self):
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')
    self.longitude = config.getfloat('location', 'longitude')
    self.latitude  = config.getfloat('location', 'latitude')
    self.altitude  = config.getfloat('location', 'altitude')
    self.tabobdec  = config.getboolean('location', 'tabobdec')
    self.tabobpath = config.get('location', 'tabobpath')
    self.timebins  = config.getfloat('misc', 'timebins')
    self.curtime   = config.getboolean('misc', 'curtime')

def ReadTabob(conf):
  objects = {}
  fop = open(conf.tabobpath)
  for line in fop.readlines():
    sl = line.split()
    RA = sl[1] + " " + sl[2] + " " + sl[3]
    DEC = sl[4] + " " + sl[5] + " " + sl[6]
    objects[sl[0].lstrip("RBPLJ")] = [RA,DEC]
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
  if conf.tabobdec:
     RA = float(RA)
     DEC = float(DEC)
  else:
     RA = ToSingleValue(RA)*15 #RA in degrees
     DEC = ToSingleValue(DEC)
  calc_date = datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
  year = calc_date.year
  month = calc_date.month
  day = calc_date.day
  for time in timebins:
    hour,minute,second = hmsSystem.singleToMix(time)
    curtime = datetime(year,month,day,hour,minute,int(second))
    Gst = sidereal.SiderealTime.fromDatetime(curtime) #FIXME
    Lst = Gst.lst(math.radians(conf.longitude))
    Lst = Lst.hours * 15 #local siderial time - in degrees
    Hourangle = red_to_pos(Lst-RA)
    RADec = sidereal.RADec(math.radians(RA), math.radians(DEC))
    AltAz = RADec.altAz(math.radians(Hourangle*15.0), math.radians(conf.latitude))
    Altitudes.append(math.degrees(AltAz.alt))
  return Altitudes

def GetAlt(conf,objects):
  timebins = numpy.arange(0.0, 24.0, conf.timebins)
  for obj in objects.keys():
    objects[obj] = CalcAlt(conf,objects[obj],timebins)
  return objects,timebins

def GetMax(x,y):
  ymax = max(y)
  ymaxindex = y.index(ymax)
  xmax = x[ymaxindex]
  return xmax,ymax

class Plot():
  #Created this class because i need ax2 to be "global"
  #see example http://matplotlib.sourceforge.net/examples/api/fahrenheit_celcius_scales.html
  def __init__(self, objects, timebins, conf):
    self.fig = plt.figure(figsize=(15,6))
    self.ax = self.fig.add_subplot(111)
    #self.ax2 = self.ax.twinx() #airmass axis
    #self.ax.callbacks.connect("ylim_changed", self.UpdateAx2)
    self.ax.set_title("Altitudes on "+date)
    self.ax.set_ylabel('Altitude (deg)')
    self.ax.set_xlabel('UTC')
    xlim = 24-(timebins[1]-timebins[0])
    self.ax.set_xlim((0,xlim))
    self.ax.set_ylim((18,95))
    #self.ax2.set_xlim((0,24))
    #self.ax2.set_ylabel('Airmass')
    for obj in objects.keys():
      alt = objects[obj]
      xmax, ymax = GetMax(timebins,alt)
      self.ax.text(xmax, ymax+1, obj, ha='center', va='center', rotation=90)
      self.ax.plot( timebins, alt, 'g')
    self.ax.axhline(y=30, xmin=0, xmax=xlim, color='r')
    self.ax.text(2, 31.5, "airmass=2.0",color='r', ha='center', va='center')
    self.ax.axhline(y=41.45, xmin=0, xmax=xlim, color='r')
    self.ax.text(2, 42.95, "airmass=1.5", color='r', ha='center', va='center')
    trans = mtransforms.blended_transform_factory(self.ax.transData, self.ax.transAxes)
    if night_end > 12:
        xfill = numpy.arange(night_end, 23.9999, 0.1)
        self.ax.fill_between(xfill, 0, 91, facecolor='red', alpha=0.2, transform=trans)
        xfill = numpy.arange(0, night_start, 0.1)
        self.ax.fill_between(xfill, 0, 91, facecolor='red', alpha=0.2, transform=trans)
    else:
        xfill = numpy.arange(night_end,night_start, 0.1)
        self.ax.fill_between(xfill, 0, 91, facecolor='red', alpha=0.2, transform=trans)
    if conf.curtime:
      curtime = datetime.now().hour + datetime.now().minute/60. + datetime.now().second/3600.
      self.ax.axvline(x=curtime, ymin=0, ymax=95, color='gray')
    #plt.show()
    plt.savefig(figname,bbox_inches='tight')
  def UpdateAx2(self,ax1):
    y1, y2 = self.ax.get_ylim()
    self.ax2.set_ylim(self.AirMass(y1), self.AirMass(y2))
    self.ax2.figure.canvas.draw()
  def AirMass(self,h):
    secz = 1./math.cos(math.radians(90 - h))
    X = secz-0.0018167*(secz-1)-0.002875*(secz-1)**2-0.0008083*(secz-1)**3
    #X=secz
    return X

def main():
  conf = Config()
  objects = ReadTabob(conf)
  objects, timebins = GetAlt(conf,objects)
  Plot(objects, timebins, conf)

if __name__ == '__main__':
  main()
