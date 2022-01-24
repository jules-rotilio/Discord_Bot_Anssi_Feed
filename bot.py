# check https://stackoverflow.com/questions/54845875/how-do-i-check-if-a-user-has-a-specific-role-in-discord
import os
import time
import feedparser
import discord
from discord.ext.commands import Bot
import re
import asyncio

TOKEN="Your Bot Token HERE"
GUILD="Bot Anssi"
ALLOW_ID=["id1","id2"]

bot = Bot("!")

CLEANR = re.compile('<.*?>') 
def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext

@bot.event
async def on_ready():
	for guild in bot.guilds:
		print(
			f'{bot.user} is connected to the following guild:\n'
			f'{guild.name}(id: {guild.id})'
		)

@bot.command()
async def alerte(ctx):
	await erase(ctx)
	if ctx.author.id not in ALLOW_ID:
		return
	link = 'https://www.cert.ssi.gouv.fr/alerte/feed/'
	await func_parser(ctx, link)

@bot.command()
async def avis(ctx):
	await erase(ctx)
	if ctx.author.id not in ALLOW_ID:
		return
	link = 'https://www.cert.ssi.gouv.fr/avis/feed/'
	await func_parser(ctx, link)
	

async def func_parser(ctx,link,timer=3600):
	lt = await parser(ctx,link, "")
	while True:
		await asyncio.sleep(timer)
		lt = await parser(ctx,link, lt)

async def parser(ctx,link,lastest_published):
	#loop to update the channel with the lastest news
	news_feed = feedparser.parse(link)
	if (news_feed.entries[0].published != lastest_published) :
		for entry in reversed(news_feed.entries):
			titre = entry['title']
			desc = cleanhtml(entry['summary'])
			link = entry['link']
			if entry.link > lastest_published :
				msg=discord.Embed(title=titre, url=link, description=desc, color=discord.Color.red())
				await ctx.send(embed=msg)
				lastest_published = entry.link
		news_feed = ""
	#delay before parsing the feed
	return lastest_published

@bot.command()
async def erase(ctx):
	if ctx.author.id not in ALLOW_ID:
		message = await ctx.channel.history(limit=1).flatten()
		await message[0].delete()
		await ctx.send("<@"+str(ctx.author.id)+"> touche pas à ça petit con")
		return
	messages = await ctx.channel.history(limit=200).flatten()
	for msg in messages :
		await msg.delete()

'''
@bot.command()
async def test_feed(ctx):
	await erase(ctx)
	if ctx.author.id not in ALLOW_ID:
		return
	link = 'https://lorem-rss.herokuapp.com/feed?unit=second&interval=30'
	await func_parser(ctx, link, 15)
'''

bot.run(TOKEN)