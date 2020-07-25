import pyaudio
import struct
import numpy as np
import matplotlib.pyplot as plt
import speech_recognition as sr
import win32com.client as winc
import os
import sys
import time
import pyautogui as pag
import win32api
import win32con
import pickle
from joblib import load
from scipy import signal
from tkinter import * 

tk = False
voice = True

r = sr.Recognizer()

speak = winc.Dispatch("SAPI.SpVoice")
speak.Volume = 100
speak.Rate = 2

clf = load('svm.joblib')
s = pickle.dumps(clf)
svm = pickle.loads(s)

# speak.Voice = speak.GetVoices('Name=Microsoft Zira')


class Listener:

	def __init__(self):
		# constants
		self.CHUNK = 1024 * 2			 # samples per frame
		self.FORMAT = pyaudio.paInt16	 # audio format (bytes per sample)
		self.CHANNELS = 1				 # single channel for microphone
		self.RATE = 44100				 # samples per second
		
		self.win = Tk()
	 
	def background_listening(self):

		# pyaudio class instance
		p = pyaudio.PyAudio()

		# stream object to get data from microphone
		stream = p.open(
			format=self.FORMAT,
			channels=self.CHANNELS,
			rate=self.RATE,
			input=True,
			output=True,
			frames_per_buffer=self.CHUNK
		)
		   
		if tk:
			self.tk1()

		print('stream started')

		while True:
			
			# binary data
			data = stream.read(self.CHUNK)  
	
			# convert data to integers, make np array
			data_np = np.array(struct.unpack(str(self.CHUNK) + 'h', data))
			
			if self.first_test(data_np):
				if self.second_test(data_np):
					self.look_for_jarvis()
					for i in range(4):
						stream.read(self.CHUNK)

			if tk:
				self.tk2()
		
	def first_test(self, data_np):
		if np.max(data_np) >= 1000:
			return True
			
	def second_test(self, data_np):
		f, t, Sxx = signal.spectrogram(data_np, 44100)
		X = []
		for j in range(len(Sxx)):
			count = 0
			for k in range(len(Sxx[0])):
				count += Sxx[j][k]
			count = count / len(Sxx[0])
			X.append(count)
		print(svm.predict(np.array(X).reshape(1,-1)))
		if svm.predict(np.array(X).reshape(1,-1)) == ['clap']:
			return True
		else:
			return False
	
	def look_for_jarvis(self):
		
		with sr.Microphone() as source:
			# audio = r.listen(source, timeout = 3, phrase_time_limit = 3)
			audio = r.listen(source, phrase_time_limit = 3)
			try:
				speech_fr = r.recognize_google(audio, language = "fr-FR")
				print(speech_fr)
				if 'Jarvis' in speech_fr:
					if voice:
						speak.Speak('Bien sur !')
					print("I'm here for you")
					manager = Manager(speech_fr)
					manager.manage()
					
				else:
					pass
			except:
				pass
		print('listening...')

	def tk1(self):
		# create matplotlib figure and axes
		fig, ax = plt.subplots(1, figsize=(15, 7))

		# variable for plotting
		x = np.arange(0, 2 * self.CHUNK, 2)

		# create a line object with random data
		line, = ax.plot(x, np.random.rand(self.CHUNK), '-', lw=2)

		# basic formatting for the axes
		ax.set_title('AUDIO WAVEFORM')
		ax.set_xlabel('samples')
		ax.set_ylabel('volume')
		ax.set_ylim(0, 128)
		ax.set_xlim(0, 2 * self.CHUNK)
		plt.setp(ax, xticks=[0, self.CHUNK, 2 * self.CHUNK], yticks=[0, 128, 255])

		# show the plot
		plt.show(block=False)

	def tk2(self, line, fig):
		line.set_ydata(data_np)
		
		# update figure canvas
		try:
			fig.canvas.draw()
			fig.canvas.flush_events()
			
		except TclError:
			pass #chercher comment mettre un break ici

class Manager:

	def __init__(self, command):
		self.command = command.split(' ')[1:]
		if type(self.command) == list:
			self.command = ' '.join(self.command)
	
	def manage(self):
		print(self.command)
		if 'joue' in self.command:
			self.play_music()
		elif 'veille' in self.command:
			self.veille()
		elif 'session' in self.command:
			self.close_session()
		elif 'son' in self.command:
			self.son()
				
	def quit(self):
		print('cleaning up ...')
		print('checking for update ...')
		if voice:
			speak.Speak("C'est un plaisir de vous avoir aidé !")
			speak.Speak("Au revoir !")
		print('closing ...')
		sys.exit(0)
		
	def translate(self):

		print("\033[1m", word, "\033[0m", '\n')

		#teste si le mot existe en français ou en anglais
		urlcheck = "https://fr.wiktionary.org/wiki/{}".format(word)
		htmlcheck = urlopen(urlcheck)
		soupcheck = BeautifulSoup(htmlcheck, 'html.parser')
		isFrench = soupcheck.find(id='Français') != None
		isEnglish = soupcheck.find(id='Anglais') != None
		print("Français : ", "\033[1m", "Oui" if isFrench else "Non", "\033[0m")
		print("Anglais : ", "\033[1m", "Oui" if isEnglish else "Non", "\033[0m")

		#traduit le mot en français
		if (isEnglish):
			req = Request("https://translate.google.com/?hl=fr&ie=UTF8&text={0}&langpair=en|fr".format(word), headers={'User-Agent': 'Mozilla/5.0'})
			htmltrad_fr = urlopen(req).read()
			souptrad_fr = BeautifulSoup(htmltrad_fr, 'html.parser')
			result_fr = souptrad_fr.find(title=word)
			if result_fr != None:
				result_fr = result_fr.string
				print("Tranduction française : ", "\033[31;1m", result_fr, "\033[0m")
			else:
				print("Pas de traduction française disponible")
					
			speak.Speak(word + "signifie" + result_fr)


		#traduit le mot en anglais
		if (isFrench):
			req = Request("https://translate.google.com/?hl=fr&ie=UTF8&text={0}&langpair=fr|en".format(word), headers={'User-Agent': 'Mozilla/5.0'})
			htmltrad_en = urlopen(req).read()
			souptrad_en = BeautifulSoup(htmltrad_en, 'html.parser')
			result_en = souptrad_en.find(title=word)
			if result_en != None:
				result_en = result_en.string
				print("Tranduction anglaise : ", "\033[31;1m", result_en, "\033[0m")
			else:
				print("Pas de traduction anglaise disponible")
					
			speak.Speak(word + "signifie" + result_en)

		#affiche les synonymes
		if (isFrench):
			urlsyn = "http://www.crisco.unicaen.fr/des/synonymes/{}".format(word)
			htmlsyn = urlopen(urlsyn)
			soupsyn = BeautifulSoup(htmlsyn, 'html.parser')
			tabsyn = soupsyn.table.find_all('a')
	
		print("Liste des synonymes dans l'ordre de pertinence", "\033[31;1m")
		for obj_a in tabsyn:
			print(obj_a.string)
		print("\033[0m")	
				
	def play_music(self):
		music = self.command.split(' ')[1:]
		if type(music) == list:
			music = ' '.join(music)
		print(music)
		
		os.system('start spotify.exe')
		if voice:
			speak.Speak('Lancement de Spotify')
		else:
			time.sleep(3)
		pag.hotkey('ctrl', 'l')
		pag.typewrite(music)
		pag.hotkey('win', 'up')
		if voice:
			speak.Speak('Sélection de la musique')
		else:
			time.sleep(3)
		win32api.SetCursorPos([950,360])
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
		time.sleep(2)
		pag.hotkey('win', 'down')
		pag.hotkey('win', 'down')
		
	def veille(self):
		if voice:
			speak.Speak('Mise en veille de la session dans 3, 2, 1')
		os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
		
	def close_session(self):
		if voice:
			speak.Speak('Mise en veille de la session dans 3, 2, 1')
		os.system('rundll32.exe user32.dll,LockWorkStation')
		sys.exit(0)
	
	def son(self):
		if 'enceinte' in self.command:
			pag.hotkey('ctrl', 'alt', 'e')
		elif 'casque' in self.command:
			pag.hotkey('ctrl', 'alt', 'c')
		elif 'télé' in self.command:
			pag.hotkey('ctrl', 'alt', 't')
		elif 'baisse' in self.command:
			for i in range(20):
				pag.press('volumedown')
		elif 'monte' in self.command:
			for i in range(20):
				pag.press('volumeup')
		elif 'coupe' or 'remet' in self.command:
			print('mute')
			pag.press('volumemute')













listener = Listener()
listener.background_listening()