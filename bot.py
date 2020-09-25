import itertools
import os

import discord
from discord.ext import tasks
from dotenv import load_dotenv
import requests

from blog_crawler import BlogCrawler


load_dotenv()

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@tasks.loop(minutes=1)
async def poll_blog():
    print('Looking for new articles...')

    previous_articles = crawler.get_articles()
    crawler.crawl()
    current_articles = crawler.get_articles()

    new_articles = list(itertools.filterfalse(lambda x: x in current_articles, previous_articles))
    if new_articles:
        channel = discord.utils.get(client.guilds[0].channels, name='general')
        await channel.send('New blog posts!')
        for article in new_articles:
            await channel.send(BlogCrawler.format_article(article))


@poll_blog.before_loop
async def poll_blog_before():
    await client.wait_until_ready()

crawler = BlogCrawler()


@client.event
async def on_message(message):

    # Don't let the bot trigger itself
    if message.author == client.user:
        return

    # If no message or message doesn't start with !, ignore it
    if not message.content or not message.content[0] == '!':
        return

    # Split up message into command and arguments to use in many different commands
    content_list = [x.strip() for x in message.content.split(' ')]
    command = content_list[0]

    if command == '!latest':
        article = crawler.get_latest_article()
        await message.channel.send(BlogCrawler.format_article(article))

    else:
        # Unknown command, search for author name
        author_name = command.replace('!', '').replace('-', ' ')
        author_name += ' ' + ' '.join(content_list[1:])

        articles = crawler.get_articles(author=author_name)
        if not articles:
            await message.channel.send(f'No articles authored by {author_name} found')
        else:
            for article in articles:
                await message.channel.send(BlogCrawler.format_article(article))

poll_blog.start()
client.run('NzUwMTMyMzk5NjA1Njc4MTQw.X02FPA.Uwo_5PqlD7UuEnCFCYPx_vkEye4')
