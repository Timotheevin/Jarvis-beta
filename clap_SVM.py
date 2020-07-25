import pyaudio
import numpy as np
from scipy import signal
import time
import struct
import wave
from sklearn import svm
from joblib import dump
from tempfile import TemporaryFile


class Listener:

	def __init__(self):
		# constants
		self.CHUNK = 1024 * 2			 # samples per frame
		self.FORMAT = pyaudio.paInt16	 # audio format (bytes per sample)
		self.CHANNELS = 1				 # single channel for microphone
		self.RATE = 44100				 # samples per second
		self.wav = wave.open('data.wav', mode = 'wb')
		self.wav.setnchannels(self.CHANNELS)
		self.wav.setsampwidth(2)
		self.wav.setframerate(self.RATE)
		
		self.timer = time.time()
		
		self.tab = []
		self.dt_c = []
		self.dt_pc = []

	
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

		print('stream started')

		while time.time() - self.timer < 20:
			print(time.time() - self.timer)
			# binary data
			data = stream.read(self.CHUNK)  
	
			# convert data to integers, make np array
			data_np = np.array(struct.unpack(str(self.CHUNK) + 'h', data))
					
			self.first_test(data_np, data, stream)
			
		while time.time() - self.timer < 40:
			print(time.time() - self.timer)
			# binary data
			data = stream.read(self.CHUNK)  
	
			# convert data to integers, make np array
			data_np = np.array(struct.unpack(str(self.CHUNK) + 'h', data))
			
			self.first_test2(data_np, data)
			
		
		
		self.wav.close()
		self.arrange_data()
		
	def arrange_data(self):
		pos = int(self.play_audio_file('data.wav'))
		
		print('pos = ', pos)
		data_clap = self.tab[:pos]
		print('len(data_clap) = ', len(data_clap))
		data_no_clap = self.tab[pos:]
		print('len(data_pas_clap) = ', len(data_no_clap))
		
		self.classification(data_clap, data_no_clap)
		
		
	def classification(self, data_clap, data_no_clap):
		print('processing...')
		for i in range(len(data_clap)):
			f1, t1, Sxx1 = signal.spectrogram(data_clap[i], 44100)
			count_list = []
			for j in range(len(Sxx1)):
				count = 0
				for k in range(len(Sxx1[0])):
					count += Sxx1[j][k]
				count = count / len(Sxx1[0])
				count_list.append(count)
			self.dt_c.append(count_list)
			
		for i in range(len(data_no_clap)):
			f2, t2, Sxx2 = signal.spectrogram(data_no_clap[i], 44100)
			count_list = []
			for j in range(len(Sxx2)):
				count = 0
				for k in range(len(Sxx2[0])):
					count += Sxx2[j][k]
				count = count / len(Sxx2[0])
				count_list.append(count)
			self.dt_pc.append(count_list)
		
		self.fit_SVM(self.dt_c, self.dt_pc)
		
		
	def fit_SVM(self, dt_c, dt_pc):
		Svm = svm.SVC(gamma='scale')
		X, y = np.array(dt_c + dt_pc), ['clap'] * len(dt_c) + ['pas clap'] * len(dt_pc)
		outfile = "dataset"
		np.save(outfile, X)
		print('operations done.')
		Svm.fit(X, y)
		print('fit done.')
		dump(Svm, 'svm.joblib')
		print('svm dumped with success !')
	
	
	def first_test(self, data_np, data, stream):
		if np.max(data_np) >= 1000:
			self.wav.writeframesraw(data)
			self.tab.append(data_np)
			for i in range(10):
				stream.read(self.CHUNK)
				
	def first_test2(self, data_np, data):
		if np.max(data_np) >= 1000:
			self.wav.writeframesraw(data)
			self.tab.append(data_np)
	
	
	def play_audio_file(self, fname):
	
		stop = False
		
		file_wav = wave.open(fname, 'rb')
		
		audio = pyaudio.PyAudio()
		stream_out = audio.open(
			format=audio.get_format_from_width(file_wav.getsampwidth()),
			channels=file_wav.getnchannels(),
			rate=file_wav.getframerate(), input=False, output=True)
		stream_out.start_stream()
			
		while not stop:
		
			file_data = file_wav.readframes(2048)
			stream_out.write(file_data)
			time.sleep(0.2)
			stop = input('(O/n):')
			
		stream_out.stop_stream()
		stream_out.close()
		audio.terminate()	
		return (file_wav.tell()/ 2048) - 2



listener = Listener()
listener.background_listening()