# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 20:10:51 2020

@author: ruihi
"""

from enum import IntEnum,Enum
from math import floor
import numpy as np
from copy import deepcopy
from scipy.interpolate import interp1d
#import datetime as dt

gpst0=[1980,1,6,0,0,0]


class rCST():
    CLIGHT=299792458.0
    MU_GPS=3.9860050E14
    MU_GAL=3.986004418E14
    GME=3.986004415E+14
    GMS=1.327124E+20
    GMM=4.902801E+12
    OMGE=7.2921151467E-5
    OMGE_GAL=7.2921151467E-5
    RE_WGS84=6378137.0
    FE_WGS84=(1.0/298.257223563)
    AU=149597870691.0
    D2R=0.017453292519943295
    AS2R=D2R/3600.0
    DAY_SEC=86400.0    
    CENTURY_SEC=DAY_SEC*36525.0

class uGNSS(IntEnum):
    GPS=0;SBS=1;GAL=2;BDS=3;QZS=5;GLO=6;GNSSMAX=7
    GPSMAX=32;GALMAX=36;BDSMAX=63;QZSMAX=10;
    GLOMAX=24;SBSMAX=24
    NONE=-1
    MAXSAT=GPSMAX+GLOMAX+GALMAX+BDSMAX+QZSMAX

class uSIG(IntEnum):
    GPS_L1CA=0;GPS_L2W=2;GPS_L2CL=3;GPS_L2CM=4;GPS_L5Q=6
    SBS_L1CA=0
    GAL_E1C=0;GAL_E1B=1;GAL_E5BI=5;GAL_E5BQ=6
    BDS_B1ID1=0;BDS_B1ID2=1;BDS_B2ID1=2;BDS_B2ID2=3
    QZS_L1CA=0;QZS_L1S=1;QZS_L2CM=4;QZS_L2CL=5
    GLO_L1OF=0;GLO_L2OF=2
    NONE=-1
    SIGMAX=7

class rSIG(IntEnum):
    NONE=0;L1C=1;L1X=2;L1W=3;L2L=4;L2X=5;L2W=6;L5Q=7;L5X=8;L7Q=9;L7X=10
    SIGMAX=16

class gtime_t():
    def __init__(self,time=0,sec=0.0):
        self.time=time
        self.sec=sec

class Obs():
    def __init__(self):
        self.nm=0
        self.t=gtime_t()
        self.P=[]
        self.L=[]
        self.data=[]
        self.sat=[]

class Eph():
    sat=0;iode=0;iodc=0
    af0=0.0;af1=0.0;af2=0.0
    toc=0;toe=0;tot=0;week=0
    crs=0.0;crc=0.0;cus=0.0;cus=0.0;cis=0.0;cic=0.0
    e=0.0;i0=0.0;A=0.0;deln=0.0;M0=0.0;OMG0=0.0
    OMGd=0.0;omg=0.0;idot=0.0;tgd=0.0;tgd_b=0.0
    sva=0;health=0;fit=0
    toes=0
    
    def __init__(self,sat=0):
        self.sat=sat

class Nav():
    def __init__(self):
        self.eph=[]
        self.ion=np.array([
            [0.1118E-07,-0.7451E-08,-0.5961E-07, 0.1192E-06],
            [0.1167E+06,-0.2294E+06,-0.1311E+06, 0.1049E+07]])
        self.elmin=np.deg2rad(15.0)
        self.tidecorr=False
        self.nf=2
        self.excl_sat=[]
        self.freq=[1.57542e9,1.22760e9,1.17645e9,1.20714e9]
        self.rb=[0,0,0] # base station position in ECEF [m]
        #self.gnss_t=[uGNSS.GPS,uGNSS.QZS]
        self.gnss_t=[uGNSS.GPS,uGNSS.GAL,uGNSS.QZS]
    
def leaps(tgps):
    return -18.0

def epoch2time(ep):
    doy=[1,32,60,91,121,152,182,213,244,274,305,335]
    time=gtime_t()
    year=int(ep[0]);mon=int(ep[1]);day=int(ep[2])
    
    if year<1970 or 2099<year or mon<1 or 12<mon:
        return time
    days=(year-1970)*365+(year-1969)//4+doy[mon-1]+day-2
    if year%4==0 and mon>=3:
        days+=1
    sec=int(ep[5])
    time.time=days*86400+int(ep[3])*3600+int(ep[4])*60+sec
    time.sec=ep[5]-sec
    return time

def gpst2utc(tgps,leaps=-18):
    #tutc=tgps+dt.timedelta(seconds=leaps(tgps))
    tutc=tgps+leaps
    return tutc

def timeadd(t:gtime_t,sec):
    tr=deepcopy(t)
    tr.sec+=sec
    tt=floor(tr.sec)
    tr.time+=int(tt)
    tr.sec-=tt
    return tr

def timediff(t1:gtime_t,t2:gtime_t):
    dt=t1.time-t2.time
    dt+=t1.sec-t2.sec
    return dt

def gpst2time(week,tow):
    t=epoch2time(gpst0)
    if tow<-1e9 or 1e9<tow:
        tow=0.0
    t.time+=86400*7*week+int(tow)
    t.sec=tow-int(tow)
    #t=dt.datetime(1980,1,6)+dt.timedelta(weeks=week,seconds=tow)
    return t

def time2gpst(t:gtime_t):
    t0=epoch2time(gpst0)
    sec=t.time-t0.time
    week=int(sec/(86400*7))
    tow=sec-week*86400*7+t.sec
    
    #dts=(t-dt.datetime(1980,1,6)).total_seconds()
    #week=int(dts)//604800
    #tow=dts-week*604800
    return week,tow

def time2epoch(t):
    mday=[31,28,31,30,31,30,31,31,30,31,30,31,31,28,31,30,31,30,31,31,30,31,30,31,
          31,29,31,30,31,30,31,31,30,31,30,31,31,28,31,30,31,30,31,31,30,31,30,31]

    days=int(t.time/86400)
    sec=int(t.time-days*86400)
    day=days%1461
    for mon in range(48):
        if day>=mday[mon]:
            day-=mday[mon]
        else:
            break
    ep=[0,0,0,0,0,0]
    ep[0]=1970+days//1461*4+mon//12
    ep[1]=mon%12+1
    ep[2]=day+1
    ep[3]=sec//3600
    ep[4]=sec%3600//60
    ep[5]=sec%60+t.sec
    return ep
    
def time2doy(t):
    ep=time2epoch(t)
    ep[1]=ep[2]=1.0;ep[3]=ep[4]=ep[5]=0.0
    return timediff(t,epoch2time(ep))/86400+1

def prn2sat(sys,prn):
    if sys==uGNSS.GPS:
        sat=prn
    elif sys==uGNSS.GLO:
        sat=prn+uGNSS.GPSMAX
    elif sys==uGNSS.GAL:
        sat=prn+uGNSS.GPSMAX+uGNSS.GLOMAX
    elif sys==uGNSS.BDS:
        sat=prn+uGNSS.GPSMAX+uGNSS.GLOMAX+uGNSS.GALMAX
    elif sys==uGNSS.QZS:
        sat=prn-192+uGNSS.GPSMAX+uGNSS.GLOMAX+uGNSS.GALMAX+uGNSS.BDSMAX            
    else:
        sat=0
    return sat

def sat2prn(sat):
    if sat>uGNSS.GPSMAX+uGNSS.GLOMAX+uGNSS.GALMAX+uGNSS.BDSMAX:
        prn=sat-(uGNSS.GPSMAX+uGNSS.GLOMAX+uGNSS.GALMAX+uGNSS.BDSMAX)+192
        sys=uGNSS.QZS
    elif sat>uGNSS.GPSMAX+uGNSS.GLOMAX+uGNSS.GALMAX:
        prn=sat-(uGNSS.GPSMAX+uGNSS.GLOMAX+uGNSS.GALMAX)
        sys=uGNSS.BDS
    elif sat>uGNSS.GPSMAX+uGNSS.GLOMAX:
        prn=sat-(uGNSS.GPSMAX+uGNSS.GLOMAX)
        sys=uGNSS.GAL
    elif sat>uGNSS.GPSMAX:
        prn=sat-uGNSS.GPSMAX
        sys=uGNSS.GLO
    else:
        prn=sat
        sys=uGNSS.GPS
    return (sys,prn)

def sat2id(sat):
    id=[]
    sys,prn=sat2prn(sat)
    gnss_tbl='GSECIJR'
    if sys==uGNSS.QZS:
        prn-=192
    id='%s%02d' %(gnss_tbl[sys],prn)
    return id

def geodist(rs,rr):
    e=rs-rr
    r=np.linalg.norm(e)
    e=e/r
    r+=rCST.OMGE*(rs[0]*rr[1]-rs[1]*rr[0])/rCST.CLIGHT
    return r,e

# TBD
def dops_h(H):
    Qinv=np.linalg.inv(np.dot(H.T,H))
    dop=np.diag(Qinv)
    hdop=dop[0]+dop[1] # TBD
    vdop=dop[2] # TBD
    pdop=hdop+vdop;gdop=pdop+dop[3]
    dop=np.array([gdop,pdop,hdop,vdop])
    return dop

def dops(az,el,elmin=0):
    nm=az.shape[0]
    H=np.zeros((nm,4))
    n=0
    for i in range(nm):
        if el[i]<elmin:
            continue
        cel=np.cos(el[i]);sel=np.sin(el[i])
        H[n,0]=cel*np.sin(az[i])
        H[n,1]=cel*np.cos(az[i])
        H[n,2]=sel
        H[n,3]=1
        n+=1
    if n<4:
        return None
    Qinv=np.linalg.inv(np.dot(H.T,H))
    dop=np.diag(Qinv)
    hdop=dop[0]+dop[1] # TBD
    vdop=dop[2] # TBD
    pdop=hdop+vdop;gdop=pdop+dop[3]
    dop=np.array([gdop,pdop,hdop,vdop])
    return dop        


def xyz2enu(pos):
    sp=np.sin(pos[0]);cp=np.cos(pos[0]);
    sl=np.sin(pos[1]);cl=np.cos(pos[1]);
    E=np.array([[-sl,cl,0],
                [-sp*cl,-sp*sl,cp],
                [cp*cl,cp*sl,sp]])
    return E

def ecef2pos(r):
    e2=rCST.FE_WGS84*(2-rCST.FE_WGS84)
    r2=r[0]**2+r[1]**2
    v=rCST.RE_WGS84
    z=r[2]
    while True:
        zk=z
        sp=z/np.sqrt(r2+z**2)
        v=rCST.RE_WGS84/np.sqrt(1-e2*sp**2)
        z=r[2]+v*e2*sp
        if np.fabs(z-zk)<1e-4:
            break
    pos=np.array([np.arctan(z/np.sqrt(r2)),
                  np.arctan2(r[1],r[0]),
                  np.sqrt(r2+z**2)-v])
    return pos

def pos2ecef(pos):
    s_p=np.sin(pos[0]);c_p=np.cos(pos[0])
    s_l=np.sin(pos[1]);c_l=np.cos(pos[1])
    e2=rCST.FE_WGS84*(2.0-rCST.FE_WGS84)
    v=rCST.RE_WGS84/np.sqrt(1.0-e2*s_p**2)
    r=np.array([(v+pos[2])*c_p*c_l,
                (v+pos[2])*c_p*s_l,
                (v*(1.0-e2)+pos[2])*s_p])
    return r

def ecef2enu(pos,r):
    E=xyz2enu(pos)
    e=np.dot(E,r)
    return e

def satazel(pos,e):
    enu=ecef2enu(pos,e)
    az=np.arctan2(enu[0],enu[1])
    el=np.arcsin(enu[2])
    return az,el

def ionmodel(t,pos,az,el,ion=None):
    psi=0.0137/(el/np.pi+0.11)-0.022
    phi=pos[0]/np.pi+psi*np.cos(az)
    phi=np.max((-0.416,np.min((0.416,phi))))
    lam=pos[1]/np.pi+psi*np.sin(az)/np.cos(phi*np.pi)
    phi+=0.064*np.cos((lam-1.617)*np.pi)
    week,tow=time2gpst(t)
    tt=43200.0*lam+tow # local time
    tt-=np.floor(tt/86400)*86400
    f=1.0+16.0*np.power(0.53-el/np.pi,3.0) # slant factor
    
    h=[1,phi,phi**2,phi**3]
    amp=np.dot(h,ion[0,:])
    per=np.dot(h,ion[1,:])
    if amp<0:
        amp=0
    if per<72000.0:
        per=72000.0
    x=2.0*np.pi*(tt-50400.0)/per
    if np.abs(x)<1.57:
        v=5e-9+amp*(1.0+x*x*(-0.5+x*x/24.0))
    else:
        v=5e-9
    diono=rCST.CLIGHT*f*v
    return diono

def interpc(coef,lat):
    i=int(lat/15.0)
    if i<1:
        return coef[:,0]
    elif i>4:
        return coef[:,4]
    d=lat/15.0-i
    return coef[:,i-1]*(1.0-d)+coef[:,i]*d

def mapf(el,a,b,c):
    sinel=np.sin(el)
    return (1.0+a/(1.0+b/(1.0+c)))/(sinel+(a/(sinel+b/(sinel+c))))

def tropmapf(t,pos,el):
    if pos[2]<-1e3 or pos[2]>20e3 or el<=0.0:
        return 0.0,0.0
    coef = np.array([
        [1.2769934E-3, 1.2683230E-3, 1.2465397E-3, 1.2196049E-3, 1.2045996E-3],
        [2.9153695E-3, 2.9152299E-3, 2.9288445E-3, 2.9022565E-3, 2.9024912E-3],
        [62.610505E-3, 62.837393E-3, 63.721774E-3, 63.824265E-3, 64.258455E-3],
        [0.0000000E-0, 1.2709626E-5, 2.6523662E-5, 3.4000452E-5, 4.1202191E-5],
        [0.0000000E-0, 2.1414979E-5, 3.0160779E-5, 7.2562722E-5, 11.723375E-5],
        [0.0000000E-0, 9.0128400E-5, 4.3497037E-5, 84.795348E-5, 170.37206E-5],
        [5.8021897E-4, 5.6794847E-4, 5.8118019E-4, 5.9727542E-4, 6.1641693E-4],
        [1.4275268E-3, 1.5138625E-3, 1.4572752E-3, 1.5007428E-3, 1.7599082E-3],
        [4.3472961E-2, 4.6729510E-2, 4.3908931E-2, 4.4626982E-2, 5.4736038E-2],
        ])
    aht=[2.53E-5, 5.49E-3, 1.14E-3]
    lat=np.rad2deg(pos[0]);hgt=pos[2]
    y=(time2doy(t)-28.0)/365.25
    if lat<0.0:
        y+=0.5
    cosy=np.cos(2.0*np.pi*y)
    lat=np.abs(lat)
    c=interpc(coef,lat)
    ah=c[0:3]-c[3:6]*cosy
    aw=c[6:9]
    dm=(1.0/np.sin(el)-mapf(el,aht[0],aht[1],aht[2]))*hgt*1e-3
    mapfh=mapf(el,ah[0],ah[1],ah[2])+dm
    mapfw=mapf(el,aw[0],aw[1],aw[2])
    return mapfh,mapfw

def tropmodel(t,pos,el,humi=0.7):
    hgt=pos[2]
    
    # standard atmosphere
    pres=1013.25*np.power(1-2.2557e-5*hgt,5.2568)
    temp=15.0-6.5e-3*hgt+273.16
    e=6.108*humi*np.exp((17.15*temp-4684.0)/(temp-38.45))
    # saastamoinen
    z=np.pi/2.0-el
    trop_hs=0.0022768*pres/(1.0-0.00266*np.cos(2*pos[0])-0.00028e-3*hgt)
    trop_wet=0.002277*(1255.0/temp+0.05)*e
    return (trop_hs+trop_wet)/np.cos(z)   

if __name__ == '__main__':
    t=epoch2time([2021,3,19,12,0,0])
    ep=time2epoch(t)
    #t=gpst2time(2151,554726)
    week,tow=time2gpst(t)
    t1=timeadd(t,300)
    
        