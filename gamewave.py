#GameWave: An Interactive Educational Sound Exhibit
#By Rhiannon Chiacchiaro
#Program Code

#Imports and initializes pygame and other necessary libraries
import pygame, pygame.midi, pygame.font
pygame.init()
pygame.midi.init()
pygame.font.init()
from midi.MidiInFile import MidiInFile
import midi_events
import os
import pyaudio

#Creates a class playlist for all of the songs used
class Song:
	filename = None
	channel = None
	default_ins = None
	delay = None

def __init__(self, filename):
	self.filename = filename
	confname = filename[:-3] + "conf"
	f = open(confname)
	confdata = eval(f.read())
	self.channel = confdata["channel"]
	self.default_ins = confdata["default_ins"]
	self.delay = confdata["delay"]
	f.close()
	self.load()

def load(self):
	self.events = midi_events.MidiEvents()
	midi_in = MidiInFile (self.events, self.filename)	
	midi_in.read()
	self.data = self.events.event_list
	def play(self):
	global midi_data
	global main_channel
	global delay
	global program_time
	global note_index42
	global idle_count
	midi_data = self.data
	main_channel = self.channel
	delay = self.delay
	program_time = 0
	note_index = {}
	for index_channel in midi_data.keys():
		note_index[index_channel] = 0
	idle_count += 1

songlist = []

# Loads songs into the song list for playing
def midi_test(test_file):
	if test_file[-3:] == "mid":
		return True
	return False

def load_songs():
	files = os.listdir("Songfiles")
	midis = filter(midi_test, files)
	for f in midis:
		songlist.append(Song("Songfiles/"+f))

#Turns on the joystick controller.
jstick = pygame.joystick.Joystick(0)
jstick.init()

#Initializes variables
ins_list = [0, 2, 4, 6, 13, 19, 21, 23, 25, 34, 46, 56, 58, 65, 68, 71, 73, 75, 79]
next_ins = -1
stop = True
stop_time = 0.0
on_notes = []
program_time = 0
last_midi_time = 0
off_channel = 0x80
delay = 2.5
pitch_value = 0x40
main_channel = 0
song_number = 0
width = 1024
height = 480
screen = pygame.display.set_mode((width, height))
note_index = {}
idle_count = -1

#Loads button map
button_map = pygame.image.load ("controller_map.png")
button_map = pygame.transform.scale(button_map, (width/2.5, height/2))

#Configure and initialize the microphone for oscilloscope data
chunk_size = 1024
audio_format = pyaudio.paInt16
num_of_chans = 1
audio_rate = 44100
audio_config = pyaudio.PyAudio()
mic_in = audio_config.open(format = audio_format, channels = num_of_chans, rate =
audio_rate, input = True, frames_per_buffer = chunk_size)

#Set up font for idle mode
font = pygame.font.SysFont(u'tlwgtypewriter', 30, bold = True)

#Set up MIDI output port
midi_out = pygame.midi.Output(2, 0)

#Loads the songlist into the program
load_songs()
songlist[song_number].play()

#Main functions
quitflag = False
last_midi_time = pygame.midi.time()
status = {}
try:
	while quitflag == False:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				#Quit the program
				quitflag = True
			if event.type == pygame.JOYBUTTONDOWN:
				idle_count = 0
				#Stop/Start
				if event.button == 9:
					if stop == False:
						stop = True
						# Stop all currently playing notes
						for note in on_notes:
							midi_out.write_short(off_channel+note[1], note[0])
						elif stop == True:
							stop = False
							last_midi_time = pygame.midi.time()

				# Scroll through songs
				if event.button == 8:
					for note in on_notes:
						midi_out.write_short(off_channel+note[1], note[0])
						song_number += 1
						if song_number > len(songlist)-1:
							song_number = 0
							songlist[song_number].play()

				# Change instruments
				if event.button == 2:
					next_ins -= 1
					if next_ins <= 0:
						next_ins = len(ins_list) - 1
					if type(main_channel) == int:
						midi_out.write_short(0xc0+main_channel, ins_list[next_ins])
					elif type(main_channel) == tuple:
						for ins_channel in main_channel:
							midi_out.write_short(0xc0+ins_channel, ins_list[next_ins])
							if event.button == 1:
								next_ins += 1
								if next_ins >= len(ins_list):
									next_ins = 0
							if type(main_channel) == int:
								midi_out.write_short(0xc0+main_channel, ins_list[next_ins])
							elif type(main_channel) == tuple:
								for ins_channel in main_channel:
									midi_out.write_short(0xc0+ins_channel, ins_list[next_ins])
									if event.type == pygame.JOYAXISMOTION:
										idle_count = 0
				
				#Change tempo
				if event.value == 1 and event.axis == 3:
					delay -= 0.25
					if delay < 0.25:
						delay = 0.25
					if event.value < 0 and event.axis == 3:
						delay += 0.25
					
				#Change pitch
				if event.value < 0 and event.axis == 4:
					pitch_value += 8
						if pitch_value > 0x7F:
							pitch_value = 0x7F
				if type(main_channel) == int:
					midi_out.write_short(0xe0+main_channel, 0x00,  pitch_value)
				if type(main_channel) == tuple:
					for pitch_chan in main_channel:
						midi_out.write_short(0xe0+pitch_chan, 0x00, pitch_value)
						if event.value == 1 and event.axis == 4:
							pitch_value -= 8
							if pitch_value < 0:
								pitch_value = 0
								if type(main_channel) == int:
									midi_out.write_short(0xe0+main_channel, 0x00, pitch_value)
								if type(main_channel) == tuple:
									for pitch_chan in main_channel:
										midi_out.write_short(0xe0+pitch_chan, 0x00, pitch_value)
				
				#Play the next song in the queue automatically
				song_done = True
				for channel_key in midi_data.keys():
					if len(midi_data[channel_key]) > note_index[channel_key]:
						song_done = False
						break
					if song_done == True:
						song_number += 1
					if song_number > len(songlist)-1:
						song_number = 0
					songlist[song_number].play()
				
				# If program is not paused, process and play MIDI
				if stop == False:
					# Update time
					program_time += (pygame.midi.time() - last_midi_time) / delay
					last_midi_time = pygame.midi.time()
					# Get next MIDI events
					for channel in midi_data.keys():
						if len(midi_data[channel]) == note_index[channel]:
							continue
						if midi_data[channel][note_index[channel]][1] > (program_time):
							continue
						current_data = midi_data[channel][note_index[channel]]
						note_index[channel] += 1
						status[current_data[0][0]] = True
						# Process MIDI data
						# Store notes that are currently playing for start/stop function
						if (current_data[0][0] & 0xF0) == 0x90: # Note on command
							if current_data[0][2] > 0:
								on_notes.append ((current_data[0][1], channel))
							else:
								note = on_notes.index ((current_data[0][1], channel))
									del on_notes[note]
							if (current_data[0][0] & 0xF0) == 0x80: 
							# Note off command
								note = on_notes.index((current_data[0][1], channel))
								del on_notes[note]
							midi_out.write ([current_data])
				
				#Implement idle mode after 5 songs without user input
				if idle_count >= 5:
					stop = True
					# Stop all currently playing notes
					for note in on_notes:
						midi_out.write_short(off_channel+note[1], note[0])
				
				#Draws the graphical frame and creates the oscilloscope waveform
				screen.fill((0,0,0))
				samples = mic_in.read(chunk_size)
				for i in range(0, len(samples) - 2, 2):
					pygame.draw.line (screen, 0x49E9BD,(i / 2, height / 2 + (struct.unpack
					("<h", samples[i] + samples[i+1])[0] * height / 2**16)),(i / 2 + 1, height / 2 + (struct.unpack("<h", samples[i+2] + samples[i+3])[0] * height / 2**16)))

				#Makes the paused music text box
				if stop == True:
					text = font.render("Press START to continue.", False, (0xFF, 0xFF, 0xFF), (0x00, 0x00, 0x00))
					textrect = text.get_rect()
					textrect.center = (width/2, height/5)
					screen.blit(text, textrect)
					maprect = button_map.get_rect(center = (width/2, height/2))
					screen.blit(button_map, maprect)
				pygame.display.flip()

except:
raise