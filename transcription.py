import websockets
import asyncio
import base64
import json
from configure import auth_key
import pyaudio
import sys
import random

# Stream data
FPB = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()

# link for assemblyai
URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"

# start the recording
stream = p.open(
	format=FORMAT,
	channels=CHANNELS,
	rate=RATE,
	input=True,
	frames_per_buffer=FPB
)

async def send_receive():

	print(f'\n\nConnecting websocket to url ${URL}')

	# create connection to websocket
	async with websockets.connect(
		URL,
		extra_headers=(("Authorization", auth_key),),
		ping_interval= 5,
		ping_timeout = 20
	) as _ws:

		# create session between script and assemblyai
		await asyncio.sleep(0.1)

		session_begins = await _ws.recv()

		print("Successfully connected. Say \'Help\' for list of commands.\n")


		# obtain data from audio stream, decode to 64 bits, and send to websocket API
		async def send():
			while True:
				try:
					data = stream.read(FPB)
					data = base64.b64encode(data).decode("utf-8")
					json_data = json.dumps({"audio_data":str(data)})
					await _ws.send(json_data)

				except websockets.exceptions.ConnectionClosedError as e:
					print(e)
					assert e.code == 4008
					break

				except Exception as e:
					assert False, "Not a websocket 4008 error."
				await asyncio.sleep(0.01)

			return True


		# receive the text conversions of the send audio and print
		async def receive():
			while True:
				try:
					result_str = await _ws.recv()

					# only consider completed sentences
					if json.loads(result_str)['message_type'] == 'FinalTranscript':
						message = json.loads(result_str)['text']

						if message == 'Help.' or message == 'help.':
							print('COMMANDS:\n' +
								'PRINT : print following message to terminal.\n' +
								'HELP : list commands in the terminal.\n' +
								'END TRANSCRIPTION : exit program.\n\n')

						elif message[:5] == 'Print' or message[:5] == 'print':
							space_index = message.find(' ') + 1
							print(message[space_index:])

						elif message == 'End transcription.':
							print('Ending transcription, thank you.\n')
							sys.exit()

				except websockets.exception.ConnectionClosedError as e:
					print(e)
					assert e.code == 4008
					break

				except Exception as e:
					assert False, "Not a websocket 4008 error"

		send_result, receive_result = await asyncio.gather(send(), receive())


# Run the send/receive loop
asyncio.run(send_receive())
