# Bi_Weekly_SoD_Timer_Bot.py
# .env file contains:
#TOKEN=
#STATUS=
import os
import datetime
import discord
import asyncio
import pytz
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
STATUS = os.getenv('STATUS')
client = discord.Client(intents=discord.Intents.default())

def is_dst(dt=None, timezone="UTC"):
    if dt is None:
        dt = datetime.utcnow()
    timezone = pytz.timezone(timezone)
    timezone_aware_date = timezone.localize(dt + datetime.timedelta(hours=24), is_dst=None) ##the timedelta(hours=24) is needed because the option kind of works a day too late
    return timezone_aware_date.tzinfo._dst.seconds != 0
    
    #>>> is_dst() # it is never DST in UTC
    #False
    #>>> is_dst(datetime(2019, 1, 1), timezone="US/Pacific")
    #False
    #>>> is_dst(datetime(2019, 4, 1), timezone="US/Pacific")
    #True
    #>>> is_dst(datetime(2019, 3, 10, 2), timezone="US/Pacific")
    #NonExistentTimeError
    #>>> is_dst(datetime(2019, 11, 3, 1), timezone="US/Pacific")
    #AmbiguousTimeError

def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds  
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    return days, hours, minutes

#gets you the next weekday from datetime object, weekday 0-6
def next_weekday(dateTime, weekday):
    days_ahead = weekday - dateTime.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return dateTime + datetime.timedelta(days_ahead)
    
#calculates the bi_weekly timer
def calculate_biweekly_timer() :
    now = datetime.datetime.today()
    
    resetHour = 5 ## when the reset happens in AM
       
    # if daylight savings time is active, the reset shifts by 1h
    if is_dst(now, timezone="Europe/Berlin") : 
        resetHour = resetHour + 1
    
    weekday = now.weekday()   #Mon 0, Tue 1, Wed 2, Thu 3, Fri 4, Sat 5, Sun 6  
    current_hour = int(now.strftime("%H"))  ## e.g. 14:24 = 14
    
    timeIntoTheWeek = (weekday*100) + current_hour
    #print("Used for determination of which of the two resets to count down to: " + str(timeIntoTheWeek))
    
    #Wednesday timer
    if timeIntoTheWeek < (200 + resetHour) or timeIntoTheWeek >= (600 + resetHour) :
        next_wednesday = now.replace(hour=resetHour, minute=00, second=00)
        
        if weekday != 2:
            next_wednesday = next_weekday(now, 2) # 0 = Monday, 1=Tuesday, 2=Wednesday...
            next_wednesday = next_wednesday.replace(hour=resetHour, minute=00, second=00)
            
        timer = next_wednesday - now
    
    #Sunday timer
    if timeIntoTheWeek >= (200 + resetHour) and timeIntoTheWeek < (600 + resetHour) :
        next_sunday = now.replace(hour=resetHour, minute=00, second=00)
        
        if weekday != 6:
            next_sunday = next_weekday(now, 6) # 0 = Monday, 1=Tuesday, 2=Wednesday...
            next_sunday = next_sunday.replace(hour=resetHour, minute=00, second=00)
            
        timer = next_sunday - now
        
    
    days, hours, minutes = convert_timedelta(timer)

    # only show days if its not 0 days
    if days != 0:
        days = str(days) + "d "
    else:
        days = ""
    # only show hours if its not 0 hours
    if hours != 0:
        hours =  str(hours%24) + "h "
    else:
        hours = ""
    # only minutes if minutes are not zero and days are zero   
    if days == "":
        minutes = str(minutes%60) + "m "
    else:
        minutes = ""
        
    return days, hours, minutes

@tasks.loop(seconds=45)
async def update_timer():
    days, hours, minutes = calculate_biweekly_timer()       
    
    for guild in client.guilds:
        await guild.me.edit(nick="!BiWeekly: " + days + hours + minutes)        

@client.event
async def on_ready():
    # Waiting until the bot is ready
    await client.wait_until_ready()
    print(f'{client.user} has connected to Discord! UwU')
	
    # starts update timer function if not already running
    if not update_timer.is_running() :
        update_timer.start()
	
    await asyncio.sleep(10)
    status = discord.CustomActivity(name=STATUS)
    await client.change_presence(status=discord.Status.online, activity=status)
    print(f'{client.user} has set its status! OwO')

client.run(TOKEN)
