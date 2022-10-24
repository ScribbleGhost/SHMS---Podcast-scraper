# SHMS - Podcast scraper

## What is this?

A Python 3 script for downloading episodes from the Waking Up podcast using the subscribers only RSS link. Note that you must have a subscription, Although there are free episodes, the RSS feed is only provided for subscribing members.

## What it does

In contrast to just downloading episodes one by one, this script will:

- Download all available episodes in an RSS feed.
- Date-stamp and name the episode files accordingly.
- Fetch the corresponding thumbnail and set it as a cover for the MP3 file.
- Add corresponding MP3 tags to the files.
- Skip existing downloads.

## Dependencies

You need to install the following Python libraries to make this work.

```
pip install bs4
pip install mutagen
pip install requests
```

## How to use it

Download and install Python 3+ and the above mentioned libraries.

Edit the `options.py` file:

- Add a save location. Note that forward slashes `\` should be written double: `\\`.
- Add either an RSS link (you should be able to get that if you are a subscriber), or add an XML file.

Run the `main.py` and let Python download each episode, one by one.
