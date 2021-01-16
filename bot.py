import discord
from discord.ext import commands
import datetime
import asyncio
import json
import os


# redacted, of course
token = ''


bot = commands.Bot(command_prefix='~')

# path to JSON file (does not need to exist initially)
TIMERS = r''

def get_remaining(end):
    hours, minutes = end.split(':')
    now = datetime.datetime.utcnow()
    goal = now.replace(hour=int(hours), minute=int(minutes))
    left = goal - now
    if left.total_seconds() < 0:
        goal = goal.replace(day=goal.day + 1)
        left = goal - now
    seconds = left.total_seconds()
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return int(hours), int(minutes)



async def update_timers():
    while True:
        zero_test = get_remaining('00:00')[1]
        if zero_test % 10 == 0:
            data = json.load(open(TIMERS))
            regions = data['timers']
            for item in regions:
                h,m = get_remaining(regions[item]['time'])
                title = f"{regions[item]['region']} Reset: {h}h {m}m"
                channel = await bot.fetch_channel(item)
                await channel.edit(name=title)
            await asyncio.sleep(60)
        await asyncio.sleep(1)

@bot.event
async def on_ready():
    bot.loop.create_task(update_timers())

@bot.command()
@commands.has_any_role('Role 1', 'Role 2')
async def add_timer(ctx, channel_id, region_name, reset_time):
    if not os.path.exists(TIMERS):
        data = {'timers': {}}
    else:
        data = json.load(open(TIMERS))
    data['timers'][channel_id] = {'time': reset_time, 'region': region_name}
    json.dump(data, open(TIMERS, 'w'))
    channel = await bot.fetch_channel(channel_id)
    h,m = get_remaining(reset_time)
    name = f"{region_name} Reset: {h}h {m}m"
    await channel.edit(name=name)
    await ctx.send(f"Timer added/adjusted.")

@bot.command()
@commands.has_any_role('Role 1', 'Role 2')
async def testme(ctx):
    await ctx.send("Approved")


if __name__ == '__main__':
    bot.run(token)
