import discord
from discord.ext import commands, tasks
import asyncio
from lifunctions import tryUpdateGMTickets
from lifunctions import tryUpdateOnlineCount
from lifunctions import tryReportAuditGM
from lifunctions import tryResponse
from lifunctions import isGM
import global_defines

class CCog(commands.Cog):
    
    def startTasks(self):
        self.onlineCountTask.start()
        self.ticketReaderTask.start()
        self.auditGMTask.start()
    
    @tasks.loop(seconds=305)
    async def onlineCountTask(self):
        await tryUpdateOnlineCount()

    @tasks.loop(hours=6)
    async def auditGMTask(self):
        await tryReportAuditGM()
        
    @tasks.loop(seconds=15)
    async def ticketReaderTask(self):
        await tryUpdateGMTickets()