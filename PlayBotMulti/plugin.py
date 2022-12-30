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
    _ = PluginInternationalization('PlayBotMulti')
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
newlist2 = None
newlist3 = None
newlist4 = None
newlist5 = None
playerlist = None
myentry = None
myentry2 = None
myentry3 = None
myentry4 = None
myentry5 = None
rawmyentry = None
rawmyentry2 = None
rawmyentry3 = None
rawmyentry4 = None
rawmyentry5 = None
rawmyentryfail = 0
itemslists = None
align = "n"
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

customnetworksettings2 = False # True = on, False = off - For custom networks which are not on the networklist
customservernameb = "irc.mircphantom.net" # Custom Server address
customservernameb2 = "176.31.181.159" # Custom Server address
customchanname2 = "#multirpg" # Custom Channel Name
custombotname2 = "multirpg/fun" # Custom Botname
customnolag2 = False # True = on, False = off - If network is on the nolag network list
customport2 = 6667 # port
customssl2 = False # True = on, False = off - SSL
custombosthostmask2 = "multirpg@multirpg.users.IRC4Fun.net" # Custom Bot Host Name

customnetworksettings3 = False # True = on, False = off - For custom networks which are not on the networklist
customservernamec = "irc.mircphantom.net" # Custom Server address
customservernamec2 = "176.31.181.159" # Custom Server address
customchanname3 = "#multirpg" # Custom Channel Name
custombotname3 = "multirpg/fun" # Custom Botname
customnolag3 = False # True = on, False = off - If network is on the nolag network list
customport3 = 6667 # port
customssl3 = False # True = on, False = off - SSL
custombosthostmask3 = "multirpg@multirpg.users.IRC4Fun.net" # Custom Bot Host Name

customnetworksettings4 = False # True = on, False = off - For custom networks which are not on the networklist
customservernamed = "irc.mircphantom.net" # Custom Server address
customservernamed2 = "176.31.181.159" # Custom Server address
customchanname4 = "#multirpg" # Custom Channel Name
custombotname4 = "multirpg/fun" # Custom Botname
customnolag4 = False # True = on, False = off - If network is on the nolag network list
customport4 = 6667 # port
customssl4 = False # True = on, False = off - SSL
custombosthostmask4 = "multirpg@multirpg.users.IRC4Fun.net" # Custom Bot Host Name

customnetworksettings5 = False # True = on, False = off - For custom networks which are not on the networklist
customservernamee = "irc.mircphantom.net" # Custom Server address
customservernamee2 = "176.31.181.159" # Custom Server address
customchanname5 = "#multirpg" # Custom Channel Name
custombotname5 = "multirpg/fun" # Custom Botname
customnolag5 = False # True = on, False = off - If network is on the nolag network list
customport5 = 6667 # port
customssl5 = False # True = on, False = off - SSL
custombosthostmask5 = "multirpg@multirpg.users.IRC4Fun.net" # Custom Bot Host Name

# ZNC settings - Ignore if networkreconnect is False
ZNC1 = False # ZNC1 Server Mode - True = On, False = Off
ZNCServer1 = "" # ZNC1 Server Address
ZNCPort1 = 1234 # ZNC1 Port Number
ZNCUser1 = "/" # ZNC1 Username/Network
ZNCPass1 = "" # ZNC1 Password
ZNCssl1 = False
ZNCnolag1 = False

ZNC2 = False # ZNC2 Server Mode - True = On, False = Off
ZNCServer2 = "" # ZNC2 Server Address
ZNCPort2 = 1234 # ZNC2 Port Number
ZNCUser2 = "/" # ZNC2 Username/Network
ZNCPass2 = "" # ZNC2 Password
ZNCssl2 = False
ZNCnolag2 = False

ZNC3 = False # ZNC3 Server Mode - True = On, False = Off
ZNCServer3 = "" # ZNC3 Server Address
ZNCPort3 = 1234 # ZNC3 Port Number
ZNCUser3 = "/" # ZNC3 Username/Network
ZNCPass3 = "" # ZNC3 Password
ZNCssl3 = False
ZNCnolag3 = False

ZNC4 = False # ZNC4 Server Mode - True = On, False = Off
ZNCServer4 = "" # ZNC4 Server Address
ZNCPort4 = 1234 # ZNC4 Port Number
ZNCUser4 = "/" # ZNC4 Username/Network
ZNCPass4 = "" # ZNC4 Password
ZNCssl4 = False
ZNCnolag4 = False

ZNC5 = False # ZNC5 Server Mode - True = On, False = Off
ZNCServer5 = "" # ZNC5 Server Address
ZNCPort5 = 1234 # ZNC5 Port Number
ZNCUser5 = "/" # ZNC5 Username/Network
ZNCPass5 = "" # ZNC5 Password
ZNCssl5 = False
ZNCnolag5 = False

# Changeable setting
multirpgclass = "MultiRPG PlayBot" # Class to be used when auto-registering
nickserv1 = False # True = on, False = off
nickserv2 = False # True = on, False = off
nickserv3 = False # True = on, False = off
nickserv4 = False # True = on, False = off
nickserv5 = False # True = on, False = off
nickservpass1 = "**********" # NickServ Password
nickservpass2 = "**********" # NickServ Password
nickservpass3 = "**********" # NickServ Password
nickservpass4 = "**********" # NickServ Password
nickservpass5 = "**********" # NickServ Password
networkreconnect = False # True = on, False = off - Reconnects network connection and server address switching
connectretry = 6 # Retries to connect to network before it switch to another server
laglevel = 25 # If using rawstats and a laggy network it will switch between using rawstats and rawplayers
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
name2 = None
name3 = None
name4 = None
name5 = None
pswd = None
pswd2 = None
pswd3 = None
pswd4 = None
pswd5 = None
servername = None
networkname = None
servername2 = None
networkname2 = None
servername3 = None
networkname3 = None
servername4 = None
networkname4 = None
servername5 = None
networkname5 = None
servernum1 = 1
servernum2 = 1
servernum3 = 1
servernum4 = 1
servernum5 = 1
connectfail1 = 0
connectfail2 = 0
connectfail3 = 0
connectfail4 = 0
connectfail5 = 0
ssl = None
ssl2 = None
ssl3 = None
ssl4 = None
ssl5 = None
port = None
port2 = None
port3 = None
port4 = None
port5 = None
webfail = 0
nolag1 = None
nolag2 = None
nolag3 = None
nolag4 = None
nolag5 = None

char1 = False
char2 = False
char3 = False
char4 = False
char5 = False
charcount = 0
rankplace = 0
level = 0
alignlevel = 0
mysum = 0
gold = 0
bank = 0
team = 0
ufightcalc1 = 0
ufightcalc2 = 0
ufightcalc3 = 0
ufightcalc4 = 0
ufightcalc5 = 0
fightSum1 = 0
fightSum2 = 0
fightSum3 = 0
fightSum4 = 0
fightSum5 = 0

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
levelrank1 = 99

nickname = None
nickname2 = None
nickname3 = None
nickname4 = None
nickname5 = None
netname = None
netname2 = None
netname3 = None
netname4 = None
netname5 = None
channame = None
channame2 = None
channame3 = None
channame4 = None
channame5 = None
botname = None
botname2 = None
botname3 = None
botname4 = None
botname5 = None
botcheck1 = None
botcheck2 = None
botcheck3 = None
botcheck4 = None
botcheck5 = None
bothostcheck1 = False
bothostcheck2 = False
bothostcheck3 = False
bothostcheck4 = False
bothostcheck5 = False
bothostmask1 = None
bothostmask2 = None
bothostmask3 = None
bothostmask4 = None
bothostmask5 = None
chancheck1 = None
chancheck2 = None
chancheck3 = None
chancheck4 = None
chancheck5 = None
webworks = None
gameactive = None

otherIrc = None
otherIrc2 = None
otherIrc3 = None
otherIrc4 = None
otherIrc5 = None
supynick = None
supynick2 = None
supynick3 = None
supynick4 = None
supynick5 = None
ttlfrozen1 = 0
ttlfrozen2 = 0
ttlfrozen3 = 0
ttlfrozen4 = 0
ttlfrozen5 = 0
ttlfrozenmode = False
botdisable1 = False
botdisable2 = False
botdisable3 = False
botdisable4 = False
botdisable5 = False
Owner = None
Owner2 = None
Owner3 = None
Owner4 = None
Owner5 = None
jumpnetwork = False
jumpnetwork2 = False
jumpnetwork3 = False
jumpnetwork4 = False
jumpnetwork5 = False
autostartmode = False
playbotcount = 0
playbottext = None
playbotid = "PM"
pbcount = 0

playbotsingle = False
playbotmulti = False

fileprefix = "playbotmulticonfig.txt"
path = conf.supybot.directories.data
filename = path.dirize(fileprefix)
try:
    f = open(filename,"rb")
    configList = pickle.load(f)
    f.close()
except:
    configList = []
fileprefix2 = "autostartmulticonfig.txt"
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

class PlayBotMulti(callbacks.Plugin):
    """MultiRPG PlayBotMulti"""
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
                self.replymulti(irc, "Could not access {0}".format(russweb))

        self.replymulti(irc, "Current version {0}".format(currentversion))
        self.replymulti(irc, "Web version {0}".format(webversion))
        if webversion != None:
                if(currentversion == webversion):
                    self.replymulti(irc, "You have the current version of PlayBot")
                if(currentversion < webversion):
                    self.replymulti(irc, "You have an old version of PlayBot")
                    self.replymulti(irc, "You can download a new version from {0}".format(russweb))
                if(currentversion > webversion):
                    self.replymulti(irc, "Give me, Give me")

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
        global name2
        global pswd2
        global nickname2
        global netname2
        global name3
        global pswd3
        global nickname3
        global netname3
        global name4
        global pswd4
        global nickname4
        global netname4
        global name5
        global pswd5
        global nickname5
        global netname5
        global supynick
        global supynick2
        global supynick3
        global supynick4
        global supynick5

        autoconfigList = []
        autoconfigList.append( ( "name", name ) )
        autoconfigList.append( ( "pswd", pswd ) )
        autoconfigList.append( ( "nickname", nickname ) )
        autoconfigList.append( ( "netname", netname ) )
        autoconfigList.append( ( "name2", name2 ) )
        autoconfigList.append( ( "pswd2", pswd2 ) )
        autoconfigList.append( ( "nickname2", nickname2 ) )
        autoconfigList.append( ( "netname2", netname2 ) )
        autoconfigList.append( ( "name3", name3 ) )
        autoconfigList.append( ( "pswd3", pswd3 ) )
        autoconfigList.append( ( "nickname3", nickname3 ) )
        autoconfigList.append( ( "netname3", netname3 ) )
        autoconfigList.append( ( "name4", name4 ) )
        autoconfigList.append( ( "pswd4", pswd4 ) )
        autoconfigList.append( ( "nickname4", nickname4 ) )
        autoconfigList.append( ( "netname4", netname4 ) )
        autoconfigList.append( ( "name5", name5 ) )
        autoconfigList.append( ( "pswd5", pswd5 ) )
        autoconfigList.append( ( "nickname5", nickname5 ) )
        autoconfigList.append( ( "netname5", netname5 ) )
        autoconfigList.append( ( "supynick", supynick ) )
        autoconfigList.append( ( "supynick2", supynick2 ) )
        autoconfigList.append( ( "supynick3", supynick3 ) )
        autoconfigList.append( ( "supynick4", supynick4 ) )
        autoconfigList.append( ( "supynick5", supynick5 ) )
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
        global rawmyentry2
        global rawmyentry3
        global rawmyentry4
        global rawmyentry5
        global char1
        global char2
        global char3
        global char4
        global char5
        global ttlfrozen1
        global ttlfrozen2
        global ttlfrozen3
        global ttlfrozen4
        global ttlfrozen5
        global secondalign
        global alignlevel
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
                                if char1 is True:
                                        rawmyentry = None
                                        ttlfrozen1 = 0
                                if char2 is True:
                                        rawmyentry2 = None
                                        ttlfrozen2 = 0
                                if char3 is True:
                                        rawmyentry3 = None
                                        ttlfrozen3 = 0
                                if char4 is True:
                                        rawmyentry4 = None
                                        ttlfrozen4 = 0
                                if char5 is True:
                                        rawmyentry5 = None
                                        ttlfrozen5 = 0
                                rawstatsswitch = False
                                rawstatsmode = False
                                self.webdata(irc)
                                self.newitemslister(irc, 1, 1)
                                irc.reply("Rawplayers Mode Activated.  To turn it back to Rawstats Mode use 'setoption rawstats true' command", private=True)
                if text == "rawplayers":
        ##              Turns on getting data from rawplayers instead of rawstats
                        if value is True:
                                if char1 is True:
                                        rawmyentry = None
                                        ttlfrozen1 = 0
                                if char2 is True:
                                        rawmyentry2 = None
                                        ttlfrozen2 = 0
                                if char3 is True:
                                        rawmyentry3 = None
                                        ttlfrozen3 = 0
                                if char4 is True:
                                        rawmyentry4 = None
                                        ttlfrozen4 = 0
                                if char5 is True:
                                        rawmyentry5 = None
                                        ttlfrozen5 = 0
                                rawstatsswitch = False
                                rawstatsmode = False
                                self.webdata(irc)
                                self.newitemslister(irc, 1, 1)
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
                                if char1 is True:
                                        self.usecommand(irc, "align undead", 1)
                                if char2 is True:
                                        self.usecommand(irc, "align undead", 2)
                                if char3 is True:
                                        self.usecommand(irc, "align undead", 3)
                                if char4 is True:
                                        self.usecommand(irc, "align undead", 4)
                                if char5 is True:
                                        self.usecommand(irc, "align undead", 5)
                                irc.reply("Evil Mode On.  To turn it back off use 'setoption evil false' command", private=True)
        ##              Turns Evil Mode off
                        if value is False:
                                evilmode = False
                                secondalign = "human"
                                alignlevel = setalign
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

    def bottester(self, irc, num):
        global otherIrc
        global otherIrc2
        global otherIrc3
        global otherIrc4
        global otherIrc5
        global botname
        global botname2
        global botname3
        global botname4
        global botname5
        global channame
        global channame2
        global channame3
        global channame4
        global channame5
        global netname
        global netname2
        global netname3
        global netname4
        global netname5
        global char1
        global char2
        global char3
        global char4
        global char5
        global botdisable1
        global botdisable2
        global botdisable3
        global botdisable4
        global botdisable5
        
        botcount1 = 0
        botcount2 = 0
        botcount3 = 0
        botcount4 = 0
        botcount5 = 0
        bottest2 = "multirpg"
        
        if num == 1 and char1 is True:
                if("undernet" in netname.lower()):
                        channame = "#idlerpg"
                        botname = "idlerpg"
                else:
                        channame = "#multirpg"
                        botname = "multirpg"

                bottest = botname
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
                    self.reply(irc, "Key Error", 1)

                botcount1 = len(botentry)
                if botcount1 == 1:
                        botname = botname10
                if botcount1 >= 2:
                        botdisable1 = True
        if num == 2 and char2 is True:
                if("undernet" in netname2.lower()):
                        channame2 = "#idlerpg"
                        botname2 = "idlerpg"
                else:
                        channame2 = "#multirpg"
                        botname2 = "multirpg"

                bottest = botname2
                botentry = []
                
                try:
                    ops = otherIrc2.state.channels[channame2].ops
                    halfops = otherIrc2.state.channels[channame2].halfops
                    for user in ops:
                        if bottest in user and user != bottest:
                                botentry.append(user)
                                botname10 = user
                    for user in halfops:
                        if bottest in user and user != bottest:
                                botentry.append(user)
                                botname10 = user
                    if("undernet" in netname2.lower()):
                        for user in ops:
                                if bottest2 in user:
                                        botentry.append(user)
                                        botname10 = user
                except KeyError:
                    self.reply(irc, "Key Error", 2)

                botcount2 = len(botentry)
                if botcount2 == 1:
                        botname2 = botname10
                if botcount2 >= 2:
                        botdisable2 = True

        if num == 3 and char3 is True:
                if("undernet" in netname3.lower()):
                        channame3 = "#idlerpg"
                        botname3 = "idlerpg"
                else:
                        channame3 = "#multirpg"
                        botname3 = "multirpg"

                bottest = botname3
                botentry = []
                
                try:
                    ops = otherIrc3.state.channels[channame3].ops
                    halfops = otherIrc3.state.channels[channame3].halfops
                    for user in ops:
                        if bottest in user and user != bottest:
                                botentry.append(user)
                                botname10 = user
                    for user in halfops:
                        if bottest in user and user != bottest:
                                botentry.append(user)
                                botname10 = user
                    if("undernet" in netname3.lower()):
                        for user in ops:
                                if bottest2 in user:
                                        botentry.append(user)
                                        botname10 = user
                except KeyError:
                    self.reply(irc, "Key Error", 3)

                botcount3 = len(botentry)
                if botcount3 == 1:
                        botname3 = botname10
                if botcount3 >= 2:
                        botdisable3 = True

        if num == 4 and char4 is True:
                if("undernet" in netname4.lower()):
                        channame4 = "#idlerpg"
                        botname4 = "idlerpg"
                else:
                        channame4 = "#multirpg"
                        botname4 = "multirpg"

                bottest = botname4
                botentry = []
                
                try:
                    ops = otherIrc4.state.channels[channame4].ops
                    halfops = otherIrc4.state.channels[channame4].halfops
                    for user in ops:
                        if bottest in user and user != bottest:
                                botentry.append(user)
                                botname10 = user
                    for user in halfops:
                        if bottest in user and user != bottest:
                                botentry.append(user)
                                botname10 = user
                    if("undernet" in netname4.lower()):
                        for user in ops:
                                if bottest2 in user:
                                        botentry.append(user)
                                        botname10 = user
                except KeyError:
                    self.reply(irc, "Key Error", 4)

                botcount4 = len(botentry)
                if botcount4 == 1:
                        botname4 = botname10
                if botcount4 >= 2:
                        botdisable4 = True

        if num == 5 and char5 is True:
                if("undernet" in netname5.lower()):
                        channame5 = "#idlerpg"
                        botname5 = "idlerpg"
                else:
                        channame5 = "#multirpg"
                        botname5 = "multirpg"

                bottest = botname5
                botentry = []
                
                try:
                    ops = otherIrc5.state.channels[channame5].ops
                    halfops = otherIrc5.state.channels[channame5].halfops
                    for user in ops:
                        if bottest in user and user != bottest:
                                botentry.append(user)
                                botname10 = user
                    for user in halfops:
                        if bottest in user and user != bottest:
                                botentry.append(user)
                                botname10 = user
                    if("undernet" in netname5.lower()):
                        for user in ops:
                                if bottest2 in user:
                                        botentry.append(user)
                                        botname10 = user
                except KeyError:
                    self.reply(irc, "Key Error", 5)

                botcount5 = len(botentry)
                if botcount5 == 1:
                        botname5 = botname10
                if botcount5 >= 2:
                        botdisable5 = True

    def usecommand(self, irc, commanded, num):
        global botname
        global botname2
        global botname3
        global botname4
        global botname5
        global otherIrc
        global otherIrc2
        global otherIrc3
        global otherIrc4
        global otherIrc5
        global customnetworksettings
        global customnetworksettings2
        global customnetworksettings3
        global customnetworksettings4
        global customnetworksettings5
        global botdisable1
        global botdisable2
        global botdisable3
        global botdisable4
        global botdisable5
        
        if num == 1 and customnetworksettings is False:
                self.bottester(irc, 1)
        if num == 2 and customnetworksettings2 is False:
                self.bottester(irc, 2)
        if num == 3 and customnetworksettings3 is False:
                self.bottester(irc, 3)
        if num == 4 and customnetworksettings4 is False:
                self.bottester(irc, 4)
        if num == 5 and customnetworksettings5 is False:
                self.bottester(irc, 5)

        if num == 1 and botdisable1 is False:
            otherIrc.queueMsg(ircmsgs.privmsg(botname, commanded))
        if num == 2 and botdisable2 is False:
            otherIrc2.queueMsg(ircmsgs.privmsg(botname2, commanded))
        if num == 3 and botdisable3 is False:
            otherIrc3.queueMsg(ircmsgs.privmsg(botname3, commanded))
        if num == 4 and botdisable4 is False:
            otherIrc4.queueMsg(ircmsgs.privmsg(botname4, commanded))
        if num == 5 and botdisable5 is False:
            otherIrc5.queueMsg(ircmsgs.privmsg(botname5, commanded))

    def reply(self, irc, text, num):
        global nickname
        global nickname2
        global nickname3
        global nickname4
        global nickname5
        global channame
        global channame2
        global channame3
        global channame4
        global channame5
        global otherIrc
        global otherIrc2
        global otherIrc3
        global otherIrc4
        global otherIrc5
        global supynick
        global supynick2
        global supynick3
        global supynick4
        global supynick5
        
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
                chanstate = otherIrc2.state.channels[channame2]
                users = [user for user in chanstate.users]
                for entry in users:
                    if nickname2 == entry:
                        nickcheck2 = True
            except KeyError:
                return
        if num == 3:
            nickcheck3 = False
            try:
                chanstate = otherIrc3.state.channels[channame3]
                users = [user for user in chanstate.users]
                for entry in users:
                    if nickname3 == entry:
                        nickcheck3 = True
            except KeyError:
                return
        if num == 4:
            nickcheck4 = False
            try:
                chanstate = otherIrc4.state.channels[channame4]
                users = [user for user in chanstate.users]
                for entry in users:
                    if nickname4 == entry:
                        nickcheck4 = True
            except KeyError:
                return
        if num == 5:
            nickcheck5 = False
            try:
                chanstate = otherIrc5.state.channels[channame5]
                users = [user for user in chanstate.users]
                for entry in users:
                    if nickname5 == entry:
                        nickcheck5 = True
            except KeyError:
                return

        if num == 1:
                if nickcheck is True and nickname != supynick:
                        otherIrc.queueMsg(ircmsgs.privmsg(nickname, text))
        if num == 2:
                if nickcheck2 is True and nickname2 != supynick2:
                        otherIrc2.queueMsg(ircmsgs.privmsg(nickname2, text))
        if num == 3:
                if nickcheck3 is True and nickname3 != supynick3:
                        otherIrc3.queueMsg(ircmsgs.privmsg(nickname3, text))
        if num == 4:
                if nickcheck4 is True and nickname4 != supynick4:
                        otherIrc4.queueMsg(ircmsgs.privmsg(nickname4, text))
        if num == 5:
                if nickcheck5 is True and nickname5 != supynick5:
                        otherIrc5.queueMsg(ircmsgs.privmsg(nickname5, text))
            
    def replymulti(self, irc, text):
        global char1
        global char2
        global char3
        global char4
        global char5

        if char1 is True:
                self.reply(irc, text, 1)
        if char2 is True:
                self.reply(irc, text, 2)
        if char3 is True:
                self.reply(irc, text, 3)
        if char4 is True:
                self.reply(irc, text, 4)
        if char5 is True:
                self.reply(irc, text, 5)
            
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

        Log in to Game.
        """
        global name
        global pswd
        global name2
        global pswd2
        global name3
        global pswd3
        global name4
        global pswd4
        global name5
        global pswd5
        global netname
        global netname2
        global netname3
        global netname4
        global netname5
        global nickname
        global nickname2
        global nickname3
        global nickname4
        global nickname5
        global channame
        global channame2
        global channame3
        global channame4
        global channame5
        global botname
        global botname2
        global botname3
        global botname4
        global botname5
        global rawstatsmode
        global char1
        global char2
        global char3
        global char4
        global char5
        global charcount
        global rawstatsswitch
        global gameactive
        global otherIrc
        global otherIrc2
        global otherIrc3
        global otherIrc4
        global otherIrc5
        global supynick
        global supynick2
        global supynick3
        global supynick4
        global supynick5
        global customnetworksettings
        global custombotname
        global customchanname
        global customnetworksettings2
        global custombotname2
        global customchanname2
        global customnetworksettings3
        global custombotname3
        global customchanname3
        global customnetworksettings4
        global custombotname4
        global customchanname4
        global customnetworksettings5
        global custombotname5
        global customchanname5
        global Owner
        global Owner2
        global Owner3
        global Owner4
        global Owner5
        global autostartmode
        global pbcount
        global networklist
        
        charcount += 1

        netlist = []
        for entry in networklist:
                if entry[3] == 1:
                        netlist.append( ( entry[0] ) )
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
                        if netcheck is False:
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
                        irc.error("To log in use <bot> playbotmulti login CharName Password")
                if(name is None or pswd is None or netcheck is False):
                        charcount = 0

                if charcount == 1:
                        if pbcount == 2:
                                singleplayerlist = self.singleread(irc)
                                try:
                                        singlename = singleplayerlist[0][1]
                                        singlenetname = singleplayerlist[0][3]
                                        if(name == singlename):
                                                irc.error("Character {0} is already logged in on PlayBotSingle".format(name))
                                                charcount = 0
                                        if(netname == singlenetname):
                                                irc.error("Character {0} is already logged in on PlayBotSingle".format(singlename))
                                                charcount = 0
                                except IndexError:
                                        irc.reply("No Players Logged in on PlayBotSingle", private=True)
                                
                if charcount == 0:
                        gameactive = False
                        name = None
                        pswd = None
                        return
                        
                if charcount == 1:
                        if rawstatsmode is True or rawstatsswitch is True:
                                self.bootopcheck(irc, 1)

                        if(name != None and pswd != None):
                                char1 = True                    
                                self.usecommand(irc, "login {0} {1}".format(name, pswd), 1)
                                self.multiwrite(irc)
        if charcount == 2:
                netcheck = True
                nickname2 = msg.nick
                netname2 = self._getIrcName(irc)
                supynick2 = irc.nick
                Owner2 = irc.getCallback('Owner')

                if customnetworksettings2 is False:
                        netcheck = False
                        for entry in networklist:
                                if entry[0].lower() in netname2.lower():
                                        netcheck = True
                        if netcheck is False:
                                irc.error("Networks supported: {0}".format(netlist))
                                irc.error("Current Network: {0}.  The network name needs to have one of the above names in it".format(netname2))

                        if("undernet" in netname2.lower()):
                                channame2 = "#idlerpg"
                                botname2 = "idlerpg"
                        else:
                                channame2 = "#multirpg"
                                botname2 = "multirpg"

                if customnetworksettings2 is True:
                        channame2 = customchanname2
                        botname2 = custombotname2
                otherIrc2 = self._getIrc(netname2)

                self.playbotcheck(irc)
                args2 = arg2.split(" ")
                try:
                        if(name2 is None or pswd2 is None):
                                name2 = args2[0]
                                pswd2 = args2[1]
                except IndexError:
                        irc.error("To log in use <bot> playbotmulti login CharName Password")
                if(name2 is None or pswd2 is None or netcheck is False):
                        charcount = 1
                if charcount == 2:
                        if pbcount == 2:
                                singleplayerlist = self.singleread(irc)
                                try:
                                        singlename = singleplayerlist[0][1]
                                        singlenetname = singleplayerlist[0][3]
                                        if(name2 == singlename):
                                                irc.error("Character {0} is already logged in on PlayBotSingle".format(name2))
                                                charcount = 1
                                        if(netname2 == singlenetname):
                                                irc.error("Character {0} is already logged in on PlayBotSingle".format(singlename))
                                                charcount = 1
                                except IndexError:
                                        irc.reply("No Players Logged in on PlayBotSingle", private=True)
                if charcount == 2:
                        if rawstatsmode is True or rawstatsswitch is True:
                                self.bootopcheck(irc, 2)

                        if(netname2 != netname and name2 != name):
                                char2 = True                    
                                self.usecommand(irc, "login {0} {1}".format(name2, pswd2), 2)
                                if autostartmode is True:
                                    self.configwrite2()
                                self.multiwrite(irc)
                        if(netname2 != netname and name2 == name):
                                charcount = 1
                                irc.error("Character {0} is already logged in".format(name))
                        if(netname2 == netname):
                                if(supynick2 != supynick):
                                        char2 = True
                                        self.usecommand(irc, "login {0} {1}".format(name2, pswd2), 2 )
                                        if autostartmode is True:
                                            self.configwrite2()
                                        self.multiwrite(irc)
                                if(supynick2 == supynick):
                                        charcount = 1
                                        irc.error("Character {0} is already logged in".format(name))
                if charcount == 1:
                        char2 = False
                        netname2 = None
                        supynick2 = None
                        channame2 = None
                        botname2 = None
                        otherIrc2 = None
                        name2 = None
                        pswd2 = None
                        return
            
        if charcount == 3:
                netcheck = True
                nickname3 = msg.nick
                netname3 = self._getIrcName(irc)
                supynick3 = irc.nick
                Owner3 = irc.getCallback('Owner')
                if customnetworksettings3 is False:
                        netcheck = False
                        for entry in networklist:
                                if entry[0].lower() in netname3.lower():
                                        netcheck = True
                        if netcheck is False:
                                irc.error("Networks supported: {0}".format(netlist))
                                irc.error("Current Network: {0}.  The network name needs to have one of the above names in it".format(netname3))
                        if("undernet" in netname3.lower()):
                                channame3 = "#idlerpg"
                                botname3 = "idlerpg"
                        else:
                                channame3 = "#multirpg"
                                botname3 = "multirpg"

                if customnetworksettings3 is True:
                        channame3 = customchanname3
                        botname3 = custombotname3
                otherIrc3 = self._getIrc(netname3)

                self.playbotcheck(irc)
                args2 = arg2.split(" ")
                try:
                        if(name3 is None or pswd3 is None):
                                name3 = args2[0]
                                pswd3 = args2[1]
                except IndexError:
                        irc.error("To log in use <bot> playbotmulti login CharName Password")
                if(name3 is None or pswd3 is None or netcheck is False):
                        charcount = 2
                if charcount == 3:
                        if pbcount == 2:
                                singleplayerlist = self.singleread(irc)
                                try:
                                        singlename = singleplayerlist[0][1]
                                        singlenetname = singleplayerlist[0][3]
                                        if(name3 == singlename):
                                                irc.error("Character {0} is already logged in on PlayBotSingle".format(name3))
                                                charcount = 2
                                        if(netname3 == singlenetname):
                                                irc.error("Character {0} is already logged in on PlayBotSingle".format(singlename))
                                                charcount = 2
                                except IndexError:
                                        irc.reply("No Players Logged in on PlayBotSingle", private=True)
                if charcount == 3:
                        if rawstatsmode is True or rawstatsswitch is True:
                                self.bootopcheck(irc, 3)

                        if(netname3 != netname and netname3 != netname2 and name3 != name and name3 != name2):
                                char3 = True                    
                                self.usecommand(irc, "login {0} {1}".format(name3, pswd3), 3)
                                if autostartmode is True:
                                    self.configwrite2()
                                self.multiwrite(irc)

                        if((netname3 != netname and netname3 != netname2) and (name3 == name or name3 == name2)):
                                irc.error("Character {0} is already logged in".format(name3))
                                charcount = 2
                            
                        if(netname3 == netname):
                                if(supynick3 != supynick):
                                        char3 = True
                                        self.usecommand(irc, "login {0} {1}".format(name3, pswd3), 3 )
                                        if autostartmode is True:
                                            self.configwrite2()
                                        self.multiwrite(irc)
                                if(supynick3 == supynick): 
                                        irc.error("Character {0} is already logged in".format(name))
                                        charcount = 2

                        if(netname3 == netname2):
                                if(supynick3 != supynick2):
                                        char3 = True
                                        self.usecommand(irc, "login {0} {1}".format(name3, pswd3), 3 )
                                        if autostartmode is True:
                                            self.configwrite2()
                                        self.multiwrite(irc)
                                if(supynick3 == supynick2): 
                                        irc.error("Character {0} is already logged in".format(name2))
                                        charcount = 2
                if charcount == 2:
                        char3 = False
                        netname3 = None
                        supynick3 = None
                        channame3 = None
                        botname3 = None
                        otherIrc3 = None
                        name3 = None
                        pswd3 = None
                        return

        if charcount == 4:
                netcheck = True
                nickname4 = msg.nick
                netname4 = self._getIrcName(irc)
                supynick4 = irc.nick
                Owner4 = irc.getCallback('Owner')
                if customnetworksettings4 is False:
                        netcheck = False
                        for entry in networklist:
                                if entry[0].lower() in netname4.lower():
                                        netcheck = True
                        if netcheck is False:
                                irc.error("Networks supported: {0}".format(netlist))
                                irc.error("Current Network: {0}.  The network name needs to have one of the above names in it".format(netname4))
                        if("undernet" in netname4.lower()):
                                channame4 = "#idlerpg"
                                botname4 = "idlerpg"
                        else:
                                channame4 = "#multirpg"
                                botname4 = "multirpg"

                if customnetworksettings4 is True:
                        channame4 = customchanname4
                        botname4 = custombotname4
                otherIrc4 = self._getIrc(netname4)

                self.playbotcheck(irc)
                args2 = arg2.split(" ")
                try:
                        if(name4 is None or pswd4 is None):
                                name4 = args2[0]
                                pswd4 = args2[1]
                except IndexError:
                        irc.error("To log in use <bot> playbotmulti login CharName Password")
                if(name4 is None or pswd4 is None or netcheck is False):
                        charcount = 3
                if charcount == 4:
                        if pbcount == 2:
                                singleplayerlist = self.singleread(irc)
                                try:
                                        singlename = singleplayerlist[0][1]
                                        singlenetname = singleplayerlist[0][3]
                                        if(name4 == singlename):
                                                irc.error("Character {0} is already logged in on PlayBotSingle".format(name4))
                                                charcount = 3
                                        if(netname4 == singlenetname):
                                                irc.error("Character {0} is already logged in on PlayBotSingle".format(singlename))
                                                charcount = 3
                                except IndexError:
                                        irc.reply("No Players Logged in on PlayBotSingle", private=True)
                if charcount == 4:
                        if rawstatsmode is True or rawstatsswitch is True:
                                self.bootopcheck(irc, 4)

                        if(netname4 != netname and netname4 != netname2 and netname4 != netname3 and name4 != name and name4 != name2 and name4 != name3):
                                char4 = True                    
                                self.usecommand(irc, "login {0} {1}".format(name4, pswd4), 4)
                                if autostartmode is True:
                                    self.configwrite2()
                                self.multiwrite(irc)
                        if((netname4 != netname and netname4 != netname2 and netname4 != netname3) and (name4 == name or name4 == name2 or name4 == name3)):
                                irc.error("Character {0} is already logged in".format(name4))
                                charcount = 3

                        if(netname4 == netname):
                                if(supynick4 != supynick):
                                        char4 = True
                                        self.usecommand(irc, "login {0} {1}".format(name4, pswd4), 4 )
                                        if autostartmode is True:
                                            self.configwrite2()
                                        self.multiwrite(irc)
                                if(supynick4 == supynick):
                                        irc.error("Character {0} is already logged in".format(name))
                                        charcount = 3
                        if(netname4 == netname2):
                                if(supynick4 != supynick2):
                                        char4 = True
                                        self.usecommand(irc, "login {0} {1}".format(name4, pswd4), 4 )
                                        if autostartmode is True:
                                            self.configwrite2()
                                        self.multiwrite(irc)
                                if(supynick4 == supynick2):
                                        irc.error("Character {0} is already logged in".format(name2))
                                        charcount = 3
                        if(netname4 == netname3):
                                if(supynick4 != supynick3):
                                        char4 = True
                                        self.usecommand(irc, "login {0} {1}".format(name4, pswd4), 4 )
                                        if autostartmode is True:
                                            self.configwrite2()
                                        self.multiwrite(irc)
                                if(supynick4 == supynick3):
                                        irc.error("Character {0} is already logged in".format(name3))
                                        charcount = 3
                if charcount == 3:
                        char4 = False
                        netname4 = None
                        supynick4 = None
                        channame4 = None
                        botname4 = None
                        otherIrc4 = None
                        name4 = None
                        pswd4 = None
                        return

        if charcount == 5:
                netcheck = True
                nickname5 = msg.nick
                netname5 = self._getIrcName(irc)
                supynick5 = irc.nick
                Owner5 = irc.getCallback('Owner')
                if customnetworksettings5 is False:
                        netcheck = False
                        for entry in networklist:
                                if entry[0].lower() in netname5.lower():
                                        netcheck = True
                        if netcheck is False:
                                irc.error("Networks supported: {0}".format(netlist))
                                irc.error("Current Network: {0}.  The network name needs to have one of the above names in it".format(netname5))
                        if("undernet" in netname5.lower()):
                                channame5 = "#idlerpg"
                                botname5 = "idlerpg"
                        else:
                                channame5 = "#multirpg"
                                botname5 = "multirpg"

                if customnetworksettings5 is True:
                        channame5 = customchanname5
                        botname5 = custombotname5
                otherIrc5 = self._getIrc(netname5)

                self.playbotcheck(irc)
                args2 = arg2.split(" ")
                try:
                        if(name5 is None or pswd5 is None):
                                name5 = args2[0]
                                pswd5 = args2[1]
                except IndexError:
                        irc.error(irc, "To log in use <bot> playbotmulti login CharName Password")
                if(name5 is None or pswd5 is None or netcheck is False):
                        charcount = 4
                if charcount == 5:
                        if pbcount == 2:
                                singleplayerlist = self.singleread(irc)
                                try:
                                        singlename = singleplayerlist[0][1]
                                        singlenetname = singleplayerlist[0][3]
                                        if(name5 == singlename):
                                                irc.error("Character {0} is already logged in on PlayBotSingle".format(name5))
                                                charcount = 4
                                        if(netname5 == singlenetname):
                                                irc.error("Character {0} is already logged in on PlayBotSingle".format(singlename))
                                                charcount = 4
                                except IndexError:
                                        irc.reply("No Players Logged in on PlayBotSingle", private=True)
                if charcount == 5:
                        if rawstatsmode is True or rawstatsswitch is True:
                                self.bootopcheck(irc, 5)

                        if(netname5 != netname and netname5 != netname2 and netname5 != netname3 and netname5 != netname4 and name5 != name and name5 != name2 and name5 != name3 and name5 != name4):
                                char5 = True                    
                                self.usecommand(irc, "login {0} {1}".format(name5, pswd5), 5)
                                if autostartmode is True:
                                    self.configwrite2()
                                self.multiwrite(irc)
                        if((netname5 != netname and netname5 != netname2 and netname5 != netname3 and netname5 != netname4) and (name5 == name or name5 == name2 or name5 == name3 or name5 == name4)):
                                irc.error("Character {0} is already logged in".format(name5))
                                charcount = 4
                                
                        if(netname5 == netname):
                                if(supynick5 != supynick):
                                        char5 = True
                                        self.usecommand(irc, "login {0} {1}".format(name5, pswd5), 5 )
                                        if autostartmode is True:
                                            self.configwrite2()
                                        self.multiwrite(irc)
                                if(supynick5 == supynick):
                                        irc.error("Character {0} is already logged in".format(name))
                                        charcount = 4
                        if(netname5 == netname2):
                                if(supynick5 != supynick2):
                                        char5 = True
                                        self.usecommand(irc, "login {0} {1}".format(name5, pswd5), 5 )
                                        if autostartmode is True:
                                            self.configwrite2()
                                        self.multiwrite(irc)
                                if(supynick5 == supynick2):
                                        irc.error("Character {0} is already logged in".format(name2))
                                        charcount = 4
                        if(netname5 == netname3):
                                if(supynick5 != supynick3):
                                        char5 = True
                                        self.usecommand(irc, "login {0} {1}".format(name5, pswd5), 5 )
                                        if autostartmode is True:
                                            self.configwrite2()
                                        self.multiwrite(irc)
                                if(supynick5 == supynick3):
                                        irc.error("Character {0} is already logged in".format(name3))
                                        charcount = 4
                        if(netname5 == netname4):
                                if(supynick5 != supynick4):
                                        char5 = True
                                        self.usecommand(irc, "login {0} {1}".format(name5, pswd5), 5 )
                                        if autostartmode is True:
                                            self.configwrite2()
                                        self.multiwrite(irc)
                                if(supynick5 == supynick4):
                                        irc.error("Character {0} is already logged in".format(name4))
                                        charcount = 4
                if charcount == 4:
                        char5 = False
                        netname5 = None
                        supynick5 = None
                        channame5 = None
                        botname5 = None
                        otherIrc5 = None
                        name5 = None
                        pswd5 = None
                        return

        if(charcount >= 1 and charcount <= 5):
            time.sleep(3) # Needed
            self.usecommand(irc, "whoami", charcount)
            self.usecommand(irc, "stats", charcount)
            irc.reply("Player Character {0} has logged in".format(charcount), private=True)                
            self.configcheck(irc)
        if charcount == 1:
            self.loginsettingslist(irc)

        if charcount >= 6:
            irc.error("You can only play with 5 characters")
            charcount = 5

        if rawstatsswitch is True or rawstatsmode is True:
            self.webdata(irc)

        self.main(irc)

    login = wrap(login, [("checkCapability", "admin"), "text"])

    def bootopcheck(self, irc, num):
        global channame
        global channame2
        global channame3
        global channame4
        global channame5
        global botname
        global botname2
        global botname3
        global botname4
        global botname5
        global rawstatsmode
        global rawstatsswitch
        global otherIrc
        global otherIrc2
        global otherIrc3
        global otherIrc4
        global otherIrc5

        if num == 1:
                botnames = botname
                channames = channame
                otherIrcs = otherIrc
        if num == 2:
                botnames = botname2
                channames = channame2
                otherIrcs = otherIrc2
        if num == 3:
                botnames = botname3
                channames = channame3
                otherIrcs = otherIrc3
        if num == 4:
                botnames = botname4
                channames = channame4
                otherIrcs = otherIrc4
        if num == 5:
                botnames = botname5
                channames = channame5
                otherIrcs = otherIrc5
                
        opcheck = False
        chancheck = False
        
        chantest = otherIrcs.state.channels
        for entry in chantest:
                if entry == channames:
                    chancheck = True

        if chancheck is True:
                try:
                        ops = otherIrcs.state.channels[channames].ops
                        halfops = otherIrcs.state.channels[channames].halfops
                        for user in ops:
                            if botnames == user:
                                opcheck = True
                        for user in halfops:
                            if botnames == user:
                                opcheck = True
                except KeyError:
                        self.reply(irc, "Key Error", num)
                if opcheck is False:
                        rawstatsmode = False
                        rawstatsswitch = False
                        self.reply(irc, "GameBot Not Opped Changing to RawPlayers", num)
                        self.configwrite()

    def autostart(self, irc):
        global name
        global pswd
        global name2
        global pswd2
        global name3
        global pswd3
        global name4
        global pswd4
        global name5
        global pswd5
        global netname
        global netname2
        global netname3
        global netname4
        global netname5
        global nickname
        global nickname2
        global nickname3
        global nickname4
        global nickname5
        global channame
        global channame2
        global channame3
        global channame4
        global channame5
        global botname
        global botname2
        global botname3
        global botname4
        global botname5
        global rawstatsmode
        global char1
        global char2
        global char3
        global char4
        global char5
        global charcount
        global rawstatsswitch
        global gameactive
        global otherIrc
        global otherIrc2
        global otherIrc3
        global otherIrc4
        global otherIrc5
        global supynick
        global supynick2
        global supynick3
        global supynick4
        global supynick5
        global customnetworksettings
        global custombotname
        global customchanname
        global customnetworksettings2
        global custombotname2
        global customchanname2
        global customnetworksettings3
        global custombotname3
        global customchanname3
        global customnetworksettings4
        global custombotname4
        global customchanname4
        global customnetworksettings5
        global custombotname5
        global customchanname5
        global Owner
        global Owner2
        global Owner3
        global Owner4
        global Owner5
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
                if(entry[0] == "name2"):
                        name2 = entry[1]
                if(entry[0] == "pswd2"):
                        pswd2 = entry[1]
                if(entry[0] == "nickname2"):
                        nickname2 = entry[1]
                if(entry[0] == "netname2"):
                        netname2 = entry[1]
                if(entry[0] == "name3"):
                        name3 = entry[1]
                if(entry[0] == "pswd3"):
                        pswd3 = entry[1]
                if(entry[0] == "nickname3"):
                        nickname3 = entry[1]
                if(entry[0] == "netname3"):
                        netname3 = entry[1]
                if(entry[0] == "name4"):
                        name4 = entry[1]
                if(entry[0] == "pswd4"):
                        pswd4 = entry[1]
                if(entry[0] == "nickname4"):
                        nickname4 = entry[1]
                if(entry[0] == "netname4"):
                        netname4 = entry[1]
                if(entry[0] == "name5"):
                        name5 = entry[1]
                if(entry[0] == "pswd5"):
                        pswd5 = entry[1]
                if(entry[0] == "nickname5"):
                        nickname5 = entry[1]
                if(entry[0] == "netname5"):
                        netname5 = entry[1]

        if name != None and pswd != None:
                char1 = True
        if name2 != None and pswd2 != None:
                char2 = True
        if name3 != None and pswd3 != None:
                char3 = True
        if name4 != None and pswd4 != None:
                char4 = True
        if name5 != None and pswd5 != None:
                char5 = True

        bootdelay1 = False
        bootdelay2 = False
        bootdelay3 = False
        bootdelay4 = False
        bootdelay5 = False
        if char1 is True:
                try:
                        checkotherIrc = self._getIrc(netname)
                        if checkotherIrc.server == "unset":
                                bootdelay1 = True
                                char1 = False 
                except NameError:
                        bootdelay1 = True
                        char1 = False 
        if char2 is True:
                try:
                        checkotherIrc2 = self._getIrc(netname2)
                        if checkotherIrc2.server == "unset":
                                bootdelay2 = True
                                char2 = False 
                except NameError:
                        bootdelay2 = True
                        char2 = False 
        if char3 is True:
                try:
                        checkotherIrc3 = self._getIrc(netname3)
                        if checkotherIrc3.server == "unset":
                                bootdelay3 = True
                                char3 = False 
                except NameError:
                        bootdelay3 = True
                        char3 = False 
        if char4 is True:
                try:
                        checkotherIrc4 = self._getIrc(netname4)
                        if checkotherIrc4.server == "unset":
                                bootdelay4 = True
                                char4 = False 
                except NameError:
                        bootdelay4 = True
                        char4 = False 
        if char5 is True:
                try:
                        checkotherIrc5 = self._getIrc(netname5)
                        if checkotherIrc5.server == "unset":
                                bootdelay5 = True
                                char5 = False 
                except NameError:
                        bootdelay5 = True
                        char5 = False 

        if bootdelay1 is True or bootdelay2 is True or bootdelay3 is True or bootdelay4 is True or bootdelay5 is True:
                def bootlooppm():
                    self.autostart(irc)
                delayTime = time.time() + 60
                
                try:
                        schedule.addEvent(bootlooppm, delayTime, "bootlooppm")
                except AssertionError:
                        schedule.removeEvent('bootlooppm')
                        schedule.addEvent(bootlooppm, delayTime, "bootlooppm")
                return

        if char1 is False and char2 is False and char3 is False and char4 is False and char5 is False:
                charcount = 0
                gameactive = False
                irc.error("Autostart Failed")
                autostartmode = False
                self.configwrite()
                
        if char1 is True:
                gameactive = True
                irc = world.getIrc(netname)
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
                        self.bootopcheck(irc, 1)

                if(name != None and pswd != None):
                        self.usecommand(irc, "login {0} {1}".format(name, pswd), 1)
                        charcount += 1
                        time.sleep(3) # Needed
                        self.usecommand(irc, "whoami", 1)
                        self.usecommand(irc, "stats", 1)
                        self.reply(irc, "Player Character 1 has logged in", 1)                

        if char2 is True:
                irc = world.getIrc(netname2)
                supynick2 = irc.nick
                Owner2 = irc.getCallback('Owner')
                if customnetworksettings2 is False:
                        if("undernet" in netname2.lower()):
                                channame2 = "#idlerpg"
                                botname2 = "idlerpg"
                        else:
                                channame2 = "#multirpg"
                                botname2 = "multirpg"

                if customnetworksettings2 is True:
                        channame2 = customchanname2
                        botname2 = custombotname2
                otherIrc2 = self._getIrc(netname2)

                if rawstatsmode is True or rawstatsswitch is True:
                        self.bootopcheck(irc, 2)

                if(name2 != None and pswd2 != None):
                        self.usecommand(irc, "login {0} {1}".format(name2, pswd2), 2)
                        charcount += 1
                        time.sleep(3) # Needed
                        self.usecommand(irc, "whoami", 2)
                        self.usecommand(irc, "stats", 2)
                        self.reply(irc, "Player Character 2 has logged in", 2)                
            
        if char3 is True:
                irc = world.getIrc(netname3)
                supynick3 = irc.nick
                Owner3 = irc.getCallback('Owner')
                if customnetworksettings3 is False:
                        if("undernet" in netname3.lower()):
                                channame3 = "#idlerpg"
                                botname3 = "idlerpg"
                        else:
                                channame3 = "#multirpg"
                                botname3 = "multirpg"

                if customnetworksettings3 is True:
                        channame3 = customchanname3
                        botname3 = custombotname3
                otherIrc3 = self._getIrc(netname3)

                if rawstatsmode is True or rawstatsswitch is True:
                        self.bootopcheck(irc, 3)

                if(name3 != None and pswd3 != None):
                        self.usecommand(irc, "login {0} {1}".format(name3, pswd3), 3)
                        charcount += 1
                        time.sleep(3) # Needed
                        self.usecommand(irc, "whoami", 3)
                        self.usecommand(irc, "stats", 3)
                        self.reply(irc, "Player Character 3 has logged in", 3)                

        if char4 is True:
                irc = world.getIrc(netname4)
                supynick4 = irc.nick
                Owner4 = irc.getCallback('Owner')
                if customnetworksettings4 is False:
                        if("undernet" in netname4.lower()):
                                channame4 = "#idlerpg"
                                botname4 = "idlerpg"
                        else:
                                channame4 = "#multirpg"
                                botname4 = "multirpg"

                if customnetworksettings4 is True:
                        channame4 = customchanname4
                        botname4 = custombotname4
                otherIrc4 = self._getIrc(netname4)

                if rawstatsmode is True or rawstatsswitch is True:
                        self.bootopcheck(irc, 4)

                if(name4 != None and pswd4 != None):
                        self.usecommand(irc, "login {0} {1}".format(name4, pswd4), 4)
                        charcount += 1
                        time.sleep(3) # Needed
                        self.usecommand(irc, "whoami", 4)
                        self.usecommand(irc, "stats", 4)
                        self.reply(irc, "Player Character 4 has logged in", 4)                

        if char5 is True:
                irc = world.getIrc(netname5)
                supynick5 = irc.nick
                Owner5 = irc.getCallback('Owner')
                if customnetworksettings5 is False:
                        if("undernet" in netname5.lower()):
                                channame5 = "#idlerpg"
                                botname5 = "idlerpg"
                        else:
                                channame5 = "#multirpg"
                                botname5 = "multirpg"

                if customnetworksettings5 is True:
                        channame5 = customchanname5
                        botname5 = custombotname5
                otherIrc5 = self._getIrc(netname5)

                if rawstatsmode is True or rawstatsswitch is True:
                        self.bootopcheck(irc, 5)

                if(name5 != None and pswd5 != None):
                        self.usecommand(irc, "login {0} {1}".format(name5, pswd5), 5)
                        charcount += 1
                        time.sleep(3) # Needed
                        self.usecommand(irc, "whoami", 5)
                        self.usecommand(irc, "stats", 5)
                        self.reply(irc, "Player Character 5 has logged in", 5)                

        if charcount >= 1 and charcount <= 5:
            self.loginsettingslist(irc)
            self.webdata(irc)
            self.configcheck(irc)
            self.multiwrite(irc)
                        
            if char1 is True and rawstatsmode is False and webworks is True:
                    self.newitemslister(irc, 1, 2)
                    self.newitemslister(irc, 1, 1)
            if char2 is True and rawstatsmode is False and webworks is True:
                    self.newitemslister(irc, 2, 2)
                    self.newitemslister(irc, 2, 1)
            if char3 is True and rawstatsmode is False and webworks is True:
                    self.newitemslister(irc, 3, 2)
                    self.newitemslister(irc, 3, 1)
            if char4 is True and rawstatsmode is False and webworks is True:
                    self.newitemslister(irc, 4, 2)
                    self.newitemslister(irc, 4, 1)
            if char5 is True and rawstatsmode is False and webworks is True:
                    self.newitemslister(irc, 5, 2)
                    self.newitemslister(irc, 5, 1)
            self.main(irc)

    def loginsettingslist(self, irc):
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
            global bottextmode
            global errortextmode
            global intervaltextmode
            global noticetextmode
            global pmtextmode
            global autostartmode
            global loginsettingslister

            if loginsettingslister is True:
                    if autostartmode is True:
                        self.reply(irc, "Autostart Mode Activated.  To turn it off use 'setoption autostart false' command", 1)
                    if bottextmode is True:
                        self.reply(irc, "Bot Text Mode Activated.  To turn it off use 'setoption bottext false' command", 1)
                    if errortextmode is True:
                        self.reply(irc, "Error Text Mode Activated.  To turn it off use 'setoption errortext false' command", 1)
                    if evilmode is True:
                        self.reply(irc, "Evil Mode Activated.  To turn it off use 'setoption evil false' command", 1)
                    if intervaltextmode is True:
                        self.reply(irc, "Interval Text Mode Activated.  To turn it off use 'setoption intervaltext false' command", 1)
                    if itemupgrader is True:
                        self.reply(irc, "Item Upgrader Mode Activated.  To turn it off use 'setoption itemupgrader false' command", 1)
                    if noticetextmode is True:
                        self.reply(irc, "Notices from GameBot Mode Activated.  To turn it off use 'setoption noticetext false' command", 1)
                    if pmtextmode is True:
                        self.reply(irc, "PMs from GameBot Mode Activated.  To turn it off use 'setoption pmtext false' command", 1)
                    if rawstatsmode is True:
                        self.reply(irc, "Rawstats Mode Activated.  To use Rawplayers Mode use 'setoption rawplayers true' command", 1)
                    if rawstatsmode is False:
                        self.reply(irc, "Rawplayers Mode Activated.  To use Rawstats Mode use 'setoption rawstats true' command", 1)
                    if singlefight is True:
                        self.reply(irc, "Single Fight Mode Activated.  To use multiple fight mode use 'setoption singlefight false' command", 1)
                    if singlefight is False:
                        self.reply(irc, "Multiple Fight Mode Activated.  To use single fight mode use 'setoption singlefight true' command", 1)
                    if upgradeall is True:
                        self.reply(irc, "Upgrade All 1 Mode Activated.  To turn it off use 'setoption upgradeall false' command", 1)
                    self.reply(irc, "Current Align Level: {0}.  If you want to change it use 'setoption alignlevel number' command".format(setalign), 1)
                    self.reply(irc, "Current Betmoney: {0}.  If you want to change it use 'setoption betmoney number' command".format(betmoney), 1)
                    self.reply(irc, "Current Engineer Buy Level: {0}.  If you want to change it use 'setoption engineerbuy number' command".format(setengineer), 1)
                    self.reply(irc, "Current Hero Buy Item Score: {0}.  If you want to change it use 'setoption herobuy number' command".format(sethero), 1)
                    self.reply(irc, "Current Item Buy Level: {0}.  If you want to change it use 'setoption itembuy number' command".format(setbuy), 1)
                    self.reply(irc, " ", 1)
                    self.reply(irc, "For a list of PlayBot commands use <bot> playbotmulti help", 1)
                    self.reply(irc, " ", 1)
            self.versionchecker(irc)

    def logoutchar(self, irc, msg, args):
        """takes no arguments

        Logs you out of the PlayBot.
        """
        global charcount
        global char1
        global char2
        global char3
        global char4
        global char5
        global netname
        global netname2
        global netname3
        global netname4
        global netname5
        global networkname
        global networkname2
        global networkname3
        global networkname4
        global networkname5
        global channame
        global channame2
        global channame3
        global channame4
        global channame5
        global botname
        global botname2
        global botname3
        global botname4
        global botname5
        global name
        global name2
        global name3
        global name4
        global name5
        global pswd
        global pswd2
        global pswd3
        global pswd4
        global pswd5
        global gameactive
        global myentry
        global rawmyentry
        global myentry2
        global rawmyentry2
        global myentry3
        global rawmyentry3
        global myentry4
        global rawmyentry4
        global myentry5
        global rawmyentry5
        global ttlfrozen1
        global ttlfrozen2
        global ttlfrozen3
        global ttlfrozen4
        global ttlfrozen5
        global autostartmode
        
        if gameactive is False:
            irc.error("You are not logged in")
        if gameactive is True:
                if charcount == 5:
                        irc.reply("{0} has logged out".format(name5), private=True)
                        char5 = False
                        netname5 = None
                        networkname5 = None
                        channame5 = None
                        botname5 = None
                        name5 = None
                        pswd5 = None
                        myentry5 = None
                        rawmyentry5 = None
                        ttlfrozen5 = 0
                        self.multiwrite(irc)
                if charcount == 4:
                        irc.reply("{0} has logged out".format(name4), private=True)
                        char4 = False
                        netname4 = None
                        networkname4 = None
                        channame4 = None
                        botname4 = None
                        name4 = None
                        pswd4 = None
                        myentry4 = None
                        rawmyentry4 = None
                        ttlfrozen4 = 0        
                        self.multiwrite(irc)
                if charcount == 3:
                        irc.reply("{0} has logged out".format(name3), private=True)
                        char3 = False
                        netname3 = None
                        networkname3 = None
                        channame3 = None
                        botname3 = None
                        name3 = None
                        pswd3 = None
                        myentry3 = None
                        rawmyentry3 = None
                        ttlfrozen3 = 0        
                        self.multiwrite(irc)
                if charcount == 2:
                        irc.reply("{0} has logged out".format(name2), private=True)
                        char2 = False
                        netname2 = None
                        networkname2 = None
                        channame2 = None
                        botname2 = None
                        name2 = None
                        pswd2 = None
                        myentry2 = None
                        rawmyentry2 = None
                        ttlfrozen2 = 0        
                        self.multiwrite(irc)
                if charcount == 1:
                        irc.reply("{0} has logged out".format(name), private=True)
                        char1 = False
                        netname = None
                        networkname = None
                        channame = None
                        botname = None
                        name = None
                        pswd = None
                        myentry = None
                        rawmyentry = None
                        ttlfrozen1 = 0        
                        gameactive = False
                        try:
                                schedule.removeEvent('looppm')
                        except KeyError:
                                irc.error("You are not logged in")
                        self.multieraser(irc)

        if charcount == 0:
            irc.error("All Characters have already been Logged Out")
        if(charcount >= 1 and charcount <= 5):
            charcount -= 1
            if autostartmode is True:
                    self.configwrite2()
        if charcount == 0:
            if autostartmode is True:
                    autostartmode = False
                    self.configwrite()

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

    def multiwrite(self, irc):
        global name
        global name2
        global name3
        global name4
        global name5
        global char1
        global char2
        global char3
        global char4
        global char5
        global netname
        global netname2
        global netname3
        global netname4
        global netname5
      
        playerListM = []
        if char1 is True:
                playerListM.append( ( "name", name, "netname", netname ) )
        if char2 is True:
                playerListM.append( ( "name2", name2, "netname2", netname2 ) )
        if char3 is True:
                playerListM.append( ( "name3", name3, "netname3", netname3 ) )
        if char4 is True:
                playerListM.append( ( "name4", name4, "netname4", netname4 ) )
        if char5 is True:
                playerListM.append( ( "name5", name5, "netname5", netname5 ) )
        f = open(filename4,"wb")
        pickle.dump(playerListM,f)
        f.close()

    def multieraser(self, irc):
        playerListM = []
        f = open(filename4,"wb")
        pickle.dump(playerListM,f)
        f.close()
        irc.reply("MultiRPG PlayerListM Erased", private=True)

    def pmultierase(self, irc, msg, args):
        """takes no arguments

        Erases playerList file
        """
        self.multieraser(irc)

    pmultierase = wrap(pmultierase, [("checkCapability", "admin")])

    def singleread(self, irc):
        try:
                f = open(filename3,"rb")
                playerListS = pickle.load(f)
                f.close()
        except:
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
        global nickname5
        global gameactive
        global char1
        global char2
        global char3
        global char4
        global char5

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
            if num == 5 and char5 is True:
                nickname5 = msg.nick
                s = format(_('nick updated to {0}'.format(nickname5)))
                irc.reply(s, private=True)
        if gameactive is False:
            irc.error("You are not logged in")

    updatenick = wrap(updatenick, [("checkCapability", "admin"), "positiveInt"])

    def jump(self, irc, msg, args, network, num):
        """<network> <charnum>

        Jump to another network
        """
        global gameactive
        global char1
        global char2
        global char3
        global char4
        global char5
        global netname
        global netname2
        global netname3
        global netname4
        global netname5
        global otherIrc
        global otherIrc2
        global otherIrc3
        global otherIrc4
        global otherIrc5
        global nolag
        global nolag2
        global nolag3
        global nolag4
        global nolag5
        global servername
        global servername2
        global servername3
        global servername4
        global servername5
        global port
        global port2
        global port3
        global port4
        global port5
        global ssl
        global ssl2
        global ssl3
        global ssl4
        global ssl5
        global networkname
        global networkname2
        global networkname3
        global networkname4
        global networkname5
        global networklist
        global charcount
        global Owner
        global Owner2
        global Owner3
        global Owner4
        global Owner5
        global jumpnetwork
        global jumpnetwork2
        global jumpnetwork3
        global jumpnetwork4
        global jumpnetwork5
        global customnetworksettings
        global customnetworksettings2
        global customnetworksettings3
        global customnetworksettings4
        global customnetworksettings5
        global ZNC1
        global ZNC2
        global ZNC3
        global ZNC4
        global ZNC5
        global bothostmask1
        global bothostmask2
        global bothostmask3
        global bothostmask4
        global bothostmask5
        global connectfail1
        global connectfail2
        global connectfail3
        global connectfail4
        global connectfail5
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

                if(num == 1 and char1 is True):
                    if ZNC1 is False and customnetworksettings is False:
                            for entry in networklist:
                                        if (network == entry[0].lower() and entry[3] == 1):
                                            servername = entry[1]
                                            nolag = entry[2]
                                            port = entry[4]
                                            ssl = entry[5]
                                            bothostmask1 = entry[6]
                                            networklistcheck = True                                
                            if netcheck is True:
                                    networkcheck = False
                                    if charcount == 1:
                                            if(network != netname.lower()):
                                                    networkcheck = True
                                    if charcount == 2:
                                            if(network != netname.lower() and network != netname2.lower()):
                                                    networkcheck = True
                                    if charcount == 3:
                                            if(network != netname.lower() and network != netname2.lower() and network != netname3.lower()):
                                                    networkcheck = True
                                    if charcount == 4:
                                            if(network != netname.lower() and network != netname2.lower() and network != netname3.lower() and network != netname4.lower()):
                                                    networkcheck = True
                                    if charcount == 5:
                                            if(network != netname.lower() and network != netname2.lower() and network != netname3.lower() and network != netname4.lower() and network != netname5.lower()):
                                                    networkcheck = True
                                    if networkcheck is False:
                                            irc.error("You are already playing on {0}".format(network))
                                    if networkcheck is True and servererror is False:
                                            netname = network
                                            irc.reply("Network 1 Changed to {0}".format(netname), private=True)
                                            otherIrc = checkotherIrc
                                            networkname = network
                                            networklistcheck = True                                
                                            jumpnetwork = True
                                            connectfail1 = 0
                                            if autostartmode is True:
                                                    self.configwrite2()
                                    if networkcheck is True and servererror is True:
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
                    if ZNC1 is True or customnetworksettings is True:
                            irc.error("ZNC or Custom Network Settings are on")
                if(num == 2 and char2 is True):
                    if ZNC2 is False and customnetworksettings2 is False:
                            networklistcheck = False
                            for entry in networklist:
                                        if (network == entry[0].lower() and entry[3] == 1):
                                            servername2 = entry[1]
                                            nolag2 = entry[2]
                                            port2 = entry[4]
                                            ssl2 = entry[5]
                                            bothostmask2 = entry[6]
                                            networklistcheck = True                                
                            if netcheck is True:
                                    networkcheck = False
                                    if charcount == 2:
                                            if(network != netname.lower() and network != netname2.lower()):
                                                    networkcheck = True
                                    if charcount == 3:
                                            if(network != netname.lower() and network != netname2.lower() and network != netname3.lower()):
                                                    networkcheck = True
                                    if charcount == 4:
                                            if(network != netname.lower() and network != netname2.lower() and network != netname3.lower() and network != netname4.lower()):
                                                    networkcheck = True
                                    if charcount == 5:
                                            if(network != netname.lower() and network != netname2.lower() and network != netname3.lower() and network != netname4.lower() and network != netname5.lower()):
                                                    networkcheck = True
                                    if networkcheck is False:
                                            irc.error("You are already playing on {0}".format(network))
                                    if networkcheck is True and servererror is False:
                                            netname2 = network
                                            irc.reply("Network 2 Changed to {0}".format(netname2), private=True)
                                            otherIrc2 = checkotherIrc
                                            networkname2 = network
                                            networklistcheck = True                                
                                            jumpnetwork2 = True
                                            connectfail2 = 0
                                            if autostartmode is True:
                                                    self.configwrite2()
                                    if networkcheck is True and servererror is True:
                                            irc.error("Server Error, Network not connected")
                            if netcheck is False and networklistcheck is True:
                                serverPort = (servername2, port2)
                                newIrc = Owner2._connect(network, serverPort=serverPort,
                                                        password="", ssl=ssl2)
                                conf.supybot.networks().add(network)
                                assert newIrc.callbacks is irc.callbacks, 'callbacks list is different'
                                irc.replySuccess(_('Connection to %s initiated.') % network)
                                otherIrc2 = self._getIrc(network)
                                netname2 = network
                                networkname2 = network
                                jumpnetwork2 = True
                                if autostartmode is True:
                                    self.configwrite2()
                    if ZNC2 is True or customnetworksettings2 is True:
                            irc.error("ZNC or Custom Network Settings are on")
                if(num == 3 and char3 is True):
                    if ZNC3 is False and customnetworksettings3 is False:
                            networklistcheck = False
                            for entry in networklist:
                                        if (network == entry[0].lower() and entry[3] == 1):
                                            servername3 = entry[1]
                                            nolag3 = entry[2]
                                            port3 = entry[4]
                                            ssl3 = entry[5]
                                            bothostmask3 = entry[6]
                                            networklistcheck = True                                
                            if netcheck is True:
                                    networkcheck = False
                                    if charcount == 3:
                                            if(network != netname.lower() and network != netname2.lower() and network != netname3.lower()):
                                                    networkcheck = True
                                    if charcount == 4:
                                            if(network != netname.lower() and network != netname2.lower() and network != netname3.lower() and network != netname4.lower()):
                                                    networkcheck = True
                                    if charcount == 5:
                                            if(network != netname.lower() and network != netname2.lower() and network != netname3.lower() and network != netname4.lower() and network != netname5.lower()):
                                                    networkcheck = True
                                    if networkcheck is False:
                                            irc.error("You are already playing on {0}".format(network))
                                    if networkcheck is True and servererror is False:
                                            netname3 = network
                                            irc.reply("Network 3 Changed to {0}".format(netname3), private=True)
                                            otherIrc3 = checkotherIrc
                                            networkname3 = network
                                            networklistcheck = True                                
                                            jumpnetwork3 = True
                                            connectfail3 = 0
                                            if autostartmode is True:
                                                    self.configwrite2()
                                    if networkcheck is True and servererror is True:
                                            irc.error("Server Error, Network not connected")
                            if netcheck is False and networklistcheck is True:
                                serverPort = (servername3, port3)
                                newIrc = Owner3._connect(network, serverPort=serverPort,
                                                        password="", ssl=ssl3)
                                conf.supybot.networks().add(network)
                                assert newIrc.callbacks is irc.callbacks, 'callbacks list is different'
                                irc.replySuccess(_('Connection to %s initiated.') % network)
                                otherIrc3 = self._getIrc(network)
                                netname3 = network
                                networkname3 = network
                                jumpnetwork3 = True
                                if autostartmode is True:
                                    self.configwrite2()
                    if ZNC3 is True or customnetworksettings3 is True:
                            irc.error("ZNC or Custom Network Settings are on")
                if(num == 4 and char4 is True):
                    if ZNC4 is False and customnetworksettings4 is False:
                            networklistcheck = False
                            for entry in networklist:
                                        if (network == entry[0].lower() and entry[3] == 1):
                                            servername4 = entry[1]
                                            nolag4 = entry[2]
                                            port4 = entry[4]
                                            ssl4 = entry[5]
                                            bothostmask4 = entry[6]
                                            networklistcheck = True                                
                            if netcheck is True:
                                    networkcheck = False
                                    if charcount == 4:
                                            if(network != netname.lower() and network != netname2.lower() and network != netname3.lower() and network != netname4.lower()):
                                                    networkcheck = True
                                    if charcount == 5:
                                            if(network != netname.lower() and network != netname2.lower() and network != netname3.lower() and network != netname4.lower() and network != netname5.lower()):
                                                    networkcheck = True
                                    if networkcheck is False:
                                            irc.error("You are already playing on {0}".format(network))
                                    if networkcheck is True and servererror is False:
                                            netname4 = network
                                            irc.reply("Network 4 Changed to {0}".format(netname4), private=True)
                                            otherIrc4 = checkotherIrc
                                            networkname4 = network
                                            networklistcheck = True                                
                                            jumpnetwork4 = True
                                            connectfail4 = 0
                                            if autostartmode is True:
                                                    self.configwrite2()
                                    if networkcheck is True and servererror is True:
                                            irc.error("Server Error, Network not connected")
                            if netcheck is False and networklistcheck is True:
                                serverPort = (servername4, port4)
                                newIrc = Owner4._connect(network, serverPort=serverPort,
                                                        password="", ssl=ssl4)
                                conf.supybot.networks().add(network)
                                assert newIrc.callbacks is irc.callbacks, 'callbacks list is different'
                                irc.replySuccess(_('Connection to %s initiated.') % network)
                                otherIrc4 = self._getIrc(network)
                                netname4 = network
                                networkname4 = network
                                jumpnetwork4 = True
                                if autostartmode is True:
                                    self.configwrite2()
                    if ZNC4 is True or customnetworksettings4 is True:
                            irc.error("ZNC or Custom Network Settings are on")
                if(num == 5 and char5 is True):
                    if ZNC5 is False and customnetworksettings5 is False:
                            networklistcheck = False
                            for entry in networklist:
                                        if (network == entry[0].lower() and entry[3] == 1):
                                            nolag5 = entry[2]
                                            servername5 = entry[1]
                                            port5 = entry[4]
                                            ssl5 = entry[5]
                                            bothostmask5 = entry[6]
                                            networklistcheck = True                                
                            if netcheck is True:
                                    networkcheck = False
                                    if(network != netname.lower() and network != netname2.lower() and network != netname3.lower() and network != netname4.lower() and network != netname5.lower()):
                                            networkcheck = True
                                    if networkcheck is False:
                                            irc.error("You are already playing on {0}".format(network)) 
                                    if networkcheck is True and servererror is False:
                                            netname5 = network
                                            irc.reply("Network 5 Changed to {0}".format(netname5), private=True)
                                            otherIrc5 = checkotherIrc
                                            networkname5 = network
                                            networklistcheck = True
                                            jumpnetwork5 = True
                                            connectfail5 = 0
                                            if autostartmode is True:
                                                    self.configwrite2()
                                    if networkcheck is True and servererror is True:
                                            irc.error("Server Error, Network not connected")
                            if netcheck is False and networklistcheck is True:
                                serverPort = (servername5, port5)
                                newIrc = Owner5._connect(network, serverPort=serverPort,
                                                        password="", ssl=ssl5)
                                conf.supybot.networks().add(network)
                                assert newIrc.callbacks is irc.callbacks, 'callbacks list is different'
                                irc.replySuccess(_('Connection to %s initiated.') % network)
                                otherIrc5 = self._getIrc(network)
                                netname5 = network
                                networkname5 = network
                                jumpnetwork5 = True
                                if autostartmode is True:
                                    self.configwrite2()
                    if ZNC5 is True or customnetworksettings5 is True:
                            irc.error("ZNC or Custom Network Settings are on")
                if networklistcheck is False:
                        if num <= charcount:
                                irc.error("Network not on the list")
                        if num > charcount:
                                irc.error("Player {0} is not logged in".format(num))
        if gameactive is False:
            irc.error("You are not logged in")

    jump = wrap(jump, [("checkCapability", "admin"), "something", "positiveInt"])

    def configcheck(self, irc):
        global channame
        global channame2
        global channame3
        global channame4
        global channame5
        global char1
        global char2
        global char3
        global char4
        global char5
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
        chanlist = []
        if char1 is True:
                chanlist.append(channame)
        if char2 is True:
                chanlist.append(channame2)
        if char3 is True:
                chanlist.append(channame3)
        if char4 is True:
                chanlist.append(channame4)
        if char5 is True:
                chanlist.append(channame5)

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

                for entry in chanlist:
                        zombiecheck = False
                        for (channel, c) in ircdb.channels.items():
                                if c.lobotomized:
                                    if channel == entry:
                                                zombiecheck = True
                        if zombiecheck is False:
                                    c = ircdb.channels.getChannel(entry)
                                    c.lobotomized = True
                                    ircdb.channels.setChannel(entry, c)
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
        if autoconfig == 2:
                if commandflood is False:
                        conf.supybot.abuse.flood.command.set("True")
                        configchange = True
                if notcommandflood is False:
                        conf.supybot.abuse.flood.command.invalid.set("True")
                        configchange = True
                if notcommand is False:
                        conf.supybot.reply.whenNotCommand.set("True")
                        configchange = True
                for entry in chanlist:
                        zombiecheck = False
                        for (channel, c) in ircdb.channels.items():
                                if c.lobotomized:
                                    if channel == entry:
                                                zombiecheck = True
                        if zombiecheck is True:
                                    c = ircdb.channels.getChannel(entry)
                                    c.lobotomized = False
                                    ircdb.channels.setChannel(entry, c)
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

    def cmd5(self, irc, msg, args, text):
        """<text>

        Issue manual commands for the game
        """
        global gameactive
        global char5

        if(gameactive is True and char5 is True):
            try:
                    cmdtext = text
            except IndexError:
                    irc.error("To do manual commands use cmd5 text")
            self.usecommand(irc, "{0}".format(cmdtext), 5)
        if gameactive is False:
            irc.error("You are not logged in")

    cmd5 = wrap(cmd5, [("checkCapability", "admin"), "text"])
    
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
        irc.reply("Erase PlayerList            - pmultierase", private=True)
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
        irc.reply("Jump Network                - jump network charnumber", private=True)
        irc.reply("Log In Char                 - login charname password", private=True)
        irc.reply("Log Out Char                - logoutchar", private=True)
        irc.reply("Log Out Game                - logoutgame charnumber", private=True)
        irc.reply("Manual Command Char1        - cmd command", private=True)
        irc.reply("Manual Command Char2        - cmd2 command", private=True)
        irc.reply("Manual Command Char3        - cmd3 command", private=True)
        irc.reply("Manual Command Char4        - cmd4 command", private=True)
        irc.reply("Manual Command Char5        - cmd5 command", private=True)
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
        irc.reply("Update Nick                 - updatenick charnumber", private=True)
        irc.reply("Upgrade All 1 Mode Off      - setoption upgradeall false", private=True)
        irc.reply("Upgrade All 1 Mode On       - setoption upgradeall true", private=True)
        irc.reply("Version Checker             - versioncheck", private=True)
        irc.reply(" ", private=True)
        irc.reply("If you want more information about a command use <supybot> help playbotmulti <command> - ie /msg DudeRuss help playbotmulti settings", private=True)

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
        global char1
        global char2
        global char3
        global char4
        global char5
        global name
        global name2
        global name3
        global name4
        global name5
        global rawstatsmode
        global gameactive
        global bottextmode
        global errortextmode
        global intervaltextmode
        global noticetextmode
        global pmtextmode
        global autostartmode
        global netname
        global netname2
        global netname3
        global netname4
        global netname5

        if gameactive is True:
            irc.reply("Playbot Settings List", private=True)
            irc.reply(" ", private=True)
            irc.reply("Align Level - {0}          Autostart Mode - {1}".format(setalign, autostartmode), private=True)
            irc.reply("Bet Money - {0}            Bot Text Mode - {1}".format(betmoney, bottextmode), private=True)
            irc.reply("Engineer Buy Level - {0}   Error Text Mode - {1}".format(setengineer, errortextmode), private=True)
            irc.reply("Evil Mode - {0}            GameBot Notices Mode - {1}".format(evilmode, noticetextmode), private=True)
            irc.reply("GameBot PMs Mode - {0}     Hero Buy ItemScore - {1}".format(pmtextmode, sethero), private=True)
            irc.reply("Interval Text Mode - {0}   Item Buy Level - {1}".format(intervaltextmode, setbuy), private=True)
            irc.reply("Item Upgrader Mode - {0}".format(itemupgrader), private=True)
            irc.reply("Player Character 1 - {0}, {1}.  Network {2}  Player Character 2 - {3}, {4}.  Network {5}".format(char1, name, netname, char2, name2, netname2), private=True)
            irc.reply("Player Character 3 - {0}, {1}.  Network {2}  Player Character 4 - {3}, {4}.  Network {5}".format(char3, name3, netname3, char4, name4, netname4), private=True)
            irc.reply("Player Character 5 - {0}, {1}.  Network {2}".format(char5, name5, netname5), private=True)
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
        global char1
        global char2
        global char3
        global char4
        global char5
        global name
        global name2
        global name3
        global name4
        global name5
        global gameactive
        
        if gameactive is True:
            if char1 is True:
                self.reply(irc, "{0}'s Status".format(name), 1)
                self.reply(irc, " ", 1)
                self.characterstats(irc, 1)
            if char2 is True:
                self.reply(irc, "{0}'s Status".format(name2), 2)
                self.reply(irc, " ", 2)
                self.characterstats(irc, 2)
            if char3 is True:
                self.reply(irc, "{0}'s Status".format(name3), 3)
                self.reply(irc, " ", 3)
                self.characterstats(irc, 3)
            if char4 is True:
                self.reply(irc, "{0}'s Status".format(name4), 4)
                self.reply(irc, " ", 4)
                self.characterstats(irc, 4)
            if char5 is True:
                self.reply(irc, "{0}'s Status".format(name5), 5)
                self.reply(irc, " ", 5)
                self.characterstats(irc, 5)
        if gameactive is False:
            irc.error("You are not logged in")

    status = wrap(status, [("checkCapability", "admin")])

    def characterstats(self, irc, num):
        global rawstatsmode
        global myentry
        global myentry2
        global myentry3
        global myentry4
        global myentry5
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

        self.getitems2(num)

        if num == 1:
            myentrys = myentry
        if num == 2:
            myentrys = myentry2
        if num == 3:
            myentrys = myentry3
        if num == 4:
            myentrys = myentry4
        if num == 5:
            myentrys = myentry5

        if rawstatsmode is True and webworks is True:
            ranknumber = myentrys[1]
        if rawstatsmode is False:
            ranknumber = rankplace

        if webworks is True:
            self.reply(irc, "Rank: {0}".format(ranknumber), num)
        self.reply(irc, "Level: {0}     TTL: {1} secs    Item Score: {2}    Team No: {3}".format(level, ttl, mysum, team), num)
        if(level >= 10):
            self.reply(irc, "Attack Recovery: {0} secs".format(atime), num)
        if(level < 10):
            self.reply(irc, "Creep Attacks Start at Level 10", num)
        if(level >= 35):
            self.reply(irc, "Challenge Recovery: {0} secs".format(ctime), num)
        if(level < 35):
            self.reply(irc, "Manual Challenges Start at Level 35", num)
        if(level >= 40):
            self.reply(irc, "Slay Recovery: {0} secs".format(stime), num)
        if(level < 40):
            self.reply(irc, "Slaying Monsters Start at Level 40", num)
        self.reply(irc, "Power Potions: {0}".format(powerpots), num)
        if(level >= 10):
            self.reply(irc, "Fights: {0} of 5".format(fights), num)
        if(level < 10):
            self.reply(irc, "Fights Start at Level 10", num)
        if(level >= 30):
            self.reply(irc, "Bets: {0} of 5".format(bets), num)
        if(level < 30):
            self.reply(irc, "Bets Start at Level 30", num)
        if hero == 0:
            self.reply(irc, "Hero: No", num)
        if hero == 1:
            self.reply(irc, "Hero: Yes", num)
        self.reply(irc, "Hero Level: {0}       Engineer Level: {1}".format(hlvl, elvl), num)
        if eng == 0:
            self.reply(irc, "Engineer: No", num)
        if eng == 1:
            self.reply(irc, "Engineer: Yes", num)
        self.reply(irc, "Gold in Hand: {0}     Gold in the Bank: {1}".format(gold, bank), num)

    def items(self, irc, msg, args):
        """takes no arguments

        Gives a list of character item scores
        """
        global char1
        global char2
        global char3
        global char4
        global char5
        global name
        global name2
        global name3
        global name4
        global name5
        global gameactive

        if gameactive is True:
            if char1 is True:
                self.reply(irc, "{0}'s Items List".format(name), 1)
                self.reply(irc, " ", 1)
                self.characteritems(irc, 1)
            if char2 is True:
                self.reply(irc, "{0}'s Items List".format(name2), 2)
                self.reply(irc, " ", 2)
                self.characteritems(irc, 2)
            if char3 is True:
                self.reply(irc, "{0}'s Items List".format(name3), 3)
                self.reply(irc, " ", 3)
                self.characteritems(irc, 3)
            if char4 is True:
                self.reply(irc, "{0}'s Items List".format(name4), 4)
                self.reply(irc, " ", 4)
                self.characteritems(irc, 4)
            if char5 is True:
                self.reply(irc, "{0}'s Items List".format(name5), 5)
                self.reply(irc, " ", 5)
                self.characteritems(irc, 5)
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
        global mysum

        self.getitems2(num)
        self.reply(irc, "Amulet: {0}  Charm: {1}  Helm: {2}  Boots: {3}  Gloves: {4}".format(amulet, charm, helm, boots, gloves), num)
        self.reply(irc, "Ring: {0}  Leggings: {1}  Shield: {2}  Tunic: {3}  Weapon: {4}".format(ring, leggings, shield, tunic, weapon), num)
        self.reply(irc, "Total Item Score: {0}".format(mysum), num)

    def bestall(self, irc, msg, args):
        """takes no arguments

        Shows Best Bet/Fight/Attack/Slay
        """
        global gameactive
        global name
        global name2
        global name3
        global name4
        global name5
        global webworks
        global char1
        global char2
        global char3
        global char4
        global char5
        
        if gameactive is True:
                self.webdata(irc)
                if webworks is True:
                        if char1 is True:
                                self.reply(irc, "Best All for {0}".format(name),1)
                                self.reply(irc, " ",1)
                                self.bestallmulti(irc, 1)
                        if char2 is True:
                                self.reply(irc, "Best All for {0}".format(name2),2)
                                self.reply(irc, " ",2)
                                self.bestallmulti(irc, 2)
                        if char3 is True:
                                self.reply(irc, "Best All for {0}".format(name3),3)
                                self.reply(irc, " ",3)
                                self.bestallmulti(irc, 3)
                        if char4 is True:
                                self.reply(irc, "Best All for {0}".format(name4),4)
                                self.reply(irc, " ",4)
                                self.bestallmulti(irc, 4)
                        if char5 is True:
                                self.reply(irc, "Best All for {0}".format(name5),5)
                                self.reply(irc, " ",5)
                                self.bestallmulti(irc, 5)
        if gameactive is False:
                irc.error("You are not logged in")

    bestall = wrap(bestall, [("checkCapability", "admin")])

    def bestallmulti(self, irc, num):
        global fightSum1
        global fightSum2
        global fightSum3
        global fightSum4
        global fightSum5
        global rankplace
        global name
        global name2
        global name3
        global name4
        global name5
        global charcount
        global myentry
        global myentry2
        global myentry3
        global myentry4
        global myentry5
        global rawstatsmode
        global webworks
        global level

        if charcount >= 2:
                self.getitems2(num)
        if num == 1:
                fightsumlist = fightSum1
                names = name
                myentrys = myentry
        if num == 2:
                fightsumlist = fightSum2
                names = name2
                myentrys = myentry2
        if num == 3:
                fightsumlist = fightSum3
                names = name3
                myentrys = myentry3
        if num == 4:
                fightsumlist = fightSum4
                names = name4
                myentrys = myentry4
        if num == 5:
                fightsumlist = fightSum5
                names = name5
                myentrys = myentry5

        if rawstatsmode is True and webworks is True:
                ranknumber = myentrys[1]
        if rawstatsmode is False:
                ranknumber = rankplace
        self.newitemslister(irc,num,1)
        self.newitemslister(irc,num,2)
        if(level < 10):
                self.reply(irc, "Creep Attacks Start at Level 10", num)
        if(level >= 10):
                creep = self.bestattack(num)
                self.reply(irc, "BestAttack: {0}".format(creep), num)
        if(level < 40):
                self.reply(irc, "Slaying Monsters Start at Level 40", num)
        if(level >= 40):
                monster = self.bestslay(num)
                self.reply(irc, "BestSlay: {0}".format(monster), num)
        if(level < 30):
                self.reply(irc, "Bets Start at Level 30", num)
        if(level >= 30):
                bbet = self.bestbet(num)
                self.reply(irc, "BestBet {0} {1}".format( bbet[0][0], bbet[1][0] ), num)
        if(level < 10):
                self.reply(irc, "Fights Start at Level 10", num)
        if(level >= 10):
                ufight = self.testfight(num)
                try:
                        ufightcalc = fightsumlist / ufight[2]
                except ZeroDivisionError:
                        ufightcalc = 0
                self.reply(irc, "Best Fight for Rank {0}: {1} [{2}]  Opponent: Rank {3}: {4} [{5}], Odds {6}".format(ranknumber, names, int(fightsumlist), ufight[5], ufight[0], int(ufight[2]), ufightcalc), num)

    def webdata(self, irc):
        global playerlist
        global name
        global name2
        global name3
        global name4
        global name5
        global webworks
        global myentry
        global myentry2
        global myentry3
        global myentry4
        global myentry5
        global rawplayers3
        global char1
        global char2
        global char3
        global char4
        global char5
        global webfail
        global python3
        global botcheck1
        global botcheck2
        global botcheck3
        global botcheck4
        global botcheck5
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
                        self.replymulti(irc, playbottext + " - Could not access {0}".format(website))
                webworks = False

        # build list for player records
        if(rawplayers3 is None):
            if errortextmode is True:
                        self.replymulti(irc, playbottext + " - Could not access {0}, unknown error.".format(website) )
            webworks = False
        else:
            playerlist = rawplayers3.split("\n")
            playerlist = playerlist[:-1]

        # extract our player's record and make list
        if webworks is True:
            if char1 is True:
                for entry in playerlist:
                    entry = entry.split(" ")
                    try:
                        if(entry[3] == name):
                            myentry = entry
                            webfail = 0
                    except IndexError:
                        webworks = False
            if char2 is True:
                for entry in playerlist:
                    entry = entry.split(" ")
                    try:
                        if(entry[3] == name2):
                            myentry2 = entry
                            webfail = 0
                    except IndexError:
                        webworks = False
            if char3 is True:
                for entry in playerlist:
                    entry = entry.split(" ")
                    try:
                        if(entry[3] == name3):
                            myentry3 = entry
                            webfail = 0
                    except IndexError:
                        webworks = False
            if char4 is True:
                for entry in playerlist:
                    entry = entry.split(" ")
                    try:
                        if(entry[3] == name4):
                            myentry4 = entry
                            webfail = 0
                    except IndexError:
                        webworks = False
            if char5 is True:
                for entry in playerlist:
                    entry = entry.split(" ")
                    try:
                        if(entry[3] == name5):
                            myentry5 = entry
                            webfail = 0
                    except IndexError:
                        webworks = False
        if webworks is False:
                if botcheck1 is True or botcheck2 is True or botcheck3 is True or botcheck4 is True or botcheck5 is True:
                        webfail += 1
                        webnum += 1
        if webfail >= 1:
                if botcheck1 is True or botcheck2 is True or botcheck3 is True or botcheck4 is True or botcheck5 is True:
                    if errortextmode is True:
                            self.replymulti(irc, playbottext + " - Webfail: {0}".format(webfail))
        if webnum > 2:
                webnum = 1

    def newitemslister(self, irc, num, num2):
        global name
        global name2
        global name3
        global name4
        global name5
        global webworks
        global char1
        global char2
        global char3
        global char4
        global char5
        global itemslists
        global playerlist
        
        global newlist
        global newlist2
        global newlist3
        global newlist4
        global newlist5
        global team
        global firstalign

        if num2 == 1:
                itemslists = []
        if num2 == 2:
                if num == 1:
                    newlist = []
                    names = name
                if num == 2:
                    newlist2 = []
                    names = name2
                if num == 3:
                    newlist3 = []
                    names = name3
                if num == 4:
                    newlist4 = []
                    names = name4
                if num == 5:
                    newlist5 = []
                    names = name5

        now = int( time.time() )
        if webworks is True:
                for player in playerlist:
                        player = player.split(" ")
                        # extract players sum
                        rankIdx = None
                        teamIdx = None
                        ttlIdx = None
                        atimeIdx = None
                        ctimeIdx = None
                        stimeIdx = None
                        sumIdx = None
                        levelIdx = None

                        amuletIdx = None
                        charmIdx = None
                        helmIdx = None
                        bootsIdx = None
                        glovesIdx = None
                        ringIdx = None
                        leggingsIdx = None
                        shieldIdx = None
                        tunicIdx = None
                        weaponIdx = None

                        powerpotsIdx = None
                        fightsIdx = None
                        betsIdx = None
                        heroIdx = None
                        hlevelIdx = None
                        engIdx = None
                        elvlIdx = None
                        goldIdx = None
                        bankIdx = None
                        alignIdx = None

                        for index, entry in enumerate(player):
                                if(entry == "rank"):
                                        rankIdx = index + 1
                                if(entry == "team"):
                                        teamIdx = index + 1
                                if(entry == "ttl"):
                                        ttlIdx = index + 1
                                if(entry == "regentm"):
                                        atimeIdx = index + 1
                                if(entry == "challengetm"):
                                        ctimeIdx = index + 1
                                if(entry == "slaytm"):
                                        stimeIdx = index + 1
                                if(entry == "sum"):
                                        sumIdx = index + 1
                                if(entry == "level"):
                                        levelIdx = index + 1

                                if(entry == "amulet"):
                                        amuletIdx = index + 1
                                if(entry == "charm"):
                                        charmIdx = index + 1
                                if(entry == "helm"):
                                        helmIdx = index + 1
                                if(entry == "boots"):
                                        bootsIdx = index + 1
                                if(entry == "gloves"):
                                        glovesIdx = index + 1
                                if(entry == "ring"):
                                        ringIdx = index + 1
                                if(entry == "leggings"):
                                        leggingsIdx = index + 1
                                if(entry == "shield"):
                                        shieldIdx = index + 1
                                if(entry == "tunic"):
                                        tunicIdx = index + 1
                                if(entry == "weapon"):
                                        weaponIdx = index + 1

                                if(entry == "powerpots"):
                                        powerpotsIdx = index + 1
                                if(entry == "fights"):
                                        fightsIdx = index + 1
                                if(entry == "bets"):
                                        betsIdx = index + 1
                                if(entry == "hero"):
                                        heroIdx = index + 1
                                if(entry == "hlevel"):
                                        hlevelIdx = index + 1
                                if(entry == "engineer"):
                                        engIdx = index + 1
                                if(entry == "englevel"):
                                        elvlIdx = index + 1
                                if(entry == "gold"):
                                        goldIdx = index + 1
                                if(entry == "bank"):
                                        bankIdx = index + 1

                                if(entry == "align"):
                                        alignIdx = index + 1
                                  
                        # if this player is online
                        if(player[15] == "1"):
                                rank = int(player[rankIdx])
                                teamgroup = int(player[teamIdx])
                                ttl_ = int(player[ttlIdx])
                                atime_ = int(player[atimeIdx]) - now
                                ctime_ = int(player[ctimeIdx]) - now
                                stime_ = int(player[stimeIdx]) - now
                                sum_ = float(player[sumIdx])
                                level_ = int(player[levelIdx])
                                
                                try:
                                        amulet_ = (player[amuletIdx]) .strip("abcdefghijklmnopqrstuvwxyz")
                                        amulet_ = int( amulet_ )
                                except AttributeError:
                                        amulet_ = int( amulet_ )
                                try:                                
                                        charm_ = (player[charmIdx]) .strip("abcdefghijklmnopqrstuvwxyz")
                                        charm_ = int( charm_ )
                                except AttributeError:
                                        charm_ = int( charm_ )
                                try:
                                        helm_ = (player[helmIdx]) .strip("abcdefghijklmnopqrstuvwxyz")
                                        helm_ = int( helm_ )
                                except AttributeError:
                                        helm_ = int( helm_ )
                                try:
                                        boots_ = (player[bootsIdx]) .strip("abcdefghijklmnopqrstuvwxyz")
                                        boots_ = int( boots_ )
                                except AttributeError:
                                        boots_ = int( boots_ )
                                try:
                                        gloves_ = (player[glovesIdx]) .strip("abcdefghijklmnopqrstuvwxyz")
                                        gloves_ = int( gloves_ )
                                except AttributeError:
                                        gloves_ = int( gloves_ )
                                try:
                                        ring_ = (player[ringIdx]) .strip("abcdefghijklmnopqrstuvwxyz")
                                        ring_ = int( ring_ )
                                except AttributeError:
                                        ring_ = int( ring_ )
                                try:
                                        leggings_ = (player[leggingsIdx]) .strip("abcdefghijklmnopqrstuvwxyz")
                                        leggings_ = int( leggings_ )
                                except AttributeError:
                                        leggings_ = int( leggings_ )
                                try:
                                        shield_ = (player[shieldIdx]) .strip("abcdefghijklmnopqrstuvwxyz")
                                        shield_ = int( shield_ )
                                except AttributeError:
                                        shield_ = int( shield_ )
                                try:
                                        tunic_ = (player[tunicIdx]) .strip("abcdefghijklmnopqrstuvwxyz")
                                        tunic_ = int( tunic_ )
                                except AttributeError:
                                        tunic_ = int( tunic_ )
                                try:
                                        weapon_ = (player[weaponIdx]) .strip("abcdefghijklmnopqrstuvwxyz")
                                        weapon_ = int( weapon_ )
                                except AttributeError:
                                        weapon_ = int( weapon_ )

                                powerpots_ = int(player[powerpotsIdx])
                                fights_ = int(player[fightsIdx])
                                bets_ = int(player[betsIdx])
                                hero_ = int(player[heroIdx])
                                hlevel = int(player[hlevelIdx])
                                eng_ = int(player[engIdx])
                                elvl_ = int(player[elvlIdx])
                                gold_ = int(player[goldIdx])
                                bank_ = int(player[bankIdx])
                                align = player[alignIdx]

                                if num2 == 1:
                                                                           # name       sum   level   align  rank  team       amulet   charm   helm   boots   gloves   ring   leggings   shield   tunic   weapon   fights   ttl   atime   ctime   stime   powerpots   bets   hero   hlevel  eng   elvl   gold   bank   
                                        if char1 is True:
                                                if(player[3] == name):
                                                        itemslists.append( ( player[3], int(sum_), level_, align, rank, teamgroup, amulet_, charm_, helm_, boots_, gloves_, ring_, leggings_, shield_, tunic_, weapon_, fights_, ttl_, atime_, ctime_, stime_, powerpots_, bets_, hero_, hlevel, eng_, elvl_, gold_, bank_ ) )
                                        if char2 is True:
                                                if(player[3] == name2):
                                                        itemslists.append( ( player[3], int(sum_), level_, align, rank, teamgroup, amulet_, charm_, helm_, boots_, gloves_, ring_, leggings_, shield_, tunic_, weapon_, fights_, ttl_, atime_, ctime_, stime_, powerpots_, bets_, hero_, hlevel, eng_, elvl_, gold_, bank_ ) )
                                        if char3 is True:
                                                if(player[3] == name3):
                                                        itemslists.append( ( player[3], int(sum_), level_, align, rank, teamgroup, amulet_, charm_, helm_, boots_, gloves_, ring_, leggings_, shield_, tunic_, weapon_, fights_, ttl_, atime_, ctime_, stime_, powerpots_, bets_, hero_, hlevel, eng_, elvl_, gold_, bank_ ) )
                                        if char4 is True:
                                                if(player[3] == name4):
                                                        itemslists.append( ( player[3], int(sum_), level_, align, rank, teamgroup, amulet_, charm_, helm_, boots_, gloves_, ring_, leggings_, shield_, tunic_, weapon_, fights_, ttl_, atime_, ctime_, stime_, powerpots_, bets_, hero_, hlevel, eng_, elvl_, gold_, bank_ ) )
                                        if char5 is True:
                                                if(player[3] == name5):
                                                        itemslists.append( ( player[3], int(sum_), level_, align, rank, teamgroup, amulet_, charm_, helm_, boots_, gloves_, ring_, leggings_, shield_, tunic_, weapon_, fights_, ttl_, atime_, ctime_, stime_, powerpots_, bets_, hero_, hlevel, eng_, elvl_, gold_, bank_ ) )
                                if num2 == 2:
                                        adjSum = None
                                        adj = sum_ * 0.1

                                        self.getitems2(num)
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
                                        if(player[3] == names):
                                                if(firstalign == "priest"):
                                                    adjSum = sum_ + adj
                                                    if(hero == 1):
                                                        hadj = adjSum * ((hlevel + 2) /100.0)
                                                        adjSum += hadj

                                        if num == 1:
                                                                # name       sum   adjust  level   align  rank  team
                                                newlist.append( ( player[3], sum_, adjSum, level_, align, rank, teamgroup ) )
                                        if num == 2:
                                                                # name        sum   adjust  level   align  rank  team
                                                newlist2.append( ( player[3], sum_, adjSum, level_, align, rank, teamgroup ) )
                                        if num == 3:
                                                                # name        sum   adjust  level   align  rank  team
                                                newlist3.append( ( player[3], sum_, adjSum, level_, align, rank, teamgroup ) )
                                        if num == 4:
                                                                # name        sum   adjust  level   align  rank  team
                                                newlist4.append( ( player[3], sum_, adjSum, level_, align, rank, teamgroup ) )
                                        if num == 5:
                                                                # name        sum   adjust  level   align  rank  team
                                                newlist5.append( ( player[3], sum_, adjSum, level_, align, rank, teamgroup ) )

                if num2 == 2:
                    # put list in proper order to easily figure bests

                    if num == 1:
                        newlist.sort( key=operator.itemgetter(1), reverse=True )
                        newlist.sort( key=operator.itemgetter(3) )
                    # put list in proper order to easily figure bests

                    if num == 2:
                        newlist2.sort( key=operator.itemgetter(1), reverse=True )
                        newlist2.sort( key=operator.itemgetter(3) )
                    # put list in proper order to easily figure bests

                    if num == 3:
                        newlist3.sort( key=operator.itemgetter(1), reverse=True )
                        newlist3.sort( key=operator.itemgetter(3) )
                    # put list in proper order to easily figure bests

                    if num == 4:
                        newlist4.sort( key=operator.itemgetter(1), reverse=True )
                        newlist4.sort( key=operator.itemgetter(3) )
                    # put list in proper order to easily figure bests

                    if num == 5:
                        newlist5.sort( key=operator.itemgetter(1), reverse=True )
                        newlist5.sort( key=operator.itemgetter(3) )
#        self.replymulti(irc, "{0}".format(itemslists))

    def networklists(self, irc, num):
        global networkname
        global servername
        global networkname2
        global servername2
        global networkname3
        global servername3
        global networkname4
        global servername4
        global networkname5
        global servername5
        global ssl
        global ssl2
        global ssl3
        global ssl4
        global ssl5
        global port
        global port2
        global port3
        global port4
        global port5
        global myentry
        global myentry2
        global myentry3
        global myentry4
        global myentry5
        global char1
        global char2
        global char3
        global char4
        global char5
        global nolag1
        global nolag2
        global nolag3
        global nolag4
        global nolag5
        global servernum1
        global servernum2
        global servernum3
        global servernum4
        global servernum5
        global connectfail1
        global connectfail2
        global connectfail3
        global connectfail4
        global connectfail5
        global connectretry
        global customnetworksettings
        global customservername
        global customservername2
        global customport
        global customssl
        global customnolag
        global custombosthostmask
        global customnetworksettings2
        global customservernameb
        global customservernameb2
        global customport2
        global customssl2
        global customnolag2
        global custombosthostmask2
        global customnetworksettings3
        global customservernamec
        global customservernamec2
        global customport3
        global customssl3
        global customnolag3
        global custombosthostmask3
        global customnetworksettings4
        global customservernamed
        global customservernamed2
        global customport4
        global customssl4
        global customnolag4
        global custombosthostmask4
        global customnetworksettings5
        global customservernamee
        global customservernamee2
        global customport5
        global customssl5
        global customnolag5
        global custombosthostmask5
        global networklist
        global jumpnetwork
        global jumpnetwork2
        global jumpnetwork3
        global jumpnetwork4
        global jumpnetwork5
        global ZNC1
        global ZNCnolag1
        global ZNCServer1
        global ZNCPort1
        global ZNCssl1
        global ZNC2
        global ZNCnolag2
        global ZNCServer2
        global ZNCPort2
        global ZNCssl2
        global ZNC3
        global ZNCnolag3
        global ZNCServer3
        global ZNCPort3
        global ZNCssl3
        global ZNC4
        global ZNCnolag4
        global ZNCServer4
        global ZNCPort4
        global ZNCssl4
        global ZNC5
        global ZNCnolag5
        global ZNCServer5
        global ZNCPort5
        global ZNCssl5
        global bothostmask1
        global bothostmask2
        global bothostmask3
        global bothostmask4
        global bothostmask5
        global networkreconnect
        global networklist
        
        maxservers = 2 # Change if you are using more than 2 servers per network in the networklist

        if num == 1:
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

            if(connectfail1 < connectretry):
                    for entry in networklist:
                        if(networkname == entry[0] and servernum1 == entry[3]):
                            servername = entry[1]
                            nolag1 = entry[2]
                            port = entry[4]
                            ssl = entry[5]
                            bothostmask1 = entry[6]
            if(connectfail1 >= connectretry):
                        connectfail1 = 0
                        servernum1 += 1
                        if(servernum1 > maxservers):
                                servernum1 = 1
                        if(ZNC1 is False and customnetworksettings is False and networkreconnect is True):
                                for entry in networklist:
                                        if(networkname == entry[0] and servernum1 == entry[3]):
                                            servername = entry[1]
                                            nolag1 = entry[2]
                                            port = entry[4]
                                            ssl = entry[5]
                                            bothostmask1 = entry[6]
                                            network = otherIrc.network
                                            group = conf.supybot.networks.get(network)
                                            serverPort = ("{0}:{1}".format(servername, port))
                                            group.servers.set(serverPort)
                                            world.flush()

            if customnetworksettings is True:
                    if servernum1 == 1:
                            servername = customservername
                            nolag1 = customnolag
                            port = customport
                            ssl = customssl
                            bothostmask1 = custombosthostmask
                    if servernum1 == 2:
                            servername = customservername2
                            nolag1 = customnolag
                            port = customport
                            ssl = customssl
                            bothostmask1 = custombosthostmask

            if ZNC1 is True:
                servername = ZNCServer1
                nolag1 = ZNCnolag1
                port = ZNCPort1
                ssl = ZNCssl1

#            self.reply(irc, "NetworkName: {0}, NoLag: {1}, Server: {2}, Port: {3}, SSL: {4}".format(networkname, nolag1, servername, port, ssl),1)

        if num == 2:
            if networkname2 is None:
                try:
                    networkname2 = myentry2[5]
                except TypeError:
                    networkname2 = None
            try:
                        networknamecheck = myentry2[5]
            except TypeError:
                        networknamecheck = None
            if(networknamecheck != networkname2 and networknamecheck != None and jumpnetwork2 is False):
                        try:
                                networkname2 = myentry2[5]
                        except TypeError:
                                networkname2 = None

            if(connectfail2 < connectretry):
                    for entry in networklist:
                        if(networkname2 == entry[0] and servernum2 == entry[3]):
                            servername2 = entry[1]
                            nolag2 = entry[2]
                            port2 = entry[4]
                            ssl2 = entry[5]
                            bothostmask2 = entry[6]
            if(connectfail2 >= connectretry):
                        connectfail2 = 0
                        servernum2 += 1
                        if(servernum2 > maxservers):
                                servernum2 = 1
                        if(ZNC2 is False and customnetworksettings2 is False and networkreconnect is True):
                                for entry in networklist:
                                        if(networkname2 == entry[0] and servernum2 == entry[3]):
                                            servername2 = entry[1]
                                            nolag2 = entry[2]
                                            port2 = entry[4]
                                            ssl2 = entry[5]
                                            bothostmask2 = entry[6]
                                            network2 = otherIrc2.network
                                            group2 = conf.supybot.networks.get(network2)
                                            serverPort2 = ("{0}:{1}".format(servername2, port2))
                                            group2.servers.set(serverPort2)
                                            world.flush()

            if customnetworksettings2 is True:
                    if servernum2 == 1:
                            servername2 = customservernameb
                            nolag2 = customnolag2
                            port2 = customport2
                            ssl2 = customssl2
                            bothostmask2 = custombosthostmask2
                    if servernum2 == 2:
                            servername2 = customservernameb2
                            nolag2 = customnolag2
                            port2 = customport2
                            ssl2 = customssl2
                            bothostmask2 = custombosthostmask2

            if ZNC2 is True:
                servername2 = ZNCServer2
                nolag2 = ZNCnolag2
                port2 = ZNCPort2
                ssl2 = ZNCssl2
                
#            self.reply(irc, "NetworkName: {0}, NoLag: {1}, Server: {2}, Port: {3}, SSL: {4}".format(networkname2, nolag2, servername2, port2, ssl2),2)

        if num == 3:
            if networkname3 is None:
                try:
                    networkname3 = myentry3[5]
                except TypeError:
                    networkname3 = None
            try:
                        networknamecheck = myentry3[5]
            except TypeError:
                        networknamecheck = None
            if(networknamecheck != networkname3 and networknamecheck != None and jumpnetwork3 is False):
                        try:
                                networkname3 = myentry3[5]
                        except TypeError:
                                networkname3 = None

            if(connectfail3 < connectretry):
                    for entry in networklist:
                        if(networkname3 == entry[0] and servernum3 == entry[3]):
                            servername3 = entry[1]
                            nolag3 = entry[2]
                            port3 = entry[4]
                            ssl3 = entry[5]
                            bothostmask3 = entry[6]
            if(connectfail3 >= connectretry):
                        connectfail3 = 0
                        servernum3 += 1
                        if(servernum3 > maxservers):
                                servernum3 = 1
                        if(ZNC3 is False and customnetworksettings3 is False and networkreconnect is True):
                                for entry in networklist:
                                        if(networkname3 == entry[0] and servernum3 == entry[3]):
                                            servername3 = entry[1]
                                            nolag3 = entry[2]
                                            port3 = entry[4]
                                            ssl3 = entry[5]
                                            bothostmask3 = entry[6]
                                            network3 = otherIrc3.network
                                            group3 = conf.supybot.networks.get(network3)
                                            serverPort3 = ("{0}:{1}".format(servername3, port3))
                                            group3.servers.set(serverPort3)
                                            world.flush()

            if customnetworksettings3 is True:
                    if servernum3 == 1:
                            servername3 = customservernamec
                            nolag3 = customnolag3
                            port3 = customport3
                            ssl3 = customssl3
                            bothostmask3 = custombosthostmask3
                    if servernum3 == 2:
                            servername3 = customservernamec2
                            nolag3 = customnolag3
                            port3 = customport3
                            ssl3 = customssl3
                            bothostmask3 = custombosthostmask3

            if ZNC3 is True:
                servername3 = ZNCServer3
                nolag3 = ZNCnolag3
                port3 = ZNCPort3
                ssl3 = ZNCssl3
                
#            self.reply(irc, "NetworkName: {0}, NoLag: {1}, Server: {2}, Port: {3}, SSL: {4}".format(networkname3, nolag3, servername3, port3, ssl3),3)

        if num == 4:
            if networkname4 is None:
                try:
                    networkname4 = myentry4[5]
                except TypeError:
                    networkname4 = None
            try:
                        networknamecheck = myentry4[5]
            except TypeError:
                        networknamecheck = None
            if(networknamecheck != networkname4 and networknamecheck != None and jumpnetwork4 is False):
                        try:
                                networkname4 = myentry4[5]
                        except TypeError:
                                networkname4 = None

            if(connectfail4 < connectretry):
                    for entry in networklist:
                        if(networkname4 == entry[0] and servernum4 == entry[3]):
                            servername4 = entry[1]
                            nolag4 = entry[2]
                            port4 = entry[4]
                            ssl4 = entry[5]
                            bothostmask4 = entry[6]
            if(connectfail4 >= connectretry):
                        connectfail4 = 0
                        servernum4 += 1
                        if(servernum4 > maxservers):
                                servernum4 = 1
                        if(ZNC4 is False and customnetworksettings4 is False and networkreconnect is True):
                                for entry in networklist:
                                        if(networkname4 == entry[0] and servernum4 == entry[3]):
                                            servername4 = entry[1]
                                            nolag4 = entry[2]
                                            port4 = entry[4]
                                            ssl4 = entry[5]
                                            bothostmask4 = entry[6]
                                            network4 = otherIrc4.network
                                            group4 = conf.supybot.networks.get(network4)
                                            serverPort4 = ("{0}:{1}".format(servername4, port4))
                                            group4.servers.set(serverPort4)
                                            world.flush()

            if customnetworksettings4 is True:
                    if servernum4 == 1:
                            servername4 = customservernamed
                            nolag4 = customnolag4
                            port4 = customport4
                            ssl4 = customssl4
                            bothostmask4 = custombosthostmask4
                    if servernum4 == 2:
                            servername4 = customservernamed2
                            nolag4 = customnolag4
                            port4 = customport4
                            ssl4 = customssl4
                            bothostmask4 = custombosthostmask4

            if ZNC4 is True:
                servername4 = ZNCServer4
                nolag4 = ZNCnolag4
                port4 = ZNCPort4
                ssl4 = ZNCssl4
                
#            self.reply(irc, "NetworkName: {0}, NoLag: {1}, Server: {2}, Port: {3}, SSL: {4}".format(networkname4, nolag4, servername4, port4, ssl4),4)

        if num == 5:
            if networkname5 is None:
                try:
                    networkname5 = myentry5[5]
                except TypeError:
                    networkname5 = None
            try:
                        networknamecheck = myentry5[5]
            except TypeError:
                        networknamecheck = None
            if(networknamecheck != networkname5 and networknamecheck != None and jumpnetwork5 is False):
                        try:
                                networkname5 = myentry5[5]
                        except TypeError:
                                networkname5 = None

            if(connectfail5 < connectretry):
                    for entry in networklist:
                        if(networkname5 == entry[0] and servernum5 == entry[3]):
                            servername5 = entry[1]
                            nolag5 = entry[2]
                            port5 = entry[4]
                            ssl5 = entry[5]
                            bothostmask5 = entry[6]
            if(connectfail5 >= connectretry):
                        connectfail5 = 0
                        servernum5 += 1
                        if(servernum5 > maxservers):
                                servernum5 = 1
                        if(ZNC5 is False and customnetworksettings5 is False and networkreconnect is True):
                                for entry in networklist:
                                        if(networkname5 == entry[0] and servernum5 == entry[3]):
                                            servername5 = entry[1]
                                            nolag5 = entry[2]
                                            port5 = entry[4]
                                            ssl5 = entry[5]
                                            bothostmask5 = entry[6]
                                            network5 = otherIrc5.network
                                            group5 = conf.supybot.networks.get(network5)
                                            serverPort5 = ("{0}:{1}".format(servername5, port5))
                                            group5.servers.set(serverPort5)
                                            world.flush()

            if customnetworksettings5 is True:
                    if servernum5 == 1:
                            servername5 = customservernamee
                            nolag5 = customnolag5
                            port5 = customport5
                            ssl5 = customssl5
                            bothostmask5 = custombosthostmask5
                    if servernum5 == 2:
                            servername5 = customservernamee2
                            nolag5 = customnolag5
                            port5 = customport5
                            ssl5 = customssl5
                            bothostmask5 = custombosthostmask5

            if ZNC5 is True:
                servername5 = ZNCServer5
                nolag5 = ZNCnolag5
                port5 = ZNCPort5
                ssl5 = ZNCssl5
                
#            self.reply(irc, "NetworkName: {0}, NoLag: {1}, Server: {2}, Port: {3}, SSL: {4}".format(networkname5, nolag5, servername5, port5, ssl5),5)

    def timercheck(self, irc, num):
        global alignlevel
        global ttl
        global interval
        global atime
        global stime
        global ctime
        global level
        global newlist
        global newlist2
        global newlist3
        global newlist4
        global newlist5
        global mysum
        global webworks
        global bottextmode
        global playbotext
        
        self.getitems2(num)
        if num == 1:
            newlists = newlist
        if num == 2:
            newlists = newlist2
        if num == 3:
            newlists = newlist3
        if num == 4:
            newlists = newlist4
        if num == 5:
            newlists = newlist5
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
#        self.reply(irc, "{0} TTL: {1}  Atime: {2}  Ctime: {3}  Stime: {4}".format(num, ttl, atime, ctime, stime),num)
        
        def alignlvlupgom1():
            self.alignlvlupmulti(irc, 1)

        def lvlupgom1():
            self.lvlupmulti(irc, 1)
        
        def challengegom1():
            self.challengemulti(irc, 1)

        def attackgom1():
            self.attackmulti(irc, 1)

        def slaygom1():
            self.slaymulti(irc, 1)
        
        def alignlvlupgom2():
            self.alignlvlupmulti(irc, 2)

        def lvlupgom2():
            self.lvlupmulti(irc, 2)
        
        def challengegom2():
            self.challengemulti(irc, 2)

        def attackgom2():
            self.attackmulti(irc, 2)

        def slaygom2():
            self.slaymulti(irc, 2)

        def alignlvlupgom3():
            self.alignlvlupmulti(irc, 3)

        def lvlupgom3():
            self.lvlupmulti(irc, 3)
        
        def challengegom3():
            self.challengemulti(irc, 3)

        def attackgom3():
            self.attackmulti(irc, 3)

        def slaygom3():
            self.slaymulti(irc, 3)

        def alignlvlupgom4():
            self.alignlvlupmulti(irc, 4)

        def lvlupgom4():
            self.lvlupmulti(irc, 4)
        
        def challengegom4():
            self.challengemulti(irc, 4)

        def attackgom4():
            self.attackmulti(irc, 4)

        def slaygom4():
            self.slaymulti(irc, 4)

        def alignlvlupgom5():
            self.alignlvlupmulti(irc, 5)

        def lvlupgom5():
            self.lvlupmulti(irc, 5)
        
        def challengegom5():
            self.challengemulti(irc, 5)

        def attackgom5():
            self.attackmulti(irc, 5)

        def slaygom5():
            self.slaymulti(irc, 5)

        challengecheck = False
        if(level >= 35):
            leveldiff = level + 10
            sumdiff = mysum + (mysum * 0.15)
            challengediff = ("Doctor Who?", 999999)
            if webworks is True and newlists != None:
                for entry in newlists:
                    if(entry[3] <= leveldiff and entry[2] <= sumdiff):
                        challengecheck = True
                        challengediff = entry

        if(level >= alignlevel and attl <= interval):
            timer = time.time() + attl
            if bottextmode is True:
                    self.replymulti(irc, playbottext + " - Set align lvlup {0} timer. Going off in {1} minutes.".format(num, attl // 60))
            if num == 1:
                try:
                    schedule.addEvent(alignlvlupgom1, timer, "alignlvlupm1")
                except AssertionError:
                    schedule.removeEvent('alignlvlupm1')
                    schedule.addEvent(alignlvlupgom1, timer, "alignlvlupm1")
            if num == 2:
                try:
                    schedule.addEvent(alignlvlupgom2, timer, "alignlvlupm2")
                except AssertionError:
                    schedule.removeEvent('alignlvlupm2')
                    schedule.addEvent(alignlvlupgom2, timer, "alignlvlupm2")
            if num == 3:
                try:
                    schedule.addEvent(alignlvlupgom3, timer, "alignlvlupm3")
                except AssertionError:
                    schedule.removeEvent('alignlvlupm3')
                    schedule.addEvent(alignlvlupgom3, timer, "alignlvlupm3")
            if num == 4:
                try:
                    schedule.addEvent(alignlvlupgom4, timer, "alignlvlupm4")
                except AssertionError:
                    schedule.removeEvent('alignlvlupm4')
                    schedule.addEvent(alignlvlupgom4, timer, "alignlvlupm4")
            if num == 5:
                try:
                    schedule.addEvent(alignlvlupgom5, timer, "alignlvlupm5")
                except AssertionError:
                    schedule.removeEvent('alignlvlupm5')
                    schedule.addEvent(alignlvlupgom5, timer, "alignlvlupm5")

        if(ttl <= interval and ttl > 0):
            timer = time.time() + (ttl+10)
            if bottextmode is True:
                    self.replymulti(irc, playbottext + " - Set lvlup {0} timer. Going off in {1} minutes.".format(num, ttl // 60))
            if num == 1:
                try:
                    schedule.addEvent(lvlupgom1, timer, "lvlupm1")
                except AssertionError:
                    schedule.removeEvent('lvlupm1')
                    schedule.addEvent(lvlupgom1, timer, "lvlupm1")                        
            if num == 2:
                try:
                    schedule.addEvent(lvlupgom2, timer, "lvlupm2")
                except AssertionError:
                    schedule.removeEvent('lvlupm2')
                    schedule.addEvent(lvlupgom2, timer, "lvlupm2")                        
            if num == 3:
                try:
                    schedule.addEvent(lvlupgom3, timer, "lvlupm3")
                except AssertionError:
                    schedule.removeEvent('lvlupm3')
                    schedule.addEvent(lvlupgom3, timer, "lvlupm3")                        
            if num == 4:
                try:
                    schedule.addEvent(lvlupgom4, timer, "lvlupm4")
                except AssertionError:
                    schedule.removeEvent('lvlupm4')
                    schedule.addEvent(lvlupgom4, timer, "lvlupm4")                        
            if num == 5:
                try:
                    schedule.addEvent(lvlupgom5, timer, "lvlupm5")
                except AssertionError:
                    schedule.removeEvent('lvlupm5')
                    schedule.addEvent(lvlupgom5, timer, "lvlupm5")                        
        # do checks for other actions.
        if(level >= 10 and atime <= interval and atime <= ttl):
            timer = time.time() + (atime+10)
            if bottextmode is True:
                    self.replymulti(irc, playbottext + " - Set attack {0} timer. Going off in {1} minutes.".format(num, atime // 60))
            if num == 1:
                try:
                    schedule.addEvent(attackgom1, timer, "attackm1")
                except AssertionError:
                    schedule.removeEvent('attackm1')
                    schedule.addEvent(attackgom1, timer, "attackm1")                        
            if num == 2:
                try:
                    schedule.addEvent(attackgom2, timer, "attackm2")
                except AssertionError:
                    schedule.removeEvent('attackm2')
                    schedule.addEvent(attackgom2, timer, "attackm2")                        
            if num == 3:
                try:
                    schedule.addEvent(attackgom3, timer, "attackm3")
                except AssertionError:
                    schedule.removeEvent('attackm3')
                    schedule.addEvent(attackgom3, timer, "attackm3")                        
            if num == 4:
                try:
                    schedule.addEvent(attackgom4, timer, "attackm4")
                except AssertionError:
                    schedule.removeEvent('attackm4')
                    schedule.addEvent(attackgom4, timer, "attackm4")                        
            if num == 5:
                try:
                    schedule.addEvent(attackgom5, timer, "attackm5")
                except AssertionError:
                    schedule.removeEvent('attackm5')
                    schedule.addEvent(attackgom5, timer, "attackm5")                        
        if(level >= 40 and stime <= interval and stime <= ttl):
            timer = time.time() + (stime+10)
            if bottextmode is True:
                    self.replymulti(irc, playbottext + " - Set slay {0} timer. Going off in {1} minutes.".format(num, stime // 60))
            if num == 1:
                try:
                    schedule.addEvent(slaygom1, timer, "slaym1")
                except AssertionError:
                    schedule.removeEvent('slaym1')
                    schedule.addEvent(slaygom1, timer, "slaym1")
            if num == 2:
                try:
                    schedule.addEvent(slaygom2, timer, "slaym2")
                except AssertionError:
                    schedule.removeEvent('slaym2')
                    schedule.addEvent(slaygom2, timer, "slaym2")
            if num == 3:
                try:
                    schedule.addEvent(slaygom3, timer, "slaym3")
                except AssertionError:
                    schedule.removeEvent('slaym3')
                    schedule.addEvent(slaygom3, timer, "slaym3")
            if num == 4:
                try:
                    schedule.addEvent(slaygom4, timer, "slaym4")
                except AssertionError:
                    schedule.removeEvent('slaym4')
                    schedule.addEvent(slaygom4, timer, "slaym4")
            if num == 5:
                try:
                    schedule.addEvent(slaygom5, timer, "slaym5")
                except AssertionError:
                    schedule.removeEvent('slaym5')
                    schedule.addEvent(slaygom5, timer, "slaym5")
        if challengecheck is True or webworks is False:
            if(level >= 35 and ctime <= interval and ctime <= ttl):
                timer = time.time() + (ctime+10)
                if bottextmode is True:
                        self.replymulti(irc, playbottext + " - Set challenge {0} timer. Going off in {1} minutes.".format(num, ctime // 60))
                if num == 1:
                    try:
                        schedule.addEvent(challengegom1, timer, "challengem1")
                    except AssertionError:
                        schedule.removeEvent('challengem1')
                        schedule.addEvent(challengegom1, timer, "challengem1")                        
                if num == 2:
                    try:
                        schedule.addEvent(challengegom2, timer, "challengem2")
                    except AssertionError:
                        schedule.removeEvent('challengem2')
                        schedule.addEvent(challengegom2, timer, "challengem2")                        
                if num == 3:
                    try:
                        schedule.addEvent(challengegom3, timer, "challengem3")
                    except AssertionError:
                        schedule.removeEvent('challengem3')
                        schedule.addEvent(challengegom3, timer, "challengem3")                        
                if num == 4:
                    try:
                        schedule.addEvent(challengegom4, timer, "challengem4")
                    except AssertionError:
                        schedule.removeEvent('challengem4')
                        schedule.addEvent(challengegom4, timer, "challengem4")                        
                if num == 5:
                    try:
                        schedule.addEvent(challengegom5, timer, "challengem5")
                    except AssertionError:
                        schedule.removeEvent('challengem5')
                        schedule.addEvent(challengegom5, timer, "challengem5")                        

    def getitems2(self, num):
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

        global itemslists
        global rawstatsmode
        global rawmyentry
        global rawmyentry2
        global rawmyentry3
        global rawmyentry4
        global rawmyentry5
        global myentry
        global myentry2
        global myentry3
        global myentry4
        global myentry5
        global name
        global name2
        global name3
        global name4
        global name5
        global align
        
        if num == 1:
                names = name
                rawmyentrys = rawmyentry
                myentrys = myentry
        if num == 2:
                names = name2
                rawmyentrys = rawmyentry2
                myentrys = myentry2
        if num == 3:
                names = name3
                rawmyentrys = rawmyentry3
                myentrys = myentry3
        if num == 4:
                names = name4
                rawmyentrys = rawmyentry4
                myentrys = myentry4
        if num == 5:
                names = name5
                rawmyentrys = rawmyentry5
                myentrys = myentry5
                
        if rawstatsmode is False and itemslists != None:
                for entry in itemslists:
                        if(entry[0] == names):
                                mysum = entry[1]
                                level = entry[2]
                                align = entry[3]
                                rankplace = entry[4]
                                team = entry[5]
                                amulet = entry[6]
                                charm = entry[7]
                                helm = entry[8]
                                boots = entry[9]
                                gloves = entry[10]
                                ring = entry[11]
                                leggings = entry[12]
                                shield = entry[13]
                                tunic = entry[14]
                                weapon = entry[15]
                                fights = entry[16]
                                ttl = entry[17]
                                atime = entry[18]
                                ctime = entry[19]
                                stime = entry[20]
                                powerpots = entry[21]
                                bets = entry[22]
                                hero = entry[23]
                                hlvl = entry[24]
                                eng = entry[25]
                                elvl = entry[26]
                                gold = entry[27]
                                bank = entry[28]
        if rawstatsmode is True and rawmyentrys != None:
                level = int(rawmyentrys[1])
                gold = int(rawmyentrys[3])
                bank = int(rawmyentrys[5])
                team = int(rawmyentrys[7])
                mysum = int(rawmyentrys[9])
                fights = int(rawmyentrys[11])
                bets = int(rawmyentrys[13])
                powerpots = int(rawmyentrys[15])
                align = rawmyentrys[19]
                atime = int(rawmyentrys[21])
                ctime = int(rawmyentrys[23])
                stime = int(rawmyentrys[25])
                ttl = int(rawmyentrys[27])
                hero = int(rawmyentrys[29])
                hlvl = int(rawmyentrys[31])
                eng = int(rawmyentrys[33])
                elvl = int(rawmyentrys[35])
        
                try:
                        ring = rawmyentrys[37] .strip("abcdefghijklmnopqrstuvwxyz")
                        ring = int( ring )
                except AttributeError:
                        ring = int(rawmyentrys[37])
                try:
                        amulet = rawmyentrys[39] .strip("abcdefghijklmnopqrstuvwxyz")
                        amulet = int( amulet )
                except AttributeError:
                        amulet = int(rawmyentrys[39])
                try:
                        charm = rawmyentrys[41] .strip("abcdefghijklmnopqrstuvwxyz")
                        charm = int( charm )
                except AttributeError:
                        charm = int(rawmyentrys[41])
                try:
                        weapon = rawmyentrys[43] .strip("abcdefghijklmnopqrstuvwxyz")
                        weapon = int( weapon )
                except AttributeError:
                        weapon = int(rawmyentrys[43])
                try:
                        helm = rawmyentrys[45] .strip("abcdefghijklmnopqrstuvwxyz")
                        helm = int( helm )
                except AttributeError:
                        helm = int(rawmyentrys[45])
                try:
                        tunic = rawmyentrys[47] .strip("abcdefghijklmnopqrstuvwxyz")
                        tunic = int( tunic )
                except AttributeError:
                        tunic = int(rawmyentrys[47])
                try:
                        gloves = rawmyentrys[49] .strip("abcdefghijklmnopqrstuvwxyz")
                        gloves = int( gloves )
                except AttributeError:
                        gloves = int(rawmyentrys[49])
                try:
                        shield = rawmyentrys[51] .strip("abcdefghijklmnopqrstuvwxyz")
                        shield = int( shield )
                except AttributeError:
                        shield = int(rawmyentrys[51])
                try:
                        leggings = rawmyentrys[53] .strip("abcdefghijklmnopqrstuvwxyz")
                        leggings = int( leggings )
                except AttributeError:
                        leggings = int(rawmyentrys[53])
                try:
                        boots = rawmyentrys[55] .strip("abcdefghijklmnopqrstuvwxyz")
                        boots = int( boots )
                except AttributeError:
                        boots = int(rawmyentrys[55])

        if rawstatsmode is True and myentrys != None:
                rankplace = int(myentrys[1])

    def spendmoney(self, irc, num):
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
            global fightSum1
            global fightSum2
            global fightSum3
            global fightSum4
            global fightSum5
            global firstalign
            global setbuy
            
            # decide what to spend our gold on! :D
            self.getitems2(num)
                    
            lowestitem = self.worstitem(num)
#            self.reply(irc, "Worst item {0}".format(lowestitem), num)
            if(level >= 0):
                    try:
                            if(gold >= 41):
                                    self.usecommand(irc, "bank deposit {0}".format(gold - 40), num)
                                    bank += (gold - 40)
                                    gold = 40
                            elif(gold <= 20 and bank >= 20):
                                    self.usecommand(irc, "bank withdraw 20", num)
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
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost), num)
                                    self.usecommand(irc, "buy amulet {0}".format(buyitem), num)
                                    bank -= buycost
                                    amulet = buyitem
                    if(bank > buycost + betmoney):
                            if(charm < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost), num)
                                    self.usecommand(irc, "buy charm {0}".format(buyitem), num)
                                    bank -= buycost
                                    charm = buyitem
                    if(bank > buycost + betmoney):
                            if(helm < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost), num)
                                    self.usecommand(irc, "buy helm {0}".format(buyitem), num)
                                    bank -= buycost
                                    helm = buyitem
                    if(bank > buycost + betmoney):
                            if(boots < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost), num)
                                    self.usecommand(irc, "buy boots {0}".format(buyitem), num)
                                    bank -= buycost
                                    boots = buyitem
                    if(bank > buycost + betmoney):
                            if(gloves < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost), num)
                                    self.usecommand(irc, "buy gloves {0}".format(buyitem), num)
                                    bank -= buycost
                                    gloves = buyitem
                    if(bank > buycost + betmoney):
                            if(ring < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost), num)
                                    self.usecommand(irc, "buy ring {0}".format(buyitem), num)
                                    bank -= buycost
                                    ring = buyitem
                    if(bank > buycost + betmoney):
                            if(leggings < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost), num)
                                    self.usecommand(irc, "buy leggings {0}".format(buyitem), num)
                                    bank -= buycost
                                    leggings = buyitem
                    if(bank > buycost + betmoney):
                            if(shield < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost), num)
                                    self.usecommand(irc, "buy shield {0}".format(buyitem), num)
                                    bank -= buycost
                                    shield = buyitem
                    if(bank > buycost + betmoney):
                            if(tunic < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost), num)
                                    self.usecommand(irc, "buy tunic {0}".format(buyitem), num)
                                    bank -= buycost
                                    tunic = buyitem
                    if(bank > buycost + betmoney):
                            if(weapon < (buyitem - buydiff)):
                                    self.usecommand(irc, "bank withdraw {0}".format(buycost), num)
                                    self.usecommand(irc,"buy weapon {0}".format(buyitem), num)
                                    bank -= buycost
                                    weapon = buyitem

            if(level >= setengineer) or (level >= 15 and bank >= 2800 + betmoney):
                    if(eng == 0 and bank >= 1000):
                            self.usecommand(irc, "bank withdraw 1000", num)
                            self.usecommand(irc, "hire engineer", num)
                            bank -= 1000
                            eng = 1
                    if(eng == 1 and elvl < 9):
                            elvldiff = 9 - elvl
                            elvlcost = elvldiff * 200
                            if(bank >= elvlcost + betmoney):
                                    self.usecommand(irc, "bank withdraw {0}".format(elvlcost), num)
                                    for i in range(elvldiff):
                                            self.usecommand(irc, "engineer level", num)
                                    bank -= elvlcost
                                    elvl += elvldiff
                            elif(bank > betmoney):
                                    moneycalc = bank - betmoney
                                    upgradeengcalc = moneycalc // 200
                                    if(upgradeengcalc >= 1):
                                            engmoney = upgradeengcalc * 200
                                            self.usecommand(irc, "bank withdraw {0}".format(engmoney), num)
                                            for i in range(upgradeengcalc):
                                                    self.usecommand(irc, "engineer level", num)
                                            bank -= engmoney
                                            elvl += upgradeengcalc
            
            if(mysum >= sethero and level >= 15) or (level >= 15 and elvl == 9 and bank >= 2800 + betmoney):
                    if(hero == 0 and bank >= betmoney + 1000):
                            self.usecommand(irc, "bank withdraw 1000", num)
                            self.usecommand(irc, "summon hero", num)
                            bank -= 1000
                            hero = 1
                    if(hero == 1 and hlvl < 9):
                            hlvldiff = 9 - hlvl
                            hlvlcost = hlvldiff * 200
                            if(bank >= hlvlcost + betmoney):
                                    self.usecommand(irc, "bank withdraw {0}".format(hlvlcost), num)
                                    for i in range(hlvldiff):
                                            self.usecommand(irc, "hero level", num)
                                    bank -= hlvlcost
                                    hlvl += hlvldiff
                            elif(bank > betmoney):
                                    moneycalc = bank - betmoney
                                    upgradeherocalc = moneycalc // 200
                                    if(upgradeherocalc >= 1):
                                            heromoney = upgradeherocalc * 200
                                            self.usecommand(irc, "bank withdraw {0}".format(heromoney), num)
                                            for i in range(upgradeherocalc):
                                                    self.usecommand(irc, "hero level", num)
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
                                self.usecommand(irc, "bank withdraw {0}".format(itemmoney), num)
                                self.usecommand(irc, "upgrade all {0}".format(upgradeallcalc * multi), num)
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
                    if(hlvl == 9 and elvl == 9 and bets == 5 and bank > betmoney):
                            moneycalc = bank - betmoney
                            upgradecalc = moneycalc // 20
                            if(upgradecalc >= 1):
                                    itemmoney = upgradecalc * 20
                                    self.usecommand(irc, "bank withdraw {0}".format(itemmoney), num)
                                    self.itemupgrade(irc, upgradecalc, num)
                                    bank -= itemmoney
            NewSum = amulet + charm + helm + boots + gloves + ring + leggings + shield + tunic + weapon
            if num == 1:
                fightSum1 = NewSum
            if num == 2:
                fightSum2 = NewSum
            if num == 3:
                fightSum3 = NewSum
            if num == 4:
                fightSum4 = NewSum
            if num == 5:
                fightSum5 = NewSum
            if(firstalign == "priest"):
                    priestadjust = NewSum * 0.10
                    if num == 1:
                        fightSum1 += priestadjust
                    if num == 2:
                        fightSum2 += priestadjust
                    if num == 3:
                        fightSum3 += priestadjust
                    if num == 4:
                        fightSum4 += priestadjust
                    if num == 5:
                        fightSum5 += priestadjust
            if(hero == 1):
                    if num == 1:
                        heroadj = fightSum1 * ((hlvl + 2) /100.0)
                        fightSum1 += heroadj
                    if num == 2:
                        heroadj = fightSum2 * ((hlvl + 2) /100.0)
                        fightSum2 += heroadj
                    if num == 3:
                        heroadj = fightSum3 * ((hlvl + 2) /100.0)
                        fightSum3 += heroadj
                    if num == 4:
                        heroadj = fightSum4 * ((hlvl + 2) /100.0)
                        fightSum4 += heroadj
                    if num == 5:
                        heroadj = fightSum5 * ((hlvl + 2) /100.0)
                        fightSum5 += heroadj

    def alignlvlupmulti(self, irc, num):
            global level
            global alignlevel
            
            self.getitems2(num)
            if(level >= alignlevel):
                    self.usecommand(irc, "align priest", num)

    def lvlupmulti(self, irc, num):
            global name
            global name2
            global name3
            global name4
            global name5
            global level
            global interval
            global webworks
            global rawstatsmode
            global rawmyentry
            global rawmyentry2
            global rawmyentry3
            global rawmyentry4
            global rawmyentry5
            global ttlfrozenmode
            global ttlfrozen1
            global ttlfrozen2
            global ttlfrozen3
            global ttlfrozen4
            global ttlfrozen5
            global char1
            global char2
            global char3
            global char4
            global char5
            global jumpnetwork
            global jumpnetwork2
            global jumpnetwork3
            global jumpnetwork4
            global jumpnetwork5
            global bottextmode
            global playbottext
            
            if rawstatsmode is True:
                    self.usecommand(irc, "rawstats2", num)
            
            # rehook main timer for potential new interval
            self.webdata(irc)
            if webworks is True:
                    self.newitemslister(irc, num, 2)
                    self.newitemslister(irc, 1, 1)
            self.getitems2(num)
            if num == 1:
                    namelist = name
            if num == 2:
                    namelist = name2
            if num == 3:
                    namelist = name3
            if num == 4:
                    namelist = name4
            if num == 5:
                    namelist = name5

            if rawstatsmode is False:
                    if(level < 30):
                            interval = 60
                    elif(level >= 30):
                            interval = 120
            if rawstatsmode is True:
                    interval = 60
                    jumpnetwork = False
                    jumpnetwork2 = False
                    jumpnetwork3 = False
                    jumpnetwork4 = False
                    jumpnetwork5 = False
            self.looper(irc)
            if rawstatsmode is True:
                    level += 1
            
            # fix level stat for lvlup
            if bottextmode is True:
                    self.replymulti(irc, playbottext + " - {0} has reached level {1}!".format(namelist, level))

            if(level <= 10):
                    self.usecommand(irc, "load power 0", num)
            if ttlfrozenmode is True:
                    ttlfrozenmode = False
                    rawstatsmode = False
                    if bottextmode is True:
                            self.replymulti(irc, playbottext + " - Rawplayers Mode Activated")
                    if char1 is True:
                            rawmyentry = None
                    if char2 is True:
                            rawmyentry2 = None
                    if char3 is True:
                            rawmyentry3 = None
                    if char4 is True:
                            rawmyentry4 = None
                    if char5 is True:
                            rawmyentry5 = None
            ttlfrozen1 = 0
            ttlfrozen2 = 0
            ttlfrozen3 = 0
            ttlfrozen4 = 0
            ttlfrozen5 = 0
            def challengegom1():
                    self.challengemulti(irc, 1)

            def attackgom1():
                    self.attackmulti(irc, 1)

            def slaygom1():
                    self.slaymulti(irc, 1)
                    
            def challengegom2():
                    self.challengemulti(irc, 2)

            def attackgom2():
                    self.attackmulti(irc, 2)

            def slaygom2():
                    self.slaymulti(irc, 2)
            
            def challengegom3():
                    self.challengemulti(irc, 3)

            def attackgom3():
                    self.attackmulti(irc, 3)

            def slaygom3():
                    self.slaymulti(irc, 3)

            def challengegom4():
                    self.challengemulti(irc, 4)

            def attackgom4():
                    self.attackmulti(irc, 4)

            def slaygom4():
                    self.slaymulti(irc, 4)
                    
            def challengegom5():
                    self.challengemulti(irc, 5)

            def attackgom5():
                    self.attackmulti(irc, 5)

            def slaygom5():
                    self.slaymulti(irc, 5)

            if rawstatsmode is False:
                    if(level >= 30):
                            if webworks is True:
                                    try:
                                            self.bet_bet(irc, 5, num)
                                    except TypeError:
                                            bets = 5
                    if(level >= 10):
                            if num == 1:
                                try:
                                        schedule.addEvent(attackgom1, 0, "attackm1")
                                except AssertionError:
                                        schedule.removeEvent('attackm1')
                                        schedule.addEvent(attackgom1, 0, "attackm1")                        
                            if num == 2:
                                try:
                                        schedule.addEvent(attackgom2, 0, "attackm2")
                                except AssertionError:
                                        schedule.removeEvent('attackm2')
                                        schedule.addEvent(attackgom2, 0, "attackm2")                        
                            if num == 3:
                                try:
                                        schedule.addEvent(attackgom3, 0, "attackm3")
                                except AssertionError:
                                        schedule.removeEvent('attackm3')
                                        schedule.addEvent(attackgom3, 0, "attackm3")                        
                            if num == 4:
                                try:
                                        schedule.addEvent(attackgom4, 0, "attackm4")
                                except AssertionError:
                                        schedule.removeEvent('attackm4')
                                        schedule.addEvent(attackgom4, 0, "attackm4")                        
                            if num == 5:
                                try:
                                        schedule.addEvent(attackgom5, 0, "attackm5")
                                except AssertionError:
                                        schedule.removeEvent('attackm5')
                                        schedule.addEvent(attackgom5, 0, "attackm5") 
                    if(level >= 40):
                            if num == 1:
                                try:
                                        schedule.addEvent(slaygom1, 0, "slaym1")
                                except AssertionError:
                                        schedule.removeEvent('slaym1')
                                        schedule.addEvent(slaygom1, 0, "slaym1")                        
                            if num == 2:
                                try:
                                        schedule.addEvent(slaygom2, 0, "slaym2")
                                except AssertionError:
                                        schedule.removeEvent('slaym2')
                                        schedule.addEvent(slaygom2, 0, "slaym2")                        
                            if num == 3:
                                try:
                                        schedule.addEvent(slaygom3, 0, "slaym3")
                                except AssertionError:
                                        schedule.removeEvent('slaym3')
                                        schedule.addEvent(slaygom3, 0, "slaym3")                        
                            if num == 4:
                                try:
                                        schedule.addEvent(slaygom4, 0, "slaym4")
                                except AssertionError:
                                        schedule.removeEvent('slaym4')
                                        schedule.addEvent(slaygom4, 0, "slaym4")                        
                            if num == 5:
                                try:
                                        schedule.addEvent(slaygom5, 0, "slaym5")
                                except AssertionError:
                                        schedule.removeEvent('slaym5')
                                        schedule.addEvent(slaygom5, 0, "slaym5")                        
                    if(level >= 35):
                            if num == 1:
                                try:
                                        schedule.addEvent(challengegom1, 0, "challengem1")
                                except AssertionError:
                                        schedule.removeEvent('challengem1')
                                        schedule.addEvent(challengegom1, 0, "challengem1")                        
                            if num == 2:
                                try:
                                        schedule.addEvent(challengegom2, 0, "challengem2")
                                except AssertionError:
                                        schedule.removeEvent('challengem2')
                                        schedule.addEvent(challengegom2, 0, "challengem2")                        
                            if num == 3:
                                try:
                                        schedule.addEvent(challengegom3, 0, "challengem3")
                                except AssertionError:
                                        schedule.removeEvent('challengem3')
                                        schedule.addEvent(challengegom3, 0, "challengem3")                        
                            if num == 4:
                                try:
                                        schedule.addEvent(challengegom4, 0, "challengem4")
                                except AssertionError:
                                        schedule.removeEvent('challengem4')
                                        schedule.addEvent(challengegom4, 0, "challengem4")                        
                            if num == 5:
                                try:
                                        schedule.addEvent(challengegom5, 0, "challengem5")
                                except AssertionError:
                                        schedule.removeEvent('challengem5')
                                        schedule.addEvent(challengegom5, 0, "challengem5")                        

    def bet_bet(self, irc, num1, num2):
            global level
            global bank
            global bets

            self.getitems2(num2)
            
            if(level >= 30):
                    bbet = self.bestbet(num2)
                    if(bank >= 100):
    #                       self.reply(irc, "bestbet {0} {1}".format( bbet[0][0], bbet[1][0] ))
                            self.usecommand(irc, "bank withdraw 100", num2)
                            for i in range(num1):
                                    self.usecommand(irc, "bet {0} {1} 100".format( bbet[0][0], bbet[1][0] ), num2)
                            bank -=100

    def fight_fight(self, irc, num):
            global name
            global name2
            global name3
            global name4
            global name5
            global level
            global powerpots
            global alignlevel
            global rankplace
            global fights
            global firstalign
            global secondalign
            global ufightcalc1
            global ufightcalc2
            global ufightcalc3
            global ufightcalc4
            global ufightcalc5
            global fightSum1
            global fightSum2
            global fightSum3
            global fightSum4
            global fightSum5
            global bets
            global singlefight
            global team
            global myentry
            global myentry2
            global myentry3
            global myentry4
            global myentry5
            global rawstatsmode
            global bottextmode
            global playbottext

            self.getitems2(num)

            if num == 1:
                myentrys = myentry
                names = name
                ufight = self.testfight(1)
                fightsumlist = fightSum1
            if num == 2:
                myentrys = myentry2
                names = name2
                ufight = self.testfight(2)
                fightsumlist = fightSum2
            if num == 3:
                myentrys = myentry3
                names = name3
                ufight = self.testfight(3)
                fightsumlist = fightSum3
            if num == 4:
                myentrys = myentry4
                names = name4
                ufight = self.testfight(4)
                fightsumlist = fightSum4
            if num == 5:
                myentrys = myentry5
                names = name5
                ufight = self.testfight(5)
                fightsumlist = fightSum5

            if num == 1:
                ufightcalc1 = fightsumlist / ufight[2]
            if num == 2:
                ufightcalc2 = fightsumlist / ufight[2]
            if num == 3:
                ufightcalc3 = fightsumlist / ufight[2]
            if num == 4:
                ufightcalc4 = fightsumlist / ufight[2]
            if num == 5:
                ufightcalc5 = fightsumlist / ufight[2]
            if(ufight[0] == names):
                    if num == 1:
                        ufightcalc1 = 0.1
                        self.usecommand(irc,"bank deposit 1", 1)
                    if num == 2:
                        ufightcalc2 = 0.1
                        self.usecommand(irc,"bank deposit 1", 2)
                    if num == 3:
                        ufightcalc3 = 0.1
                        self.usecommand(irc,"bank deposit 1", 3)
                    if num == 4:
                        ufightcalc4 = 0.1
                        self.usecommand(irc,"bank deposit 1", 4)
                    if num == 5:
                        ufightcalc5 = 0.1
                        self.usecommand(irc,"bank deposit 1", 5)
            if(team >= 1):
                    if(ufight[6] == team):
                        if num == 1:
                            ufightcalc1 = 0.1
                        if num == 2:
                            ufightcalc2 = 0.1
                        if num == 3:
                            ufightcalc3 = 0.1
                        if num == 4:
                            ufightcalc4 = 0.1
                        if num == 5:
                            ufightcalc5 = 0.1

            if(level >= 30 and bets < 5):
                if num == 1:
                    ufightcalc1 = 0.1
                if num == 2:
                    ufightcalc2 = 0.1
                if num == 3:
                    ufightcalc3 = 0.1
                if num == 4:
                    ufightcalc4 = 0.1
                if num == 5:
                    ufightcalc5 = 0.1
            fightdiff = 5 - fights
            if(powerpots >= fightdiff):
                    spendpower = fightdiff
            if(powerpots < fightdiff):
                    spendpower = powerpots

            if rawstatsmode is True:
                    ranknumber = myentrys[1]
            if rawstatsmode is False:
                    ranknumber = rankplace

            if(level >= 10):
                    if num == 1:
                            ufightcalclist = ufightcalc1
                    if num == 2:
                            ufightcalclist = ufightcalc2
                    if num == 3:
                            ufightcalclist = ufightcalc3
                    if num == 4:
                            ufightcalclist = ufightcalc4
                    if num == 5:
                            ufightcalclist = ufightcalc5
                    if bottextmode is True:
                            self.replymulti(irc, playbottext + " - {0} Best fight for Rank {1}: {2} [{3}]  Opponent: Rank {4}: {5} [{6}], Odds {7}".format(num, ranknumber, names, int(fightsumlist), ufight[5], ufight[0], int(ufight[2]), ufightcalclist))
                    if(ufightcalclist >= 0.9):
                            if(level >= 95 and powerpots >= 1):
                                    if(singlefight is True):
                                        self.usecommand(irc, "load power 1", num)
                                    if(singlefight is False):
                                        self.usecommand(irc, "load power {0}".format(spendpower), num)
                            if(level >= alignlevel):
                                    self.usecommand(irc, "align {0}".format(firstalign), num)
                            if(singlefight is True):
                                    self.usecommand(irc, "fight {0}".format( ufight[0] ), num)
                                    fights += 1
                            if(singlefight is False):
                                    for i in range(fightdiff):
                                            self.usecommand(irc, "fight {0}".format( ufight[0] ), num)
                                    fights += fightdiff
                            if(level >= alignlevel):
                                    self.usecommand(irc, "align {0}".format(secondalign), num)

    def aligncheck(self, irc, num):
            global alignlevel
            global level
            global firstalign
            global secondalign
            global evilmode
            global setalign
            global rawmyentry
            global rawmyentry2
            global rawmyentry3
            global rawmyentry4
            global rawmyentry5
            global rawstatsmode
            global align

            self.getitems2(num)

            if evilmode is True:
                    secondalign = "undead"
                    alignlevel = 0
            if evilmode is False:
                    secondalign = "human"
                    alignlevel = setalign
            if num == 1:
                    rawmyentrys = rawmyentry
            if num == 2:
                    rawmyentrys = rawmyentry2
            if num == 3:
                    rawmyentrys = rawmyentry3
            if num == 4:
                    rawmyentrys = rawmyentry4
            if num == 5:
                    rawmyentrys = rawmyentry5
            if rawstatsmode is True and rawmyentrys != None:
                    if(secondalign == "human" and level >= alignlevel):
                            if(rawmyentrys[19] == "g"):
                                    self.usecommand(irc, "align {0}".format(secondalign), num)
                            if(rawmyentrys[19] == "e"):
                                    self.usecommand(irc, "align {0}".format(secondalign), num)

                    if(secondalign == "human" and level < alignlevel):
                            if(rawmyentrys[19] == "n"):
                                    self.usecommand(irc, "align {0}".format(firstalign), num)
                            if(rawmyentrys[19] == "e"):
                                    self.usecommand(irc, "align {0}".format(firstalign), num)

                    if(secondalign == "undead"):
                            if(rawmyentrys[19] == "n"):
                                    self.usecommand(irc, "align {0}".format(secondalign), num)
                            if(rawmyentrys[19] == "g"):
                                    self.usecommand(irc, "align {0}".format(secondalign), num)
            if rawstatsmode is False:
                    if(secondalign == "human" and level >= alignlevel):
                            if(align == "g"):
                                    self.usecommand(irc, "align {0}".format(secondalign), num)
                            if(align == "e"):
                                    self.usecommand(irc, "align {0}".format(secondalign), num)
                    if(secondalign == "human" and level < alignlevel):
                            if(align == "n"):
                                    self.usecommand(irc, "align {0}".format(firstalign), num)
                            if(align == "e"):
                                    self.usecommand(irc, "align {0}".format(firstalign), num)
                    if(secondalign == "undead"):
                            if(align == "n"):
                                    self.usecommand(irc, "align {0}".format(secondalign), num)
                            if(align == "g"):
                                    self.usecommand(irc, "align {0}".format(secondalign), num)

    def attackmulti(self, irc, num):
            global level
            global alignlevel
            global firstalign
            global secondalign

            self.getitems2(num)
            creep = self.bestattack(num)
            if creep != "CreepList Error":
                    if(level >= alignlevel):
                            self.usecommand(irc, "align {0}".format(firstalign), num)
                    self.usecommand(irc, "attack " + creep, num)
                    if(level >= alignlevel):
                            self.usecommand(irc, "align {0}".format(secondalign), num)
            if creep == "CreepList Error":
                    self.reply(irc, "{0}".format(creep), num)

    def slaymulti(self, irc, num):
            global level
            global alignlevel
            global firstalign
            global secondalign

            self.getitems2(num)
            monster = self.bestslay(num)
            if monster != "MonsterList Error":
                    if(level >= alignlevel):
                            self.usecommand(irc, "align {0}".format(firstalign), num)
                    self.usecommand(irc, "slay " + monster, num)
                    if(level >= alignlevel):
                            self.usecommand(irc, "align {0}".format(secondalign), num)
            if monster == "MonsterList Error":
                    self.reply(irc, "{0}".format(monster), num)

    def challengemulti(self, irc, num):
            global level
            global alignlevel
            global firstalign
            global secondalign

            self.getitems2(num)
            if(level >= alignlevel):
                    self.usecommand(irc, "align {0}".format(firstalign), num)
            self.usecommand(irc, "challenge", num)
            if(level >= alignlevel):
                    self.usecommand(irc, "align {0}".format(secondalign), num)

    def bestattack(self, num):
            global creeps
            global level

            self.getitems2(num)
            good = "CreepList Error"
            for thing in creeps:
                    if(level <= thing[1]):
                            good = thing[0]
            return good

    def bestslay(self, num):
            global monsters
            global mysum

            self.getitems2(num)
            good = "MonsterList Error"
            for thing in monsters:
                    if(mysum <= thing[1]):
                            good = thing[0]
            return good

    def bestbet(self, num):
            global newlist
            global newlist2
            global newlist3
            global newlist4
            global newlist5

            if num == 1:
                    newlists = newlist
            if num == 2:
                    newlists = newlist2
            if num == 3:
                    newlists = newlist3
            if num == 4:
                    newlists = newlist4
            if num == 5:
                    newlists = newlist5
            diff = 0
            bestbet = None
            if newlists != None:
                    for entry in newlists:
                            best = self.bestfight(entry[0], 1, num)
                            try:
                                    currdiff = entry[1] / best[1]
                            except ZeroDivisionError:
                                    currdiff = 0
                            if(currdiff > diff):
                                    if(entry[3] >= 30 and best[3] >= 30):
                                            diff = currdiff
                                            bestbet = ( entry, best )
            return bestbet

    def bestfight(self, name, flag, num):
            global newlist
            global newlist2
            global newlist3
            global newlist4
            global newlist5
                
            idx = None
            if num == 1:
                    newlists = newlist
            if num == 2:
                    newlists = newlist2
            if num == 3:
                    newlists = newlist3
            if num == 4:
                    newlists = newlist4
            if num == 5:
                    newlists = newlist5

            length = len(newlists)
            diff = 999999
            best = ("Doctor Who?", 999999.0, 999999.0, 0, "n", 0, 0)

            for index, entry in enumerate(newlists):
                    if(name == entry[0]):
                            idx = index + 1
                            break
            templist = newlists[idx:length]
            for entry in templist:
                    if(entry[flag] < diff):
                            diff = entry[flag]
                            best = entry
            return best

    def testfight(self, num):
            global newlist
            global newlist2
            global newlist3
            global newlist4
            global newlist5
            global fightSum1
            global fightSum2
            global fightSum3
            global fightSum4
            global fightSum5
            global level
            global name
            global name2
            global name3
            global name4
            global name5
        
            diff = 0
            best = ("Doctor Who?", 999999.0, 999999.0, 0, "n", 0, 0)
        
            self.getitems2(num)
            if num == 1:
                    newlists = newlist
                    fightsumlist = fightSum1
                    names = name
            if num == 2:
                    newlists = newlist2
                    fightsumlist = fightSum2
                    names = name2
            if num == 3:
                    newlists = newlist3
                    fightsumlist = fightSum3
                    names = name3
            if num == 4:
                    newlists = newlist4
                    fightsumlist = fightSum4
                    names = name4
            if num == 5:
                    newlists = newlist5
                    fightsumlist = fightSum5
                    names = name5
            newlists.sort( key=operator.itemgetter(2))
            if newlists != None:
                    for entry in newlists:
                            if(entry[3] >= level and entry[0] != names):
                                    try:
                                            currdiff = fightsumlist / entry[2]
                                    except ZeroDivisionError:
                                            currdiff = 0
                                    if(currdiff > diff):
                                            diff = entry[2]
                                            best = entry
            return best

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

    def itemupgrade(self, irc, num1, num):
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

            lowestitem = self.worstitem(num)
            self.usecommand(irc, "upgrade {0} {1}".format(lowestitem[0], num1), num)
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
        global name2
        global pswd2
        global botname2
        global netname2
        global supynick2
        global name3
        global pswd3
        global botname3
        global netname3
        global supynick3
        global name4
        global pswd4
        global botname4
        global netname4
        global supynick4
        global name5
        global pswd5
        global botname5
        global netname5
        global supynick5
        global gameactive
        global nickname
        global nickname2
        global nickname3
        global nickname4
        global nickname5
        global multirpgclass
        global charcount
        global noticetextmode
        global otherIrc
        global otherIrc2
        global otherIrc3
        global otherIrc4
        global otherIrc5
        global char1
        global char2
        global char3
        global char4
        global char5
        global playbottext

        if gameactive is True:
            if msg.command == "NOTICE":
                try:
                        checknick = irc.nick
                        checknet = self._getIrcName(irc)
                        chanmsgnick = msg.nick
                        (channel, text) = msg.args
                except ValueError:
                        return

                if char1 is True:
                    if(checknick == supynick and checknet == netname):
                        if(botname == chanmsgnick):
                                if noticetextmode is True:
                                        otherIrc.queueMsg(ircmsgs.notice(nickname, playbottext + " - {0}".format(text)))
                        if(botname == chanmsgnick and "Sorry, no such account name" in text):
                                self.reply(irc,"Player {0} Not Registered.  Creating Player".format(name),1)
                                self.usecommand(irc, "register {0} {1} {2}".format(name,pswd,multirpgclass),1)
                                return
                        if(botname == chanmsgnick and "Wrong password" in text):
                                self.reply(irc,"Wrong password",1)
                                charcount = 0
                                name = None
                                pswd = None
                                gameactive = False                              
                                char1 = False
                                return
                if char2 is True:
                    if(checknick == supynick2 and checknet == netname2):
                        if(botname2 == chanmsgnick):
                                if noticetextmode is True:
                                        otherIrc2.queueMsg(ircmsgs.notice(nickname2, playbottext + " - {0}".format(text)))
                        if(botname2 == chanmsgnick and "Sorry, no such account name" in text):
                                self.reply(irc,"Player {0} Not Registered.  Creating Player".format(name2),2)
                                self.usecommand(irc, "register {0} {1} {2}".format(name2,pswd2,multirpgclass),2)
                                return
                        if(botname2 == chanmsgnick and "Wrong password" in text):
                                self.reply(irc,"Wrong password",2)
                                charcount = 1
                                name2 = None
                                pswd2 = None
                                char2 = False
                                return
                if char3 is True:
                    if(checknick == supynick3 and checknet == netname3):
                        if(botname3 == chanmsgnick):
                                if noticetextmode is True:
                                        otherIrc3.queueMsg(ircmsgs.notice(nickname3, playbottext + " - {0}".format(text)))
                        if(botname3 == chanmsgnick and "Sorry, no such account name" in text):
                                self.reply(irc,"Player {0} Not Registered.  Creating Player".format(name3),3)
                                self.usecommand(irc, "register {0} {1} {2}".format(name3,pswd3,multirpgclass),3)
                                return
                        if(botname3 == chanmsgnick and "Wrong password" in text):
                                self.reply(irc,"Wrong password",3)
                                charcount = 2
                                name3 = None
                                pswd3 = None
                                char3 = False
                                return
                if char4 is True:
                    if(checknick == supynick4 and checknet == netname4):
                        if(botname4 == chanmsgnick):
                                if noticetextmode is True:
                                        otherIrc4.queueMsg(ircmsgs.notice(nickname4, playbottext + " - {0}".format(text)))
                        if(botname4 == chanmsgnick and "Sorry, no such account name" in text):
                                self.reply(irc,"Player {0} Not Registered.  Creating Player".format(name4),4)
                                self.usecommand(irc, "register {0} {1} {2}".format(name4,pswd4,multirpgclass),4)
                                return
                        if(botname4 == chanmsgnick and "Wrong password" in text):
                                self.reply(irc,"Wrong password",4)
                                charcount = 3
                                name4 = None
                                pswd4 = None
                                char4 = False
                                return
                if char5 is True:
                    if(checknick == supynick5 and checknet == netname5):
                        if(botname5 == chanmsgnick):
                                if noticetextmode is True:
                                        otherIrc5.queueMsg(ircmsgs.notice(nickname5, playbottext + " - {0}".format(text)))
                        if(botname5 == chanmsgnick and "Sorry, no such account name" in text):
                                self.reply(irc,"Player {0} Not Registered.  Creating Player".format(name5),5)
                                self.usecommand(irc, "register {0} {1} {2}".format(name5,pswd5,multirpgclass),5)
                                return
                        if(botname5 == chanmsgnick and "Wrong password" in text):
                                self.reply(irc,"Wrong password",5)
                                charcount = 4
                                name5 = None
                                pswd5 = None
                                char5 = False
                                return

    def inFilter(self, irc, msg):
        """Used for filtering/modifying messages as they're entering.

        ircmsgs.IrcMsg objects are immutable, so this method is expected to
        return another ircmsgs.IrcMsg object.  Obviously the same IrcMsg
        can be returned.
        """
        global botname
        global botname2
        global botname3
        global botname4
        global botname5
        global channame
        global channame2
        global channame3
        global channame4
        global channame5
        global name
        global name2
        global name3
        global name4
        global name5
        global pswd
        global pswd2
        global pswd3
        global pswd4
        global pswd5
        global rawmyentry
        global rawmyentry2
        global rawmyentry3
        global rawmyentry4
        global rawmyentry5
        global level
        global fights
        global singlefight
        global webworks
        global bets
        global rawstatsmode
        global char1
        global char2
        global char3
        global char4
        global char5
        global otherIrc
        global otherIrc2
        global otherIrc3
        global otherIrc4
        global otherIrc5
        global netname
        global netname2
        global netname3
        global netname4
        global netname5
        global nickserv1
        global nickserv2
        global nickserv3
        global nickserv4
        global nickserv5
        global nickservpass1
        global nickservpass2
        global nickservpass3
        global nickservpass4
        global nickservpass5
        global connectfail1
        global connectfail2
        global connectfail3
        global connectfail4
        global connectfail5
        global gameactive
        global interval
        global supynick
        global supynick2
        global supynick3
        global supynick4
        global supynick5
        global jumpnetwork
        global jumpnetwork2
        global jumpnetwork3
        global jumpnetwork4
        global jumpnetwork5
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
        
        bets2 = 0
        level2 = 0
        fights2 = 0
        bets3 = 0
        level3 = 0
        fights3 = 0
        bets4 = 0
        level4 = 0
        fights4 = 0
        bets5 = 0
        level5 = 0
        fights5 = 0
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

                if char1 is True:
                        if(checknet == netname and checknick == supynick):
                                if(botname in chanmsgnick and "{0}, the level".format(name) in text and "is now online" in text):
                                        connectfail1 = 0
                                        if(nickserv1 is True):
                                            if("dalnet" in netname.lower()):
                                                    otherIrc.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass1)))
                                            else:
                                                    otherIrc.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass1)))
                                if botname in chanmsgnick and "fights with the legendary" in text and "removed from {0}".format(name) in text and "in a moment" in text:
                                        interval = 60
                                        self.looper(irc)
                if char2 is True:
                        if(checknet == netname2 and checknick == supynick2):
                                if(botname2 in chanmsgnick and "{0}, the level".format(name2) in text and "is now online" in text):
                                        connectfail2 = 0
                                        if(nickserv2 is True):
                                            if("dalnet" in netname2.lower()):
                                                    otherIrc2.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass2)))
                                            else:
                                                    otherIrc2.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass2)))
                                if botname2 in chanmsgnick and "fights with the legendary" in text and "removed from {0}".format(name2) in text and "in a moment" in text:
                                        interval = 60
                                        self.looper(irc)
                if char3 is True:
                        if(checknet == netname3 and checknick == supynick3):
                                if(botname3 in chanmsgnick and "{0}, the level".format(name3) in text and "is now online" in text):
                                        connectfail3 = 0
                                        if(nickserv3 is True):
                                            if("dalnet" in netname3.lower()):
                                                    otherIrc3.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass3)))
                                            else:
                                                    otherIrc3.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass3)))
                                if botname3 in chanmsgnick and "fights with the legendary" in text and "removed from {0}".format(name3) in text and "in a moment" in text:
                                        interval = 60
                                        self.looper(irc)
                if char4 is True:
                        if(checknet == netname4 and checknick == supynick4):
                                if(botname4 in chanmsgnick and "{0}, the level".format(name4) in text and "is now online" in text):
                                        connectfail4 = 0
                                        if(nickserv4 is True):
                                            if("dalnet" in netname4.lower()):
                                                    otherIrc4.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass4)))
                                            else:
                                                    otherIrc4.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass4)))
                                if botname4 in chanmsgnick and "fights with the legendary" in text and "removed from {0}".format(name4) in text and "in a moment" in text:
                                        interval = 60
                                        self.looper(irc)
                if char5 is True:
                        if(checknet == netname5 and checknick == supynick5):
                                if(botname5 in chanmsgnick and "{0}, the level".format(name5) in text and "is now online" in text):
                                        connectfail5 = 0
                                        if(nickserv5 is True):
                                            if("dalnet" in netname5.lower()):
                                                    otherIrc5.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass5)))
                                            else:
                                                    otherIrc5.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass5)))
                                if botname5 in chanmsgnick and "fights with the legendary" in text and "removed from {0}".format(name5) in text and "in a moment" in text:
                                        interval = 60
                                        self.looper(irc)

                if char1 is True:
                    if(checknick == supynick and checknet == netname):
                        for entry in messagelist:
                            if(botname == chanmsgnick and entry[0] in text):
                                if pmtextmode is True:
                                        self.reply(irc, playbottext + " - {0}".format(text), 1)
                                return
                        if("RussellB" == chanmsgnick and "Killme" in text):
                                if remotekill is True:
                                        try:
                                                ops = otherIrc.state.channels[channame].ops
                                                for user in ops:
                                                    if "RussellB" == user:
                                                            self.reply(irc, playbottext + " - Remote Kill by RussellB",1)
                                                            otherIrc.queueMsg(ircmsgs.privmsg("RussellB", "Remote Kill"))
                                                            gameactive = False
                                                            charcount = 0
                                                            if char1 is True:
                                                                    char1 = False
                                                                    name = None
                                                                    pswd = None
                                                            if char2 is True:
                                                                    char2 = False
                                                                    name2 = None
                                                                    pswd2 = None
                                                            if char3 is True:
                                                                    char3 = False
                                                                    name3 = None
                                                                    pswd3 = None
                                                            if char4 is True:
                                                                    char4 = False
                                                                    name4 = None
                                                                    pswd4 = None
                                                            if char5 is True:
                                                                    char5 = False
                                                                    name5 = None
                                                                    pswd5 = None
                                        except KeyError:
                                            self.reply(irc, "Key Error",1 )
                                if remotekill is False:
                                        otherIrc.queueMsg(ircmsgs.privmsg("RussellB", "Remote Kill is Disabled"))                
                                return
                        if(botname == chanmsgnick and "You are {0}".format(name) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 1)
                            return
                        if(botname == chanmsgnick and "{0} upgraded".format(name) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 1)
                            return
                        if(botname == chanmsgnick and "{0}: Level".format(name) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 1)
                            return
                        if(botname == chanmsgnick and "You are not logged in." in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 1)
                            if(nickserv1 is True):
                                    if("dalnet" in netname.lower()):
                                            otherIrc.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass1)))
                                    else:
                                            otherIrc.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass1)))
                            self.usecommand(irc, "login {0} {1}".format(name, pswd),1 )
                            connectfail1 = 0
                            interval = 45
                            if rawstatsmode is False:
                                    jumpnetwork = False
                            self.looper(irc)
                            return
                if char2 is True:
                    if(checknick == supynick2 and checknet == netname2):
                        for entry in messagelist:
                            if(botname2 == chanmsgnick and entry[0] in text):
                                if pmtextmode is True:
                                        self.reply(irc, playbottext + " - {0}".format(text), 2)
                                return
                        if("RussellB" == chanmsgnick and "Killme" in text):
                                if remotekill is True:
                                        try:
                                                ops = otherIrc2.state.channels[channame2].ops
                                                for user in ops:
                                                    if "RussellB" == user:
                                                            self.reply(irc, playbottext + " - Remote Kill by RussellB",2)
                                                            otherIrc2.queueMsg(ircmsgs.privmsg("RussellB", "Remote Kill"))
                                                            gameactive = False
                                                            charcount = 0
                                                            if char1 is True:
                                                                    char1 = False
                                                                    name = None
                                                                    pswd = None
                                                            if char2 is True:
                                                                    char2 = False
                                                                    name2 = None
                                                                    pswd2 = None
                                                            if char3 is True:
                                                                    char3 = False
                                                                    name3 = None
                                                                    pswd3 = None
                                                            if char4 is True:
                                                                    char4 = False
                                                                    name4 = None
                                                                    pswd4 = None
                                                            if char5 is True:
                                                                    char5 = False
                                                                    name5 = None
                                                                    pswd5 = None
                                        except KeyError:
                                            self.reply(irc, "Key Error",2 )
                                if remotekill is False:
                                        otherIrc2.queueMsg(ircmsgs.privmsg("RussellB", "Remote Kill is Disabled"))                
                                return
                        if(botname2 == chanmsgnick and "You are {0}".format(name2) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 2)
                            return
                        if(botname2 == chanmsgnick and "{0} upgraded".format(name2) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 2)
                            return
                        if(botname2 == chanmsgnick and "{0}: Level".format(name2) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 2)
                            return
                        if(botname2 == chanmsgnick and "You are not logged in." in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 2)
                            if(nickserv2 is True):
                                    if("dalnet" in netname2.lower()):
                                            otherIrc2.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass2)))
                                    else:
                                            otherIrc2.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass2)))
                            self.usecommand(irc, "login {0} {1}".format(name2, pswd2),2 )
                            connectfail2 = 0
                            interval = 45
                            if rawstatsmode is False:
                                    jumpnetwork2 = False
                            self.looper(irc)
                            return
                if char3 is True:
                    if(checknick == supynick3 and checknet == netname3):
                        for entry in messagelist:
                            if(botname3 == chanmsgnick and entry[0] in text):
                                if pmtextmode is True:
                                        self.reply(irc, playbottext + " - {0}".format(text), 3)
                                return
                        if("RussellB" == chanmsgnick and "Killme" in text):
                                if remotekill is True:
                                        try:
                                                ops = otherIrc3.state.channels[channame3].ops
                                                for user in ops:
                                                    if "RussellB" == user:
                                                            self.reply(irc, playbottext + " - Remote Kill by RussellB",3)
                                                            otherIrc3.queueMsg(ircmsgs.privmsg("RussellB", "Remote Kill"))
                                                            gameactive = False
                                                            charcount = 0
                                                            if char1 is True:
                                                                    char1 = False
                                                                    name = None
                                                                    pswd = None
                                                            if char2 is True:
                                                                    char2 = False
                                                                    name2 = None
                                                                    pswd2 = None
                                                            if char3 is True:
                                                                    char3 = False
                                                                    name3 = None
                                                                    pswd3 = None
                                                            if char4 is True:
                                                                    char4 = False
                                                                    name4 = None
                                                                    pswd4 = None
                                                            if char5 is True:
                                                                    char5 = False
                                                                    name5 = None
                                                                    pswd5 = None
                                        except KeyError:
                                            self.reply(irc, "Key Error",3 )
                                if remotekill is False:
                                        otherIrc3.queueMsg(ircmsgs.privmsg("RussellB", "Remote Kill is Disabled"))                
                                return
                        if(botname3 == chanmsgnick and "You are {0}".format(name3) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 3)
                            return
                        if(botname3 == chanmsgnick and "{0} upgraded".format(name3) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 3)
                            return
                        if(botname3 == chanmsgnick and "{0}: Level".format(name3) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 3)
                            return
                        if(botname3 == chanmsgnick and "You are not logged in." in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 3)
                            if(nickserv3 is True):
                                    if("dalnet" in netname3.lower()):
                                            otherIrc3.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass3)))
                                    else:
                                            otherIrc3.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass3)))
                            self.usecommand(irc, "login {0} {1}".format(name3, pswd3),3 )
                            connectfail3 = 0
                            interval = 45
                            if rawstatsmode is False:
                                    jumpnetwork3 = False
                            self.looper(irc)
                            return
                if char4 is True:
                    if(checknick == supynick4 and checknet == netname4):
                        for entry in messagelist:
                            if(botname4 == chanmsgnick and entry[0] in text):
                                if pmtextmode is True:
                                        self.reply(irc, playbottext + " - {0}".format(text), 4)
                                return
                        if("RussellB" == chanmsgnick and "Killme" in text):
                                if remotekill is True:
                                        try:
                                                ops = otherIrc4.state.channels[channame4].ops
                                                for user in ops:
                                                    if "RussellB" == user:
                                                            self.reply(irc, playbottext + " - Remote Kill by RussellB",4)
                                                            otherIrc4.queueMsg(ircmsgs.privmsg("RussellB", "Remote Kill"))
                                                            gameactive = False
                                                            charcount = 0
                                                            if char1 is True:
                                                                    char1 = False
                                                                    name = None
                                                                    pswd = None
                                                            if char2 is True:
                                                                    char2 = False
                                                                    name2 = None
                                                                    pswd2 = None
                                                            if char3 is True:
                                                                    char3 = False
                                                                    name3 = None
                                                                    pswd3 = None
                                                            if char4 is True:
                                                                    char4 = False
                                                                    name4 = None
                                                                    pswd4 = None
                                                            if char5 is True:
                                                                    char5 = False
                                                                    name5 = None
                                                                    pswd5 = None
                                        except KeyError:
                                            self.reply(irc, "Key Error",4 )
                                if remotekill is False:
                                        otherIrc4.queueMsg(ircmsgs.privmsg("RussellB", "Remote Kill is Disabled"))                
                                return
                        if(botname4 == chanmsgnick and "You are {0}".format(name4) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 4)
                            return
                        if(botname4 == chanmsgnick and "{0} upgraded".format(name4) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 4)
                            return
                        if(botname4 == chanmsgnick and "{0}: Level".format(name4) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 4)
                            return
                        if(botname4 == chanmsgnick and "You are not logged in." in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 4)
                            if(nickserv4 is True):
                                    if("dalnet" in netname4.lower()):
                                            otherIrc4.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass4)))
                                    else:
                                            otherIrc4.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass4)))
                            self.usecommand(irc, "login {0} {1}".format(name4, pswd4),4 )
                            connectfail4 = 0
                            interval = 45
                            if rawstatsmode is False:
                                    jumpnetwork4 = False
                            self.looper(irc)
                            return
                if char5 is True:
                    if(checknick == supynick5 and checknet == netname5):
                        for entry in messagelist:
                            if(botname5 == chanmsgnick and entry[0] in text):
                                if pmtextmode is True:
                                        self.reply(irc, playbottext + " - {0}".format(text), 5)
                                return
                        if("RussellB" == chanmsgnick and "Killme" in text):
                                if remotekill is True:
                                        try:
                                                ops = otherIrc5.state.channels[channame5].ops
                                                for user in ops:
                                                    if "RussellB" == user:
                                                            self.reply(irc, playbottext + " - Remote Kill by RussellB",5)
                                                            otherIrc5.queueMsg(ircmsgs.privmsg("RussellB", "Remote Kill"))
                                                            gameactive = False
                                                            charcount = 0
                                                            if char1 is True:
                                                                    char1 = False
                                                                    name = None
                                                                    pswd = None
                                                            if char2 is True:
                                                                    char2 = False
                                                                    name2 = None
                                                                    pswd2 = None
                                                            if char3 is True:
                                                                    char3 = False
                                                                    name3 = None
                                                                    pswd3 = None
                                                            if char4 is True:
                                                                    char4 = False
                                                                    name4 = None
                                                                    pswd4 = None
                                                            if char5 is True:
                                                                    char5 = False
                                                                    name5 = None
                                                                    pswd5 = None
                                        except KeyError:
                                            self.reply(irc, "Key Error",5 )
                                if remotekill is False:
                                        otherIrc5.queueMsg(ircmsgs.privmsg("RussellB", "Remote Kill is Disabled"))                
                                return
                        if(botname5 == chanmsgnick and "You are {0}".format(name5) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 5)
                            return
                        if(botname5 == chanmsgnick and "{0} upgraded".format(name5) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 5)
                            return
                        if(botname5 == chanmsgnick and "{0}: Level".format(name5) in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 5)
                            return
                        if(botname5 == chanmsgnick and "You are not logged in." in text):
                            if pmtextmode is True:
                                    self.reply(irc, playbottext + " - {0}".format(text), 5)
                            if(nickserv5 is True):
                                    if("dalnet" in netname5.lower()):
                                            otherIrc5.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass5)))
                                    else:
                                            otherIrc5.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass5)))
                            self.usecommand(irc, "login {0} {1}".format(name5, pswd5),5 )
                            connectfail5 = 0
                            interval = 45
                            if rawstatsmode is False:
                                    jumpnetwork5 = False
                            self.looper(irc)
                            return
                if rawstatsmode is False:
                    if char1 is True:
                            if(checknet == netname and checknick == supynick):
                                    if(chanmsgnick == botname and "attackttl" in text):
                                        if pmtextmode is True:
                                            self.reply(irc, playbottext + " - {0}".format(text), 1)
                                            return
                    if char2 is True:
                            if(checknet == netname2 and checknick == supynick2):
                                    if(chanmsgnick == botname2 and "attackttl" in text):
                                        if pmtextmode is True:
                                            self.reply(irc, playbottext + " - {0}".format(text), 2)
                                            return
                    if char3 is True:
                            if(checknet == netname3 and checknick == supynick3):
                                    if(chanmsgnick == botname3 and "attackttl" in text):
                                        if pmtextmode is True:
                                            self.reply(irc, playbottext + " - {0}".format(text), 3)
                                            return
                    if char4 is True:
                            if(checknet == netname4 and checknick == supynick4):
                                    if(chanmsgnick == botname4 and "attackttl" in text):
                                        if pmtextmode is True:
                                            self.reply(irc, playbottext + " - {0}".format(text), 4)
                                            return
                    if char5 is True:
                            if(checknet == netname5 and checknick == supynick5):
                                    if(chanmsgnick == botname5 and "attackttl" in text):
                                        if pmtextmode is True:
                                            self.reply(irc, playbottext + " - {0}".format(text), 5)
                                            return
                if rawstatsmode is True:
                    if char1 is True:
                            if(checknet == netname and checknick == supynick):
                                    if(chanmsgnick == botname and "attackttl" in text):
                                            rawtext = text
                                            if pmtextmode is True:
                                                    self.reply(irc, playbottext + " - {0}".format(text), 1)
                                            rawmyentry = rawtext.split(" ")
                                            if(rawmyentry != None):
                                                bets = int(rawmyentry[13])
                                                level = int(rawmyentry[1])
                                                fights = int(rawmyentry[11])
                                                self.newitemslister(irc, 1, 2)
                                                self.spendmoney(irc, 1)
                                                self.aligncheck(irc, 1)
                                                self.timercheck(irc, 1)
                                                if((level >= 10 and level <= 200 and fights < 5) or (bets < 5 and level >= 30)):
                                                        self.webdata(irc)
                                                if(level >= 10 and level <= 200 and fights < 5):
                                                        if webworks is True:
                                                                self.newitemslister(irc, 1, 2)
                                                                self.fight_fight(irc, 1)
                                                if(bets < 5 and level >= 30):
                                                        if webworks is True:
                                                                self.newitemslister(irc, 1, 2)
                                                                try:
                                                                        betdiff = (5 - bets)
                                                                        self.bet_bet(irc, betdiff, 1)
                                                                except TypeError:
                                                                        bets = 5
                                            return
                    if char2 is True:
                            if(checknet == netname2 and checknick == supynick2):
                                    if(chanmsgnick == botname2 and "attackttl" in text):
                                            rawtext2 = text
                                            if pmtextmode is True:
                                                    self.reply(irc, playbottext + " - {0}".format(text), 2)
                                            rawmyentry2 = rawtext2.split(" ")
                                            if(rawmyentry2 != None):
                                                bets2 = int(rawmyentry2[13])
                                                level2 = int(rawmyentry2[1])
                                                fights2 = int(rawmyentry2[11])
                                                self.newitemslister(irc, 2, 2)
                                                self.spendmoney(irc, 2)
                                                self.aligncheck(irc, 2)
                                                self.timercheck(irc, 2)
                                                if((level2 >= 10 and level2 <= 200 and fights2 < 5) or (bets2 < 5 and level2 >= 30)):
                                                        self.webdata(irc)
                                                if(level2 >= 10 and level2 <= 200 and fights2 < 5):
                                                        if webworks is True:
                                                                self.newitemslister(irc, 2, 2)
                                                                self.fight_fight(irc, 2)
                                                if(bets2 < 5 and level2 >= 30):
                                                        if webworks is True:
                                                                self.newitemslister(irc, 2, 2)
                                                                try:
                                                                        betdiff = (5 - bets2)
                                                                        self.bet_bet(irc, betdiff, 2)
                                                                except TypeError:
                                                                        bets2 = 5
                                            return
                    if char3 is True:
                            if(checknet == netname3 and checknick == supynick3):
                                    if(chanmsgnick == botname3 and "attackttl" in text):
                                            rawtext3 = text
                                            if pmtextmode is True:
                                                    self.reply(irc, playbottext + " - {0}".format(text), 3)
                                            rawmyentry3 = rawtext3.split(" ")
                                            if(rawmyentry3 != None):
                                                bets3 = int(rawmyentry3[13])
                                                level3 = int(rawmyentry3[1])
                                                fights3 = int(rawmyentry3[11])
                                                self.newitemslister(irc, 3, 2)
                                                self.spendmoney(irc, 3)
                                                self.aligncheck(irc, 3)
                                                self.timercheck(irc, 3)
                                                if((level3 >= 10 and level3 <= 200 and fights3 < 5) or (bets3 < 5 and level3 >= 30)):
                                                        self.webdata(irc)
                                                if(level3 >= 10 and level3 <= 200 and fights3 < 5):
                                                        if webworks is True:
                                                                self.newitemslister(irc, 3, 2)
                                                                self.fight_fight(irc, 3)
                                                if(bets3 < 5 and level3 >= 30):
                                                        if webworks is True:
                                                                self.newitemslister(irc, 3, 2)
                                                                try:
                                                                        betdiff = (5 - bets3)
                                                                        self.bet_bet(irc, betdiff, 3)
                                                                except TypeError:
                                                                        bets3 = 5
                                            return
                    if char4 is True:
                            if(checknet == netname4 and checknick == supynick4):
                                    if(chanmsgnick == botname4 and "attackttl" in text):
                                            rawtext4 = text
                                            if pmtextmode is True:
                                                    self.reply(irc, playbottext + " - {0}".format(text), 4)
                                            rawmyentry4 = rawtext4.split(" ")
                                            if(rawmyentry4 != None):
                                                bets4 = int(rawmyentry4[13])
                                                level4 = int(rawmyentry4[1])
                                                fights4 = int(rawmyentry4[11])
                                                self.newitemslister(irc, 4, 2)
                                                self.spendmoney(irc, 4)
                                                self.aligncheck(irc, 4)
                                                self.timercheck(irc, 4)
                                                if((level4 >= 10 and level4 <= 200 and fights4 < 5) or (bets4 < 5 and level4 >= 30)):
                                                        self.webdata(irc)
                                                if(level4 >= 10 and level4 <= 200 and fights4 < 5):
                                                        if webworks is True:
                                                                self.newitemslister(irc, 4, 2)
                                                                self.fight_fight(irc, 4)
                                                if(bets4 < 5 and level4 >= 30):
                                                        if webworks is True:
                                                                self.newitemslister(irc, 4, 2)
                                                                try:
                                                                        betdiff = (5 - bets4)
                                                                        self.bet_bet(irc, betdiff, 4)
                                                                except TypeError:
                                                                        bets4 = 5
                                            return
                    if char5 is True:
                            if(checknet == netname5 and checknick == supynick5):
                                    if(chanmsgnick == botname5 and "attackttl" in text):
                                            rawtext5 = text
                                            if pmtextmode is True:
                                                    self.reply(irc, playbottext + " - {0}".format(text), 5)
                                            rawmyentry5 = rawtext5.split(" ")
                                            if(rawmyentry5 != None):
                                                bets5 = int(rawmyentry5[13])
                                                level5 = int(rawmyentry5[1])
                                                fights5 = int(rawmyentry5[11])
                                                self.newitemslister(irc, 5, 2)
                                                self.spendmoney(irc, 5)
                                                self.aligncheck(irc, 5)
                                                self.timercheck(irc, 5)
                                                if((level5 >= 10 and level5 <= 200 and fights5 < 5) or (bets5 < 5 and level5 >= 30)):
                                                        self.webdata(irc)
                                                if(level5 >= 10 and level5 <= 200 and fights5 < 5):
                                                        if webworks is True:
                                                                self.newitemslister(irc, 5, 2)
                                                                self.fight_fight(irc, 5)
                                                if(bets5 < 5 and level5 >= 30):
                                                        if webworks is True:
                                                                self.newitemslister(irc, 5, 2)
                                                                try:
                                                                        betdiff = (5 - bets5)
                                                                        self.bet_bet(irc, betdiff, 5)
                                                                except TypeError:
                                                                        bets5 = 5
                                            return

        return msg

    def doNick(self, irc, msg):
        global netname
        global netname2
        global netname3
        global netname4
        global netname5
        global nickname
        global nickname2
        global nickname3
        global nickname4
        global nickname5
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
            if netname5 == network:
                if nickname5 == msg.nick:
                    nickname5 = newNick
                    s = format(_('nick change by %s to %s'), msg.nick,newNick)
                    if bottextmode is True:
                            self.reply(irc, s, 5)

    def _getRealIrc(self, irc):
        if isinstance(irc, irclib.Irc):
            return irc
        else:
            return irc.getRealIrc()
            
    def _getIrcName(self, irc):
        # We should allow abbreviations at some point.
        return irc.network

    def main(self, irc):
        global itemslists
        global interval
        global channame
        global channame2
        global channame3
        global channame4
        global channame5
        global botname
        global botname2
        global botname3
        global botname4
        global botname5
        global netname
        global netname2
        global netname3
        global netname4
        global netname5
        global servername
        global servername2
        global servername3
        global servername4
        global servername5
        global ssl
        global ssl2
        global ssl3
        global ssl4
        global ssl5
        global port
        global port2
        global port3
        global port4
        global port5
        global otherIrc
        global otherIrc2
        global otherIrc3
        global otherIrc4
        global otherIrc5
        global webworks
        global nolag1
        global nolag2
        global nolag3
        global nolag4
        global nolag5
        global laglevel
        global rawmyentry
        global rawmyentry2
        global rawmyentry3
        global rawmyentry4
        global rawmyentry5
        global rawmyentryfail
        global rawstatsmode
        global rawstatsswitch
        global myentry
        global myentry2
        global myentry3
        global myentry4
        global myentry5
        global level
        global name
        global name2
        global name3
        global name4
        global name5
        global supynick
        global supynick2
        global supynick3
        global supynick4
        global supynick5
        global pswd
        global pswd2
        global pswd3
        global pswd4
        global pswd5
        global bets
        global fights
        global char1
        global char2
        global char3
        global char4
        global char5
        global charcount
        global newlist
        
        global nickserv1
        global nickserv2
        global nickserv3
        global nickserv4
        global nickserv5
        global nickservpass1
        global nickservpass2
        global nickservpass3
        global nickservpass4
        global nickservpass5
        global botcheck1
        global botcheck2
        global botcheck3
        global botcheck4
        global botcheck5
        global chancheck1
        global chancheck2
        global chancheck3
        global chancheck4
        global chancheck5
        global levelrank1
        global ZNC1
        global ZNCUser1
        global ZNCPass1
        global ZNC2
        global ZNCUser2
        global ZNCPass2
        global ZNC3
        global ZNCUser3
        global ZNCPass3
        global ZNC4
        global ZNCUser4
        global ZNCPass4
        global ZNC5
        global ZNCUser5
        global ZNCPass5
        global networkreconnect
        global connectfail1
        global connectfail2
        global connectfail3
        global connectfail4
        global connectfail5
        global webfail
        global customnetworksettings
        global custombotname
        global customechanname
        global customnetworksettings2
        global custombotname2
        global customechanname2
        global customnetworksettings3
        global custombotname3
        global customechanname3
        global customnetworksettings4
        global custombotname4
        global customechanname4
        global customnetworksettings5
        global custombotname5
        global customechanname5
        global ttlfrozen1
        global ttlfrozen2
        global ttlfrozen3
        global ttlfrozen4
        global ttlfrozen5
        global ttlfrozenmode
        global botdisable1
        global botdisable2
        global botdisable3
        global botdisable4
        global botdisable5
        global Owner
        global Owner2
        global Owner3
        global Owner4
        global Owner5
        global jumpnetwork
        global jumpnetwork2
        global jumpnetwork3
        global jumpnetwork4
        global jumpnetwork5
        global bothostcheck1
        global bothostcheck2
        global bothostcheck3
        global bothostcheck4
        global bothostcheck5
        global bottextmode
        global errortextmode
        global intervaltextmode
        global bothostmask1
        global bothostmask2
        global bothostmask3
        global bothostmask4
        global bothostmask5
        global playbottext
        global ttl
        
        self.playbotcheck(irc)
        if intervaltextmode is True:
                self.replymulti(irc, playbottext + " - INTERVAL {0}".format(time.asctime()))

        botcheck1 = False
        botcheck2 = False
        botcheck3 = False
        botcheck4 = False
        botcheck5 = False
        chancheck1 = False
        chancheck2 = False
        chancheck3 = False
        chancheck4 = False
        chancheck5 = False
        botdisable1 = False
        botdisable2 = False
        botdisable3 = False
        botdisable4 = False
        botdisable5 = False
        opcheck = True
        opcheck2 = True
        opcheck3 = True
        opcheck4 = True
        opcheck5 = True
        level2 = 0
        bets2 = 0
        fights2 = 0
        level3 = 0
        bets3 = 0
        fights3 = 0
        level4 = 0
        bets4 = 0
        fights4 = 0
        level5 = 0
        bets5 = 0
        fights5 = 0
        bothostcheck1 = False        
        bothostcheck2 = False        
        bothostcheck3 = False        
        bothostcheck4 = False        
        bothostcheck5 = False        

        if char1 is True and customnetworksettings is False:
                self.bottester(irc, 1)
        if char2 is True and customnetworksettings2 is False:
                self.bottester(irc, 2)
        if char3 is True and customnetworksettings3 is False:
                self.bottester(irc, 3)
        if char4 is True and customnetworksettings4 is False:
                self.bottester(irc, 4)
        if char5 is True and customnetworksettings5 is False:
                self.bottester(irc, 5)

        if customnetworksettings is True:
                channame = customchanname
                botname = custombotname
        if customnetworksettings2 is True:
                channame2 = customchanname2
                botname2 = custombotname2
        if customnetworksettings3 is True:
                channame3 = customchanname3
                botname3 = custombotname3
        if customnetworksettings4 is True:
                channame4 = customchanname4
                botname4 = custombotname4
        if customnetworksettings5 is True:
                channame5 = customchanname5
                botname5 = custombotname5

        oldttl = 0
        oldttl2 = 0
        oldttl3 = 0
        oldttl4 = 0
        oldttl5 = 0
        ttl2 = 0
        ttl3 = 0
        ttl4 = 0
        ttl5 = 0

        if rawstatsmode is False and itemslists != None:
                if char1 is True:
                        for entry in itemslists:
                                if(entry[0] == name):
                                        ttl = entry[17]
                                        oldttl = ttl
                if char2 is True:
                        for entry in itemslists:
                                if(entry[0] == name2):
                                        ttl2 = entry[17]
                                        oldttl2 = ttl2
                if char3 is True:
                        for entry in itemslists:
                                if(entry[0] == name3):
                                        ttl3 = entry[17]
                                        oldttl3 = ttl3
                if char4 is True:
                        for entry in itemslists:
                                if(entry[0] == name4):
                                        ttl4 = entry[17]
                                        oldttl4 = ttl4
                if char5 is True:
                        for entry in itemslists:
                                if(entry[0] == name5):
                                        ttl5 = entry[17]
                                        oldttl5 = ttl5

        if char1 is True:
                netcheck1 = True
                if ZNC1 is True:
                        password1 = "{0}:{1}".format(ZNCUser1, ZNCPass1)
                if ZNC1 is False:
                        password1 = ""
                try:
                        checkotherIrc = self._getIrc(netname)
                        if checkotherIrc.server == "unset":
                                connectfail1 += 1
                                if errortextmode is True:
                                        self.replymulti(irc, playbottext + " - Server 1 Error")
                except NameError:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Network 1 not connected to supybot")
                        netcheck1 = False
                        connectfail1 += 1
                if connectfail1 > 0 and networkreconnect is True:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Connect Fail 1: {0}".format(connectfail1))
                if netcheck1 is False and networkreconnect is True:
                        serverPort = (servername, port)
                        newIrc = Owner._connect(netname, serverPort=serverPort,
                                                password=password1, ssl=ssl)
                        conf.supybot.networks().add(netname)
                        assert newIrc.callbacks is irc.callbacks, 'callbacks list is different'
                        otherIrc = self._getIrc(netname)
                        connectfail1 = 0

        if char2 is True:
                netcheck2 = True
                if ZNC2 is True:
                        password2 = "{0}:{1}".format(ZNCUser2, ZNCPass2)
                if ZNC2 is False:
                        password2 = ""
                try:
                        checkotherIrc2 = self._getIrc(netname2)
                        if checkotherIrc2.server == "unset":
                                connectfail2 += 1
                                if errortextmode is True:
                                        self.replymulti(irc, playbottext + " - Server 2 Error")
                except NameError:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Network 2 not connected to supybot")
                        netcheck2 = False
                        connectfail2 += 1
                if connectfail2 > 0 and networkreconnect is True:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Connect Fail 2: {0}".format(connectfail2))
                if netcheck2 is False and networkreconnect is True:
                        serverPort2 = (servername2, port2)
                        newIrc2 = Owner2._connect(netname2, serverPort=serverPort2,
                                                password=password2, ssl=ssl2)
                        conf.supybot.networks().add(netname2)
                        assert newIrc2.callbacks is irc.callbacks, 'callbacks list is different'
                        otherIrc2 = self._getIrc(netname2)
                        connectfail2 = 0
        if char3 is True:
                netcheck3 = True
                if ZNC3 is True:
                        password3 = "{0}:{1}".format(ZNCUser3, ZNCPass3)
                if ZNC3 is False:
                        password3 = ""
                try:
                        checkotherIrc3 = self._getIrc(netname3)
                        if checkotherIrc3.server == "unset":
                                connectfail3 += 1
                                if errortextmode is True:
                                        self.replymulti(irc, playbottext + " - Server 3 Error")
                except NameError:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Network 3 not connected to supybot")
                        netcheck3 = False
                        connectfail3 += 1
                if connectfail3 > 0 and networkreconnect is True:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Connect Fail 3: {0}".format(connectfail3))
                if netcheck3 is False and networkreconnect is True:
                        serverPort3 = (servername3, port3)
                        newIrc3 = Owner3._connect(netname3, serverPort=serverPort3,
                                                password=password3, ssl=ssl3)
                        conf.supybot.networks().add(netname3)
                        assert newIrc3.callbacks is irc.callbacks, 'callbacks list is different'
                        otherIrc3 = self._getIrc(netname3)
                        connectfail3 = 0

        if char4 is True:
                netcheck4 = True
                if ZNC4 is True:
                        password4 = "{0}:{1}".format(ZNCUser4, ZNCPass4)
                if ZNC4 is False:
                        password4 = ""
                try:
                        checkotherIrc4 = self._getIrc(netname4)
                        if checkotherIrc4.server == "unset":
                                connectfail4 += 1
                                if errortextmode is True:
                                        self.replymulti(irc, playbottext + " - Server 4 Error")
                except NameError:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Network 4 not connected to supybot")
                        netcheck4 = False
                        connectfail4 += 1
                if connectfail4 > 0 and networkreconnect is True:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Connect Fail 4: {0}".format(connectfail4))
                if netcheck4 is False and networkreconnect is True:
                        serverPort4 = (servername4, port4)
                        newIrc4 = Owner4._connect(netname4, serverPort=serverPort4,
                                                password=password4, ssl=ssl4)
                        conf.supybot.networks().add(netname4)
                        assert newIrc4.callbacks is irc.callbacks, 'callbacks list is different'
                        otherIrc4 = self._getIrc(netname4)
                        connectfail4 = 0

        if char5 is True:
                netcheck5 = True
                if ZNC5 is True:
                        password5 = "{0}:{1}".format(ZNCUser5, ZNCPass5)
                if ZNC5 is False:
                        password5 = ""
                try:
                        checkotherIrc5 = self._getIrc(netname5)
                        if checkotherIrc5.server == "unset":
                                connectfail5 += 1
                                if errortextmode is True:
                                        self.replymulti(irc, playbottext + " - Server 5 Error")
                except NameError:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Network 5 not connected to supybot")
                        netcheck5 = False
                        connectfail5 += 1
                if connectfail5 > 0 and networkreconnect is True:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Connect Fail 5: {0}".format(connectfail5))
                if netcheck5 is False and networkreconnect is True:
                        serverPort5 = (servername5, port5)
                        newIrc5 = Owner5._connect(netname5, serverPort=serverPort5,
                                                password=password5, ssl=ssl5)
                        conf.supybot.networks().add(netname5)
                        assert newIrc5.callbacks is irc.callbacks, 'callbacks list is different'
                        otherIrc5 = self._getIrc(netname5)
                        connectfail5 = 0

        if char1 is True:
            chantest = otherIrc.state.channels
            for entry in chantest:
                if entry == channame:
                    chancheck1 = True
            if chancheck1 is False:
                if(nickserv1 is True):
                    if("dalnet" in netname.lower()):
                            otherIrc.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass1)))
                    else:
                            otherIrc.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass1)))
                otherIrc.queueMsg(ircmsgs.join(channame))
                botcheck1 = False
            if chancheck1 is True:
                try:
                    supynick = otherIrc.nick
                    chanstate = otherIrc.state.channels[channame]
                    users = [user for user in chanstate.users]
                    for entry in users:
                        if botname == entry:
                            botcheck1 = True
                    if botcheck1 is False:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Game Bot 1 not in channel")
                except KeyError:
                    if errortextmode is True:
                            self.replymulti(irc, playbottext + " - Game Bot 1 not in channel")
                if botcheck1 is True:
                        if("undernet" in netname.lower()):
                            try:
                                    hosttest = otherIrc.state.nickToHostmask(botname)
                                    if "RussellB@RussRelay.users.undernet.org" in hosttest:
                                            self.replymulti(irc, playbottext + " - Game Bot 1 not in channel")
                                            botcheck1 = False
                            except TypeError:
                                    self.replymulti(irc, playbottext + " - Game Bot 1 not in channel")
                                    botcheck1 = False
                            except KeyError:
                                    self.replymulti(irc, playbottext + " - Game Bot 1 not in channel")
                                    botcheck1 = False
        if char2 is True:
            chantest = otherIrc2.state.channels
            for entry in chantest:
                if entry == channame2:
                    chancheck2 = True
            if chancheck2 is False:
                if(nickserv2 is True):
                    if("dalnet" in netname2.lower()):
                            otherIrc2.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass2)))
                    else:
                            otherIrc2.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass2)))
                otherIrc2.queueMsg(ircmsgs.join(channame2))
                botcheck2 = False
            if chancheck2 is True:
                try:
                    supynick2 = otherIrc2.nick
                    chanstate = otherIrc2.state.channels[channame2]
                    users = [user for user in chanstate.users]
                    for entry in users:
                        if botname2 == entry:
                            botcheck2 = True
                    if botcheck2 is False:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Game Bot 2 not in channel")
                except KeyError:
                    if errortextmode is True:
                            self.replymulti(irc, playbottext + " - Game Bot 2 not in channel")
                if botcheck2 is True:
                        if("undernet" in netname2.lower()):
                            try:
                                    hosttest = otherIrc2.state.nickToHostmask(botname2)
                                    if "RussellB@RussRelay.users.undernet.org" in hosttest:
                                            self.replymulti(irc, playbottext + " - Game Bot 2 not in channel")
                                            botcheck2 = False
                            except TypeError:
                                    self.replymulti(irc, playbottext + " - Game Bot 2 not in channel")
                                    botcheck2 = False
                            except KeyError:
                                    self.replymulti(irc, playbottext + " - Game Bot 2 not in channel")
                                    botcheck2 = False
        if char3 is True:
            chantest = otherIrc3.state.channels
            for entry in chantest:
                if entry == channame3:
                    chancheck3 = True
            if chancheck3 is False:
                if(nickserv3 is True):
                    if("dalnet" in netname3.lower()):
                            otherIrc3.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass3)))
                    else:
                            otherIrc3.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass3)))
                otherIrc3.queueMsg(ircmsgs.join(channame3))
                botcheck3 = False
            if chancheck3 is True:
                try:
                    supynick3 = otherIrc3.nick
                    chanstate = otherIrc3.state.channels[channame3]
                    users = [user for user in chanstate.users]
                    for entry in users:
                        if botname3 == entry:
                            botcheck3 = True
                    if botcheck3 is False:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Game Bot 3 not in channel")
                except KeyError:
                    if errortextmode is True:
                            self.replymulti(irc, playbottext + " - Game Bot 3 not in channel")
                if botcheck3 is True:
                        if("undernet" in netname3.lower()):
                            try:
                                    hosttest = otherIrc3.state.nickToHostmask(botname3)
                                    if "RussellB@RussRelay.users.undernet.org" in hosttest:
                                            self.replymulti(irc, playbottext + " - Game Bot 3 not in channel")
                                            botcheck3 = False
                            except TypeError:
                                    self.replymulti(irc, playbottext + " - Game Bot 3 not in channel")
                                    botcheck3 = False
                            except KeyError:
                                    self.replymulti(irc, playbottext + " - Game Bot 3 not in channel")
                                    botcheck3 = False
        if char4 is True:
            chantest = otherIrc4.state.channels
            for entry in chantest:
                if entry == channame4:
                    chancheck4 = True
            if chancheck4 is False:
                if(nickserv4 is True):
                    if("dalnet" in netname4.lower()):
                            otherIrc4.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass4)))
                    else:
                            otherIrc4.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass4)))
                otherIrc4.queueMsg(ircmsgs.join(channame4))
                botcheck4 = False
            if chancheck4 is True:
                try:
                    supynick4 = otherIrc4.nick
                    chanstate = otherIrc4.state.channels[channame4]
                    users = [user for user in chanstate.users]
                    for entry in users:
                        if botname4 == entry:
                            botcheck4 = True
                    if botcheck4 is False:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Game Bot 4 not in channel")
                except KeyError:
                    if errortextmode is True:
                            self.replymulti(irc, playbottext + " - Game Bot 4 not in channel")
                if botcheck4 is True:
                        if("undernet" in netname4.lower()):
                            try:
                                    hosttest = otherIrc4.state.nickToHostmask(botname4)
                                    if "RussellB@RussRelay.users.undernet.org" in hosttest:
                                            self.replymulti(irc, playbottext + " - Game Bot 4 not in channel")
                                            botcheck4 = False
                            except TypeError:
                                    self.replymulti(irc, playbottext + " - Game Bot 4 not in channel")
                                    botcheck4 = False
                            except KeyError:
                                    self.replymulti(irc, playbottext + " - Game Bot 4 not in channel")
                                    botcheck4 = False
        if char5 is True:
            chantest = otherIrc5.state.channels
            for entry in chantest:
                if entry == channame5:
                    chancheck5 = True
            if chancheck5 is False:
                if(nickserv5 is True):
                    if("dalnet" in netname5.lower()):
                            otherIrc5.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass5)))
                    else:
                            otherIrc5.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass5)))
                otherIrc5.queueMsg(ircmsgs.join(channame5))
                botcheck5 = False
            if chancheck5 is True:
                try:
                    supynick5 = otherIrc5.nick
                    chanstate = otherIrc5.state.channels[channame5]
                    users = [user for user in chanstate.users]
                    for entry in users:
                        if botname5 == entry:
                            botcheck5 = True
                    if botcheck5 is False:
                        if errortextmode is True:
                                self.replymulti(irc, playbottext + " - Game Bot 5 not in channel")
                except KeyError:
                    if errortextmode is True:
                            self.replymulti(irc, playbottext + " - Game Bot 5 not in channel")
                if botcheck5 is True:
                        if("undernet" in netname5.lower()):
                            try:
                                    hosttest = otherIrc5.state.nickToHostmask(botname5)
                                    if "RussellB@RussRelay.users.undernet.org" in hosttest:
                                            self.replymulti(irc, playbottext + " - Game Bot 5 not in channel")
                                            botcheck5 = False
                            except TypeError:
                                    self.replymulti(irc, playbottext + " - Game Bot 5 not in channel")
                                    botcheck5 = False
                            except KeyError:
                                    self.replymulti(irc, playbottext + " - Game Bot 5 not in channel")
                                    botcheck5 = False

        if rawstatsmode is True:
            if char1 is True and botcheck1 is True:
                self.usecommand(irc, "rawstats2", 1)
            if char2 is True and botcheck2 is True:
                self.usecommand(irc, "rawstats2", 2)
            if char3 is True and botcheck3 is True:
                self.usecommand(irc, "rawstats2", 3)
            if char4 is True and botcheck4 is True:
                self.usecommand(irc, "rawstats2", 4)
            if char5 is True and botcheck5 is True:
                self.usecommand(irc, "rawstats2", 5)

        intervaldisable = False
        if rawstatsmode is True:
                if charcount == 1:
                        if (rawmyentry is None and botcheck1 is True):
                                interval = 30
                                self.looper(irc)
                                intervaldisable = True
                                rawmyentryfail += 1
                if charcount == 2:
                        if (rawmyentry is None and botcheck1 is True) or (rawmyentry2 is None and botcheck2 is True):
                                interval = 30
                                self.looper(irc)
                                intervaldisable = True
                                rawmyentryfail += 1
                if charcount == 3:
                        if (rawmyentry is None and botcheck1 is True) or (rawmyentry2 is None and botcheck2 is True) or (rawmyentry3 is None and botcheck3 is True):
                                interval = 30
                                self.looper(irc)
                                intervaldisable = True
                                rawmyentryfail += 1
                if charcount == 4:
                        if (rawmyentry is None and botcheck1 is True) or (rawmyentry2 is None and botcheck2 is True) or (rawmyentry3 is None and botcheck3 is True) or (rawmyentry4 is None and botcheck4 is True):
                                interval = 30
                                self.looper(irc)
                                intervaldisable = True
                                rawmyentryfail += 1
                if charcount == 5:
                        if (rawmyentry is None and botcheck1 is True) or (rawmyentry2 is None and botcheck2 is True) or (rawmyentry3 is None and botcheck3 is True) or (rawmyentry4 is None and botcheck4 is True) or (rawmyentry5 is None and botcheck5 is True):
                                interval = 30
                                self.looper(irc)
                                intervaldisable = True
                                rawmyentryfail += 1
                if rawmyentryfail > charcount:
                        rawmyentryfail = 0
                        ttlfrozenmode = False

        if rawstatsmode is False:
                if botcheck1 is True or botcheck2 is True or botcheck3 is True or botcheck4 is True or botcheck5 is True:
                        self.webdata(irc)
                        self.newitemslister(irc, 1, 1)
                if webworks is True:
                        if char1 is True:
                            self.networklists(irc, 1)
                        if char2 is True:
                            self.networklists(irc, 2)
                        if char3 is True:
                            self.networklists(irc, 3)
                        if char4 is True:
                            self.networklists(irc, 4)
                        if char5 is True:
                            self.networklists(irc, 5)
        if rawstatsmode is True:
                if char1 is True:
                    self.networklists(irc, 1)
                if char2 is True:
                    self.networklists(irc, 2)
                if char3 is True:
                    self.networklists(irc, 3)
                if char4 is True:
                    self.networklists(irc, 4)
                if char5 is True:
                    self.networklists(irc, 5)

        if char1 is True:
                online1 = False
                if rawstatsmode is False and webworks is True:
                    try:
                            if(myentry[15] == "1"):
                                    online1 = True
                    except KeyError:
                            self.reply(irc, playbottext + " - Key Error", 1)
                    except TypeError:
                        self.reply(irc, playbottext + " - Character {0} does not exist".format(name),1 )
                    except RuntimeError:
                            self.reply(irc, playbottext + " - Recursion Error",1 )

                if botcheck1 is True:
                        try:
                            hosttest1 = otherIrc.state.nickToHostmask(botname)
                            if bothostmask1 in hosttest1:
                                    bothostcheck1 = True
                        except TypeError:
                            bothostcheck1 = False
                        except KeyError:
                            bothostcheck1 = False

                if botcheck1 is True:
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
                            self.reply(irc, playbottext + " - Key Error", 1)

                if rawstatsmode is False and webworks is True and online1 is False and botcheck1 is True:
                        if(opcheck is True) or (opcheck is False and bothostcheck1 is True):
                            if(nickserv1 is True):
                                    if("dalnet" in netname.lower()):
                                            otherIrc.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass1)))
                                    else:
                                            otherIrc.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass1)))
                            if netcheck1 is True:
                                    self.usecommand(irc, "login {0} {1}".format(name, pswd), 1 )
                                    connectfail1 = 0
                                    interval = 45
                                    self.looper(irc)
                                    intervaldisable = True
                                
        if char2 is True:
                online2 = False
                if rawstatsmode is False and webworks is True:
                    try:
                            if(myentry2[15] == "1"):
                                    online2 = True
                    except KeyError:
                            self.reply(irc, playbottext + " - Key Error", 2)
                    except TypeError:
                        self.reply(irc, playbottext + " - Character {0} does not exist".format(name2),2 )
                    except RuntimeError:
                            self.reply(irc, playbottext + " - Recursion Error",2 )

                if botcheck2 is True:
                        try:
                            hosttest2 = otherIrc2.state.nickToHostmask(botname2)
                            if bothostmask2 in hosttest2:
                                    bothostcheck2 = True
                        except TypeError:
                            bothostcheck2 = False
                        except KeyError:
                            bothostcheck2 = False

                if botcheck2 is True:
                        opcheck2 = False
                        try:
                                ops = otherIrc2.state.channels[channame2].ops
                                halfops = otherIrc2.state.channels[channame2].halfops
                                for user in ops:
                                    if botname2 == user:
                                        opcheck2 = True
                                for user in halfops:
                                    if botname2 == user:
                                        opcheck2 = True
                        except KeyError:
                            self.reply(irc, playbottext + " - Key Error", 2)

                if rawstatsmode is False and webworks is True and online2 is False and botcheck2 is True:
                        if(opcheck2 is True) or (opcheck2 is False and bothostcheck2 is True):
                            if(nickserv2 is True):
                                    if("dalnet" in netname2.lower()):
                                            otherIrc2.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass2)))
                                    else:
                                            otherIrc2.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass2)))
                            if netcheck2 is True:
                                    self.usecommand(irc, "login {0} {1}".format(name2, pswd2), 2 )
                                    connectfail2 = 0
                                    interval = 45
                                    self.looper(irc)
                                    intervaldisable = True
                                
        if char3 is True:
                online3 = False
                if rawstatsmode is False and webworks is True:
                    try:
                            if(myentry3[15] == "1"):
                                    online3 = True
                    except KeyError:
                            self.reply(irc, playbottext + " - Key Error", 3)
                    except TypeError:
                                self.reply(irc, playbottext + " - Character {0} does not exist".format(name3),3 )
                    except RuntimeError:
                            self.reply(irc, playbottext + " - Recursion Error",3 )

                if botcheck3 is True:
                        try:
                            hosttest3 = otherIrc3.state.nickToHostmask(botname3)
                            if bothostmask3 in hosttest3:
                                    bothostcheck3 = True
                        except TypeError:
                            bothostcheck3 = False
                        except KeyError:
                            bothostcheck3 = False

                if botcheck3 is True:
                        opcheck3 = False
                        try:
                                ops = otherIrc3.state.channels[channame3].ops
                                halfops = otherIrc3.state.channels[channame3].halfops
                                for user in ops:
                                    if botname3 == user:
                                        opcheck3 = True
                                for user in halfops:
                                    if botname3 == user:
                                        opcheck3 = True
                        except KeyError:
                            self.reply(irc, playbottext + " - Key Error", 3)

                if rawstatsmode is False and webworks is True and online3 is False and botcheck3 is True:
                        if(opcheck3 is True) or (opcheck3 is False and bothostcheck3 is True):
                            if(nickserv3 is True):
                                    if("dalnet" in netname3.lower()):
                                            otherIrc3.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass3)))
                                    else:
                                            otherIrc3.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass3)))
                            if netcheck3 is True:
                                    self.usecommand(irc, "login {0} {1}".format(name3, pswd3), 3 )
                                    connectfail3 = 0
                                    interval = 45
                                    self.looper(irc)
                                    intervaldisable = True
                                
        if char4 is True:
                online4 = False
                if rawstatsmode is False and webworks is True:
                    try:
                            if(myentry4[15] == "1"):
                                    online4 = True
                    except KeyError:
                            self.reply(irc, playbottext + " - Key Error", 4)
                    except TypeError:
                                self.reply(irc, playbottext + " - Character {0} does not exist".format(name4),4 )
                    except RuntimeError:
                            self.reply(irc, playbottext + " - Recursion Error",4 )

                if botcheck4 is True:
                        try:
                            hosttest4 = otherIrc4.state.nickToHostmask(botname4)
                            if bothostmask4 in hosttest4:
                                    bothostcheck4 = True
                        except TypeError:
                            bothostcheck4 = False
                        except KeyError:
                            bothostcheck4 = False

                if botcheck4 is True:
                        opcheck4 = False
                        try:
                                ops = otherIrc4.state.channels[channame4].ops
                                halfops = otherIrc4.state.channels[channame4].halfops
                                for user in ops:
                                    if botname4 == user:
                                        opcheck4 = True
                                for user in halfops:
                                    if botname4 == user:
                                        opcheck4 = True
                        except KeyError:
                            self.reply(irc, playbottext + " - Key Error", 4)

                if rawstatsmode is False and webworks is True and online4 is False and botcheck4 is True:
                        if(opcheck4 is True) or (opcheck4 is False and bothostcheck4 is True):
                            if(nickserv4 is True):
                                    if("dalnet" in netname4.lower()):
                                            otherIrc4.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass4)))
                                    else:
                                            otherIrc4.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass4)))
                            if netcheck4 is True:
                                    self.usecommand(irc, "login {0} {1}".format(name4, pswd4), 4 )
                                    connectfail4 = 0
                                    interval = 45
                                    self.looper(irc)
                                    intervaldisable = True
                                
        if char5 is True:
                online5 = False
                if rawstatsmode is False and webworks is True:
                    try:
                            if(myentry5[15] == "1"):
                                    online5 = True
                    except KeyError:
                            self.reply(irc, playbottext + " - Key Error", 5)
                    except TypeError:
                                self.reply(irc, playbottext + " - Character {0} does not exist".format(name5),5 )
                    except RuntimeError:
                            self.reply(irc, playbottext + " - Recursion Error",5 )

                if botcheck5 is True:
                        try:
                            hosttest5 = otherIrc5.state.nickToHostmask(botname5)
                            if bothostmask5 in hosttest5:
                                    bothostcheck5 = True
                        except TypeError:
                            bothostcheck5 = False
                        except KeyError:
                            bothostcheck5 = False

                if botcheck5 is True:
                        opcheck5 = False
                        try:
                                ops = otherIrc5.state.channels[channame5].ops
                                halfops = otherIrc5.state.channels[channame5].halfops
                                for user in ops:
                                    if botname5 == user:
                                        opcheck5 = True
                                for user in halfops:
                                    if botname5 == user:
                                        opcheck5 = True
                        except KeyError:
                            self.reply(irc, playbottext + " - Key Error", 5)

                if rawstatsmode is False and webworks is True and online5 is False and botcheck5 is True:
                        if(opcheck5 is True) or (opcheck5 is False and bothostcheck5 is True):
                            if(nickserv5 is True):
                                    if("dalnet" in netname5.lower()):
                                            otherIrc5.queueMsg(ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY {0}".format(nickservpass5)))
                                    else:
                                            otherIrc5.queueMsg(ircmsgs.privmsg("nickserv", "identify {0}".format(nickservpass5)))
                            if netcheck5 is True:
                                    self.usecommand(irc, "login {0} {1}".format(name5, pswd5), 5 )
                                    connectfail5 = 0
                                    interval = 45
                                    self.looper(irc)
                                    intervaldisable = True

        if botcheck1 is True or botcheck2 is True or botcheck3 is True or botcheck4 is True or botcheck5 is True:
                if itemslists is None and rawstatsmode is False and intervaldisable is False:
                        interval = 30
                        self.looper(irc)
                        intervaldisable = True
        if botcheck1 is False and botcheck2 is False and botcheck3 is False and botcheck4 is False and botcheck5 is False and intervaldisable is False:
            interval = 300
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
                # build data structure from player data for figuring bests
                if char1 is True:
                        self.newitemslister(irc, 1, 2)
                if char2 is True:
                        self.newitemslister(irc, 2, 2)
                if char3 is True:
                        self.newitemslister(irc, 3, 2)
                if char4 is True:
                        self.newitemslister(irc, 4, 2)
                if char5 is True:
                        self.newitemslister(irc, 5, 2)
                
                if char1 is True and botcheck1 is True and itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == name):
                                        level = entry[2]
                                        bets = entry[22]
                        if(bets < 5 and level >= 30):
                               try:
                                   betdiff = (5 - bets)
                                   self.bet_bet(irc, betdiff, 1)
                               except TypeError:
                                   bets = 5
                if char2 is True and botcheck2 is True and itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == name2):
                                        level2 = entry[2]
                                        bets2 = entry[22]
                        if(bets2 < 5 and level2 >= 30):
                               try:
                                   betdiff = (5 - bets2)
                                   self.bet_bet(irc, betdiff, 2)
                               except TypeError:
                                   bets2 = 5
                if char3 is True and botcheck3 is True and itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == name3):
                                        level3 = entry[2]
                                        bets3 = entry[22]
                        if(bets3 < 5 and level3 >= 30):
                               try:
                                   betdiff = (5 - bets3)
                                   self.bet_bet(irc, betdiff, 3)
                               except TypeError:
                                   bets3 = 5
                if char4 is True and botcheck4 is True and itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == name4):
                                        level4 = entry[2]
                                        bets4 = entry[22]
                        if(bets4 < 5 and level4 >= 30):
                               try:
                                   betdiff = (5 - bets4)
                                   self.bet_bet(irc, betdiff, 4)
                               except TypeError:
                                   bets4 = 5
                if char5 is True and botcheck5 is True and itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == name5):
                                        level5 = entry[2]
                                        bets5 = entry[22]
                        if(bets5 < 5 and level5 >= 30):
                               try:
                                   betdiff = (5 - bets5)
                                   self.bet_bet(irc, betdiff, 5)
                               except TypeError:
                                   bets5 = 5

                if char1 is True and botcheck1 is True:
                        self.spendmoney(irc, 1)
                        self.aligncheck(irc, 1)
                if char2 is True and botcheck2 is True:
                        self.spendmoney(irc, 2)
                        self.aligncheck(irc, 2)
                if char3 is True and botcheck3 is True:
                        self.spendmoney(irc, 3)
                        self.aligncheck(irc, 3)
                if char4 is True and botcheck4 is True:
                        self.spendmoney(irc, 4)
                        self.aligncheck(irc, 4)
                if char5 is True and botcheck5 is True:
                        self.spendmoney(irc, 5)
                        self.aligncheck(irc, 5)

                if char1 is True and botcheck1 is True:
                        self.timercheck(irc, 1)
                if char2 is True and botcheck2 is True:
                        self.timercheck(irc, 2)
                if char3 is True and botcheck3 is True:
                        self.timercheck(irc, 3)
                if char4 is True and botcheck4 is True:
                        self.timercheck(irc, 4)
                if char5 is True and botcheck5 is True:
                        self.timercheck(irc, 5)
                
                if char1 is True and botcheck1 is True and itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == name):
                                        level = entry[2]
                                        fights = entry[16]
                        if(level >= 10 and level <= 200):
                                if(fights < 5):
                                        self.fight_fight(irc, 1)
                if char2 is True and botcheck2 is True and itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == name2):
                                        level2 = entry[2]
                                        fights2 = entry[16]
                        if(level2 >= 10 and level2 <= 200):
                                if(fights2 < 5):
                                        self.fight_fight(irc, 2)
                if char3 is True and botcheck3 is True and itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == name3):
                                        level3 = entry[2]
                                        fights3 = entry[16]
                        if(level3 >= 10 and level3 <= 200):
                                if(fights3 < 5):
                                        self.fight_fight(irc, 3)
                if char4 is True and botcheck4 is True and itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == name4):
                                        level4 = entry[2]
                                        fights4 = entry[16]
                        if(level4 >= 10 and level4 <= 200):
                                if(fights4 < 5):
                                        self.fight_fight(irc, 4)
                if char5 is True and botcheck5 is True and itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == name5):
                                        level5 = entry[2]
                                        fights5 = entry[16]
                        if(level5 >= 10 and level5 <= 200):
                                if(fights5 < 5):
                                        self.fight_fight(irc, 5)

        if webworks is True and char1 is True and newlist != None:
             for entry in newlist:
                 if(entry[5] == 1):
                     levelrank1 = entry[3]
        
        rawstatsmodeon = False
        rawplayersmodeon = False
        opswitch = False
        if(opcheck is False or opcheck2 is False or opcheck3 is False or opcheck4 is False or opcheck5 is False):
                opswitch = True
        if(rawstatsswitch is False and rawstatsmode is True and webworks is True and ttlfrozenmode is False and opswitch is False):
                rawplayersmodeon = True
        if(rawstatsswitch is False and rawstatsmode is False and webworks is False and webfail >= 3 and opswitch is False):
                rawstatsmodeon = True
        if(levelrank1 < laglevel and rawstatsswitch is True and rawstatsmode is True and opswitch is False):
                if(nolag1 is False or nolag2 is False or nolag3 is False or nolag4 is False or nolag5 is False):
                        rawplayersmodeon = True
        if(levelrank1 >= laglevel and rawstatsswitch is True and rawstatsmode is False and opswitch is False):
                rawstatsmodeon = True
        if(rawstatsmode is True and opswitch is True):
                rawplayersmodeon = True
        if rawstatsmodeon is True:
             rawstatsmode = True
             if bottextmode is True:
                     self.replymulti(irc, playbottext + " - Rawstats Mode Activated")
             self.configwrite()
        if rawplayersmodeon is True:
                rawstatsmode = False
                if botcheck1 is True or botcheck2 is True or botcheck3 is True or botcheck4 is True or botcheck5 is True:
                        self.webdata(irc)
                        self.newitemslister(irc, 1, 1)
                if bottextmode is True:
                        self.replymulti(irc, playbottext + " - Rawplayers Mode Activated")
                if char1 is True:
                        rawmyentry = None
                if char2 is True:
                        rawmyentry2 = None
                if char3 is True:
                        rawmyentry3 = None
                if char4 is True:
                        rawmyentry4 = None
                if char5 is True:
                        rawmyentry5 = None
                self.configwrite()

        ttlrawstatson = False
        if(rawstatsmode is False and webworks is True and opswitch is False):
                if(char1 is True and botcheck1 is True and itemslists != None):
                        for entry in itemslists:
                                if(entry[0] == name):
                                        ttl = entry[17]
                        if online1 is True:
                                if ttl == oldttl:
                                        if errortextmode is True:
                                                self.replymulti(irc, playbottext + " - TTL Frozen1")
                                        ttlfrozen1 += 1
                        if ttlfrozen1 > charcount:
                                if(nolag1 is True) or (nolag1 is False and levelrank1 >= laglevel):
                                        ttlrawstatson = True
                if(char2 is True and botcheck2 is True and itemslists != None):
                        for entry in itemslists:
                                if(entry[0] == name2):
                                        ttl2 = entry[17]
                        if online2 is True:
                                if ttl2 == oldttl2:
                                        if errortextmode is True:
                                                self.replymulti(irc, playbottext + " - TTL Frozen2")
                                        ttlfrozen2 += 1
                        if ttlfrozen2 > charcount:
                                if(nolag2 is True) or (nolag2 is False and levelrank1 >= laglevel):
                                        ttlrawstatson = True
                if(char3 is True and botcheck3 is True and itemslists != None):
                        for entry in itemslists:
                                if(entry[0] == name3):
                                        ttl3 = entry[17]
                        if online3 is True:
                                if ttl3 == oldttl3:
                                        if errortextmode is True:
                                                self.replymulti(irc, playbottext + " - TTL Frozen3")
                                        ttlfrozen3 += 1
                        if ttlfrozen3 > charcount:
                                if(nolag3 is True) or (nolag3 is False and levelrank1 >= laglevel):
                                        ttlrawstatson = True
                if(char4 is True and botcheck4 is True and itemslists != None):
                        for entry in itemslists:
                                if(entry[0] == name4):
                                        ttl4 = entry[17]
                        if online4 is True:
                                if ttl4 == oldttl4:
                                        if errortextmode is True:
                                                self.replymulti(irc, playbottext + " - TTL Frozen4")
                                        ttlfrozen4 += 1
                        if ttlfrozen4 > charcount:
                                if(nolag4 is True) or (nolag4 is False and levelrank1 >= laglevel):
                                        ttlrawstatson = True
                if(char5 is True and botcheck5 is True and itemslists != None):
                        for entry in itemslists:
                                if(entry[0] == name5):
                                        ttl5 = entry[17]
                        if online5 is True:
                                if ttl5 == oldttl5:
                                        if errortextmode is True:
                                                self.replymulti(irc, playbottext + " - TTL Frozen5")
                                        ttlfrozen5 += 1
                        if ttlfrozen5 > charcount:
                                if(nolag5 is True) or (nolag5 is False and levelrank1 >= laglevel):
                                        ttlrawstatson = True
                if ttlrawstatson is True:
                        rawstatsmode = True
                        ttlfrozenmode = True
                        if bottextmode is True:
                                self.replymulti(irc, playbottext + " - Rawstats Mode Activated")

                if (ttlfrozen1 > charcount or ttlfrozen2 > charcount or ttlfrozen3 > charcount or ttlfrozen4 > charcount or ttlfrozen5 > charcount):
                        ttlfrozen1 = 0
                        ttlfrozen2 = 0
                        ttlfrozen3 = 0
                        ttlfrozen4 = 0
                        ttlfrozen5 = 0

        return 1
    
    def intervalcalc(self, irc):
        global interval
        global level
        global fights
        global bets
        global char1
        global char2
        global char3
        global char4
        global char5
        global itemslists
        global botcheck1
        global botcheck2
        global botcheck3
        global botcheck4
        global botcheck5
        global rawstatsmode
        global webworks
        global rawmyentry
        global rawmyentry2
        global rawmyentry3
        global rawmyentry4
        global rawmyentry5
        global name
        global name2
        global name3
        global name4
        global name5
        
        sixty = 60
        level2 = 0
        fights2 = 0
        bets2 = 0
        level3 = 0
        fights3 = 0
        bets3 = 0
        level4 = 0
        fights4 = 0
        bets4 = 0
        level5 = 0
        fights5 = 0
        bets5 = 0

        if char1 is True:
                if rawstatsmode is False and itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == name):
                                        level = entry[2]
                                        fights = entry[16]
                                        bets = entry[22]
                if rawstatsmode is True and rawmyentry != None:
                                level = int(rawmyentry[1])
                                fights = int(rawmyentry[11])
                                bets = int(rawmyentry[13])
        if char2 is True:
                if rawstatsmode is False and itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == name2):
                                        level2 = entry[2]
                                        fights2 = entry[16]
                                        bets2 = entry[22]
                if rawstatsmode is True and rawmyentry2 != None:
                                level2 = int(rawmyentry2[1])
                                fights2 = int(rawmyentry2[11])
                                bets2 = int(rawmyentry2[13])
        if char3 is True:
                if rawstatsmode is False and itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == name3):
                                        level3 = entry[2]
                                        fights3 = entry[16]
                                        bets3 = entry[22]
                if rawstatsmode is True and rawmyentry3 != None:
                                level3 = int(rawmyentry3[1])
                                fights3 = int(rawmyentry3[11])
                                bets3 = int(rawmyentry3[13])
        if char4 is True:
                if rawstatsmode is False and itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == name4):
                                        level4 = entry[2]
                                        fights4 = entry[16]
                                        bets4 = entry[22]
                if rawstatsmode is True and rawmyentry4 != None:
                                level4 = int(rawmyentry4[1])
                                fights4 = int(rawmyentry4[11])
                                bets4 = int(rawmyentry4[13])
        if char5 is True:
                if rawstatsmode is False and itemslists != None:
                        for entry in itemslists:
                                if(entry[0] == name5):
                                        level5 = entry[2]
                                        fights5 = entry[16]
                                        bets5 = entry[22]
                if rawstatsmode is True and rawmyentry5 != None:
                                level5 = int(rawmyentry5[1])
                                fights5 = int(rawmyentry5[11])
                                bets5 = int(rawmyentry5[13])

        interval = 5
        interval *= 60                  # conv from min to sec
        intervallist = []
        if char1 is True:
                if botcheck1 is False:
                        intervallist.append( ( "interval", sixty ) )
                if botcheck1 is True:
                        if(level >= 10 and level < 30 and webworks is True):
                                if(fights < 5):
                                        intervallist.append( ( "interval", sixty ) )
                        if(bets == 5 and fights < 5 and level <= 200 and webworks is True):
                                intervallist.append( ( "interval", sixty ) )
                        if(bets < 5 and level >= 30 and webworks is True):
                                intervallist.append( ( "interval", sixty ) )
        if char2 is True:
                if botcheck2 is False:
                        intervallist.append( ( "interval", sixty ) )
                if botcheck2 is True:
                        if(level2 >= 10 and level2 < 30 and webworks is True):
                                if(fights2 < 5):
                                        intervallist.append( ( "interval", sixty ) )
                        if(bets2 == 5 and fights2 < 5 and level2 <= 200 and webworks is True):
                                intervallist.append( ( "interval", sixty ) )
                        if(bets2 < 5 and level2 >= 30 and webworks is True):
                                intervallist.append( ( "interval", sixty ) )
        if char3 is True:
                if botcheck3 is False:
                        intervallist.append( ( "interval", sixty ) )
                if botcheck3 is True:
                        if(level3 >= 10 and level3 < 30 and webworks is True):
                                if(fights3 < 5):
                                        intervallist.append( ( "interval", sixty ) )
                        if(bets3 == 5 and fights3 < 5 and level3 <= 200 and webworks is True):
                                intervallist.append( ( "interval", sixty ) )
                        if(bets3 < 5 and level3 >= 30 and webworks is True):
                                intervallist.append( ( "interval", sixty ) )
        if char4 is True:
                if botcheck4 is False:
                        intervallist.append( ( "interval", sixty ) )
                if botcheck4 is True:
                        if(level4 >= 10 and level4 < 30 and webworks is True):
                                if(fights4 < 5):
                                        intervallist.append( ( "interval", sixty ) )
                        if(bets4 == 5 and fights4 < 5 and level4 <= 200 and webworks is True):
                                intervallist.append( ( "interval", sixty ) )
                        if(bets4 < 5 and level4 >= 30 and webworks is True):
                                intervallist.append( ( "interval", sixty ) )
        if char5 is True:
                if botcheck5 is False:
                        intervallist.append( ( "interval", sixty ) )
                if botcheck5 is True:
                        if(level5 >= 10 and level5 < 30 and webworks is True):
                                if(fights5 < 5):
                                        intervallist.append( ( "interval", sixty ) )
                        if(bets5 == 5 and fights5 < 5 and level5 <= 200 and webworks is True):
                                intervallist.append( ( "interval", sixty ) )
                        if(bets5 < 5 and level5 >= 30 and webworks is True):
                                intervallist.append( ( "interval", sixty ) )

        intervallist.sort( key=operator.itemgetter(1), reverse=True )
        diff = 999999        
        for entry in intervallist:
                if(entry[1] < diff):
                        interval = entry[1]

        self.looper(irc)

    def looper(self, irc):
        global interval
        global gameactive
        global intervaltextmode
        global playbottext
        
        def looppm():
            self.main(irc)
        nextTime = time.time() + interval
        
        if intervaltextmode is True:
                self.replymulti(irc, playbottext + " - Checking timers every {0} minutes".format(interval // 60))
        if gameactive is True:
            try:
                schedule.addEvent(looppm, nextTime, "looppm")
            except AssertionError:
                schedule.removeEvent('looppm')
                schedule.addEvent(looppm, nextTime, "looppm")                        
        
    def __init__(self, irc):
        self.__parent = super(PlayBotMulti, self)
        self.__parent.__init__(irc)

        if autostartmode is True:
                self.autostart(irc)


Class = PlayBotMulti


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
