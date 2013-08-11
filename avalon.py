#!/usr/bin/env python
from random import randint
players = ['ever', 'sharon', 'karolina', 'liam','henry','charlie','player7','player8','player9','player10']
def playerassign(players):
    if len(players) > 10:
        print "[i] there are too many players \n[i] --> shortening the list"
        players = players[0:10]
        print players
    resistance = ['merlyn','percible','servant1','servant2','servant3','servant4']
    spies = ['morgana','assasin','mordrid','spy1','oberon']
    roles = ['merlyn','assasin','percible','morgana','servant1','spy1','servant2','servant3','servant4','spy2']
    takenPlayers = []
    PlayerAssigns = {}
    for player in players:
        pickerindex = randint(0,len(players)-1)
        while pickerindex in takenPlayers:
            pickerindex = randint(0,len(players)-1)
        takenPlayers.append(pickerindex)
        PlayerAssigns[player] = roles[pickerindex]
        print pickerindex
    print PlayerAssigns
    return PlayerAssigns
        

playerassign(players)
print "I work"