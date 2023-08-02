import discord
from discord.ext import commands, tasks
import asyncio
import mariadb
import zones
from lifunctions import tryUpdateGMTickets
from lifunctions import tryUpdateOnlineCount
from lifunctions import tryReportAuditGM
from lifunctions import tryResponse
from lifunctions import isGM
from cog import CCog
import global_defines
import liliconfigs

global_defines.init()
# https://discordpy.readthedocs.io/en/stable/api.html#discord.Intents
intents=discord.Intents.default()
intents.message_content = True
global_defines.client = discord.Client(intents=intents)
print("Establishing database connection...")
db = mariadb.connect(user=liliconfigs.dbuser, \
        password=liliconfigs.dbpass, \
        host=liliconfigs.dbhost, \
        port=liliconfigs.dbport, \
        database=liliconfigs.dbname,
        autocommit=True)

global_defines.cursor = db.cursor(buffered=True)
print("Database connection established!")
global_defines.bot_ready = False
global_defines.cog = CCog() # task manager

    

##############################
#           Events           #
##############################

@global_defines.client.event
async def on_ready():
    print("Successfully logged in as user " + str(global_defines.client.user) + "!")
    global_defines.bot_ready = True
    global_defines.cog.startTasks()

@global_defines.client.event
async def on_disconnect():
    print("Bot disconnected, attempting to reconnect...")

@global_defines.client.event
async def on_message(message):
    if global_defines.bot_ready == False or message.author == global_defines.client.user:
        return
    
    await tryResponse(message)

@global_defines.client.event
async def on_guild_channel_create(channel):
    if global_defines.bot_ready == False:
        return
    if "[ip exception]" in channel.category.name.lower():
        await channel.send("Hello! You should understand that an account exception ties the 2nd account to yours and that they share in punishment in the event of any rule infractions. "
                           "You are not allowed to play each others accounts or to effectively use them as a crafting mule. Any action taken "
                           "due to suspicion of dual boxing/suspect activity is at the sole discretion of the GM team. Do you agree to these conditions?\n\n"
                           "Additionally, I will require some form of verification where I can clearly see 2 work/play setups in the same domicile. A picture of the computer stations "
                           "with timestamps will suffice. You do not need to show people in the picture, but it can help expedite the process so long as you clearly show there are 2 "
                           "real people living in the house wanting to play.\n\n"
                           "Please remember to include your account name and the email associated with your account in this ticket. In addition, it is required that the other "
                           "party that will be using the second account also has a phone-verified Discord account and can post in this Discord server so please include their Discord "
                           "tag here (i.e. JoeM#5106). Once you have posted all required information as well as "
                           "an \"I agree\" to the terms above along with sufficient timestamped photos, a staff member will greet you in this channel to add the second party to "
                           "this ticket and begin processing your request. "
                           "If you do not agree to the terms, you can click the padlock icon on the ticket to close it, and then the green checkmark to confirm. \n"
                           "🔸 Please include any information or screenshots before GMs come into the ticket. A blank ticket will be deleted. \n"
                           "Please do not tag or @ GMs or Staff, this will only delay a response to your ticket.")
                           
    if "[player report]" in channel.category.name.lower():
        await channel.send("Hello! Please provide the following information: \n"
                            "🔸 Include your own character name in the ticket. \n"
                            "🔸 The character name of the person you are reporting, describe IN DETAIL what you think is wrong/went wrong, what rule is being broken, etc \n"
                            "🔸 If a player was being mean to you verbally in game, /blist add playername. Most situations can be avoided with this. \n"
                            "🔸 Depending on the situation, such as MPK attempts, video evidence is preferred to have over pictures just so the GMs or staff helping you out can have the best chance to help you out. More often than not, it's difficult to do anything about it without us physically being there. It helps us see what exactly happened when we weren't there ourselves. \n"
                            "🔸 There are many video recording softwares such as NVIDIA's shadowplay (which is built into your graphics card and defaulted to be turned on if you have that brand of GPU), streamlabs, twitch streams/clips, local recording, etc are just examples of video recording abilities. \n"
                            "🔸 Please include any information or screenshots before GMs come into the ticket. A blank ticket will be deleted. \n"
                            "Please do not tag or @ GMs or Staff, this will only delay a response to your ticket.")
                            
    if "bcnm/ksnm" in channel.category.name.lower():
        await channel.send("Hello! Please provide the following information: \n"
                             "🔸 Include your own character name in the ticket. \n"
                             "🔸 Include the BCNM/KSNM name and the orb name, or which Maat fight you are attempting to defeat. \n"
                             "🔸 A picture or video of the zone crashing, the battlefield is empty, Loot in the pool but the zone is crashing, etc will suffice as enough evidence to have orbs and/or loot returned to you. Include a list of the names of the people and what loot to be given to them. \n"
                             "🔸 No evidence will result in a lost orb or testimony. Sorry! \n"
                             "🔸 Please include any information or screenshots before GMs come into the ticket. A blank ticket will be deleted. \n"
                             "Please do not tag or @ GMs or Staff, this will only delay a response to your ticket.")

    if "mission / quest" in channel.category.name.lower():                        
        await channel.send("Hello! Please provide the following information: \n"
                             "🔸 Include your own character name in the ticket. \n"
                                "🔸 Include the mission/quest name, the part you are at, the wiki link (if applicable) of the quest aor mission, and a list of others with you that are stuck on the quest/mission as well. \n"
                                "🔸 Pictures of what's going wrong, proof of you getting NPC dialogue, etc will greatly enhance our ability to help you out as fast as possible. \n"
                                "🔸 Help will not be given if you play at something other than 30 fps. The game was originally designed to play at 30 fps, and the launcher Wings uses defaults the game at 60 fps (/fps 1 for Ashita). To reduce your fps to 30, type '/fps 2' in game on Ashita. \n"
                                "🔸 Help will not be given if you use cutscene skippers. Your variables will be returned to the previous spot so that it forces you to redo whatever you finished. \n"
                                "🔸 Make sure you have the correct /ver number. The correct version # is 30190305_0. \n"
                                "🔸 Please include any information or screenshots before GMs come into the ticket. A blank ticket will be deleted. \n"
                                "Please do not tag or @ GMs or Staff, this will only delay a response to your ticket.")

    if "zone / r0" in channel.category.name.lower():                        
        await channel.send("Hello! Please provide the following information: \n"
                             "🔸 Include your own character name in the ticket. \n"
                                "🔸 A picture/video of the zone R0ing is required to refund BCNM / other instances. \n"
                                "🔸 A picture/video of the treasure pool and the zone crashing will be enough evidence to give you guys back the loot you need returned. \n"
                                "🔸 Big zone crashes (city zones, for example) are talked about a lot in general chat in the discord. Please look there before making a ticket here. We don't need 10+ people telling us a city crashed when we read it in general chat. \n"
                                "🔸 Please include any information or screenshots before GMs come into the ticket. A blank ticket will be deleted. \n"
                                "Please do not tag or @ GMs or Staff, this will only delay a response to your ticket.")
                                
    if "nm/hnm" in channel.category.name.lower():                        
        await channel.send("Hello! Please provide the following information: \n"
                            "🔸 Include your own character name in the ticket. \n"
                            "🔸 If an NM/HNM died and the zone crashed, and there was loot in the treasure, take a picture with: \n"
                                      "1. The treasure list visible, along with \n"
                                      "2. The picture of the zone crashing visible \n"
                                      "If this is the case, include the list of the player names of who you wasnt the loot given to \n"
                            "🔸 If a zone crashed that had an NM or HNM in it and it was alive, a picture of the zone crashing as well as you currently fighting the NM will be required. ALL NM AND HNMs WILL BE RETURNED TO THE PERSON/GROUP WITH CLAIM AT THE TIME A ZONE CRASHES. \n "
                            "🔸 Most NMs and HNMs persist through zone crashes and will pop on next PH death if sufficient time has passed. \n" 
                            "🔸 Please include any information or screenshots before GMs come into the ticket. A blank ticket will be deleted. \n"
                            "Please do not tag or @ GMs or Staff, this will only delay a response to your ticket.")
                                
    if "other" in channel.category.name.lower():                        
        await channel.send("Hello! Please provide the following information: \n"
                            "🔸 Include your own character name in the ticket. \n"
                            "🔸 Please include any information or screenshots before GMs come into the ticket. A blank ticket will be deleted. \n"
                            "Please do not tag or @ GMs or Staff, this will only delay a response to your ticket.")
                            
    if "email" in channel.category.name.lower():                        
        await channel.send("Hello! Please provide the following information: \n"
                            "🔸 Please include both your Account name and Email that you are trying to verify the account for. \n"
                            "🔸 Please include any information or screenshots before GMs come into the ticket. A blank ticket will be deleted. \n"
                            "Please do not tag or @ GMs or Staff, this will only delay a response to your ticket.")
    if "gm application" in channel.category.name.lower():
        await channel.send("Hello!  Thanks for your interest in applying to be a GM.  Feel free to share with us in this channel why you think that you'd be an asset to the team! \n"
                           "These tickets may not get an immediate staff response, but do not worry, that is normal!  We are leaving these tickets open for a few days so that everyone on staff has a chance to review the applicant pool. \n"
                           "If a member of staff has any additional questions for you during this time, they'll leave it here.  Thanks for your interest!")
                                
global_defines.client.run(liliconfigs.discordAPIKey)