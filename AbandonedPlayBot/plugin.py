###
# Copyright (c) 2021-2026, Russell Beech
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
    _ = PluginInternationalization('AbandonedPlayBot')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

__module_name__ = "Abandoned-IRC #ZW-IdleRPG Playbot Script"
__module_version__ = "2.1"
__module_description__ = "Abandoned-IRC #ZW-IdleRPG Playbot Script"

# build hardcoded monster/creep lists, reverse
creeps = [      ["Roach",       1500],   \
                ["Spider",      2000],  \
                ["Bat",         3000],  \
                ["Wolf",        4000],  \
                ["Goblin",      5000],  \
                ["Shadow",      6000],  \
                ["Lich",        7000],  \
                ["Skeleton",    8000],  \
                ["Ghost",       9000],  \
                ["Phantom",     10000],  \
                ["Troll",       12000], \
                ["Cyclop",      14000],  \
                ["Mutant",      17000], \
                ["Ogre",        21000],  \
                ["Phoenix",     25000],  \
                ["Wraith",      30000],  \
                ["Vampire",     35000],  \
                ["Bigfoot",     40000],  \
                ["Chimera",     45000],  \
                ["Witch",       50000], \
                ["Imp",         55000], \
                ["Hag",         60000], \
                ["Kraken",      65000], \
                ["Wyvern",      70000], \
                ["Grendel",     75000], \
                ["Banshee",     80000], \
                ["Leprechaun",  85000], \
                ["Mummy",       90000], \
                ["Sphinx",      95000], \
                ["Krampus",     100000], \
                ["Griffin",     105000], \
                ["Harpy",       110000], \
                ["Hydra",       115000], \
                ["Demon",       125000], \
                ["Centaur",     150000], \
                ["Werewolf",    250000], \
                ["Giant",       2000000], \
                ["Satan",       9999999]  ]

monsters = [    ["Blue_Dragon",         7500],  \
                ["Yellow_Dragon",       15000],  \
                ["Green_Dragon",        25000], \
                ["Red_Dragon",          35000], \
                ["Black_Dragon",        40000], \
                ["White_Dragon",        60000], \
                ["Bronze_Dragon",       80000], \
                ["Silver_Dragon",       100000], \
                ["Gold_Dragon",         350000], \
                ["Platinum_Dragon",     6000000], \
                ["Diamond_Dragon",      9999999]  ]

creeps.reverse()
monsters.reverse()

website = "https://irpg.abandoned-irc.net"
website2 = "playerview.php"
website3 = "/players.php"
russweb = "http://russellb.x10.mx/"
gitweb = "https://github.com/RussellBeech/supybot-plugins"
gitweb2 = "https://raw.githubusercontent.com/RussellBeech/supybot-plugins/master/"
rawplayers3 = None
interval = 300
newlist = None
playerlist = None 
playerspage = None
playerspagelist = None
myentry = None
currentversion = __module_version__
currentversion = float( currentversion )

# Changeable settings
setbuy = 15 # level to start buying items from
goldsave = 3100 # gold kept in hand
buylife = True
blackbuyspend = True
blackbuyspend14 = True
getgems = True
fightmode = True
channame = "#zw-idlerpg"
botname = "IdleRPG"
creepattack = True # True = On, False = Off - Autocreep selection
setcreeptarget = "Werewolf" # Sets creep target. creepattack needs to be False to use
scrollssum = 3000 # Itemscore you start buying scrolls at
xpupgrade = True # Upgrade Items with XP
xpspend = 20 # Amount you use with xpget to upgrade items
bottextmode = True # True = on, False = off
errortextmode = True # True = on, False = off
pmtextmode = True # True = on, False = off
intervaltext = True # True = on, False = off - Text displayed every interval
townworkswitch = True # True = Town/Work Area Switching, False = Town/Forest Area Switching, None = Area Switching Off
areasum = 6000 # Sum at which you switch to Fast Town Switching
buyluck = False
buypower = False
expbuy = False
autoconfig = 1 # 0 = off, 1 = on, 2 = remove config changes.
slaysum = 1000 # minimum sum you start slaying without mana from
loginsettingslist = True # True = on, False = off - Settings List at start

# declare stats as global
name = None
pswd = None
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
luck = 0
powerpots = 0
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
eatused = 0

nickname = None
netname = None
online = None
botcheck = None
webworks = None
webworks2 = None 
gameactive = None
lottonum1 = None
lottonum2 = None
lottonum3 = None
location = None
locationtime = 0

otherIrc = None
supynick = None
botdisable1 = False
autostartmode = False
playbotcount = 0
playbottext = None
playbotid = "AS"
pbcount = 0

abandoned = False
abandonedmulti = False

fileprefix = "AbandonedPlayBotconfig.txt"
path = conf.supybot.directories.data
filename = path.dirize(fileprefix)
try:
        f = open(filename,"rb")
        configList = pickle.load(f)
        f.close()
except:
        configList = []
fileprefix2 = "autostartsingleconfigas.txt"
path = conf.supybot.directories.data
filename2 = path.dirize(fileprefix2)
try:
        f = open(filename2,"rb")
        autoconfigList = pickle.load(f)
        f.close()
except:
        autoconfigList = []
fileprefix3 = "abandonedsingleplayers.txt"
path = conf.supybot.directories.data
filename3 = path.dirize(fileprefix3)
fileprefix4 = "abandonedmultiplayers.txt"
path = conf.supybot.directories.data
filename4 = path.dirize(fileprefix4)

for entry in configList:
        if(entry[0] == "autostartmode"):
                autostartmode = entry[1]
        if(entry[0] == "blackbuyspend"):
                blackbuyspend = entry[1]
        if(entry[0] == "blackbuyspend14"):
                blackbuyspend14 = entry[1]
        if(entry[0] == "bottextmode"):
                bottextmode = entry[1]
        if(entry[0] == "buylife"):
                buylife = entry[1]
        if(entry[0] == "buyluck"):
                buyluck = entry[1]
        if(entry[0] == "buypower"):
                buypower = entry[1]
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

class AbandonedPlayBot(callbacks.Plugin):
    """Abandoned PlayBot Idlerpg"""
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

        webversion = None
        gitversion = None
        newversion = 0
        versionfilename = "playbotversionabandonedsupy.txt"

        try:
                if python3 is False:
                        text = urllib2.urlopen(russweb + versionfilename)
                if python3 is True:
                        text = urllib.request.urlopen(russweb + versionfilename)
                webversion = text.read()
                webversion = float( webversion )
                text.close()

        except:
                self.reply(irc, "Could not access {0}".format(russweb))

        try:
                context = ssl._create_unverified_context()
                if python3 is False:
                        text2 = urllib2.urlopen(gitweb2 + versionfilename, context=context)
                if python3 is True:
                        text2 = urllib.request.urlopen(gitweb2 + versionfilename, context=context)
                gitversion = text2.read()
                text2.close()
                if python3 is True:
                        gitversion = gitversion.decode("UTF-8")
                gitversion = float( gitversion )

        except:
                self.reply(irc, "Could not access {0}".format(gitweb2))

        self.reply(irc, "Current version {0}".format(currentversion))
        self.reply(irc, "Web version {0}".format(webversion))
        self.reply(irc, "GitHub version {0}".format(gitversion))
        if webversion is None and gitversion is None:
                self.reply(irc, "Both Websites have failed to read.  Try again later")
                return
        if gitversion is None and webversion != None:
                newversion = webversion
        if webversion is None and gitversion != None:
                newversion = gitversion
        if webversion != None and gitversion != None:
                if webversion > gitversion:
                        newversion = webversion
                if webversion < gitversion:
                        newversion = gitversion
                if webversion == gitversion:
                        newversion = gitversion

        if newversion != None:
                if(currentversion == newversion):
                        self.reply(irc, "You have the current version of PlayBot")
                if(currentversion < newversion):
                        self.reply(irc, "You have an old version of PlayBot")
                        self.reply(irc, "You can download a new version from {0} or {1}".format(russweb, gitweb))
                if(currentversion > newversion):
                        self.reply(irc, "Give me, Give me")

    def configwrite(self):
        global autostartmode
        global blackbuyspend
        global blackbuyspend14
        global buylife
        global buyluck
        global buypower
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
        configList.append( ( "autostartmode", autostartmode ) )
        configList.append( ( "blackbuyspend", blackbuyspend ) )
        configList.append( ( "blackbuyspend14", blackbuyspend14 ) )
        configList.append( ( "bottextmode", bottextmode ) )
        configList.append( ( "buylife", buylife ) )
        configList.append( ( "buyluck", buyluck ) )
        configList.append( ( "buypower", buypower ) )
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

    def configwrite2(self):
        global name
        global pswd
        global nickname
        global netname

        autoconfigList = []
        autoconfigList.append( ( "name", name ) )
        autoconfigList.append( ( "pswd", pswd ) )
        autoconfigList.append( ( "nickname", nickname ) )
        autoconfigList.append( ( "netname", netname ) )
        f = open(filename2,"wb")
        pickle.dump(autoconfigList,f)
        f.close()

    def eraseconfig(self, irc, msg, args):
        """takes no arguments

        Erases config file
        """
        configList = []
        f = open(filename,"wb")
        pickle.dump(configList,f)
        f.close()
        autoconfigList = []
        f = open(filename2,"wb")
        pickle.dump(autoconfigList,f)
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
        global buyluck
        global buypower
        global gameactive
        global slaysum
        global bottextmode
        global errortextmode
        global pmtextmode
        global autostartmode
        
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
        ##              Turns Area Switching Off
                        if value == "off" or value == "Off":
                                townworkswitch = None
                                irc.reply("Town/Work Switch Mode Deactivated.  To change to Town/Work use 'setoption townwork true' command", private=True)
                if text == "townforest":
        ##              Change player area switching to town/forest
                        if value is True:
                                townworkswitch = False
                                irc.reply("Town/Forest Switch Mode Activated.  To change to Town/Work use 'setoption townforest false' command", private=True)
        ##              Change player area switching to town/work
                        if value is False:
                                townworkswitch = True
                                irc.reply("Town/Work Switch Mode Activated.  To change to Town/Forest use 'setoption townforest true' command", private=True)
        ##              Turns Area Switching Off
                        if value == "off" or value == "Off":
                                townworkswitch = None
                                irc.reply("Town/Forest Switch Mode Deactivated.  To change to Town/Forest use 'setoption townforest true' command", private=True)
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
                if text == "buyluck":
        ##              Turns on Buying Luck Potions
                        if value is True:
                                buyluck = True
                                irc.reply("Buying Luck Potions Mode Activated.  To turn it back off use 'setoption buyluck false' command", private=True)
        ##              Turns off Buying Luck Potions
                        if value is False:
                                buyluck = False
                                irc.reply("Buying Luck Potions Mode Deactivated.  To turn it back on use 'setoption buyluck true' command", private=True)
                if text == "buypower":
        ##              Turns on Buying Power Potions
                        if value is True:
                                buypower = True
                                irc.reply("Buying Power Potions Mode Activated.  To turn it back off use 'setoption buypower false' command", private=True)
        ##              Turns off Buying Power Potions
                        if value is False:
                                buypower = False
                                irc.reply("Buying Power Potions Mode Deactivated.  To turn it back on use 'setoption buypower true' command", private=True)
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
                if text == "autostart":
        ##              Turns Autostart Mode on
                        if value is True:
                                autostartmode = True
                                self.configwrite2()
                                irc.reply("Autostart Mode on.  To turn it back off use 'setoption autostart false' command", private=True)
        ##              Turns Autostart Mode off
                        if value is False:
                                autostartmode = False
                                autoconfigList = []
                                f = open(filename2,"wb")
                                pickle.dump(autoconfigList,f)
                                f.close()
                                irc.reply("Autostart Mode off  To turn it back on use 'setoption autostart true' command", private=True)

                self.configwrite()
        if gameactive is False:
            irc.error("You are not logged in")

    setoption = wrap(setoption, [('checkCapability', 'admin'), 'something', 'something'])

    def bottester(self, irc):
        global otherIrc
        global botname
        global channame
        global botdisable1
        
        botcount1 = 0

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
        global abandoned
        global abandonedmulti

        playbotcount = 0
        pbcount = 0
        quakeon = True
        quakemultion = True
        abandonedon = True
        abandonedmultion = True
        playbotsingleon = True
        playbotmultion = True
        quake = False
        quakemulti = False
        abandoned = False
        abandonedmulti = False
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
                abandonedcheck = conf.supybot.plugins.get("AbandonedPlayBot")
        except:
                abandonedon = False
        try:
                abandonedmulticheck = conf.supybot.plugins.get("AbandonedPlayBotMulti")
        except:
                abandonedmultion = False
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

        if quakemultion is True:
                quakemulti = conf.supybot.plugins.QuakenetPlayBotMulti()
                if quakemulti is True:
                        playbotcount += 1

        if abandonedon is True:
                abandoned = conf.supybot.plugins.AbandonedPlayBot()
                if abandoned is True:
                        playbotcount += 1
                        pbcount += 1

        if abandonedmultion is True:
                abandonedmulti = conf.supybot.plugins.AbandonedPlayBotMulti()
                if abandonedmulti is True:
                        playbotcount += 1
                        pbcount += 1

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

    def autostart(self, irc):
        global name
        global pswd
        global netname
        global charcount
        global nickname
        global gameactive
        global otherIrc
        global supynick
        global Owner
        global autostartmode

        for entry in autoconfigList:
                if(entry[0] == "name"):
                        name = entry[1]
                if(entry[0] == "pswd"):
                        pswd = entry[1]
                if(entry[0] == "nickname"):
                        nickname = entry[1]
                if(entry[0] == "netname"):
                        netname = entry[1]

        if name != None and pswd != None:
                charcount += 1

        bootdelay = False

        if charcount == 1:
                try:
                        checkotherIrc = self._getIrc(netname)
                        if checkotherIrc.server == "unset":
                                bootdelay = True
                                charcount = 0
                except NameError:
                        bootdelay = True
                        charcount = 0

                if bootdelay is True:
                        def bootloopas():
                            self.autostart(irc)
                        delayTime = time.time() + 60
                        
                        try:
                                schedule.addEvent(bootloopas, delayTime, "bootloopas")
                        except AssertionError:
                                schedule.removeEvent('bootloopas')
                                schedule.addEvent(bootloopas, delayTime, "bootloopas")
                        return

        irc = world.getIrc(netname)
        if charcount == 0:
                gameactive = False
                irc.error("Autostart Failed")
                autostartmode = False
                self.configwrite()

        if charcount == 1:
                gameactive = True
                supynick = irc.nick
                Owner = irc.getCallback('Owner')
                otherIrc = self._getIrc(netname)

                if(name != None and pswd != None):
                        self.loginstart(irc)
                        self.singlewrite(irc)

    def login(self, irc, msg, args, arg2):
        """<charname> <password>

        Log into Game.
        """
        global name
        global pswd
        global netname
        global nickname
        global gameactive
        global charcount
        global otherIrc
        global supynick
        global playerspagelist
        global webworks
        global webworks2
        global pbcount

        charcount += 1

        if charcount == 1:
                gameactive = True
                netname = self._getIrcName(irc)
                nickname = msg.nick
                supynick = irc.nick
                otherIrc = self._getIrc(netname)
                namecheck = False

                if "undernet" in netname.lower():
                        irc.error("The #irpg game on Undernet is not supported.  Expect your head to explode if you continue")
                        charcount = 0
                if "quakenet" in netname.lower():
                        irc.error("You need to use the QuakeNet version of PlayBot")
                        charcount = 0

                if charcount == 1:
                        self.playbotcheck(irc)
                        args2 = arg2.split(" ")

                        try:
                                if(name is None or pswd is None):
                                        name = args2[0]
                                        pswd = args2[1]
                        except IndexError:
                                irc.error("To log in use <bot> abandonedplaybot login CharName Password" )
                                
                        self.webdata(irc)
                        self.webdata2(irc)
                        if(name is None or pswd is None):
                                charcount = 0
                                irc.error("Login Failed")
                if charcount == 1:
                        try:
                                for entry in playerspagelist:
                                        if ">{0}<".format(name) in entry:
                                                namecheck = True
                        except TypeError:
                                webworks2 = False
                        if(namecheck is False and webworks2 is True):
                                irc.error("LOGIN ERROR: {0} does not exist".format(name))
                                charcount = 0

                if charcount == 1:
                        if pbcount >= 2:
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
                                        irc.error("Character {0} is already logged in on AbandonedPlayBotMulti".format(name))
                                        charcount = 0
                                if(netname == multinetname):
                                        irc.error("Character {0} is already logged in on AbandonedPlayBotMulti".format(multiname))
                                        charcount = 0
                                if(netname == multinetname2):
                                        irc.error("Character {0} is already logged in on AbandonedPlayBotMulti".format(multiname2))
                                        charcount = 0
                                if(netname == multinetname3):
                                        irc.error("Character {0} is already logged in on AbandonedPlayBotMulti".format(multiname3))
                                        charcount = 0
                                if(netname == multinetname4):
                                        irc.error("Character {0} is already logged in on AbandonedPlayBotMulti".format(multiname4))
                                        charcount = 0

                if charcount == 0:
                        gameactive = False
                        name = None
                        pswd = None

                if charcount == 1:
                        if(name != None and pswd != None):
                                self.loginstart(irc)

        if charcount >= 2:
            irc.error("You can only play with 1 character.  You are already logged in as {0}".format(name))
            charcount = 1

    login = wrap(login, [("checkCapability", "admin"), "text"])

    def loginstart(self, irc):
        global name
        global pswd

        global setbuy
        global buylife
        global fightmode
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
        global buyluck
        global buypower
        global expbuy
        global slaysum
        global loginsettingslist
        global bottextmode
        global errortextmode
        global pmtextmode

        self.usecommand(irc, "login {0} {1}".format(name, pswd) )
        time.sleep(3) # Needed
        self.usecommand(irc, "whoami")
        self.reply(irc, "Player Character {0} has logged in".format(name))

        if loginsettingslist is True:
                if blackbuyspend is True:
                        self.reply(irc, "BlackBuy Spend Mode Activated.  To turn it off use 'setoption blackbuy false' command")
                if blackbuyspend is False:
                        self.reply(irc, "BlackBuy Spend Mode Deactivated.  To turn it off use 'setoption blackbuy true' command")
                if blackbuyspend14 is True:
                        self.reply(irc, "BlackBuy Spend 14 Mode Activated.  To turn it off use 'setoption blackbuy14 false' command")
                if blackbuyspend14 is False:
                        self.reply(irc, "BlackBuy Spend 14 Mode Deactivated.  To turn it off use 'setoption blackbuy14 true' command")
                if bottextmode is True:
                        self.reply(irc, "Bot Text Mode Activated.  To turn it off use 'setoption bottext false' command")
                if buylife is True:
                        self.reply(irc, "Buy Life Mode Activated.  To turn it off use 'setoption buylife false' command")
                if buylife is False:
                        self.reply(irc, "Buy Life Mode Deactivated.  To turn it on use 'setoption buylife true' command")
                if buyluck is True:
                        self.reply(irc, "Buy Luck Potions Mode Activated.  To turn it off use 'setoption buyluck false' command")
                if buyluck is False:
                        self.reply(irc, "Buy Luck Potions Mode Deactivated.  To turn it on use 'setoption buyluck true' command")
                if buypower is True:
                        self.reply(irc, "Buy Power Potions Mode Activated.  To turn it off use 'setoption buypower false' command")
                if buypower is False:
                        self.reply(irc, "Buy Power Potions Mode Deactivated.  To turn it on use 'setoption buypower true' command")
                if creepattack is True:
                        self.reply(irc, "CreepAttack Mode Activated.  To turn it off use 'setoption creepattack false' command")
                if creepattack is False:
                        self.reply(irc, "CreepAttack Mode Deactivated.  To turn it on use 'setoption creepattack true' command")
                if errortextmode is True:
                        self.reply(irc, "Error Text Mode Activated.  To turn it off use 'setoption errortext false' command")
                if expbuy is True:
                        self.reply(irc, "Experience Buying Mode Activated.  To turn it off use 'setoption expbuy false' command")
                if expbuy is False:
                        self.reply(irc, "Experience Buying Mode Deactivated.  To turn it on use 'setoption expbuy true' command")
                if fightmode is True:
                        self.reply(irc, "Fighting Mode Activated.  To turn it off use 'setoption fights false' command")
                if fightmode is False:
                        self.reply(irc, "Fighting Mode Deactivated.  To turn it on use 'setoption fights true' command")
                if getgems is True:
                        self.reply(irc, "GetGems Mode Activated.  To turn it off use 'setoption getgems false' command")
                if getgems is False:
                        self.reply(irc, "GetGems Mode Deactivated.  To turn it on use 'setoption getgems true' command")
                if intervaltext is True:
                        self.reply(irc, "Interval Text Mode Activated.  To turn it off use 'setoption intervaltext false' command")
                if pmtextmode is True:
                        self.reply(irc, "PMs from GameBot Mode Activated.  To turn it off use 'setoption pmtext false' command")
                if townworkswitch is True:
                        self.reply(irc, "Town/Work Switch Mode Activated.  To change to Town/Forest use 'setoption townforest true' command")
                if townworkswitch is False:
                        self.reply(irc, "Town/Forest Switch Mode Activated.  To change to Town/Work use 'setoption townwork true' command")
                if xpupgrade is True:
                        self.reply(irc, "XPUpgrade Mode Activated.  To turn it off use 'setoption xpupgrade false' command")
                if xpupgrade is False:
                        self.reply(irc, "XPUpgrade Mode Deactivated.  To turn it on use 'setoption xpupgrade true' command")
                self.reply(irc, "Current Goldsave: {0}.  If you want to change it use 'setoption goldsave number' command".format(goldsave))
                self.reply(irc, "Current Item Buy Level: {0}.  If you want to change it use 'setoption itembuy number' command".format(setbuy))
                self.reply(irc, "Current Scrolls Buy ItemScore: {0}.  If you want to change it use 'setoption scrollssum number' command".format(scrollssum))
                self.reply(irc, "Current SlaySum Minimum ItemScore: {0}.  If you want to change it use 'setoption slaysum number' command".format(slaysum))
                self.reply(irc, "Current XPSpend for xpget item upgrades: {0}.  If you want to change it use 'setoption xpspend number' command".format(xpspend))
                self.reply(irc, " ")
                self.reply(irc, "For a list of PlayBot commands use <bot> abandonedplaybot help")
                self.reply(irc, " ")
        self.versionchecker(irc)
        self.configcheck(irc)
        self.singlewrite(irc)

        self.main(irc)

    def logoutchar(self, irc, msg, args):
        """takes no arguments

        Logs you out of the PlayBot.
        """
        global charcount
        global netname
        global name
        global pswd
        global gameactive
        global autostartmode
        
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
                if autostartmode is True:
                    autostartmode = False
                    self.configwrite()
                    self.configwrite2()
                try:
                    schedule.removeEvent('loopas')
                except KeyError:
                    irc.error("You are not logged in")

    logoutchar = wrap(logoutchar, [("checkCapability", "admin")])

    def logoutgame(self, irc, msg, args):
        """takes no arguments

        Logs you out of IdleRPG.
        """
        global gameactive
        
        if gameactive is True:
                self.usecommand(irc, "logout")
        if gameactive is False:
            irc.error("You are not logged in")

    logoutgame = wrap(logoutgame, [("checkCapability", "admin")])

    def aplayerslist(self, irc, msg, args):
        """takes no arguments

        Lists players on all Abandoned plugins loaded
        """

        global abandoned
        global abandonedmulti

        self.playbotcheck(irc)
       
        if abandoned is True:
                afileprefix3 = "abandonedsingleplayers.txt"
                path = conf.supybot.directories.data
                afilename3 = path.dirize(afileprefix3)
                acheck = True
                try:
                        f = open(afilename3,"rb")
                        playerListS = pickle.load(f)
                        f.close()
                except:
                        playerListS = []
                try:
                        asinglename = playerListS[0][1]
                        asinglenetname = playerListS[0][3]
                except IndexError:
                        irc.reply("No Players Logged in on AbandonedPlayBot", private=True)
                        irc.reply(" ", private=True)
                        irc.reply(" ", private=True)
                        acheck = False
                if acheck is True:
                        irc.reply("Abandoned PlayBot Single", private=True)
                        irc.reply(" ", private=True)
                        irc.reply("Player Character - {0}.  Network {1}".format(asinglename, asinglenetname), private=True)
                        irc.reply(" ", private=True)
                        irc.reply(" ", private=True)

        if abandonedmulti is True:
                afileprefix4 = "abandonedmultiplayers.txt"
                path = conf.supybot.directories.data
                afilename4 = path.dirize(afileprefix4)
                amcheck = False
                try:
                        f = open(afilename4,"rb")
                        playerListM = pickle.load(f)
                        f.close()
                except:
                        playerListM = []
                count = 0
                amultiname = None
                amultiname2 = None
                amultiname3 = None
                amultiname4 = None
                amultinetname = None
                amultinetname2 = None
                amultinetname3 = None
                amultinetname4 = None
                for entry in playerListM:
                        count += 1
                        if count == 1:
                                amultiname = entry[1]
                                amultinetname = entry[3]
                                amcheck = True
                        if count == 2:
                                amultiname2 = entry[1]
                                amultinetname2 = entry[3]
                        if count == 3:
                                amultiname3 = entry[1]
                                amultinetname3 = entry[3]
                        if count == 4:
                                amultiname4 = entry[1]
                                amultinetname4 = entry[3]
                if amcheck is False:
                        irc.reply("No Players Logged in on AbandonedPlayBotMulti", private=True)
                if amcheck is True:
                        irc.reply("Abandoned PlayBot Multi", private=True)
                        irc.reply(" ", private=True)
                        irc.reply("Player Character 1 - {0}.  Network {1}    Player Character 2 - {2}.  Network {3}".format(amultiname, amultinetname, amultiname2, amultinetname2), private=True)
                        irc.reply("Player Character 3 - {0}.  Network {1}    Player Character 4 - {2}.  Network {3}".format(amultiname3, amultinetname3, amultiname4, amultinetname4), private=True)

    aplayerslist = wrap(aplayerslist, [("checkCapability", "admin")])

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
        irc.reply("Abandoned PlayerListS Erased", private=True)

    def asingleerase(self, irc, msg, args):
        """takes no arguments

        Erases playerList file
        """
        self.singleeraser(irc)

    asingleerase = wrap(asingleerase, [("checkCapability", "admin")])

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
            irc.reply("Area Switching Mode Off     - setoption townwork off", private=True)
            irc.reply("Autostart Mode Off          - setoption autostart false", private=True)
            irc.reply("Autostart Mode On           - setoption autostart true", private=True)
            irc.reply("BlackBuy Spend Mode Off     - setoption blackbuy false", private=True)
            irc.reply("BlackBuy Spend Mode On      - setoption blackbuy true", private=True)
            irc.reply("BlackBuy 14 Spend Mode Off  - setoption blackbuy14 false", private=True)
            irc.reply("BlackBuy 14 Spend Mode On   - setoption blackbuy14 true", private=True)
            irc.reply("Bot Text Mode Off           - setoption bottext false", private=True)
            irc.reply("Bot Text Mode On            - setoption bottext true", private=True)
            irc.reply("Buy Life Mode Off           - setoption buylife false", private=True)
            irc.reply("Buy Life Mode On            - setoption buylife true", private=True)
            irc.reply("Buy Luck Potion Mode Off    - setoption buyluck false", private=True)
            irc.reply("Buy Luck Potion Mode On     - setoption buyluck true", private=True)
            irc.reply("Buy Power Potion Mode Off   - setoption buypower false", private=True)
            irc.reply("Buy Power Potion Mode On    - setoption buypower true", private=True)
            irc.reply("CreepAttack Mode Off        - setoption creepattack false", private=True)
            irc.reply("CreepAttack Mode On         - setoption creepattack true", private=True)
            irc.reply("Erase Config File           - eraseconfig", private=True)
            irc.reply("Erase PlayerList            - asingleerase", private=True)
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
            irc.reply("Players List                - aplayerslist", private=True)
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
            irc.reply("If you want more information about a command use <bot> help abandonedplaybot <command> - ie /msg DudeRuss help abandonedplaybot settings", private=True)

    help = wrap(help)

    def settings(self, irc, msg, args):
            """takes no arguments

            Gives a list of settings which you can change
            """
            global buylife
            global buyluck
            global buypower
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
            global autostartmode

            irc.reply("Playbot Settings List", private=True)
            irc.reply(" ", private=True)
            if townworkswitch is True:
                    irc.reply("Area Switch Mode - Town/Work", private=True)
            if townworkswitch is False:
                    irc.reply("Area Switch Mode - Town/Forest", private=True)
            if townworkswitch is None:
                     irc.reply("Area Switch Mode - Deactivated", private=True)
            irc.reply("Autostart Mode - {0}           BlackBuy Spend Mode - {1}".format(autostartmode, blackbuyspend), private=True)
            irc.reply("BlackBuy 14 Spend Mode - {0}   Bot Text Mode - {1}".format(blackbuyspend14, bottextmode), private=True)
            irc.reply("Buy Life Mode - {0}            Buy Luck Potion Mode - {1}".format(buylife, buyluck), private=True)
            irc.reply("Buy Power Potion Mode - {0}    CreepAttack Mode - {1}".format(buypower, creepattack), private=True)
            irc.reply("Error Text Mode - {0}          Experience Buying Mode - {1}".format(errortextmode, expbuy), private=True)
            irc.reply("Fighting Mode - {0}            GameBot PMs Mode - {1}".format(fightmode, pmtextmode), private=True)
            irc.reply("GetGems Mode - {0}             Goldsave - {1}".format(getgems, goldsave), private=True)
            irc.reply("Interval Text Mode - {0}       Item Buy Level - {1}".format(intervaltext, setbuy), private=True)
            irc.reply("Player Character - {0}         Scrolls Buy ItemScore - {1}".format(name, scrollssum), private=True)
            irc.reply("Set Creep Target - {0}         SlaySum Minimum - {1}".format(setcreeptarget, slaysum), private=True)
            irc.reply("XPSpend Upgrade Amount - {0}   XPUpgrade Mode - {1}".format(xpspend, xpupgrade), private=True)

    settings = wrap(settings, [("checkCapability", "admin")])

    def newlister2(self, irc):
        global playerlist
        global newlist
        global ability
        global webworks
        global webworks2
        global playerspagelist
        global website2

        newlist = []
        count = 0
        newlistererror = False

        if webworks is True and playerlist != None:
                for player in playerlist:
                        count += 1
                        if count > 3:
                                player = player.split(" ")
                                # extract players sum
                                levelIdx = None
                                abilityIdx = None
                                upgradelevelIdx = None
                                expertIdx1 = None
                                expertIdx2 = None
                                expertIdx3 = None
                                onlineIdx = None
                                lifeIdx = None
                                
                                amuletIdx = None
                                bootsIdx = None
                                charmIdx = None
                                glovesIdx = None
                                helmIdx = None
                                leggingsIdx = None
                                ringIdx = None
                                shieldIdx = None
                                tunicIdx = None
                                weaponIdx = None
                                sumIdx = None

                                for index, entry in enumerate(player):
                                        if(entry == "level"):
                                           levelIdx = index + 1
                                           lifeIdx = index + 3
                                        if(entry == "ability"):
                                           abilityIdx = index + 1

                                        if(entry == "upgrade"):
                                           upgradelevelIdx = index + 1
                                        if(entry == "ExpertItem01"):
                                           expertIdx1 = index + 1
                                        if(entry == "ExpertItem02"):
                                           expertIdx2 = index + 1
                                        if(entry == "ExpertItem03"):
                                           expertIdx3 = index + 1
                                        if(entry == "online"):
                                           onlineIdx = index + 1

                                        if(entry == "item_amulet"):
                                           amuletIdx = index + 1
                                        if(entry == "item_boots"):
                                           bootsIdx = index + 1
                                        if(entry == "item_charm"):
                                           charmIdx = index + 1
                                        if(entry == "item_gloves"):
                                           glovesIdx = index + 1
                                        if(entry == "item_helm"):
                                           helmIdx = index + 1
                                        if(entry == "item_leggings"):
                                           leggingsIdx = index + 1
                                        if(entry == "item_ring"):
                                           ringIdx = index + 1
                                        if(entry == "item_shield"):
                                           shieldIdx = index + 1
                                        if(entry == "item_tunic"):
                                           tunicIdx = index + 1
                                        if(entry == "item_weapon"):
                                           weaponIdx = index + 1

                                try:
                                        online_ = 0
                                        online_ = int(player[onlineIdx])
                                        
                                        if online_ == 1:
                                                rank_ = 0
                                                if webworks2 is True and playerspagelist != None:
                                                        for entry9 in playerspagelist:
                                                                if website2 in entry9 and ">{0}<".format(player[1]) in entry9:
                                                                        try:
                                                                                test = entry9
                                                                                test = test.split(">")
                                                                                ranktext = test[2]
                                                                                ranktext = ranktext.split("</")
                                                                                rank_ = int(ranktext[0])
                                                                        except:
                                                                                rank_ = 0
                                                                        
                                                level_ = int(player[levelIdx])

                                                amulet_ = int(player[amuletIdx])
                                                boots_ = int(player[bootsIdx])
                                                charm_ = int(player[charmIdx])
                                                gloves_ = int(player[glovesIdx])
                                                helm_ = int(player[helmIdx])
                                                leggings_ = int(player[leggingsIdx])
                                                ring_ = int(player[ringIdx])
                                                shield_ = int(player[shieldIdx])
                                                tunic_ = int(player[tunicIdx])
                                                weapon_ = int(player[weaponIdx])
                                                sum_ = amulet_ + boots_ + charm_ + gloves_ + helm_ + leggings_ + ring_ + shield_ + tunic_ + weapon_

                                                expert1_ = player[expertIdx1]
                                                expert2_ = player[expertIdx2]
                                                expert3_ = player[expertIdx3]
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

                                                ability_ = player[abilityIdx]
                                                upgradelevel_ = int(player[upgradelevelIdx])
                                                ulevelcalc = upgradelevel_ * 100
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
                                                life_ = float(player[lifeIdx])
                                                lifecalc = life_ / 100
                                                adjSum = math.floor((sum_ + ulevelcalc + abilityadj + expertcalcsumtotal) * lifecalc)

                                                                # char       sum          adjSum  level   life   ability   rank
                                                newlist.append( ( player[1], float(sum_), adjSum, level_, life_, ability_, rank_) )

                                except:
                                        newlistererror = True

        if newlistererror is True:
                webworks = False
                if errortextmode is True:
                        self.reply(irc, "Newlister Error")

        newlist.sort( key=operator.itemgetter(1), reverse=True )
        newlist.sort( key=operator.itemgetter(3) )
#        self.reply(irc, "{0}".format(newlist))

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
            
            global powerpots
            global fights
            global gold
            global gems
            global xp
            global mana
            global luck
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
            global eatused

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
                irc.reply("Luck Potion: {0}  Mana Potion: {1}  Power Potions: {2}".format(luck, mana, powerpots), private=True)
                if(level >= 25):
                        irc.reply("Fights: {0} of 5".format(fights), private=True)
                if(level < 25):
                        irc.reply("Fights Start at Level 25", private=True)
                irc.reply("Gems: {0}  Gold: {1}  XP: {2}".format(gems, gold, xp), private=True)
                irc.reply("Lotto1: {0}  Lotto2: {1}  Lotto3: {2}".format(lottonum1, lottonum2, lottonum3), private=True)
                irc.reply("Exp Used: {0} of 5  Scrolls: {1} of 5  Eat Used: {2} of 5".format(exp, scrolls, eatused), private=True)
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
            global myentry
            global rawplayers3
            global python3
            global website
            global playbottext
            global errortextmode
            
            webworks = True
            weberror = False
            context = ssl._create_unverified_context()

            # get raw player data from web, parse for relevant entry
            try:
                if python3 is False:
                        text = urllib2.urlopen(website + "/indexraw3.html", context=context)
                if python3 is True:
                        text = urllib.request.urlopen(website + "/indexraw3.html", context=context)
                rawplayers3 = text.read()
                text.close()
                if python3 is True:
                        rawplayers3 = rawplayers3.decode("UTF-8")
            except:
                weberror = True

            if weberror is True:
                if errortextmode is True:
                        self.reply(irc, "1 {0} - Could not access {1}".format(playbottext, website))
                webworks = False

            # build list for player records
            if(rawplayers3 is None):
                    if errortextmode is True:
                            self.reply(irc, "1 {0} - Could not access {1}, unknown error.".format(playbottext, website) )
                    webworks = False
            else:
                    playerlist = rawplayers3.split("\n")
                    playerlist = playerlist[:-1]
            # extract our player's record and make list
            if webworks is True:
                for entry in playerlist:
                        if "char" in entry:
                                entry = entry.split(" ")
                                
                                try:
                                        if(entry[1] == name):
                                                myentry = entry
                                except IndexError:
                                        webworks = False
                                        self.reply(irc, "myentry fail")

    def webdata2(self, irc):
        global webworks2
        global python3
        global playerspage
        global playerspagelist
        global website
        global website3
        global playbottext
        global errortextmode
        
        webworks2 = True
        weberror = False

        context = ssl._create_unverified_context()
        # get raw player data from web, parse for relevant entry
        try:
                if python3 is False:
                        text2 = urllib2.urlopen(website + website3, context=context)
                if python3 is True:
                        text2 = urllib.request.urlopen(website + website3, context=context)
                playerspage = text2.read()
                text2.close()
                if python3 is True:
                        playerspage = playerspage.decode("UTF-8")
        except:
                weberror = True
        if weberror is True:
                if errortextmode is True:
                        self.reply(irc, "2 {0} - Could not access {1}".format(playbottext, website))
                webworks2 = False

        if(playerspage is None):
                if errortextmode is True:
                        self.reply(irc, "2 {0} - Could not access {1}, unknown error.".format(playbottext, website) )
                webworks2 = False
        else:
                playerspagelist = playerspage.split("\n")
                playerspagelist = playerspagelist[:-1]

    def playerarea(self, irc):
        global level
        global mysum
        global location
        global locationtime
        global townworkswitch
        global areasum
        
        if townworkswitch is True:
                area = "work"
        if townworkswitch is False:
                area = "forest"
        if townworkswitch is None:
                return

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
                
        if(location == "In Town" and locationtime >= mintime and mysum < areasum and mysum != 0):
                self.usecommand(irc, "goto {0}".format(area))
        if(location == "In Town" and mysum >= areasum):
                self.usecommand(irc, "goto {0}".format(area))
        if(location == "At Work" and locationtime >= mintime):
                self.usecommand(irc, "goto town")
        if(location == "In The Forest" and locationtime >= (24 * 60 * 60)):
                self.usecommand(irc, "goto town")

    def getvariables(self, irc):
        global myentry
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
        global luck
        global mana
        global powerpots
        global align
        global eatused

        global stone1
        global stone2
        global stone3
        global expert1
        global expert2
        global expert3

        global atime
        global stime
        global webworks
        global gameactive
        global lottonum1
        global lottonum2
        global lottonum3
        global playbottext
        global location
        global locationtime
        global errortextmode
        global online
        
        lotto11 = 0
        lotto12 = 0
        lotto13 = 0
        lotto21 = 0
        lotto22 = 0
        lotto23 = 0
        lotto31 = 0
        lotto32 = 0
        lotto33 = 0
        worktime = 0
        towntime = 0
        foresttime = 0
        locationtime = 0
        location = None
        
        # get current system time UTC
        now = int( time.time() )

        if webworks is True and gameactive is True and myentry != None:
                for index, var in enumerate(myentry):
                        i = index + 1
                        if( i >= len(myentry) ):
                                break
                        num = myentry[i]
                        if str.isdigit(num):
                                num = int( num )
                        if var == "ExpertItem01":
                                expert1 = num
                        if var == "ExpertItem02":
                                expert2 = num
                        if var == "ExpertItem03":
                                expert3 = num
                        if var == "Foresttime":
                                foresttime = num
                                if foresttime > 0:
                                        foresttime = now - foresttime
                        if var == "Special01":
                                stone1 = num
                        if var == "Special02":
                                stone2 = num
                        if var == "Special03":
                                stone3 = num
                        if var == "Towntime":
                                towntime = num
                                if towntime > 0:
                                        towntime = now - towntime
                        if var == "Worktime":
                                worktime = num
                                if worktime > 0:
                                        worktime = now - worktime
                        if var == "ability":
                                ability = num
                        if var == "alignment":
                                align = num
                        if var == "dragontm":
                                try:
                                        stime = num - now
                                except:
                                        stime = 0
                        if var == "expcount":
                                try:
                                        exp = num
                                except:
                                        exp = 0
                        if var == "experience":
                                xp = num
                        if var == "ffight":
                                eatused = num
                        if var == "fightcount":
                                fights = num
                        if var == "gems":
                                gems = num
                        if var == "gold":
                                gold = num
                        if var == "item_amulet":
                                amulet = num
                        if var == "item_boots":
                                boots = num
                        if var == "item_charm":
                                charm = num
                        if var == "item_gloves":
                                gloves = num
                        if var == "item_helm":
                                helm = num
                        if var == "item_leggings":
                                leggings = num
                        if var == "item_ring":
                                ring = num
                        if var == "item_shield":
                                shield = num
                        if var == "item_tunic":
                                tunic = num
                        if var == "item_weapon":
                                weapon = num
                        if var == "level":
                                level = num
                        if var == "life":
                                life = int(num)
                        if var == "lotto11":
                                lotto11 = num
                        if var == "lotto12":
                                lotto12 = num
                        if var == "lotto13":
                                lotto13 = num
                        if var == "lotto21":
                                lotto21 = num
                        if var == "lotto22":
                                lotto22 = num
                        if var == "lotto23":
                                lotto23 = num
                        if var == "lotto31":
                                lotto31 = num
                        if var == "lotto32":
                                lotto32 = num
                        if var == "lotto33":
                                lotto33 = num
                        if var == "luck":
                                luck = num
                        if var == "mana":
                                mana = num
                        if var == "online":
                                online = num
                        if var == "powerpotion":
                                powerpots = num
                        if var == "regentm":
                                try:
                                        atime = num - now
                                except:
                                        atime = 0
                        if var == "scrolls":
                                try:
                                        scrolls = num
                                except:
                                        scrolls = 0
                        if var == "next":
                                ttl = num
                        if var == "upgrade":
                                upgradelevel = num

                        mysum = int(amulet + boots + charm + gloves + helm + leggings + ring + shield + tunic + weapon)
                        lottonum1 = "{0} {1} and {2}".format(lotto11, lotto12, lotto13)
                        lottonum2 = "{0} {1} and {2}".format(lotto21, lotto22, lotto23)
                        lottonum3 = "{0} {1} and {2}".format(lotto31, lotto32, lotto33)
                        
                        if worktime > 0:
                                location = "At Work"
                                locationtime = worktime
                        if towntime > 0:
                                location = "In Town"
                                locationtime = towntime
                        if foresttime > 0:
                                location = "In The Forest"
                                locationtime = foresttime

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
            global powerpots
            global gold
            global life
            global buypower
            global slaysum
            global playbottext
            global bottextmode
            
            # make sure no times are negative
            if(atime < 0):
                    atime = 0
            if(stime < 0):
                    stime = 0
#            self.reply(irc, "atime {0}  stime {1}  ttl {2}".format(atime, stime, ttl))
            slaydisable = False
            
            def lvlupgoas():
                self.lvlup(irc)
            
            def attackgoas():
                self.attack(irc, 1)
            def attackgobas():
                self.attack(irc, 2)

            def slaygoas():
                self.slay(irc, 1)
            def slaygobas():
                self.slay(irc, 2)

            if(ttl <= interval and ttl > 0):
                    timer = time.time() + (ttl+10)
                    if bottextmode is True:
                            self.reply(irc, "{0} - Set lvlup timer. Going off in {1} minutes.".format(playbottext, ttl // 60))
                    try:
                        schedule.addEvent(lvlupgoas, timer, "lvlupas")
                    except AssertionError:
                        schedule.removeEvent('lvlupas')
                        schedule.addEvent(lvlupgoas, timer, "lvlupas")                        
            if(level >= 15 and atime <= interval and atime <= ttl and life > 10):
                    if powerpots == 0 and gold >= 1100 and buypower is True:
                        self.usecommand(irc, "buy power")
                        gold -= 1000
                        powerpots = 1

                    timer = time.time() + (atime+10)
                    if bottextmode is True:
                            self.reply(irc, "{0} - Set attack timer. Going off in {1} minutes.".format(playbottext, atime // 60))
                    slaydisable = True

                    if powerpots == 0:
                            try:
                                schedule.addEvent(attackgoas, timer, "attackas")
                            except AssertionError:
                                schedule.removeEvent('attackas')
                                schedule.addEvent(attackgoas, timer, "attackas")                        
                    if powerpots == 1:
                            powerpots = 0
                            try:
                                schedule.addEvent(attackgobas, timer, "attackas")
                            except AssertionError:
                                schedule.removeEvent('attackas')
                                schedule.addEvent(attackgobas, timer, "attackas")                        

            if(level >= 30 and attackslaySum >= 1000 and stime <= interval and stime <= ttl and slaydisable is False and life > 10):
                    if(mana == 0 and gold >= 1100 and attackslaySum < 6300000):
                        self.usecommand(irc, "buy mana")
                        gold -= 1000
                        mana = 1
                    timer = time.time() + (stime+10)
                    if mana == 0 and attackslaySum >= slaysum:
                            if bottextmode is True:
                                    self.reply(irc, "{0} - Set slay timer. Going off in {1} minutes.".format(playbottext, stime // 60))
                            try:
                                schedule.addEvent(slaygoas, timer, "slayas")
                            except AssertionError:
                                schedule.removeEvent('slayas')
                                schedule.addEvent(slaygoas, timer, "slayas")
                    if mana == 1:
                            if bottextmode is True:
                                    self.reply(irc, "{0} - Set slay timer. Going off in {1} minutes.".format(playbottext, stime // 60))
                            mana = 0
                            try:
                                schedule.addEvent(slaygobas, timer, "slayas")
                            except AssertionError:
                                schedule.removeEvent('slayas')
                                schedule.addEvent(slaygobas, timer, "slayas")

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
        global luck
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
        global buyluck
        global expbuy
        
        # level 15 >= buy - decide what to spend our gold on! :D
        # level 1 >= blackbuy - requires 15 gems per buy
        # level 1 >= get x gems - 150 gold per gem
        # xpget 20xp minimum
        # buy experience - 1000 gold - 10% off TTL
        
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
                
        if(gembuy is True and level >= 15 and buyluck is True):
                if(luck == 0 and gold >= 2100):
                        self.usecommand(irc, "buy luck")
                        luck = 1
                        gold -= 1000
                        
        if(gembuy is True and expbuy is True and exp < 5):
                expdiff = 5 - exp
                expcost = expdiff * 1000
                if(gold >= (expcost + 1100)):
                        for i in range(expdiff):
                                self.usecommand(irc, "buy exp")
                                gold -= 1000
                                exp += 1
                elif(gold >= 1000 + 1100):
                        golddiff = gold - 1100
                        expcalc = golddiff // 1000
                        if expcalc >= 1:
                                for i in range(expcalc):
                                        self.usecommand(irc, "buy exp")
                                        gold -= 1000
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
            global gold
            global powerpots
            global life
            global buypower
            global playbottext
            global bottextmode
           
            level += 1

            if bottextmode is True:
                    self.reply(irc, "{0} - {1} has reached level {2}!".format(playbottext, name, level))

            interval = 60
            self.looper(irc)

            def attackgoas():
                    self.attack(irc, 1)
            def attackgobas():
                    self.attack(irc, 2)

            if(level >= 16 and life > 10):
                    if powerpots == 0 and gold >= 1100 and buypower is True:
                        self.usecommand(irc, "buy power")
                        gold -= 1000
                        powerpots = 1

                    if powerpots == 0:
                            try:
                                    schedule.addEvent(attackgoas, 0, "attackas")
                            except AssertionError:
                                    schedule.removeEvent('attackas')
                                    schedule.addEvent(attackgoas, 0, "attackas")                        
                    if powerpots == 1:
                            powerpots = 0
                            try:
                                    schedule.addEvent(attackgobas, 0, "attackas")
                            except AssertionError:
                                    schedule.removeEvent('attackas')
                                    schedule.addEvent(attackgobas, 0, "attackas")                        

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
                        self.reply(irc, "{0} - Best fight for Rank {1}:  {2}  [{3}]  Opponent: Rank {4}:  {5}  [{6}], Odds {7}".format(playbottext, rank, name, int(fightAdj), ufight[6], ufight[0], int(ufight[2]), ufightcalc))
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

    def attack(self, irc, num2):
        global creepattack
        global setcreeptarget
        
        if creepattack is True:
            creep = self.bestattack(num2)
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

    def bestattack(self, num2):
        global creeps
        global attackslaySum
              
        good = "CreepList Error"
        if num2 == 1:
                multi = 1
        if num2 == 2:
                multi = 2
        for thing in creeps:
                if((attackslaySum * multi) <= thing[1]):
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

        messagelist2 = [ ["Items: |Ring"],        \
                         ["| Gloves"],            \
                         ["| Gold:"],            \
                         ["| Fights Used:"],            \
                         ["| Power Potion:"],            \
                         ["| Lotto 1:"],            \
                         ["| Stone 1:"],            \
                         ["| Expert 1:"],            \
                         ["| Next Creep Attack:"],            \
                         ["| Tournament Recover:"],            \
                         ["| Quest Recover Time:"],            ]
        
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
                        if botname in chanmsgnick and "has challenged" in text and "is added to {0} clock".format(name) in text: #rand challenge
                                lifebuy = True
                        if botname in chanmsgnick and "has attacked a" in text and "is added to {0} clock".format(name) in text: #attack
                                lifebuy = True
                        if botname in chanmsgnick and "tried to slay a" in text and "is added to {0} clock".format(name) in text: #slay
                                lifebuy = True
                        if botname in chanmsgnick and "has been set upon by some" in text and "is added to {0}'s clock".format(name) in text: #rand creep
                                lifebuy = True
                        if botname in chanmsgnick and "fights a random" in text and "is added to {0} clock".format(name) in text: #rand god
                                lifebuy = True
                        if botname in chanmsgnick and "{0}".format(name) in text and "have hunted down a bunch of" in text and "but they beat them badly!" in text: #team hunt
                                lifebuy = True
                        if botname in chanmsgnick and "from {0}!".format(name) in text and "XP and loses" in text: #tourney
                                lifebuy = True
                        if lifebuy is True:
                                if(level >= 15 and buylife is True and life >= 0):
                                        self.usecommand(irc, "buy life")
                                        life = 100

                if(checknick == supynick and checknet == netname):
                        if(botname == chanmsgnick and "You are not logged in" in text):
                            if pmtextmode is True:
                                    self.reply(irc, "{0} - {1}".format(playbottext, text))
                            self.usecommand(irc, "login {0} {1}".format(name, pswd) )
                            interval = 60
                            self.looper(irc)
                            return               
                        for entry in messagelist:
                            if(botname == chanmsgnick and entry[0] in text):
                                if pmtextmode is True:
                                        self.reply(irc, "{0} - {1}".format(playbottext, text))
                                return
                        for entry in messagelist2:
                            if(botname == chanmsgnick and entry[0] in text):
                                return
                        if(botname == chanmsgnick and "You are {0}".format(name) in text):
                            if pmtextmode is True:
                                    self.reply(irc, "{0} - {1}".format(playbottext, text))
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
        global webworks2
        global rank
        global online
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
        global website2
        global ttl
        
        self.playbotcheck(irc)
        if intervaltext is True:
                self.reply(irc, "{0} - INTERVAL {1}".format(playbottext, time.asctime()) )

        oldttl = ttl
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
                                self.reply(irc, "{0} - Server Error".format(playbottext))
        except NameError:
                if errortextmode is True:
                        self.reply(irc, "{0} - Network not connected to supybot".format(playbottext))
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
                            self.reply(irc, "{0} - Game Bot not in channel".format(playbottext))
            except KeyError:
                if errortextmode is True:
                        self.reply(irc, "{0} - Game Bot not in channel".format(playbottext))

        online = 0
        if botcheck is True:
                self.webdata(irc)
                self.webdata2(irc)
                if webworks is True:
                        self.getvariables(irc)

        test = []
        rank = 0
        if webworks2 is True and gameactive is True and botcheck is True:
                if online == 1:
                        for entry in playerspagelist:
                                if website2 in entry and ">{0}<".format(name) in entry:
                                        try:
                                                test = entry
                                                test = test.split(">")
                                                ranktext = test[2]
                                                ranktext = ranktext.split("</")
                                                rank = int(ranktext[0])
                                        except:
                                                rank = 0
        if(webworks is True and online == 0 and botcheck is True):
                if errortextmode is True:
                        self.reply(irc, "{0} - Player Offline".format(playbottext))

        if webworks is True and online == 0 and botcheck is True:
                if netcheck is True:
                        self.usecommand(irc, "login {0} {1}".format(name, pswd) )
                        interval = 45
                        self.looper(irc)
                        intervaldisable = True

        if ((webworks is False and webworks2 is True) or (webworks is True and webworks2 is False)) and intervaldisable is False:
            interval = 60
            self.looper(irc)
            intervaldisable = True
        if webworks is False and webworks2 is False and intervaldisable is False:
            interval = 300
            self.looper(irc)
            intervaldisable = True
        if webworks is True and webworks2 is True and intervaldisable is False:
            self.intervalcalc(irc)
               
        if webworks is True and online == 1 and botcheck is True:
                self.playerarea(irc)
                self.spendmoney(irc)
                self.timercheck(irc)
                if(level >= 25 and fights >= 0 and fights < 5 and life > 0):
                        if bottextmode is True:
                                self.reply(irc, "{0} - Fights available".format(playbottext))
                if(level >= 25 and fights >= 0 and fights < 5 and life > 10):
                        self.newlister2(irc)
                        self.fight_fight(irc)

        if(webworks is True and botcheck is True):
                if online == 1:
                        if(ttl == oldttl):
                                if errortextmode is True:
                                        self.reply(irc, "{0} - TTL Frozen".format(playbottext))

        return 1
    
    def intervalcalc(self, irc):
        global interval
        global level
        global fights
        global botcheck
        global online
        global life
        global fightmode
        
        interval = 5
        interval *= 60                  # conv from min to sec

        if botcheck is False or online == 0:
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
        
        def loopas():
            self.main(irc)
        nextTime = time.time() + interval
        
        if intervaltext is True:
                self.reply(irc, "{0} - Checking timers every {1} minutes".format(playbottext, interval // 60))
        if gameactive is True:
            try:
                schedule.addEvent(loopas, nextTime, "loopas")
            except AssertionError:
                schedule.removeEvent('loopas')
                schedule.addEvent(loopas, nextTime, "loopas")        

    def __init__(self, irc):
        self.__parent = super(AbandonedPlayBot, self)
        self.__parent.__init__(irc)

        if autostartmode is True:
                self.autostart(irc)

    def die(self):
        self.__parent.die()
        try:
                schedule.removeEvent('loopas')
        except:
                return

Class = AbandonedPlayBot


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
