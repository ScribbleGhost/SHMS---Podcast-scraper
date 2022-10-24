import functions # local module
import headers # local module
import options # local module
from bs4 import BeautifulSoup
from mutagen.id3 import AENC,APIC,ASPI,COMM,COMR,ENCR,EQU2,ETCO,GEOB,GRID,LINK,MCDI,MLLT,OWNE,PCNT,PCST,POPM,POSS,PRIV,RBUF,RVA2,RVRB,SEEK,SIGN,SYLT,SYTC,TALB,TBPM,TCAT,TCOM,TCON,TCOP,TDEN,TDES,TDLY,TDOR,TDRC,TDRL,TDTG,TENC,TEXT,TFLT,TGID,TIPL,TIT1,TIT2,TIT3,TKEY,TLAN,TLEN,TMCL,TMED,TMOO,TOAL,TOFN,TOLY,TOPE,TOWN,TPE1,TPE2,TPE3,TPE4,TPOS,TPRO,TPUB,TRCK,TRSN,TRSO,TSOA,TSOP,TSOT,TSRC,TSSE,TSST,TXXX,UFID,USER,USLT,WCOM,WCOP,WFED,WOAF,WOAR,WOAS,WORS,WPAY,WPUB,WXXX
from mutagen.id3 import ID3, ID3NoHeaderError
import datetime
import json
import os
import re
import requests
import mimetypes



# getRSS gets the RSS from link or file.
# For each item in the XML, get some values
root = functions.getRSS()
for xml_item in root.iter('item'):




	episode_data = {} # Make a dict for the episode values




	# -----------------------------------------------------------------------------
	# Add the episode values to the dictionary
	# -----------------------------------------------------------------------------
	episode_data['title'] = functions.character_fixer(xml_item.find('title').text)
	episode_data['title_filesafe'] = functions.filename(episode_data['title'])
	episode_data['guid'] = xml_item.find('guid').text
	episode_data['enclosure'] = (xml_item.find('enclosure')).get('url')
	episode_data['link'] = xml_item.find('link').text
	episode_data['pubDate'] = functions.iso_8601(xml_item.find('pubDate').text)
	
	# Subtitle
	namespaces = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
	for x in xml_item.findall('itunes:subtitle', namespaces):
		if (type(x.text)) == str:
			episode_data['subtitle'] = functions.character_fixer(x.text)
			episode_data['subtitle_short'] = functions.subtitleAppender(episode_data['subtitle'])
			episode_data['subtitle_short'] = functions.filename(episode_data['subtitle_short'])

	# Description
	try:
		from bs4 import BeautifulSoup
		episode_data['description'] = BeautifulSoup(xml_item.find('description').text, "xml").text
	except TypeError as e:
		pass




	# -----------------------------------------------------------------------------
	# Make file names
	# -----------------------------------------------------------------------------
	try:
		episode_full_name = episode_data['pubDate'] + ' - ' + episode_data['title_filesafe'] + ' - ' + episode_data['subtitle_short']
	except KeyError:
		episode_full_name = episode_data['pubDate'] + ' - ' + episode_data['title_filesafe']
	except Exception:
		print('ERROR: 🔺 Could not make a file name for the episode for some reason. Skipping the download.')
		break
	final_destination = os.path.join(options.save_location, 'Making Sense with Sam Harris - Subscriber Content')
	if not os.path.exists(final_destination):
		os.makedirs(final_destination)
	final_filename_fullpath = os.path.join(options.save_location, 'Making Sense with Sam Harris - Subscriber Content', episode_full_name + '.mp3')




	if os.path.isfile(final_filename_fullpath) == False:




		# -----------------------------------------------------------------------------
		# Let's access the webpage link for each episode
		# in order to get the artworkfor the episode
		# -----------------------------------------------------------------------------
		response = requests.get(episode_data['link'], headers=headers.headers, allow_redirects=True) # Get the HTML
		soup = BeautifulSoup(response.text, 'html.parser') # Read the HTML
		read_json = json.loads(soup.find('script', id='__NEXT_DATA__').get_text()) # Parse JSON from the <script> tag
		imageUrl = (read_json['props']['pageProps']['episode']['imageUrl']) # Get the full size image URL




		# Download the artwork from the episode article
		img_dl = functions.fileDownloader(imageUrl, episode_full_name)




		# -----------------------------------------------------------------------------
		# Download the audio
		# -----------------------------------------------------------------------------
		# Download the audio from the episode article
		audio_dl = functions.fileDownloader(episode_data['enclosure'], episode_full_name)




		# -----------------------------------------------------------------------------
		# Merge MP3 with images
		# -----------------------------------------------------------------------------
		try:
			functions.ffmpegMerger(audio_dl, img_dl, final_filename_fullpath)
			if os.path.exists(final_filename_fullpath) == True:
				print('✔ Successfully downloaded and processed: ', os.path.basename(final_filename_fullpath))

		except Exception as e:
			print('⚠ Could not merge the audio and artwork for the episode: ', episode_data['title'])
			exit()




		# -----------------------------------------------------------------------------
		# Clear all MP3 ID3 tags and write an empty ID3 tag instance (fix)
		# https://github.com/quodlibet/mutagen/issues/327#issuecomment-339316014
		# -----------------------------------------------------------------------------
		try:
			audio = ID3(final_filename_fullpath)
		except ID3NoHeaderError:
			audio = ID3()
			audio.save(final_filename_fullpath)




		# -----------------------------------------------------------------------------
		# Write ID3 tags to the file with mutagen
		# https://mutagen-specs.readthedocs.io/en/latest/id3/id3v2.4.0-frames.html
		# -----------------------------------------------------------------------------

		# Title/songname/content description
		try:
			audio.add(TIT2(encoding=3, text=episode_data['pubDate'] + ' - ' + episode_data['title_filesafe'] + ' - ' + episode_data['subtitle_short']))
		except Exception:
			audio.add(TIT2(encoding=3, text=episode_data['pubDate'] + ' - ' + episode_data['title_filesafe']))
		except Exception:
			audio.add(TIT2(encoding=3, text=episode_data['pubDate'] + ' - ' + 'Title missing...'))
		except Exception as e: print(e)

		# Unsynchronised lyric/text transcription
		try: audio.add(USLT(encoding=3, text=episode_data['description']))
		except Exception as e: pass
		
		# Artist
		try: audio.add(TPE1(encoding=3, text="Sam Harris"))
		except Exception as e: print(e)

		# Unique file identifier (PERFORMER spesifically for Foobar2000)
		try: audio.add(UFID(encoding=3, desc='PERFORMER', text="Sam Harris"))
		except Exception as e: print(e)

		# Band/orchestra/accompaniment [Also known as album artist]
		try: audio.add(TPE2(encoding=3, text="Sam Harris"))
		except Exception as e: print(e)

		# Performer sort order
		try: audio.add(TSOP(encoding=1, text="Harris, Sam"))
		except Exception as e: print(e)

		# Album/Movie/Show title
		except Exception as e: print(e)
		try: audio.add(TALB(encoding=3, text="Making Sense with Sam Harris - Subscriber Content"))
		except Exception as e: print(e)

		# Content type [Genre]
		try: audio.add(TCON(encoding=3, text="Podcast"))
		except Exception as e: print(e)

		# Encoding time [When the audio was encoded]
		try: audio.add(TDEN(encoding=3, text=[datetime.datetime.now().isoformat()]))
		except Exception as e: print(e)

		try:
			audio.add(TDOR(encoding=3, text=episode_data['pubDate'])) # Original release time [Usually just the year]
			audio.add(TDTG(encoding=3, text=episode_data['pubDate'])) # Tagging time
			audio.add(TDRL(encoding=3, text=episode_data['pubDate'])) # Release time
			audio.add(TDRC(encoding=3, text=episode_data['pubDate'])) # Recording time
		except Exception as e: print(e)

		# File type
		try: audio.add(TFLT(encoding=3, text="3 MPEG 1/2 layer III"))
		except Exception as e: print(e)

		# Unique file identifier
		try: audio.add(UFID(encoding=3, text=episode_data['guid']))
		except Exception as e: print(e)

		# Language(s) [Language of lyrics in ISO-639-2 e.g eng]
		try: audio.add(TLAN(encoding=3, text="eng"))
		except Exception as e: print(e)

		# Media type
		try: audio.add(TMED(encoding=3, text="Original MP3 audio from the podcast"))
		except Exception as e: print(e)

		# Comment spesifically for Tag&Rename
		try: audio.add(TENC(encoding=3, text="WEB-DL MP3"))
		except Exception as e: print(e)

		# User defined URL link frame
		try: audio.add(WXXX(encoding=0, desc=u'', url=episode_data['link']))
		except Exception as e: pass

		# User defined text information frame
		try: audio.add(TXXX(encoding=3, text="WEB-DL MP3 from samharris.org"))
		except Exception as e: print(e)
		
		try:
			audio.add(TIT3(encoding=3, text=episode_data['subtitle'])) # Subtitle/Description refinement
			audio.add(COMM(encoding=3, text=episode_data['subtitle'])) # Comments	
			audio.add(TDES(encoding=3, text=episode_data['subtitle'])) # iTunes Podcast Description	
			audio.add(COMM(encoding=3, text=episode_data['subtitle'])) # User comment
		except KeyError as e: pass
		except ValueError as e: pass

		# iTunes Podcast Flag
		try: audio.add(PCST(value=1))
		except Exception as e: print(e)

		# Episode number (Tag&Rename)
		try:
			episode_number = re.search(r'\d+', episode_data['title']).group()
		except Exception as e: print(e)
		try:
			audio.add(TXXX(encoding=1, desc='EpisodeNumber', text=episode_number))
			audio.add(TRCK(encoding=1, text=episode_number))
		except Exception as e: pass

		# Episode ID
		try: audio.add(TXXX(encoding=1, desc='EpisodeID', text=episode_data['guid']))
		except Exception as e: print(e)

		# Podcast category
		try: audio.add(TXXX(encoding=1, desc='EpisodeID', text='Philosophy'))
		except Exception as e: print(e)

		# Podcast category
		try: audio.add(TCAT(encoding=1, desc='EpisodeID', text='Philosophy'))
		except Exception as e: print(e)

		# Podcast ID
		try: audio.add(TGID(encoding=1, desc='EpisodeID', text=''))
		except Exception as e: print(e)

		# Podcast ID
		try: audio.add(WFED(encoding=1, url='https://www.samharris.org/podcasts/making-sense-episodes'))
		except Exception as e: print(e)

		# OriginalAlbum / Show title (Tag&Rename)
		try: audio.add(TOAL(encoding=1, text="Making Sense with Sam Harris - Subscriber Content"))
		except Exception as e: print(e)

		# Remember to change to image/jpeg if JPG or image/png if PNG.
		# Remember that no description should be similar.
		# More info at: https://mutagen-specs.readthedocs.io/en/latest/id3/id3v2.4.0-frames.html#attached-picture
		# -------------------------------------------------------
		try:
			mimetype = (mimetypes.MimeTypes().guess_type(img_dl)[0]) # Detect and set MIME type for the cover image
			audio.add(APIC(encoding=0, mime=mimetype, type=3, desc='Cover (front)', data=open(img_dl,'rb').read()))
		except Exception as e: print(e)

		audio.save(final_filename_fullpath)




		# -----------------------------------------------------------------------------
		# Removing redundant files
		# -----------------------------------------------------------------------------
		try: os.remove(img_dl)
		except Exception as e:
			print(e)
		try:os.remove(audio_dl)
		except Exception as e:
			print(e)




	else:
		print('💭 File already exist:', os.path.basename(final_filename_fullpath))