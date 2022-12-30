###
# Copyright (c) 2018-2022, Russell Beech
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
    _ = PluginInternationalization('PlayBotSingle')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

__module_name__ = "Multirpg Playbot Script"
__module_version__ = "2.8"
__module_description__ = "Multirpg Playbot Script"

# build hardcoded monster/creep lists, reverse
# Creep Recovery Multipliers:
# Bush, Locust x 1
# Spider, Goblin, Lich, Skeleton, Ghost, Shadow x 2
# Troll, Cyclops, Mutant, Monkey x 3
# Phoenix, Minotaur, Beholder, Wyvern x 4
# Ogre x 5

creeps = [      ["Bush",        10],    \
                ["Locust",      15],    \
                ["Spider",      20],    \
                ["Goblin",      30],    \
                ["Lich",        40],    \
#               ["Skeleton",    50],    \
#               ["Ghost",       60],    \
                ["Shadow",      70],    \
#               ["Troll",       80],    \
#               ["Cyclops",     90],    \
#               ["Mutant",      100],   \
                ["Monkey",      110],   \
                ["Phoenix",     120],   \
                ["Minotaur",    130],   \
                ["Beholder",    140],   \
                ["Wyvern",      150],   \
                ["Ogre",        1600],  ]

monsters = [    ["Medusa",      3500],  \
                ["Centaur",     4000],  \
                ["Mammoth",     5000],  \
                ["Vampire",     6000],  \
                ["Dragon",      7000],  \
                ["Sphinx",      8000],  \
                ["Hippogriff",  999999] ]

# list of all networks
#                   Network,        Server,                     NoLag   SNum    Port    SSL     BotHostMask
networklist = [     ["AyoChat",     "irc.ayochat.or.id",        False,  1,      6667,   False,  "multirpg@venus.skralg.com"],  \
                    ["AyoChat",     "149.202.240.157",          False,  2,      6667,   False,  "multirpg@venus.skralg.com"],  \
                    ["ChatLounge",  "irc.chatlounge.net",       True,   1,      6667,   False,  "multirpg@2001:579:9f05:1800:9119:8531:5e14:559"],  \
                    ["ChatLounge",  "185.34.216.32",            True,   2,      6667,   False,  "multirpg@2001:579:9f05:1800:9119:8531:5e14:559"],  \
                    ["DALnet",      "irc.dal.net",              False,  1,      6667,   False,  "multirpg@venus.skralg.com"], \
                    ["DALnet",      "94.125.182.251",           False,  2,      6667,   False,  "multirpg@venus.skralg.com"], \
                    ["EFnet",       "irc.efnet.net",            False,  1,      6667,   False,  "multirpg@venus.skralg.com"], \
                    ["EFnet",       "66.225.225.225",           False,  2,      6667,   False,  "multirpg@venus.skralg.com"], \
                    ["GameSurge",   "irc.gamesurge.net",        True,   1,      6667,   False,  "multirpg@multirpg.bot.gamesurge"],  \
                    ["GameSurge",   "195.68.206.250",           True,   2,      6667,   False,  "multirpg@multirpg.bot.gamesurge"],  \
                    ["IRC4Fun",     "irc.irc4fun.net",          False,  1,      6667,   False,  "multirpg@bots/multirpg"],  \
                    ["IRC4Fun",     "139.99.113.250",           False,  2,      6667,   False,  "multirpg@bots/multirpg"],  \
                    ["Koach",       "irc.koach.com",            False,  1,      6667,   False,  ".skralg.com"], \
                    ["Koach",       "172.105.168.90",           False,  2,      6667,   False,  ".skralg.com"], \
                    ["Libera",      "irc.libera.chat",          False,  1,      6667,   False,  "multirpg@venus.skralg.com"], \
                    ["Libera",      "130.185.232.126",          False,  2,      6667,   False,  "multirpg@venus.skralg.com"], \
                    ["mIRCPhantom", "irc.mircphantom.net",      False,  1,      6667,   False,  ".skralg.com"], \
                    ["mIRCPhantom", "51.89.198.165",            False,  2,      6667,   False,  ".skralg.com"], \
                    ["Pissnet",     "irc.letspiss.net",         False,  1,      6667,   False,  ".skralg.com"], \
                    ["Pissnet",     "91.92.144.105",            False,  2,      6667,   False,  ".skralg.com"], \
                    ["QuakeNet",    "irc.quakenet.org",         False,  1,      6667,   False,  "multirpg@multirpg.users.quakenet.org"], \
                    ["QuakeNet",    "188.240.145.70",           False,  2,      6667,   False,  "multirpg@multirpg.users.quakenet.org"], \
                    ["Rizon",       "irc.rizon.net",            False,  1,      6667,   False,  ".skralg.com"], \
                    ["Rizon",       "80.65.57.18",              False,  2,      6667,   False,  ".skralg.com"], \
                    ["ScaryNet",    "irc.scarynet.org",         True,   1,      6667,   False,  "multirpg@venus.skralg.com"],  \
                    ["ScaryNet",    "69.162.163.62",            True,   2,      6667,   False,  "multirpg@venus.skralg.com"],  \
                    ["SkyChatz",    "irc.skychatz.org",         False,  1,      6667,   False,  "multirpg@skychatz.user.multirpg"],  \
                    ["SkyChatz",    "15.235.141.21",            False,  2,      6667,   False,  "multirpg@skychatz.user.multirpg"],  \
                    ["Techtronix",  "irc.techtronix.net",       True,   1,      6697,   True,   "multirpg@multirpg.net"],  \
                    ["Techtronix",  "35.229.28.106",            True,   2,      6697,   True,   "multirpg@multirpg.net"],  \
                    ["Undernet",    "irc.undernet.org",         False,  1,      6667,   False,  "multirpg@idlerpg.users.undernet.org"], \
                    ["Undernet",    "154.35.136.18",            False,  2,      6667,   False,  "multirpg@idlerpg.users.undernet.org"], \
                    ["UniversalNet","irc.universalnet.org",     False,  1,      6667,   False,  "multirpg@venus.skralg.com"], \
                    ["UniversalNet","62.171.172.8",             False,  2,      6667,   False,  "multirpg@venus.skralg.com"], \
                    ["Virtulus",    "irc.virtulus.net",         True,   1,      6667,   False,  "multirpg@B790DC3F.D0CDF40.88109D7.IP"], \
                    ["Virtulus",    "18.193.247.191",           True,   2,      6667,   False,  "multirpg@B790DC3F.D0CDF40.88109D7.IP"] ]

creeps.reverse()
monsters.reverse()

multirpgweb = "https://www.multirpg.net/"
idlerpgweb = "http://www.idlerpg.org/"
russweb = "https://russellb.000webhostapp.com/"
rawplayers3 = None
interval = 300
newlist = None
playerlist = None
myentry = None
rawmyentry = None
rawmyentryfail = 0
currentversion = __module_version__
currentversion = float( currentversion )

# custom network settings - For linked networks or networks which are not on the networklist
customnetworksettings = False # True = on, False = off - For custom networks which are not on the networklist
customservername = "irc.mircphantom.net" # Custom Server address
customservername2 = "176.31.181.159" # Custom Server address
customchanname = "#multirpg" # Custom Channel Name
custombotname = "multirpg/fun" # Custom Botname
customnolag = False # True = on, False = off - If network is on the nolag network list
customport = 6667 # port
customssl = False # True = on, False = off - SSL
custombosthostmask = "multirpg@multirpg.users.IRC4Fun.net" # Custom Bot Host Name

# ZNC settings - Ignore if networkreconnect is False
ZNC = False # ZNC Server Mode - True = On, False = Off
ZNCServer = "" # ZNC Server Address
ZNCPort = 1234 # ZNC Port Number
ZNCUser = "/" # ZNC Username/Network
ZNCPass = "" # ZNC Password
ZNCssl = False # True = on, False = off
ZNCnolag = False # True = on, False = off

# Changeable settings
multirpgclass = "MultiRPG PlayBot" # Class to be used when auto-registering
nickserv = False # True = on, False = off
nickservpass = "" # NickServ Password
laglevel = 25 # If using rawstats and a laggy network it will switch between using rawstats and rawplayers
networkreconnect = False # True = on, False = off - Reconnects network connection and server address switching
connectretry = 6 # Retries to connect to network
setalign = 40 # Level in which alignment changes from permanent priest to human/priest switching
upgradeall = True # True = on, False = off - Upgrades all 1 and above after Hero and Engineer is upgraded to level 9
itemupgrader = True # True = on, False = off - Upgrades individual items after Hero and Engineer is upgraded to level 9
betmoney = 220 # Money kept in bank to be used for bets
sethero = 1200 # item score to start to buy/upgrading hero
setengineer = 25 # level to start to buy/upgrading engineer
setbuy = 16 # level to start buying items from
singlefight = True # True = on, False = off
evilmode = False # True = on, False = off
webnum = 1 # 1 = multirpg.net, 2 = idlerpg.org
bottextmode = True # True = on, False = off
errortextmode = True # True = on, False = off
noticetextmode = True # True = on, False = off
pmtextmode = True # True = on, False = off
intervaltextmode = True # True = on, False = off
remotekill = True # True = on, False = off # Gives me the option if the PlayBot is flooding the GameBot to disable the PlayBot
autoconfig = 1 # 0 = off, 1 = on, 2 = remove config changes.
loginsettingslister = True # True = on, False = off - Settings List at start

# declare stats as global
name = None
pswd = None
servername = None
networkname = None
servernum = 1
ssl = None
port = None
connectfail = 0
webfail = 0
nolag = None
charcount = 0
rankplace = 0
level = 0
alignlevel = 0
mysum = 0
gold = 0
bank = 0
team = 0
ufightcalc = 0
fightSum = 0

hero = 0
hlvl = 0
eng = 0
elvl = 0
ttl = 0
atime = 0 # regentm
ctime = 0 # challengetm
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

bets = 0
fights = 0
powerpots = 0
firstalign = "priest"
secondalign = "human"
rawstatsmode = False
rawstatsswitch = False
levelrank1 = 0

nickname = None
netname = None
channame = None
botname = None
botcheck = None
bothostcheck = False
bothostmask = None
chancheck = None
webworks = None
gameactive = None

otherIrc = None
supynick = None
ttlfrozen = 0
ttlfrozenmode = False
botdisable1 = False
Owner = None
jumpnetwork = False
autostartmode = False
playbotcount = 0
playbottext = None
playbotid = "PS"
pbcount = 0

playbotsingle = False
playbotmulti = False

fileprefix = "playbotsingleconfig.txt"
path = conf.supybot.directories.data
filename = path.dirize(fileprefix)
try:
        f = open(filename,"rb")
        configList = pickle.load(f)
        f.close()
except:
        configList = []
fileprefix2 = "autostartsingleconfig.txt"
path = conf.supybot.directories.data
filename2 = path.dirize(fileprefix2)
try:
        f = open(filename2,"rb")
        autoconfigList = pickle.load(f)
        f.close()
except:
        autoconfigList = []
fileprefix3 = "playbotsingleplayers.txt"
path = conf.supybot.directories.data
filename3 = path.dirize(fileprefix3)
fileprefix4 = "playbotmultiplayers.txt"
path = conf.supybot.directories.data
filename4 = path.dirize(fileprefix4)

for entry in configList:
        if(entry[0] == "autostartmode"):
                autostartmode = entry[1]
        if(entry[0] == "betmoney"):
                betmoney = entry[1]
        if(entry[0] == "bottextmode"):
                bottextmode = entry[1]
        if(entry[0] == "errortextmode"):
                errortextmode = entry[1]
        if(entry[0] == "evilmode"):
                evilmode = entry[1]
        if(entry[0] == "intervaltextmode"):
                intervaltextmode = entry[1]
        if(entry[0] == "itemupgrader"):
                itemupgrader = entry[1]
        if(entry[0] == "noticetextmode"):
                noticetextmode = entry[1]
        if(entry[0] == "pmtextmode"):
                pmtextmode = entry[1]
        if(entry[0] == "rawstatsmode"):
                rawstatsmode = entry[1]
        if(entry[0] == "rawstatsswitch"):
                rawstatsswitch = entry[1]
        if(entry[0] == "setalign"):
                setalign = entry[1]
        if(entry[0] == "sethero"):
                sethero = entry[1]
        if(entry[0] == "setengineer"):
                setengineer = entry[1]
        if(entry[0] == "setbuy"):
                setbuy = entry[1]
        if(entry[0] == "singlefight"):
                singlefight = entry[1]
        if(entry[0] == "upgradeall"):
                upgradeall = entry[1]

class PlayBotSingle(callbacks.Plugin):
    """MultiRPG PlayBotSingle"""
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

        webversion = None
        try:
                if python3 is False:
                        text = urllib2.urlopen(russweb + "playbotversionsupy.txt")
                if python3 is True:
                        text = urllib.request.urlopen(russweb + "playbotversionsupy.txt")
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
                    self.reply(irc, "You can download a new version from {0}".format(russweb))
                if(currentversion > webversion):
                    self.reply(irc, "Give me, Give me")

    def configwrite(self):
        global autostartmode
        global betmoney
        global evilmode
        global itemupgrader
        global rawstatsmode
        global setalign
        global setbuy
        global setengineer
        global sethero
        global singlefight
        global upgradeall
        global rawstatsswitch
        global bottextmode
        global errortextmode
        global intervaltextmode
        global noticetextmode
        global pmtextmode

        configList = []
        configList.append( ( "autostartmode", autostartmode ) )
        configList.append( ( "betmoney", betmoney ) )
        configList.append( ( "bottextmode", bottextmode ) )
        configList.append( ( "errortextmode", errortextmode ) )
        configList.append( ( "evilmode", evilmode ) )
        configList.append( ( "intervaltextmode", intervaltextmode ) )
        configList.append( ( "itemupgrader", itemupgrader ) )
        configList.append( ( "noticetextmode", noticetextmode ) )
        configList.append( ( "pmtextmode", pmtextmode ) )
        configList.append( ( "rawstatsmode", rawstatsmode ) )
        configList.append( ( "rawstatsswitch", rawstatsswitch ) )
        configList.append( ( "setalign", setalign ) )
        configList.append( ( "setbuy", setbuy ) )
        configList.append( ( "setengineer", setengineer ) )
        configList.append( ( "sethero", sethero ) )
        configList.append( ( "singlefight", singlefight ) )
        configList.append( ( "upgradeall", upgradeall ) )
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
        global betmoney
        global evilmode
        global itemupgrader
        global rawstatsmode
        global setalign
        global setbuy
        global setengineer
        global sethero
        global singlefight
        global upgradeall
        global rawstatsswitch
        global rawmyentry
        global ttlfrozen
        global secondalign
        global alignlevel
        global level
        global firstalign
        global bottextmode
        global errortextmode
        global intervaltextmode
        global noticetextmode
        global pmtextmode
        global autostartmode
        global gameactive
        
        if value.lower()=='true':
            value=True
        elif value.lower()=='false':
            value=False

        if gameactive is True:
        ##      Sets which level you start doing priest/human alignment changes
                if text == "alignlevel":
                        if str.isdigit(value):
                                setalign = int( value )
                        irc.reply("Align Level changed to {0}".format(setalign), private=True)
                        if(setalign > level):
                                self.usecommand(irc, "align {0}".format(firstalign))
                        if(setalign <= level):
                                self.usecommand(irc, "align {0}".format(secondalign))
        ##      Sets how much gold you keep in your bank to be used for bets
                if text == "betmoney":
                        if str.isdigit(value):
                                betmoney = int( value )
                        irc.reply("Betmoney changed to {0}".format(betmoney), private=True)
        ##      Sets at which level you will buy your engineer from
                if text == "engineerbuy":
                        if str.isdigit(value):
                                setengineer = int( value )
                        irc.reply("Engineer Buy Level changed to {0}".format(setengineer), private=True)
        ##      Sets at which item score you will buy your hero from
                if text == "herobuy":
                        if str.isdigit(value):
                                sethero = int( value )
                        irc.reply("Hero Buy Item Score changed to {0}".format(sethero), private=True)
        ##      Sets at which level you will start buying items from
                if text == "itembuy":
                        if str.isdigit(value):
                                setbuy = int( value )
                        irc.reply("Item Buy Level changed to {0}".format(setbuy), private=True)
                if text == "singlefight":
        ##              You use 1 fight at a time instead of all 5 fights together
                        if value is True:
                                singlefight = True
                                irc.reply("Single Fight Mode Activated.  To use Multiple Fight mode use 'setoption singlefight false' command", private=True)
        ##              You use all 5 fights together
                        if value is False:
                                singlefight = False
                                irc.reply("Multiple Fight Mode Activated.  To use Single Fight mode use 'setoption singlefight true' command", private=True)
                if text == "upgradeall":
        ##              Turns on upgrade all in multiples of 1.  This only works once you have maxed your hero and engineer
                        if value is True:
                                upgradeall = True
                                irc.reply("Upgrade All Mode Activated.  To turn it off use 'setoption upgradeall false' command", private=True)
        ##              Turns off upgrade all in multiples of 1
                        if value is False:
                                upgradeall = False
                                irc.reply("Upgrade All Mode Deactivated.  To turn it back on use 'setoption upgradeall true' command", private=True)
                if text == "itemupgrader":
        ##              Turns on upgrades to your weakest item.  This only works once you have maxed your hero and engineer
                        if value is True:
                                itemupgrader = True
                                irc.reply("Item Upgrader Mode Activated.  To turn it off use 'setoption itemupgrader false' command", private=True)
        ##              Turns off upgrades to your weakest item
                        if value is False:
                                itemupgrader = False
                                irc.reply("Item Upgrader Mode Deactivated.  To turn it back on use 'setoption itemupgrader true' command", private=True)
                if text == "rawstats":
        ##              Turns on getting data from rawstats instead of rawplayers.  It is best not to use rawstats on laggy networks at game reset and use rawplayers instead
                        if value is True:
                                rawstatsswitch = True
                                rawstatsmode = True
                                irc.reply("Rawstats Mode Activated.  To turn it back to Rawplayers Mode use 'setoption rawplayers true' command", private=True)
        ##              Turns on getting data from rawplayers instead of rawstats
                        if value is False:
                                rawmyentry = None
                                ttlfrozen = 0
                                rawstatsswitch = False
                                rawstatsmode = False
                                irc.reply("Rawplayers Mode Activated.  To turn it back to Rawstats Mode use 'setoption rawstats true' command", private=True)
                if text == "rawplayers":
        ##              Turns on getting data from rawplayers instead of rawstats
                        if value is True:
                                rawmyentry = None
                                ttlfrozen = 0
                                rawstatsswitch = False
                                rawstatsmode = False
                                irc.reply("Rawplayers Mode Activated.  To turn it back to Rawstats Mode use 'setoption rawstats true' command", private=True)
        ##              Turns on getting data from rawstats instead of rawplayers.  It is best not to use rawstats on laggy networks at game reset and use rawplayers instead
                        if value is False:
                                rawstatsswitch = True
                                rawstatsmode = True
                                irc.reply("Rawstats Mode Activated.  To turn it back to Rawplayers Mode use 'setoption rawplayers true' command", private=True)
                if text == "evil":
        ##              Aligns you to undead and turns undead/priest alignment switching on
                        if value is True:
                                evilmode = True
                                secondalign = "undead"
                                alignlevel = 0
                                self.usecommand(irc, "align undead")
                                irc.reply("Evil Mode On.  To turn it back off use 'setoption evil false' command", private=True)
        ##              Turns Evil Mode off
                        if value is False:
                                evilmode = False
                                secondalign = "human"
                                alignlevel = setalign
                                if(alignlevel > level):
                                        self.usecommand(irc, "align {0}".format(firstalign))
                                if(alignlevel <= level):
                                        self.usecommand(irc, "align {0}".format(secondalign))
                                irc.reply("Evil Mode Off.  To turn it back on use 'setoption evil true' command", private=True)
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
                if text == "intervaltext":
        ##              Turns Interval Messages on
                        if value is True:
                                intervaltextmode = True
                                irc.reply("Interval Text Mode On.  To turn it back off use 'setoption intervaltext false' command", private=True)
        ##              Turns Interval Messages off
                        if value is False:
                                intervaltextmode = False
                                irc.reply("Interval Text Mode Off.  To turn it back on use 'setoption intervaltext true' command", private=True)
                if text == "noticetext":
        ##              Turns Notices from GameBot on
                        if value is True:
                                noticetextmode = True
                                irc.reply("Turns Notices from GameBot on.  To turn it back off use 'setoption noticetext false' command", private=True)
        ##              Turns Notices from GameBot off
                        if value is False:
                                noticetextmode = False
                                irc.reply("Turns Notices from GameBot off.  To turn it back on use 'setoption noticetext true' command", private=True)
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
        global netname
        global botdisable1
        
        botcount1 = 0
        if("undernet" in netname.lower()):
                channame = "#idlerpg"
                botname = "idlerpg"
        else:
                channame = "#multirpg"
                botname = "multirpg"

        bottest = botname
        bottest2 = "multirpg"
        botentry = []

        try:
                ops = otherIrc.state.channels[channame].ops
                halfops = otherIrc.state.channels[channame].halfops

                for user in ops:
                        if bottest in user and user != bottest:
                                botentry.append(user)
                                botname10 = user
                for user in halfops:
                        if bottest in user and user != bottest:
                                botentry.append(user)
                                botname10 = user
                if("undernet" in netname.lower()):
                        for user in ops:
                                if bottest2 in user:
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
        global customnetworksettings
        global botdisable1
        
        if customnetworksettings is False:
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
        global playbotsingle
        global playbotmulti

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

        if quakemultion is True:
                quakemulti = conf.supybot.plugins.QuakenetPlayBotMulti()
                if quakemulti is True:
                        playbotcount += 1

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
                        pbcount += 1
        if playbotmultion is True:
                playbotmulti = conf.supybot.plugins.PlayBotMulti()       
                if playbotmulti is True:
                        playbotcount += 1
                        pbcount += 1

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
        global netname
        global channame
        global botname
        global charcount
        global rawstatsmode
        global rawstatsswitch
        global nickname
        global gameactive
        global otherIrc
        global supynick
        global customnetworksettings
        global custombotname
        global customchanname
        global Owner
        global pbcount
        global networklist

        charcount += 1

        if charcount == 1:
                gameactive = True
                netcheck = True
                nickname = msg.nick
                netname = self._getIrcName(irc)
                supynick = irc.nick
                Owner = irc.getCallback('Owner')

                if customnetworksettings is False:
                        netcheck = False
                        for entry in networklist:
                                if entry[0].lower() in netname.lower():
                                        netcheck = True
                        netlist = []
                        if netcheck is False:
                                for entry in networklist:
                                        if entry[3] == 1:
                                                netlist.append( ( entry[0] ) )
                                irc.error("Networks supported: {0}".format(netlist))
                                irc.error("Current Network: {0}.  The network name needs to have one of the above names in it".format(netname))

                        if("undernet" in netname.lower()):
                                channame = "#idlerpg"
                                botname = "idlerpg"
                        else:
                                channame = "#multirpg"
                                botname = "multirpg"

                if customnetworksettings is True:
                        channame = customchanname
                        botname = custombotname
                otherIrc = self._getIrc(netname)

                self.playbotcheck(irc)
                args2 = arg2.split(" ")

                try:
                        if(name is None or pswd is None):
                                name = args2[0]
                                pswd = args2[1]
                except IndexError:
                        irc.error("To log in use <bot> playbotsingle login CharName Password" )
                        
                if(name is None or pswd is None or netcheck is False):
                        charcount = 0

                if charcount == 1:
                        if pbcount == 2:
                                multiplayerlist = self.multiread(irc)
                                count = 0
                                multiname = None
                                multiname2 = None
                                multiname3 = None
                                multiname4 = None
                                multiname5 = None
                                multinetname = None
                                multinetname2 = None
                                multinetname3 = None
                                multinetname4 = None
                                multinetname5 = None
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
                                        if count == 5:
                                                multiname5 = entry[1]
                                                multinetname5 = entry[3]
                                if(name == multiname or name == multiname2 or name == multiname3 or name == multiname4 or name == multiname5):
                                        irc.error("Character {0} is already logged in on PlayBotMulti".format(name))
                                        charcount = 0
                                if(netname == multinetname):
                                        irc.error("Character {0} is already logged in on PlayBotMulti".format(multiname))
                                        charcount = 0
                                if(netname == multinetname2):
                                        irc.error("Character {0} is already logged in on PlayBotMulti".format(multiname2))
                                        charcount = 0
                                if(netname == multinetname3):
                                        irc.error("Character {0} is already logged in on PlayBotMulti".format(multiname3))
                                        charcount = 0
                                if(netname == multinetname4):
                                        irc.error("Character {0} is already logged in on PlayBotMulti".format(multiname4))
                                        charcount = 0
                                if(netname == multinetname5):
                                        irc.error("Character {0} is already logged in on PlayBotMulti".format(multiname5))
                                        charcount = 0
                                        
                if charcount == 0:
                        gameactive = False
                        name = None
                        pswd = None
                        return

                if charcount == 1:
                        if rawstatsmode is True or rawstatsswitch is True:
                                self.bootopcheck(irc)

                        if(name != None and pswd != None):
                                self.loginstart(irc)

        if charcount >= 2:
            irc.error("You can only play with 1 character.  You are already logged in as {0}".format(name))
            charcount = 1

    login = wrap(login, [("checkCapability", "admin"), "text"])

    def loginstart(self, irc):
        global name
        global pswd
        global upgradeall
        global betmoney
        global itemupgrader
        global setalign
        global setbuy
        global sethero
        global setengineer
        global singlefight
        global evilmode
        global rawstatsmode
        global newlist
        global levelrank1
        global rawstatsswitch
        global webworks
        global bottextmode
        global errortextmode
        global intervaltextmode
        global noticetextmode
        global pmtextmode
        global autostartmode
        global loginsettingslister

        self.usecommand(irc, "login {0} {1}".format(name, pswd))
        time.sleep(3) # Needed
        self.usecommand(irc, "whoami")
        self.usecommand(irc, "stats")
        self.reply(irc, "Player Character {0} has logged in".format(name))                
        
        if loginsettingslister is True:
                if autostartmode is True:
                        self.reply(irc, "Autostart Mode Activated.  To turn it off use 'setoption autostart false' command")
                if bottextmode is True:
                        self.reply(irc, "Bot Text Mode Activated.  To turn it off use 'setoption bottext false' command")
                if errortextmode is True:
                        self.reply(irc, "Error Text Mode Activated.  To turn it off use 'setoption errortext false' command")
                if evilmode is True:
                        self.reply(irc, "Evil Mode Activated.  To turn it off use 'setoption evil false' command")
                if intervaltextmode is True:
                        self.reply(irc, "Interval Text Mode Activated.  To turn it off use 'setoption intervaltext false' command")
                if itemupgrader is True:
                        self.reply(irc, "Item Upgrader Mode Activated.  To turn it off use 'setoption itemupgrader false' command")
                if noticetextmode is True:
                        self.reply(irc, "Notices from GameBot Mode Activated.  To turn it off use 'setoption noticetext false' command")
                if pmtextmode is True:
                        self.reply(irc, "PMs from GameBot Mode Activated.  To turn it off use 'setoption pmtext false' command")
                if rawstatsmode is True:
                    self.reply(irc, "Rawstats Mode Activated.  To use Rawplayers Mode use 'setoption rawplayers true' command")
                if rawstatsmode is False:
                    self.reply(irc, "Rawplayers Mode Activated.  To use Rawstats Mode use 'setoption rawstats true' command")
                if singlefight is True:
                        self.reply(irc, "Single Fight Mode Activated.  To use multiple fight mode use 'setoption singlefight false' command")
                if singlefight is False:
                        self.reply(irc, "Multiple Fight Mode Activated.  To use single fight mode use 'setoption singlefight true' command")
                if upgradeall is True:
                        self.reply(irc, "Upgrade All 1 Mode Activated.  To turn it off use 'setoption upgradeall false' command")
                self.reply(irc, "Current Align Level: {0}.  If you want to change it use 'setoption alignlevel number' command".format(setalign))
                self.reply(irc, "Current Betmoney: {0}.  If you want to change it use 'setoption betmoney number' command".format(betmoney))
                self.reply(irc, "Current Engineer Buy Level: {0}.  If you want to change it use 'setoption engineerbuy number' command".format(setengineer))
                self.reply(irc, "Current Hero Buy Item Score: {0}.  If you want to change it use 'setoption herobuy number' command".format(sethero))
                self.reply(irc, "Current Item Buy Level: {0}.  If you want to change it use 'setoption itembuy number' command".format(setbuy))
                self.reply(irc, " ")
                self.reply(irc, "For a list of PlayBot commands use <bot> playbotsingle help")
                self.reply(irc, " ")
        self.versionchecker(irc)
        self.configcheck(irc)
        self.singlewrite(irc)
        if rawstatsswitch is True or rawstatsmode is True:
            self.webdata(irc)
            if webworks is True:
                self.newlister()
                if newlist != None:
                        for entry in newlist:
                            if(entry[5] == 1):
                                levelrank1 = entry[3]

        self.main(irc)
        if rawstatsmode is True:
                self.looper(irc)

    def bootopcheck(self, irc):
        global channame
        global botname
        global rawstatsmode
        global rawstatsswitch
        global otherIrc
                
        opcheck = False
        chancheck = False
        
        chantest = otherIrc.state.channels
        for entry in chantest:
                if entry == channame:
                    chancheck = True

        if chancheck is True:
                try:
                        ops = otherIrc.state.channels[channame].ops
                        halfops = otherIrc.state.channels[channame].halfops
                        for user in ops:
                            if botname == user:
                                opcheck = True
                        for user in halfops:
                            if botname == user:
                                opcheck = True
                except KeyError:
                        self.reply(irc, "Key Error")
                if opcheck is False:
                        rawstatsmode = False
                        rawstatsswitch = False
                        self.reply(irc, playbottext + " - GameBot Not Opped Changing to RawPlayers")
                        self.configwrite()

    def autostart(self, irc):
        global name
        global pswd
        global netname
        global channame
        global botname
        global charcount
        global rawstatsmode
        global rawstatsswitch
        global nickname
        global gameactive
        global otherIrc
        global supynick
        global customnetworksettings
        global custombotname
        global customchanname
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
                def bootloopps():
                    self.autostart(irc)
                delayTime = time.time() + 60
                
                try:
                        schedule.addEvent(bootloopps, delayTime, "bootloopps")
                except AssertionError:
                        schedule.removeEvent('bootloopps')
                        schedule.addEvent(bootloopps, delayTime, "bootloopps")
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
                if customnetworksettings is False:
                        if("undernet" in netname.lower()):
                                channame = "#idlerpg"
                                botname = "idlerpg"
                        else:
                                channame = "#multirpg"
                                botname = "multirpg"

                if customnetworksettings is True:
                        channame = customchanname
                        botname = custombotname
                otherIrc = self._getIrc(netname)
                        
                if rawstatsmode is True or rawstatsswitch is True:
                        self.bootopcheck(irc)

                if(name != None and pswd != None):
                        self.loginstart(irc)
                        self.singlewrite(irc)

    def logoutchar(self, irc, msg, args):
        """takes no arguments

        Logs you out of the PlayBot.
        """
        global charcount
        global netname
        global channame
        global botname
        global name
        global pswd
        global gameactive
        global myentry
        global rawmyentry
        global ttlfrozen
        global autostartmode
        
        if gameactive is False:
            irc.error("You are not logged in")
        if gameactive is True:
                irc.reply("{0} has logged out".format(name), private=True)
                charcount = 0
                netname = None
                channame = None
                botname = None
                name = None
                pswd = None
                myentry = None
                rawmyentry = None
                ttlfrozen = 0        
                gameactive = False
                self.singleeraser(irc)
                if autostartmode is True:
                    autostartmode = False
                    self.configwrite()
                try:
                    schedule.removeEvent('loopps')
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

    def playerslist(self, irc, msg, args):
        """takes no arguments

        Lists players on all MultiRPG plugins loaded
        """

        global playbotsingle
        global playbotmulti

        self.playbotcheck(irc)

        if playbotsingle is True:
                psfileprefix3 = "playbotsingleplayers.txt"
                path = conf.supybot.directories.data
                psfilename3 = path.dirize(psfileprefix3)
                pscheck = True
                try:
                        f = open(psfilename3,"rb")
                        playerListS = pickle.load(f)
                        f.close()
                except:
                        playerListS = []
                try:
                        psinglename = playerListS[0][1]
                        psinglenetname = playerListS[0][3]
                except IndexError:
                        irc.reply("No Players Logged in on PlayBotSingle", private=True)
                        irc.reply(" ", private=True)
                        irc.reply(" ", private=True)
                        pscheck = False
                if pscheck is True:
                        irc.reply("MultiRPG PlayBot Single", private=True)
                        irc.reply(" ", private=True)
                        irc.reply("Player Character - {0}.  Network {1}".format(psinglename, psinglenetname), private=True)
                        irc.reply(" ", private=True)
                        irc.reply(" ", private=True)

        if playbotmulti is True:
                pmfileprefix4 = "playbotmultiplayers.txt"
                path = conf.supybot.directories.data
                pmfilename4 = path.dirize(pmfileprefix4)
                pmcheck = False
                try:
                        f = open(pmfilename4,"rb")
                        playerListM = pickle.load(f)
                        f.close()
                except:
                        playerListM = []
                count = 0
                pmultiname = None
                pmultiname2 = None
                pmultiname3 = None
                pmultiname4 = None
                pmultiname5 = None
                pmultinetname = None
                pmultinetname2 = None
                pmultinetname3 = None
                pmultinetname4 = None
                pmultinetname5 = None
                for entry in playerListM:
                        count += 1
                        if count == 1:
                                pmultiname = entry[1]
                                pmultinetname = entry[3]
                                pmcheck = True
                        if count == 2:
                                pmultiname2 = entry[1]
                                pmultinetname2 = entry[3]
                        if count == 3:
                                pmultiname3 = entry[1]
                                pmultinetname3 = entry[3]
                        if count == 4:
                                pmultiname4 = entry[1]
                                pmultinetname4 = entry[3]
                        if count == 5:
                                pmultiname5 = entry[1]
                                pmultinetname5 = entry[3]
                if pmcheck is False:
                        irc.reply("No Players Logged in on PlayBotMulti", private=True)
                if pmcheck is True:
                        irc.reply("MultiRPG PlayBot Multi", private=True)
                        irc.reply(" ", private=True)
                        irc.reply("Player Character 1 - {0}.  Network {1}    Player Character 2 - {2}.  Network {3}".format(pmultiname, pmultinetname, pmultiname2, pmultinetname2), private=True)
                        irc.reply("Player Character 3 - {0}.  Network {1}    Player Character 4 - {2}.  Network {3}".format(pmultiname3, pmultinetname3, pmultiname4, pmultinetname4), private=True)
                        irc.reply("Player Character 5 - {0}.  Network {1}".format(pmultiname5, pmultinetname5), private=True)

    playerslist = wrap(playerslist, [("checkCapability", "admin")])
        
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
        irc.reply("MultiRPG PlayerListS Erased", private=True)

    def psingleerase(self, irc, msg, args):
        """takes no arguments

        Erases playerList file
        """
        self.singleeraser(irc)

    psingleerase = wrap(psingleerase, [("checkCapability", "admin")])

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

    def jump(self, irc, msg, args, network):
        """<network>

        Jump to another network
        """
        global gameactive
        global netname
        global otherIrc
        global nolag
        global servername
        global port
        global ssl
        global networkname
        global networklist
        global Owner
        global jumpnetwork
        global customnetworksettings
        global ZNC
        global bothostmask
        global connectfail
        global autostartmode
        global pbcount
        
        if(pbcount == 2 and gameactive is True):
                irc.error("Jump command disabled as both Playbot Single and Multi loaded")

        if(pbcount == 1 and gameactive is True):
                networklistcheck = False
                netcheck = True
                servererror = False
                network = network.lower()
                try:
                    checkotherIrc = self._getIrc(network)
                    serverPort = conf.supybot.networks.get(network).servers()[0]
                    if checkotherIrc.server == "unset":
                            servererror = True
                except IndexError:
                    irc.error("To do jump command use jump network")
                except NameError:
                    irc.error("Network not connected to supybot")
                    netcheck = False

                if ZNC is False and customnetworksettings is False:
                            for entry in networklist:
                                        if (network == entry[0].lower() and entry[3] == 1):
                                            servername = entry[1]
                                            nolag = entry[2]
                                            port = entry[4]
                                            ssl = entry[5]
                                            bothostmask = entry[6]
                                            networklistcheck = True                                

                            if netcheck is True:
                                    if servererror is False:
                                            netchange = False
                                            if netname.lower() != network:
                                                    netname = network
                                                    irc.reply("Network Changed to {0}".format(netname), private=True)
                                                    otherIrc = checkotherIrc
                                                    networkname = network
                                                    networklistcheck = True                                
                                                    jumpnetwork = True
                                                    netchange = True
                                                    connectfail = 0
                                                    if autostartmode is True:
                                                            self.configwrite2()
                                            if netname.lower() == network and netchange is False:
                                                    irc.error("You are already playing on {0}".format(netname))
                                    if servererror is True:
                                            irc.error("Server Error, Network not connected")
                            if netcheck is False and networklistcheck is True:
                                serverPort = (servername, port)
                                newIrc = Owner._connect(network, serverPort=serverPort,
                                                        password="", ssl=ssl)
                                conf.supybot.networks().add(network)
                                assert newIrc.callbacks is irc.callbacks, 'callbacks list is different'
                                irc.replySuccess(_('Connection to %s initiated.') % network)
                                otherIrc = self._getIrc(network)
                                netname = network
                                networkname = network
                                jumpnetwork = True
                                if autostartmode is True:
                                    self.configwrite2()
                if ZNC is True or customnetworksettings is True:
                            irc.error("ZNC or Custom Network Settings are on")
                if networklistcheck is False:
                    irc.error("Network not on the list")
                    
        if gameactive is False:
            irc.error("You are not logged in")

    jump = wrap(jump, [("checkCapability", "admin"), "something"])

    def configcheck(self, irc):
        global channame
        global autoconfig

        pingtime = conf.supybot.protocols.irc.ping.interval()
        commandflood = conf.supybot.abuse.flood.command()
        notcommandflood = conf.supybot.abuse.flood.command.invalid()
        addressed = conf.supybot.reply.whenAddressedBy.chars()
        inprivate = conf.supybot.reply.error.inPrivate()
        inprivate2 = conf.supybot.reply.inPrivate()
        addressed2 = conf.supybot.reply.whenAddressedBy.nick()
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

                if addressed == "":
                        conf.supybot.reply.whenAddressedBy.chars.set("!")
                        configchange = True
                if inprivate is True:
                        conf.supybot.reply.error.inPrivate.set("False")
                        configchange = True
                if inprivate2 is True:
                        conf.supybot.reply.inPrivate.set("False")
                        configchange = True
                if addressed2 is False:
                        conf.supybot.reply.whenAddressedBy.nick.set("True")
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
            irc.reply("Autostart Mode Off          - setoption autostart false", private=True)
            irc.reply("Autostart Mode On           - setoption autostart true", private=True)
            irc.reply("Best Bet/Fight/Creep/Slay   - bestall", private=True)
            irc.reply("Bot Text Mode Off           - setoption bottext false", private=True)
            irc.reply("Bot Text Mode On            - setoption bottext true", private=True)
            irc.reply("Erase Config File           - eraseconfig", private=True)
            irc.reply("Erase PlayerList            - psingleerase", private=True)
            irc.reply("Error Text Mode Off         - setoption errortext false", private=True)
            irc.reply("Error Text Mode On          - setoption errortext true", private=True)
            irc.reply("Evil Mode Off               - setoption evil false", private=True)
            irc.reply("Evil Mode On                - setoption evil true", private=True)
            irc.reply("Fix Looper                  - fixlooper", private=True)
            irc.reply("GameBot Notices Mode Off    - setoption noticetext false", private=True)
            irc.reply("GameBot Notices Mode On     - setoption noticetext true", private=True)
            irc.reply("GameBot PMs Mode Off        - setoption pmtext false", private=True)
            irc.reply("GameBot PMs Mode On         - setoption pmtext true", private=True)
            irc.reply("Interval Text Mode Off      - setoption intervaltext false", private=True)
            irc.reply("Interval Text Mode On       - setoption intervaltext true", private=True)
            irc.reply("Item Upgrader Mode Off      - setoption itemupgrader false", private=True)
            irc.reply("Item Upgrader Mode On       - setoption itemupgrader true", private=True)
            irc.reply("Jump Network                - jump network", private=True)
            irc.reply("Log In Char                 - login charname password", private=True)
            irc.reply("Log Out Char                - logoutchar", private=True)
            irc.reply("Log Out Game                - logoutgame", private=True)
            irc.reply("Manual Command              - cmd command", private=True)
            irc.reply("Multiple Fight Mode         - setoption singlefight false", private=True)
            irc.reply("PlayBot Commands List       - help", private=True)
            irc.reply("Player's Items              - items", private=True)
            irc.reply("Player's Status             - status", private=True)
            irc.reply("Players List                - playerslist", private=True)
            irc.reply("Rawplayers Mode On          - setoption rawplayers true", private=True)
            irc.reply("Rawstats Mode On            - setoption rawstats true", private=True)
            irc.reply("Set Align Level             - setoption alignlevel number", private=True)
            irc.reply("Set BetMoney                - setoption betmoney number", private=True)
            irc.reply("Set Engineer Buy Level      - setoption engineerbuy number", private=True)
            irc.reply("Set Hero Buy ItemScore      - setoption herobuy number", private=True)
            irc.reply("Set Item Buy Level          - setoption itembuy number", private=True)
            irc.reply("Set Option                  - setoption command value", private=True)
            irc.reply("Settings List               - settings", private=True)
            irc.reply("Single Fight Mode           - setoption singlefight true", private=True)
            irc.reply("Update Nick                 - updatenick", private=True)
            irc.reply("Upgrade All 1 Mode Off      - setoption upgradeall false", private=True)
            irc.reply("Upgrade All 1 Mode On       - setoption upgradeall true", private=True)
            irc.reply("Version Checker             - versioncheck", private=True)
            irc.reply(" ", private=True)
            irc.reply("If you want more information about a command use <bot> help playbotsingle <command> - ie /msg DudeRuss help playbotsingle settings", private=True)

    help = wrap(help)

    def settings(self, irc, msg, args):
            """takes no arguments

            Gives a list of settings which you can change
            """
            global itemupgrader
            global upgradeall
            global singlefight
            global setalign
            global setbuy
            global betmoney
            global sethero
            global setengineer
            global evilmode
            global name
            global rawstatsmode
            global gameactive
            global bottextmode
            global errortextmode
            global intervaltextmode
            global noticetextmode
            global pmtextmode
            global autostartmode
            global netname

            if gameactive is True:
                irc.reply("Playbot Settings List", private=True)
                irc.reply(" ", private=True)
                irc.reply("Align Level - {0}          Autostart Mode - {1}".format(setalign, autostartmode), private=True)
                irc.reply("Bet Money - {0}            Bot Text Mode - {1}".format(betmoney, bottextmode), private=True)
                irc.reply("Engineer Buy Level - {0}   Error Text Mode - {1}".format(setengineer, errortextmode), private=True)
                irc.reply("Evil Mode - {0}            GameBot Notices Mode - {1}".format(evilmode, noticetextmode), private=True)
                irc.reply("GameBot PMs Mode - {0}     Hero Buy ItemScore - {1}".format(pmtextmode, sethero), private=True)
                irc.reply("Interval Text Mode - {0}   Item Buy Level - {1}".format(intervaltextmode, setbuy), private=True)
                irc.reply("Item Upgrader Mode - {0}   Player Character - {1}.  Network {2}".format(itemupgrader, name, netname), private=True)
                if rawstatsmode is True:
                        irc.reply("Rawstats Mode - True", private=True)
                if rawstatsmode is False:
                        irc.reply("Rawplayers Mode - True", private=True)
                irc.reply("Single Fight Mode - {0}    Upgrade All 1 Mode - {1}".format(singlefight, upgradeall), private=True)
            if gameactive is False:
                irc.error("You are not logged in")

    settings = wrap(settings, [("checkCapability", "admin")])

    def status(self, irc, msg, args):
            """takes no arguments

            Gives a list of character stats
            """
            global rawstatsmode
            global charcount
            global myentry
            global name
            global webworks
            
            global rankplace
            global level
            global team
            global ttl
            global atime
            global ctime
            global stime
            global mysum

            global powerpots
            global fights
            global bets
            global hero
            global hlvl
            global eng
            global elvl
            global gold
            global bank
            global gameactive

            if gameactive is True:
                if rawstatsmode is True and webworks is True:
                        ranknumber = myentry[1]
                if rawstatsmode is False:
                        ranknumber = rankplace
                irc.reply("{0}'s Status".format(name), private=True)
                irc.reply(" ", private=True)
                if webworks is True:
                        irc.reply("Rank: {0}".format(ranknumber), private=True)
                irc.reply("Level: {0}     TTL: {1} secs     Item Score: {2}     Team No: {3}".format(level, ttl, mysum, team), private=True)
                if(level >= 10):
                        irc.reply("Attack Recovery: {0} secs".format(atime), private=True)
                if(level < 10):
                        irc.reply("Creep Attacks Start at Level 10", private=True)
                if(level >= 35):
                        irc.reply("Challenge Recovery: {0} secs".format(ctime), private=True)
                if(level < 35):
                        irc.reply("Manual Challenges Start at Level 35", private=True)
                if(level >= 40):
                        irc.reply("Slay Recovery: {0} secs".format(stime), private=True)
                if(level < 40):
                        irc.reply("Slaying Monsters Start at Level 40", private=True)
                irc.reply("Power Potions: {0}".format(powerpots), private=True)
                if(level >= 10):
                        irc.reply("Fights: {0} of 5".format(fights), private=True)
                if(level < 10):
                        irc.reply("Fights Start at Level 10", private=True)
                if(level >= 30):
                        irc.reply("Bets: {0} of 5".format(bets), private=True)
                if(level < 30):
                        irc.reply("Bets Start at Level 30", private=True)
                if hero == 0:
                        irc.reply("Hero: No", private=True)
                if hero == 1:
                        irc.reply("Hero: Yes", private=True)
                irc.reply("Hero Level: {0}      Engineer Level: {1}".format(hlvl, elvl), private=True)
                if eng == 0:
                        irc.reply("Engineer: No", private=True)
                if eng == 1:
                        irc.reply("Engineer: Yes", private=True)
                irc.reply("Gold in Hand: {0}    Gold in the Bank: {1}".format(gold, bank), private=True)
            if gameactive is False:
                irc.error("You are not logged in")

    status = wrap(status, [("checkCapability", "admin")])

    def items(self, irc, msg, args):
            """takes no arguments

            Gives a list of character item scores
            """
            global name
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
            global gameactive

            if gameactive is True:
                irc.reply("{0}'s Items List".format(name), private=True)
                irc.reply(" ", private=True)
                irc.reply("Amulet: {0}  Charm: {1}  Helm: {2}  Boots: {3}  Gloves: {4}".format(amulet, charm, helm, boots, gloves), private=True)
                irc.reply("Ring: {0}  Leggings: {1}  Shield: {2}  Tunic: {3}  Weapon: {4}".format(ring, leggings, shield, tunic, weapon), private=True)
                irc.reply("Total Item Score: {0}".format(mysum), private=True)
            if gameactive is False:
                irc.error("You are not logged in")

    items = wrap(items, [("checkCapability", "admin")])

    def bestall(self, irc, msg, args):
        """takes no arguments

        Shows Best Bet/Fight/Attack/Slay
        """
        global gameactive
        global fightSum
        global rankplace
        global name
        global myentry
        global rawstatsmode
        global webworks
        global level
        
        if gameactive is True:
                self.webdata(irc)
                if webworks is True:
                        if rawstatsmode is True and webworks is True:
                                ranknumber = myentry[1]
                        if rawstatsmode is False:
                                ranknumber = rankplace
                        self.getvariables()
                        self.newlister()
                        irc.reply("Best All for {0}".format(name), private=True)
                        irc.reply(" ", private=True)
                        if(level < 10):
                                irc.reply("Creep Attacks Start at Level 10", private=True)
                        if(level >= 10):
                                creep = self.bestattack()
                                irc.reply("BestAttack: {0}".format(creep), private=True)
                        if(level < 40):
                                irc.reply("Slaying Monsters Start at Level 40", private=True)
                        if(level >= 40):
                                monster = self.bestslay()
                                irc.reply("BestSlay: {0}".format(monster), private=True)
                        if(level < 30):
                                irc.reply("Bets Start at Level 30", private=True)
                        if(level >= 30):
                                bbet = self.bestbet()
                                irc.reply("BestBet {0} {1}".format( bbet[0][0], bbet[1][0] ), private=True)
                        if(level < 10):
                                irc.reply("Fights Start at Level 10", private=True)
                        if(level >= 10):
                                ufight = self.testfight()
                                try:
                                        ufightcalc = fightSum / ufight[2]
                                except ZeroDivisionError:
                                        ufightcalc = 0
                                irc.reply("Best Fight for Rank {0}: {1} [{2}]  Opponent: Rank {3}: {4} [{5}], Odds {6}".format(ranknumber, name, int(fightSum), ufight[5], ufight[0], int(ufight[2]), ufightcalc), private=True)
        if gameactive is False:
                irc.error("You are not logged in")

    bestall = wrap(bestall, [("checkCapability", "admin")])

    def webdata(self, irc):
            global playerlist
            global name
            global webworks
            global myentry
            global rawplayers3
            global webfail
            global python3
            global botcheck
            global errortextmode
            global multirpgweb
            global idlerpgweb
            global webnum
            global playbottext
            
            webworks = True
            weberror = False

            if webnum == 1:
                website = "multirpg.net"
                websites = multirpgweb
            if webnum == 2:
                website = "idlerpg.org"
                websites = idlerpgweb
            # get raw player data from web, parse for relevant entry
            try:
                if python3 is True:
                        text = urllib.request.urlopen(websites + "rawplayers3.php")
                if python3 is False:
                        text = urllib2.urlopen(websites + "rawplayers3.php")
                rawplayers3 = text.read()
                text.close()
                if python3 is True:
                        rawplayers3 = rawplayers3.decode("UTF-8")
            except:
                weberror = True

            if weberror is True:
                if errortextmode is True:
                        self.reply(irc, playbottext + " - Could not access {0}".format(website))
                webworks = False

            # build list for player records
            if(rawplayers3 is None):
                    if errortextmode is True:
                            self.reply(irc, playbottext + " - Could not access {0}, unknown error.".format(website) )
                    webworks = False
            else:
                    playerlist = rawplayers3.split("\n")
                    playerlist = playerlist[:-1]

            # extract our player's record and make list
            if webworks is True:
                    for entry in playerlist:
                            entry = entry.split(" ")
                            try:
                                    if(entry[3] == name):
                                            myentry = entry
                                            webfail = 0
                            except IndexError:
                                    webworks = False
            if webworks is False:
                if botcheck is True:
                        webfail += 1
                        webnum += 1
            if webfail >= 1 and botcheck is True:
                if errortextmode is True:
                        self.reply(irc, playbottext + " - Webfail: {0}".format(webfail))
            if webnum > 2:
                webnum = 1

    def newlister(self):
            global newlist
            global team
            global playerlist
            global firstalign
            global name
            global webworks

            newlist = []
            
            if webworks is True:
                    for player in playerlist:
                            player = player.split(" ")
                            # extract players sum
                            sumIdx = None
                            levelIdx = None
                            alignIdx = None
                            heroIdx = None
                            hlevelIdx = None
                            teamIdx = None
                            rankIdx = None
                            for index, entry in enumerate(player):
                                    if(entry == "sum"):
                                            sumIdx = index + 1
                                    if(entry == "level"):
                                            levelIdx = index + 1
                                    if(entry == "align"):
                                            alignIdx = index + 1
                                    if(entry == "hero"):
                                            heroIdx = index + 1
                                    if(entry == "hlevel"):
                                            hlevelIdx = index + 1
                                    if(entry == "team"):
                                            teamIdx = index + 1
                                    if(entry == "rank"):
                                            rankIdx = index + 1
                            # if this player is online
                            if(player[15] == "1"):
                                    adjSum = None
                                    sum_ = float(player[sumIdx])
                                    adj = sum_ * 0.1
                                    align = player[alignIdx]
                                    level_ = int(player[levelIdx])
                                    hero = int(player[heroIdx])
                                    hlevel = int(player[hlevelIdx])
                                    teamgroup = int(player[teamIdx])
                                    rank = int(player[rankIdx])
                                    # adjust sum for alignment and hero
                                    if(align == "g"):
                                            adjSum = sum_ + adj
                                    elif(align == "e"):
                                            adjSum = sum_ - adj
                                    elif(align == "n"):
                                            adjSum = sum_
                                    if(hero == 1):
                                            hadj = adjSum * ((hlevel + 2) /100.0)
                                            adjSum += hadj
                                    if(teamgroup >= 1):
                                            if(team == teamgroup):
                                                    adjSum += 50000
                                    if(player[3] == name):
                                            if(firstalign == "priest"):
                                                    adjSum = sum_ + adj
                                                    if(hero == 1):
                                                            hadj = adjSum * ((hlevel + 2) /100.0)
                                                            adjSum += hadj

                                                    # name       sum   adjust  level   align  rank  team
                                    newlist.append( ( player[3], sum_, adjSum, level_, align, rank, teamgroup ) )

                    # put list in proper order to easily figure bests

                    newlist.sort( key=operator.itemgetter(1), reverse=True )
                    newlist.sort( key=operator.itemgetter(3) )

    def networklists(self, irc):
            global networkname
            global servername
            global ssl
            global port
            global myentry
            global nolag
            global servernum
            global connectfail
            global connectretry
            global customnetworksettings
            global customservername
            global customservername2
            global customport
            global customssl
            global customnolag
            global custombosthostmask
            global networklist
            global jumpnetwork
            global ZNC
            global ZNCnolag
            global ZNCServer
            global ZNCPort
            global ZNCssl
            global bothostmask
            global networkreconnect
            global networklist
            
            maxservers = 2 # Change if you are using more than 2 servers per network in the networklist

            if networkname is None:
                    try:
                            networkname = myentry[5]
                    except TypeError:
                            networkname = None
            try:
                        networknamecheck = myentry[5]
            except TypeError:
                        networknamecheck = None
            if(networknamecheck != networkname and networknamecheck != None and jumpnetwork is False):
                        try:
                                networkname = myentry[5]
                        except TypeError:
                                networkname = None

            if(connectfail < connectretry):
                    for entry in networklist:
                            if(networkname == entry[0] and servernum == entry[3]):
                                    servername = entry[1]
                                    nolag = entry[2]
                                    port = entry[4]
                                    ssl = entry[5]
                                    bothostmask = entry[6]

            if(connectfail >= connectretry):
                connectfail = 0
                servernum += 1
                if(servernum > maxservers):
                    servernum = 1
                if(ZNC is False and customnetworksettings is False and networkreconnect is True):
                        for entry in networklist:
                                if(networkname == entry[0] and servernum == entry[3]):
                                            servername = entry[1]
                                            nolag = entry[2]
                                            port = entry[4]
                                            ssl = entry[5]
                                            bothostmask = entry[6]
                                            network = otherIrc.network
                                            group = conf.supybot.networks.get(network)
                                            serverPort = ("{0}:{1}".format(servername, port))
                                            group.servers.set(serverPort)
                                            world.flush()
            if customnetworksettings is True:
                if servernum == 1:
                    servername = customservername
                    nolag = customnolag
                    port = customport
                    ssl = customssl
                    bothostmask = custombosthostmask
                if servernum == 2:
                    servername = customservername2
                    nolag = customnolag
                    port = customport
                    ssl = customssl
                    bothostmask = custombosthostmask
            if ZNC is True:
                servername = ZNCServer
                nolag = ZNCnolag
                port = ZNCPort
                ssl = ZNCssl

#            self.reply(irc, "NetworkName: {0}, NoLag: {1}, Server: {2}, Port: {3}, SSL: {4}".format(networkname, nolag, servername, port, ssl))

    def getvariables(self):
            global rawmyentry
            global myentry
            global rawstatsmode

            global rankplace
            global level
            global team
            global ttl
            global atime
            global ctime
            global stime
            global mysum

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

            global powerpots
            global fights
            global bets
            global hero
            global hlvl
            global eng
            global elvl
            global gold
            global bank

            if rawstatsmode is True:
                    myentrys = rawmyentry
            if rawstatsmode is False:
                    myentrys = myentry

            # get current system time UTC
            now = int( time.time() )

            # parse relevant data for all used variables

            if(myentrys != None):
                    for index, var in enumerate(myentrys):
                            i = index + 1
                            if( i >= len(myentrys) ):
                                    break
                            num = myentrys[i]
                            if str.isdigit(num):
                                    num = int( num )
                            
                            if rawstatsmode is False:
                                    if(var == "rank"):
                                            rankplace = num
                            if(var == "level"):
                                    level = num
                            elif(var == "team"):
                                    team = num
                            elif(var == "ttl"):
                                    ttl = num
                            if rawstatsmode is False:
                                    if(var == "regentm"):
                                            atime = num - now
                                    elif(var == "challengetm"):
                                            ctime = num - now
                                    elif(var == "slaytm"):
                                            stime = num - now
                            if rawstatsmode is True:
                                    if(var == "attackttl"):
                                            atime = num
                                    elif(var == "challengettl"):
                                            ctime = num
                                    elif(var == "slayttl"):
                                            stime = num

                            if(var == "sum"):
                                    mysum = num
                            elif(var == "amulet"):
                                    try:
                                            amulet = num .strip("abcdefghijklmnopqrstuvwxyz")
                                            amulet = int( amulet )
                                    except AttributeError:
                                            amulet = num
                            elif(var == "charm"):
                                    try:
                                            charm = num .strip("abcdefghijklmnopqrstuvwxyz")
                                            charm = int( charm )
                                    except AttributeError:
                                            charm = num
                            elif(var == "helm"):
                                    try:
                                            helm = num .strip("abcdefghijklmnopqrstuvwxyz")
                                            helm = int( helm )
                                    except AttributeError:
                                            helm = num
                            elif(var == "boots"):
                                    try:
                                            boots = num .strip("abcdefghijklmnopqrstuvwxyz")
                                            boots = int( boots )
                                    except AttributeError:
                                            boots = num
                            elif(var == "gloves"):
                                    try:
                                            gloves = num .strip("abcdefghijklmnopqrstuvwxyz")
                                            gloves = int( gloves )
                                    except AttributeError:
                                            gloves = num
                            elif(var == "ring"):
                                    try:
                                            ring = num .strip("abcdefghijklmnopqrstuvwxyz")
                                            ring = int( ring )
                                    except AttributeError:
                                            ring = num
                            elif(var == "leggings"):
                                    try:
                                            leggings = num .strip("abcdefghijklmnopqrstuvwxyz")
                                            leggings = int( leggings )
                                    except AttributeError:
                                            leggings = num
                            elif(var == "shield"):
                                    try:
                                            shield = num .strip("abcdefghijklmnopqrstuvwxyz")
                                            shield = int( shield )
                                    except AttributeError:
                                            shield = num
                            elif(var == "tunic"):
                                    try:
                                            tunic = num .strip("abcdefghijklmnopqrstuvwxyz")
                                            tunic = int( tunic )
                                    except AttributeError:
                                            tunic = num
                            elif(var == "weapon"):
                                    try:
                                            weapon = num .strip("abcdefghijklmnopqrstuvwxyz")
                                            weapon = int( weapon )
                                    except AttributeError:
                                            weapon = num
                            elif(var == "powerpots"):
                                    powerpots = num
                            elif(var == "fights"):
                                    fights = num
                            elif(var == "bets"):
                                    bets = num
                            elif(var == "hero"):
                                    hero = num
                            elif(var == "hlevel"):
                                    hlvl = num
                            elif(var == "engineer"):
                                    eng = num
                            elif(var == "englevel"):
                                    elvl = num
                            elif(var == "gold"):
                                    gold = num
                            elif(var == "bank"):
                                    bank = num

    def timercheck(self, irc):
            global alignlevel
            global ttl
            global interval
            global atime
            global stime
            global ctime
            global level
            global newlist
            global mysum
            global webworks
            global bottextmode
            global playbotext
            
            attl = ttl - 60
            # make sure no times are negative
            if(attl < 0):
                    attl = 0
            if(atime < 0):
                    atime = 0
            if(ctime < 0):
                    ctime = 0
            if(stime < 0):
                    stime = 0
            
            def alignlvlupgos():
                self.alignlvlup(irc)

            def lvlupgos():
                self.lvlup(irc)
            
            def challengegos():
                self.challenge(irc)

            def attackgos():
                self.attack(irc)

            def slaygos():
                self.slay(irc)
            
            challengecheck = False
            if(level >= 35):
                    leveldiff = level + 10
                    sumdiff = mysum + (mysum * 0.15)
                    challengediff = ("Doctor Who?", 999999)
                    if webworks is True and newlist != None:
                        for entry in newlist:
                                if(entry[3] <= leveldiff and entry[2] <= sumdiff):
                                        challengecheck = True
                                        challengediff = entry

            if(level >= alignlevel and attl <= interval):
                    timer = time.time() + attl
                    if bottextmode is True:
                            self.reply(irc, playbottext + " - Set align lvlup timer. Going off in {0} minutes.".format(attl // 60))
                    try:
                        schedule.addEvent(alignlvlupgos, timer, "alignlvlups")
                    except AssertionError:
                        schedule.removeEvent('alignlvlups')
                        schedule.addEvent(alignlvlupgos, timer, "alignlvlups")

            if(ttl <= interval and ttl > 0):
                    timer = time.time() + (ttl+10)
                    if bottextmode is True:
                            self.reply(irc, playbottext + " - Set lvlup timer. Going off in {0} minutes.".format(ttl // 60))
                    try:
                        schedule.addEvent(lvlupgos, timer, "lvlups")
                    except AssertionError:
                        schedule.removeEvent('lvlups')
                        schedule.addEvent(lvlupgos, timer, "lvlups")                        
            # do checks for other actions.
            if(level >= 10 and atime <= interval and atime <= ttl):
                    timer = time.time() + (atime+10)
                    if bottextmode is True:
                            self.reply(irc, playbottext + " - Set attack timer. Going off in {0} minutes.".format(atime // 60))
                    try:
                        schedule.addEvent(attackgos, timer, "attacks")
                    except AssertionError:
                        schedule.removeEvent('attacks')
                        schedule.addEvent(attackgos, timer, "attacks")                        
            if(level >= 40 and stime <= interval and stime <= ttl):
                    timer = time.time() + (stime+10)
                    if bottextmode is True:
                            self.reply(irc, playbottext + " - Set slay timer. Going off in {0} minutes.".format(stime // 60))
                    try:
                        schedule.addEvent(slaygos, timer, "slays")
                    except AssertionError:
                        schedule.removeEvent('slays')
                        schedule.addEvent(slaygos, timer, "slays")
            if challengecheck is True or webworks is False:
                    if(level >= 35 and ctime <= interval and ctime <= ttl):
                            timer = time.time() + (ctime+10)
                            if bottextmode is True:
                                    self.reply(irc, playbottext + " - Set challenge timer. Going off in {0} minutes.".format(ctime // 60))
                            try:
                                schedule.addEvent(challengegos, timer, "challenges")
                            except AssertionError:
                                schedule.removeEvent('challenges')
                                schedule.addEvent(challengegos, timer, "challenges")                        

    def spendmoney(self, irc):
            global level
            global mysum
            global gold
            global bank
            global hero
            global hlvl
            global eng
            global elvl
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
            global betmoney
            global bets
            global upgradeall
            global itemupgrader
            global sethero
            global setengineer
            global fightSum
            global firstalign
            global setbuy
            
            # decide what to spend our gold on! :D
                    
            lowestitem = self.worstitem()
#            self.reply(irc, "Worst item {0}".format(lowestitem))
            if(level >= 0):
                    try:
                            if(gold >= 41):
                                    self.usecommand(irc, "bank deposit {0}".format(gold - 40))
                                    bank += (gold - 40)
                                    gold = 40
                            elif(gold <= 20 and bank >= 20):
                                    self.usecommand(irc, "bank withdraw 20")
                                    bank -= 20
                                    gold += 20
                    except TypeError:
                            gold = 0

            if(level >= setbuy):
                    buycost = level * 6
                    buyitem = level * 2
                    buydiff = 19
                    if(bank > buycost + betmoney):
                            if(amulet < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost))
                                    self.usecommand(irc, "buy amulet {0}".format(buyitem))
                                    bank -= buycost
                                    amulet = buyitem
                    if(bank > buycost + betmoney):
                            if(charm < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost))
                                    self.usecommand(irc, "buy charm {0}".format(buyitem))
                                    bank -= buycost
                                    charm = buyitem
                    if(bank > buycost + betmoney):
                            if(helm < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost))
                                    self.usecommand(irc, "buy helm {0}".format(buyitem))
                                    bank -= buycost
                                    helm = buyitem
                    if(bank > buycost + betmoney):
                            if(boots < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost))
                                    self.usecommand(irc, "buy boots {0}".format(buyitem))
                                    bank -= buycost
                                    boots = buyitem
                    if(bank > buycost + betmoney):
                            if(gloves < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost))
                                    self.usecommand(irc, "buy gloves {0}".format(buyitem))
                                    bank -= buycost
                                    gloves = buyitem
                    if(bank > buycost + betmoney):
                            if(ring < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost))
                                    self.usecommand(irc, "buy ring {0}".format(buyitem))
                                    bank -= buycost
                                    ring = buyitem
                    if(bank > buycost + betmoney):
                            if(leggings < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost))
                                    self.usecommand(irc, "buy leggings {0}".format(buyitem))
                                    bank -= buycost
                                    leggings = buyitem
                    if(bank > buycost + betmoney):
                            if(shield < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost))
                                    self.usecommand(irc, "buy shield {0}".format(buyitem))
                                    bank -= buycost
                                    shield = buyitem
                    if(bank > buycost + betmoney):
                            if(tunic < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost))
                                    self.usecommand(irc, "buy tunic {0}".format(buyitem))
                                    bank -= buycost
                                    tunic = buyitem
                    if(bank > buycost + betmoney):
                            if(weapon < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost))
                                    self.usecommand(irc,"buy weapon {0}".format(buyitem))
                                    bank -= buycost
                                    weapon = buyitem

            if(level >= setengineer) or (level >= 15 and bank >= 2800 + betmoney):
                    if(eng == 0 and bank >= 1000):
                            self.usecommand(irc, "bank withdraw 1000")
                            self.usecommand(irc, "hire engineer")
                            bank -= 1000
                            eng = 1
                    if(eng == 1 and elvl < 9):
                            elvldiff = 9 - elvl
                            elvlcost = elvldiff * 200
                            if(bank >= elvlcost + betmoney):
                                    self.usecommand(irc, "bank withdraw {0}".format(elvlcost))
                                    for i in range(elvldiff):
                                            self.usecommand(irc, "engineer level")
                                    bank -= elvlcost
                                    elvl += elvldiff
                            elif(bank > betmoney):
                                    moneycalc = bank - betmoney
                                    upgradeengcalc = moneycalc // 200
                                    if(upgradeengcalc >= 1):
                                            engmoney = upgradeengcalc * 200
                                            self.usecommand(irc, "bank withdraw {0}".format(engmoney))
                                            for i in range(upgradeengcalc):
                                                    self.usecommand(irc, "engineer level")
                                            bank -= engmoney
                                            elvl += upgradeengcalc
            
            if(mysum >= sethero and level >= 15) or (level >= 15 and elvl == 9 and bank >= 2800 + betmoney):
                    if(hero == 0 and bank >= betmoney + 1000):
                            self.usecommand(irc, "bank withdraw 1000")
                            self.usecommand(irc, "summon hero")
                            bank -= 1000
                            hero = 1
                    if(hero == 1 and hlvl < 9):
                            hlvldiff = 9 - hlvl
                            hlvlcost = hlvldiff * 200
                            if(bank >= hlvlcost + betmoney):
                                    self.usecommand(irc, "bank withdraw {0}".format(hlvlcost))
                                    for i in range(hlvldiff):
                                            self.usecommand(irc, "hero level")
                                    bank -= hlvlcost
                                    hlvl += hlvldiff
                            elif(bank > betmoney):
                                    moneycalc = bank - betmoney
                                    upgradeherocalc = moneycalc // 200
                                    if(upgradeherocalc >= 1):
                                            heromoney = upgradeherocalc * 200
                                            self.usecommand(irc, "bank withdraw {0}".format(heromoney))
                                            for i in range(upgradeherocalc):
                                                    self.usecommand(irc, "hero level")
                                            bank -= heromoney
                                            hlvl += upgradeherocalc

            upgradeallon = False
            if(level >= 15 and level < 29 and hlvl == 9 and elvl == 9) or (bets == 5 and (hlvl < 9 or elvl < 9) or (bets == 5 and upgradeall is False and itemupgrader is False)):
                upgradeallon = True
                multi = 5
            if upgradeall is True:
                if(hlvl == 9 and elvl == 9 and bets == 5):
                        upgradeallon = True
                        multi = 1
                
            if upgradeallon is True:
                if(bank > betmoney):
                        moneycalc = bank - betmoney
                        upgradeallcalc = moneycalc // (200 * multi)
                        if(upgradeallcalc >= 1):
                                itemmoney = upgradeallcalc * (200 * multi) 
                                self.usecommand(irc, "bank withdraw {0}".format(itemmoney))
                                self.usecommand(irc, "upgrade all {0}".format(upgradeallcalc * multi))
                                bank -= itemmoney
                                amulet += upgradeallcalc * multi
                                charm += upgradeallcalc * multi
                                helm += upgradeallcalc * multi
                                boots += upgradeallcalc * multi
                                gloves += upgradeallcalc * multi
                                ring += upgradeallcalc * multi
                                leggings += upgradeallcalc * multi
                                shield += upgradeallcalc * multi
                                tunic += upgradeallcalc * multi
                                weapon += upgradeallcalc * multi


            if itemupgrader is True:
                    if(hlvl == 9 and elvl == 9 and bets == 5):
                            if(bank > betmoney):
                                    moneycalc = bank - betmoney
                                    upgradecalc = moneycalc // 20
                                    if(upgradecalc >= 1):
                                            itemmoney = upgradecalc * 20
                                            self.usecommand(irc, "bank withdraw {0}".format(itemmoney))
                                            self.itemupgrade(irc, upgradecalc)
                                            bank -= itemmoney
            NewSum = amulet + charm + helm + boots + gloves + ring + leggings + shield + tunic + weapon
            fightSum = NewSum
            if(firstalign == "priest"):
                    priestadjust = NewSum * 0.10
                    fightSum += priestadjust
            if(hero == 1):
                    heroadj = fightSum * ((hlvl + 2) /100.0)
                    fightSum += heroadj

    def alignlvlup(self, irc):
            global level
            global alignlevel
            if(level >= alignlevel):
                    self.usecommand(irc, "align priest")

    def lvlup(self, irc):
            global name
            global level
            global interval
            global webworks
            global rawstatsmode
            global rawmyentry
            global ttlfrozenmode
            global ttlfrozen
            global jumpnetwork
            global bottextmode
            global playbottext
            
            # rehook main timer for potential new interval
            self.webdata(irc)
            if webworks is True:
                    self.getvariables()
                    self.newlister()

            if rawstatsmode is False:
                    if(level < 30):
                            interval = 60
                    elif(level >= 30):
                            interval = 120
            if rawstatsmode is True:
                    interval = 60
                    jumpnetwork = False
            self.looper(irc)
            if rawstatsmode is True:
                    level += 1
            
            # fix level stat for lvlup
            if bottextmode is True:
                    self.reply(irc, playbottext + " - {0} has reached level {1}!".format(name, level))

            if(level <= 10):
                    self.usecommand(irc, "load power 0")
            if ttlfrozenmode is True:
                    ttlfrozenmode = False
                    rawstatsmode = False
                    if bottextmode is True:
                            self.reply(irc, playbottext + " - Rawplayers Mode Activated")
                    rawmyentry = None
            ttlfrozen = 0
            def challengegos():
                    self.challenge(irc)

            def attackgos():
                    self.attack(irc)

            def slaygos():
                    self.slay(irc)

            if rawstatsmode is False:
                    if(level >= 30):
                            if webworks is True:
                                    try:
                                            self.bet_bet(irc, 5)
                                    except TypeError:
                                            bets = 5
                    if(level >= 10):
                            try:
                                    schedule.addEvent(attackgos, 0, "attacks")
                            except AssertionError:
                                    schedule.removeEvent('attacks')
                                    schedule.addEvent(attackgos, 0, "attacks")                        
                    if(level >= 40):
                            try:
                                    schedule.addEvent(slaygos, 0, "slays")
                            except AssertionError:
                                    schedule.removeEvent('slays')
                                    schedule.addEvent(slaygos, 0, "slays")                 
                    if(level >= 35):
                            try:
                                    schedule.addEvent(challengegos, 0, "challenges")
                            except AssertionError:
                                    schedule.removeEvent('challenges')
                                    schedule.addEvent(challengegos, 0, "challenges")                        

    def bet_bet(self, irc, num1):
            global level
            global bank
            global bets
            
            if(level >= 30):
                    bbet = self.bestbet()
                    if(bank >= 100):
    #                       self.reply(irc, "bestbet {0} {1}".format( bbet[0][0], bbet[1][0] ))
                            self.usecommand(irc, "bank withdraw 100")
                            for i in range(num1):
                                    self.usecommand(irc, "bet {0} {1} 100".format( bbet[0][0], bbet[1][0] ))
                            bank -=100

    def fight_fight(self, irc):
            global name
            global level
            global powerpots
            global alignlevel
            global rankplace
            global fights
            global firstalign
            global secondalign
            global ufightcalc
            global fightSum
            global bets
            global singlefight
            global team
            global myentry
            global rawstatsmode
            global bottextmode
            global playbottext

            ufight = self.testfight()

            ufightcalc = fightSum / ufight[2]
            if(ufight[0] == name):
                    ufightcalc = 0.1
                    self.usecommand(irc,"bank deposit 1")
            if(team >= 1):
                    if(ufight[6] == team):
                            ufightcalc = 0.1

            if(level >= 30 and bets < 5):
                    ufightcalc = 0.1
            fightdiff = 5 - fights
            if(powerpots >= fightdiff):
                    spendpower = fightdiff
            if(powerpots < fightdiff):
                    spendpower = powerpots

            if rawstatsmode is True:
                    ranknumber = myentry[1]
            if rawstatsmode is False:
                    ranknumber = rankplace

            if(level >= 10):
                    if bottextmode is True:
                            self.reply(irc, playbottext + " - Best fight for Rank {0}: {1} [{2}]  Opponent: Rank {3}: {4} [{5}], Odds {6}".format(ranknumber, name, int(fightSum), ufight[5], ufight[0], int(ufight[2]), ufightcalc))
                    if(ufightcalc >= 0.9):
                            if(level >= 95 and powerpots >= 1):
                                    if(singlefight is True):
                                        self.usecommand(irc, "load power 1")
                                    if(singlefight is False):
                                        self.usecommand(irc, "load power {0}".format(spendpower))
                            if(level >= alignlevel):
                                    self.usecommand(irc, "align {0}".format(firstalign))
                            if(singlefight is True):
                                    self.usecommand(irc, "fight {0}".format( ufight[0] ))
                                    fights += 1
                            if(singlefight is False):
                                    for i in range(fightdiff):
                                            self.usecommand(irc, "fight {0}".format( ufight[0] ))
                                    fights += fightdiff
                            if(level >= alignlevel):
                                    self.usecommand(irc, "align {0}".format(secondalign))

    def aligncheck(self, irc):
            global name
            global newlist
            global alignlevel
            global level
            global firstalign
            global secondalign
            global evilmode
            global setalign
            global rawmyentry
            global rawstatsmode

            if evilmode is True:
                    secondalign = "undead"
                    alignlevel = 0
            if evilmode is False:
                    secondalign = "human"
                    alignlevel = setalign
            if rawstatsmode is True and rawmyentry != None:
                    if(secondalign == "human" and level >= alignlevel):
                            if(rawmyentry[19] == "g"):
                                    self.usecommand(irc, "align {0}".format(secondalign))
                            if(rawmyentry[19] == "e"):
                                    self.usecommand(irc, "align {0}".format(secondalign))

                    if(secondalign == "human" and level < alignlevel):
                            if(rawmyentry[19] == "n"):
                                    self.usecommand(irc, "align {0}".format(firstalign))
                            if(rawmyentry[19] == "e"):
                                    self.usecommand(irc, "align {0}".format(firstalign))

                    if(secondalign == "undead"):
                            if(rawmyentry[19] == "n"):
                                    self.usecommand(irc, "align {0}".format(secondalign))
                            if(rawmyentry[19] == "g"):
                                    self.usecommand(irc, "align {0}".format(secondalign))
            if rawstatsmode is False and newlist != None:
                    for entry in newlist:
                            if(name == entry[0]):
                                    if(secondalign == "human" and level >= alignlevel):
                                            if(entry[4] == "g"):
                                                    self.usecommand(irc, "align {0}".format(secondalign))
                                            if(entry[4] == "e"):
                                                    self.usecommand(irc, "align {0}".format(secondalign))
                                    if(secondalign == "human" and level < alignlevel):
                                            if(entry[4] == "n"):
                                                    self.usecommand(irc, "align {0}".format(firstalign))
                                            if(entry[4] == "e"):
                                                    self.usecommand(irc, "align {0}".format(firstalign))
                                    if(secondalign == "undead"):
                                            if(entry[4] == "n"):
                                                    self.usecommand(irc, "align {0}".format(secondalign))
                                            if(entry[4] == "g"):
                                                    self.usecommand(irc, "align {0}".format(secondalign))

    def attack(self, irc):
            global level
            global alignlevel
            global firstalign
            global secondalign
            creep = self.bestattack()
            if creep != "CreepList Error":
                    if(level >= alignlevel):
                            self.usecommand(irc, "align {0}".format(firstalign))
                    self.usecommand(irc, "attack " + creep)
                    if(level >= alignlevel):
                            self.usecommand(irc, "align {0}".format(secondalign))
            if creep == "CreepList Error":
                    self.reply(irc, "{0}".format(creep))

    def slay(self, irc):
            global level
            global alignlevel
            global firstalign
            global secondalign
            monster = self.bestslay()
            if monster != "MonsterList Error":
                    if(level >= alignlevel):
                            self.usecommand(irc, "align {0}".format(firstalign))
                    self.usecommand(irc, "slay " + monster)
                    if(level >= alignlevel):
                            self.usecommand(irc, "align {0}".format(secondalign))
            if monster == "MonsterList Error":
                    self.reply(irc, "{0}".format(monster))

    def challenge(self, irc):
            global level
            global alignlevel
            global firstalign
            global secondalign
            if(level >= alignlevel):
                    self.usecommand(irc, "align {0}".format(firstalign))
            self.usecommand(irc, "challenge")
            if(level >= alignlevel):
                    self.usecommand(irc, "align {0}".format(secondalign))

    def bestattack(self):
            global creeps
            global level
            good = "CreepList Error"
            for thing in creeps:
                    if(level <= thing[1]):
                            good = thing[0]
            return good

    def bestslay(self):
            global monsters
            global mysum
            good = "MonsterList Error"
            for thing in monsters:
                    if(mysum <= thing[1]):
                            good = thing[0]
            return good

    def bestbet(self):
            global newlist
            diff = 0
            bestbet = None
            if newlist != None:
                    for entry in newlist:
                            best = self.bestfight(entry[0], 1)
                            try:
                                    currdiff = entry[1] / best[1]
                            except ZeroDivisionError:
                                    currdiff = 0
                            if(currdiff > diff):
                                    if(entry[3] >= 30 and best[3] >= 30):
                                            diff = currdiff
                                            bestbet = ( entry, best )
            return bestbet

    def bestfight(self, name, flag):
            global newlist
            
            idx = None
            length = len(newlist)
            diff = 999999
            best = ("Doctor Who?", 999999.0, 999999.0, 0, "n", 0, 0)

            for index, entry in enumerate(newlist):
                    if(name == entry[0]):
                            idx = index + 1
                            break
            templist = newlist[idx:length]
            for entry in templist:
                    if(entry[flag] < diff):
                            diff = entry[flag]
                            best = entry
            return best

    def testfight(self):
            global newlist
            global fightSum
            global level
            global name
            
            diff = 0
            best = ("Doctor Who?", 999999.0, 999999.0, 0, "n", 0, 0)
            newlist.sort( key=operator.itemgetter(2))
            if newlist != None:
                    for entry in newlist:
                            if(entry[3] >= level and entry[0] != name):
                                    try:
                                            currdiff = fightSum / entry[2]
                                    except ZeroDivisionError:
                                            currdiff = 0
                                    if(currdiff > diff):
                                            diff = entry[2]
                                            best = entry
            return best

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

    def itemupgrade(self, irc, num1):
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

            lowestitem = self.worstitem()
            self.usecommand(irc, "upgrade {0} {1}".format(lowestitem[0], num1))
            if(lowestitem[0] == "amulet"):
                    amulet += num1
            elif(lowestitem[0] == "charm"):
                    charm += num1
            elif(lowestitem[0] == "helm"):
                    helm += num1
            elif(lowestitem[0] == "boots"):
                    boots += num1
            elif(lowestitem[0] == "gloves"):
                    gloves += num1
            elif(lowestitem[0] == "ring"):
                    ring += num1
            elif(lowestitem[0] == "leggings"):
                    leggings += num1
            elif(lowestitem[0] == "shield"):
                    shield += num1
            elif(lowestitem[0] == "tunic"):
                    tunic += num1
            elif(lowestitem[0] == "weapon"):
                    weapon += num1

    def doNotice(self, irc, msg):
        global name
        global pswd
        global botname
        global netname
        global supynick
        global gameactive
        global nickname
        global multirpgclass
        global charcount
        global noticetextmode
        global otherIrc
        global playbottext

        if gameactive is True:
            try:
                    checknet = self._getIrcName(irc)
                    checknick = irc.nick
                    chanmsgnick = msg.nick
                    (channel, text) = msg.args
            except ValueError:
                    return

            if msg.command == "NOTICE":
                if(checknick == supynick and checknet == netname):
                        if(botname == chanmsgnick):
                                if noticetextmode is True:
                                        otherIrc.queueMsg(ircmsgs.notice(nickname, playbottext + " - {0}".format(text)))
                        if(botname == chanmsgnick and "Sorry, no such account name" in text):
                                self.reply(irc, "Player {0} is Not Registered.  Creating Player".format(name))
                                self.usecommand(irc, "register {0} {1} {2}".format(name,pswd,multirpgclass))
                                return
                        if(botname == chanmsgnick and "Wrong password" in text):
                                self.reply(irc, "Wrong password")
                                charcount = 0
                                name = None
                                pswd = None
                                gameactive = False
                                return

    def inFilter(self, irc, msg):
        """Used for filtering/modifying messages as they're entering.

        ircmsgs.IrcMsg objects are immutable, so this method is expected to
        return another ircmsgs.IrcMsg object.  Obviously the same IrcMsg
        can be returned.
        """
        global botname
        global channame
        global name
        global pswd
        global rawmyentry
        global level
        global fights
        global singlefight
        global webworks
        global bets
        global rawstatsmode
        global otherIrc
        global netname
        global nickserv
        global nickservpass
        global connectfail
        global gameactive
        global interval
        global supynick
        global jumpnetwork
        global pmtextmode
        global charcount
        global remotekill
        global playbottext

        messagelist = [ ["Items: ring"],        \
                        ["Remaining Gold:"],    \
                        ["Power Potions: "],    \
                        ["You can attack again in"],            \
                        ["You can ATTACK in"],            \
                        ["You can ATTACK at"],            \
                        ["You can now ATTACK"],         \
                        ["You can only Fight"],            \
                        ["You can't buy an item more than two times your level"],            \
                        ["You changed alignment to"],  \
                        ["You have deposited"],               \
                        ["You have withdrawn"],               \
                        ["You have been invited to team"],      \
                        ["You have had your 5 FIGHTS"],               \
                        ["You haven't recovered from your last"],               \
                        ["Your Engineer"],               \
                        ["Your Hero"],              \
                        ["You don't have that much gold"],              \
                        ["You don't have enough gold"],              \
                        ["Sorry, you are already online"],  \
                        ["You already have a Hero"],        \
                        ["You already have an Engineer"],        \
                        ["It makes no sense"],                  \
                        ["BET Request Denied: Players must have the same level or higher"], \
                        ["BET Request Denied: You don't have enough gold to BET"], \
                        ["BET Request Denied: You have had your 5 BETS on this level"], \
                        ["You are too good for fighting"], \
                        ["You are not a member of a team"], \
                        ["Available commands:"],        \
                        ["Your team invitations:"],      \
                        ["To join one of them, message me"],    \
                        ["You are now the owner of team"],      \
                        ["You are the owner of team"],      \
                        ["You have just deleted your team"],    \
                        ["now has an invite for your team"],    \
                        ["Team Members:"],      \
                        ["Team invitations:"],  \
                        ["is no longer part of your team"],     \
                        ["has kicked you out of team"],         \
                        ["Congratulations, you are now on Team"],       \
                        ["You are already a member of team"],   \
                        ["You are no longer a part of team"],   \
                        ["You haven't been invited to team"],   \
                        ["Team named changed to"],      \
                        ["is already on a different team"],     \
                        ["That player doesn't exist"],          \
                        ["is no longer invited to your team"],  \
                        ["You can not kick yourself"],  \
                        ["is already on your team"],    \
                        ["already has an invite for your team"],        \
                        ["You can't dissolve your team while there are other people in it. Kick them out first"],       \
                        ["You now have"],                ]

        if gameactive is True:
            try:
                checknick = irc.nick
                checknet = self._getIrcName(irc)
                chanmsgnick = msg.nick
                (channel, text) = msg.args
            except ValueError:
                return

            if msg.command == 'PRIVMSG':
                if "IRC connection timed out" in text:
                        return
                if "Disconnected from IRC" in text:
                        return
                if "Error from server: Closing Link" in text:
                        return
                if "Connected!" in text:
                        return

                if(checknick == supynick and checknet == netname):
                        if(botname in chanmsgnick and "{0}, the level".format(name) in text and "is now online" in text):
                                connectfail = 0
                                if(nickserv is True):
                                    if("dalnet" in netname.lower()):
                                            otherIrc.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass)))
                                    else:
                                            otherIrc.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass)))
                        if botname in chanmsgnick and "fights with the legendary" in text and "removed from {0}".format(name) in text and "in a moment" in text:
                                interval = 60
                                self.looper(irc)

                if(checknick == supynick and checknet == netname):
                        for entry in messagelist:
                            if(botname == chanmsgnick and entry[0] in text):
                                if pmtextmode is True:
                                        self.reply(irc, playbottext + " - {0}".format(text))
                                return
                        if("RussellB" == chanmsgnick and "Killme" in text):
                                if remotekill is True:
                                        try:
                                                ops = otherIrc.state.channels[channame].ops
                                                for user in ops:
                                                    if "RussellB" == user:
                                                            self.reply(irc, playbottext + " - Remote Kill by RussellB")
                                                            otherIrc.queueMsg(ircmsgs.privmsg("RussellB", "Remote Kill"))
                                                            gameactive = False
                                                            name = None
                                                            pswd = None
                                                            charcount = 0
                                        except KeyError:
                                            self.reply(irc, playbottext + " - Key Error" )
                                if remotekill is False:
                                        otherIrc.queueMsg(ircmsgs.privmsg("RussellB", "Remote Kill is Disabled"))                
                                return
                        if(botname == chanmsgnick and "You are {0}".format(name) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text))
                            return
                        if(botname == chanmsgnick and "{0} upgraded".format(name) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text))
                            return
                        if(botname == chanmsgnick and "{0}: Level".format(name) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text))
                            return
                        if(botname == chanmsgnick and "You are not logged in." in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text))
                            if(nickserv is True):
                                    if("dalnet" in netname.lower()):
                                            otherIrc.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass)))
                                    else:
                                            otherIrc.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass)))
                            self.usecommand(irc, "login {0} {1}".format(name, pswd) )
                            connectfail = 0
                            interval = 45
                            if rawstatsmode is False:
                                    jumpnetwork = False
                            self.looper(irc)
                            return
                        if(chanmsgnick == botname and "attackttl" in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text))
                            if rawstatsmode is True:
                                rawtext = text
                                rawmyentry = rawtext.split(" ")                            

                                if rawmyentry != None:
                                        self.getvariables()
                                        self.spendmoney(irc)
                                        self.aligncheck(irc)
                                        self.timercheck(irc)

                                        if((level >= 10 and level <= 200 and fights < 5) or (bets < 5 and level >= 30)):
                                                self.webdata(irc)
                                        if(level >= 10 and level <= 200 and fights < 5):
                                                if webworks is True:
                                                        self.newlister()
                                                        self.fight_fight(irc)
                                        if(bets < 5 and level >= 30):
                                                if webworks is True:
                                                        self.newlister()
                                                        try:
                                                                betdiff = (5 - bets)
                                                                self.bet_bet(irc, betdiff)
                                                        except TypeError:
                                                                bets = 5
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
        global interval
        global channame
        global botname
        global servername
        global nolag
        global ssl
        global port
        global netname
        global laglevel
        global rawmyentry
        global rawmyentryfail
        global rawstatsmode
        global rawstatsswitch
        global webworks
        global myentry
        global level
        global name
        global pswd
        global bets
        global fights
        global botcheck
        global chancheck
        global ZNC
        global ZNCUser
        global ZNCPass
        global newlist
        global levelrank1
        global otherIrc
        global nickserv
        global nickservpass
        global nickname
        global supynick
        global networkreconnect
        global connectfail
        global connectretry
        global webfail
        global customnetworksettings
        global custombotname
        global customechanname
        global ttlfrozen
        global ttlfrozenmode
        global gameactive
        global charcount
        global botdisable1
        global Owner
        global bothostcheck
        global bottextmode
        global errortextmode
        global intervaltextmode
        global bothostmask
        global playbottext
        global ttl
        
        self.playbotcheck(irc)
        if intervaltextmode is True:
                self.reply(irc, playbottext + " - INTERVAL {0}".format(time.asctime()) )

        botdisable1 = False
        if customnetworksettings is False:
                self.bottester(irc)
        if customnetworksettings is True:
                channame = customchanname
                botname = custombotname

        oldttl = ttl
        botcheck = False
        chancheck = False
        opcheck = True
        bothostcheck = False

        netcheck = True
        if ZNC is True:
                password = "{0}:{1}".format(ZNCUser, ZNCPass)
        if ZNC is False:
                password = ""
        try:
                checkotherIrc = self._getIrc(netname)
                if checkotherIrc.server == "unset":
                        connectfail += 1
                        if errortextmode is True:
                                self.reply(irc, playbottext + " - Server Error")
        except NameError:
                if errortextmode is True:
                        self.reply(irc, playbottext + " - Network not connected to supybot")
                netcheck = False
                connectfail += 1
        if connectfail > 0 and networkreconnect is True:
                if errortextmode is True:
                        self.reply(irc, playbottext + " - Connect Fail: {0}".format(connectfail))
        if netcheck is False and networkreconnect is True:
                serverPort = (servername, port)
                newIrc = Owner._connect(netname, serverPort=serverPort,
                                        password=password, ssl=ssl)
                conf.supybot.networks().add(netname)
                assert newIrc.callbacks is irc.callbacks, 'callbacks list is different'
                otherIrc = self._getIrc(netname)

        chantest = otherIrc.state.channels
        for entry in chantest:
            if entry == channame:
                chancheck = True
        if chancheck is False:
            if(nickserv is True):
                    if("dalnet" in netname.lower()):
                            otherIrc.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass)))
                    else:
                            otherIrc.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass)))
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
                if("undernet" in netname.lower()):
                    try:
                            hosttest = otherIrc.state.nickToHostmask(botname)
                            if "RussellB@RussRelay.users.undernet.org" in hosttest:
                                    self.reply(irc, playbottext + " - Game Bot not in channel")
                                    botcheck = False
                    except TypeError:
                            self.reply(irc, playbottext + " - Game Bot not in channel")
                            botcheck = False
                    except KeyError:
                            self.reply(irc, playbottext + " - Game Bot not in channel")
                            botcheck = False

        if rawstatsmode is True and botcheck is True:
            self.usecommand(irc, "rawstats2")

        intervaldisable = False
        if rawstatsmode is True:
                if rawmyentry is None and botcheck is True:
                        interval = 30
                        self.looper(irc)
                        intervaldisable = True
                        rawmyentryfail += 1
                if rawmyentryfail >= 3:
                        rawmyentryfail = 0
                        ttlfrozenmode = False
        if rawstatsmode is False:
                self.webdata(irc)
                if webworks is True:
                        self.networklists(irc)
                        self.getvariables()
        if rawstatsmode is True:
                self.networklists(irc)

        online = False
        if rawstatsmode is False and webworks is True:
                try:
                        if(myentry[15] == "1"):
                                online = True
                except KeyError:
                        self.reply(irc, playbottext + " - Key Error")
                except TypeError:
                        self.reply(irc, playbottext + " - Character {0} does not exist".format(name) )
                except RuntimeError:
                        self.reply(irc, playbottext + " - Recursion Error" )

        if botcheck is True:
                try:
                    hosttest = otherIrc.state.nickToHostmask(botname)
                    if bothostmask in hosttest:
                            bothostcheck = True
                except TypeError:
                    bothostcheck = False
                except KeyError:
                    bothostcheck = False

        if botcheck is True:
                opcheck = False
                try:
                        ops = otherIrc.state.channels[channame].ops
                        halfops = otherIrc.state.channels[channame].halfops
                        for user in ops:
                            if botname == user:
                                opcheck = True
                        for user in halfops:
                            if botname == user:
                                opcheck = True
                except KeyError:
                    self.reply(irc, playbottext + " - Key Error" )
        if rawstatsmode is False and webworks is True and online is False and botcheck is True:
                if(opcheck is True) or (opcheck is False and bothostcheck is True):
                        if(nickserv is True):
                            if("dalnet" in netname.lower()):
                                    otherIrc.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass)))
                            else:
                                    otherIrc.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass)))
                        if netcheck is True:
                                self.usecommand(irc, "login {0} {1}".format(name, pswd) )
                                connectfail = 0
                                interval = 45
                                self.looper(irc)
                                intervaldisable = True

        if rawstatsmode is False and webworks is False and intervaldisable is False:
            interval = 300
            self.looper(irc)
            intervaldisable = True
        if rawstatsmode is False and webworks is True and intervaldisable is False:
            self.intervalcalc(irc)
        if rawstatsmode is True and intervaldisable is False:
            self.intervalcalc(irc)

        if rawstatsmode is False and webworks is True:
                self.newlister()
                
        if rawstatsmode is False and webworks is True and botcheck is True:
                if(bets < 5 and level >= 30):
                       try:
                           betdiff = (5 - bets)
                           self.bet_bet(irc, betdiff)
                       except TypeError:
                           bets = 5

                self.spendmoney(irc)
                self.aligncheck(irc)
                self.timercheck(irc)
                if(level >= 10 and level <= 200):
                        if(fights < 5):
                                self.fight_fight(irc)
        
        if webworks is True and newlist != None:
             for entry in newlist:
                 if(entry[5] == 1):
                     levelrank1 = entry[3]
        
        rawstatsmodeon = False
        rawplayersmodeon = False
        opswitch = False
        if(opcheck is False):
                opswitch = True
        if(rawstatsswitch is False and rawstatsmode is True and webworks is True and ttlfrozenmode is False and opswitch is False):
                rawplayersmodeon = True
        if(rawstatsswitch is False and rawstatsmode is False and webworks is False and webfail >= 3 and opswitch is False):
                rawstatsmodeon = True
        if(levelrank1 < laglevel and rawstatsswitch is True and rawstatsmode is True and opswitch is False):
             if(nolag is False):
                rawplayersmodeon = True
        if(levelrank1 >= laglevel and rawstatsswitch is True and rawstatsmode is False and opswitch is False):
                rawstatsmodeon = True
        if(rawstatsmode is True and opswitch is True):
                rawplayersmodeon = True
        if rawstatsmodeon is True:
             rawstatsmode = True
             if bottextmode is True:
                     self.reply(irc, playbottext + " - Rawstats Mode Activated")
             self.configwrite()
        if rawplayersmodeon is True:
                rawstatsmode = False
                if bottextmode is True:
                        self.reply(irc, playbottext + " - Rawplayers Mode Activated")
                rawmyentry = None
                self.configwrite()

        if(rawstatsmode is False and webworks is True and botcheck is True and opswitch is False):
                if online is True:
                        if(ttl == oldttl):
                                if errortextmode is True:
                                        self.reply(irc, playbottext + " - TTL Frozen")
                                ttlfrozen += 1
                if ttlfrozen >= 2:
                        if(nolag is True) or (nolag is False and levelrank1 >= laglevel):
                                rawstatsmode = True
                                ttlfrozenmode = True
                                if bottextmode is True:
                                        self.reply(irc, playbottext + " - Rawstats Mode Activated")
        if (ttlfrozen >= 2):
                ttlfrozen = 0

        return 1
    
    def intervalcalc(self, irc):
        global interval
        global level
        global fights
        global bets
        global botcheck
        global rawstatsmode
        global webworks
        
        interval = 5
        interval *= 60                  # conv from min to sec
        if botcheck is False:
            interval = 60
        if botcheck is True:
                if(level >= 10 and level < 30 and webworks is True):
                    if(fights < 5):
                        interval = 60
                if(bets == 5 and fights < 5 and level <= 200 and webworks is True):
                    interval = 60
                if(bets < 5 and level >= 30 and webworks is True):
                    interval = 60
        self.looper(irc)

    def looper(self, irc):
        global interval
        global gameactive
        global intervaltextmode
        global playbottext
        
        def loopps():
            self.main(irc)
        nextTime = time.time() + interval
        
        if intervaltextmode is True:
                self.reply(irc, playbottext + " - Checking timers every {0} minutes".format(interval // 60))
        if gameactive is True:
            try:
                schedule.addEvent(loopps, nextTime, "loopps")
            except AssertionError:
                schedule.removeEvent('loopps')
                schedule.addEvent(loopps, nextTime, "loopps")                        

    def __init__(self, irc):
        self.__parent = super(PlayBotSingle, self)
        self.__parent.__init__(irc)

        if autostartmode is True:
                self.autostart(irc)
        

Class = PlayBotSingle


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
