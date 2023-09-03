import discord
from discord.ext import commands, tasks
import asyncio
import mariadb
import zones
import global_defines
#import MySQLdb
import os
import time
import re
import subprocess

##############################
#         Functions          #
##############################

# checks if a user is in a role designated as "GM"
def isGM(user):
    for role in user.roles:
        if "game master" in role.name.lower() or "admin" in role.name.lower() or "janitor" in role.name.lower() or "antisocial" in role.name.lower() or "sr dev" in role.name.lower():
            #print("wastrue")
            return True
    #print("wasfalse")
    return False

def isSeniorStaffChannel(channel):
    channels = [
        "senior-chat"
    ]
    channelName = channel.name.lower()
    if channelName in channels:
        return True
    return False

def isStaffChannel(channel):
    channels = [
        "bot-commands",
        "staff-chat",
        "senior-chat",
        "baby-gms",
        "gm-chat",
        "staff-lounge"
    ]
    prefixes = [
        "ticket"
    ]
    channelName = channel.name.lower()
    if isSeniorStaffChannel(channel) or channelName in channels or channelName.split('-') in prefixes:
        return True
    return False

# Outputs the results of an array of sql queries to the requested channel
def sqlOutput(sqlQueries):
    fullOutput = []
    for sqlQuery in sqlQueries:
        global_defines.cursor.execute(sqlQuery)
        fullOutput.append("Results: " + str(global_defines.cursor.rowcount))
        columns = global_defines.cursor.description 
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in global_defines.cursor.fetchall()]
        output = ""
        count = 0
        for col in columns:
            count += 1
            output += "<="+str(count)+"=>" + str(col[0])
        fullOutput.append(output)
        
        for result in results:
            output = ""
            count = 0
            for col in columns:
                count += 1
                output += "<="+str(count)+"=>" + str(result[col[0]])
            fullOutput.append(output)
    # join lines of output until the discord max per send
    output = []
    for line in fullOutput:
        if len(output) == 0 or (len(output[-1]) + len(line) > 1800):
            # terminate current message with code wrapper and start new one
            if len(output) > 0:
                output[-1] += "\n```"
            output.append("```\n" + line)
        else:
            output[-1] += "\n" + line
    output[-1] += "\n```"
    return output

def audit_gm(hours):
    if hours == 0:
        hours = 36

    return sqlOutput(["select zone_settings.name as zone,audit_gm.* from audit_gm left join zone_settings using (zoneid) where date_time > date_add(now(), interval -{} hour) order by gm_name,date_time desc".format(hours)])

async def tryResponse(mess):
    msg = mess.content.lower()
    
    if "good bot" in msg:
        await mess.channel.send(":D")
    elif "bad bot" in msg:
        await mess.channel.send("D:")
    elif "stupid bot" in msg:
        await mess.channel.send("; ;")
    elif "weeb bot" in msg:
        await mess.channel.send("OREWA SHINDEIRU")
    elif "gaga bot" in msg:
        await mess.channel.send("RAH RAH AH AH AH")
    elif "rissa" in msg and False: #todo: festivus onry
        await mess.channel.send("You're a very beautiful girl, no sarcasm intended. I don't even know you. I respect all players equally. I have done nothing to you but try to help. I never simped for you. I never cared for you because you were a girl. You were a part of my LS once, and I only cared to HELP you because of that. ANYONE who has anything negative to say about me is full of it, because ANYONE who knows me KNOWS the type of player I am. It's a shame that you can't see past the nonsense and continue to throw shade @ me when i've done nothing wrong to you. IDK anyone in this game, but I treat everyone w/ respect. Too bad not all can reciprocate that.. Let me treat you unjust so that you may do the same, until then you shall never find happiness.")
    elif msg.startswith("enhance") or msg.startswith("$enhance"):
        await mess.channel.send("https://tenor.com/view/enhance-gif-10953787")
    elif "can't do that" in msg:
        await mess.channel.send("https://tenor.com/view/itysl-i-think-you-should-leave-tim-robinson-you-cant-do-that-cant-gif-23125076")
    elif "know everything" in msg:
        await mess.channel.send("https://tenor.com/view/itysl-everything-dont-know-everybody-gif-25351975")

    # commands only allowed by "GM" roles. These are inserted into the audit_gm table
    if msg.startswith("$") and isGM(mess.author):
        if not (' ' in msg):
            await mess.channel.send("no actual command sent? Maybe we should make a $help command")
            # TODO put helpful info here
            return

        # record the discord command in db
        sqlQuery = "INSERT into audit_gm (date_time,zoneid,gm_name,command,full_string) VALUES(current_timestamp(),0,'{}','{}','{}')".format(
            mess.author.name,
            msg.split(' ')[0],
            msg
        )
        global_defines.cursor.execute(sqlQuery)

        if msg.startswith("$service"):
        
            username_lookup = {
                'MowFord':  'Daddy',
                'Twilight': 'Twi twi',
                'Gweivyth': 'sir, bossman',     
                'Wildclaws': 'sir!  Or should I say...yes fur'}
            
            username = mess.author.name
            
            if username in username_lookup:
                await mess.channel.send("Yes " + username_lookup[username] + " " + username + "!")
            else:
                await mess.channel.send("Wait... Who are you again? " + username + "...")
                
            words = ["",""]
            word_id = 0
            
            words = msg.split(' ')

            command = words[1]
            cluster = ''
            if len(words) > 2:
                cluster = words[2]
            extra = ''
            if len(words) > 3:
                extra = words[3]
            
            try:
                h_debugged = open("clusters_debug.txt")
                for debugged_cluster in h_debugged:
                    cur_clust = debugged_cluster.strip()
                    if cur_clust == cluster:
                        h_debugged.close()
                        await mess.channel.send("Devs told me not to reset " + cluster + "while they are debugging it -- try asking them..")
                        return
                    if cur_clust == "everything":
                        h_debugged.close()
                        await mess.channel.send("Devs told me not to reset any clusters while they are debugging things -- try asking them..")
                        return
                h_debugged.close()
            except IOError:
                pass

            #clusterName = "wings2-live_" + cluster
            clusterName = subprocess.getoutput("powershell \"& {(get-service wings2-live_* | ? {$_.name -ne 'wings2-live_LilisetteBot' -and ($_.name -like '*_" + cluster + "' -or $_.displayname.split(' ')[3] -eq '" + cluster + "')}).name \"}")
            clusterName = clusterName.replace("'", "`'")
            if '_' in clusterName or command in 'list':
                if command == "restart":
                    await mess.channel.send("Please wait while I restart " + clusterName)
                    output = subprocess.getoutput("powershell \"& {restart-service " + clusterName + " \"}")
                    await mess.channel.send("Lily has finished resetting " + clusterName + " for you!")
                    await mess.channel.send(output)
                elif command == "info":
                    output = subprocess.getoutput("powershell \"& {get-service " + clusterName + " | %{$_.name + ';' + $_.displayname + ';' + $_.status + ';' + (get-wmiobject win32_service | where { $_.name -eq '" + clusterName + "'}).processID} }\" ")
                    await mess.channel.send(output)
                    pid = output.split(';')[3]
                    #output = subprocess.getoutput("powershell \"& {$filter = `\"Name eq '" + clusterName + "'`\" ; $filter }\" ") # $id = (Get-WmiObject -Class Win32_Service -Filter $filter).ProcessId ; (get-process -id ((Get-CimInstance Win32_Process -Filter `\"name <> 'conhost.exe' and ParentProcessId = $id`\").processid -join ','))).id}\" "
                    #await mess.channel.send(output)
                elif command == "logs":
                    if not isStaffChannel(mess.channel):
                        await mess.channel.send("https://tenor.com/view/itysl-i-think-you-should-leave-tim-robinson-you-cant-do-that-cant-gif-23125076")
                        return
                    buffer = 500
                    filterOut = " 0C0 "
                    filterIn = ''
                    if extra != '':
                        filterIn = extra
                        buffer = 50000
                    output = subprocess.getoutput("powershell \"& {get-content -tail " + str(buffer) + " c:/workspace/servicelogs/"+clusterName+"_* | ? {$_ -notmatch '" + filterOut + "' -and $_ -match '" + filterIn + "'}}\" ")
                    # shrink to fit in discord output
                    output2 = "".join(reversed("".join(reversed(output))[1:2000:]))
                    await mess.channel.send(output2)
                elif command == "list":
                    if not isStaffChannel(mess.channel):
                        await mess.channel.send("https://tenor.com/view/itysl-i-think-you-should-leave-tim-robinson-you-cant-do-that-cant-gif-23125076")
                        return
                    output = subprocess.getoutput("powershell \"& {get-service wings2-live_* | %{$_.name.split('_')[1] + ';' + $_.displayname.split(' ')[3]} \"}")
                    await mess.channel.send(output)
                elif command == "zones":
                    if not isStaffChannel(mess.channel):
                        await mess.channel.send("https://tenor.com/view/itysl-i-think-you-should-leave-tim-robinson-you-cant-do-that-cant-gif-23125076")
                        return
                    zonePort = clusterName.split('_')[1]
                    if zonePort.isdigit():
                        sqlQueries = []
                        # list zones assigned to service and all current player sessions
                        sqlQueries.append("SELECT zoneid,zonetype,concat(zoneip,':',zoneport) as ip,name,a.* from zone_settings LEFT JOIN (SELECT chars.accid,chars.charid,charname,pos_zone from accounts_sessions LEFT join chars USING (charid) WHERE server_port = " + str(zonePort) + ") AS a ON a.pos_zone = zoneid WHERE zoneport = " + str(zonePort))
                        for output in sqlOutput(sqlQueries):
                            await mess.channel.send(output)
                    else:
                        await mess.channel.send("Not a valid map server service")
                else:
                    await mess.channel.send("invalid service command (" + command +")")
            else:
                await mess.channel.send("Service not found.")
            
            return
        
        if isStaffChannel(mess.channel):
            if msg.startswith("$closeweb"):
                pinned_message = 0     
                pins = await mess.channel.pins()
                for temp_message in pins:
                    if temp_message.author == global_defines.client.user:
                        pinned_message = temp_message
                        break
            
                if pinned_message == 0:
                    print("Error! Lilisette's pinned message was not found!")
                    return
                
                web_ticket_id = ""
                i = 0
                try:
                    i = pinned_message.content.index("webID ") + 6
                except:
                    print("Error! Lilisette's pinned message doesn't contain the webID!")
                    return
                
                while pinned_message.content[i] in "0123456789":
                    web_ticket_id += pinned_message.content[i]
                    i += 1
                global_defines.cursor.execute("UPDATE ffxiwings.server_gmcalls SET status = 3 WHERE callid IN (" + web_ticket_id + ") AND status NOT IN (3) LIMIT 1;")
                
                if global_defines.cursor.rowcount == 0:
                    await mess.channel.send("The associated web ticket is already closed!")
                else:
                    await mess.channel.send("The associated web ticket has been successfully closed!")
                    global_defines.cursor.execute("UPDATE ffxiwings.server_gmcalls SET assignee = 'Lilisette' WHERE callid IN (" + web_ticket_id + ") LIMIT 1;")
                    
                    closed_category = 0
                    for guild in global_defines.client.guilds:
                        for category in guild.categories:
                            if "closed tickets" in category.name.lower():
                                closed_category = category
                                break
                    if closed_category == 0:
                        print("Error! There is no closed tickets category!")
                        return
                    
                    await mess.channel.move(category=closed_category,end=True)
                    
            if msg.startswith("$verify"):
                words = ["","",""]
                word_id = 0
                for letter in msg:
                    if letter != " ":
                        words[word_id] += letter
                    else:
                        word_id += 1
                
                if word_id != 2:
                    await mess.channel.send("Incorrect syntax! Command must be \"$verify [account] [email]\" to verify an email.")
                    return
                
                account = words[1]
                email = words[2]
                
                if "'" in account or "'" in email:
                    await mess.channel.send("Invalid account name or email.")
                    return
                
                global_defines.cursor.execute("SELECT * FROM wingslogin.ww_accounts WHERE username IN ('" + account + "') AND email IN ('" + email + "') LIMIT 1;")
                
                if global_defines.cursor.rowcount == 0:
                    await mess.channel.send("Could not find account " + account + " with email " + email + ". Make sure you spelled both exactly correctly. If the issue still persists, contact an admin with database access.")
                    return
                
                global_defines.cursor.execute("UPDATE wingslogin.ww_accounts SET status = 1 WHERE username IN ('" + account + "') AND email IN ('" + email + "') LIMIT 1;")
                
                if global_defines.cursor.rowcount == 0:
                    await mess.channel.send("Account " + account + " is already verified!")
                    return
                else:
                    await mess.channel.send("Account has been verified " + account + "! You are good to go!")
                    return            
            
            if msg.startswith("$eadd"):
                words = ["","",""]
                word_id = 0
                for letter in msg:
                    if letter != " ":
                        words[word_id] += letter
                    else:
                        word_id += 1
                
                if word_id != 2:
                    await mess.channel.send("Incorrect syntax! Command must be \"$eadd [account] [email]\" to add an IP exception to an account.")
                    return
                
                account = words[1]
                email = words[2]
                
                if "'" in account or "'" in email:
                    await mess.channel.send("Invalid account name or email.")
                    return
                
                global_defines.cursor.execute("SELECT * FROM wingslogin.ww_accounts WHERE username IN ('" + account + "') AND email IN ('" + email + "') LIMIT 1;")
                
                if global_defines.cursor.rowcount == 0:
                    await mess.channel.send("Could not find account " + account + " with email " + email + ". Make sure you spelled both exactly correctly. If the issue still persists, contact an admin with database access.")
                    return
                
                global_defines.cursor.execute("UPDATE wingslogin.ww_accounts SET ip_exempt = 1 WHERE username IN ('" + account + "') AND email IN ('" + email + "') LIMIT 1;")
                
                if global_defines.cursor.rowcount == 0:
                    await mess.channel.send("Account " + account + " already has an IP exemption!")
                    return
                else:
                    await mess.channel.send("IP exemption has been successfully added to account " + account + "! Feel free to keep this ticket open until you've successfully created your account.  Thanks for joining Wings!")
                    return
            
            if msg.startswith("$eremove"):
                words = ["",""]
                word_id = 0
                for letter in msg:
                    if letter != " ":
                        words[word_id] += letter
                    else:
                        word_id += 1
                
                if word_id != 1:
                    await mess.channel.send("Incorrect syntax! Command must be \"$eremove [account]\" to remove an IP exception to an account.")
                    return
                    
                account = words[1]
                
                if "'" in account:
                    await mess.channel.send("Invalid account name.")
                    return
                
                global_defines.cursor.execute("SELECT * FROM wingslogin.ww_accounts WHERE username IN ('" + account + "') LIMIT 1;")
                
                if global_defines.cursor.rowcount == 0:
                    await mess.channel.send("Could not find account " + account + ". Make sure you spelled it exactly correctly. If the issue still persists, contact an admin with database access.")
                    return
                
                global_defines.cursor.execute("UPDATE wingslogin.ww_accounts SET ip_exempt = 0 WHERE username IN ('" + account + "') LIMIT 1;")
                
                if global_defines.cursor.rowcount == 0:
                    await mess.channel.send("Could not remove IP exception from " + account + " because it does not have one right now.")
                    return
                else:
                    await mess.channel.send("IP exemption has been successfully removed from account " + account + "!")
                    return
                    
            if msg.startswith("$ehas"):
                words = ["",""]
                word_id = 0
                for letter in msg:
                    if letter != " ":
                        words[word_id] += letter
                    else:
                        word_id += 1
                
                if word_id != 1:
                    await mess.channel.send("Incorrect syntax! Command must be \"$ehas [player]\" to check if a player has an IP exemption on their account.")
                    return
                    
                player = words[1]
                
                if "'" in player:
                    await mess.channel.send("Invalid player name.")
                    return
                
                global_defines.cursor.execute("SELECT username,id,ip_exempt,email FROM wingslogin.ww_accounts WHERE id = (SELECT ffxiwings.chars.accid FROM ffxiwings.chars WHERE charname IN ('" + player + "') LIMIT 1);")
                
                row = global_defines.cursor.fetchone()
                if row == None:
                    await mess.channel.send("Could not find player " + player + ". Make sure you spelled it exactly correctly. If the issue still persists, contact an admin with database access.")
                    return
                
                account = row[0]
                accountid = row[1]
                ip_exempt = row[2]
                email = row[3]
                
                global_defines.cursor.execute("SELECT charname FROM ffxiwings.chars WHERE accid = " + str(accountid) + ";")
                
                player_list = ""
                is_first = True
                for row in global_defines.cursor:
                    if is_first == False:
                        player_list += ", "
                    player_list += row[0]
                    is_first = False
                
                if ip_exempt == 0:
                    await mess.channel.send("Account: " + account + " (" + str(accountid) + ") with characters {" + player_list + "} does not have an IP exception.")
                    return
                else:
                    response = "Account: " + account + "(" + str(accountid) + ")" + " with characters {" + player_list + "} has an IP exception"
                    #global_defines.cursor.execute("SELECT username,id FROM wingslogin.ww_accounts WHERE id IN (SELECT DISTINCT account_id FROM wingslogin.ww_login_log WHERE client_ip IN (SELECT DISTINCT client_ip FROM wingslogin.ww_login_log WHERE account_id = " + str(accountid) + ") AND account_id != 0) AND id NOT IN (" + str(accountid) + ") ORDER BY id ASC;")
                    
                    global_defines.cursor.execute("WITH R as (SELECT DISTINCT account_id AS n FROM wingslogin.ww_login_log WHERE client_ip IN (SELECT DISTINCT client_ip FROM wingslogin.ww_login_log WHERE account_id = " + str(accountid) + ") AND account_id NOT IN (0, " + str(accountid) + ")) SELECT username,id FROM wingslogin.ww_accounts WHERE id IN (SELECT n FROM R) ORDER BY id ASC;")
                    if global_defines.cursor.rowcount == 0:
                        response += " but no other account has been logged into its associated IP address yet."
                    else:
                        response += ". Other accounts that have logged in with its associated IP address: "
                        is_first = True
                        accountid_list = ""
                        i = 0
                        current_accid = 0
                        for row in global_defines.cursor:
                            if is_first == False:
                                response += "and "
                                accountid_list += ","
                            else:
                                current_accid = row[1]
                            response += row[0] + "(" + str(row[1]) + ")"
                            accountid_list += str(row[1])
                            i += 1
                            is_first = False
                        
                        response += " with the characters, respectively, {"
                        global_defines.cursor.execute("SELECT accid,charname FROM ffxiwings.chars WHERE accid IN (" + accountid_list + ") ORDER BY accid ASC;")
                        
                        is_first_char = True
                        for row in global_defines.cursor:
                            if row[0] != current_accid:
                                response += "} and {"
                                is_first_char = True
                                current_accid = row[0]
                            if is_first_char == False:
                                response += ", "
                            response += row[1]
                            is_first_char = False
                        
                        response += "}."
                        
                        await mess.channel.send(response)
                        return
                    
            if msg.startswith("$account"):
                words = msg.split(' ')

                command = words[1]
                account = ''
                if len(words) > 2:
                    account = words[2]
                extra = ''
                if len(words) > 3:
                    extra = words[3]
                
                allNumbers = True
                for id in str(account).split(","):
                    if not id.isdigit():
                        allNumbers = False

                if account.isdigit():
                    accountWhereStr = "id = " + str(account)
                elif allNumbers == True:
                    accountWhereStr = "id IN (" + str(account) + ")"
                else:
                    if command in ["unban","ban","addcontent"]: # force name match for certain commands
                        accountWhereStr = "username = '" + str(account) + "'"
                    else:
                        accountWhereStr = "username like '%" + str(account) + "%'"


                is_first = True
                if len(account) > 0:
                    global_defines.cursor.execute("SELECT id FROM wingslogin.ww_accounts WHERE " + str(accountWhereStr) + " limit 10;")
                    
                    account_list = ""
                    for row in global_defines.cursor:
                        if is_first == False:
                            account_list += ","
                        account_list += str(row[0])
                        is_first = False
                
                if is_first == False or command == "unique":
                    sqlQueries = []
                    if command == "addcontent":
                        sqlQueries.append("INSERT INTO wingslogin.ww_contents SELECT NULL,id as account_id,1 as enabled from wingslogin.ww_accounts where id in ({});".format(str(account_list)))
                        await mess.channel.send("content ids should be added for all accounts listed run `$account getcontent {}` to verify".format(account_list))
                    elif command == "getcontent":
                        sqlQueries.append("select count(account_id) as FreeIDs,account_id,enabled,group_concat(charid) from wingslogin.ww_contents left join ffxiwings.chars using(content_id) where account_id in ({}) group by account_id,isnull(charid);".format(str(account_list)))
                    elif command == "addbeta":
                        if len(account_list.split(',')) > 10:
                            await mess.channel.send("please don't try to add beta to more than 10 accounts at a time")
                            return
                        # runs the info command before this command
                        sqlQueries.append("SELECT id,username,features,status,privileges,ip_exempt,temp_exempt,timecreated,timemodified,(select group_concat(concat(charname,'(',charid,')')) from ffxiwings.chars where accid = wingslogin.ww_accounts.id) as chars FROM wingslogin.ww_accounts WHERE id in (" + str(account_list) + ");")
                        sqlQueries.append("UPDATE wingslogin.ww_accounts set privileges = privileges + 2 where privileges & 2 = 0 and id in ({});".format(str(account_list)))
                        await mess.channel.send("beta access should be added for all accounts listed that didn't already have it. Run `$account info {}` to verify".format(account_list))
                    elif command == "info":
                        sqlQueries.append("SELECT id,username,features,status,privileges,ip_exempt,temp_exempt,timecreated,timemodified,(select group_concat(concat(charname,'(',charid,')')) from ffxiwings.chars where accid = wingslogin.ww_accounts.id) as chars FROM wingslogin.ww_accounts WHERE id in (" + str(account_list) + ");")
                    elif command == "unban":
                        if not isSeniorStaffChannel(mess.channel) or ',' in account_list:
                            await mess.channel.send("https://tenor.com/view/itysl-i-think-you-should-leave-tim-robinson-you-cant-do-that-cant-gif-23125076")
                            return
                        sqlQueries.append("update wingslogin.ww_accounts set status = 1 WHERE id in (" + str(account_list) + ");")
                    elif command == "ban":
                        if not isSeniorStaffChannel(mess.channel) or ',' in account_list:
                            await mess.channel.send("https://tenor.com/view/itysl-i-think-you-should-leave-tim-robinson-you-cant-do-that-cant-gif-23125076")
                            return
                        sqlQueries.append("update wingslogin.ww_accounts set status = 2 WHERE id in (" + str(account_list) + ");")
                    elif command == "logins":
                        for account in account_list.split(','):
                            sqlQueries.append("""\
SELECT l1.* 
FROM wingslogin.ww_login_log l1 LEFT JOIN wingslogin.ww_login_log l2
ON (l1.account_id = l2.account_id AND l1.client_ip = l2.client_ip and l1.login_time < l2.login_time)
WHERE l2.client_ip IS NULL AND l1.login_time > DATE_ADD(NOW(), INTERVAL -1 MONTH) AND l1.account_id =""" + str(account) + " ORDER BY l1.login_time desc;")
                    elif command == "unique":
                        sqlQueries.append("""\
select date(login_time),count(distinct account_id)
from wingslogin.ww_login_log
where login_time > date_add(now(),interval -7 day)
group by date(login_time)
order by login_time desc
""")
                    else:
                        await mess.channel.send("invalid account command (" + command +")")
                        return
                else:
                    await mess.channel.send("No account found or more than one found for certain commands")
                    return
                # execute sql and output results
                #await mess.channel.send(sqlQuery)
                for output in sqlOutput(sqlQueries):
                    await mess.channel.send(output)
                return

            if msg.startswith("$char"):
                words = msg.split(' ')

                command = words[1]
                char = ''
                if len(words) > 2:
                    char = words[2]
                extra = ''
                if len(words) > 3:
                    extra = words[3]
                
                
                allNumbers = True
                for id in str(char).split(","):
                    if not id.isdigit():
                        allNumbers = False

                if char.isdigit():
                    charWhereStr = "charid = " + str(char)
                elif allNumbers == True:
                    charWhereStr = "charid IN (" + str(char) + ")"
                else:
                    if command in ["dbox","setvar"]: # force name match for certain command
                        charWhereStr = "charname = '" + str(char) + "'"
                    else:
                        charWhereStr = "charname like '%" + str(char) + "%'"


                is_first = True
                if len(char) > 0:
                    global_defines.cursor.execute("SELECT charid FROM chars WHERE " + str(charWhereStr) + " limit 10;")
                    
                    char_list = ""
                    for row in global_defines.cursor:
                        if is_first == False:
                            char_list += ","
                        char_list += str(row[0])
                        is_first = False
                
                if is_first == False:
                    sqlQueries = []
                    if command == "info":
                        sqlQueries.append("SELECT charid AS id,accid,charname AS NAME,pos_zone as zone,pos_prevzone AS prevzone,(round(playtime/(24*60*60),1)) as playtime,timecreated,lastupdate FROM chars WHERE charid IN (" + str(char_list) + ");")
                    elif command == "getvar":
                        sqlQueries.append("SELECT * from char_vars WHERE varname like '%" + str(extra) + "%' and charid IN (" + str(char_list) + ");")
                    elif command == "setvar":
                        if not isSeniorStaffChannel(mess.channel):
                            await mess.channel.send("https://tenor.com/view/itysl-i-think-you-should-leave-tim-robinson-you-cant-do-that-cant-gif-23125076")
                            return
                        validItems = True
                        splitItems = extra.split(',')
                        if len(splitItems) != 2:
                            validItems = False
                        else:
                            varname = splitItems[0]
                            varvalue = splitItems[1]
                            if not (varvalue.isnumeric()):
                                validItems = False
                        if validItems:
                            insertQuery = "INSERT INTO char_vars (charid,varname,value) values ({0},'{1}',{2}) ON DUPLICATE KEY UPDATE value = {2}".format(str(char_list),str(varname),str(varvalue))
                            print(insertQuery)
                            global_defines.cursor.execute(insertQuery)
            
                            if global_defines.cursor.rowcount == 0:
                                await mess.channel.send("charvar set failed!")
                            else:
                                await mess.channel.send("Set charvar (`{}`) to value (`{}`) for charid ({})".format(varname, varvalue, char_list))
                            return
                        else:
                            await mess.channel.send("Invalid (varname,value) given: " + extra)
                            return
                        return
                    elif command == "posfix":
                        await mess.channel.send("coming soon")
                        return
                    elif command == "dbox":
                        # TODO distinguish staff from GMs for commands like this
                        if not isSeniorStaffChannel(mess.channel):
                            await mess.channel.send("https://tenor.com/view/itysl-i-think-you-should-leave-tim-robinson-you-cant-do-that-cant-gif-23125076")
                            return
                        if not (',' in extra):
                            items = extra + ',1'
                        else:
                            items = extra
                        validItems = True
                        splitItems = items.split(',')
                        if len(splitItems) != 2:
                            validItems = False
                        else:
                            itemID = splitItems[0]
                            quantity = splitItems[1]
                            if not (itemID.isnumeric() and quantity.isnumeric()):
                                validItems = False
                            else:
                                itemID = int(itemID)
                                quantity = int(quantity)
                                global_defines.cursor.execute("SELECT name,stackSize FROM item_basic WHERE itemid = {};".format(itemID))
                                rows = global_defines.cursor.fetchall()
                                if len(rows) != 1:
                                    validItems = False
                                else:
                                    for row in rows:
                                        if (quantity > int(row[1])) or quantity < 1:
                                            validItems = False
                                        else:
                                            itemName = row[0]
                        if validItems:
                            insertQuery = "INSERT INTO delivery_box (box,charid,charname,sender,itemid,quantity) values (1,{0},(select charname from chars where charid = {0}),'{1}',{2})".format(char_list,mess.author.name,items)
                            global_defines.cursor.execute(insertQuery)
            
                            if global_defines.cursor.rowcount == 0:
                                await mess.channel.send("dbox add failed!")
                            else:
                                await mess.channel.send("Added item (`{}`) to dbox for charid ({})".format(itemName, char_list))
                            return
                        else:
                            await mess.channel.send("Invalid item/quantity given: " + items)
                            return
                    else:
                        await mess.channel.send("invalid char command (" + command +")")
                        return
                else:
                    await mess.channel.send("No char found or more than one found for certain commands")
                    return
                # execute sql and output results
                #await mess.channel.send(sqlQuery)
                for output in sqlOutput(sqlQueries):
                    await mess.channel.send(output)
                return

            # commands only allowed from senior chat channel
            if isSeniorStaffChannel(mess.channel):
                if msg.startswith("$audit"):
                    words = msg.split(' ')

                    command = words[1]
                    account = ''
                    if len(words) > 2:
                        account = words[2]
                    extra = ''
                    if len(words) > 3:
                        extra = words[3]

                    if account.isnumeric():
                        hours = int(account)
                    else:
                        hours = 0

                    for output in audit_gm(hours):
                        await mess.channel.send(output)
                    return
        

# Reports gm command audit to senior staff channel
async def tryReportAuditGM():
    staff_channel = 0
    for guild in global_defines.client.guilds:
        for channel in guild.channels:
            if "senior-chat" == channel.name.lower():
                staff_channel = channel
                break
    if staff_channel == 0:
        print("Error! No senior-chat channel found.")
        return
    
    hours = 6
    await staff_channel.send("Scheduled GM command audit, running every {} hours".format(hours))
    for output in audit_gm(hours):
        await staff_channel.send(output)
    return

# Updates the online count voice channel name
async def tryUpdateOnlineCount():
    players_online_channel = 0
    for guild in global_defines.client.guilds:
        for channel in guild.channels:
            if "online" in channel.name.lower():
                players_online_channel = channel
                break
    if players_online_channel == 0:
        print("Error! No players online voice channel found.")
        return
    
    # record current player count
    global_defines.cursor.execute("SELECT count(accid) FROM ffxiwings.accounts_sessions;")
    num_online = int(global_defines.cursor.fetchone()[0])
    global_defines.cursor.execute("INSERT INTO wingslogin.ww_playercounts (onlineplayers) VALUES (" + str(num_online) + ");")
    # adjusting that player count for funny numbers
    # reported number: [min,max]
    funnyNumbers = {
    86:     [80,92],
    69:     [64,74],
    42:     [20,45],
    69420:  [0,2],
    420:    [400,440],
    }
    disp_num_online = num_online
    currentDisplay = int(re.findall(r'\d+', players_online_channel.name)[0])
    for key in funnyNumbers:
        range = funnyNumbers[key]
        if num_online >= range[0] and num_online <= range[1]:
            disp_num_online = key
            break

    #global_defines.cursor.execute("SELECT ceil(avg(onlineplayers)),min(onlineplayers),max(onlineplayers),floor(hour(TIME)/6) = floor(HOUR(NOW())/6) FROM wingslogin.ww_playercounts where TIME > date_add(NOW(), INTERVAL -1 HOUR) ORDER BY time;")
    #countHistory = global_defines.cursor.fetchone()
    # only update discord if 
    #playercount higher than the last hour's average -- DISABLED
    #count swings past min and max over last hour
    #every 24 % 6 hours
    #if (num_online > int(countHistory[1]) - 2 and num_online < int(countHistory[2]) + 2) and int(countHistory[3]) == 1: # and num_online < int(countHistory[0]) * 1.05:
    report = False
    if disp_num_online in funnyNumbers:
        if currentDisplay != disp_num_online:
            report = True
    elif currentDisplay < disp_num_online - 6 or currentDisplay > disp_num_online + 4:
        if not ((currentDisplay in funnyNumbers) and (num_online < funnyNumbers[currentDisplay][0] - 2) and (num_online > funnyNumbers[currentDisplay][1] + 2)):
            report = True

    if report == False:
        print("Player count not being adjusted")
        return

    await players_online_channel.edit(reason="playercount bot update",name="✅Online: " + str(disp_num_online) + "✅")
    print("Successfully updated playercount to " + str(disp_num_online) + ".")

async def tryUpdateGMTickets():
    global_defines.cursor.execute("SELECT callid,charid,charname,zoneid,message,harassment,stuck,blocked,accid FROM ffxiwings.server_gmcalls WHERE status NOT IN (1,2,3) ORDER BY callid ASC LIMIT 1;")
    #                                        0      1       2       3     4         5        6      7      8
    if global_defines.cursor.rowcount == 0:
        return
    row = global_defines.cursor.fetchone()
    if row == None:
        return
    
    print("New web ticket found (" + str(row[0]) + "). Creating new channel for web ticket...")
    
    first_message = ("This is an automated transcript from a web ticket that was submitted through the website or in-game Help Desk. It is NOT managed by Ticket Tool. "
                     "The player that opened this ticket is not added to this channel by default. They must be contacted in-game or added here manually if their Discord tag is known. "
                     "To close this ticket, use the $closeweb command which will close the ticket on the website/in-game and move this ticket to the CLOSED TICKETS category. "
                     "Transcripts must be saved using the Archiver bot.\n\n")
    first_message += "Player **" + row[2] + "**(" + str(row[1]) + ") of account (" + str(row[8]) + ") opened ticket(webID " + str(row[0]) + ") in " + zones.ZONES[row[3]]
    if row[6] != 0 or row[7] != 0:
        first_message += ", indicating they are stuck or blocked. "
    elif row[5] != 0:
        first_message += ", indicating a harassment situation. "
    else:
        first_message += ". "
    first_message += "User's message is detailed below:\n```--------------------------------------------------------------------```"
    
    web_category = 0
    for guild in global_defines.client.guilds:
        for category in guild.categories:
            if "[web]" in category.name.lower():
                web_category = category
                break
    
    if web_category == 0:
        print("Error! Could not find the web category for tickets.")
        return
    
    web_ticket_channel = await web_category.create_text_channel("wticket-" + str(row[0]))
    
    sent_message = await web_ticket_channel.send(first_message)
    await web_ticket_channel.send("*" + row[4] + "*")
    await sent_message.pin()
    
    global_defines.cursor.execute("UPDATE ffxiwings.server_gmcalls SET status = 1 WHERE callid IN (" + str(row[0]) + ") LIMIT 1;")
    