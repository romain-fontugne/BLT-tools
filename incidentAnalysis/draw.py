import matplotlib
import sys
matplotlib.use("AGG")
from matplotlib import pyplot as plt
import numpy as np
import argparse
import pickle
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from datetime import datetime as dt
from datetime import timedelta as td
import csv


parser = argparse.ArgumentParser()
parser.add_argument("pickle_file")
parser.add_argument("outfile")
parser.add_argument("-t", "--tags", help = "if you want to draw only several tags. ex) duplicate_announce,new_prefix")
parser.add_argument("-l", "--log", help = "if you want to draw as log scale.", action = "store_true")
args = parser.parse_args()

# get date
date = args.pickle_file.split("/")[-1][:8]

# pickle load
pkl = args.pickle_file
with open(pkl, "rb") as f:
    data = pickle.load(f)   ## data[tagName][time] = [value]

alert_flags = dict()
sorted_data = dict()
for tag in data.items():
    sorted_data[tag[0]] = np.array(sorted(tag[1].items(), key=lambda x: x[0]))[:,1]
    alert_flags[tag[0]] = 0

info = dict()
for sdata in sorted_data.items():
    # info = {tag_name : [mean, std, threshold]
    info[sdata[0]] = list()
    info[sdata[0]].append(np.mean(sdata[1]))
    info[sdata[0]].append(np.std(sdata[1]))
    info[sdata[0]].append(info[sdata[0]][0] + info[sdata[0]][1] * 2)
    print sdata[0] + ": " + str(info[sdata[0]])

# figure format
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
daysFmt = mdates.DateFormatter("%H")
ax.xaxis.set_major_formatter(daysFmt)
ax.set_xlabel("hour")
ax.set_ylabel("the number of tag")
tagColors = ['blue', 'turquoise', 'g','greenyellow', 'y', 'gold', 'coral', 'r', 'mediumvioletred', 'purple','indigo', 'rosybrown', 'cadetblue','k']

# plot
movingValue = 30
ones = np.ones(movingValue)/movingValue
maximumY = 0
maximumY2 = 0
scatter = False
startTime = dt.strptime(date + "0000", "%Y%m%d%H%M")
endTime = dt.strptime(date + "2359", "%Y%m%d%H%M")
timeStamp = startTime
for (tag,C) in zip(data.items(), tagColors):
    if tag[0] == "prepending_change":
        continue
    if tag[0] == "prepending_add":
        continue
    if tag[0] == "prepending_remove":
        continue
    x = list()
    y = list()
    while timeStamp < tag[1].keys()[0]:
        x.append(timeStamp)
        y.append(0)
        timeStamp += td(minutes=1)
    lgnd = plt.legend(bbox_to_anchor=(1.05, 0), loc='lower left', borderaxespad=0)
    for item in sorted(tag[1].items(), key=lambda x: x[0]):
        x.append(item[0])
        y.append(item[1])


    if len(x) == 0 and len(y) == 0:
        continue
    if len(y) >= movingValue:
        y2 = np.convolve(y, ones, "same").tolist()
    if max(y) > maximumY:
        maximumY = max(y)
    if max(y2) > maximumY2:
        maximumY2 = max(y2)
    for (ts, value) in zip(x, y2):
        if alert_flags[tag[0]] == 0:
            if value > info[tag[0]][2]:
                print "alert! " + str(ts) + " " + tag[0] + " value: " + str(value) + " thr:" + str(info[tag[0]][2])
                alert_flags[tag[0]] = 1
        else:
            if value <= info[tag[0]][2]:
                alert_flags[tag[0]] = 0
    if scatter == True:
        ax.scatter(x,y, s=20, c=C, marker='+', label=tag[0])
        ax.plot(x,y2,c=C, alpha=0.3 ,linewidth=1)
    else:
        ax.plot(x,y2,c=C, linewidth=1, label = tag[0])
    # log
    if args.log == True:
        ax.set_yscale("log")
    # /log
ax.set_xlim(startTime, endTime)
if args.log == True:
    ax.set_ylim(1, (maximumY*20/10))
else:
    ax.set_ylim(0, (maximumY2*11/10))

plt.savefig(args.outfile, bbox_extra_artists=(lgnd,), bbox_inches='tight')