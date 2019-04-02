#!/bin/python3
import csv
import urllib.request
import sqlite3
import io
import math
from datetime import datetime

URL = "http://www.mips-lab.net/export_events_to_csv"
YEAR = 2018

def stats_ouverture(events_url, year=None):
    '''
    Cette fonction extrait les statistiques depuis le fichier CSV
    '''
    if year is None:
        year = YEAR
    csv_events = urllib.request.urlopen(events_url).read().decode('UTF-8')
    csv_events = io.StringIO(csv_events)
    events = csv.reader(csv_events, delimiter=";")
    conn = sqlite3.connect(":memory:")
    c = conn.cursor()
    c.execute('''CREATE TABLE events
            (cat text,
            title text,
            who text,
            start date,
            end date,
            duration real)
            ''')
    for row in events:
        if len(row) != 0 and row[0] != "cat":
            start = datetime.strptime(row[3], "%d/%m/%Y %H:%M")
            end = datetime.strptime(row[4], "%d/%m/%Y %H:%M")
            sql = [row[0], row[1], row[2], start.isoformat(), end.isoformat(), row[5]]
            c.execute('''INSERT INTO events
                    (cat, title, who, start, end, duration)
                    VALUES (?, ?, ?, ?, ?, ?)''', sql)
            conn.commit()
    c.execute("SELECT cat FROM events")
    list_events = c.fetchall()
    categories = []
    for item in list_events:
        categories.append(item[0])
    events_type = list(set(categories))
    events_stats = {}
    for events in events_type:
        c.execute("SELECT COUNT (*) FROM events WHERE cat = ? AND start >= ? AND end <= ?", (events, "{}-01-01".format(year), "{}-12-31".format(year)))
        events_stats[events] = c.fetchone()[0]
    for events in events_type:
        c.execute("SELECT SUM(duration) FROM events WHERE cat = ? AND start >= ? AND end <= ?", (events, "{}-01-01".format(year), "{}-12-31".format(year)))
        duration = events + '_duration'
        try:
            events_stats[duration] = float(c.fetchone()[0])
        except TypeError:
            events_stats[duration] = 0
    conn.close()
    return(events_stats)


def graph(nom, stats, liste):
    angle_full = []
    angle_deg = []
    somme = 0
    for partie in liste:
        angle_full.append(stats[partie])
    for i in angle_full:
        somme = somme + i
    for i in angle_full:
        angle_deg.append((i / somme) * 360)
    nom_f = nom.replace(' ','_') + '.svg'
    f = open(nom_f,"w")
    f.write('''<svg xmlns="http://www.w3.org/2000/svg" version="1.1">\n''')
    f.write('''<text x="200" y="20" style="text-anchor: middle">''')
    f.write(nom)
    f.write('''</text>\n''')
    radius = 180
    startx = 200
    starty = 220
    lastx = radius
    lasty = 0
    seg = 0
    i = 0
    color_liste = ['red','yellow','green','blue','indigo',
            'slategrey','greenyellow','wheat']
    for a in angle_deg:
        arc = "0"
        seg = a + seg
        if (a > 180):
            arc = "1"
        radseg = math.radians(seg)
        nextx = int(math.cos(radseg) * radius)
        nexty = int(math.sin(radseg) * radius)
        f.write('<path d="M '+str(startx)+','+str(starty)+
                ' l '+str(lastx)+','+str(-(lasty))+' a' +
                str(radius) + ',' +str(radius) + ' 0 ' + arc + ',0 '+
                str(nextx - lastx)+
                ','+str(-(nexty - lasty))+ ' z" ')
        f.write('fill="'+ color_liste[i] +'" stroke="black" stroke-width="2"' +
                ' stroke-linejoin="round" />\n')
        f.write('<rect x="400" y="'+str(35+(i*25))+'" width="40" height="20"' +
                ' fill="'+ color_liste[i] +'" stroke="black"' +
                ' stroke-width="1" />\n')
        f.write('<text x="442" y="'+str(50+(i*25))+
                '" style="text-anchor: start">')
        q = int(stats[liste[i]])
        qp = round(((q*100) / somme), 2)
        n = liste[i].replace('-',' ').replace('_',' ')
        f.write(str(n) + ' : ' + str(qp) + '% (' + str(q) + ')')
        f.write('</text>\n')
        lastx = nextx
        lasty = nexty
        i = i + 1
    f.write('</svg>\n')
    f.close()
### Fin de la fonction pour le graphique

if __name__ == '__main__':
    statistiques_events = stats_ouverture(events_url, events_type)
    graph("Les ouvertures du MIPS - par nombre",statistiques_events,listegraph1)
    graph("Les ouvertures du MIPS - par heures",statistiques_events,listegraph2)
