### Test the connection status and port of external microphone. 

import pyaudio
p = pyaudio.PyAudio()

for i in range(p.get_device_count()):
	print(p.get_device_info_by_index(i).get('name'))
