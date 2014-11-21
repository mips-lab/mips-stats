#!/bin/python3
import csv
import urllib.request
import sqlite3
import io
import math

events_url = "http://www.mips-lab.net/export_events_to_csv"
events_type = ['ouvertures', 'craft-stickers-flocage', 'formation-python',
    'formation-decoupeuse-laser', 'formation-imprimante-3d']
listegraph1 = ['ouvertures', 'formation-imprimante-3d', 'formation-decoupeuse-laser',
    'craft-stickers-flocage', 'formation-python']

### Début de la fonction pour les statistiques d'ouverture :
# Prend en argument le fichier CSV du plone (url)
# et une liste des types d'événements.
# Il en ressort un dict avec les nombres de créneaux et les durées de ces
# créneaux d'ouverture.
###

def stats_ouverture(events_url, events_type):
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
        if len(row) != 0:
            sql = [row[0], row[1], row[2], row[3], row[4], row[5]]
            c.execute('''INSERT INTO events
                    (cat, title, who, start, end, duration)
                    VALUES (?, ?, ?, ?, ?, ?)''', sql)
            conn.commit()
    events_stats = {}
    for events in events_type:
        c.execute('''SELECT COUNT (*) FROM events WHERE cat = ?''', (events,))
        events_stats[events] = (c.fetchone()[0])
    c.execute('''SELECT duration FROM events''')
    for events in events_type:
        total = 0
        c.execute('''SELECT duration FROM events WHERE cat = ?''', (events,))
        for row in c:
            dur = row[0].replace(',','.')
            try:
                h = float(dur)
            except:
                h = 0
                pass
            total = total + h
            duration = events + '_duration'
            events_stats[duration] = total
    conn.close()
    return(events_stats)
### Fin de la fonction pour les statistiques d'ouverture

### Début de la fonction pour le graphique
# Prend en argument le nom du grah, le dict de statistiques et
# la liste des choses à grapher.
# Cette page m'a bien aidé : http://wiki.scribus.net/canvas/Making_a_Pie_Chart
###

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
        n = liste[i].replace('-',' ')
        f.write(str(n) + ' : ' + str(qp) + '% (' + str(q) + ' heures)')
        f.write('</text>\n')
        lastx = nextx
        lasty = nexty
        i = i + 1
    f.write('</svg>\n')
    f.close()
### Fin de la fonction pour le graphique

if __name__ == '__main__':
    statistiques = stats_ouverture(events_url, events_type)
    graph("Les ouvertures du MIPS",statistiques,listegraph1)
