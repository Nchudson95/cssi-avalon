#!/usr/bin/env python
# -------------------- Dependencies ------------------------
import webapp2
import jinja2
import os
from random import randint
import datetime
import time

from google.appengine.ext import ndb

jinja_environment = jinja2.Environment(loader=
    jinja2.FileSystemLoader(os.path.dirname(__file__)))

# ----------------------------------------------------------
# --------------------- Model ------------------------------
# ----------------------------------------------------------
class Game(ndb.Model):
    nameofgame = ndb.StringProperty(required = True)
    gamecreator = ndb.StringProperty(required = True)
    playersingame = ndb.StringProperty(repeated = True)
    roles = ndb.StringProperty(repeated = True)
    maxplayers = ndb.IntegerProperty(required = True)
    playerroles = ndb.JsonProperty(required = False)
    currentround = ndb.IntegerProperty(required = True)
    rejectcount = ndb.IntegerProperty(required = True)
    pickedonmission = ndb.StringProperty(repeated = True)
    selectionvotes = ndb.JsonProperty(required = False)
    missionselector = ndb.StringProperty(required = True)
    playersonmission = ndb.StringProperty(repeated = True)
    passfailvotes = ndb.JsonProperty(required = False)
    roundscores = ndb.StringProperty(repeated = True)
    submittedselection = ndb.BooleanProperty(required = True)
    approvereject = ndb.StringProperty(required = False)
    numoffails = ndb.JsonProperty(required = False)
    
    def url(self):
        return self.key.id()

# ----------------------------------------------------------
# --------------------- Useful Functions -------------------
# ----------------------------------------------------------

# This function assigns the various roles randomly to the players
# playing the game. It takes in both a list of players and list of
# avaible roles and then returns a dictionary in the format of
# dictionary[player] = role
def playerassign(players, roles):
    if len(players) > 10:
        players = players[0:10]
    takenPlayers = []
    PlayerAssigns = {}
    for player in players:
        pickerindex = randint(0,len(players)-1)
        while pickerindex in takenPlayers:
            pickerindex = randint(0,len(players)-1)
        takenPlayers.append(pickerindex)
        PlayerAssigns[player] = roles[pickerindex]
        print pickerindex
    return PlayerAssigns

# This function handles which player can see which other player names
# It takes in both the role of the player and a dictionary containing
# each player and their role ( {player1:role1, player2:role2...} ) and
# and returns a list of visible player names
def FindMatches(Role, playerroles):
    visible_roles = []
    if Role == 'Merlin':
        for player,role in playerroles.iteritems():
            if role in ['Morgana','Assasin','Oberon','Spy 1','Spy 2','Spy 3']:
                visible_roles.append(player)
    if Role in ['Assasin','Mordrid','Morgana','Spy 1','Spy 2','Spy 3']:
        for player,role in playerroles.iteritems():
            if role in ['Morgana','Assasin','Mordrid','Spy 1','Spy 2','Spy 3']:
                visible_roles.append(player)
    if Role == 'Percival':
        for player,role in playerroles.iteritems():
            if role in ['Morgana','Merlin']:
                visible_roles.append(player)
    return visible_roles

# -----------------------------------------------------------
# --------------------- Handlers ----------------------------
# -----------------------------------------------------------

# Upon landing on this page players are presented the option of
# joining a current game if they are avaible, creating a new game
# or going to an instruction page
class Landing(webapp2.RequestHandler):
    def get(self):
        currentgames = Game.query()
        currentgame = currentgames.get()
        # Checks if they are returning from another game and if so
        # deletes the old game from the game list
        if self.request.get('id') != '':
            if Game.get_by_id(int(self.request.get('id'))):
                game= Game.get_by_id(int(self.request.get('id')))
                game.key.delete()
        currentgames = Game.query()
        # if there are no current games, display special notice to user
        # noticed triggered but 'nogames' Boolean
        if not currentgame:
            template_values = {'games':currentgames, 'nogames':True, 'faileduser':False, 'failedgame':False}
            template = jinja_environment.get_template('landing.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'games':currentgames, 'nogames':False, 'faileduser':False, 'failedgame':False}
        template = jinja_environment.get_template('landing.html')
        self.response.out.write(template.render(template_values))
    def post(self):
        # The following if statements are checks to see if the user either selected a game or forgot to input
        # a username in an effort to avoid stack traces. 1) No game selection or username, 2) No username, 3) No game selected
        if self.request.get('user')=='' and self.request.get('game')=='':
            currentgames = Game.query()
            template_values= {'games':currentgames, "faileduser":True, 'nogames':False, "failedgame":True}
            template = jinja_environment.get_template('landing.html')
            self.response.out.write(template.render(template_values))
            return
        if self.request.get('user')=='':
            currentgames = Game.query()
            template_values = {'games':currentgames,'faileduser':True, 'nogames':False, 'failedgame':False}
            template = jinja_environment.get_template('landing.html')
            self.response.out.write(template.render(template_values))
            return
        if self.request.get('game')=='':
            currentgames = Game.query()
            template_values = {'games':currentgames, 'faileduser': False, 'nogames':False, 'failedgame': True}
            template = jinja_environment.get_template('landing.html')
            self.response.out.write(template.render(template_values))
            return
        # if input checks out, send user to a secondary landing page with link to desired game
        input_username = self.request.get('user')
        int_pickedgame=int(self.request.get('game'))
        Game.query().filter
        game = Game.get_by_id(int_pickedgame)
        game.playersingame.append(input_username)
        game.put()
        Games = Game.query()
        template_values= {"games":Games, 'pickedgame':game, 'user':input_username, 'nogames':False, "gameid":int_pickedgame}
        template = jinja_environment.get_template('landing2.html')
        self.response.out.write(template.render(template_values))

# As the name implies this is the create game page and handler
class CreateGame(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template('creategame.html')
        self.response.out.write(template.render(template_values))
    def post(self):
        input_nameofgame = self.request.get('nameofgame')
        input_creator = self.request.get('creator')
        input_maxplayers = self.request.get('max_players')
        input_maxplayers = int(input_maxplayers)
        mordridcheck = self.request.get('mordrid')
        oberoncheck = self.request.get('oberon')
        pervicalmorganacheck = self.request.get('pandm')
        # The following is the default list of roles
        input_roles = ['Merlin','Assasin','Resistance Servant 1','Spy 1','Resistance Servant 2','Spy 2','Resistance Servant 3','Resistance Servant 4','Resistance Servant 5','Spy 3']
        # The following series of If statements modify the above list in accordance to user selections
        if pervicalmorganacheck == 'yes':
            input_roles[2] = 'Percival'
            input_roles[3] = 'Morgana'
        if mordridcheck == 'yes':
            if input_roles[3] != 'Spy 1':
                input_roles[5] = 'Mordrid'
            else:
                input_roles[3] = 'Mordrid'
        if oberoncheck == 'yes':
            if input_roles[3] != 'Spy 1':
                if input_roles[5] != 'Spy 2':
                    input_roles[9] = 'Oberon'
                else:
                    input_roles[5] = 'Oberon'
            else:
                input_roles[3] = 'Oberon'
        # Create game entity with following attributes
        new_game = Game(nameofgame = input_nameofgame, gamecreator = input_creator, playersingame = [input_creator], roles = input_roles, missionselector = input_creator, maxplayers = input_maxplayers, pickedonmission = [], playersonmission = [], playerroles = {}, currentround = 0, rejectcount = 0, selectionvotes = {}, passfailvotes = {}, roundscores = ['1','2','3','4','5','6'], submittedselection = False, approvereject = '', numoffails = {})
        new_game.put()
        # Handle the lag between storing entities in ndb and being able to query that information
        time.sleep(1)
        Games = Game.query().filter(Game.nameofgame == input_nameofgame)
        Games = Games.fetch()
        template_values = {'games': Games, "user": input_creator}
        template = jinja_environment.get_template('creategame2.html')
        self.response.out.write(template.render(template_values))

# This is a waiting page until all necessary players are present. When that condition
# is met, then the creator of the game will be able to assign player roles the playerassign function.
# Furthermore, this page will also display which role you were assigned and which other players are
# visible to you via that role
class GameLobby(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        visibleroles = []
        if game.playerroles:
            visibleroles = FindMatches(game.playerroles[user], game.playerroles)
        template_values = {'game':game, 'gameid':gameid, 'user':user, 'visibleroles':visibleroles}
        template = jinja_environment.get_template('gamelobby.html')
        self.response.out.write(template.render(template_values))
    def post(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        assignments = playerassign(game.playersingame, game.roles)
        game.playerroles = assignments
        game.put()
        game = Game.get_by_id(int(gameid))
        visibleroles = FindMatches(game.playerroles[user], game.playerroles)
        template_values = {'gameid':gameid, 'user':user, 'game':game, 'visibleroles':visibleroles}
        template = jinja_environment.get_template('gamelobby.html')
        self.response.out.write(template.render(template_values))

#--------------- Round 1 Handlers -----------------------------------
# RoundVote1W handler sets up the nomination process for selecting which players will go on Mission 1
class RoundVote1W(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        roundnum = game.currentround
        # game.missionselector is a string calulated every time a sucessful nomination is sent.
        # As such, the modulo of roundnum will be used to be able to allow each player the chance
        # to nominate and to not break when roundnum exceeds the length of playersingame
        game.missionselector =  game.playersingame[roundnum%game.maxplayers]
        if game.approvereject == 'reject':
            game.approvereject = ''
            game.selectionvotes.clear()
            game.put()
        # Check if missionselector has submitted nominations for the mission
        if game.submittedselection:
            template_values = {'gameid':gameid, 'round':1, 'user':user, 'game':game}
            template = jinja_environment.get_template('mswait.html')
            self.response.out.write(template.render(template_values))
            return
        # Direct missionselector to nomination page with required number of nominations
        if user == game.missionselector:
            if game.maxplayers in [5,6,7]:
                requiredonmission = 2
            if game.maxplayers in [8,9,10]:
                requiredonmission = 3
            template_values = {'gameid':gameid, 'user':user, 'game':game, 'requiredonmission': requiredonmission, 'round':1, 'failselection':False}
            template = jinja_environment.get_template('missionselect.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'gameid':gameid, "round":1, 'user':user, 'game':game}
        template = jinja_environment.get_template('mswait.html')
        self.response.out.write(template.render(template_values))
    def post(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        playerselected = []
        # collect all of the nominated players into a list
        for player in game.playersingame:
            onmission = self.request.get(player)
            if onmission == 'yes':
                playerselected.append(player)
        # Verify nominations in accordance to game requirements of nominations
        if game.maxplayers in [5,6,7]:
            if len(playerselected) != 2:
                template_values = {'gameid':gameid, 'user':user, 'game':game, 'requiredonmission': 2, 'round':1, 'failselection':True}
                template = jinja_environment.get_template('missionselect.html')
                self.response.out.write(template.render(template_values))
                return
        if game.maxplayers in [8,9,10]:
            if len(playerselected) != 3:
                template_values = {'gameid':gameid, 'user':user, 'game':game,'requiredonmission': 3, 'round':1, 'failselecton':True}
                template = jinja_environment.get_template('missionselect.html')
                self.response.out.write(template.render(template_values))
                return
        # If all data checks out, store nominations and increment currentround
        game.pickedonmission = playerselected
        game.playersonmission = []
        game.submittedselection = True
        roundnum = game.currentround
        roundnum += 1
        game.currentround = roundnum
        game.put()
        template_values = {'gameid':gameid, 'user':user, 'round':1, 'game':game}
        template = jinja_environment.get_template('missionselectpass.html')
        self.response.out.write(template.render(template_values))

# This handler sets up the approve reject part of the game for the selection, if rejected,
# it will redirect to a mission nomination page with new missionselector
class RoundVote1V(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        if self.request.get('vote'):
            vote = self.request.get('vote')
            if not user in game.selectionvotes:
                game.selectionvotes[user] = vote
                game.put()
                # Does calculation of aapprove or reject upon last player submission
                if len(game.selectionvotes) == game.maxplayers:
                    game.playersonmission = game.pickedonmission
                    game.pickedonmission = []
                    game.submittedselection = False
                    tallyapproves = 0
                    for vote in game.selectionvotes:
                        if game.selectionvotes[vote] == 'approve':
                            tallyapproves += 1
                    if tallyapproves > game.maxplayers/2:
                        game.approvereject = 'approve'
                    else:
                        game.approvereject = 'reject'
                        if game.currentround == 5:
                            game.roundscores[0] = 'fail'
                    game.put()
            # exit if all votes are accounted for
            if len(game.selectionvotes) == game.maxplayers:
                template_values = {'gameid':gameid, 'game':game, 'user':user, 'round':1}
                template = jinja_environment.get_template('approverejectresults.html')
                self.response.out.write(template.render(template_values))
                return
            template_values = {'gameid':gameid, 'game':game, 'user':user, 'vote':vote, 'round':1}
            template = jinja_environment.get_template('approverejectwait.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'game':game, 'gameid':gameid, 'user':user, 'round':1}
        template = jinja_environment.get_template('approvereject.html')
        self.response.out.write(template.render(template_values))

# Mission wait page with exit for players on mission, send players on mission to specific page to vote
# after they vote, direct them to wait page with other players
class RoundMission1Wait(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        if user in game.playersonmission and user not in game.passfailvotes:
            if self.request.get('passfail'):
                game.passfailvotes[user] = self.request.get('passfail')
                game.put()
                template_values = {'game':game, 'gameid':gameid, 'round':1, 'user':user}
                template = jinja_environment.get_template('missionstandby.html')
                self.response.out.write(template.render(template_values))
                return
            template_values = {'game':game,'gameid':gameid, 'round':1, 'user':user, "numfails": 'one','scores':[0,0]}
            template = jinja_environment.get_template('onmission.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'game':game,'gameid':gameid, 'round':1 ,'user':user}
        template = jinja_environment.get_template('missionstandby.html')
        self.response.out.write(template.render(template_values))

# Displays mission results. Results calculated upon first person entering the page
class RoundMission1Results(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        # Run calculation for the first person to enter the page
        # tally fail votes and pass them off into template values to be displayed
        if game.roundscores[0] == '1':
            tally = 0
            for vote in game.passfailvotes:
                if game.passfailvotes[vote] == 'fail':
                    tally+=1
            if tally > 0:
                game.roundscores[0] = 'fail'
            else:
                game.roundscores[0] = 'pass'
            game.selectionvotes = {}
            game.approvereject = ''
            game.numoffails[0] = tally
            game.passfailvotes = {}
            game.rejectcount = 0
            game.put()
        template_values = {'gameid':gameid, 'game':game, 'round':2,'user':user, 'failvotes':tally}
        template = jinja_environment.get_template('missionresults.html')
        self.response.out.write(template.render(template_values))

#--------------- Round 2 Handlers -----------------------------------
class RoundVote2W(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        roundnum = game.currentround
        rejectcount = game.rejectcount
        if rejectcount == roundnum:
            rejectcount = 0
        game.missionselector =  game.playersingame[roundnum%game.maxplayers]
        if game.approvereject == 'reject':
            game.approvereject = ''
            game.selectionvotes.clear()
            game.put()
        if game.submittedselection:
            template_values = {'gameid':gameid, 'round':2, 'user':user, 'game':game}
            template = jinja_environment.get_template('mswait.html')
            self.response.out.write(template.render(template_values))
            return
        if user == game.missionselector:
            if game.maxplayers in [5,6,7]:
                requiredonmission = 3
            if game.maxplayers in [8,9,10]:
                requiredonmission = 4
            template_values = {'gameid':gameid, 'user':user, 'game':game, 'requiredonmission': requiredonmission, 'round':2, 'failselection':False}
            template = jinja_environment.get_template('missionselect.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'gameid':gameid, 'user':user, 'round':2, 'game':game}
        template = jinja_environment.get_template('mswait.html')
        self.response.out.write(template.render(template_values))
    def post(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        playerselected = []
        for player in game.playersingame:
            onmission = self.request.get(player)
            if onmission == 'yes':
                playerselected.append(player)
        if game.maxplayers in [5,6,7]:
            if len(playerselected) != 3:
                template_values = {'gameid':gameid, 'user':user, 'game':game, 'requiredonmission': 3, 'round':2, 'failselection':True}
                template = jinja_environment.get_template('missionselect.html')
                self.response.out.write(template.render(template_values))
                return
        if game.maxplayers in [8,9,10]:
            if len(playerselected) != 4:
                template_values = {'gameid':gameid, 'user':user, 'game':game,'requiredonmission': 4,'round':2, 'failselecton':True}
                template = jinja_environment.get_template('missionselect.html')
                self.response.out.write(template.render(template_values))
                return
        game.pickedonmission = playerselected
        game.submittedselection = True
        roundnum = game.currentround
        roundnum += 1
        rejectcount = game.rejectcount
        rejectcount +=1
        game.currentround = roundnum
        game.rejectcount = rejectcount
        game.put()
        template_values = {'gameid':gameid, 'user':user, 'round':2, 'game':game}
        template = jinja_environment.get_template('missionselectpass.html')
        self.response.out.write(template.render(template_values))

class RoundVote2V(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        if self.request.get('vote'):
            vote = self.request.get('vote')
            if not user in game.selectionvotes:
                game.selectionvotes[user] = vote
                game.put()
                if len(game.selectionvotes) == game.maxplayers:
                    game.playersonmission = game.pickedonmission
                    game.pickedonmission = []
                    game.submittedselection = False
                    tallyapproves = 0
                    for vote in game.selectionvotes:
                        if game.selectionvotes[vote] == 'approve':
                            tallyapproves += 1
                    if tallyapproves > game.maxplayers/2:
                        game.approvereject = 'approve'
                    else:
                        game.approvereject = 'reject'
                        if game.rejectcount == 5:
                            game.roundscores[1] = 'fail'
                    game.put()
            if len(game.selectionvotes) == game.maxplayers:
                template_values = {'gameid':gameid, 'game':game, 'user':user, 'round':2}
                template = jinja_environment.get_template('approverejectresults.html')
                self.response.out.write(template.render(template_values))
                return
            template_values = {'gameid':gameid, 'game':game, 'user':user, 'vote':vote, 'round':2}
            template = jinja_environment.get_template('approverejectwait.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'game':game, 'gameid':gameid, 'user':user, 'round':2}
        template = jinja_environment.get_template('approvereject.html')
        self.response.out.write(template.render(template_values))

class RoundMission2Wait(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        if user in game.playersonmission and user not in game.passfailvotes:
            if self.request.get('passfail'):
                game.passfailvotes[user] = self.request.get('passfail')
                game.put()
                template_values = {'game':game, 'gameid':gameid, 'round':2, 'user':user}
                template = jinja_environment.get_template('missionstandby.html')
                self.response.out.write(template.render(template_values))
                return
            passes = game.roundscores.count('pass')
            fails = game.roundscores.count('fail')
            scores = [passes,fails]
            template_values = {'game':game,'gameid':gameid, 'round':2, 'user':user, "numfails": 'one','scores':scores}
            template = jinja_environment.get_template('onmission.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'game':game,'gameid':gameid, 'round':2 ,'user':user}
        template = jinja_environment.get_template('missionstandby.html')
        self.response.out.write(template.render(template_values))

class RoundMission2Results(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        if game.roundscores[1] == '2':
            tally = 0
            for vote in game.passfailvotes:
                if game.passfailvotes[vote] == 'fail':
                    tally+=1
            if tally > 0:
                game.roundscores[1] = 'fail'
            else:
                game.roundscores[1] = 'pass'
            game.selectionvotes = {}
            game.approvereject = ''
            game.numoffails[1] = tally
            game.passfailvotes = {}
            game.rejectcount = 0
            game.put()
        template_values = {'gameid':gameid, 'game':game, 'round':3,'user':user, 'failvotes':tally}
        template = jinja_environment.get_template('missionresults.html')
        self.response.out.write(template.render(template_values))

#--------------- Round 3 Handlers -----------------------------------
class RoundVote3W(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        roundnum = game.currentround
        rejectcount = game.rejectcount
        game.missionselector =  game.playersingame[roundnum%game.maxplayers]
        if game.approvereject == 'reject':
            game.approvereject = ''
            game.selectionvotes.clear()
            game.put()
        if game.submittedselection:
            template_values = {'gameid':gameid, 'round':3, 'user':user, 'game':game}
            template = jinja_environment.get_template('mswait.html')
            self.response.out.write(template.render(template_values))
            return
        if user == game.missionselector:
            if game.maxplayers == 5:
                requiredonmission = 2
            if game.maxplayers == 7:
                requiredonmission = 3
            if game.maxplayers in [6,8,9,10]:
                requiredonmission = 4
            template_values = {'gameid':gameid, 'user':user, 'game':game, 'round':3, 'requiredonmission': requiredonmission, 'failselection':False}
            template = jinja_environment.get_template('missionselect.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'gameid':gameid, 'user':user, 'round':3, 'game':game}
        template = jinja_environment.get_template('mswait.html')
        self.response.out.write(template.render(template_values))
    def post(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        playerselected = []
        for player in game.playersingame:
            onmission = self.request.get(player)
            if onmission == 'yes':
                playerselected.append(player)
        if game.maxplayers == 5:
            if len(playerselected) != 2:
                template_values = {'gameid':gameid, 'user':user, 'game':game, 'requiredonmission': 2, 'round':3, 'failselection':True}
                template = jinja_environment.get_template('missionselect.html')
                self.response.out.write(template.render(template_values))
                return
        if game.maxplayers == 7:
            if len(playerselected) != 3:
                template_values = {'gameid':gameid, 'user':user, 'game':game, 'requiredonmission': 3, 'round':3, 'failselection':True}
                template = jinja_environment.get_template('missionselect.html')
                self.response.out.write(template.render(template_values))
                return
        if game.maxplayers in [6,8,9,10]:
            if len(playerselected) != 4:
                template_values = {'gameid':gameid, 'user':user, 'game':game,'requiredonmission': 4,'round':3, 'failselecton':True}
                template = jinja_environment.get_template('missionselect.html')
                self.response.out.write(template.render(template_values))
                return
        game.pickedonmission = playerselected
        game.submittedselection = True
        roundnum = game.currentround
        roundnum += 1
        rejectcount = game.rejectcount
        rejectcount +=1
        game.currentround = roundnum
        game.rejectcount = rejectcount
        game.put()
        template_values = {'gameid':gameid, 'user':user, 'round':3, 'game':game}
        template = jinja_environment.get_template('missionselectpass.html')
        self.response.out.write(template.render(template_values))

class RoundVote3V(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        if self.request.get('vote'):
            vote = self.request.get('vote')
            if not user in game.selectionvotes:
                game.selectionvotes[user] = vote
                game.put()
                if len(game.selectionvotes) == game.maxplayers:
                    game.playersonmission = game.pickedonmission
                    game.pickedonmission = []
                    game.submittedselection = False
                    tallyapproves = 0
                    for vote in game.selectionvotes:
                        if game.selectionvotes[vote] == 'approve':
                            tallyapproves += 1
                    if tallyapproves > game.maxplayers/2:
                        game.approvereject = 'approve'
                    else:
                        game.approvereject = 'reject'
                        if game.rejectcount == 5:
                            game.roundscores[2] = 'fail'
                    game.put()
            if len(game.selectionvotes) == game.maxplayers:
                template_values = {'gameid':gameid, 'game':game, 'user':user, 'round':3}
                template = jinja_environment.get_template('approverejectresults.html')
                self.response.out.write(template.render(template_values))
                return
            template_values = {'gameid':gameid, 'game':game, 'user':user, 'vote':vote, 'round':3}
            template = jinja_environment.get_template('approverejectwait.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'game':game, 'gameid':gameid, 'user':user, 'round':3}
        template = jinja_environment.get_template('approvereject.html')
        self.response.out.write(template.render(template_values))

class RoundMission3Wait(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        if user in game.playersonmission and user not in game.passfailvotes:
            if self.request.get('passfail'):
                game.passfailvotes[user] = self.request.get('passfail')
                game.put()
                template_values = {'game':game, 'gameid':gameid, 'round':3, 'user':user}
                template = jinja_environment.get_template('missionstandby.html')
                self.response.out.write(template.render(template_values))
                return
            passes = game.roundscores.count('pass')
            fails = game.roundscores.count('fail')
            scores = [passes,fails]
            template_values = {'game':game,'gameid':gameid, 'round':3, 'user':user, "numfails": 'one','scores':scores}
            template = jinja_environment.get_template('onmission.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'game':game,'gameid':gameid, 'round':3 ,'user':user}
        template = jinja_environment.get_template('missionstandby.html')
        self.response.out.write(template.render(template_values))

class RoundMission3Results(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        if game.roundscores[2] == '3':
            tally = 0
            for vote in game.passfailvotes:
                if game.passfailvotes[vote] == 'fail':
                    tally+=1
            if tally > 0:
                game.roundscores[2] = 'fail'
            else:
                game.roundscores[2] = 'pass'
            game.selectionvotes = {}
            game.approvereject = ''
            game.numoffails[2] = tally
            game.passfailvotes = {}
            game.rejectcount = 0
            game.put()
        # Check if game is over (test to see if one team has won more 3 missions)
        if game.roundscores.count('pass') == 3:
            template_values = {'gameid': gameid,'game':game,'user':user}
            template = jinja_environment.get_template('resistancevictory.html')
            self.response.out.write(template.render(template_values))
            return
        if game.roundscores.count('fail') == 3:
            template_values = {'gameid':gameid,'game':game,'user':user}
            template = jinja_environment.get_template('spyvictory.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'gameid':gameid, 'game':game, 'round':4,'user':user, 'failvotes':tally}
        template = jinja_environment.get_template('missionresults.html')
        self.response.out.write(template.render(template_values))

#--------------- Round 4 Handlers -----------------------------------
class RoundVote4W(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        roundnum = game.currentround
        rejectcount = game.rejectcount
        game.missionselector =  game.playersingame[roundnum%game.maxplayers]
        if game.approvereject == 'reject':
            game.approvereject = ''
            game.selectionvotes.clear()
            game.put()
        if game.submittedselection:
            template_values = {'gameid':gameid, 'round':4, 'user':user, 'game':game}
            template = jinja_environment.get_template('mswait.html')
            self.response.out.write(template.render(template_values))
            return
        if user == game.missionselector:
            if game.maxplayers == 5:
                requiredonmission = 2
            if game.maxplayers == 7:
                requiredonmission = 3
            if game.maxplayers in [6,8,9,10]:
                requiredonmission = 4
            template_values = {'gameid':gameid, 'user':user, 'game':game, 'round':4, 'requiredonmission': requiredonmission, 'failselection':False}
            template = jinja_environment.get_template('missionselect.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'gameid':gameid, 'user':user, 'round':4, 'game':game}
        template = jinja_environment.get_template('mswait.html')
        self.response.out.write(template.render(template_values))
    def post(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        playerselected = []
        for player in game.playersingame:
            onmission = self.request.get(player)
            if onmission == 'yes':
                playerselected.append(player)
        if game.maxplayers in [5,6]:
            if len(playerselected) != 3:
                template_values = {'gameid':gameid, 'user':user, 'game':game, 'requiredonmission': 3, 'round':4, 'failselection':True}
                template = jinja_environment.get_template('missionselect.html')
                self.response.out.write(template.render(template_values))
                return
        if game.maxplayers == 7:
            if len(playerselected) != 4:
                template_values = {'gameid':gameid, 'user':user, 'game':game, 'requiredonmission': 4, 'round':4, 'failselection':True}
                template = jinja_environment.get_template('missionselect.html')
                self.response.out.write(template.render(template_values))
                return
        if game.maxplayers in [8,9,10]:
            if len(playerselected) != 5:
                template_values = {'gameid':gameid, 'user':user, 'game':game,'requiredonmission': 5,'round':4, 'failselecton':True}
                template = jinja_environment.get_template('missionselect.html')
                self.response.out.write(template.render(template_values))
                return
        game.pickedonmission = playerselected
        game.submittedselection = True
        roundnum = game.currentround
        roundnum += 1
        rejectcount = game.rejectcount
        rejectcount +=1
        game.currentround = roundnum
        game.rejectcount = rejectcount
        game.put()
        template_values = {'gameid':gameid, 'user':user, 'round':4, 'game':game}
        template = jinja_environment.get_template('missionselectpass.html')
        self.response.out.write(template.render(template_values))

class RoundVote4V(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        if self.request.get('vote'):
            vote = self.request.get('vote')
            if not user in game.selectionvotes:
                game.selectionvotes[user] = vote
                game.put()
                if len(game.selectionvotes) == game.maxplayers:
                    game.playersonmission = game.pickedonmission
                    game.pickedonmission = []
                    game.submittedselection = False
                    tallyapproves = 0
                    for vote in game.selectionvotes:
                        if game.selectionvotes[vote] == 'approve':
                            tallyapproves += 1
                    if tallyapproves > game.maxplayers/2:
                        game.approvereject = 'approve'
                    else:
                        game.approvereject = 'reject'
                        if game.rejectcount == 5:
                            game.roundscores[3] = 'fail'
                    game.put()
            if len(game.selectionvotes) == game.maxplayers:
                template_values = {'gameid':gameid, 'game':game, 'user':user, 'round':4}
                template = jinja_environment.get_template('approverejectresults.html')
                self.response.out.write(template.render(template_values))
                return
            template_values = {'gameid':gameid, 'game':game, 'user':user, 'vote':vote, 'round':4}
            template = jinja_environment.get_template('approverejectwait.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'game':game, 'gameid':gameid, 'user':user, 'round':4}
        template = jinja_environment.get_template('approvereject.html')
        self.response.out.write(template.render(template_values))

class RoundMission4Wait(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        if user in game.playersonmission and user not in game.passfailvotes:
            if self.request.get('passfail'):
                game.passfailvotes[user] = self.request.get('passfail')
                game.put()
                template_values = {'game':game, 'gameid':gameid, 'round':4, 'user':user}
                template = jinja_environment.get_template('missionstandby.html')
                self.response.out.write(template.render(template_values))
                return
            passes = game.roundscores.count('pass')
            fails = game.roundscores.count('fail')
            scores = [passes,fails]
            template_values = {'game':game,'gameid':gameid, 'round':4, 'user':user, "numfails": 'one','scores':scores}
            template = jinja_environment.get_template('onmission.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'game':game,'gameid':gameid, 'round':4 ,'user':user}
        template = jinja_environment.get_template('missionstandby.html')
        self.response.out.write(template.render(template_values))

class RoundMission4Results(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        if game.roundscores[3] == '4':
            tally = 0
            for vote in game.passfailvotes:
                if game.passfailvotes[vote] == 'fail':
                    tally+=1
            if game.maxplayers in [5,6]:
                if tally > 0:
                    game.roundscores[3] = 'fail'
                else:
                    game.roundscores[3] = 'pass'
            if game.maxplayers in [7,8,9,10]:
                if tally > 1:
                    game.roundscores[3] = 'fail'
                else:
                    game.roundscores[3] = 'pass'
            game.selectionvotes = {}
            game.approvereject = ''
            game.numoffails[3] = tally
            game.passfailvotes = {}
            game.rejectcount = 0
            game.put()
        if game.roundscores.count('pass') == 3:
            template_values = {'gameid': gameid,'game':game,'user':user}
            template = jinja_environment.get_template('resistancevictory.html')
            self.response.out.write(template.render(template_values))
            return
        if game.roundscores.count('fail') == 3:
            template_values = {'gameid':gameid,'game':game,'user':user}
            template = jinja_environment.get_template('spyvictory.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'gameid':gameid, 'game':game, 'round':5,'user':user, 'failvotes':tally}
        template = jinja_environment.get_template('missionresults.html')
        self.response.out.write(template.render(template_values))

#--------------- Round 5 Handlers -----------------------------------
class RoundVote5W(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        roundnum = game.currentround
        rejectcount = game.rejectcount
        game.missionselector =  game.playersingame[roundnum%game.maxplayers]
        if game.approvereject == 'reject':
            game.approvereject = ''
            game.selectionvotes.clear()
            game.put()
        if game.submittedselection:
            template_values = {'gameid':gameid, 'round':5, 'user':user, 'game':game}
            template = jinja_environment.get_template('mswait.html')
            self.response.out.write(template.render(template_values))
            return
        if user == game.missionselector:
            if game.maxplayers == 5:
                requiredonmission = 3
            if game.maxplayers in [6,7]:
                requiredonmission = 4
            if game.maxplayers in [8,9,10]:
                requiredonmission = 5
            template_values = {'gameid':gameid, 'user':user, 'game':game, 'round':5, 'requiredonmission': requiredonmission, 'failselection':False}
            template = jinja_environment.get_template('missionselect.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'gameid':gameid, 'user':user, 'round':5, 'game':game}
        template = jinja_environment.get_template('mswait.html')
        self.response.out.write(template.render(template_values))
    def post(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        playerselected = []
        for player in game.playersingame:
            onmission = self.request.get(player)
            if onmission == 'yes':
                playerselected.append(player)
        if game.maxplayers == 5:
            if len(playerselected) != 3:
                template_values = {'gameid':gameid, 'user':user, 'game':game, 'requiredonmission': 3, 'round':5, 'failselection':True}
                template = jinja_environment.get_template('missionselect.html')
                self.response.out.write(template.render(template_values))
                return
        if game.maxplayers in [6,7]:
            if len(playerselected) != 4:
                template_values = {'gameid':gameid, 'user':user, 'game':game, 'requiredonmission': 4, 'round':5, 'failselection':True}
                template = jinja_environment.get_template('missionselect.html')
                self.response.out.write(template.render(template_values))
                return
        if game.maxplayers in [8,9,10]:
            if len(playerselected) != 5:
                template_values = {'gameid':gameid, 'user':user, 'game':game,'requiredonmission': 5,'round':5, 'failselecton':True}
                template = jinja_environment.get_template('missionselect.html')
                self.response.out.write(template.render(template_values))
                return
        game.pickedonmission = playerselected
        game.submittedselection = True
        roundnum = game.currentround
        roundnum += 1
        rejectcount = game.rejectcount
        rejectcount +=1
        game.currentround = roundnum
        game.rejectcount = rejectcount
        game.put()
        template_values = {'gameid':gameid, 'user':user, 'round':5, 'game':game}
        template = jinja_environment.get_template('missionselectpass.html')
        self.response.out.write(template.render(template_values))

class RoundVote5V(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        if self.request.get('vote'):
            vote = self.request.get('vote')
            if not user in game.selectionvotes:
                game.selectionvotes[user] = vote
                game.put()
                if len(game.selectionvotes) == game.maxplayers:
                    game.playersonmission = game.pickedonmission
                    game.pickedonmission = []
                    game.submittedselection = False
                    tallyapproves = 0
                    for vote in game.selectionvotes:
                        if game.selectionvotes[vote] == 'approve':
                            tallyapproves += 1
                    if tallyapproves > game.maxplayers/2:
                        game.approvereject = 'approve'
                    else:
                        game.approvereject = 'reject'
                        if game.rejectcount == 5:
                            game.roundscores[4] = 'fail'
                    game.put()
            if len(game.selectionvotes) == game.maxplayers:
                template_values = {'gameid':gameid, 'game':game, 'user':user, 'round':5}
                template = jinja_environment.get_template('approverejectresults.html')
                self.response.out.write(template.render(template_values))
                return
            template_values = {'gameid':gameid, 'game':game, 'user':user, 'vote':vote, 'round':5}
            template = jinja_environment.get_template('approverejectwait.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'game':game, 'gameid':gameid, 'user':user, 'round':5}
        template = jinja_environment.get_template('approvereject.html')
        self.response.out.write(template.render(template_values))

class RoundMission5Wait(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        if user in game.playersonmission and user not in game.passfailvotes:
            if self.request.get('passfail'):
                game.passfailvotes[user] = self.request.get('passfail')
                game.put()
                template_values = {'game':game, 'gameid':gameid, 'round':5, 'user':user}
                template = jinja_environment.get_template('missionstandby.html')
                self.response.out.write(template.render(template_values))
                return
            passes = game.roundscores.count('pass')
            fails = game.roundscores.count('fail')
            scores = [passes,fails]
            template_values = {'game':game,'gameid':gameid, 'round':5, 'user':user, "numfails": 'one','scores':scores}
            template = jinja_environment.get_template('onmission.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'game':game,'gameid':gameid, 'round':5 ,'user':user}
        template = jinja_environment.get_template('missionstandby.html')
        self.response.out.write(template.render(template_values))

class RoundMission5Results(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        if game.roundscores[4] == '5':
            tally = 0
            for vote in game.passfailvotes:
                if game.passfailvotes[vote] == 'fail':
                    tally+=1
            if tally > 0:
                game.roundscores[4] = 'fail'
            else:
                game.roundscores[4] = 'pass'
            game.selectionvotes = {}
            game.approvereject = ''
            game.numoffails[4] = tally
            game.passfailvotes = {}
            game.rejectcount = 0
            game.put()
        if game.roundscores.count('pass') == 3:
            template_values = {'gameid': gameid,'game':game,'user':user}
            template = jinja_environment.get_template('resistancevictory.html')
            self.response.out.write(template.render(template_values))
            return
        if game.roundscores.count('fail') == 3:
            template_values = {'gameid':gameid,'game':game,'user':user}
            template = jinja_environment.get_template('spyvictory.html')
            self.response.out.write(template.render(template_values))
            return
        template_values = {'gameid':gameid, 'game':game, 'round':6,'user':user, 'failvotes':tally}
        template = jinja_environment.get_template('missionresults.html')
        self.response.out.write(template.render(template_values))

#--------------- Back Up Handler -----------------------------------
# If after all 5 five rounds no team won, redirect to this page to which will
# then return to the game list page and delete this current game
class RoundVote6W(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        template_values = {'gameid':gameid, 'game':game,'user':user}
        template = jinja_environment.get_template('somethingwrong.html')
        self.response.out.write(template.render(template_values))

# Called upon when Resistance wins 3 missions
class AssasinVictory(webapp2.RequestHandler):
    def get(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        # check if current player's role is Assasin
        template_values = {'gameid':gameid, 'game':game, 'user':user}
        if game.playerroles[user] == 'Assasin':
            template = jinja_environment.get_template('assasinselection.html')
            self.response.out.write(template.render(template_values))
            return
        template = jinja_environment.get_template('assasinwait.html')
        self.response.out.write(template.render(template_values))
    def post(self):
        gameid = self.request.get('id')
        user = self.request.get('user')
        game = Game.get_by_id(int(gameid))
        assasination = self.request.get('kill')
        # Check if Assasin correctly selected Merlin or not
        if game.playerroles[assasination] == "Merlin":
            game.roundscores[5] = 'Killed'
        else:
            game.roundscores[5] = 'Failed'
        game.put()
        template_values = {'gameid':gameid, 'game':game, 'user':user}
        template = jinja_environment.get_template('assasinwait.html')
        self.response.out.write(template.render(template_values))

#---------------- Instructions -------------------------------------
class Instructions(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template('instructions.html')
        self.response.out.write(template.render(template_values))

# -----------------------------------------------------------
# ------------------ Handler Redirects ----------------------
# -----------------------------------------------------------
app = webapp2.WSGIApplication([
    ('/', Landing),
    ('/creategame', CreateGame),
    ('/gamlobby', GameLobby),
    ('/gamerv1w', RoundVote1W),
    ('/gamerv1v', RoundVote1V),
    ('/gamerm1w', RoundMission1Wait),
    ('/gamerm1r', RoundMission1Results),
    ('/gamerv2w', RoundVote2W),
    ('/gamerv2v', RoundVote2V),
    ('/gamerm2w', RoundMission2Wait),
    ('/gamerm2r', RoundMission2Results),
    ('/gamerv3w', RoundVote3W),
    ('/gamerv3v', RoundVote3V),
    ('/gamerm3w', RoundMission3Wait),
    ('/gamerm3r', RoundMission3Results),
    ('/gamerv4w', RoundVote4W),
    ('/gamerv4v', RoundVote4V),
    ('/gamerm4w', RoundMission4Wait),
    ('/gamerm4r', RoundMission4Results),
    ('/gamerv5w', RoundVote5W),
    ('/gamerv5v', RoundVote5V),
    ('/gamerm5w', RoundMission5Wait),
    ('/gamerm5r', RoundMission5Results),
    ('/gamerv6w', RoundVote6W),
    ('/gameassasin', AssasinVictory),
    ('/instructions', Instructions),
], debug=True)