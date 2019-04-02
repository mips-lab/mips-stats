#!/usr/bin/env python3
import csv
import urllib.request
import sqlite3
import io
import math
from datetime import datetime
import pygal
import pprint

URL = "http://www.mips-lab.net/export_events_to_csv"
YEAR = 2017


def stats_ouverture(url=None, year=None):
    '''
    Cette fonction extrait les statistiques depuis le fichier CSV
    '''
    if year is None:
        year = YEAR
    if url is None:
        url = URL
    csv_events = urllib.request.urlopen(url).read().decode('UTF-8')
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
            sql = [row[0], row[1], row[2],
                    start.isoformat(), end.isoformat(), row[5]]
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
        c.execute("SELECT COUNT (*) FROM events WHERE cat = ? AND start >= ? AND end <= ?",
                (events, "{}-01-01".format(year), "{}-12-31".format(year)))
        events_stats[events] = c.fetchone()[0]
    for events in events_type:
        c.execute("SELECT SUM(duration) FROM events WHERE cat = ? AND start >= ? AND end <= ?",
                (events, "{}-01-01".format(year), "{}-12-31".format(year)))
        duration = events + '_duration'
        try:
            events_stats[duration] = float(c.fetchone()[0])
        except TypeError:
            events_stats[duration] = 0
    conn.close()
    return(events_stats)


def graph(stats):
    '''
    Graph avec pygal
    '''
    pie_chart = pygal.Pie()
    pie_chart.title = 'Ouverture du MIPS-lab'
    for item in stats:
        if "duration" not in item:
            if stats[item] != 0:
                pie_chart.add(item, stats[item])
    pie_chart.render_to_file('ouvertures-nbre.svg')
    pie_chart = pygal.Pie()
    pie_chart.title = 'Heures d\'ouverture du MIPS-lab'
    for item in stats:
        if "duration" in item:
            if stats[item] != 0:
                pie_chart.add(item.split("_")[0], stats[item])
    pie_chart.render_to_file('ouvertures-heures.svg')


if __name__ == '__main__':
    statistiques_events = stats_ouverture()
    graph(statistiques_events)
    pprint.pprint(statistiques_events)
