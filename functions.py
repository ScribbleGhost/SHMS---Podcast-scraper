from bs4 import BeautifulSoup
import datetime
import mimetypes
import os
import requests
import shutil
import headers # local module
import options # local module
import xml.etree.ElementTree as ET




def getRSS():
	"""
	Get XML data.
	If no link is provided look for XML file instead.
	"""
	if options.rss_link and options.rss_link.strip():
		response = requests.get(options.rss_link, headers=headers.headers)
		root = ET.fromstring(response.text)
		return root
	else:
		# Get RSS from XML file
		if options.rss_xml_file and options.rss_xml_file.strip():
			if os.path.isfile(options.rss_xml_file) == True:
				with open(options.rss_xml_file, 'r', encoding='utf8') as f:
					tree = ET.parse(f)
					root = tree.getroot()
					return root
		else:
			print('No XML file or link provided.')




def iso_8601(date):
	"""
	# Convert XML date format
	"""
	date = datetime.datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z')
	iso_8601_date = date.strftime('%Y-%m-%d') # https://strftime.org/
	return iso_8601_date




def character_fixer(string):
	"""
	# Download a file
	"""
	import re
	# Remove illegal file name characters in Windows
	string = string.replace('  ',' ')
	# Replace different types of hyphens with a normal hyphen
	string = string.replace('—','-')
	string = string.replace('−','-')
	string = string.replace('‒','-')
	string = string.replace('–','-')
	# Replace double spaces
	string = re.sub('\s+', ' ', string)
	string = string.strip()
	if string:
		return string




def filename(string):
	"""
	# Download a file
	"""
	for x in '\/:*?"<>|':
	# 	# Remove illegal file name characters in Windows
		string = string.replace(x,'')
	string = string.replace(' )',')')
	string = string.replace('( ','(')
	# # Replace different types of hyphens with a normal hyphen
	string = string.replace('—','-')
	string = string.replace('−','-')
	string = string.replace('‒','-')
	string = string.replace('–','-')
	# # Replace double spaces
	string = string.replace('  ',' ')
	# # Truncate long strings
	string = (string[:140] + '...') if len(string) > 140 else string
	string = string.strip()
	return string;





def subtitleAppender(subtitle):
	"""
	# Reformat short subtitles
	"""
	try:
		subtitle = subtitle.removeprefix("A Conversation with ")
		subtitle = subtitle.removeprefix("An Interview with ")
		subtitle = subtitle.strip()
	except AttributeError:
		pass
	if subtitle:
		subtitle = '(' + subtitle + ')'
	else:
		subtitle = ''
	return subtitle




def ffmpegMerger(input_audio, input_image, ffmpeg_output_filename):
	import subprocess
	ffmpeg = [
		'ffmpeg',
		'-y',
		'-hide_banner',
		'-nostats',
		'-loglevel',		'error',
		'-i',				input_audio,
		'-i',				input_image,
		'-map',				'0:0',
		'-map',				'1:0',
		'-c:a',				'copy',
		ffmpeg_output_filename
	]
	try:
		subprocess.run(ffmpeg)
	except Exception as e:
		return e




def fileDownloader(input_url, file_name):
	"""
	Download files from the internet.
	"""
	import mimetypes
	import filetype
	import requests
	import shutil
	import os
	import glob

	# If the file already exist (without a file extension)...


	# Request the link and get the (MIME) type
	r = requests.get(input_url, stream=True, allow_redirects=True)
	ext = mimetypes.guess_extension(r.headers['content-type'])
	
	# If the MIME-type is none or binary...
	if ext == None or ext == '.bin':
			
		# Download the file first
		with open(file_name,'wb') as f:
			shutil.copyfileobj(r.raw, f)

		# Use 'filetype' to detect the file type
		ext = '.' + filetype.guess(file_name).extension
	
		# Rename with the ext found
		try:
			os.rename(file_name, file_name + ext)
			file_name = file_name + ext
			return file_name
		except FileExistsError as e:
			raise
		except:
			raise

	else:
		file_name = file_name + ext
		with open(file_name,'wb') as f:
			shutil.copyfileobj(r.raw, f)
		return file_name