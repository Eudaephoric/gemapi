# gemapi utils
from threading import Thread
from threading import Event
import time
import websocket
import requests
import signal
import sys
import json

class GemKeyReader():

	def getKey(self):
		file = open('gemapikey')
		return file.read()

	def getSecret(self):
		file = open('gemapisecret')
		return file.read()

class GemSocket(Thread):
	def __init__(self, onMessage, onError = None):
		Thread.__init__(self)
		self.onMessage = onMessage
		self.onError = onError
		signal.signal(signal.SIGINT, self.stop)

	def run(self):
		self._ws = websocket.WebSocketApp("wss://api.gemini.com/v1/marketdata/BTCUSD", on_message=self.parseMessage, on_error=self.parseError)
		self._ws.run_forever(ping_interval=5)

	def parseMessage(self, ws, message):
		data = json.loads(message)
		event = data['events'][0]
		if event['type'] == 'trade':
			ms = data['timestampms']
			price = event['price']

			result = {
				'timestampms': ms,
				'price': price
			}
			self.onMessage(result)

	def parseError(self, ws, error):
		data = json.loads(error)
		self.onError(data)

	def stop(self, signal = None, frame = None):
		self._ws.keep_running = False

class GemRest(Thread):
	def __init__(self, history, callback):
		Thread.__init__(self)
		self.history = history
		self.callback = callback
		self.stopped = Event()
		# self.onMessage = onMessage
		# self.onError = onError
		signal.signal(signal.SIGINT, self.stop)

	def run(self):
		while not self.stopped.wait(5):
			self.callAPI()

	def callAPI(self):
		url = 'https://api.gemini.com/v1/trades/BTCUSD'
		currentms = lambda: int(round(time.time() * 1000))

		for ch in self.history:
			resp = requests.get(url + '?limit_trades=1&since=%d' % (currentms() - ch['time'] * 1000)).json()
			if resp:
				ch['price'].set(float(resp[0]['price']))
		self.callback(self.history)

	def stop(self, signal = None, frame = None):
		self.stopped.set()

def onMessage(msg):
	print(msg)

# arr = [{'price': 10, 'time': 10},
# 			{'price': 10, 'time': 300}]
# stopflag = Event()
# gr = GemRest( arr, onMessage)
# print(arr)
# gr.start()
# time.sleep(20)
# gr.stop()