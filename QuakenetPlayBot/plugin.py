###
# Copyright (c) 2021-2023, Russell Beech
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import operator
import time
import pickle
import os
import sys
import re 
import math
import socket
import supybot.utils as utils
import supybot.world as world
from supybot.commands import *
import supybot.irclib as irclib
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.schedule as schedule
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
import supybot.conf as conf
import supybot.ircdb as ircdb

if sys.version_info[0] >= 3:
        import urllib.error
        import urllib.request
        import http.client
        python3 = True
if sys.version_info[0] < 3:
        import urllib2
        import httplib
        python3 = False

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('QuakenetPlayBot')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

__module_name__ = "Quakenet #IdleRPG Playbot Script"
__module_version__ = "1.5"
__module_description__ = "Quakenet #IdleRPG Playbot Script"

# build hardcoded monster/creep lists, reverse
creeps = [      ["Roach",       1500],   \
                ["Spider",      2500],  \
                ["Bat",         3500],  \
                ["Wolf",        4500],  \
                ["Goblin",      5500],  \
                ["Shadow",      6500],  \
                ["Lich",        7500],  \
                ["Skeleton",    8500],  \
                ["Ghost",       9500],  \
                ["Phantom",     10500],  \
                ["Troll",       12500], \
                ["Cyclop",      14500],  \
                ["Mutant",      17500], \
                ["Ogre",        21500],  \
                ["Phoenix",     25500],  \
                ["Demon",       30500], \
                ["Centaur",     35500], \
                ["Werewolf",    40500], \
                ["Giant",       9999999]  ]

monsters = [    ["Blue_Dragon",         8500],  \
                ["Yellow_Dragon",       16000],  \
                ["Green_Dragon",        26000], \
                ["Red_Dragon",          36000], \
                ["Black_Dragon",        41000], \
                ["White_Dragon",        61000], \
                ["Bronze_Dragon",       81000], \
                ["Silver_Dragon",       101000], \
                ["Gold_Dragon",         151000], \
                ["Platinum_Dragon",     9999999]  ]

creeps.reverse()
monsters.reverse()

russweb = "https://russellb.000webhostapp.com/"
gitweb = "https://github.com/RussellBeech/supybot-plugins"
playerview = None 
interval = 300
newlist = None
playerlist = None 
playerspage = None
playerspagelist = None
currentversion = __module_version__
currentversion = float( currentversion )

# Changeable settings
website = "https://quakeirpg.abandoned-irc.net"
setbuy = 15 # level to start buying items from
goldsave = 3100 # gold kept in hand
buylife = True
blackbuyspend = True
blackbuyspend14 = True
getgems = True
fightmode = True
channame = "#idlerpg"
setbotname = "IdleRPG"
creepattack = True # True = On, False = Off - Autocreep selection
setcreeptarget = "Werewolf" # Sets creep target. creepattack needs to be False to use
scrollssum = 3000 # Itemscore you start buying scrolls at
xpupgrade = True # Upgrade Items with XP
xpspend = 20 # Amount you use with xpget to upgrade items
bottextmode = True # True = on, False = off
errortextmode = True # True = on, False = off
pmtextmode = True # True = on, False = off
intervaltext = True # True = on, False = off - Text displayed every interval
townworkswitch = True # True = Town/Work Area Switching, False = Town/Forest Area Switching
autoconfig = 1 # 0 = off, 1 = on, 2 = remove config changes.
expbuy = False
slaysum = 1000 # minimum sum you start slaying without mana from
loginsettingslist = True # True = on, False = off - Settings List at start

# declare stats as global
name = None
pswd = None
botname = setbotname
charcount = 0
level = 0
mysum = 0
itemSum = 0
expertSum = 0
attackslaySum = 0
ufightcalc = 0
gold = 0
rank = 0

ttl = 0
atime = 0 # regentm
stime = 0 # slaytm

amulet = 0
charm = 0
helm = 0
boots = 0
gloves = 0
ring = 0
leggings = 0
shield = 0
tunic = 0
weapon = 0

fights = 0
scrolls = 0
exp = 0
mana = 0
stone1 = None
stone2 = None
stone3 = None
expert1 = None
expert2 = None
expert3 = None
expertitem1 = 0
expertitem2 = 0
expertitem3 = 0
gems = 0
ability = None
xp = 0
life = 0
align = "n"
upgradelevel = 0

nickname = None
netname = None
offline = None
botcheck = None
webworks = None
gameactive = None
lottonum1 = None
lottonum2 = None
lottonum3 = None
location = None
locationtime = 0

otherIrc = None
supynick = None
botdisable1 = False
playbotcount = 0
playbottext = None
playbotid = "QS"
pbcount = 0

quake = False
quakemulti = False

fileprefix = "QuakenetPlayBotconfig.txt"
path = conf.supybot.directories.data
filename = path.dirize(fileprefix)
try:
        f = open(filename,"rb")
        configList = pickle.load(f)
        f.close()
except:
        configList = []
fileprefix3 = "quakesingleplayers.txt"
path = conf.supybot.directories.data
filename3 = path.dirize(fileprefix3)
fileprefix4 = "quakemultiplayers.txt"
path = conf.supybot.directories.data
filename4 = path.dirize(fileprefix4)

for entry in configList:
        if(entry[0] == "blackbuyspend"):
                blackbuyspend = entry[1]
        if(entry[0] == "blackbuyspend14"):
                blackbuyspend14 = entry[1]
        if(entry[0] == "bottextmode"):
                bottextmode = entry[1]
        if(entry[0] == "buylife"):
                buylife = entry[1]
        if(entry[0] == "creepattack"):
                creepattack = entry[1]
        if(entry[0] == "errortextmode"):
                errortextmode = entry[1]
        if(entry[0] == "expbuy"):
                expbuy = entry[1]
        if(entry[0] == "fightmode"):
                fightmode = entry[1]
        if(entry[0] == "getgems"):
                getgems = entry[1]
        if(entry[0] == "goldsave"):
                goldsave = entry[1]
        if(entry[0] == "intervaltext"):
                intervaltext = entry[1]
        if(entry[0] == "pmtextmode"):
                pmtextmode = entry[1]
        if(entry[0] == "scrollssum"):
                scrollssum = entry[1]
        if(entry[0] == "setbuy"):
                setbuy = entry[1]
        if(entry[0] == "setcreeptarget"):
                setcreeptarget = entry[1]
        if(entry[0] == "slaysum"):
                slaysum = entry[1]
        if(entry[0] == "townworkswitch"):
                townworkswitch = entry[1]
        if(entry[0] == "xpspend"):
                xpspend = entry[1]
        if(entry[0] == "xpupgrade"):
                xpupgrade = entry[1]

class QuakenetPlayBot(callbacks.Plugin):
    """Quakenet PlayBot #Idlerpg"""
    threaded = True

    def _getIrc(self, network):
        irc = world.getIrc(network)
        if irc:
            return irc
        else:
            raise NameError('I\'m not currently connected to %s.' % network)

    def versionchecker(self, irc):
        global currentversion
        global python3
        global russweb
        global gitweb

        webversion = None
        try:
                if python3 is False:
                        text = urllib2.urlopen(russweb + "playbotversionquakesupy.txt")
                if python3 is True:
                        text = urllib.request.urlopen(russweb + "playbotversionquakesupy.txt")
                webversion = text.read()
                webversion = float( webversion )
                text.close()

        except:
                self.reply(irc, "Could not access {0}".format(russweb))

        self.reply(irc, "Current version {0}".format(currentversion))
        self.reply(irc, "Web version {0}".format(webversion))
        if webversion != None:
                if(currentversion == webversion):
                    self.reply(irc, "You have the current version of PlayBot")
                if(currentversion < webversion):
                    self.reply(irc, "You have an old version of PlayBot")
                    self.reply(irc, "You can download a new version from {0} or {1}".format(russweb, gitweb))
                if(currentversion > webversion):
                    self.reply(irc, "Give me, Give me")

    def configwrite(self):
        global blackbuyspend
        global blackbuyspend14
        global buylife
        global creepattack
        global expbuy
        global fightmode
        global getgems
        global goldsave
        global intervaltext
        global scrollssum
        global setbuy
        global setcreeptarget
        global slaysum
        global townworkswitch
        global xpspend
        global xpupgrade
        global bottextmode
        global errortextmode
        global pmtextmode

        configList = []
        configList.append( ( "blackbuyspend", blackbuyspend ) )
        configList.append( ( "blackbuyspend14", blackbuyspend14 ) )
        configList.append( ( "bottextmode", bottextmode ) )
        configList.append( ( "buylife", buylife ) )
        configList.append( ( "creepattack", creepattack ) )
        configList.append( ( "errortextmode", errortextmode ) )
        configList.append( ( "expbuy", expbuy ) )
        configList.append( ( "fightmode", fightmode ) )
        configList.append( ( "getgems", getgems ) )
        configList.append( ( "goldsave", goldsave ) )
        configList.append( ( "intervaltext", intervaltext ) )
        configList.append( ( "pmtextmode", pmtextmode ) )
        configList.append( ( "scrollssum", scrollssum ) )
        configList.append( ( "setbuy", setbuy ) )
        configList.append( ( "setcreeptarget", setcreeptarget ) )
        configList.append( ( "slaysum", slaysum ) )
        configList.append( ( "townworkswitch", townworkswitch ) )
        configList.append( ( "xpspend", xpspend ) )
        configList.append( ( "xpupgrade", xpupgrade ) )
        f = open(filename,"wb")
        pickle.dump(configList,f)
        f.close()

    def eraseconfig(self, irc, msg, args):
        """takes no arguments

        Erases config file
        """
        configList = []
        f = open(filename,"wb")
        pickle.dump(configList,f)
        f.close()
        irc.reply("Config Erased", private=True)
    eraseconfig = wrap(eraseconfig, [("checkCapability", "admin")])

    def setoption(self, irc, msg, args, text, value):
        """<option> <value>
        
        Changes a setting in PlayBot.  You can view the 
        current PlayBot settings with the "settings" command."""
        global goldsave
        global fightmode
        global getgems
        global buylife
        global setbuy
        global scrollssum
        global xpupgrade
        global xpspend
        global creepattack
        global blackbuyspend
        global blackbuyspend14
        global setcreeptarget
        global creeps
        global townworkswitch
        global intervaltext
        global expbuy
        global gameactive
        global slaysum
        global bottextmode
        global errortextmode
        global pmtextmode
        
        if value.lower()=='true':
            value=True
        elif value.lower()=='false':
            value=False

        if gameactive is True:
        ##      Sets creep target in manual selection mode
                if text == "creep":
                        testsetcreeptarget = value
                        creepcheck = False
                        for entry in creeps:
                                if testsetcreeptarget == entry[0]:
                                        creepcheck = True
                        if creepcheck is True:
                                setcreeptarget = testsetcreeptarget
                                irc.reply("Creep changed to {0}".format(setcreeptarget), private=True)
                        if creepcheck is False:
                                irc.reply("Creep is not on the creep list", private=True)
        ##      Sets how much gold you keep in hand
                if text == "goldsave":
                        if str.isdigit(value):
                                goldsave = int( value )
                        irc.reply("Goldsave changed to {0}".format(goldsave), private=True)
        ##      Sets at which level you will buy your engineer from
                if text == "scrollssum":
                        if str.isdigit(value):
                                scrollssum = int( value )
                        irc.reply("scrollssum Buy Level changed to {0}".format(scrollssum), private=True)
        ##      Sets at which level you will start buying items from
                if text == "itembuy":
                        if str.isdigit(value):
                                setbuy = int( value )
                        irc.reply("Item Buy Level changed to {0}".format(setbuy), private=True)
        ##      Sets the Itemscore at which you start slaying dragons
                if text == "slaysum":
                        if str.isdigit(value):
                                slaysum = int( value )
                        irc.reply("SlaySum Minimum ItemScore changed to {0}".format(slaysum), private=True)
        ##      Sets how much you spend with xpget when upgrading items
                if text == "xpspend":
                        if str.isdigit(value):
                                testxpspend = int( value )
                                if testxpspend >= 20:
                                        xpspend = testxpspend
                                        irc.reply("XPSpend for Item Upgrade changed to {0}".format(xpspend), private=True)
                                if testxpspend < 20:
                                        irc.reply("XPSpend needs to be 20 or over", private=True)
                if text == "xpupgrade":
        ##              Turns on upgrading items with XP
                        if value is True:
                                xpupgrade = True
                                irc.reply("XPUpgrade Mode Activated.  To turn it off use 'setoption xpupgrade false' command", private=True)
        ##              Turns off upgrading items with XP
                        if value is False:
                                xpupgrade = False
                                irc.reply("XPUpgrade Mode Deactivated.  To turn it back on use 'setoption xpupgrade true' command", private=True)
                if text == "creepattack":
        ##              Turns on Auto CreepAttack selection
                        if value is True:
                                creepattack = True
                                irc.reply("CreepAttack Auto Mode Activated.  To turn it off use 'setoption creepattack false' command", private=True)
        ##              Turns off Auto CreepAttack selection.  To set creep target use 'setoption creep creepname'
                        if value is False:
                                creepattack = False
                                irc.reply("CreepAttack Auto Mode Deactivated.  To turn it back on use 'setoption creepattack true' command", private=True)
                if text == "getgems":
        ##              Turns on buying gems
                        if value is True:
                                getgems = True
                                irc.reply("GetGems Mode Activated.  To turn it off use 'setoption getgems false' command", private=True)
        ##              Turns off buying gems
                        if value is False:
                                getgems = False
                                irc.reply("GetGems Mode Deactivated.  To turn it back on use 'setoption getgems true' command", private=True)
                if text == "blackbuy":
        ##              Turns on blackbuy upgrading of items
                        if value is True:
                                blackbuyspend = True
                                irc.reply("BlackBuy Spend Mode Activated.  To turn it off use 'setoption blackbuy false' command", private=True)
        ##              Turns off blackbuy upgrading of items
                        if value is False:
                                blackbuyspend = False
                                irc.reply("BlackBuy Spend Mode Deactivated.  To turn it back on use 'setoption blackbuy true' command", private=True)
                if text == "blackbuy14":
        ##              Turns on blackbuy 14 upgrading of items
                        if value is True:
                                blackbuyspend14 = True
                                irc.reply("BlackBuy Spend Mode 14 Activated.  To turn it off use 'setoption blackbuy14 false' command", private=True)
        ##              Turns off blackbuy 14 upgrading of items
                        if value is False:
                                blackbuyspend14 = False
                                irc.reply("BlackBuy Spend Mode 14 Deactivated.  To turn it back on use 'setoption blackbuy14 true' command", private=True)
                if text == "buylife":
        ##              Turns on auto buylife
                        if value is True:
                                buylife = True
                                irc.reply("BuyLife Mode Activated.  To turn it off use 'setoption buylife false' command", private=True)
        ##              Turns off auto buylife
                        if value is False:
                                buylife = False
                                irc.reply("BuyLife Mode Deactivated.  To turn it back on use 'setoption buylife true' command", private=True)
                if text == "fights":
        ##              Turns on auto fighting 
                        if value is True:
                                fightmode = True
                                irc.reply("Fights Mode On.  To turn it back off use 'setoption fights false' command", private=True)
        ##              Turns off auto fighting
                        if value is False:
                                fightmode = False
                                irc.reply("Fights Mode Off.  To turn it back on use 'setoption fights true' command", private=True)
                if text == "townwork":
        ##              Change player area switching to town/work
                        if value is True:
                                townworkswitch = True
                                irc.reply("Town/Work Switch Mode Activated.  To change to Town/Forest use 'setoption townwork false' command", private=True)
        ##              Change player area switching to town/forest
                        if value is False:
                                townworkswitch = False
                                irc.reply("Town/Forest Switch Mode Activated.  To change to Town/Work use 'setoption townwork true' command", private=True)
                if text == "townforest":
        ##              Change player area switching to town/forest
                        if value is True:
                                townworkswitch = False
                                irc.reply("Town/Forest Switch Mode Activated.  To change to Town/Work use 'setoption townforest false' command", private=True)
        ##              Change player area switching to town/work
                        if value is False:
                                townworkswitch = True
                                irc.reply("Town/Work Switch Mode Activated.  To change to Town/Forest use 'setoption townforest true' command", private=True)
                if text == "intervaltext":
        ##              Turns Interval Messages on
                        if value is True:
                                intervaltext = True
                                irc.reply("Interval Text Mode On.  To turn it back off use 'setoption intervaltext false' command", private=True)
        ##              Turns Interval Messages off
                        if value is False:
                                intervaltext = False
                                irc.reply("Interval Text Mode Off.  To turn it back on use 'setoption intervaltext true' command", private=True)
                if text == "expbuy":
        ##              Turns on Experience Buying
                        if value is True:
                                expbuy = True
                                irc.reply("Experience Buying Mode Activated.  To turn it back off use 'setoption expbuy false' command", private=True)
        ##              Turns off Experience Buying
                        if value is False:
                                expbuy = False
                                irc.reply("Experience Buying Mode Deactivated.  To turn it back on use 'setoption expbuy true' command", private=True)
                if text == "bottext":
        ##              Turns Bot Messages on
                        if value is True:
                                bottextmode = True
                                irc.reply("Bot Text Mode On.  To turn it back off use 'setoption bottextmode false' command", private=True)
        ##              Turns Bot Messages off
                        if value is False:
                                bottextmode = False
                                irc.reply("Bot Text Mode Off.  To turn it back on use 'setoption bottextmode true' command", private=True)
                if text == "errortext":
        ##              Turns Error Messages on
                        if value is True:
                                errortextmode = True
                                irc.reply("Error Text Mode On.  To turn it back off use 'setoption errortext false' command", private=True)
        ##              Turns Error Messages off
                        if value is False:
                                errortextmode = False
                                irc.reply("Error Text Mode Off.  To turn it back on use 'setoption errortext true' command", private=True)
                if text == "pmtext":
        ##              Turns PMs from GameBot on
                        if value is True:
                                pmtextmode = True
                                irc.reply("Turns PMs from GameBot on.  To turn it back off use 'setoption pmtext false' command", private=True)
        ##              Turns PMs from GameBot off
                        if value is False:
                                pmtextmode = False
                                irc.reply("Turns PMs from GameBot off.  To turn it back on use 'setoption pmtext true' command", private=True)

                self.configwrite()
        if gameactive is False:
            irc.error("You are not logged in")

    setoption = wrap(setoption, [('checkCapability', 'admin'), 'something', 'something'])

    def bottester(self, irc):
        global otherIrc
        global botname
        global channame
        global botdisable1
        global setbotname
        
        botcount1 = 0
        botname = setbotname

        bottest = botname
        botentry = []

        try:
                ops = otherIrc.state.channels[channame].ops

                for user in ops:
                        if bottest in user and user != bottest:
                                botentry.append(user)
                                botname10 = user

        except KeyError:
            self.reply(irc, "Key Error")

        botcount1 = len(botentry)
        if botcount1 == 1:
                botname = botname10
        if botcount1 >= 2:
                botdisable1 = True

    def usecommand(self, irc, commanded):
        global botname
        global otherIrc
        global botdisable1
        
        self.bottester(irc)
        if(botdisable1 is False):
                otherIrc.queueMsg(ircmsgs.privmsg(botname, commanded))

    def reply(self, irc, text):
        global nickname
        global channame
        global otherIrc
        global supynick
        
        nickcheck = False
        try:
            chanstate = otherIrc.state.channels[channame]
            users = [user for user in chanstate.users]
            for entry in users:
                if nickname == entry:
                    nickcheck = True
        except KeyError:
            return

        if(nickcheck is True and nickname != supynick):
                otherIrc.queueMsg(ircmsgs.privmsg(nickname, text))
            
    def playbotcheck(self, irc):
        global playbotcount
        global playbottext
        global playbotid
        global pbcount
        global quake
        global quakemulti

        playbotcount = 0
        pbcount = 0
        quakeon = True
        quakemultion = True
        multigameon = True
        multigamemultion = True
        multigamemultimultion = True
        playbotsingleon = True
        playbotmultion = True
        quake = False
        quakemulti = False
        multigame = False
        multigamemulti = False
        multigamemultimulti = False
        playbotsingle = False
        playbotmulti = False
        
        try:
                quakecheck = conf.supybot.plugins.get("QuakenetPlayBot")
        except:
                quakeon = False
        try:
                quakemulticheck = conf.supybot.plugins.get("QuakenetPlayBotMulti")
        except:
                quakemultion = False
        try:
                multigamecheck = conf.supybot.plugins.get("MultiGamePlayBot")
        except:
                multigameon = False
        try:
                multigamemulticheck = conf.supybot.plugins.get("MultiGamePlayBotMulti")
        except:
                multigamemultion = False
        try:
                multigamemultimulticheck = conf.supybot.plugins.get("MultiGamePlayBotMultiMulti")
        except:
                multigamemultimultion = False
        try:
                playbotsinglecheck = conf.supybot.plugins.get("PlayBotSingle")
        except:
                playbotsingleon = False
        try:
                playbotmulticheck = conf.supybot.plugins.get("PlayBotMulti")
        except:
                playbotmultion = False

        if quakeon is True:
                quake = conf.supybot.plugins.QuakenetPlayBot()
                if quake is True:
                        playbotcount += 1
                        pbcount += 1

        if quakemultion is True:
                quakemulti = conf.supybot.plugins.QuakenetPlayBotMulti()
                if quakemulti is True:
                        playbotcount += 1
                        pbcount += 1

        if multigameon is True:
                multigame = conf.supybot.plugins.MultiGamePlayBot()
                if multigame is True:
                        playbotcount += 1

        if multigamemultion is True:
                multigamemulti = conf.supybot.plugins.MultiGamePlayBotMulti()
                if multigamemulti is True:
                        playbotcount += 1

        if multigamemultimultion is True:
                multigamemultimulti = conf.supybot.plugins.MultiGamePlayBotMultiMulti()       
                if multigamemultimulti is True:
                        playbotcount += 1
        if playbotsingleon is True:
                playbotsingle = conf.supybot.plugins.PlayBotSingle()       
                if playbotsingle is True:
                        playbotcount += 1
        if playbotmultion is True:
                playbotmulti = conf.supybot.plugins.PlayBotMulti()       
                if playbotmulti is True:
                        playbotcount += 1

        if playbotcount == 1:
                playbottext = ""
        if playbotcount >= 2:
                playbottext = playbotid
            
    def login(self, irc, msg, args, arg2):
        """<charname> <password>

        Log into Game.
        """
        global name
        global pswd
        global setbuy
        global buylife
        global netname
        global nickname
        global gameactive
        global fightmode
        global charcount
        global otherIrc
        global supynick
        global blackbuyspend
        global blackbuyspend14
        global getgems
        global scrollssum
        global xpupgrade
        global xpspend
        global intervaltext
        global townworkswitch
        global goldsave
        global creepattack
        global expbuy
        global playerspagelist
        global webworks
        global channame
        global slaysum
        global pbcount
        global loginsettingslist
        global bottextmode
        global errortextmode
        global pmtextmode

        charcount += 1
        if charcount == 1:
                gameactive = True
                nickname = msg.nick
                netname = self._getIrcName(irc)
                supynick = irc.nick
                otherIrc = self._getIrc(netname)
                namecheck = False

                if "undernet" in netname and channame.lower() == "#irpg":
                        irc.error("The #irpg game on Undernet is not supported.  Expect your head to explode if you continue")
                self.playbotcheck(irc)
                args2 = arg2.split(" ")

                try:
                        if(name is None or pswd is None):
                                name = args2[0]
                                pswd = args2[1]
                except IndexError:
                        irc.error("To log in use <bot> quakenetplaybot login CharName Password" )
                        
                self.webdata(irc)
                if(name is None or pswd is None):
                        charcount = 0
                        irc.error("Login Failed")
                if charcount == 1:
                        try:
                                for entry in playerspagelist:
                                        if ">{0}<".format(name) in entry:
                                                namecheck = True
                        except TypeError:
                                webworks = False
                        if(namecheck is False and webworks is True):
                                irc.error("LOGIN ERROR: {0} does not exist".format(name))
                                charcount = 0

                if charcount == 1:
                        if pbcount == 2:
                                multiplayerlist = self.multiread(irc)
                                count = 0
                                multiname = None
                                multiname2 = None
                                multiname3 = None
                                multiname4 = None
                                multinetname = None
                                multinetname2 = None
                                multinetname3 = None
                                multinetname4 = None
                                for entry in multiplayerlist:
                                        count += 1
                                        if count == 1:
                                                multiname = entry[1]
                                                multinetname = entry[3]
                                        if count == 2:
                                                multiname2 = entry[1]
                                                multinetname2 = entry[3]
                                        if count == 3:
                                                multiname3 = entry[1]
                                                multinetname3 = entry[3]
                                        if count == 4:
                                                multiname4 = entry[1]
                                                multinetname4 = entry[3]
                                if(name == multiname or name == multiname2 or name == multiname3 or name == multiname4):
                                        irc.error("Character {0} is already logged in on QuakenetPlayBotMulti".format(name))
                                        charcount = 0
                                if(netname == multinetname):
                                        irc.error("Character {0} is already logged in on QuakenetPlayBotMulti".format(multiname))
                                        charcount = 0
                                if(netname == multinetname2):
                                        irc.error("Character {0} is already logged in on QuakenetPlayBotMulti".format(multiname2))
                                        charcount = 0
                                if(netname == multinetname3):
                                        irc.error("Character {0} is already logged in on QuakenetPlayBotMulti".format(multiname3))
                                        charcount = 0
                                if(netname == multinetname4):
                                        irc.error("Character {0} is already logged in on QuakenetPlayBotMulti".format(multiname4))
                                        charcount = 0

                if charcount == 0:
                        gameactive = False
                        name = None
                        pswd = None

                if charcount == 1:
                        if(name != None and pswd != None):
                                self.usecommand(irc, "login {0} {1}".format(name, pswd) )

        if charcount == 1:
                time.sleep(3) # Needed
                self.usecommand(irc, "whoami")
                irc.reply("Player Character {0} has logged in".format(name), private=True)
        if charcount == 1 and loginsettingslist is True:
                if blackbuyspend is True:
                        irc.reply("BlackBuy Spend Mode Activated.  To turn it off use 'setoption blackbuy false' command", private=True)
                if blackbuyspend is False:
                        irc.reply("BlackBuy Spend Mode Deactivated.  To turn it off use 'setoption blackbuy true' command", private=True)
                if blackbuyspend14 is True:
                        irc.reply("BlackBuy Spend 14 Mode Activated.  To turn it off use 'setoption blackbuy14 false' command", private=True)
                if blackbuyspend14 is False:
                        irc.reply("BlackBuy Spend 14 Mode Deactivated.  To turn it off use 'setoption blackbuy14 true' command", private=True)
                if bottextmode is True:
                        irc.reply("Bot Text Mode Activated.  To turn it off use 'setoption bottext false' command", private=True)
                if buylife is True:
                        irc.reply("Buy Life Mode Activated.  To turn it off use 'setoption buylife false' command", private=True)
                if buylife is False:
                        irc.reply("Buy Life Mode Deactivated.  To turn it on use 'setoption buylife true' command", private=True)
                if creepattack is True:
                        irc.reply("CreepAttack Mode Activated.  To turn it off use 'setoption creepattack false' command", private=True)
                if creepattack is False:
                        irc.reply("CreepAttack Mode Deactivated.  To turn it on use 'setoption creepattack true' command", private=True)
                if errortextmode is True:
                        irc.reply("Error Text Mode Activated.  To turn it off use 'setoption errortext false' command", private=True)
                if expbuy is True:
                        irc.reply("Experience Buying Mode Activated.  To turn it off use 'setoption expbuy false' command", private=True)
                if expbuy is False:
                        irc.reply("Experience Buying Mode Deactivated.  To turn it on use 'setoption expbuy true' command", private=True)
                if fightmode is True:
                        irc.reply("Fighting Mode Activated.  To turn it off use 'setoption fights false' command", private=True)
                if fightmode is False:
                        irc.reply("Fighting Mode Deactivated.  To turn it on use 'setoption fights true' command", private=True)
                if getgems is True:
                        irc.reply("GetGems Mode Activated.  To turn it off use 'setoption getgems false' command", private=True)
                if getgems is False:
                        irc.reply("GetGems Mode Deactivated.  To turn it on use 'setoption getgems true' command", private=True)
                if intervaltext is True:
                        irc.reply("Interval Text Mode Activated.  To turn it off use 'setoption intervaltext false' command", private=True)
                if pmtextmode is True:
                        irc.reply("PMs from GameBot Mode Activated.  To turn it off use 'setoption pmtext false' command", private=True)
                if townworkswitch is True:
                        irc.reply("Town/Work Switch Mode Activated.  To change to Town/Forest use 'setoption townforest true' command", private=True)
                if townworkswitch is False:
                        irc.reply("Town/Forest Switch Mode Activated.  To change to Town/Work use 'setoption townwork true' command", private=True)
                if xpupgrade is True:
                        irc.reply("XPUpgrade Mode Activated.  To turn it off use 'setoption xpupgrade false' command", private=True)
                if xpupgrade is False:
                        irc.reply("XPUpgrade Mode Deactivated.  To turn it on use 'setoption xpupgrade true' command", private=True)
                irc.reply("Current Goldsave: {0}.  If you want to change it use 'setoption goldsave number' command".format(goldsave), private=True)
                irc.reply("Current Item Buy Level: {0}.  If you want to change it use 'setoption itembuy number' command".format(setbuy), private=True)
                irc.reply("Current Scrolls Buy ItemScore: {0}.  If you want to change it use 'setoption scrollssum number' command".format(scrollssum), private=True)
                irc.reply("Current SlaySum Minimum ItemScore: {0}.  If you want to change it use 'setoption slaysum number' command".format(slaysum), private=True)
                irc.reply("Current XPSpend for xpget item upgrades: {0}.  If you want to change it use 'setoption xpspend number' command".format(xpspend), private=True)
                irc.reply(" ", private=True)
                irc.reply("For a list of PlayBot commands use <bot> quakenetplaybot help", private=True)
                irc.reply(" ", private=True)
        if charcount == 1:
                self.versionchecker(irc)
                self.configcheck(irc)
                self.singlewrite(irc)
                self.main(irc)

        if charcount > 1:
            irc.error("You can only play with 1 character.  You are already logged in as {0}".format(name))
            charcount = 1

    login = wrap(login, [("checkCapability", "admin"), "text"])

    def logoutchar(self, irc, msg, args):
        """takes no arguments

        Logs you out of the PlayBot.
        """
        global charcount
        global netname
        global name
        global pswd
        global gameactive
        
        if gameactive is False:
            irc.error("You are not logged in")
        if gameactive is True:
                irc.reply("{0} has logged out".format(name), private=True)
                netname = None
                name = None
                pswd = None
                gameactive = False
                charcount = 0
                self.singleeraser(irc)
                try:
                    schedule.removeEvent('loopqs')
                except KeyError:
                    irc.error("You are not logged in")

    logoutchar = wrap(logoutchar, [("checkCapability", "admin")])

    def logoutgame(self, irc, msg, args):
        """takes no arguments

        Logs you out of MultiRPG.
        """
        global gameactive
        
        if gameactive is True:
                self.usecommand(irc, "logout")
        if gameactive is False:
            irc.error("You are not logged in")

    logoutgame = wrap(logoutgame, [("checkCapability", "admin")])

    def qplayerslist(self, irc, msg, args):
        """takes no arguments

        Lists players on all QuakeNet plugins loaded
        """

        global quake
        global quakemulti

        self.playbotcheck(irc)

        if quake is True:
                qsfileprefix3 = "quakesingleplayers.txt"
                path = conf.supybot.directories.data
                qsfilename3 = path.dirize(qsfileprefix3)
                qscheck = True
                try:
                        f = open(qsfilename3,"rb")
                        playerListS = pickle.load(f)
                        f.close()
                except:
                        playerListS = []
                try:
                        qsinglename = playerListS[0][1]
                        qsinglenetname = playerListS[0][3]
                except IndexError:
                        irc.reply("No Players Logged in on QuakenetPlayBot", private=True)
                        irc.reply(" ", private=True)
                        irc.reply(" ", private=True)
                        qscheck = False
                if qscheck is True:
                        irc.reply("Quakenet PlayBot Single", private=True)
                        irc.reply(" ", private=True)
                        irc.reply("Player Character - {0}.  Network {1}".format(qsinglename, qsinglenetname), private=True)
                        irc.reply(" ", private=True)
                        irc.reply(" ", private=True)

        if quakemulti is True:
                qmfileprefix4 = "quakemultiplayers.txt"
                path = conf.supybot.directories.data
                qmfilename4 = path.dirize(qmfileprefix4)
                qmcheck = False
                try:
                        f = open(qmfilename4,"rb")
                        playerListM = pickle.load(f)
                        f.close()
                except:
                        playerListM = []
                count = 0
                qmmultiname = None
                qmmultiname2 = None
                qmmultiname3 = None
                qmmultiname4 = None
                qmmultinetname = None
                qmmultinetname2 = None
                qmmultinetname3 = None
                qmmultinetname4 = None
                for entry in playerListM:
                        count += 1
                        if count == 1:
                                qmmultiname = entry[1]
                                qmmultinetname = entry[3]
                                qmcheck = True
                        if count == 2:
                                qmmultiname2 = entry[1]
                                qmmultinetname2 = entry[3]
                        if count == 3:
                                qmmultiname3 = entry[1]
                                qmmultinetname3 = entry[3]
                        if count == 4:
                                qmmultiname4 = entry[1]
                                qmmultinetname4 = entry[3]
                if qmcheck is False:
                        irc.reply("No Players Logged in on QuakenetPlayBotMulti", private=True)
                if qmcheck is True:
                        irc.reply("Quakenet PlayBot Multi", private=True)
                        irc.reply(" ", private=True)
                        irc.reply("Player Character 1 - {0}.  Network {1}    Player Character 2 - {2}.  Network {3}".format(qmmultiname, qmmultinetname, qmmultiname2, qmmultinetname2), private=True)
                        irc.reply("Player Character 3 - {0}.  Network {1}    Player Character 4 - {2}.  Network {3}".format(qmmultiname3, qmmultinetname3, qmmultiname4, qmmultinetname4), private=True)

    qplayerslist = wrap(qplayerslist, [("checkCapability", "admin")])

    def multiread(self, irc):
        try:
                f = open(filename4,"rb")
                playerListM = pickle.load(f)
                f.close()
        except:
                playerListM = []
        return playerListM

    def singlewrite(self, irc):
        global name
        global netname
       
        playerListS = []
        playerListS.append( ( "name", name, "netname", netname ) )
        f = open(filename3,"wb")
        pickle.dump(playerListS,f)
        f.close()

    def singleeraser(self, irc):
        playerListS = []
        f = open(filename3,"wb")
        pickle.dump(playerListS,f)
        f.close()
        irc.reply("QuakeNet PlayerListS Erased", private=True)

    def qsingleerase(self, irc, msg, args):
        """takes no arguments

        Erases playerList file
        """
        self.singleeraser(irc)

    qsingleerase = wrap(qsingleerase, [("checkCapability", "admin")])

    def fixlooper(self, irc, msg, args):
        """takes no arguments

        Fixes the interval looper.
        """
        global interval
        global gameactive
        
        if gameactive is True:
                interval = 30
                self.looper(irc)
        if gameactive is False:
            irc.error("You are not logged in")

    fixlooper = wrap(fixlooper, [("checkCapability", "admin")])

    def updatenick(self, irc, msg, args):
        """takes no arguments

        Updates nickname the supybot sends info to.
        """
        global nickname
        global gameactive

        if gameactive is True:
            nickname = msg.nick
            s = format(_('nick updated to {0}'.format(nickname)))
            irc.reply(s, private=True)
        if gameactive is False:
            irc.error("You are not logged in")

    updatenick = wrap(updatenick, [("checkCapability", "admin")])

    def configcheck(self, irc):
        global channame
        global autoconfig

        pingtime = conf.supybot.protocols.irc.ping.interval()
        commandflood = conf.supybot.abuse.flood.command()
        notcommandflood = conf.supybot.abuse.flood.command.invalid()
        notcommand = conf.supybot.reply.whenNotCommand()

        configchange = False
        zombiecheck = False
        for (channel, c) in ircdb.channels.items():
                if c.lobotomized:
                    if channel == channame:
                                zombiecheck = True

        if autoconfig == 0:
                self.reply(irc, "AutoConfig Off")

        if autoconfig == 1:
                if pingtime < 500:
                        conf.supybot.protocols.irc.ping.interval.set(500)
                        configchange = True
                if commandflood is True:
                        conf.supybot.abuse.flood.command.set("False")
                        configchange = True
                if notcommandflood is True:
                        conf.supybot.abuse.flood.command.invalid.set("False")
                        configchange = True
                if notcommand is True:
                        conf.supybot.reply.whenNotCommand.set("False")
                        configchange = True


                if zombiecheck is False:
                            c = ircdb.channels.getChannel(channame)
                            c.lobotomized = True
                            ircdb.channels.setChannel(channame, c)
                            configchange = True

        if autoconfig == 2 :
                if commandflood is False:
                        conf.supybot.abuse.flood.command.set("True")
                        configchange = True
                if notcommandflood is False:
                        conf.supybot.abuse.flood.command.invalid.set("True")
                        configchange = True
                if notcommand is False:
                        conf.supybot.reply.whenNotCommand.set("True")
                        configchange = True
                if zombiecheck is True:
                            c = ircdb.channels.getChannel(channame)
                            c.lobotomized = False
                            ircdb.channels.setChannel(channame, c)
                            configchange = True

        if autoconfig == 1 or autoconfig == 2:
                if configchange is True:
                        self.reply(irc, "Config Changed")
                        world.flush() 
                if configchange is False:
                        self.reply(irc, "Config OK")

    def cmd(self, irc, msg, args, text):
        """<text>

        Issue manual commands for the game
        """
        global gameactive

        if gameactive is True:
            try:
                    cmdtext = text
            except IndexError:
                    irc.error("To do manual commands use cmd text")
            self.usecommand(irc, "{0}".format(cmdtext))
        if gameactive is False:
            irc.error("You are not logged in")

    cmd = wrap(cmd, [("checkCapability", "admin"), "text"])

    def versioncheck(self, irc, msg, args):
            """takes no arguments

            To check to see if you have the latest version of PlayBot
            """
            global gameactive

            if gameactive is True:
                    self.versionchecker(irc)
            if gameactive is False:
                    irc.error("You are not logged in")

    versioncheck = wrap(versioncheck, [("checkCapability", "admin")])

    def help(self, irc, msg, args):
            """takes no arguments

            Gives a list of Playbot commands
            """
            irc.reply("PlayBot Commands List", private=True)
            irc.reply(" ", private=True)
            irc.reply("BlackBuy Spend Mode Off     - setoption blackbuy false", private=True)
            irc.reply("BlackBuy Spend Mode On      - setoption blackbuy true", private=True)
            irc.reply("BlackBuy 14 Spend Mode Off  - setoption blackbuy14 false", private=True)
            irc.reply("BlackBuy 14 Spend Mode On   - setoption blackbuy14 true", private=True)
            irc.reply("Bot Text Mode Off           - setoption bottext false", private=True)
            irc.reply("Bot Text Mode On            - setoption bottext true", private=True)
            irc.reply("Buy Life Mode Off           - setoption buylife false", private=True)
            irc.reply("Buy Life Mode On            - setoption buylife true", private=True)
            irc.reply("CreepAttack Mode Off        - setoption creepattack false", private=True)
            irc.reply("CreepAttack Mode On         - setoption creepattack true", private=True)
            irc.reply("Erase Config File           - eraseconfig", private=True)
            irc.reply("Erase PlayerList            - qsingleerase", private=True)
            irc.reply("Error Text Mode Off         - setoption errortext false", private=True)
            irc.reply("Error Text Mode On          - setoption errortext true", private=True)
            irc.reply("Experince Buying Mode Off   - setoption expbuy false", private=True)
            irc.reply("Experince Buying Mode On    - setoption expbuy true", private=True)
            irc.reply("Fighting Mode Off           - setoption fights false", private=True)
            irc.reply("Fighting Mode On            - setoption fights true", private=True)
            irc.reply("Fix Looper                  - fixlooper", private=True)
            irc.reply("GameBot PMs Mode Off        - setoption pmtext false", private=True)
            irc.reply("GameBot PMs Mode On         - setoption pmtext true", private=True)
            irc.reply("GetGems Mode Off            - setoption getgems false", private=True)
            irc.reply("GetGems Mode On             - setoption getgems true", private=True)
            irc.reply("Interval Text Mode Off      - setoption intervaltext false", private=True)
            irc.reply("Interval Text Mode On       - setoption intervaltext true", private=True)
            irc.reply("Log In Char                 - login charname password", private=True)
            irc.reply("Log Out Char                - logoutchar", private=True)
            irc.reply("Log Out Game                - logoutgame", private=True)
            irc.reply("Manual Command              - cmd command", private=True)
            irc.reply("PlayBot Commands List       - help", private=True)
            irc.reply("Player's Items              - items", private=True)
            irc.reply("Player's Status             - status", private=True)
            irc.reply("Players List                - qplayerslist", private=True)
            irc.reply("Set Creep Target            - setoption creep creepname", private=True)
            irc.reply("Set Goldsave                - setoption goldsave number", private=True)
            irc.reply("Set Item Buy Level          - setoption itembuy number", private=True)
            irc.reply("Set Option                  - setoption command value", private=True)
            irc.reply("Set Scrolls Buy ItemScore   - setoption scrollssum number", private=True)
            irc.reply("Set SlaySum Min ItemScore   - setoption slaysum number", private=True)
            irc.reply("Set XPSpend for upgrades    - setoption xpspend number", private=True)
            irc.reply("Settings List               - settings", private=True)
            irc.reply("Town/Forest Switch Mode     - setoption townforest true", private=True)
            irc.reply("Town/Work Switch Mode       - setoption townwork true", private=True)
            irc.reply("Update Nick                 - updatenick", private=True)
            irc.reply("Version Checker             - versioncheck", private=True)
            irc.reply("XPUpgrade Mode Off          - setoption xpupgrade false", private=True)
            irc.reply("XPUpgrade Mode On           - setoption xpupgrade true", private=True)
            irc.reply(" ", private=True)
            irc.reply("If you want more information about a command use <bot> help quakenetplaybot <command> - ie /msg DudeRuss help quakenetplaybot settings", private=True)

    help = wrap(help)

    def settings(self, irc, msg, args):
            """takes no arguments

            Gives a list of settings which you can change
            """
            global buylife
            global setbuy
            global name
            global fightmode
            global blackbuyspend
            global blackbuyspend14
            global getgems
            global creepattack
            global setcreeptarget
            global scrollssum
            global xpspend
            global xpupgrade
            global intervaltext
            global townworkswitch
            global expbuy
            global goldsave
            global slaysum
            global bottextmode
            global errortextmode
            global pmtextmode

            irc.reply("Playbot Settings List", private=True)
            irc.reply(" ", private=True)
            if townworkswitch is True:
                     irc.reply("Area Switch Mode - Town/Work", private=True)
            if townworkswitch is False:
                     irc.reply("Area Switch Mode - Town/Forest", private=True)
            irc.reply("BlackBuy Spend Mode - {0}      BlackBuy 14 Spend Mode - {1}".format(blackbuyspend, blackbuyspend14), private=True)
            irc.reply("Bot Text Mode - {0}            Buy Life Mode - {1}".format(bottextmode, buylife), private=True)
            irc.reply("CreepAttack Mode - {0}         Error Text Mode - {1}".format(creepattack, errortextmode), private=True)
            irc.reply("Experience Buying Mode - {0}   Fighting Mode - {1}".format(expbuy, fightmode), private=True)
            irc.reply("GameBot PMs Mode - {0}         GetGems Mode - {1}".format(pmtextmode, getgems), private=True)
            irc.reply("Goldsave - {1}                 Interval Text Mode - {1}".format(goldsave, intervaltext), private=True)
            irc.reply("Item Buy Level - {0}           Player Character - {1}".format(setbuy, name), private=True)
            irc.reply("Scrolls Buy ItemScore - {0}    Set Creep Target - {1}".format(scrollssum, setcreeptarget), private=True)
            irc.reply("SlaySum Minimum - {0}".format(slaysum), private=True)
            irc.reply("XPSpend Upgrade Amount - {0}   XPUpgrade Mode - {1}".format(xpspend, xpupgrade), private=True)

    settings = wrap(settings, [("checkCapability", "admin")])

    def newlister(self, irc):
        global playerspagelist
        global newlist
        global ability
        global python3
        global webworks
        global website
        global level
        global playbottext
        global errortextmode
        
        test = []
        test2 = []
        test3 = []
        newlist = []
        newlistererror = False

        if webworks is True:
                testnum = 0
                for entry in playerspagelist:
                        if "playerview.php" in entry:
                                testnum += 1
                                test = entry
                                testadd = True
                                if "offline" in test:
                                        testadd = False
                                if testadd is True:
                                        test = re.sub(r'<.*?>', ' ', test)
                                        test = test.split(" ")
                                        if testnum == 1:
                                                del test[0:14]
                                        test2.append(test)        

                for entry in test2:
                        if(int(entry[8]) >= level):
                                test3.append(entry)
                for player in test3:
                        name_ = player[5]

                        webworks2 = True
                        weberror = False
                        playerview20 = None
                        playerlist20 = []

                        # get raw player data from web, parse for relevant entry
                        try:
                                if python3 is False:
                                        text = urllib2.urlopen(website + "/playerview.php?player={0}".format(name_))
                                if python3 is True:
                                        text = urllib.request.urlopen(website + "/playerview.php?player={0}".format(name_))
                                playerview20 = text.read()
                                text.close()
                                if python3 is True:
                                        playerview20 = playerview20.decode("UTF-8")
                        except:
                                weberror = True
                        if weberror is True:
                                if errortextmode is True:
                                        self.reply(irc, playbottext + " - Could not access {0}".format(website))
                                webworks2 = False

                        # build list for player records
                        if(playerview20 is None):
                                if errortextmode is True:
                                        self.reply(irc, playbottext + " - Could not access {0}, unknown error.".format(website) )
                                webworks2 = False
                        else:
                                playerlist20 = playerview20.split("\n")
                                playerlist20 = playerlist20[:-1]

                        amulettext = None
                        bootstext = None
                        charmtext = None
                        glovestext = None
                        helmtext = None
                        leggingstext = None
                        ringtext = None
                        shieldtext = None
                        tunictext = None
                        weapontext = None
                        amulet_ = None
                        boots_ = None
                        charm_ = None
                        gloves_ = None
                        helm_ = None
                        leggings_ = None
                        ring_ = None
                        shield_ = None
                        tunic_ = None
                        weapon_ = None
                        experttext1 = None
                        experttext2 = None
                        experttext3 = None
                        expert1_ = None
                        expert2_ = None
                        expert3_ = None

                        if webworks2 is True:
                                for entry in playerlist20:
                                        if "amulet:" in entry:
                                                amulettext = entry
                                        if "boots:" in entry:
                                                bootstext = entry
                                        if "charm:" in entry:
                                                charmtext = entry
                                        if "gloves:" in entry:
                                                glovestext = entry
                                        if "helm:" in entry:
                                                helmtext = entry
                                        if "leggings:" in entry:
                                                leggingstext = entry
                                        if "ring:" in entry:
                                                ringtext = entry
                                        if "shield:" in entry:
                                                shieldtext = entry
                                        if "tunic:" in entry:
                                                tunictext = entry
                                        if "weapon:" in entry:
                                                weapontext = entry
                                        if "Expert 1:" in entry:
                                                experttext1 = entry
                                        if "Expert 2:" in entry:
                                                experttext2 = entry
                                        if "Expert 3:" in entry:
                                                experttext3 = entry
                                        
                                try:
                                        amulettext = amulettext.split(" ")
                                        amuletsplit = amulettext[7]
                                        amulet_ = int(amuletsplit.strip("<br"))
                                        bootstext = bootstext.split(" ")
                                        bootssplit = bootstext[7]
                                        boots_ = int(bootssplit.strip("<br"))
                                        charmtext = charmtext.split(" ")
                                        charmsplit = charmtext[7]
                                        charm_ = int(charmsplit.strip("<br"))
                                        glovestext = glovestext.split(" ")
                                        glovessplit = glovestext[7]
                                        gloves_ = int(glovessplit.strip("<br"))
                                        helmtext = helmtext.split(" ")
                                        helmsplit = helmtext[7]
                                        helm_ = int(helmsplit.strip("<br"))
                                        leggingstext = leggingstext.split(" ")
                                        leggingssplit = leggingstext[7]
                                        leggings_ = int(leggingssplit.strip("<br"))
                                        ringtext = ringtext.split(" ")
                                        ringsplit = ringtext[7]
                                        ring_ = int(ringsplit.strip("<br"))
                                        shieldtext = shieldtext.split(" ")
                                        shieldsplit = shieldtext[7]
                                        shield_ = int(shieldsplit.strip("<br"))
                                        tunictext = tunictext.split(" ")
                                        tunicsplit = tunictext[7]
                                        tunic_ = int(tunicsplit.strip("<br"))
                                        weapontext = weapontext.split(" ")
                                        weaponsplit = weapontext[7]
                                        weapon_ = int(weaponsplit.strip("<br"))

                                        experttext1 = experttext1.split(" ")
                                        expertsplit1 = experttext1[8]
                                        expertsplitsplit1 = expertsplit1.split("<")
                                        expert1_ = expertsplitsplit1[0]
                                        experttext2 = experttext2.split(" ")
                                        expertsplit2 = experttext2[8]
                                        expertsplitsplit2 = expertsplit2.split("<")
                                        expert2_ = expertsplitsplit2[0]
                                        experttext3 = experttext3.split(" ")
                                        expertsplit3 = experttext3[8]
                                        expertsplitsplit3 = expertsplit3.split("<")
                                        expert3_ = expertsplitsplit3[0]
                                        expertcalcsum1 = 0
                                        expertcalcsum2 = 0
                                        expertcalcsum3 = 0
                                        if(expert1_ == "amulet"):
                                                expertcalcsum1 = amulet_ // 10
                                        if(expert1_ == "charm"):
                                                expertcalcsum1 = charm_ // 10
                                        if(expert1_ == "helm"):
                                                expertcalcsum1 = helm_ // 10
                                        if(expert1_ == "boots"):
                                                expertcalcsum1 = boots_ // 10
                                        if(expert1_ == "gloves"):
                                                expertcalcsum1 = gloves_ // 10
                                        if(expert1_ == "ring"):
                                                expertcalcsum1 = ring_ // 10
                                        if(expert1_ == "leggings"):
                                                expertcalcsum1 = leggings_ // 10
                                        if(expert1_ == "shield"):
                                                expertcalcsum1 = shield_ // 10
                                        if(expert1_ == "tunic"):
                                                expertcalcsum1 = tunic_ // 10
                                        if(expert1_ == "weapon"):
                                                expertcalcsum1 = weapon_ // 10

                                        if(expert2_ == "amulet"):
                                                expertcalcsum2 = amulet_ // 10
                                        if(expert2_ == "charm"):
                                                expertcalcsum2 = charm_ // 10
                                        if(expert2_ == "helm"):
                                                expertcalcsum2 = helm_ // 10
                                        if(expert2_ == "boots"):
                                                expertcalcsum2 = boots_ // 10
                                        if(expert2_ == "gloves"):
                                                expertcalcsum2 = gloves_ // 10
                                        if(expert2_ == "ring"):
                                                expertcalcsum2 = ring_ // 10
                                        if(expert2_ == "leggings"):
                                                expertcalcsum2 = leggings_ // 10
                                        if(expert2_ == "shield"):
                                                expertcalcsum2 = shield_ // 10
                                        if(expert2_ == "tunic"):
                                                expertcalcsum2 = tunic_ // 10
                                        if(expert2_ == "weapon"):
                                                expertcalcsum2 = weapon_ // 10

                                        if(expert3_ == "amulet"):
                                                expertcalcsum3 = amulet_ // 10
                                        if(expert3_ == "charm"):
                                                expertcalcsum3 = charm_ // 10
                                        if(expert3_ == "helm"):
                                                expertcalcsum3 = helm_ // 10
                                        if(expert3_ == "boots"):
                                                expertcalcsum3 = boots_ // 10
                                        if(expert3_ == "gloves"):
                                                expertcalcsum3 = gloves_ // 10
                                        if(expert3_ == "ring"):
                                                expertcalcsum3 = ring_ // 10
                                        if(expert3_ == "leggings"):
                                                expertcalcsum3 = leggings_ // 10
                                        if(expert3_ == "shield"):
                                                expertcalcsum3 = shield_ // 10
                                        if(expert3_ == "tunic"):
                                                expertcalcsum3 = tunic_ // 10
                                        if(expert3_ == "weapon"):
                                                expertcalcsum3 = weapon_ // 10
                                        expertcalcsumtotal = expertcalcsum1 + expertcalcsum2 + expertcalcsum3

                                        rank_ = int(player[2])
                                        level_ = int(player[8])
                                        sum_ = float(player[14])
                                        ulevel = int(player[16])
                                        ulevelcalc = ulevel * 100
                                        ability_ = player[20]
                                        abilityadj = 0
                                        if ability == "b":
                                                if ability_ == "w":
                                                        abilityadj = math.floor((sum_ + expertcalcsumtotal) * 0.30)

                                        if ability == "p":
                                                if ability_ == "b":
                                                        abilityadj = math.floor((sum_ + expertcalcsumtotal) * 0.30)
                                                
                                        if ability == "r":
                                                if ability_ == "p":
                                                        abilityadj = math.floor((sum_ + expertcalcsumtotal) * 0.30)
                                                
                                        if ability == "w":
                                                if ability_ == "r":
                                                        abilityadj = math.floor((sum_ + expertcalcsumtotal) * 0.30)
                                                
                                        life_ = float(player[28])
                                        lifecalc = life_ / 100
                                        adjSum = math.floor((sum_ + ulevelcalc + abilityadj + expertcalcsumtotal) * lifecalc)
                                        
                                                        # name       sum   adjsum       level   life   ability   rank     
                                        newlist.append( ( player[5], sum_, int(adjSum), level_, life_, ability_, rank_ ) )
                                except:
                                        newlistererror = True

        if newlistererror is True:
                webworks = False
                if errortextmode is True:
                        self.reply(irc, playbottext + " - Newlister Error")

        newlist.sort( key=operator.itemgetter(1), reverse=True )
        newlist.sort( key=operator.itemgetter(3) )

    def status(self, irc, msg, args):
            """takes no arguments

            Gives a list of character stats
            """
            global name
            global gameactive
            global level
            global ttl
            global atime
            global stime
            global location
            global locationtime
            
            global fights
            global gold
            global gems
            global xp
            global mana
            global upgradelevel
            global expertSum
            global itemSum
            global attackslaySum
            global life
            global exp
            global scrolls
            global rank
            global lottonum1
            global lottonum2
            global lottonum3
            global align

            if gameactive is True:
                irc.reply("{0}'s Status".format(name), private=True)
                irc.reply(" ", private=True)
                irc.reply("Rank: {0}  Level: {1}  Life: {2}  TTL: {3} secs".format(rank, level, life, ttl), private=True)
                irc.reply("Location: {0}  Time: {1} secs".format(location, locationtime), private=True)
                if align == "n":
                        irc.reply("Alignment: Neutral", private=True)
                if align == "g":
                        irc.reply("Alignment: Good", private=True)
                if align == "e":
                        irc.reply("Alignment: Evil", private=True)
                if(level >= 15):
                        irc.reply("Attack Recovery: {0} secs".format(atime), private=True)
                if(level < 15):
                        irc.reply("Creep Attacks Start at Level 15", private=True)
                if(level >= 30):
                        irc.reply("Slay Recovery: {0} secs".format(stime), private=True)
                if(level < 30):
                        irc.reply("Slaying Monsters Start at Level 30", private=True)
                irc.reply("Mana Potion: {0}".format(mana), private=True)
                if(level >= 25):
                        irc.reply("Fights: {0} of 5".format(fights), private=True)
                if(level < 25):
                        irc.reply("Fights Start at Level 25", private=True)
                irc.reply("Gems: {0}  Gold: {1}  XP: {2}".format(gems, gold, xp), private=True)
                irc.reply("Lotto1: {0}  Lotto2: {1}  Lotto3: {2}".format(lottonum1, lottonum2, lottonum3), private=True)
                irc.reply("Exp Used: {0} of 5  Scrolls: {1} of 5".format(exp, scrolls), private=True)
                irc.reply("Items Sum Score: {0}  Expert Items Score: {1}  Upgrade Level: {2}  Attack/SlaySum Item Score: {3}".format(itemSum, expertSum, upgradelevel, int(attackslaySum)), private=True)
            if gameactive is False:
                irc.error("You are not logged in")

    status = wrap(status, [("checkCapability", "admin")])

    def items(self, irc, msg, args):
            """takes no arguments

            Gives a list of character item scores
            """
            global name
            global gameactive
            global amulet
            global charm
            global helm
            global boots
            global gloves
            global ring
            global leggings
            global shield
            global tunic
            global weapon
            global itemSum
            global stone1
            global stone2
            global stone3
            global expert1
            global expert2
            global expert3
            global expertitem1
            global expertitem2
            global expertitem3

            if gameactive is True:
                irc.reply("{0}'s Items List".format(name), private=True)
                irc.reply(" ", private=True)
                irc.reply("Amulet: {0}  Boots: {1}  Charm: {2}  Gloves: {3}  Helm: {4}".format(amulet, boots, charm, gloves, helm), private=True)
                irc.reply("Leggings: {0}  Ring: {1}  Shield: {2}  Tunic: {3}  Weapon: {4}".format(leggings, ring, shield, tunic, weapon), private=True)
                irc.reply("Stones 1: {0}  2: {1}  3: {2}".format(stone1, stone2, stone3), private=True)
                irc.reply("Items Sum Score: {0}".format(itemSum), private=True)
                irc.reply("Expert Items 1: {0} {1}  2: {2} {3}  3: {4} {5}".format(expert1, expertitem1, expert2, expertitem2, expert3, expertitem3), private=True)
            if gameactive is False:
                irc.error("You are not logged in")

    items = wrap(items, [("checkCapability", "admin")])

    def webdata(self, irc):
            global playerlist
            global name
            global webworks
            global playerview
            global python3
            global playerspage
            global playerspagelist
            global website
            global playbottext
            global errortextmode
            
            webworks = True
            weberror = False

            # get raw player data from web, parse for relevant entry
            try:
                if python3 is False:
                        text = urllib2.urlopen(website + "/playerview.php?player={0}".format(name))
                if python3 is True:
                        text = urllib.request.urlopen(website + "/playerview.php?player={0}".format(name))
                playerview = text.read()
                text.close()
                if python3 is True:
                        playerview = playerview.decode("UTF-8")
                if python3 is False:
                        text2 = urllib2.urlopen(website + "/players.php")
                if python3 is True:
                        text2 = urllib.request.urlopen(website + "/players.php")
                playerspage = text2.read()
                text2.close()
                if python3 is True:
                        playerspage = playerspage.decode("UTF-8")
            except:
                weberror = True

            if weberror is True:
                if errortextmode is True:
                        self.reply(irc, playbottext + " - Could not access {0}".format(website))
                webworks = False

            # build list for player records
            if(playerview is None):
                    if errortextmode is True:
                            self.reply(irc, playbottext + " - Could not access {0}, unknown error.".format(website) )
                    webworks = False
            else:
                    playerlist = playerview.split("\n")
                    playerlist = playerlist[:-1]
            if(playerspage is None):
                    if errortextmode is True:
                            self.reply(irc, playbottext + " - Could not access {0}, unknown error.".format(website) )
                    webworks = False
            else:
                    playerspagelist = playerspage.split("\n")
                    playerspagelist = playerspagelist[:-1]

    def playerarea(self, irc):
        global level
        global mysum
        global location
        global locationtime
        global townworkswitch
        
        if townworkswitch is True:
                area = "work"
        if townworkswitch is False:
                area = "forest"

#        self.reply(irc, "{0} Time: {1} seconds".format(location, locationtime))
        if (level <= 25):
                mintime = (3 * 60 * 60)
        if (level > 25 and level <= 40):
                mintime = (6 * 60 * 60)
        if (level > 40 and level <= 50):
                mintime = (12 * 60 * 60)
        if (level > 50):
                mintime = (24 * 60 * 60)

        if locationtime == 0:
                self.usecommand(irc, "goto {0}".format(area))
                
        if(location == "In Town" and locationtime >= mintime and mysum < 6000 and mysum != 0):
                self.usecommand(irc, "goto {0}".format(area))
        if(location == "In Town" and mysum >= 6000):
                self.usecommand(irc, "goto {0}".format(area))
        if(location == "At Work" and locationtime >= mintime):
                self.usecommand(irc, "goto town")
        if(location == "In The Forest" and locationtime >= (24 * 60 * 60)):
                self.usecommand(irc, "goto town")

    def getvariables(self, irc):
        global level
        global ttl

        global ring
        global amulet
        global charm
        global weapon
        global helm
        global tunic
        global gloves
        global leggings
        global shield
        global boots

        global mysum
        global gold
        global upgradelevel
        global gems
        global ability
        global xp
        global life
        global fights
        global scrolls
        global exp
        global mana
        global align

        global stone1
        global stone2
        global stone3
        global expert1
        global expert2
        global expert3

        global atime
        global stime
        global playerlist
        global webworks
        global gameactive
        global lottonum1
        global lottonum2
        global lottonum3
        global playbottext
        global location
        global locationtime
        global errortextmode
        
        aligntext = None
        leveltext = None
        ttltext = None
        goldtext = None
        gemstext = None
        upgradetext = None
        abilitytext = None
        xptext = None
        exptext = None
        lifetext = None
        scrollstext = None
        manatext = None
        atimetext = None
        ctimetext = None
        
        amulettext = None
        bootstext = None
        charmtext = None
        glovestext = None
        helmtext = None
        leggingstext = None
        ringtext = None
        shieldtext = None
        tunictext = None
        weapontext = None

        sumtext = None
        experttext1 = None
        experttext2 = None
        experttext3 = None
        stonetext1 = None
        stonetext2 = None
        stonetext3 = None
        fightstext = None
        lottonumtext1 = None
        lottonumtext2 = None
        lottonumtext3 = None

        playeris = None
        worktext = None
        towntext = None
        foresttext = None
        atwork = False
        intown = False
        intheforest = False                       

        if webworks is True and gameactive is True and playerlist != None:
                for entry in playerlist:
                        if "Alignment:" in entry:
                                aligntext = entry
                        if "Level:" in entry:
                                leveltext = entry
                        if "Next level:" in entry:
                                ttltext = entry
                        if "Gold:" in entry:
                                goldtext = entry
                        if "Gems:" in entry:
                                gemstext = entry
                        if "Upgrade level:" in entry:
                                upgradetext = entry
                        if "Ability:" in entry:
                                abilitytext = entry
                        if "XP:" in entry:
                                xptext = entry
                        if "Exp Used:" in entry:
                                exptext = entry
                        if "Life:" in entry:
                                lifetext = entry
                        if "Scrolls Used:" in entry:
                                scrollstext = entry
                        if "Mana Potion:" in entry:
                                manatext = entry
                        if "Creep Attack in:" in entry:
                                atimetext = entry
                        if "Dragon Slay in:" in entry:
                                stimetext = entry

                        if "amulet:" in entry:
                                amulettext = entry
                        if "boots:" in entry:
                                bootstext = entry
                        if "charm:" in entry:
                                charmtext = entry
                        if "gloves:" in entry:
                                glovestext = entry
                        if "helm:" in entry:
                                helmtext = entry
                        if "leggings:" in entry:
                                leggingstext = entry
                        if "ring:" in entry:
                                ringtext = entry
                        if "shield:" in entry:
                                shieldtext = entry
                        if "tunic:" in entry:
                                tunictext = entry
                        if "weapon:" in entry:
                                weapontext = entry

                        if "Sum:" in entry:
                                sumtext = entry
                        if "Expert 1:" in entry:
                                experttext1 = entry
                        if "Expert 2:" in entry:
                                experttext2 = entry
                        if "Expert 3:" in entry:
                                experttext3 = entry
                        if "Stone 1:" in entry:
                                stonetext1 = entry
                        if "Stone 2:" in entry:
                                stonetext2 = entry
                        if "Stone 3:" in entry:
                                stonetext3 = entry
                        if "Manual FIGHT commands used (out of 5):" in entry:
                                fightstext = entry
                        if "Lotto Numbers 1:" in entry:
                                lottonumtext1 = entry
                        if "Lotto Numbers 2:" in entry:
                                lottonumtext2 = entry
                        if "Lotto Numbers 3:" in entry:
                                lottonumtext3 = entry

                        if "Player is:" in entry:
                                playeris = entry
                        if "Work Time:" in entry:
                                worktext = entry
                        if "Town Time:" in entry:
                                towntext = entry
                        if "Forest Time:" in entry:
                                foresttext = entry

                try:
                        try:
                                if "Neutral" in aligntext:
                                        align = "n"
                                if "Evil" in aligntext:
                                        align = "e"
                                if "Good" in aligntext:
                                        align = "g"
                        except TypeError:
                                align = "n"
                        leveltext = leveltext.split(" ")
                        levelsplit = leveltext[7]
                        level = int(levelsplit.strip("<br"))
                        ttltext = ttltext.split(" ")
                        daystext = int(ttltext[8])
                        timetext = ttltext[10].strip("<br")
                        ttl = self.timetosecs(daystext, timetext)
                        goldtext = goldtext.split(" ")
                        goldsplit = goldtext[7]
                        gold = int(goldsplit.strip("<br"))
                        gemstext = gemstext.split(" ")
                        gemssplit = gemstext[7]
                        gems = int(gemssplit.strip("<br"))
                        upgradetext = upgradetext.split(" ")
                        upgradesplit = upgradetext[8]
                        upgradelevel = int(upgradesplit.strip("<br"))

                        if "Barbarian" in abilitytext:
                                ability = "b"
                        if "Rogue" in abilitytext:
                                ability = "r"
                        if "Paladin" in abilitytext:
                                ability = "p"
                        if "Wizard" in abilitytext:
                                ability = "w"

                        xptext = xptext.split(" ")
                        xpsplit = xptext[7]
                        xp = int(xpsplit.strip("<br"))
                        exptext = exptext.split(" ")
                        expsplit = exptext[8]
                        expsplit = expsplit.split("/")
                        try:
                                exp = int(expsplit[0])
                        except:
                                exp = 0
                        lifetext = lifetext.split(" ")
                        lifesplit = lifetext[7]
                        life = int(lifesplit.strip("<br"))
                        scrollstext = scrollstext.split(" ")
                        scrollssplit = scrollstext[8]
                        scrollssplit = scrollssplit.split("/")
                        try:
                                scrolls = int(scrollssplit[0])
                        except ValueError:
                                scrolls = 0
                        manatext = manatext.split(" ")
                        manasplit = manatext[8]
                        manasplit = manasplit.split("/")
                        mana = int(manasplit[0])

                        try:
                                atimetext = atimetext.split(" ")
                                daystext = int(atimetext[9])
                                timetext = atimetext[11].strip("<br")
                                atime = self.timetosecs(daystext, timetext)
                        except ValueError:
                                atime = 0
                        try:
                                stimetext = stimetext.split(" ")
                                daystext = int(stimetext[9])
                                timetext = stimetext[11].strip("<br")
                                stime = self.timetosecs(daystext, timetext)
                        except ValueError:
                                stime = 0

                        amulettext = amulettext.split(" ")
                        amuletsplit = amulettext[7]
                        amulet = int(amuletsplit.strip("<br"))
                        bootstext = bootstext.split(" ")
                        bootssplit = bootstext[7]
                        boots = int(bootssplit.strip("<br"))
                        charmtext = charmtext.split(" ")
                        charmsplit = charmtext[7]
                        charm = int(charmsplit.strip("<br"))
                        glovestext = glovestext.split(" ")
                        glovessplit = glovestext[7]
                        gloves = int(glovessplit.strip("<br"))
                        helmtext = helmtext.split(" ")
                        helmsplit = helmtext[7]
                        helm = int(helmsplit.strip("<br"))
                        leggingstext = leggingstext.split(" ")
                        leggingssplit = leggingstext[7]
                        leggings = int(leggingssplit.strip("<br"))
                        ringtext = ringtext.split(" ")
                        ringsplit = ringtext[7]
                        ring = int(ringsplit.strip("<br"))
                        shieldtext = shieldtext.split(" ")
                        shieldsplit = shieldtext[7]
                        shield = int(shieldsplit.strip("<br"))
                        tunictext = tunictext.split(" ")
                        tunicsplit = tunictext[7]
                        tunic = int(tunicsplit.strip("<br"))
                        weapontext = weapontext.split(" ")
                        weaponsplit = weapontext[7]
                        weapon = int(weaponsplit.strip("<br"))

                        sumtext = sumtext.split(" ")
                        sumsplit = sumtext[7]
                        mysum = int(sumsplit.strip("<br"))
                        experttext1 = experttext1.split(" ")
                        expertsplit1 = experttext1[8]
                        expertsplitsplit1 = expertsplit1.split("<")
                        expert1 = expertsplitsplit1[0]
                        experttext2 = experttext2.split(" ")
                        expertsplit2 = experttext2[8]
                        expertsplitsplit2 = expertsplit2.split("<")
                        expert2 = expertsplitsplit2[0]
                        experttext3 = experttext3.split(" ")
                        expertsplit3 = experttext3[8]
                        expertsplitsplit3 = expertsplit3.split("<")
                        expert3 = expertsplitsplit3[0]
                        stonetext1 = stonetext1.split(" ")
                        stonesplit1 = stonetext1[8]
                        stonesplitsplit1 = stonesplit1.split("<")
                        stone1 = stonesplitsplit1[0]
                        stonetext2 = stonetext2.split(" ")
                        stonesplit2 = stonetext2[8]
                        stonesplitsplit2 = stonesplit2.split("<")
                        stone2 = stonesplitsplit2[0]
                        stonetext3 = stonetext3.split(" ")
                        stonesplit3 = stonetext3[8]
                        stonesplitsplit3 = stonesplit3.split("<")
                        stone3 = stonesplitsplit3[0]
                        fightstext = fightstext.split(" ")
                        fightssplit = fightstext[13]
                        fights = int(fightssplit.strip("<br"))
                        lottonumtext1 = re.sub(r'<.*?>', ' ', lottonumtext1)
                        lottonumtext1 = lottonumtext1.split(" ")
                        lottonumtext2 = re.sub(r'<.*?>', ' ', lottonumtext2)
                        lottonumtext2 = lottonumtext2.split(" ")
                        lottonumtext3 = re.sub(r'<.*?>', ' ', lottonumtext3)
                        lottonumtext3 = lottonumtext3.split(" ")
                        lottonum1 = "{0} {1} and {2}".format(lottonumtext1[11], lottonumtext1[12], lottonumtext1[13])                        
                        lottonum2 = "{0} {1} and {2}".format(lottonumtext2[11], lottonumtext2[12], lottonumtext2[13])                        
                        lottonum3 = "{0} {1} and {2}".format(lottonumtext3[11], lottonumtext3[12], lottonumtext3[13])                        

                        if "at work" in playeris:
                                atwork = True
                        if "in town" in playeris:
                                intown = True
                        if "in the forest" in playeris:
                                intheforest = True
                        if atwork is True:
                                try:
                                        worktext = worktext.split(" ")
                                        workdays = int(worktext[8])
                                        worksplittime = worktext[10]
                                        worksplittime = worksplittime.strip("<br")
                                        locationtime = self.timetosecs(workdays, worksplittime)
                                        location = "At Work"
                                except ValueError:
                                        locationtime = 0
                                        location = "At Work"
                        if intown is True:
                                try:
                                        towntext = towntext.split(" ")
                                        towndays = int(towntext[8])
                                        townsplittime = towntext[10]
                                        townsplittime = townsplittime.strip("<br")
                                        locationtime = self.timetosecs(towndays, townsplittime)
                                        location = "In Town"
                                except ValueError:
                                        locationtime = 0
                                        location = "In Town"
                        if intheforest is True:
                                try:
                                        foresttext = foresttext.split(" ")
                                        forestdays = int(foresttext[8])
                                        forestsplittime = foresttext[10]
                                        forestsplittime = forestsplittime.strip("<br")
                                        locationtime = self.timetosecs(forestdays, forestsplittime)
                                        location = "In The Forest"
                                except ValueError:
                                        locationtime = 0
                                        location = "In The Forest"

                except:
                        webworks = False
                        if errortextmode is True:
                                self.reply(irc, playbottext + " - Variable Error")

    def timetosecs(self, days, timetext):
        timesecs = 0
        splittime = timetext.split(":")
        hours = int(splittime[0])
        mins = int(splittime[1])
        secs = int(splittime[2])
        timesecs = ((days * 24 * 60 * 60) + (hours * 60 * 60) + (mins * 60) + secs)
        return timesecs

    def timercheck(self, irc):
            global ttl
            global interval
            global atime
            global stime
            global level
            global attackslaySum
            global mana
            global gold
            global life
            global slaysum
            global playbotext
            global bottextmode
            
            # make sure no times are negative
            if(atime < 0):
                    atime = 0
            if(stime < 0):
                    stime = 0
#            self.reply(irc, "atime {0}  stime {1}  ttl {2}".format(atime, stime, ttl))
            slaydisable = False
            
            def lvlupgoqs():
                self.lvlup(irc)
            
            def attackgoqs():
                self.attack(irc)

            def slaygoqs():
                self.slay(irc, 1)
            def slaygobqs():
                self.slay(irc, 2)

            if(ttl <= interval and ttl > 0):
                    timer = time.time() + (ttl+10)
                    if bottextmode is True:
                            self.reply(irc, playbottext + " - Set lvlup timer. Going off in {0} minutes.".format(ttl // 60))
                    try:
                        schedule.addEvent(lvlupgoqs, timer, "lvlupqs")
                    except AssertionError:
                        schedule.removeEvent('lvlupqs')
                        schedule.addEvent(lvlupgoqs, timer, "lvlupqs")                        
            if(level >= 15 and atime <= interval and atime <= ttl and life > 10):
                    timer = time.time() + (atime+10)
                    if bottextmode is True:
                            self.reply(irc, playbottext + " - Set attack timer. Going off in {0} minutes.".format(atime // 60))
                    slaydisable = True
                    try:
                        schedule.addEvent(attackgoqs, timer, "attackqs")
                    except AssertionError:
                        schedule.removeEvent('attackqs')
                        schedule.addEvent(attackgoqs, timer, "attackqs")                  
            if(level >= 30 and attackslaySum >= 1000 and stime <= interval and stime <= ttl and slaydisable is False and life > 10):
                    if(mana == 0 and gold >= 1100 and attackslaySum < 150000):
                        self.usecommand(irc, "buy mana")
                        gold -= 1000
                        mana = 1
                    timer = time.time() + (stime+10)
                    if mana == 0 and attackslaySum >= slaysum:
                            if bottextmode is True:
                                    self.reply(irc, playbottext + " - Set slay timer. Going off in {0} minutes.".format(stime // 60))
                            try:
                                schedule.addEvent(slaygoqs, timer, "slayqs")
                            except AssertionError:
                                schedule.removeEvent('slayqs')
                                schedule.addEvent(slaygoqs, timer, "slayqs")
                    if mana == 1:
                            if bottextmode is True:
                                    self.reply(irc, playbottext + " - Set slay timer. Going off in {0} minutes.".format(stime // 60))
                            mana = 0
                            try:
                                schedule.addEvent(slaygobqs, timer, "slayqs")
                            except AssertionError:
                                schedule.removeEvent('slayqs')
                                schedule.addEvent(slaygobqs, timer, "slayqs")

    def expertcalc(self, item):
        expertcalcsum = 0
        if(item == "amulet"):
                expertcalcsum = amulet // 10
        if(item == "charm"):
                expertcalcsum = charm // 10
        if(item == "helm"):
                expertcalcsum = helm // 10
        if(item == "boots"):
                expertcalcsum = boots // 10
        if(item == "gloves"):
                expertcalcsum = gloves // 10
        if(item == "ring"):
                expertcalcsum = ring // 10
        if(item == "leggings"):
                expertcalcsum = leggings // 10
        if(item == "shield"):
                expertcalcsum = shield // 10
        if(item == "tunic"):
                expertcalcsum = tunic // 10
        if(item == "weapon"):
                expertcalcsum = weapon // 10
        return expertcalcsum

    def spendmoney(self, irc):
        global level
        global gold
        global gems
        global xp
        global life
        global buylife
        global setbuy
        global upgradelevel
        global expert1
        global expert2
        global expert3
        global itemSum
        global expertSum
        global attackslaySum
        global expertitem1
        global expertitem2
        global expertitem3
        global align
        global mysum
        global blackbuyspend
        global blackbuyspend14
        global interval
        global scrolls
        global exp
        global getgems
        global goldsave
        global scrollssum
        global xpupgrade
        global xpspend
        global amulet
        global charm
        global helm
        global boots
        global gloves
        global ring
        global leggings
        global shield
        global tunic
        global weapon 
        global expbuy
        
        # level 15 >= buy - decide what to spend our gold on! :D
        # level 1 >= blackbuy - requires 15 gems per buy
        # level 1 >= get x gems - 150 gold per gem
        # xpget 20xp minimum
        # buy experience - 500 gold - 10% off TTL
        
        lowestitem = self.worstitem()
#        self.reply(irc, "Worst item {0}".format(lowestitem))

        if(gold < 0):
                gold = 0
        
        lifediff = 100 - life
        lifebuy = 9999999999999999

        if(level >= 20):
                spendmulti = level // 5
        
        if(level >= 1 and level <= 19):
                lifebuy = lifediff * 3
        if(level >= 20):
                lifebuy = lifediff * spendmulti
        if(level >= 15  and buylife is True and life >= 0 and life < 100 and gold >= lifebuy):
                self.usecommand(irc, "buy life")
                gold -= lifebuy
                life = 100

        gembuy = True
        if(level >= 35):
                if upgradelevel == 0 and gold < 600:
                        gembuy = False
                if upgradelevel == 0 and gold >= 600:
                        self.usecommand(irc, "buy upgrade")
                        gold -= 500
                        upgradelevel = 1
        if(level >= 40):
                if upgradelevel == 1 and gold < 1100:
                        gembuy = False
                if upgradelevel == 1 and gold >= 1100:
                        self.usecommand(irc, "buy upgrade")
                        gold -= 1000
                        upgradelevel = 2
        if(level >= 45):
                if upgradelevel == 2 and gold < 2100:
                        gembuy = False
                if upgradelevel == 2 and gold >= 2100:
                        self.usecommand(irc, "buy upgrade")
                        gold -= 2000
                        upgradelevel = 3
        if(level >= 50):
                if upgradelevel == 3 and gold < 4100:
                        gembuy = False
                if upgradelevel == 3 and gold >= 4100:
                        self.usecommand(irc, "buy upgrade")
                        gold -= 4000
                        upgradelevel = 4
        if(level >= 60):
                if upgradelevel == 4 and gold < 8100:
                        gembuy = False
                if upgradelevel == 4 and gold >= 8100:
                        self.usecommand(irc, "buy upgrade")
                        gold -= 8000
                        upgradelevel = 5
                
        if(gembuy is True and expbuy is True and exp < 5):
                expdiff = 5 - exp
                expcost = expdiff * 500
                if(gold >= (expcost + 1100)):
                        for i in range(expdiff):
                                self.usecommand(irc, "buy experience")
                                gold -= 500
                                exp += 1
                elif(gold >= 500 + 1100):
                        golddiff = gold - 1100
                        expcalc = golddiff // 500
                        if expcalc >= 1:
                                for i in range(expcalc):
                                        self.usecommand(irc, "buy experience")
                                        gold -= 5000
                                        exp += 1
                
#        self.reply(irc, "goldsave: {0}  gembuy: {1}  level: {2}  upgradelevel: {3}  align: {4}".format(goldsave, gembuy, level, upgradelevel, align))
        
        if(level >= setbuy):
                buycost = level * 2 * 3
                buyitem = level * 2     
                buydiff = 19
                if(gold > buycost + 100):
                        if(amulet < (buyitem - buydiff)):
                                self.usecommand(irc, "buy amulet {0}".format(buyitem))
                                gold -= buycost
                                amulet = buyitem
                if(gold > buycost + 100):
                        if(boots < (buyitem - buydiff)):
                                self.usecommand(irc, "buy boots {0}".format(buyitem))
                                gold -= buycost
                                boots = buyitem
                if(gold > buycost + 100):
                        if(charm < (buyitem - buydiff)):
                                self.usecommand(irc, "buy charm {0}".format(buyitem))
                                gold -= buycost
                                charm = buyitem
                if(gold > buycost + 100):
                        if(gloves < (buyitem - buydiff)):
                                self.usecommand(irc, "buy gloves {0}".format(buyitem))
                                gold -= buycost
                                gloves = buyitem
                if(gold > buycost + 100):
                        if(helm < (buyitem - buydiff)):
                                self.usecommand(irc, "buy helm {0}".format(buyitem))
                                gold -= buycost
                                helm = buyitem
                if(gold > buycost + 100):
                        if(leggings < (buyitem - buydiff)):
                                self.usecommand(irc, "buy leggings {0}".format(buyitem))
                                gold -= buycost
                                leggings = buyitem
                if(gold > buycost + 100):
                        if(ring < (buyitem - buydiff)):
                                self.usecommand(irc, "buy ring {0}".format(buyitem))
                                gold -= buycost
                                ring = buyitem
                if(gold > buycost + 100):
                        if(shield < (buyitem - buydiff)):
                                self.usecommand(irc, "buy shield {0}".format(buyitem))
                                gold -= buycost
                                shield = buyitem
                if(gold > buycost + 100):
                        if(tunic < (buyitem - buydiff)):
                                self.usecommand(irc, "buy tunic {0}".format(buyitem))
                                gold -= buycost
                                tunic = buyitem
                if(gold > buycost + 100):
                        if(weapon < (buyitem - buydiff)):
                                self.usecommand(irc, "buy weapon {0}".format(buyitem))
                                gold -= buycost
                                weapon = buyitem

        if(level >= 25):
                if(gems < 15):
                        if getgems is True and gembuy is True:
                                gemdiff = 15 - gems
                                gemcost = gemdiff * 150
                                if gold > (goldsave + gemcost):
                                        self.usecommand(irc, "get {0} gems".format(gemdiff))
                                        gold -= gemcost
                                        gems += gemdiff
                if(gems >= 15):
                        if getgems is True and gembuy is True:
                                gemdiv = gems // 15
                                gemdiv2 = gemdiv * 15
                                gemdiv3 = gemdiv2 + 15
                                gemdiff = gemdiv3 - gems
                                gemcost = gemdiff * 150
                                if gold > (goldsave + gemcost):
                                        self.usecommand(irc, "get {0} gems".format(gemdiff))
                                        gold -= gemcost
                                        gems += gemdiff
                                
                                moneycalc = gold - goldsave
                                gemcalc = moneycalc // 150
                                if(gemcalc >= 15):
                                        gems15 = gemcalc // 15
                                        if(gems15 >= 1):
                                                buymoney = gems15 * 150 * 15
                                                buygems = gems15 * 15
                                                self.usecommand(irc, "get {0} gems".format(buygems))
                                                gold -= buymoney
                                                gems += buygems

                        blackbuydisable = False
                        if(blackbuyspend14 is True):
                                if(gems >= (15 * 14)):
                                        self.usecommand(irc, "blackbuy {0} 14".format(lowestitem[0]))
                                        gems -= (15 * 14) 
                                        if(gems >= 15):
                                                interval = 120
                                                self.looper(irc)
                                                blackbuydisable = True

                        if(blackbuyspend is True and blackbuydisable is False):
                                if(gems >= 15):
                                        gemspend15 = gems // 15
                                        if(gemspend15 >= 1):
                                                self.usecommand(irc, "blackbuy {0} {1}".format(lowestitem[0], gemspend15))
                                                gems -= gemspend15 * 15 
                                                if(gems >= 15):
                                                        interval = 120
                                                        self.looper(irc)

                if(xp >= 20 and mysum >= scrollssum and scrolls < 5):
                        xpcalc = xp // 20
                        scrollsdiff = 5 - scrolls
                        scrollscost = scrollsdiff * 20
                        if(xp >= scrollscost):
                                for i in range(scrollsdiff):
                                        self.usecommand(irc, "xpget scroll")
                                        xp -= 20
                                        scrolls += 1
                        elif(xp >= 20):
                                xpcalc = xp // 20
                                if xpcalc >= 1:
                                        for i in range(xpcalc):
                                                self.usecommand(irc, "xpget scroll")
                                                xp -= 20
                                                scrolls += 1
                                                
        if(level >= 25 and xpupgrade is True):
                if(xp >= xpspend):
                        if(mysum < scrollssum):
                                xpcalc = xp // xpspend
                        if(mysum >= scrollssum):
                                xpdiff = xp - 200
                                xpcalc = xpdiff // xpspend
                        if(xpcalc >= 1):
                                if xpcalc > 5:
                                        xpcalc = 5
                                for i in range(xpcalc):
                                        self.usecommand(irc, "xpget {0} {1}".format(lowestitem[0], xpspend))
                                        xp -= xpspend

        expertitem1 = self.expertcalc(expert1)
        expertitem2 = self.expertcalc(expert2)
        expertitem3 = self.expertcalc(expert3)
           
        lifepercent = (float(life) / 100)
        itemSum = (amulet + charm + helm + boots + gloves + ring + leggings + shield + tunic + weapon)
        expertSum = expertitem1 + expertitem2 + expertitem3 
        upgradeSum1 = upgradelevel * 100
        attackslaySum = (itemSum + expertSum + upgradeSum1) * lifepercent

    def lvlup(self, irc):
            global name
            global level
            global interval
            global life
            global playbottext
            global bottextmode
           
            level += 1

            if bottextmode is True:
                    self.reply(irc, playbottext + " - {0} has reached level {1}!".format(name, level))

            interval = 60
            self.looper(irc)

            def attackgoqs():
                    self.attack(irc)

            if(level >= 16 and life > 10):
                    try:
                            schedule.addEvent(attackgoqs, 0, "attackqs")
                    except AssertionError:
                            schedule.removeEvent('attackqs')
                            schedule.addEvent(attackgoqs, 0, "attackqs")                        

    def fight_fight(self, irc):
            global name
            global level
            global ufightcalc
            global itemSum
            global expertSum
            global fights
            global rank
            global ability
            global upgradelevel
            global life
            global fightmode
            global playbottext
            global bottextmode

            ufight = self.testfight()

            upgradeSum1 = upgradelevel * 100
            fightSumTotal = itemSum + expertSum
            abilityadj = 0
            if ability == "b":
                if ufight[5] == "p":
                        abilityadj = math.floor(fightSumTotal * 0.30)

            if ability == "p":
                if ufight[5] == "r":
                        abilityadj = math.floor(fightSumTotal * 0.30)
                
            if ability == "r":
                if ufight[5] == "w":
                        abilityadj = math.floor(fightSumTotal * 0.30)
                
            if ability == "w":
                if ufight[5] == "b":
                        abilityadj = math.floor(fightSumTotal * 0.30)

            lifepercent = (float(life) / 100)
            fightAdj = (fightSumTotal + abilityadj + upgradeSum1) * lifepercent
        
            ufightcalc = fightAdj / ufight[2]

            if(level >= 25):
                if bottextmode is True:
                        self.reply(irc, playbottext + " - Best fight for Rank {0}:  {1}  [{2}]  Opponent: Rank {3}:  {4}  [{5}], Odds {6}".format(rank, name, int(fightAdj), ufight[6], ufight[0], int(ufight[2]), ufightcalc))
                if(ufightcalc >= 0.9 and fightmode is True):
                        self.usecommand(irc, "fight {0}".format( ufight[0] ))
                        fights += 1

    def testfight(self):
        global newlist
        global level
        global name
        global upgradelevel
        global itemSum
        global expertSum
        global ability
        global life
            
        upgradeSum1 = upgradelevel * 100
        fightSumTotal = float(itemSum + expertSum)
        lifepercent = (float(life) / 100)
        test = []
        
        diff = 0
        best = ("Doctor Who?", 9999999999.0, 9999999999.0, 0, 0, "p", 0)
        newlist.sort( key=operator.itemgetter(2))
        if newlist != None:
                for entry in newlist:
                        if(entry[3] >= level and entry[0] != name):
                                abilityadj = 0
                                if ability == "b":
                                        if entry[5] == "p":
                                                abilityadj = math.floor(fightSumTotal * 0.30)

                                if ability == "p":
                                        if entry[5] == "r":
                                                abilityadj = math.floor(fightSumTotal * 0.30)
                                        
                                if ability == "r":
                                        if entry[5] == "w":
                                                abilityadj = math.floor(fightSumTotal * 0.30)
                                        
                                if ability == "w":
                                        if entry[5] == "b":
                                                abilityadj = math.floor(fightSumTotal * 0.30)

                                fightAdj = (fightSumTotal + abilityadj + upgradeSum1) * lifepercent

                                try:
                                        currdiff = fightAdj / entry[2]
                                except ZeroDivisionError:
                                        currdiff = 0
                                test.append( (entry, currdiff) )

                test.sort( key=operator.itemgetter(1))

                for entry in test:
                        if entry[1] > diff:
                                diff = entry[1]
                                best = entry[0]

        return best

    def attack(self, irc):
        global creepattack
        global setcreeptarget
        
        if creepattack is True:
            creep = self.bestattack()
            if creep != "CreepList Error":
                    self.usecommand(irc, "attack " + creep)
            if creep == "CreepList Error":
                    self.reply(irc, "{0}".format(creep))
        if creepattack is False:
                self.usecommand(irc, "attack " + setcreeptarget)

    def slay(self, irc, num2):
        monster = self.bestslay(num2)
        if monster != "MonsterList Error":
                self.usecommand(irc, "slay " + monster)
        if monster == "MonsterList Error":
                self.reply(irc, "{0}".format(monster))

    def bestattack(self):
        global creeps
        global attackslaySum
              
        good = "CreepList Error"
        for thing in creeps:
                if(attackslaySum <= thing[1]):
                        good = thing[0]
        return good

    def bestslay(self, num2):
        global monsters
        global attackslaySum
               
        good = "MonsterList Error"
        if num2 == 1:
                multi = 1
        if num2 == 2:
                multi = 2
        for thing in monsters:
                if((attackslaySum * multi) <= thing[1]):
                        good = thing[0]
        return good

    def worstitem(self):
            global amulet
            global charm
            global helm
            global boots
            global gloves
            global ring
            global leggings
            global shield
            global tunic
            global weapon

            itemlist = [    ["amulet",      amulet],        \
                            ["charm",       charm],  \
                            ["helm",        helm],  \
                            ["boots",       boots],  \
                            ["gloves",      gloves],        \
                            ["ring",        ring],  \
                            ["leggings",    leggings],      \
                            ["shield",      shield],  \
                            ["tunic",       tunic], \
                            ["weapon",      weapon] ]

            itemlist.sort( key=operator.itemgetter(1), reverse=True )
            good = itemlist
            diff = 999999
            for thing in itemlist:
                    if(thing[1] < diff):
                            good = thing
            return good
        
    def inFilter(self, irc, msg):
        """Used for filtering/modifying messages as they're entering.

        ircmsgs.IrcMsg objects are immutable, so this method is expected to
        return another ircmsgs.IrcMsg object.  Obviously the same IrcMsg
        can be returned.
        """
        global botname
        global name
        global pswd
        global webworks
        global otherIrc
        global netname
        global gameactive
        global interval
        global supynick

        global life
        global level
        global buylife
        global playbottext
        global pmtextmode

        messagelist = [ ["You are not recovered"],    \
                        ["FIGHT Request Denied:"],    \
                        ["ATTACK Request Denied:"],    \
                        ["SLAY Request Denied:"],    \
                        ["EAT Request Denied:"],    \
                        ["Shop available to 15+"],    \
                        ["Online players:"],    \
                        ["You are already"],    \
                        ["Try: ALIGN"],    \
                        ["That would be dumb"],            \
                        ["Welcome to the shop"],            \
                        ["Do you have enough"],            \
                        ["You were not in Town"],         \
                        ["You first need to go to Town"],         \
                        ["You already have"],         \
                        ["You must explore the forest"],         \
                        ["You do not have any gold, you peasant...goto work!"],         \
                        ["Your lotto numbers set"],                ]

        messagelist2 = [ ["Items: ring"],        \
                         ["Lotto 1:"],            \
                         ["Next Creep Attack:"],            ]

        if gameactive is True:

            if msg.command == 'PRIVMSG':
                try:
                        checknick = irc.nick
                        checknet = self._getIrcName(irc)
                        chanmsgnick = msg.nick
                        (channel, text) = msg.args
                except ValueError:
                        return
                if "IRC connection timed out" in text:
                        return
                if "Disconnected from IRC" in text:
                        return
                if "Error from server: Closing Link" in text:
                        return
                if "Connected!" in text:
                        return
                        
                if(checknet == netname and checknick == supynick):
                        lifebuy = False
                        if botname in chanmsgnick and "and been defeated in combat!" in text and "is added to {0}'s clock".format(name) in text:
                                lifebuy = True
                        if botname in chanmsgnick and "has attacked a" in text and "is added to {0}'s clock".format(name) in text:
                                lifebuy = True
                        if botname in chanmsgnick and "tried to slay a" in text and "is added to {0}'s clock".format(name) in text:
                                lifebuy = True
                        if botname in chanmsgnick and "has challenged" in text and "is added to {0}'s clock".format(name) in text:
                                lifebuy = True
                        if botname in chanmsgnick and "has challenged {0}".format(name) in text and "and won!" in text:
                                lifebuy = True
                        if botname in chanmsgnick and "gold from {0}!".format(name) in text and "XP and loses" in text:
                                lifebuy = True
                        if lifebuy is True:
                                if(level >= 15 and buylife is True and life >= 0):
                                        self.usecommand(irc, "buy life")
                                        life = 100

                if(checknick == supynick and checknet == netname):
                        if(botname == chanmsgnick and "You are not logged in." in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text))
                            self.usecommand(irc, "login {0} {1}".format(name, pswd) )
                            interval = 60
                            self.looper(irc)
                            return               
                        for entry in messagelist:
                            if(botname == chanmsgnick and entry[0] in text):
                                if pmtextmode is True:
                                        self.reply(irc, playbottext + " - {0}".format(text))
                                return
                        for entry in messagelist2:
                            if(botname == chanmsgnick and entry[0] in text):
#                                self.reply(irc, playbottext + " - {0}".format(text))
                                return
                        if(botname == chanmsgnick and "You are {0}".format(name) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text))
                            return
        return msg

    def doNick(self, irc, msg):
        global netname
        global nickname
        global gameactive
        global bottextmode

        if gameactive is True:
            irc = self._getRealIrc(irc)
            newNick = msg.args[0]
            network = self._getIrcName(irc)
            if netname == network:
                    if nickname == msg.nick:
                        nickname = newNick
                        s = format(_('nick change by %s to %s'), msg.nick,newNick)
                        if bottextmode is True:
                                self.reply(irc, s)

    def _getRealIrc(self, irc):
        if isinstance(irc, irclib.Irc):
            return irc
        else:
            return irc.getRealIrc()
            
    def _getIrcName(self, irc):
        # We should allow abbreviations at some point.
        return irc.network

    def main(self, irc):
        global channame
        global botname
        global netname
        global otherIrc
        global supynick
        global botcheck
        global interval
        global webworks
        global rank
        global offline
        global playerspagelist
        global name
        global pswd
        global level
        global fights
        global gameactive
        global life
        global intervaltext
        global playbottext
        global bottextmode
        global errortextmode
        global botdisable1
        
        self.playbotcheck(irc)
        if intervaltext is True:
                self.reply(irc, playbottext + " - INTERVAL {0}".format(time.asctime()) )

        botcheck = False
        chancheck = False
        botdisable1 = False
        intervaldisable = False
        netcheck = True

        self.bottester(irc)

        try:
                checkotherIrc = self._getIrc(netname)
                if checkotherIrc.server == "unset":
                        if errortextmode is True:
                                self.reply(irc, playbottext + " - Server Error")
        except NameError:
                if errortextmode is True:
                        self.reply(irc, playbottext + " - Network not connected to supybot")
                netcheck = False

        chantest = otherIrc.state.channels
        for entry in chantest:
            if entry == channame:
                chancheck = True
        if chancheck is False:
            otherIrc.queueMsg(ircmsgs.join(channame))
            botcheck = False
        if chancheck is True:
            try:
                supynick = otherIrc.nick
                chanstate = otherIrc.state.channels[channame]
                users = [user for user in chanstate.users]
                for entry in users:
                    if botname == entry:
                        botcheck = True
                if botcheck is False:
                        if errortextmode is True:
                            self.reply(irc, playbottext + " - Game Bot not in channel")
            except KeyError:
                if errortextmode is True:
                        self.reply(irc, playbottext + " - Game Bot not in channel")

        if botcheck is True:
                self.webdata(irc)
                if webworks is True:
                        self.getvariables(irc)

        test = []
        offline = False
        rank = 0
        if webworks is True and gameactive is True and botcheck is True:
                for entry in playerspagelist:
                        if "playerview.php" in entry and name in entry:
                                test = entry
                if "offline" in test:
                        offline = True
                if offline is False:
                        test = test.split('">')
                        ranktext = test[1]
                        ranktext = ranktext.split("</")
                        rank = int(ranktext[0])
        if(webworks is True and offline is True):
                if errortextmode is True:
                        self.reply(irc, playbottext + " - Player Offline")

        if webworks is True and offline is True and botcheck is True:
                if netcheck is True:
                        self.usecommand(irc, "login {0} {1}".format(name, pswd) )
                        interval = 45
                        self.looper(irc)
                        intervaldisable = True

        if webworks is True and intervaldisable is False:
            self.intervalcalc(irc)
        if webworks is False and intervaldisable is False:
            interval = 300
            self.looper(irc)
               
        if webworks is True and offline is False and botcheck is True:
                self.playerarea(irc)
                self.spendmoney(irc)
                self.timercheck(irc)
                if(level >= 25 and fights >= 0 and fights < 5 and life > 0):
                        if bottextmode is True:
                                self.reply(irc, playbottext + " - Fights available")
                if(level >= 25 and fights >= 0 and fights < 5 and life > 10):
                        self.newlister(irc)
                        self.fight_fight(irc)

        return 1
    
    def intervalcalc(self, irc):
        global interval
        global level
        global fights
        global botcheck
        global offline
        global life
        global fightmode
        
        interval = 5
        interval *= 60                  # conv from min to sec

        if botcheck is False or offline is True:
            interval = 60
        if botcheck is True:
                if(level >= 25 and life > 10 and fightmode is True):
                        if(fights >= 0 and fights < 5):
                                interval = 120
        self.looper(irc)

    def looper(self, irc):
        global interval
        global gameactive
        global intervaltext
        global playbottext
        
        def loopqs():
            self.main(irc)
        nextTime = time.time() + interval
        
        if intervaltext is True:
                self.reply(irc, playbottext + " - Checking timers every {0} minutes".format(interval // 60))
        if gameactive is True:
            try:
                schedule.addEvent(loopqs, nextTime, "loopqs")
            except AssertionError:
                schedule.removeEvent('loopqs')
                schedule.addEvent(loopqs, nextTime, "loopqs")        

Class = QuakenetPlayBot


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
