###
# Copyright (c) 2021-2024, Russell Beech
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
import ssl

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
    _ = PluginInternationalization('QuakenetPlayBotMulti')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

__module_name__ = "Quakenet #IdleRPG Playbot Script"
__module_version__ = "1.7"
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

russweb = "http://russellb.x10.mx/"
gitweb = "https://github.com/RussellBeech/supybot-plugins"
gitweb2 = "https://raw.githubusercontent.com/RussellBeech/supybot-plugins/master/"
playerview = None 
playerview2 = None 
playerview3 = None 
playerview4 = None 
interval = 300
newlist = None
newlist2 = None
newlist3 = None
newlist4 = None
playerlist = None 
playerlist2 = None 
playerlist3 = None 
playerlist4 = None 
playerspage = None
playerspage2 = None
playerspage3 = None
playerspage4 = None
playerspagelist = None
itemslists = None
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
disableqplayerslistcommand = False # True = on, False = off - You can disable the qplayerslist command if there are multiple of them when running both single and multi together

# declare stats as global
name = None
pswd = None
name2 = None
pswd2 = None
name3 = None
pswd3 = None
name4 = None
pswd4 = None
char1 = False
char2 = False
char3 = False
char4 = False
botname = setbotname 
charcount = 0
level = 0
mysum = 0
itemSum = 0
expertSum = 0
attackslaySum = 0
itemSum2 = 0
expertSum2 = 0
attackslaySum2 = 0
itemSum3 = 0
expertSum3 = 0
attackslaySum3 = 0
itemSum4 = 0
expertSum4 = 0
attackslaySum4 = 0
ufightcalc = 0
ufightcalc2 = 0
ufightcalc3 = 0
ufightcalc4 = 0
gold = 0
rank = 0
rank2 = 0
rank3 = 0
rank4 = 0

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
expertitemb1 = 0
expertitemb2 = 0
expertitemb3 = 0
expertitemc1 = 0
expertitemc2 = 0
expertitemc3 = 0
expertitemd1 = 0
expertitemd2 = 0
expertitemd3 = 0
gems = 0
ability = None
xp = 0
life = 0
align = "n"
upgradelevel = 0

nickname = None
netname = None
nickname2 = None
netname2 = None
nickname3 = None
netname3 = None
nickname4 = None
netname4 = None
offline = None
offline2 = None
offline3 = None
offline4 = None
botcheck = None
botcheck2 = None
botcheck3 = None
botcheck4 = None
webworks = None
gameactive = None
lottonum1 = None
lottonum2 = None
lottonum3 = None
location = None
locationtime = 0

otherIrc = None
supynick = None
otherIrc2 = None
supynick2 = None
otherIrc3 = None
supynick3 = None
otherIrc4 = None
supynick4 = None
botdisable1 = False
botdisable2 = False
botdisable3 = False
botdisable4 = False
playbotcount = 0
playbottext = None
playbotid = "QM"
pbcount = 0

quake = False
quakemulti = False

fileprefix = "QuakenetPlayBotMulticonfig.txt"
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

class QuakenetPlayBotMulti(callbacks.Plugin):
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
        global gitweb2

        webversion = 0
        gitversion = 0
        newversion = 0
        try:
                if python3 is False:
                        text = urllib2.urlopen(russweb + "playbotversionquakesupy.txt")
                if python3 is True:
                        text = urllib.request.urlopen(russweb + "playbotversionquakesupy.txt")
                webversion = text.read()
                webversion = float( webversion )
                text.close()

        except:
                self.replymulti(irc, "Could not access {0}".format(russweb))

        try:
                if python3 is False:
                        text2 = urllib2.urlopen(gitweb2 + "playbotversionquakesupy.txt")
                if python3 is True:
                        text2 = urllib.request.urlopen(gitweb2 + "playbotversionquakesupy.txt")
                gitversion = text2.read()
                text2.close()
                if python3 is True:
                        gitversion = gitversion.decode("UTF-8")
                gitversion = float( gitversion )

        except:
                self.replymulti(irc, "Could not access {0}".format(gitweb2))

        self.replymulti(irc, "Current version {0}".format(currentversion))
        self.replymulti(irc, "Web version {0}".format(webversion))
        self.replymulti(irc, "GitHub version {0}".format(gitversion))
        if webversion > gitversion:
                newversion = webversion
        if webversion < gitversion:
                newversion = gitversion
        if webversion == gitversion:
                newversion = gitversion

        if newversion > 0:
                if(currentversion == newversion):
                        self.replymulti(irc, "You have the current version of PlayBot")
                if(currentversion < newversion):
                        self.replymulti(irc, "You have an old version of PlayBot")
                        self.replymulti(irc, "You can download a new version from {0} or {1}".format(russweb, gitweb))
                if(currentversion > newversion):
                        self.replymulti(irc, "Give me, Give me")

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

    def bottester(self, irc, num):
        global otherIrc
        global botname
        global channame
        global botdisable1
        global otherIrc2
        global botdisable2
        global otherIrc3
        global botdisable3
        global otherIrc4
        global botdisable4
        global char1
        global char2
        global char3
        global char4
        global setbotname
        
        botcount1 = 0
        botcount2 = 0
        botcount3 = 0
        botcount4 = 0
        botname = setbotname

        if num == 1 and char1 is True:
                bottest = botname
                botentry = []

                try:
                        ops = otherIrc.state.channels[channame].ops

                        for user in ops:
                                if bottest in user and user != bottest:
                                        botentry.append(user)
                                        botname10 = user

                except KeyError:
                    self.reply(irc, "Key Error",1)

                botcount1 = len(botentry)
                if botcount1 == 1:
                        botname = botname10
                if botcount1 >= 2:
                        botdisable1 = True
        if num == 2 and char2 is True:
                bottest = botname
                botentry = []

                try:
                        ops = otherIrc2.state.channels[channame].ops

                        for user in ops:
                                if bottest in user and user != bottest:
                                        botentry.append(user)
                                        botname10 = user

                except KeyError:
                    self.reply(irc, "Key Error",2)

                botcount2 = len(botentry)
                if botcount2 == 1:
                        botname = botname10
                if botcount2 >= 2:
                        botdisable2 = True
        if num == 3 and char3 is True:
                bottest = botname
                botentry = []

                try:
                        ops = otherIrc3.state.channels[channame].ops

                        for user in ops:
                                if bottest in user and user != bottest:
                                        botentry.append(user)
                                        botname10 = user

                except KeyError:
                    self.reply(irc, "Key Error",3)

                botcount3 = len(botentry)
                if botcount3 == 1:
                        botname = botname10
                if botcount3 >= 2:
                        botdisable3 = True
        if num == 4 and char4 is True:
                bottest = botname
                botentry = []

                try:
                        ops = otherIrc4.state.channels[channame].ops

                        for user in ops:
                                if bottest in user and user != bottest:
                                        botentry.append(user)
                                        botname10 = user

                except KeyError:
                    self.reply(irc, "Key Error",4)

                botcount4 = len(botentry)
                if botcount4 == 1:
                        botname = botname10
                if botcount4 >= 2:
                        botdisable4 = True

    def usecommand(self, irc, commanded, num):
        global botname
        global otherIrc
        global botdisable1
        global otherIrc2
        global botdisable2
        global otherIrc3
        global botdisable3
        global otherIrc4
        global botdisable4
        
        if num == 1:
                self.bottester(irc, 1)
        if num == 2:
                self.bottester(irc, 2)
        if num == 3:
                self.bottester(irc, 3)
        if num == 4:
                self.bottester(irc, 4)
        if(num == 1 and botdisable1 is False):
                otherIrc.queueMsg(ircmsgs.privmsg(botname, commanded))
        if(num == 2 and botdisable2 is False):
                otherIrc2.queueMsg(ircmsgs.privmsg(botname, commanded))
        if(num == 3 and botdisable3 is False):
                otherIrc3.queueMsg(ircmsgs.privmsg(botname, commanded))
        if(num == 4 and botdisable4 is False):
                otherIrc4.queueMsg(ircmsgs.privmsg(botname, commanded))

    def reply(self, irc, text, num):
        global nickname
        global nickname2
        global nickname3
        global nickname4
        global channame
        global otherIrc
        global otherIrc2
        global otherIrc3
        global otherIrc4
        global supynick
        global supynick2
        global supynick3
        global supynick4
        
        if num == 1:
                nickcheck = False
                try:
                    chanstate = otherIrc.state.channels[channame]
                    users = [user for user in chanstate.users]
                    for entry in users:
                        if nickname == entry:
                            nickcheck = True
                except KeyError:
                    return
        if num == 2:
                nickcheck2 = False
                try:
                    chanstate = otherIrc2.state.channels[channame]
                    users = [user for user in chanstate.users]
                    for entry in users:
                        if nickname2 == entry:
                            nickcheck2 = True
                except KeyError:
                    return
        if num == 3:
                nickcheck3 = False
                try:
                    chanstate = otherIrc3.state.channels[channame]
                    users = [user for user in chanstate.users]
                    for entry in users:
                        if nickname3 == entry:
                            nickcheck3 = True
                except KeyError:
                    return
        if num == 4:
                nickcheck4 = False
                try:
                    chanstate = otherIrc4.state.channels[channame]
                    users = [user for user in chanstate.users]
                    for entry in users:
                        if nickname4 == entry:
                            nickcheck4 = True
                except KeyError:
                    return

        if num == 1:
                if(nickcheck is True and nickname != supynick):
                        otherIrc.queueMsg(ircmsgs.privmsg(nickname, text))
        if num == 2:
                if(nickcheck2 is True and nickname2 != supynick2):
                        otherIrc2.queueMsg(ircmsgs.privmsg(nickname2, text))
        if num == 3:
                if(nickcheck3 is True and nickname3 != supynick3):
                        otherIrc3.queueMsg(ircmsgs.privmsg(nickname3, text))
        if num == 4:
                if(nickcheck4 is True and nickname4 != supynick4):
                        otherIrc4.queueMsg(ircmsgs.privmsg(nickname4, text))
            
    def replymulti(self, irc, text):
        global char1
        global char2
        global char3
        global char4

        if char1 is True:
                self.reply(irc, text, 1)
        if char2 is True:
                self.reply(irc, text, 2)
        if char3 is True:
                self.reply(irc, text, 3)
        if char4 is True:
                self.reply(irc, text, 4)

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
        global name2
        global pswd2
        global name3
        global pswd3
        global name4
        global pswd4
        global setbuy
        global buylife
        global netname
        global nickname
        global netname2
        global nickname2
        global netname3
        global nickname3
        global netname4
        global nickname4
        global gameactive
        global fightmode
        global charcount
        global otherIrc
        global supynick
        global otherIrc2
        global supynick2
        global otherIrc3
        global supynick3
        global otherIrc4
        global supynick4
        global char1
        global char2
        global char3
        global char4
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
                        irc.error("To log in use <bot> quakenetplaybotmulti login CharName Password" )
                        
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
                                singleplayerlist = self.singleread(irc)
                                try:
                                        singlename = singleplayerlist[0][1]
                                        singlenetname = singleplayerlist[0][3]
                                        if(name == singlename):
                                                irc.error("Character {0} is already logged in on QuakenetPlayBot".format(name))
                                                charcount = 0
                                        if(netname == singlenetname):
                                                irc.error("Character {0} is already logged in on QuakenetPlayBot".format(singlename))
                                                charcount = 0
                                except IndexError:
                                        irc.reply("No Players Logged in on QuakenetPlayBot", private=True)
                if charcount == 0:
                        gameactive = False
                        name = None
                        pswd = None

                if charcount == 1:
                        if(name != None and pswd != None):
                                char1 = True                    
                                self.usecommand(irc, "login {0} {1}".format(name, pswd), 1 )
        if charcount == 2:
                nickname2 = msg.nick
                netname2 = self._getIrcName(irc)
                supynick2 = irc.nick
                otherIrc2 = self._getIrc(netname2)
                namecheck2 = False

                if "undernet" in netname2 and channame.lower() == "#irpg":
                        irc.error("The #irpg game on Undernet is not supported.  Expect your head to explode if you continue")
                self.playbotcheck(irc)
                args2 = arg2.split(" ")

                try:
                        if(name2 is None or pswd2 is None):
                                name2 = args2[0]
                                pswd2 = args2[1]
                except IndexError:
                        irc.error("To log in use <bot> quakenetplaybotmulti login CharName Password" )
                        
                self.webdata(irc)
                if(name2 is None or pswd2 is None):
                        charcount = 1
                        irc.error("Login Failed")
                if charcount == 2:
                        try:
                                for entry in playerspagelist:
                                        if ">{0}<".format(name2) in entry:
                                                namecheck2 = True
                        except TypeError:
                                webworks = False
                        if(namecheck2 is False and webworks is True):
                                irc.error("LOGIN ERROR: {0} does not exist".format(name2))
                                charcount = 1
                if charcount == 2:
                        if pbcount == 2:
                                singleplayerlist = self.singleread(irc)
                                try:
                                        singlename = singleplayerlist[0][1]
                                        singlenetname = singleplayerlist[0][3]
                                        if(name2 == singlename):
                                                irc.error("Character {0} is already logged in on QuakenetPlayBot".format(name2))
                                                charcount = 1
                                        if(netname2 == singlenetname):
                                                irc.error("Character {0} is already logged in on QuakenetPlayBot".format(singlename))
                                                charcount = 1
                                except IndexError:
                                        irc.reply("No Players Logged in on QuakenetPlayBot", private=True)
                if charcount == 2:
                        if(supynick2 == supynick):
                                charcount = 1
                                irc.error("Character {0} is already logged in".format(name))
                        if(supynick2 != supynick):
                                if name2 != name:
                                        char2 = True
                                        self.usecommand(irc, "login {0} {1}".format(name2, pswd2), 2 )
                                if name2 == name:
                                        charcount = 1
                                        irc.error("Character {0} is already logged in".format(name))
                if charcount == 1:
                        char2 = False
                        netname2 = None
                        nickname2 = None
                        supynick2 = None
                        otherIrc2 = None
                        name2 = None
                        pswd2 = None
                        return

        if charcount == 3:
                nickname3 = msg.nick
                netname3 = self._getIrcName(irc)
                supynick3 = irc.nick
                otherIrc3 = self._getIrc(netname3)
                namecheck3 = False

                if "undernet" in netname3 and channame.lower() == "#irpg":
                        irc.error("The #irpg game on Undernet is not supported.  Expect your head to explode if you continue")
                self.playbotcheck(irc)
                args2 = arg2.split(" ")

                try:
                        if(name3 is None or pswd3 is None):
                                name3 = args2[0]
                                pswd3 = args2[1]
                except IndexError:
                        irc.error("To log in use <bot> quakenetplaybotmulti login CharName Password" )
                        
                self.webdata(irc)
                if(name3 is None or pswd3 is None):
                        charcount = 2
                        irc.error("Login Failed")
                if charcount == 3:
                        try:
                                for entry in playerspagelist:
                                        if ">{0}<".format(name3) in entry:
                                                namecheck3 = True
                        except TypeError:
                                webworks = False
                        if(namecheck3 is False and webworks is True):
                                irc.error("LOGIN ERROR: {0} does not exist".format(name3))
                                charcount = 2
                if charcount == 3:
                        if pbcount == 2:
                                singleplayerlist = self.singleread(irc)
                                try:
                                        singlename = singleplayerlist[0][1]
                                        singlenetname = singleplayerlist[0][3]
                                        if(name3 == singlename):
                                                irc.error("Character {0} is already logged in on QuakenetPlayBot".format(name3))
                                                charcount = 2
                                        if(netname3 == singlenetname):
                                                irc.error("Character {0} is already logged in on QuakenetPlayBot".format(singlename))
                                                charcount = 2
                                except IndexError:
                                        irc.reply("No Players Logged in on QuakenetPlayBot", private=True)
                if charcount == 3:
                        if(supynick3 != supynick and name3 != name and supynick3 != supynick2 and name3 != name2):
                                char3 = True
                                self.usecommand(irc, "login {0} {1}".format(name3, pswd3), 3 )
                        if(supynick3 == supynick or name3 == name):
                                charcount = 2
                                irc.error("Character {0} is already logged in".format(name))
                        if(supynick3 == supynick2 or name3 == name2):
                                charcount = 2
                                irc.error("Character {0} is already logged in".format(name2))
                if charcount == 2:
                        char3 = False
                        netname3 = None
                        nickname3 = None
                        supynick3 = None
                        otherIrc3 = None
                        name3 = None
                        pswd3 = None
                        return

        if charcount == 4:
                nickname4 = msg.nick
                netname4 = self._getIrcName(irc)
                supynick4 = irc.nick
                otherIrc4 = self._getIrc(netname4)
                namecheck4 = False

                if "undernet" in netname4 and channame.lower() == "#irpg":
                        irc.error("The #irpg game on Undernet is not supported.  Expect your head to explode if you continue")
                self.playbotcheck(irc)
                args2 = arg2.split(" ")

                try:
                        if(name4 is None or pswd4 is None):
                                name4 = args2[0]
                                pswd4 = args2[1]
                except IndexError:
                        irc.error("To log in use <bot> quakenetplaybotmulti login CharName Password" )
                        
                self.webdata(irc)
                if(name4 is None or pswd4 is None):
                        charcount = 3
                        irc.error("Login Failed")
                if charcount == 4:
                        try:
                                for entry in playerspagelist:
                                        if ">{0}<".format(name4) in entry:
                                                namecheck4 = True
                        except TypeError:
                                webworks = False
                        if(namecheck4 is False and webworks is True):
                                irc.error("LOGIN ERROR: {0} does not exist".format(name4))
                                charcount = 3
                if charcount == 4:
                        if pbcount == 2:
                                singleplayerlist = self.singleread(irc)
                                try:
                                        singlename = singleplayerlist[0][1]
                                        singlenetname = singleplayerlist[0][3]
                                        if(name4 == singlename):
                                                irc.error("Character {0} is already logged in on QuakenetPlayBot".format(name4))
                                                charcount = 3
                                        if(netname4 == singlenetname):
                                                irc.error("Character {0} is already logged in on QuakenetPlayBot".format(singlename))
                                                charcount = 3
                                except IndexError:
                                        irc.reply("No Players Logged in on QuakenetPlayBot", private=True)
                if charcount == 4:
                        if(supynick4 != supynick and name4 != name and supynick4 != supynick2 and name4 != name2 and supynick4 != supynick3 and name4 != name3):
                                char4 = True
                                self.usecommand(irc, "login {0} {1}".format(name4, pswd4), 4 )
                        if(supynick4 == supynick or name4 == name):
                                charcount = 3
                                irc.error("Character {0} is already logged in".format(name))
                        if(supynick4 == supynick2 or name4 == name2):
                                charcount = 3
                                irc.error("Character {0} is already logged in".format(name2))
                        if(supynick4 == supynick3 or name4 == name3):
                                charcount = 3
                                irc.error("Character {0} is already logged in".format(name3))
                if charcount == 3:
                        char4 = False
                        netname4 = None
                        nickname4 = None
                        supynick4 = None
                        otherIrc4 = None
                        name4 = None
                        pswd4 = None
                        return

        if (charcount >= 1 and charcount <= 4):        
                self.configcheck(irc)
                self.multiwrite(irc)
                time.sleep(3) # Needed
                self.usecommand(irc, "whoami", charcount)
                irc.reply("Player Character {0} has logged in".format(charcount), private=True)
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
                irc.reply("For a list of PlayBot commands use <bot> quakenetplaybotmulti help", private=True)
                irc.reply(" ", private=True)
        if charcount == 1:
                self.versionchecker(irc)
        if charcount >= 5:
            irc.error("You can only play with 4 character.")
            charcount = 4

        self.main(irc)

    login = wrap(login, [("checkCapability", "admin"), "text"])

    def logoutchar(self, irc, msg, args):
        """takes no arguments

        Logs you out of the PlayBot.
        """
        global charcount
        global char1
        global char2
        global char3
        global char4
        global netname
        global netname2
        global netname3
        global netname4
        global name
        global name2
        global name3
        global name4
        global pswd
        global pswd2
        global pswd3
        global pswd4
        global gameactive
        
        if gameactive is False:
            irc.error("You are not logged in")
        if gameactive is True:
                if charcount == 4:
                        irc.reply("{0} has logged out".format(name4), private=True)
                        char4 = False
                        netname4 = None
                        name4 = None
                        pswd4 = None
                        self.multiwrite(irc)
                if charcount == 3:
                        irc.reply("{0} has logged out".format(name3), private=True)
                        char3 = False
                        netname3 = None
                        name3 = None
                        pswd3 = None
                        self.multiwrite(irc)
                if charcount == 2:
                        irc.reply("{0} has logged out".format(name2), private=True)
                        char2 = False
                        netname2 = None
                        name2 = None
                        pswd2 = None
                        self.multiwrite(irc)
                if charcount == 1:
                        irc.reply("{0} has logged out".format(name), private=True)
                        char1 = False
                        netname = None
                        name = None
                        pswd = None
                        gameactive = False
                        try:
                            schedule.removeEvent('loopqm')
                        except KeyError:
                            irc.error("You are not logged in")
                        self.multieraser(irc)

        if charcount == 0:
            irc.error("All Characters have already been Logged Out")
        if(charcount >= 1 and charcount <= 4):
            charcount -= 1

    logoutchar = wrap(logoutchar, [("checkCapability", "admin")])

    def logoutgame(self, irc, msg, args, num):
        """<charnumber>

        Logs you out of MultiRPG.   Charnumber is 1 to 5, you can see which charnumber belongs to which char in settings.
        """
        global gameactive
        
        if gameactive is True:
                self.usecommand(irc, "logout", num)
        if gameactive is False:
            irc.error("You are not logged in")

    logoutgame = wrap(logoutgame, [("checkCapability", "admin"), "positiveInt"])

    if disableqplayerslistcommand is False:
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

    def multiwrite(self, irc):
        global name
        global name2
        global name3
        global name4
        global char1
        global char2
        global char3
        global char4
        global netname
        global netname2
        global netname3
        global netname4

        playerListM = []
        if char1 is True:
                playerListM.append( ( "name", name, "netname", netname ) )
        if char2 is True:
                playerListM.append( ( "name2", name2, "netname2", netname2 ) )
        if char3 is True:
                playerListM.append( ( "name3", name3, "netname3", netname3 ) )
        if char4 is True:
                playerListM.append( ( "name4", name4, "netname4", netname4 ) )
        f = open(filename4,"wb")
        pickle.dump(playerListM,f)
        f.close()

    def multieraser(self, irc):
        playerListM = []
        f = open(filename4,"wb")
        pickle.dump(playerListM,f)
        f.close()
        irc.reply("QuakeNet PlayerListM Erased", private=True)

    def qmultierase(self, irc, msg, args):
        """takes no arguments

        Erases playerList file
        """
        self.multieraser(irc)

    qmultierase = wrap(qmultierase, [("checkCapability", "admin")])

    def singleread(self, irc):
        try:
                f = open(filename3,"rb")
                playerListS = pickle.load(f)
                f.close()
        except IOError:
                playerListS = []
        except EOFError:
                playerListS = []
        except ValueError:
                playerListS = []
        return playerListS

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

    def updatenick(self, irc, msg, args, num):
        """<charnumber>

        Updates nickname the supybot sends info to.  Charnumber is 1 to 5, you can see which charnumber belongs to which char in settings.
        """
        global nickname
        global nickname2
        global nickname3
        global nickname4
        global gameactive
        global char1
        global char2
        global char3
        global char4

        if gameactive is True:
            if num == 1 and char1 is True:
                nickname = msg.nick
                s = format(_('nick updated to {0}'.format(nickname)))
                irc.reply(s, private=True)
            if num == 2 and char2 is True:
                nickname2 = msg.nick
                s = format(_('nick updated to {0}'.format(nickname2)))
                irc.reply(s, private=True)
            if num == 3 and char3 is True:
                nickname3 = msg.nick
                s = format(_('nick updated to {0}'.format(nickname3)))
                irc.reply(s, private=True)
            if num == 4 and char4 is True:
                nickname4 = msg.nick
                s = format(_('nick updated to {0}'.format(nickname4)))
                irc.reply(s, private=True)
        if gameactive is False:
            irc.error("You are not logged in")

    updatenick = wrap(updatenick, [("checkCapability", "admin"), "positiveInt"])

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
                self.replymulti(irc, "AutoConfig Off")

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
                        self.replymulti(irc, "Config Changed")
                        world.flush() 
                if configchange is False:
                        self.replymulti(irc, "Config OK")

    def cmd(self, irc, msg, args, text):
        """<text>

        Issue manual commands for the game
        """
        global gameactive
        global char1
        
        if(gameactive is True and char1 is True):
            try:
                    cmdtext = text
            except IndexError:
                    irc.error("To do manual commands use cmd text")
            self.usecommand(irc, "{0}".format(cmdtext), 1)
        if gameactive is False:
            irc.error("You are not logged in")

    cmd = wrap(cmd, [("checkCapability", "admin"), "text"])

    def cmd2(self, irc, msg, args, text):
        """<text>

        Issue manual commands for the game
        """
        global gameactive
        global char2

        if(gameactive is True and char2 is True):
            try:
                    cmdtext = text
            except IndexError:
                    irc.error("To do manual commands use cmd2 text")
            self.usecommand(irc, "{0}".format(cmdtext), 2)
        if gameactive is False:
            irc.error("You are not logged in")

    cmd2 = wrap(cmd2, [("checkCapability", "admin"), "text"])

    def cmd3(self, irc, msg, args, text):
        """<text>

        Issue manual commands for the game
        """
        global gameactive
        global char3

        if(gameactive is True and char3 is True):
            try:
                    cmdtext = text
            except IndexError:
                    irc.error("To do manual commands use cmd3 text")
            self.usecommand(irc, "{0}".format(cmdtext), 3)
        if gameactive is False:
            irc.error("You are not logged in")

    cmd3 = wrap(cmd3, [("checkCapability", "admin"), "text"])

    def cmd4(self, irc, msg, args, text):
        """<text>

        Issue manual commands for the game
        """
        global gameactive
        global char4

        if(gameactive is True and char4 is True):
            try:
                    cmdtext = text
            except IndexError:
                    irc.error("To do manual commands use cmd4 text")
            self.usecommand(irc, "{0}".format(cmdtext), 4)
        if gameactive is False:
            irc.error("You are not logged in")

    cmd4 = wrap(cmd4, [("checkCapability", "admin"), "text"])

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
            irc.reply("Erase PlayerList            - qmultierase", private=True)
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
            irc.reply("Log Out Game                - logoutgame charnum", private=True)
            irc.reply("Manual Command Char1        - cmd command", private=True)
            irc.reply("Manual Command Char2        - cmd2 command", private=True)
            irc.reply("Manual Command Char3        - cmd3 command", private=True)
            irc.reply("Manual Command Char4        - cmd4 command", private=True)
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
            irc.reply("Update Nick                 - updatenick charnum", private=True)
            irc.reply("Version Checker             - versioncheck", private=True)
            irc.reply("XPUpgrade Mode Off          - setoption xpupgrade false", private=True)
            irc.reply("XPUpgrade Mode On           - setoption xpupgrade true", private=True)
            irc.reply(" ", private=True)
            irc.reply("If you want more information about a command use <bot> help quakenetplaybotmulti <command> - ie /msg DudeRuss help quakenetplaybotmulti settings", private=True)

    help = wrap(help)

    def settings(self, irc, msg, args):
            """takes no arguments

            Gives a list of settings which you can change
            """
            global buylife
            global setbuy
            global char1
            global char2
            global char3
            global char4
            global name
            global name2
            global name3
            global name4
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
            irc.reply("Item Buy Level - {0}".format(setbuy), private=True)
            irc.reply("Player Character 1 - {0}, {1}  Player Character 2 - {2}, {3}".format(char1, name, char2, name2), private=True)
            irc.reply("Player Character 3 - {0}, {1}  Player Character 4 - {2}, {3}".format(char3, name3, char4, name4), private=True)
            irc.reply("Scrolls Buy ItemScore - {0}    Set Creep Target - {1}".format(scrollssum, setcreeptarget), private=True)
            irc.reply("SlaySum Minimum - {0}".format(slaysum), private=True)
            irc.reply("XPSpend Upgrade Amount - {0}   XPUpgrade Mode - {1}".format(xpspend, xpupgrade), private=True)

    settings = wrap(settings, [("checkCapability", "admin")])

    def newlister(self, irc, num):
        global playerspagelist
        global newlist
        global newlist2
        global newlist3
        global newlist4
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
        newlistererror = False

        if num == 1:
                newlist = []
        if num == 2:
                newlist2 = []
        if num == 3:
                newlist3 = []
        if num == 4:
                newlist4 = []

        self.getitems2(num)

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
                                        test = re.sub(r"&#039;", "'", test)
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
                                context = ssl._create_unverified_context()
                                if python3 is False:
                                        text = urllib2.urlopen(website + "/playerview.php?player={0}".format(name_), context=context)
                                if python3 is True:
                                        text = urllib.request.urlopen(website + "/playerview.php?player={0}".format(name_), context=context)
                                playerview20 = text.read()
                                text.close()
                                if python3 is True:
                                        playerview20 = playerview20.decode("UTF-8")
                        except:
                                weberror = True
                        if weberror is True:
                                if errortextmode is True:
                                        self.replymulti(irc, playbottext + " - Could not access {0}".format(website))
                                webworks2 = False

                        # build list for player records
                        if(playerview20 is None):
                                if errortextmode is True:
                                        self.replymulti(irc, playbottext + " - Could not access {0}, unknown error.".format(website) )
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
                                        
                                        if num == 1:
                                                                # name       sum   adjsum       level   life   ability   rank
                                                newlist.append( ( player[5], sum_, int(adjSum), level_, life_, ability_, rank_ ) )
                                        if num == 2:
                                                                 # name       sum   adjsum       level   life   ability   rank
                                                newlist2.append( ( player[5], sum_, int(adjSum), level_, life_, ability_, rank_ ) )
                                        if num == 3:
                                                                 # name       sum   adjsum       level   life   ability   rank 
                                                newlist3.append( ( player[5], sum_, int(adjSum), level_, life_, ability_, rank_ ) )
                                        if num == 4:
                                                                 # name       sum   adjsum       level   life   ability   rank 
                                                newlist4.append( ( player[5], sum_, int(adjSum), level_, life_, ability_, rank_ ) )
                                except:
                                        newlistererror = True

        if newlistererror is True:
                webworks = False
                if errortextmode is True:
                        self.replymulti(irc, playbottext + " - Newlister Error")

        if num == 1:
                newlist.sort( key=operator.itemgetter(1), reverse=True )
                newlist.sort( key=operator.itemgetter(3) )
        if num == 2:
                newlist2.sort( key=operator.itemgetter(1), reverse=True )
                newlist2.sort( key=operator.itemgetter(3) )
        if num == 3:
                newlist3.sort( key=operator.itemgetter(1), reverse=True )
                newlist3.sort( key=operator.itemgetter(3) )
        if num == 4:
                newlist4.sort( key=operator.itemgetter(1), reverse=True )
                newlist4.sort( key=operator.itemgetter(3) )

    def status(self, irc, msg, args):
            """takes no arguments

            Gives a list of character stats
            """
            global char1
            global char2
            global char3
            global char4
            global name
            global name2
            global name3
            global name4
            global botcheck
            global botcheck2
            global botcheck3
            global botcheck4
            global gameactive

            if gameactive is True:
                if char1 is True:
                        if botcheck is True:
                                self.reply(irc, "{0}'s Status".format(name),1)
                                self.reply(irc, " ",1)
                                self.characterstats(irc, 1)
                        if botcheck is False:
                                self.reply(irc, "Game Bot 1 not in channel",1)
                if char2 is True:
                        if botcheck2 is True:
                                self.reply(irc, "{0}'s Status".format(name2),2)
                                self.reply(irc, " ",2)
                                self.characterstats(irc, 2)
                        if botcheck2 is False:
                                self.reply(irc, "Game Bot 2 not in channel",2)
                if char3 is True:
                        if botcheck3 is True:
                                self.reply(irc, "{0}'s Status".format(name3),3)
                                self.reply(irc, " ",3)
                                self.characterstats(irc, 3)
                        if botcheck3 is False:
                                self.reply(irc, "Game Bot 3 not in channel",3)
                if char4 is True:
                        if botcheck4 is True:
                                self.reply(irc, "{0}'s Status".format(name4),4)
                                self.reply(irc, " ",4)
                                self.characterstats(irc, 4)
                        if botcheck4 is False:
                                self.reply(irc, "Game Bot 4 not in channel",4)
            if gameactive is False:
                irc.error("You are not logged in")

    status = wrap(status, [("checkCapability", "admin")])

    def characterstats(self, irc, num):
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
            global expertSum2
            global expertSum3
            global expertSum4
            global itemSum
            global attackslaySum
            global itemSum2
            global attackslaySum2
            global itemSum3
            global attackslaySum3
            global itemSum4
            global attackslaySum4
            global life
            global exp
            global scrolls
            global rank
            global rank2
            global rank3
            global rank4
            global lottonum1
            global lottonum2
            global lottonum3
            global align

            self.getitems2(num)

            if num == 1:
                itemSums = itemSum
                attackslaySums = attackslaySum
                expertSums = expertSum
                ranks = rank
            if num == 2:
                itemSums = itemSum2
                attackslaySums = attackslaySum2
                expertSums = expertSum2
                ranks = rank2
            if num == 3:
                itemSums = itemSum3
                attackslaySums = attackslaySum3
                expertSums = expertSum3
                ranks = rank3
            if num == 4:
                itemSums = itemSum4
                attackslaySums = attackslaySum4
                expertSums = expertSum4
                ranks = rank4

            self.reply(irc, "Rank: {0}  Level: {1}  Life: {2}  TTL: {3} secs".format(ranks, level, life, ttl),num)
            self.reply(irc, "Location: {0}  Time: {1} secs".format(location, locationtime),num)
            if align == "n":
                    self.reply(irc, "Alignment: Neutral",num)
            if align == "g":
                    self.reply(irc, "Alignment: Good",num)
            if align == "e":
                    self.reply(irc, "Alignment: Evil",num)
            if(level >= 15):
                    self.reply(irc, "Attack Recovery: {0} secs".format(atime),num)
            if(level < 15):
                    self.reply(irc, "Creep Attacks Start at Level 15",num)
            if(level >= 30):
                    self.reply(irc, "Slay Recovery: {0} secs".format(stime),num)
            if(level < 30):
                    self.reply(irc, "Slaying Monsters Start at Level 30",num)
            self.reply(irc, "Mana Potion: {0}".format(mana),num)
            if(level >= 25):
                    self.reply(irc, "Fights: {0} of 5".format(fights),num)
            if(level < 25):
                    self.reply(irc, "Fights Start at Level 25",num)
            self.reply(irc, "Gems: {0}  Gold: {1}  XP: {2}".format(gems, gold, xp),num)
            self.reply(irc, "Lotto1: {0}  Lotto2: {1}  Lotto3: {2}".format(lottonum1, lottonum2, lottonum3),num)
            self.reply(irc, "Exp Used: {0} of 5  Scrolls: {1} of 5".format(exp, scrolls), num)
            self.reply(irc, "Items Sum Score: {0}  Expert Items Score: {1}  Upgrade Level: {2}  Attack/SlaySum Item Score: {3}".format(itemSums, expertSums, upgradelevel, int(attackslaySums)),num)

    def items(self, irc, msg, args):
            """takes no arguments

            Gives a list of character item scores
            """
            global char1
            global char2
            global char3
            global char4
            global name
            global name2
            global name3
            global name4
            global botcheck
            global botcheck2
            global botcheck3
            global botcheck4
            global gameactive

            if gameactive is True:
                    if char1 is True:
                            if botcheck is True:
                                self.reply(irc, "{0}'s Items List".format(name), 1)
                                self.reply(irc, " ", 1)
                                self.characteritems(irc, 1)
                            if botcheck is False:
                                    self.reply(irc, "Game Bot 1 not in channel",1)
                    if char2 is True:
                            if botcheck2 is True:
                                self.reply(irc, "{0}'s Items List".format(name2), 2)
                                self.reply(irc, " ", 2)
                                self.characteritems(irc, 2)
                            if botcheck2 is False:
                                    self.reply(irc, "Game Bot 2 not in channel",2)
                    if char3 is True:
                            if botcheck3 is True:
                                self.reply(irc, "{0}'s Items List".format(name3), 3)
                                self.reply(irc, " ", 3)
                                self.characteritems(irc, 3)
                            if botcheck3 is False:
                                    self.reply(irc, "Game Bot 3 not in channel",3)
                    if char4 is True:
                            if botcheck4 is True:
                                self.reply(irc, "{0}'s Items List".format(name4), 4)
                                self.reply(irc, " ", 4)
                                self.characteritems(irc, 4)
                            if botcheck4 is False:
                                    self.reply(irc, "Game Bot 4 not in channel",4)
            if gameactive is False:
                    irc.error("You are not logged in")

    items = wrap(items, [("checkCapability", "admin")])

    def characteritems(self, irc, num):
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
            global itemSum2
            global itemSum3
            global itemSum4
            global stone1
            global stone2
            global stone3
            global expert1
            global expert2
            global expert3
            global expertitem1
            global expertitem2
            global expertitem3
            global expertitemb1
            global expertitemb2
            global expertitemb3
            global expertitemc1
            global expertitemc2
            global expertitemc3
            global expertitemd1
            global expertitemd2
            global expertitemd3

            self.getitems2(num)

            if num == 1:
                itemSums = itemSum
                expertitems1 = expertitem1
                expertitems2 = expertitem2
                expertitems3 = expertitem3
            if num == 2:
                itemSums = itemSum2
                expertitems1 = expertitemb1
                expertitems2 = expertitemb2
                expertitems3 = expertitemb3
            if num == 3:
                itemSums = itemSum3
                expertitems1 = expertitemc1
                expertitems2 = expertitemc2
                expertitems3 = expertitemc3
            if num == 4:
                itemSums = itemSum4
                expertitems1 = expertitemd1
                expertitems2 = expertitemd2
                expertitems3 = expertitemd3

            self.reply(irc, "Amulet: {0}  Boots: {1}  Charm: {2}  Gloves: {3}  Helm: {4}".format(amulet, boots, charm, gloves, helm), num)
            self.reply(irc, "Leggings: {0}  Ring: {1}  Shield: {2}  Tunic: {3}  Weapon: {4}".format(leggings, ring, shield, tunic, weapon), num)
            self.reply(irc, "Stones 1: {0}  2: {1}  3: {2}".format(stone1, stone2, stone2), num)
            self.reply(irc, "Items Sum Score: {0}".format(itemSums), num)
            self.reply(irc, "Expert Items 1: {0} {1}  2: {2} {3}  3: {4} {5}".format(expert1, expertitems1, expert2, expertitems2, expert3, expertitems3), num)

    def webdata(self, irc):
            global playerlist
            global playerlist2
            global playerlist3
            global playerlist4
            global name
            global name2
            global name3
            global name4
            global webworks
            global playerview
            global playerview2
            global playerview3
            global playerview4
            global char1
            global char2
            global char3
            global char4
            global python3
            global playerspage
            global playerspagelist
            global website
            global playbottext
            global errortextmode
            
            webworks = True
            weberror = False
            context = ssl._create_unverified_context()

            # get raw player data from web, parse for relevant entry
            if python3 is False:
                try:
                        if char1 is True:
                                text = urllib2.urlopen(website + "/playerview.php?player={0}".format(name), context=context)
                                playerview = text.read()
                                text.close()
                        if char2 is True:
                                textb = urllib2.urlopen(website + "/playerview.php?player={0}".format(name2), context=context)
                                playerview2 = textb.read()
                                textb.close()
                        if char3 is True:
                                textc = urllib2.urlopen(website + "/playerview.php?player={0}".format(name3), context=context)
                                playerview3 = textc.read()
                                textc.close()
                        if char4 is True:
                                textd = urllib2.urlopen(website + "/playerview.php?player={0}".format(name4), context=context)
                                playerview4 = textd.read()
                                textd.close()
                        text2 = urllib2.urlopen(website + "/players.php", context=context)
                        playerspage = text2.read()
                        text2.close()
                except:
                        weberror = True
            if python3 is True:
                try:
                        if char1 is True:
                                text = urllib.request.urlopen(website + "/playerview.php?player={0}".format(name), context=context)
                                playerview = text.read()
                                text.close()
                                playerview = playerview.decode("UTF-8")
                        if char2 is True:
                                textb = urllib.request.urlopen(website + "/playerview.php?player={0}".format(name2), context=context)
                                playerview2 = textb.read()
                                textb.close()
                                playerview2 = playerview2.decode("UTF-8")
                        if char3 is True:
                                textc = urllib.request.urlopen(website + "/playerview.php?player={0}".format(name3), context=context)
                                playerview3 = textc.read()
                                textc.close()
                                playerview3 = playerview3.decode("UTF-8")
                        if char4 is True:
                                textd = urllib.request.urlopen(website + "/playerview.php?player={0}".format(name4), context=context)
                                playerview4 = textd.read()
                                textd.close()
                                playerview4 = playerview4.decode("UTF-8")
                        text2 = urllib.request.urlopen(website + "/players.php", context=context)
                        playerspage = text2.read()
                        text2.close()
                        playerspage = playerspage.decode("UTF-8")
                except:
                        weberror = True

            if weberror is True:
                if errortextmode is True:
                        self.replymulti(irc, playbottext + " - Could not access {0}".format(website))
                webworks = False

            # build list for player records
            if char1 is True:
                    if(playerview is None):
                            if errortextmode is True:
                                    self.replymulti(irc, playbottext + " - Could not access {0}, unknown error.".format(website) )
                            webworks = False
                    else:
                            playerlist = playerview.split("\n")
                            playerlist = playerlist[:-1]
            if char2 is True:
                    if(playerview2 is None):
                            if errortextmode is True:
                                    self.replymulti(irc, playbottext + " - Could not access {0}, unknown error.".format(website) )
                            webworks = False
                    else:
                            playerlist2 = playerview2.split("\n")
                            playerlist2 = playerlist2[:-1]
            if char3 is True:
                    if(playerview3 is None):
                            if errortextmode is True:
                                    self.replymulti(irc, playbottext + " - Could not access {0}, unknown error.".format(website) )
                            webworks = False
                    else:
                            playerlist3 = playerview3.split("\n")
                            playerlist3 = playerlist3[:-1]
            if char4 is True:
                    if(playerview4 is None):
                            if errortextmode is True:
                                    self.replymulti(irc, playbottext + " - Could not access {0}, unknown error.".format(website) )
                            webworks = False
                    else:
                            playerlist4 = playerview4.split("\n")
                            playerlist4 = playerlist4[:-1]
            if(playerspage is None):
                    if errortextmode is True:
                            self.replymulti(irc, playbottext + " - Could not access {0}, unknown error.".format(website) )
                    webworks = False
            else:
                    playerspagelist = playerspage.split("\n")
                    playerspagelist = playerspagelist[:-1]

    def playerarea(self, irc, num):
        global level
        global mysum
        global location
        global locationtime
        global townworkswitch
        
        self.getitems2(num)
        
        if townworkswitch is True:
                area = "work"
        if townworkswitch is False:
                area = "forest"

#        self.reply(irc, "{0} {1} Time: {2} seconds".format(num, location, locationtime), num)
        if (level <= 25):
                mintime = (3 * 60 * 60)
        if (level > 25 and level <= 40):
                mintime = (6 * 60 * 60)
        if (level > 40 and level <= 50):
                mintime = (12 * 60 * 60)
        if (level > 50):
                mintime = (24 * 60 * 60)

        if locationtime == 0:
                self.usecommand(irc, "goto {0}".format(area), num)
                
        if(location == "In Town" and locationtime >= mintime and mysum < 6000 and mysum != 0):
                self.usecommand(irc, "goto {0}".format(area), num)
        if(location == "In Town" and mysum >= 6000):
                self.usecommand(irc, "goto {0}".format(area), num)
        if(location == "At Work" and locationtime >= mintime):
                self.usecommand(irc, "goto town", num)
        if(location == "In The Forest" and locationtime >= (24 * 60 * 60)):
                self.usecommand(irc, "goto town", num)

    def itemsbuilder(self, irc):
        global char1
        global char2
        global char3
        global char4
        global itemslists

        itemslists = []

        if char1 is True:
                itemslists.append( ( self.getvariables2(irc, 1) ) )
        if char2 is True:
                itemslists.append( ( self.getvariables2(irc, 2) ) )
        if char3 is True:
                itemslists.append( ( self.getvariables2(irc, 3) ) )
        if char4 is True:
                itemslists.append( ( self.getvariables2(irc, 4) ) )

    def getvariables2(self, irc, num):
        global playerlist
        global playerlist2
        global playerlist3
        global playerlist4
        global webworks
        global errortextmode
        
        if num == 1:
                playerlists = playerlist
        if num == 2:
                playerlists = playerlist2
        if num == 3:
                playerlists = playerlist3
        if num == 4:
                playerlists = playerlist4

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
        location_ = None
        locationtime_ = 0
        atwork = False
        intown = False
        intheforest = False                       

        if playerlists != None:
                for entry in playerlists:
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
                                        align_ = "n"
                                if "Evil" in aligntext:
                                        align_ = "e"
                                if "Good" in aligntext:
                                        align_ = "g"
                        except TypeError:
                                align_ = "n"
                        leveltext = leveltext.split(" ")
                        levelsplit = leveltext[7]
                        level_ = int(levelsplit.strip("<br"))
                        ttltext = ttltext.split(" ")
                        daystext = int(ttltext[8])
                        timetext = ttltext[10].strip("<br")
                        ttl_ = self.timetosecs(daystext, timetext)
                        goldtext = goldtext.split(" ")
                        goldsplit = goldtext[7]
                        gold_ = int(goldsplit.strip("<br"))
                        gemstext = gemstext.split(" ")
                        gemssplit = gemstext[7]
                        gems_ = int(gemssplit.strip("<br"))
                        upgradetext = upgradetext.split(" ")
                        upgradesplit = upgradetext[8]
                        upgradelevel_ = int(upgradesplit.strip("<br"))

                        if "Barbarian" in abilitytext:
                                ability_ = "b"
                        if "Rogue" in abilitytext:
                                ability_ = "r"
                        if "Paladin" in abilitytext:
                                ability_ = "p"
                        if "Wizard" in abilitytext:
                                ability_ = "w"

                        xptext = xptext.split(" ")
                        xpsplit = xptext[7]
                        xp_ = int(xpsplit.strip("<br"))
                        exptext = exptext.split(" ")
                        expsplit = exptext[8]
                        expsplit = expsplit.split("/")
                        try:
                                exp_ = int(expsplit[0])
                        except:
                                exp_ = 0
                        lifetext = lifetext.split(" ")
                        lifesplit = lifetext[7]
                        life_ = int(lifesplit.strip("<br"))
                        scrollstext = scrollstext.split(" ")
                        scrollssplit = scrollstext[8]
                        scrollssplit = scrollssplit.split("/")
                        try:
                                scrolls_ = int(scrollssplit[0])
                        except ValueError:
                                scrolls_ = 0
                        manatext = manatext.split(" ")
                        manasplit = manatext[8]
                        manasplit = manasplit.split("/")
                        mana_ = int(manasplit[0])

                        try:
                                atimetext = atimetext.split(" ")
                                daystext = int(atimetext[9])
                                timetext = atimetext[11].strip("<br")
                                atime_ = self.timetosecs(daystext, timetext)
                        except ValueError:
                                atime_ = 0
                        try:
                                stimetext = stimetext.split(" ")
                                daystext = int(stimetext[9])
                                timetext = stimetext[11].strip("<br")
                                stime_ = self.timetosecs(daystext, timetext)
                        except ValueError:
                                stime_ = 0

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

                        sumtext = sumtext.split(" ")
                        sumsplit = sumtext[7]
                        mysum_ = int(sumsplit.strip("<br"))
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
                        stonetext1 = stonetext1.split(" ")
                        stonesplit1 = stonetext1[8]
                        stonesplitsplit1 = stonesplit1.split("<")
                        stone1_ = stonesplitsplit1[0]
                        stonetext2 = stonetext2.split(" ")
                        stonesplit2 = stonetext2[8]
                        stonesplitsplit2 = stonesplit2.split("<")
                        stone2_ = stonesplitsplit2[0]
                        stonetext3 = stonetext3.split(" ")
                        stonesplit3 = stonetext3[8]
                        stonesplitsplit3 = stonesplit3.split("<")
                        stone3_ = stonesplitsplit3[0]
                        fightstext = fightstext.split(" ")
                        fightssplit = fightstext[13]
                        fights_ = int(fightssplit.strip("<br"))
                        lottonumtext1 = re.sub(r'<.*?>', ' ', lottonumtext1)
                        lottonumtext1 = lottonumtext1.split(" ")
                        lottonumtext2 = re.sub(r'<.*?>', ' ', lottonumtext2)
                        lottonumtext2 = lottonumtext2.split(" ")
                        lottonumtext3 = re.sub(r'<.*?>', ' ', lottonumtext3)
                        lottonumtext3 = lottonumtext3.split(" ")
                        lottonum1_ = "{0} {1} and {2}".format(lottonumtext1[11], lottonumtext1[12], lottonumtext1[13])                        
                        lottonum2_ = "{0} {1} and {2}".format(lottonumtext2[11], lottonumtext2[12], lottonumtext2[13])                        
                        lottonum3_ = "{0} {1} and {2}".format(lottonumtext3[11], lottonumtext3[12], lottonumtext3[13])                        

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
                                        locationtime_ = self.timetosecs(workdays, worksplittime)
                                        location_ = "At Work"
                                except ValueError:
                                        locationtime_ = 0
                                        location_ = "At Work"
                        if intown is True:
                                try:
                                        towntext = towntext.split(" ")
                                        towndays = int(towntext[8])
                                        townsplittime = towntext[10]
                                        townsplittime = townsplittime.strip("<br")
                                        locationtime_ = self.timetosecs(towndays, townsplittime)
                                        location_ = "In Town"
                                except ValueError:
                                        locationtime_ = 0
                                        location_ = "In Town"
                        if intheforest is True:
                                try:
                                        foresttext = foresttext.split(" ")
                                        forestdays = int(foresttext[8])
                                        forestsplittime = foresttext[10]
                                        forestsplittime = forestsplittime.strip("<br")
                                        locationtime_ = self.timetosecs(forestdays, forestsplittime)
                                        location_ = "In The Forest"
                                except ValueError:
                                        locationtime_ = 0
                                        location_ = "In The Forest"
                except:
                        webworks = False
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - {0} Variable Error".format(num))

                try:
                                    # num  mysum   level   life   ability   ttl 
                        itemslist = ( num, mysum_, level_, life_, ability_, ttl_, gold_, gems_, upgradelevel_, xp_, exp_, scrolls_, mana_, atime_, stime_, amulet_, boots_, charm_, gloves_, helm_, leggings_, ring_, shield_, tunic_, weapon_, expert1_, expert2_, expert3_, stone1_, stone2_, stone3_, fights_, align_, lottonum1_, lottonum2_, lottonum3_, location_, locationtime_ )
                except:
                        itemslist = ( num, None )
                        
        return itemslist

    def getitems2(self, num):
        global align
        global level
        global ttl
        global gold
        global gems
        global upgradelevel
        global ability
        global xp
        global exp
        global life
        global scrolls
        global mana
        global atime
        global stime

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

        global mysum
        global expert1
        global expert2
        global expert3
        global stone1
        global stone2
        global stone3
        global fights

        global itemslists
        global lottonum1
        global lottonum2
        global lottonum3
        global location
        global locationtime
        
#itemslists.append( ( player[5], mysum_, level_, life_, ability_, ttl_, gold_, gems_, upgradelevel_, xp_, exp_, scrolls_, mana_, atime_, stime_, amulet_, boots_, charm_, gloves_, helm_, leggings_, ring_, shield_, tunic_, weapon_, expert1_, expert2_, expert3_, stone1_, stone2_, stone3_, fights_, align_, lottonum1_, lottonum2_, lottonum3_, location_, locationtime_ ) )

        if itemslists != None:
                for entry in itemslists:
                        if(entry[0] == num and entry[1] != None):
                                mysum = entry[1]
                                level = entry[2]
                                life = entry[3]
                                ability = entry[4]
                                ttl = entry[5]
                                gold = entry[6]
                                gems = entry[7]
                                upgradelevel = entry[8]
                                xp = entry[9]
                                exp = entry[10]
                                scrolls = entry[11]
                                mana = entry[12]
                                atime = entry[13]
                                stime = entry[14]
                                amulet = entry[15]
                                boots = entry[16]
                                charm = entry[17]
                                gloves = entry[18]
                                helm = entry[19]
                                leggings = entry[20]
                                ring = entry[21]
                                shield = entry[22]
                                tunic = entry[23]
                                weapon = entry[24]
                                expert1 = entry[25]
                                expert2 = entry[26]
                                expert3 = entry[27]
                                stone1 = entry[28]
                                stone2 = entry[29]
                                stone3 = entry[30]
                                fights = entry[31]
                                align = entry[32]
                                lottonum1 = entry[33]
                                lottonum2 = entry[34]
                                lottonum3 = entry[35]
                                location = entry[36]
                                locationtime = entry[37]

    def timetosecs(self, days, timetext):
        timesecs = 0
        splittime = timetext.split(":")
        hours = int(splittime[0])
        mins = int(splittime[1])
        secs = int(splittime[2])
        timesecs = ((days * 24 * 60 * 60) + (hours * 60 * 60) + (mins * 60) + secs)
        return timesecs

    def timercheck(self, irc, num):
            global ttl
            global interval
            global atime
            global stime
            global level
            global attackslaySum
            global attackslaySum2
            global attackslaySum3
            global attackslaySum4
            global mana
            global gold
            global life
            global slaysum
            global playbotext
            global bottextmode
            
            self.getitems2(num)

            if num == 1:
                attackslaySumlist = attackslaySum
            if num == 2:
                attackslaySumlist = attackslaySum2
            if num == 3:
                attackslaySumlist = attackslaySum3
            if num == 4:
                attackslaySumlist = attackslaySum4

            # make sure no times are negative
            if(atime < 0):
                    atime = 0
            if(stime < 0):
                    stime = 0
#            self.reply(irc, "{0} atime {1}  stime {2}  ttl {3}".format(num, atime, stime, ttl), num)
            slaydisable = False
            
            def lvlupgoqm1():
                self.lvlup(irc, 1)
            def lvlupgoqm2():
                self.lvlup(irc, 2)
            def lvlupgoqm3():
                self.lvlup(irc, 3)
            def lvlupgoqm4():
                self.lvlup(irc, 4)
            
            def attackgoqm1():
                self.attack(irc, 1)
            def attackgoqm2():
                self.attack(irc, 2)
            def attackgoqm3():
                self.attack(irc, 3)
            def attackgoqm4():
                self.attack(irc, 4)

            def slaygoqm1():
                self.slay(irc, 1, 1)
            def slaygobqm1():
                self.slay(irc, 2, 1)
            def slaygoqm2():
                self.slay(irc, 1, 2)
            def slaygobqm2():
                self.slay(irc, 2, 2)
            def slaygoqm3():
                self.slay(irc, 1, 3)
            def slaygobqm3():
                self.slay(irc, 2, 3)
            def slaygoqm4():
                self.slay(irc, 1, 4)
            def slaygobqm4():
                self.slay(irc, 2, 4)

            if(ttl <= interval and ttl > 0):
                    timer = time.time() + (ttl+10)
                    if bottextmode is True:
                            self.replymulti(irc, playbottext + " - Set lvlup {0} timer. Going off in {1} minutes.".format(num, ttl // 60))
                    if num == 1:
                        try:
                            schedule.addEvent(lvlupgoqm1, timer, "lvlupqm1")
                        except AssertionError:
                            schedule.removeEvent('lvlupqm1')
                            schedule.addEvent(lvlupgoqm1, timer, "lvlupqm1")                        
                    if num == 2:
                        try:
                            schedule.addEvent(lvlupgoqm2, timer, "lvlupqm2")
                        except AssertionError:
                            schedule.removeEvent('lvlupqm2')
                            schedule.addEvent(lvlupgoqm2, timer, "lvlupqm2")                        
                    if num == 3:
                        try:
                            schedule.addEvent(lvlupgoqm3, timer, "lvlupqm3")
                        except AssertionError:
                            schedule.removeEvent('lvlupqm3')
                            schedule.addEvent(lvlupgoqm3, timer, "lvlupqm3")                        
                    if num == 4:
                        try:
                            schedule.addEvent(lvlupgoqm4, timer, "lvlupqm4")
                        except AssertionError:
                            schedule.removeEvent('lvlupqm4')
                            schedule.addEvent(lvlupgoqm4, timer, "lvlupqm4")                        
            if(level >= 15 and atime <= interval and atime <= ttl and life > 10):
                    timer = time.time() + (atime+10)
                    if bottextmode is True:
                            self.replymulti(irc, playbottext + " - Set attack {0} timer. Going off in {1} minutes.".format(num, atime // 60))
                    slaydisable = True
                    if num == 1:
                        try:
                            schedule.addEvent(attackgoqm1, timer, "attackqm1")
                        except AssertionError:
                            schedule.removeEvent('attackqm1')
                            schedule.addEvent(attackgoqm1, timer, "attackqm1")                        
                    if num == 2:
                        try:
                            schedule.addEvent(attackgoqm2, timer, "attackqm2")
                        except AssertionError:
                            schedule.removeEvent('attackqm2')
                            schedule.addEvent(attackgoqm2, timer, "attackqm2")                        
                    if num == 3:
                        try:
                            schedule.addEvent(attackgoqm3, timer, "attackqm3")
                        except AssertionError:
                            schedule.removeEvent('attackqm3')
                            schedule.addEvent(attackgoqm3, timer, "attackqm3")                        
                    if num == 4:
                        try:
                            schedule.addEvent(attackgoqm4, timer, "attackqm4")
                        except AssertionError:
                            schedule.removeEvent('attackqm4')
                            schedule.addEvent(attackgoqm4, timer, "attackqm4")                        
            if(level >= 30 and attackslaySumlist >= 1000 and stime <= interval and stime <= ttl and slaydisable is False and life > 10):
                    if(mana == 0 and gold >= 1100 and attackslaySumlist < 150000):
                        self.usecommand(irc, "buy mana", num)
                        gold -= 1000
                        mana = 1
                    timer = time.time() + (stime+10)
                    if mana == 0 and attackslaySumlist >= slaysum:
                            if bottextmode is True:
                                    self.replymulti(irc, playbottext + " - Set slay {0} timer. Going off in {1} minutes.".format(num, stime // 60))
                            if num == 1:
                                try:
                                    schedule.addEvent(slaygoqm1, timer, "slayqm1")
                                except AssertionError:
                                    schedule.removeEvent('slayqm1')
                                    schedule.addEvent(slaygoqm1, timer, "slayqm1")
                            if num == 2:
                                try:
                                    schedule.addEvent(slaygoqm2, timer, "slayqm2")
                                except AssertionError:
                                    schedule.removeEvent('slayqm2')
                                    schedule.addEvent(slaygoqm2, timer, "slayqm2")
                            if num == 3:
                                try:
                                    schedule.addEvent(slaygoqm3, timer, "slayqm3")
                                except AssertionError:
                                    schedule.removeEvent('slayqm3')
                                    schedule.addEvent(slaygoqm3, timer, "slayqm3")
                            if num == 4:
                                try:
                                    schedule.addEvent(slaygoqm4, timer, "slayqm4")
                                except AssertionError:
                                    schedule.removeEvent('slayqm4')
                                    schedule.addEvent(slaygoqm4, timer, "slayqm4")
                    if mana == 1:
                            if bottextmode is True:
                                    self.replymulti(irc, playbottext + " - Set slay {0} timer. Going off in {1} minutes.".format(num, stime // 60))
                            mana = 0
                            if num == 1:
                                try:
                                    schedule.addEvent(slaygobqm1, timer, "slayqm1")
                                except AssertionError:
                                    schedule.removeEvent('slayqm1')
                                    schedule.addEvent(slaygobqm1, timer, "slayqm1")
                            if num == 2:
                                try:
                                    schedule.addEvent(slaygobqm2, timer, "slayqm2")
                                except AssertionError:
                                    schedule.removeEvent('slayqm2')
                                    schedule.addEvent(slaygobqm2, timer, "slayqm2")
                            if num == 3:
                                try:
                                    schedule.addEvent(slaygobqm3, timer, "slayqm3")
                                except AssertionError:
                                    schedule.removeEvent('slayqm3')
                                    schedule.addEvent(slaygobqm3, timer, "slayqm3")
                            if num == 4:
                                try:
                                    schedule.addEvent(slaygobqm4, timer, "slayqm4")
                                except AssertionError:
                                    schedule.removeEvent('slayqm4')
                                    schedule.addEvent(slaygobqm4, timer, "slayqm4")

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

    def spendmoney(self, irc, num):
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
        global itemSum2
        global expertSum2
        global attackslaySum2
        global itemSum3
        global expertSum3
        global attackslaySum3
        global itemSum4
        global expertSum4
        global attackslaySum4
        global expertitem1
        global expertitem2
        global expertitem3
        global expertitemb1
        global expertitemb2
        global expertitemb3
        global expertitemc1
        global expertitemc2
        global expertitemc3
        global expertitemd1
        global expertitemd2
        global expertitemd3
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
        
        self.getitems2(num)

        lowestitem = self.worstitem(num)
#        self.reply(irc, "{0} Worst item {1}".format(num, lowestitem), num)

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
                self.usecommand(irc, "buy life", num)
                gold -= lifebuy
                life = 100
                
        gembuy = True
        if(level >= 35):
                if upgradelevel == 0 and gold < 600:
                        gembuy = False
                if upgradelevel == 0 and gold >= 600:
                        self.usecommand(irc, "buy upgrade", num)
                        gold -= 500
                        upgradelevel = 1
        if(level >= 40):
                if upgradelevel == 1 and gold < 1100:
                        gembuy = False
                if upgradelevel == 1 and gold >= 1100:
                        self.usecommand(irc, "buy upgrade", num)
                        gold -= 1000
                        upgradelevel = 2
        if(level >= 45):
                if upgradelevel == 2 and gold < 2100:
                        gembuy = False
                if upgradelevel == 2 and gold >= 2100:
                        self.usecommand(irc, "buy upgrade", num)
                        gold -= 2000
                        upgradelevel = 3
        if(level >= 50):
                if upgradelevel == 3 and gold < 4100:
                        gembuy = False
                if upgradelevel == 3 and gold >= 4100:
                        self.usecommand(irc, "buy upgrade", num)
                        gold -= 4000
                        upgradelevel = 4
        if(level >= 60):
                if upgradelevel == 4 and gold < 8100:
                        gembuy = False
                if upgradelevel == 4 and gold >= 8100:
                        self.usecommand(irc, "buy upgrade", num)
                        gold -= 8000
                        upgradelevel = 5
                
        if(gembuy is True and expbuy is True and exp < 5):
                expdiff = 5 - exp
                expcost = expdiff * 500
                if(gold >= (expcost + 1100)):
                        for i in range(expdiff):
                                self.usecommand(irc, "buy experience", num)
                                gold -= 500
                                exp += 1
                elif(gold >= 500 + 1100):
                        golddiff = gold - 1100
                        expcalc = golddiff // 500
                        if expcalc >= 1:
                                for i in range(expcalc):
                                        self.usecommand(irc, "buy experience", num)
                                        gold -= 5000
                                        exp += 1

#        self.reply(irc, "{0} goldsave: {1}  gembuy: {2}  level: {3}  upgradelevel: {4}  align: {5}".format(num, goldsave, gembuy, level, upgradelevel, align), num)
        
        if(level >= setbuy):
                buycost = level * 2 * 3
                buyitem = level * 2     
                buydiff = 19
                if(gold > buycost + 100):
                        if(amulet < (buyitem - buydiff)):
                                self.usecommand(irc, "buy amulet {0}".format(buyitem), num)
                                gold -= buycost
                                amulet = buyitem
                if(gold > buycost + 100):
                        if(boots < (buyitem - buydiff)):
                                self.usecommand(irc, "buy boots {0}".format(buyitem), num)
                                gold -= buycost
                                boots = buyitem
                if(gold > buycost + 100):
                        if(charm < (buyitem - buydiff)):
                                self.usecommand(irc, "buy charm {0}".format(buyitem), num)
                                gold -= buycost
                                charm = buyitem
                if(gold > buycost + 100):
                        if(gloves < (buyitem - buydiff)):
                                self.usecommand(irc, "buy gloves {0}".format(buyitem), num)
                                gold -= buycost
                                gloves = buyitem
                if(gold > buycost + 100):
                        if(helm < (buyitem - buydiff)):
                                self.usecommand(irc, "buy helm {0}".format(buyitem), num)
                                gold -= buycost
                                helm = buyitem
                if(gold > buycost + 100):
                        if(leggings < (buyitem - buydiff)):
                                self.usecommand(irc, "buy leggings {0}".format(buyitem), num)
                                gold -= buycost
                                leggings = buyitem
                if(gold > buycost + 100):
                        if(ring < (buyitem - buydiff)):
                                self.usecommand(irc, "buy ring {0}".format(buyitem), num)
                                gold -= buycost
                                ring = buyitem
                if(gold > buycost + 100):
                        if(shield < (buyitem - buydiff)):
                                self.usecommand(irc, "buy shield {0}".format(buyitem), num)
                                gold -= buycost
                                shield = buyitem
                if(gold > buycost + 100):
                        if(tunic < (buyitem - buydiff)):
                                self.usecommand(irc, "buy tunic {0}".format(buyitem), num)
                                gold -= buycost
                                tunic = buyitem
                if(gold > buycost + 100):
                        if(weapon < (buyitem - buydiff)):
                                self.usecommand(irc, "buy weapon {0}".format(buyitem), num)
                                gold -= buycost
                                weapon = buyitem

        if(level >= 25):
                if(gems < 15):
                        if getgems is True and gembuy is True:
                                gemdiff = 15 - gems
                                gemcost = gemdiff * 150
                                if gold > (goldsave + gemcost):
                                        self.usecommand(irc, "get {0} gems".format(gemdiff), num)
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
                                        self.usecommand(irc, "get {0} gems".format(gemdiff), num)
                                        gold -= gemcost
                                        gems += gemdiff
                                
                                moneycalc = gold - goldsave
                                gemcalc = moneycalc // 150
                                if(gemcalc >= 15):
                                        gems15 = gemcalc // 15
                                        if(gems15 >= 1):
                                                buymoney = gems15 * 150 * 15
                                                buygems = gems15 * 15
                                                self.usecommand(irc, "get {0} gems".format(buygems), num)
                                                gold -= buymoney
                                                gems += buygems

                        blackbuydisable = False
                        if(blackbuyspend14 is True):
                                if(gems >= (15 * 14)):
                                        self.usecommand(irc, "blackbuy {0} 14".format(lowestitem[0]), num)
                                        gems -= (15 * 14) 
                                        if(gems >= 15):
                                                interval = 120
                                                self.looper(irc)
                                                blackbuydisable = True

                        if(blackbuyspend is True and blackbuydisable is False):
                                if(gems >= 15):
                                        gemspend15 = gems // 15
                                        if(gemspend15 >= 1):
                                                self.usecommand(irc, "blackbuy {0} {1}".format(lowestitem[0], gemspend15), num)
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
                                        self.usecommand(irc, "xpget scroll", num)
                                        xp -= 20
                                        scrolls += 1
                        elif(xp >= 20):
                                xpcalc = xp // 20
                                if xpcalc >= 1:
                                        for i in range(xpcalc):
                                                self.usecommand(irc, "xpget scroll", num)
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
                                        self.usecommand(irc, "xpget {0} {1}".format(lowestitem[0], xpspend), num)
                                        xp -= xpspend

        if num == 1:
                expertitem1 = self.expertcalc(expert1)
                expertitem2 = self.expertcalc(expert2)
                expertitem3 = self.expertcalc(expert3)
        if num == 2:
                expertitemb1 = self.expertcalc(expert1)
                expertitemb2 = self.expertcalc(expert2)
                expertitemb3 = self.expertcalc(expert3)
        if num == 3:
                expertitemc1 = self.expertcalc(expert1)
                expertitemc2 = self.expertcalc(expert2)
                expertitemc3 = self.expertcalc(expert3)
        if num == 4:
                expertitemd1 = self.expertcalc(expert1)
                expertitemd2 = self.expertcalc(expert2)
                expertitemd3 = self.expertcalc(expert3)
           
        lifepercent = (float(life) / 100)
        if num == 1:
                itemSum = (amulet + charm + helm + boots + gloves + ring + leggings + shield + tunic + weapon)
                expertSum = expertitem1 + expertitem2 + expertitem3 
        if num == 2:
                itemSum2 = (amulet + charm + helm + boots + gloves + ring + leggings + shield + tunic + weapon)
                expertSum2 = expertitemb1 + expertitemb2 + expertitemb3 
        if num == 3:
                itemSum3 = (amulet + charm + helm + boots + gloves + ring + leggings + shield + tunic + weapon)
                expertSum3 = expertitemc1 + expertitemc2 + expertitemc3 
        if num == 4:
                itemSum4 = (amulet + charm + helm + boots + gloves + ring + leggings + shield + tunic + weapon)
                expertSum4 = expertitemd1 + expertitemd2 + expertitemd3 
        upgradeSum1 = upgradelevel * 100
        if num == 1:
                attackslaySum = (itemSum + expertSum + upgradeSum1) * lifepercent
        if num == 2:
                attackslaySum2 = (itemSum2 + expertSum2 + upgradeSum1) * lifepercent
        if num == 3:
                attackslaySum3 = (itemSum3 + expertSum3 + upgradeSum1) * lifepercent
        if num == 4:
                attackslaySum4 = (itemSum4 + expertSum4 + upgradeSum1) * lifepercent

    def lvlup(self, irc, num):
            global name
            global name2
            global name3
            global name4
            global level
            global interval
            global life
            global playbottext
            global bottextmode
           
            self.getitems2(num)
            if num == 1:
                namelist = name
            if num == 2:
                namelist = name2
            if num == 3:
                namelist = name3
            if num == 4:
                namelist = name4

            level += 1

            if bottextmode is True:
                    self.replymulti(irc, playbottext + " - {0} has reached level {1}!".format(namelist, level))

            interval = 60
            self.looper(irc)

            def attackgoqm1():
                    self.attack(irc, 1)
            def attackgoqm2():
                    self.attack(irc, 2)
            def attackgoqm3():
                    self.attack(irc, 3)
            def attackgoqm4():
                    self.attack(irc, 4)

            if(level >= 16 and life > 10):
                            if num == 1:
                                try:
                                        schedule.addEvent(attackgoqm1, 0, "attackqm1")
                                except AssertionError:
                                        schedule.removeEvent('attackqm1')
                                        schedule.addEvent(attackgoqm1, 0, "attackqm1")                        
                            if num == 2:
                                try:
                                        schedule.addEvent(attackgoqm2, 0, "attackqm2")
                                except AssertionError:
                                        schedule.removeEvent('attackqm2')
                                        schedule.addEvent(attackgoqm2, 0, "attackqm2")                        
                            if num == 3:
                                try:
                                        schedule.addEvent(attackgoqm3, 0, "attackqm3")
                                except AssertionError:
                                        schedule.removeEvent('attackqm3')
                                        schedule.addEvent(attackgoqm3, 0, "attackqm3")                        
                            if num == 4:
                                try:
                                        schedule.addEvent(attackgoqm4, 0, "attackqm4")
                                except AssertionError:
                                        schedule.removeEvent('attackqm4')
                                        schedule.addEvent(attackgoqm4, 0, "attackqm4")                        

    def fight_fight(self, irc, num):
            global name
            global name2
            global name3
            global name4
            global level
            global ufightcalc
            global ufightcalc2
            global ufightcalc3
            global ufightcalc4
            global itemSum
            global expertSum
            global itemSum2
            global expertSum2
            global itemSum3
            global expertSum3
            global itemSum4
            global expertSum4
            global fights
            global rank
            global rank2
            global rank3
            global rank4
            global ability
            global upgradelevel
            global life
            global fightmode
            global playbottext
            global bottextmode

            self.getitems2(num)

            if num == 1:
                ufight = self.testfight(1)
                namelist = name
                itemSumlist = itemSum
                expertSumlist = expertSum
                ranklist = rank
            if num == 2:
                ufight = self.testfight(2)
                namelist = name2
                itemSumlist = itemSum2
                expertSumlist = expertSum2
                ranklist = rank2
            if num == 3:
                ufight = self.testfight(3)
                namelist = name3
                itemSumlist = itemSum3
                expertSumlist = expertSum3
                ranklist = rank3
            if num == 4:
                ufight = self.testfight(4)
                namelist = name4
                itemSumlist = itemSum4
                expertSumlist = expertSum4
                ranklist = rank4

            upgradeSum1 = upgradelevel * 100
            fightSumTotal = itemSumlist + expertSumlist
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
        
            if num == 1:
                ufightcalc = fightAdj / ufight[2]
            if num == 2:
                ufightcalc2 = fightAdj / ufight[2]
            if num == 3:
                ufightcalc3 = fightAdj / ufight[2]
            if num == 4:
                ufightcalc4 = fightAdj / ufight[2]

            if(level >= 25):
                if num == 1:
                        ufightcalclist = ufightcalc
                if num == 2:
                        ufightcalclist = ufightcalc2
                if num == 3:
                        ufightcalclist = ufightcalc3
                if num == 4:
                        ufightcalclist = ufightcalc4
                if bottextmode is True:
                        self.replymulti(irc, playbottext + " - {0} Best fight for Rank {1}:  {2}  [{3}]  Opponent: Rank {4}:  {5}  [{6}], Odds {7}".format(num, ranklist, namelist, int(fightAdj), ufight[6], ufight[0], int(ufight[2]), ufightcalclist))
                if(ufightcalclist >= 0.9 and fightmode is True):
                        self.usecommand(irc, "fight {0}".format( ufight[0] ), num)
                        fights += 1

    def testfight(self, num):
        global newlist
        global newlist2
        global newlist3
        global newlist4
        global level
        global name
        global name2
        global name3
        global name4
        global upgradelevel
        global itemSum
        global expertSum
        global itemSum2
        global expertSum2
        global itemSum3
        global expertSum3
        global itemSum4
        global expertSum4
        global ability
        global life

        self.getitems2(num)
            
        if num == 1:
                newlists = newlist
                namelist = name
                itemSumlist = itemSum
                expertSumlist = expertSum
        if num == 2:
                newlists = newlist2
                namelist = name2
                itemSumlist = itemSum2
                expertSumlist = expertSum2
        if num == 3:
                newlists = newlist3
                namelist = name3
                itemSumlist = itemSum3
                expertSumlist = expertSum3
        if num == 4:
                newlists = newlist4
                namelist = name4
                itemSumlist = itemSum4
                expertSumlist = expertSum4

        upgradeSum1 = upgradelevel * 100
        fightSumTotal = float(itemSumlist + expertSumlist)
        lifepercent = (float(life) / 100)
        test = []
        
        diff = 0
        best = ("Doctor Who?", 9999999999.0, 9999999999.0, 0, 0, "p", 0)
        newlists.sort( key=operator.itemgetter(2))
        if newlists != None:
                for entry in newlists:
                        if(entry[3] >= level and entry[0] != namelist):
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

    def attack(self, irc, num):
        global creepattack
        global setcreeptarget
        
        if creepattack is True:
            creep = self.bestattack(num)
            if creep != "CreepList Error":
                    self.usecommand(irc, "attack " + creep, num)
            if creep == "CreepList Error":
                    self.reply(irc, "{0}".format(creep), num)
        if creepattack is False:
                self.usecommand(irc, "attack " + setcreeptarget, num)

    def slay(self, irc, num2, num):
        monster = self.bestslay(num2, num)
        if monster != "MonsterList Error":
                self.usecommand(irc, "slay " + monster, num)
        if monster == "MonsterList Error":
                self.reply(irc, "{0}".format(monster), num)

    def bestattack(self, num):
        global creeps
        global attackslaySum
        global attackslaySum2
        global attackslaySum3
        global attackslaySum4
              
        if num == 1:
                attackslaySumlist = attackslaySum
        if num == 2:
                attackslaySumlist = attackslaySum2
        if num == 3:
                attackslaySumlist = attackslaySum3
        if num == 4:
                attackslaySumlist = attackslaySum4

        good = "CreepList Error"
        for thing in creeps:
                if(attackslaySumlist <= thing[1]):
                        good = thing[0]
        return good

    def bestslay(self, num2, num):
        global monsters
        global attackslaySum
        global attackslaySum2
        global attackslaySum3
        global attackslaySum4
               
        if num == 1:
                attackslaySumlist = attackslaySum
        if num == 2:
                attackslaySumlist = attackslaySum2
        if num == 3:
                attackslaySumlist = attackslaySum3
        if num == 4:
                attackslaySumlist = attackslaySum4

        good = "MonsterList Error"
        if num2 == 1:
                multi = 1
        if num2 == 2:
                multi = 2
        for thing in monsters:
                if((attackslaySumlist * multi) <= thing[1]):
                        good = thing[0]
        return good

    def worstitem(self, num):
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
        global name2
        global pswd2
        global name3
        global pswd3
        global name4
        global pswd4
        global char1
        global char2
        global char3
        global char4
        global otherIrc
        global netname
        global otherIrc2
        global netname2
        global otherIrc3
        global netname3
        global otherIrc4
        global netname4
        global gameactive
        global interval
        global supynick
        global supynick2
        global supynick3
        global supynick4

        global life
        global level
        global buylife
        global playbottext
        global itemslists
        global pmtextmode

        messagelist = [ ["You are not recovered"],    \
                        ["FIGHT Request Denied:"],    \
                        ["ATTACK Request Denied:"],    \
                        ["SLAY Request Denied:"],    \
                        ["EAT Request Denied:"],    \
                        ["Shop available to 15+"],    \
                        ["Online players:"],    \
                        ["You are already"],    \
                        ["You are a Zombie!"],    \
                        ["Try: ALIGN"],    \
                        ["That would be dumb"],            \
                        ["Welcome to the shop"],            \
                        ["Do you have enough"],            \
                        ["You were not in Town"],         \
                        ["You first need to go to Town"],         \
                        ["You already have"],         \
                        ["You must explore the forest"],         \
                        ["You don't have enough gems"],         \
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
                        
                if char1 is True:
                        if(checknet == netname and checknick == supynick):
                                if itemslists != None:
                                        for entry in itemslists:
                                                if(entry[0] == 1 and entry[1] != None):
                                                        level = entry[2]
                                                        life = entry[3]
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
                                                self.usecommand(irc, "buy life", 1)
                                                life = 100
                if char2 is True:
                        if(checknet == netname2 and checknick == supynick2):
                                life2 = 0
                                level2 = 0
                                if itemslists != None:
                                        for entry in itemslists:
                                                if(entry[0] == 2 and entry[1] != None):
                                                        level2 = entry[2]
                                                        life2 = entry[3]
                                lifebuyb = False
                                if botname in chanmsgnick and "and been defeated in combat!" in text and "is added to {0}'s clock".format(name2) in text:
                                        lifebuyb = True
                                if botname in chanmsgnick and "has attacked a" in text and "is added to {0}'s clock".format(name2) in text:
                                        lifebuyb = True
                                if botname in chanmsgnick and "tried to slay a" in text and "is added to {0}'s clock".format(name2) in text:
                                        lifebuyb = True
                                if botname in chanmsgnick and "has challenged" in text and "is added to {0}'s clock".format(name2) in text:
                                        lifebuyb = True
                                if botname in chanmsgnick and "has challenged {0}".format(name2) in text and "and won!" in text:
                                        lifebuyb = True
                                if botname in chanmsgnick and "gold from {0}!".format(name2) in text and "XP and loses" in text:
                                        lifebuyb = True
                                if lifebuyb is True:
                                        if(level2 >= 15 and buylife is True and life2 >= 0):
                                                self.usecommand(irc, "buy life", 2)
                                                life2 = 100
                if char3 is True:
                        if(checknet == netname3 and checknick == supynick3):
                                life3 = 0
                                level3 = 0
                                if itemslists != None:
                                        for entry in itemslists:
                                                if(entry[0] == 3 and entry[1] != None):
                                                        level3 = entry[2]
                                                        life3 = entry[3]
                                lifebuyc = False
                                if botname in chanmsgnick and "and been defeated in combat!" in text and "is added to {0}'s clock".format(name3) in text:
                                        lifebuyc = True
                                if botname in chanmsgnick and "has attacked a" in text and "is added to {0}'s clock".format(name3) in text:
                                        lifebuyc = True
                                if botname in chanmsgnick and "tried to slay a" in text and "is added to {0}'s clock".format(name3) in text:
                                        lifebuyc = True
                                if botname in chanmsgnick and "has challenged" in text and "is added to {0}'s clock".format(name3) in text:
                                        lifebuyc = True
                                if botname in chanmsgnick and "has challenged {0}".format(name3) in text and "and won!" in text:
                                        lifebuyc = True
                                if botname in chanmsgnick and "gold from {0}!".format(name3) in text and "XP and loses" in text:
                                        lifebuyc = True
                                if lifebuyc is True:
                                        if(level3 >= 15 and buylife is True and life3 >= 0):
                                                self.usecommand(irc, "buy life", 3)
                                                life3 = 100
                if char4 is True:
                        if(checknet == netname4 and checknick == supynick4):
                                life4 = 0
                                level4 = 0
                                if itemslists != None:
                                        for entry in itemslists:
                                                if(entry[0] == 4 and entry[1] != None):
                                                        level4 = entry[2]
                                                        life4 = entry[3]
                                lifebuyd = False
                                if botname in chanmsgnick and "and been defeated in combat!" in text and "is added to {0}'s clock".format(name4) in text:
                                        lifebuyd = True
                                if botname in chanmsgnick and "has attacked a" in text and "is added to {0}'s clock".format(name4) in text:
                                        lifebuyd = True
                                if botname in chanmsgnick and "tried to slay a" in text and "is added to {0}'s clock".format(name4) in text:
                                        lifebuyd = True
                                if botname in chanmsgnick and "has challenged" in text and "is added to {0}'s clock".format(name4) in text:
                                        lifebuyd = True
                                if botname in chanmsgnick and "has challenged {0}".format(name4) in text and "and won!" in text:
                                        lifebuyd = True
                                if botname in chanmsgnick and "gold from {0}!".format(name4) in text and "XP and loses" in text:
                                        lifebuyd = True
                                if lifebuyd is True:
                                        if(level4 >= 15 and buylife is True and life4 >= 0):
                                                self.usecommand(irc, "buy life", 4)
                                                life4 = 100

                if char1 is True:
                        if(checknick == supynick and checknet == netname):
                                if(botname == chanmsgnick and "You are not logged in." in text):
                                    if pmtextmode is True:
                                            self.reply(irc, playbottext + " - {0}".format(text), 1)
                                    self.usecommand(irc, "login {0} {1}".format(name, pswd), 1 )
                                    interval = 60
                                    self.looper(irc)
                                    return               
                if char2 is True:
                        if(checknick == supynick2 and checknet == netname2):
                                if(botname == chanmsgnick and "You are not logged in." in text):
                                    if pmtextmode is True:
                                            self.reply(irc, playbottext + " - {0}".format(text), 2)
                                    self.usecommand(irc, "login {0} {1}".format(name2, pswd2), 2 )
                                    interval = 60
                                    self.looper(irc)
                                    return               
                if char3 is True:
                        if(checknick == supynick3 and checknet == netname3):
                                if(botname == chanmsgnick and "You are not logged in." in text):
                                    if pmtextmode is True:
                                            self.reply(irc, playbottext + " - {0}".format(text), 3)
                                    self.usecommand(irc, "login {0} {1}".format(name3, pswd3), 3 )
                                    interval = 60
                                    self.looper(irc)
                                    return               
                if char4 is True:
                        if(checknick == supynick4 and checknet == netname4):
                                if(botname == chanmsgnick and "You are not logged in." in text):
                                    if pmtextmode is True:
                                            self.reply(irc, playbottext + " - {0}".format(text), 4)
                                    self.usecommand(irc, "login {0} {1}".format(name4, pswd4), 4 )
                                    interval = 60
                                    self.looper(irc)
                                    return               
                if char1 is True:
                        if(checknick == supynick and checknet == netname):
                                for entry in messagelist:
                                    if(botname == chanmsgnick and entry[0] in text):
                                        if pmtextmode is True:
                                                self.reply(irc, playbottext + " - {0}".format(text), 1)
                                        return
                                for entry in messagelist2:
                                    if(botname == chanmsgnick and entry[0] in text):
#                                        self.reply(irc, playbottext + " - {0}".format(text), 1)
                                        return
                                if(botname == chanmsgnick and "You are {0}".format(name) in text):
                                    if pmtextmode is True:
                                            self.reply(irc, playbottext + " - {0}".format(text), 1)
                                    return
                if char2 is True:
                        if(checknick == supynick2 and checknet == netname2):
                                for entry in messagelist:
                                    if(botname == chanmsgnick and entry[0] in text):
                                        if pmtextmode is True:
                                                self.reply(irc, playbottext + " - {0}".format(text), 2)
                                        return
                                for entry in messagelist2:
                                    if(botname == chanmsgnick and entry[0] in text):
#                                        self.reply(irc, playbottext + " - {0}".format(text), 2)
                                        return
                                if(botname == chanmsgnick and "You are {0}".format(name2) in text):
                                    if pmtextmode is True:
                                            self.reply(irc, playbottext + " - {0}".format(text), 2)
                                    return
                if char3 is True:
                        if(checknick == supynick3 and checknet == netname3):
                                for entry in messagelist:
                                    if(botname == chanmsgnick and entry[0] in text):
                                        if pmtextmode is True:
                                                self.reply(irc, playbottext + " - {0}".format(text), 3)
                                        return
                                for entry in messagelist2:
                                    if(botname == chanmsgnick and entry[0] in text):
#                                        self.reply(irc, playbottext + " - {0}".format(text), 3)
                                        return
                                if(botname == chanmsgnick and "You are {0}".format(name3) in text):
                                    if pmtextmode is True:
                                            self.reply(irc, playbottext + " - {0}".format(text), 3)
                                    return
                if char4 is True:
                        if(checknick == supynick4 and checknet == netname4):
                                for entry in messagelist:
                                    if(botname == chanmsgnick and entry[0] in text):
                                        if pmtextmode is True:
                                                self.reply(irc, playbottext + " - {0}".format(text), 4)
                                        return
                                for entry in messagelist2:
                                    if(botname == chanmsgnick and entry[0] in text):
#                                        self.reply(irc, playbottext + " - {0}".format(text), 4)
                                        return
                                if(botname == chanmsgnick and "You are {0}".format(name4) in text):
                                    if pmtextmode is True:
                                            self.reply(irc, playbottext + " - {0}".format(text), 4)
                                    return
        return msg

    def doNick(self, irc, msg):
        global netname
        global nickname
        global netname2
        global nickname2
        global netname3
        global nickname3
        global netname4
        global nickname4
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
                                self.reply(irc, s, 1)
            if netname2 == network:
                    if nickname2 == msg.nick:
                        nickname2 = newNick
                        s = format(_('nick change by %s to %s'), msg.nick,newNick)
                        if bottextmode is True:
                                self.reply(irc, s, 2)
            if netname3 == network:
                    if nickname3 == msg.nick:
                        nickname3 = newNick
                        s = format(_('nick change by %s to %s'), msg.nick,newNick)
                        if bottextmode is True:
                                self.reply(irc, s, 3)
            if netname4 == network:
                    if nickname4 == msg.nick:
                        nickname4 = newNick
                        s = format(_('nick change by %s to %s'), msg.nick,newNick)
                        if bottextmode is True:
                                self.reply(irc, s, 4)

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
        global netname2
        global otherIrc2
        global supynick2
        global botcheck2
        global netname3
        global otherIrc3
        global supynick3
        global botcheck3
        global netname4
        global otherIrc4
        global supynick4
        global botcheck4
        global interval
        global webworks
        global rank
        global offline
        global rank2
        global offline2
        global rank3
        global offline3
        global rank4
        global offline4
        global playerspagelist
        global name
        global pswd
        global level
        global fights
        global name2
        global pswd2
        global name3
        global pswd3
        global name4
        global pswd4
        global char1
        global char2
        global char3
        global char4
        global life
        global intervaltext
        global playbottext
        global itemslists
        global bottextmode
        global errortextmode
        global botdisable1
        global botdisable2
        global botdisable3
        global botdisable4
        
        self.playbotcheck(irc)
        if intervaltext is True:
                self.replymulti(irc, playbottext + " - INTERVAL {0}".format(time.asctime()) )

        botcheck = False
        chancheck = False
        botcheck2 = False
        chancheck2 = False
        botcheck3 = False
        chancheck3 = False
        botcheck4 = False
        chancheck4 = False
        botdisable1 = False
        botdisable2 = False
        botdisable3 = False
        botdisable4 = False
        intervaldisable = False

        if char1 is True:
                self.bottester(irc, 1)
        if char2 is True:
                self.bottester(irc, 2)
        if char3 is True:
                self.bottester(irc, 3)
        if char4 is True:
                self.bottester(irc, 4)

        if char1 is True:
                netcheck = True
                try:
                        checkotherIrc = self._getIrc(netname)
                        if checkotherIrc.server == "unset":
                                if errortextmode is True:
                                        self.replymulti(irc, playbottext + " - Server 1 Error")
                except NameError:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Network 1 not connected to supybot")
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
                                    self.replymulti(irc, playbottext + " - Game Bot 1 not in channel")
                    except KeyError:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Game Bot 1 not in channel")
        if char2 is True:
                netcheck2 = True
                try:
                        checkotherIrc = self._getIrc(netname2)
                        if checkotherIrc.server == "unset":
                                if errortextmode is True:
                                        self.replymulti(irc, playbottext + " - Server 2 Error")
                except NameError:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Network 2 not connected to supybot")
                        netcheck2 = False

                chantest = otherIrc2.state.channels
                for entry in chantest:
                    if entry == channame:
                        chancheck2 = True
                if chancheck2 is False:
                    otherIrc2.queueMsg(ircmsgs.join(channame))
                    botcheck2 = False
                if chancheck2 is True:
                    try:
                        supynick2 = otherIrc2.nick
                        chanstate = otherIrc2.state.channels[channame]
                        users = [user for user in chanstate.users]
                        for entry in users:
                            if botname == entry:
                                botcheck2 = True
                        if botcheck2 is False:
                                if errortextmode is True:
                                    self.replymulti(irc, playbottext + " - Game Bot 2 not in channel")
                    except KeyError:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Game Bot 2 not in channel")
        if char3 is True:
                netcheck3 = True
                try:
                        checkotherIrc = self._getIrc(netname3)
                        if checkotherIrc.server == "unset":
                                if errortextmode is True:
                                        self.replymulti(irc, playbottext + " - Server 3 Error")
                except NameError:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Network 3 not connected to supybot")
                        netcheck3 = False

                chantest = otherIrc3.state.channels
                for entry in chantest:
                    if entry == channame:
                        chancheck3 = True
                if chancheck3 is False:
                    otherIrc3.queueMsg(ircmsgs.join(channame))
                    botcheck3 = False
                if chancheck3 is True:
                    try:
                        supynick3 = otherIrc3.nick
                        chanstate = otherIrc3.state.channels[channame]
                        users = [user for user in chanstate.users]
                        for entry in users:
                            if botname == entry:
                                botcheck3 = True
                        if botcheck3 is False:
                                if errortextmode is True:
                                    self.replymulti(irc, playbottext + " - Game Bot 3 not in channel")
                    except KeyError:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Game Bot 3 not in channel")
        if char4 is True:
                netcheck4 = True
                try:
                        checkotherIrc = self._getIrc(netname4)
                        if checkotherIrc.server == "unset":
                                if errortextmode is True:
                                        self.replymulti(irc, playbottext + " - Server 4 Error")
                except NameError:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Network 4 not connected to supybot")
                        netcheck4 = False

                chantest = otherIrc4.state.channels
                for entry in chantest:
                    if entry == channame:
                        chancheck4 = True
                if chancheck4 is False:
                    otherIrc4.queueMsg(ircmsgs.join(channame))
                    botcheck4 = False
                if chancheck4 is True:
                    try:
                        supynick4 = otherIrc4.nick
                        chanstate = otherIrc4.state.channels[channame]
                        users = [user for user in chanstate.users]
                        for entry in users:
                            if botname == entry:
                                botcheck4 = True
                        if botcheck4 is False:
                                if errortextmode is True:
                                    self.replymulti(irc, playbottext + " - Game Bot 4 not in channel")
                    except KeyError:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Game Bot 4 not in channel")

        if botcheck is True or botcheck2 is True or botcheck3 is True or botcheck4 is True:
                self.webdata(irc)
                if webworks is True:
                        self.itemsbuilder(irc)

        test = []
        offline = False
        offline2 = False
        offline3 = False
        offline4 = False
        rank = 0
        rank2 = 0
        rank3 = 0
        rank4 = 0
        if webworks is True:
                if char1 is True and botcheck is True:
                        for entry in playerspagelist:
                                if "playerview.php" in entry and name in entry:
                                        test = entry
                        if "offline" in test:
                                offline = True
                        if offline is False:
                                try:
                                        test = test.split('">')
                                        ranktext = test[1]
                                        ranktext = ranktext.split("</")
                                        rank = int(ranktext[0])
                                except:
                                        offline = True
                if char2 is True and botcheck2 is True:
                        for entry in playerspagelist:
                                if "playerview.php" in entry and name2 in entry:
                                        test = entry
                        if "offline" in test:
                                offline2 = True
                        if offline2 is False:
                                try:
                                        test = test.split('">')
                                        ranktext = test[1]
                                        ranktext = ranktext.split("</")
                                        rank2 = int(ranktext[0])
                                except:
                                        offline2 = True
                if char3 is True and botcheck3 is True:
                        for entry in playerspagelist:
                                if "playerview.php" in entry and name3 in entry:
                                        test = entry
                        if "offline" in test:
                                offline3 = True
                        if offline3 is False:
                                try:
                                        test = test.split('">')
                                        ranktext = test[1]
                                        ranktext = ranktext.split("</")
                                        rank3 = int(ranktext[0])
                                except:
                                        offline3 = True
                if char4 is True and botcheck4 is True:
                        for entry in playerspagelist:
                                if "playerview.php" in entry and name4 in entry:
                                        test = entry
                        if "offline" in test:
                                offline4 = True
                        if offline4 is False:
                                try:
                                        test = test.split('">')
                                        ranktext = test[1]
                                        ranktext = ranktext.split("</")
                                        rank4 = int(ranktext[0])
                                except:
                                        offline4 = True
        if char1 is True:
                if(webworks is True and offline is True):
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - 1 Player Offline")
        if char2 is True:
                if(webworks is True and offline2 is True):
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - 2 Player Offline")
        if char3 is True:
                if(webworks is True and offline3 is True):
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - 3 Player Offline")
        if char4 is True:
                if(webworks is True and offline4 is True):
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - 4 Player Offline")

        if char1 is True:
                if webworks is True and offline is True and botcheck is True:
                        if netcheck is True:
                                self.usecommand(irc, "login {0} {1}".format(name, pswd), 1 )
                                interval = 45
                                self.looper(irc)
                                intervaldisable = True
        if char2 is True:
                if webworks is True and offline2 is True and botcheck2 is True:
                        if netcheck2 is True:
                                self.usecommand(irc, "login {0} {1}".format(name2, pswd2), 2 )
                                interval = 45
                                self.looper(irc)
                                intervaldisable = True
        if char3 is True:
                if webworks is True and offline3 is True and botcheck3 is True:
                        if netcheck3 is True:
                                self.usecommand(irc, "login {0} {1}".format(name3, pswd3), 3 )
                                interval = 45
                                self.looper(irc)
                                intervaldisable = True
        if char4 is True:
                if webworks is True and offline4 is True and botcheck4 is True:
                        if netcheck4 is True:
                                self.usecommand(irc, "login {0} {1}".format(name4, pswd4), 4 )
                                interval = 45
                                self.looper(irc)
                                intervaldisable = True

        if webworks is True and intervaldisable is False:
            self.intervalcalc(irc)
        if webworks is False and intervaldisable is False:
            interval = 300
            self.looper(irc)
               
        life2 = 0
        level2 = 0
        fights2 = 0
        life3 = 0
        level3 = 0
        fights3 = 0
        life4 = 0
        level4 = 0
        fights4 = 0
        
        if char1 is True:
                if itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == 1 and entry[1] != None):
                                        level = entry[2]
                                        fights = entry[31]
                                        life = entry[3]
        if char2 is True:
                if itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == 2 and entry[1] != None):
                                        level2 = entry[2]
                                        fights2 = entry[31]
                                        life2 = entry[3]
        if char3 is True:
                if itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == 3 and entry[1] != None):
                                        level3 = entry[2]
                                        fights3 = entry[31]
                                        life3 = entry[3]
        if char4 is True:
                if itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == 4 and entry[1] != None):
                                        level4 = entry[2]
                                        fights4 = entry[31]
                                        life4 = entry[3]

        if webworks is True:
                if char1 is True and offline is False and botcheck is True:
                        self.playerarea(irc, 1)
                        self.spendmoney(irc, 1)
                        self.timercheck(irc, 1)
                        if(level >= 25 and fights >= 0 and fights < 5 and life > 0):
                                if bottextmode is True:
                                        self.reply(irc, playbottext + " - 1 Fights available",1)
                        if(level >= 25 and fights >= 0 and fights < 5 and life > 10):
                                self.newlister(irc, 1)
                                self.fight_fight(irc, 1)
                if char2 is True and offline2 is False and botcheck2 is True:
                        self.playerarea(irc, 2)
                        self.spendmoney(irc, 2)
                        self.timercheck(irc, 2)
                        if(level2 >= 25 and fights2 >= 0 and fights2 < 5 and life2 > 0):
                                if bottextmode is True:
                                        self.reply(irc, playbottext + " - 2 Fights available",2)
                        if(level2 >= 25 and fights2 >= 0 and fights2 < 5 and life2 > 10):
                                self.newlister(irc, 2)
                                self.fight_fight(irc, 2)
                if char3 is True and offline3 is False and botcheck3 is True:
                        self.playerarea(irc, 3)
                        self.spendmoney(irc, 3)
                        self.timercheck(irc, 3)
                        if(level3 >= 25 and fights3 >= 0 and fights3 < 5 and life3 > 0):
                                if bottextmode is True:
                                        self.reply(irc, playbottext + " - 3 Fights available",3)
                        if(level3 >= 25 and fights3 >= 0 and fights3 < 5 and life3 > 10):
                                self.newlister(irc, 3)
                                self.fight_fight(irc, 3)
                if char4 is True and offline4 is False and botcheck4 is True:
                        self.playerarea(irc, 4)
                        self.spendmoney(irc, 4)
                        self.timercheck(irc, 4)
                        if(level4 >= 25 and fights4 >= 0 and fights4 < 5 and life4 > 0):
                                if bottextmode is True:
                                        self.reply(irc, playbottext + " - 4 Fights available",4)
                        if(level4 >= 25 and fights4 >= 0 and fights4 < 5 and life4 > 10):
                                self.newlister(irc, 4)
                                self.fight_fight(irc, 4)

        return 1
    
    def intervalcalc(self, irc):
        global interval
        global level
        global fights
        global botcheck
        global offline
        global life
        global botcheck2
        global offline2
        global botcheck3
        global offline3
        global botcheck4
        global offline4
        global char1
        global char2
        global char3
        global char4
        global fightmode
        global itemslists
        
        sixty = 60
        onetwenty = 120
        interval = 5
        interval *= 60                  # conv from min to sec
        intervallist = []
                        
        level2 = 0
        fights2 = 0
        life2 = 0
        level3 = 0
        fights3 = 0
        life3 = 0
        level4 = 0
        fights4 = 0
        life4 = 0
        
        if char1 is True:
                if itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == 1 and entry[1] != None):
                                        level = entry[2]
                                        fights = entry[31]
                                        life = entry[3]
        if char2 is True:
                if itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == 2 and entry[1] != None):
                                        level2 = entry[2]
                                        fights2 = entry[31]
                                        life2 = entry[3]
        if char3 is True:
                if itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == 3 and entry[1] != None):
                                        level3 = entry[2]
                                        fights3 = entry[31]
                                        life3 = entry[3]
        if char4 is True:
                if itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == 4 and entry[1] != None):
                                        level4 = entry[2]
                                        fights4 = entry[31]
                                        life4 = entry[3]

        if char1 is True:                                       
                if botcheck is False or offline is True:
                        intervallist.append( ( "interval", sixty ) )
                if botcheck is True and fightmode is True:
                        if(level >= 25 and life > 10 and fightmode is True):
                                if(fights >= 0 and fights < 5):
                                        intervallist.append( ( "interval", onetwenty ) )
        if char2 is True:
                if botcheck2 is False or offline2 is True:
                        intervallist.append( ( "interval", sixty ) )
                if botcheck2 is True and fightmode is True:
                        if(level2 >= 25 and life2 > 10 and fightmode is True):
                                if(fights2 >= 0 and fights2 < 5):
                                        intervallist.append( ( "interval", onetwenty ) )
        if char3 is True:
                if botcheck3 is False or offline3 is True:
                        intervallist.append( ( "interval", sixty ) )
                if botcheck3 is True and fightmode is True:
                        if(level3 >= 25 and life3 > 10 and fightmode is True):
                                if(fights3 >= 0 and fights3 < 5):
                                        intervallist.append( ( "interval", onetwenty ) )
        if char4 is True:
                if botcheck4 is False or offline4 is True:
                        intervallist.append( ( "interval", sixty ) )
                if botcheck4 is True and fightmode is True:
                        if(level4 >= 25 and life4 > 10 and fightmode is True):
                                if(fights4 >= 0 and fights4 < 5):
                                        intervallist.append( ( "interval", onetwenty ) )

        intervallist.sort( key=operator.itemgetter(1), reverse=True )
        diff = 999999        
        for entry in intervallist:
                if(entry[1] < diff):
                        interval = entry[1]

        self.looper(irc)

    def looper(self, irc):
        global interval
        global gameactive
        global intervaltext
        global playbottext
        
        def loopqm():
            self.main(irc)
        nextTime = time.time() + interval
        
        if intervaltext is True:
                self.replymulti(irc, playbottext + " - Checking timers every {0} minutes".format(interval // 60))
        if gameactive is True:
            try:
                schedule.addEvent(loopqm, nextTime, "loopqm")
            except AssertionError:
                schedule.removeEvent('loopqm')
                schedule.addEvent(loopqm, nextTime, "loopqm")        

Class = QuakenetPlayBotMulti


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
