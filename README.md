A discord bot that includes the following commands / functions:

* 12 times per day, it will check the https://interstem.us/ website for new articles. If there are new articles, the bot will send an embed message with each new article's title, author, description and date.

* "!latest" will check interstem.us for the latest post, and send an embed message with the article's title, author, description, and date as a response

* "!<name>" will check interstem.us for any posts authored by "<name>" and send an embed message with each article's title, author, description, and date as a response. !name can be something either like !First Last or !First-Last, or even just !First. Any of these will work, and it is case insensitive.

Screenshot demonstration: https://share.getcloudapp.com/JrugkY4L

To get this bot code to connect to your own discord bot, you'll need to set your bot's token as an environment variable called "BOTTOKEN".
