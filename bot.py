# check https://stackoverflow.com/questions/54845875/how-do-i-check-if-a-user-has-a-specific-role-in-discord
import os
import time
import feedparser
import discord
from discord.ext.commands import Bot
import re
import asyncio
import datetime
from html import unescape

inpt = input("test or nothing? ")

if inpt == "test":
	TOKEN = "DISCORD_TEST_BOT_TOKEN"
else:
	TOKEN = "DISCORD_BOT_TOKEN"
ALLOW_ID=["ID1","ID2"]

bot = Bot("!")
#bot = commands.Bot(command_prefix='!', case_insensitive=True)

CLEANR = re.compile('<.*?>')
def cleanhtml(raw_html):
	cleantext = re.sub(CLEANR, '', raw_html)
	return cleantext

liste_rss_feed=['alerte','avis','bleepingcomputer','latesthackingnews','securityaffairs']

@bot.event
async def on_ready():
	for guild in bot.guilds:
		print(
			f'{bot.user} is connected to the following guild:\n'
			f'{guild.name}(id: {guild.id})'
		)
		rss,rss_feeds = await check_channels(guild)
		await create_channels(guild,rss,rss_feeds)


async def check_channels(guild):
	rss = 0
	rss_feeds = {}
	for rss_feed in liste_rss_feed:
		rss_feeds.update({rss_feed:0})
	for category in guild.categories:
		if category.name.lower() == "rss":
			rss = category
			for channel in category.channels:
				if channel.name in liste_rss_feed:
					rss_feeds.update({channel.name:1})
	return rss,rss_feeds

async def create_channels(guild,rss,channels):
	if not isinstance(rss,discord.channel.CategoryChannel):
		rss = await guild.create_category("rss")
	for channel in channels.keys():
		if channels[channel] == 0:
			await rss.create_text_channel(channel)

@bot.command()
async def alerte(ctx):
	await erase(ctx,1)
	if str(ctx.author.id) not in ALLOW_ID:
		return
	link = 'https://www.cert.ssi.gouv.fr/alerte/feed/'
	await func_parser(ctx, link)

@bot.command()
async def avis(ctx):
	await erase(ctx,1)
	if str(ctx.author.id) not in ALLOW_ID:
		return
	link = 'https://www.cert.ssi.gouv.fr/avis/feed/'
	await func_parser(ctx, link)

@bot.command()
async def bleepingcomputer(ctx):
	await erase(ctx,1)
	if str(ctx.author.id) not in ALLOW_ID:
		return
	link = 'https://www.bleepingcomputer.com/feed/'
	await func_parser(ctx, link)

@bot.command()
async def latesthackingnews(ctx):
	await erase(ctx,1)
	if str(ctx.author.id) not in ALLOW_ID:
		return
	link = 'https://latesthackingnews.com/feed/'
	await func_parser(ctx, link)

@bot.command()
async def securityaffairs(ctx):
	await erase(ctx,1)
	if str(ctx.author.id) not in ALLOW_ID:
		return
	link = 'https://securityaffairs.co/wordpress/feed'
	await func_parser(ctx, link)

async def func_parser(ctx,link,timer=3600):
	file = "path_to_folder"
	if "avis" in link:
		file += str(ctx.guild.id) + "_avis"
	elif "alerte" in link :
		file += str(ctx.guild.id) + "_alerte"
	elif "bleepingcomputer" in link:
		file += str(ctx.guild.id) + "_bleepingcomputer"
	elif "latesthackingnews" in link :
		file += str(ctx.guild.id) + "_latesthackingnews"
	elif "securityaffairs" in link :
		file += str(ctx.guild.id) + "_securityaffairs"
	if os.path.exists(file):
		with open(file) as f:
			lp = f.readlines()[0]
			f.close()
	else:
		lp = str(int(time.mktime(time.strptime("1 Jan 00","%d %b %y"))))
	lu = str(int(time.mktime(time.strptime("1 Jan 00","%d %b %y"))))
	lp,lu = await parser(ctx,link, lp,lu)
	while True:
		with open(file,"w") as f:
			f.write(lp)
			f.close()
		await asyncio.sleep(timer)
		lp,lu = await parser(ctx,link, lp,lu)

async def parser(ctx,link,lastest_published,lastest_updated):
	#loop to update the channel with the lastest news
	news_feed = feedparser.parse(link)
	if (news_feed.updated != lastest_updated) :
		lastest_updated = news_feed.updated
		news_feed.entries.sort(key=lambda x: x.published_parsed)
		for entry in news_feed.entries:
			titre = entry['title']
			desc = unescape(cleanhtml(entry['summary']))
			link = entry['link']
			pp = int(time.mktime(entry.published_parsed))
			if pp > int(lastest_published) :
				msg=discord.Embed(title=titre, url=link, description=desc, color=discord.Color.red())
				await ctx.send(embed=msg)
				lastest_published = str(pp)
	return lastest_published,lastest_updated

@bot.command()
async def erase(ctx,count=15):
	if str(ctx.author.id) not in ALLOW_ID:
		message = await ctx.channel.history(limit=1).flatten()
		await message[0].delete()
		await ctx.send("<@"+str(ctx.author.id)+"> touche pas à ça petit con")
		return
	messages = await ctx.channel.history(limit=count).flatten()
	for msg in messages :
		await msg.delete()

@bot.event
async def on_message(message):
	message.content = message.content.lower()
	await bot.process_commands(message)

@bot.command()
async def suse(ctx):
	await ctx.send("t'es un peu con, <@"+str(ctx.author.id)+"> si tu trouves que suse c'est une bonne distribution")

@bot.command()
async def ping(ctx):
	await ctx.send("pong")

bot.run(TOKEN)