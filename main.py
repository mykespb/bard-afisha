#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# by Mikhail (myke) Kolodin
# 2018-12-05 4.33
# api 2018-09-13 0.6

from __future__ import division, print_function

import sqlite3 as sql
import datetime as dt
import os
import string, re
import json

from bottle import *

__author__       = 'Mikhail (myke) Kolodin'
__version__      = '4.33'
__date__         = '2018-12-05'
__apiversion__   = '0.6'
__program__      = 'bard-afisha'
__encoding__     = 'utf-8'
__utc__          = 'UTC+0300'

DATABASE    = 'ap.db'

admname = 'miko'
admpass = 'ryto'

minusday = dt.timedelta(days=-10)
dtoday = dt.date.today()
yesday = dtoday + minusday
#yesday = dtoday
dout = str(dtoday.isoformat())
yout = str(yesday.isoformat())
#dout = str(today.isoformat())
dtnow = dt.datetime.now()
dtout = str(dtnow.isoformat())
doyear = dtout[:4]

months = "Январь Февраль Март Апрель Май Июнь Июль Август Сентябрь Октябрь Ноябрь Декабрь".split()

#from bottle import static_file

@get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='static/')

#@route('/static/<filename>')
#def server_static(filename):
#    return static_file(filename, root='/static')

def getweekday(s):
    """ weekday from sql string """
    dd = [int(q) for q in s.split('-')]
    d = dt.date(*dd)
    wds = [u"пн", u"вт", u"ср", u"чт", u"пт", u"сб", u"вс"]
    return wds[d.weekday()]

def markurls (s):
    t = re.sub (r"(http://[-a-zA-Z0-9,.%()!?/]+)", r"<a href='\1'>\1</a>", s)
    return t

def mark(s):
    """ makes html links from addresses """
    s = re.sub(r'(https?://\S+)', r'<a href="\1" target=panorama>\1</a>', s)
    return s

def dates():
    """today and tomorrow"""
    now = dt.datetime.now()
    tmrw = now + dt.timedelta(days=1)
    day_now = dt.datetime.strftime (now, "%d.%m.%Y")
    day_tmrw = dt.datetime.strftime (tmrw, "%d.%m.%Y")
    mon_now = day_now[3:]
    mon_tmrw = day_tmrw[3:]
    return day_now, mon_now, day_tmrw, mon_tmrw

@get('/')
def index():
    """ show all data from database """
    response.set_cookie ('edit', 'no')
    conn = sql.connect(DATABASE)
    c = conn.cursor()
    cur = c.execute ("select * from data where datesql >= '%s' order by datesql, time" % dout)
    d = [dict(id=row[0], wd=row[1], date=row[2], datesql=row[3],
        time=row[4], city=row[5], place=row[6], what=row[7], desc=mark(row[8]),
        source=mark(row[9])
        ) for row in cur.fetchall()]
    return template ("bdata.html", data=d, dt=dt.datetime.now(), ver=__version__, datestr=dates(), months=months)

@get('/ed')
def login():
    """ try to login """
    return template ("login.html", dt=dt.datetime.now(), ver=__version__, datestr=dates(), months=months)

@post('/ed')
def enter():
    """ check enter """
    aname = request.forms.get('name')
    apass = request.forms.get('pass')
    if True or aname == admname and apass == admpass:
        response.set_cookie ('edit', 'yes')
        conn = sql.connect(DATABASE)
        conn.text_factory = str
        c = conn.cursor()
        cur = c.execute ("select * from data where datesql >= '%s' order by datesql, time" % yout)
        d = [dict(id=row[0], wd=row[1], date=row[2], datesql=row[3],
            time=row[4], city=row[5], place=row[6], what=row[7], desc=row[8],
            source=row[9]
            ) for row in cur.fetchall()]
        cur = c.execute("select distinct place from data order by place")
        places = [row[0] for row in cur.fetchall()]
        return template ("edit.html", data=d, dt=dt.datetime.now(), places=places, ver=__version__, datestr=dates(), months=months)
    else:
        response.set_cookie ('edit', 'no')
        return template ("bdata.html", data=d, dt=dt.datetime.now(), ver=__version__, datestr=dates(), months=months)

@post('/add')
def doadd():
    """ add new event """
    if request.get_cookie('edit') != 'yes':
        response.set_cookie ('edit', 'no')
        return template ("bad.html", dt=dt.datetime.now(), ver=__version__)
    adate = request.forms.get('date')
    atime = request.forms.get('time')
    acity = request.forms.get('city')
    aplace = request.forms.get('place')
    anewplace = request.forms.get('newplace')
    awhat = request.forms.get('what')
    adesc = request.forms.get('desc')
    asource = request.forms.get('source')
    conn = sql.connect(DATABASE)
    conn.text_factory = str
    c = conn.cursor()
    simdate = adate[8:10] + '.' + adate[5:7] + '.' + adate[:4]
    wd = getweekday(adate)
    aplace = anewplace if anewplace != '-' else aplace
    cur = c.execute("insert into data (id, wd, date, datesql, time, city, place, what, desc, source) values (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
         (wd, simdate, adate, atime, acity, aplace, awhat, adesc, asource))
    conn.commit()
    cur = c.execute ("select * from data where datesql >= '%s' order by datesql, time" % yout)
    d = [dict(id=row[0], wd=row[1], date=row[2], datesql=row[3],
        time=row[4], city=row[5], place=row[6], what=row[7], desc=row[8],
        source=row[9]
        ) for row in cur.fetchall()]
    cur = c.execute("select distinct place from data order by place")
    places = [row[0] for row in cur.fetchall()]
    return template ("edit.html", data=d, dt=dt.datetime.now(), places=places, ver=__version__, datestr=dates(), months=months)
    #~ return ', '.join ([adate, atime, acity, aplace, anewplace, awhat, adesc, asource])

@get('/del/<id>')
def dodel(id):
    """ delete event """
    if request.get_cookie('edit') != 'yes':
        response.set_cookie ('edit', 'no')
        return template ("bad.html", dt=dt.datetime.now(), ver=__version__)
    conn = sql.connect(DATABASE)
    conn.text_factory = str
    c = conn.cursor()
    cur = c.execute("delete from data where id = '%s'" % id)
    conn.commit()
    cur = c.execute ("select * from data where datesql >= '%s' order by datesql, time" % yout)
    d = [dict(id=row[0], wd=row[1], date=row[2], datesql=row[3],
        time=row[4], city=row[5], place=row[6], what=row[7], desc=row[8],
        source=row[9]
        ) for row in cur.fetchall()]
    cur = c.execute("select distinct place from data order by place")
    places = [row[0] for row in cur.fetchall()]
    return template ("edit.html", data=d, dt=dt.datetime.now(), places=places, ver=__version__, datestr=dates(), months=months)

def corrdate(s):
    """check if date is set and update it """
    #~ if s.endswith(doyear):
        #~ s = s[:-10] + doyear
    #~ else:
    if s == "":
        s = doyear
    return s

@get('/mod/<id>')
def premod(id):
    """ modify event """
    if request.get_cookie('edit') != 'yes':
        response.set_cookie ('edit', 'no')
        return template ("bad.html", dt=dt.datetime.now(), ver=__version__)
    conn = sql.connect(DATABASE)
    conn.text_factory = str
    c = conn.cursor()
    cur = c.execute ("select * from data where id='%s'" % id)
    mod = cur.fetchone()
    cur = c.execute ("select * from data where datesql >= '%s' order by datesql, time" % yout)
    d = [dict(id=row[0], wd=row[1], date=row[2], datesql=row[3],
        time=row[4], city=row[5], place=row[6], what=row[7], desc=row[8],
        source=corrdate(row[9])
        ) for row in cur.fetchall()]
    cur = c.execute("select distinct place from data order by place")
    places = [row[0] for row in cur.fetchall()]
    return template ("mod.html", mod=mod, data=d, dt=dt.datetime.now(), places=places, ver=__version__, datestr=dates(), months=months)

@post('/mod')
def domod():
    """ make real modification """
    if request.get_cookie('edit') != 'yes':
        response.set_cookie ('edit', 'no')
        return template ("bad.html", dt=dt.datetime.now(), ver=__version__)
    aid = request.forms.get('id')
    adate = request.forms.get('date')
    atime = request.forms.get('time')
    acity = request.forms.get('city')
    aplace = request.forms.get('place')
    anewplace = request.forms.get('newplace')
    awhat = request.forms.get('what')
    adesc = request.forms.get('desc')
    asource = request.forms.get('source')
    conn = sql.connect(DATABASE)
    conn.text_factory = str
    c = conn.cursor()
    simdate = adate[8:10] + '.' + adate[5:7] + '.' + adate[:4]
    wd = getweekday(adate)
    aplace = anewplace if anewplace != '-' else aplace
    cur = c.execute("update data set wd=?, date=?, datesql=?, time=?, city=?, place=?, what=?, desc=?, source=? where id=?", (wd, simdate, adate, atime, acity, aplace, awhat, adesc, asource, aid))
    conn.commit()
    cur = c.execute ("select * from data where datesql >= '%s' order by datesql, time" % yout)
    d = [dict(id=row[0], wd=row[1], date=row[2], datesql=row[3],
        time=row[4], city=row[5], place=row[6], what=row[7], desc=row[8],
        source=row[9]
        ) for row in cur.fetchall()]
    cur = c.execute("select distinct place from data order by place")
    places = [row[0] for row in cur.fetchall()]
    return template ("edit.html", data=d, dt=dt.datetime.now(), places=places, ver=__version__, datestr=dates(), months=months)

@get('/clone/<id>')
def preclone(id):
    """ clone  event """
    if request.get_cookie('edit') != 'yes':
        response.set_cookie ('edit', 'no')
        return template ("bad.html", dt=dt.datetime.now(), ver=__version__)
    conn = sql.connect(DATABASE)
    conn.text_factory = str
    c = conn.cursor()
    cur = c.execute ("select * from data where id='%s'" % id)
    mod = cur.fetchone()
    cur = c.execute ("select * from data where datesql >= '%s' order by datesql, time" % dout)
    d = [dict(id=row[0], wd=row[1], date=row[2], datesql=row[3],
        time=row[4], city=row[5], place=row[6], what=row[7], desc=row[8],
        source=row[9]
        ) for row in cur.fetchall()]
    cur = c.execute("select distinct place from data order by place")
    places = [row[0] for row in cur.fetchall()]
    return template ("clone.html", mod=mod, data=d, dt=dt.datetime.now(), places=places, ver=__version__, datestr=dates(), months=months)

@post('/clone')
def doclone():
    """ make real clone """
    if request.get_cookie('edit') != 'yes':
        response.set_cookie ('edit', 'no')
        return template ("bad.html", dt=dt.datetime.now(), ver=__version__)
    aid = request.forms.get('id')
    adate = request.forms.get('date')
    atime = request.forms.get('time')
    acity = request.forms.get('city')
    aplace = request.forms.get('place')
    anewplace = request.forms.get('newplace')
    awhat = request.forms.get('what')
    adesc = request.forms.get('desc')
    asource = request.forms.get('source')
    conn = sql.connect(DATABASE)
    conn.text_factory = str
    c = conn.cursor()
    simdate = adate[8:10] + '.' + adate[5:7] + '.' + adate[:4]
    wd = getweekday(adate)
    aplace = anewplace if anewplace != '-' else aplace
    cur = c.execute("insert into data (id, wd, date, datesql, time, city, place, what, desc, source) values (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
         (wd, simdate, adate, atime, acity, aplace, awhat, adesc, asource))
    conn.commit()
    cur = c.execute ("select * from data where datesql >= '%s' order by datesql, time" % yout)
    d = [dict(id=row[0], wd=row[1], date=row[2], datesql=row[3],
        time=row[4], city=row[5], place=row[6], what=row[7], desc=row[8],
        source=row[9]
        ) for row in cur.fetchall()]
    cur = c.execute("select distinct place from data order by place")
    places = [row[0] for row in cur.fetchall()]
    return template ("edit.html", data=d, dt=dt.datetime.now(), places=places, ver=__version__, datestr=dates(), months=months)

@get('/api/version')
def api_version():
    """ api: get version of API """
    dtoday = dt.date.today()
    dout = str(dtoday.isoformat())
    dtnow = dt.datetime.now()
    dtout = str(dtnow.isoformat())
    d = {"version":__version__, "author": __author__, "apiversion": __apiversion__, "program": __program__, "encoding": __encoding__, "date": __date__, "date_time": dtout, "utc": __utc__}
    return json.dumps(d, ensure_ascii=True)

@get('/api/getnew')
def api_getnew():
    """ api: get future events list"""
    dtoday = dt.date.today()
    dout = str(dtoday.isoformat())
    dtnow = dt.datetime.now()
    dtout = str(dtnow.isoformat())
    conn = sql.connect(DATABASE)
    c = conn.cursor()
    cur = c.execute ("select * from data where datesql >= '%s' order by datesql, time" % dout)
    d = [dict(id=row[0], wd=row[1], date=row[2], datesql=row[3],
        time=row[4], city=row[5], place=row[6], what=row[7], desc=row[8],
        source=row[9]
        ) for row in cur.fetchall()]
    out = {'project': 'kab', 'service': __program__, 'request': 'future', 'version': __version__, 'api_version': __apiversion__, 'date': __date__,
        'author': __author__, 'date_time': dtout, 'utc': __utc__, 'events': d}
    #~ return out
    return json.dumps(out, ensure_ascii=True)

@get('/api/gethuman')
def api_gethuman():
    """ api: get future events list"""
    dtoday = dt.date.today()
    dout = str(dtoday.isoformat())
    dtnow = dt.datetime.now()
    dtout = str(dtnow.isoformat())
    conn = sql.connect(DATABASE)
    c = conn.cursor()
    cur = c.execute ("select * from data where datesql >= '%s' order by datesql, time" % dout)
    d = [dict(id=row[0], wd=row[1], date=row[2], datesql=row[3],
        time=row[4], city=row[5], place=row[6], what=row[7], desc=row[8],
        source=row[9]
        ) for row in cur.fetchall()]
    out = {'project': 'kab', 'service': __program__, 'request': 'future', 'version': __version__, 'api_version': __apiversion__, 'date': __date__,
        'author': __author__, 'date_time': dtout, 'utc': __utc__, 'events': d}
    #~ return out
    return json.dumps(out, ensure_ascii=False).encode('utf8')

if __name__ == '__main__':
    run(host='localhost', port=8886, reloader=True)
