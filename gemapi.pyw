# test script

import tkinter
import threading
import websocket
import json
import time

class geminiApp(tkinter.Tk):
	def __init__(self,parent):
		tkinter.Tk.__init__(self,parent)
		currentms = lambda: int(round(time.time() * 1000))
		self.time5 = currentms() - 5000
		self.time10 = currentms() - 10000
		self.time30 = currentms() - 30000
		self.time60 = currentms() - 60000
		self._ws = None
		self.parent = parent
		self.initializeUI()
		self.initializeWS()
		self.setLabel()

	def initializeUI(self):
		self.grid()

		"""ROW 0"""

		self.btcLabel = tkinter.StringVar()
		tkinter.Label(self, text='BTC:', anchor='w', fg='white', bg='black') \
			.grid(column=0, row=0, sticky='EW')
		tkinter.Label(self, textvariable=self.btcLabel, width=8, anchor='w', fg='white', bg='black') \
			.grid(column=1, row=0, columnspan=2, sticky='EW')

		self.ethLabel = tkinter.StringVar()
		tkinter.Label(self, text='ETC: ', anchor='w', fg='white', bg='black') \
			.grid(column=3, row=0, sticky='EW')
		tkinter.Label(self, textvariable=self.ethLabel, width=8, anchor='w', fg='white', bg='black') \
			.grid(column=4, row=0, columnspan=2, sticky='EW')

		self.errorLabel = tkinter.StringVar()
		tkinter.Label(self, textvariable=self.errorLabel, width=8, anchor='w', fg='red', bg='black') \
			.grid(column=6, row=0, columnspan=2, sticky='EW')

		"""ROW 1"""

		tkinter.Label(self, text='5m', anchor='w').grid(row=1, column=0, sticky='EW')
		tkinter.Label(self, text='10m', anchor='w').grid(row=1, column=1, sticky='EW')
		tkinter.Label(self, text='30m', anchor='w').grid(row=1, column=2, sticky='EW')
		tkinter.Label(self, text='1h', anchor='w').grid(row=1, column=3, sticky='EW')
		"""ROW 2"""

		self.price5 = 0.00
		self.price10 = 0.00
		self.price30 = 0.00
		self.price60 = 0.00
		self.change5 = tkinter.StringVar()
		self.change5.set('-')
		self.change10 = tkinter.StringVar()
		self.change10.set('-')
		self.change30 = tkinter.StringVar()
		self.change30.set('-')
		self.change60 = tkinter.StringVar()
		self.change60.set('-')

		tkinter.Label(self, textvariable=self.change5, anchor='w') \
			.grid(column=0, row=2, sticky='EW')

		tkinter.Label(self, textvariable=self.change10, anchor='w') \
			.grid(column=1, row=2, sticky='EW')

		tkinter.Label(self, textvariable=self.change30, anchor='w') \
			.grid(column=2, row=2, sticky='EW')

		tkinter.Label(self, textvariable=self.change60, anchor='w') \
			.grid(column=3, row=2, sticky='EW')

		"""ROW 2"""

		# priceLabel = tkinter.Label(self, text='Price:', width=6, anchor='e', fg='white', bg='black')
		# priceLabel.grid(column=0, row=2, sticky='EW')

		# self.priceVar = tkinter.StringVar()
		# priceEntry = tkinter.Entry(self, width=9, textvariable=self.priceVar)
		# priceEntry.grid(column=1, row=2, sticky='EW')

		# amtLabel = tkinter.Label(self, text='Amt:', width=4, anchor='e', fg='white', bg='black')
		# amtLabel.grid(column=2, row=2, sticky='EW')
		# self.amtVar = tkinter.StringVar()
		# amtEntry = tkinter.Entry(self, width=9, textvariable=self.amtVar)
		# amtEntry.grid(column=3, row=2, sticky='EW')

		# buyBtn = tkinter.Button(self,text='Buy', command=self.OnButtonClick)
		# buyBtn.grid(column=4, row=2)

		# sellBtn = tkinter.Button(self,text='Sell', command=self.OnButtonClick)
		# sellBtn.grid(column=5, row=2)


		# self.grid_columnconfigure(0,weight=1)
		self.resizable(True,False)
		self.update()
		self.geometry(self.geometry())
		# self.entry.focus_set()
		self.protocol('WM_DELETE_WINDOW', self.onClose)

	def initializeWS(self):
		wst = threading.Thread(target=self.wsConnection)
		wst.daemon = True
		wst.start()

	def wsConnection(self):
		self._ws = websocket.WebSocketApp("wss://api.gemini.com/v1/marketdata/BTCUSD", on_message=self.onMessage, on_error=self.onError, on_close=self.onClose)
		self._ws.run_forever(ping_interval=5)

	def onMessage(self, ws, message):
		data = json.loads(message)
		event = data['events'][0]
		if event['type'] == 'trade':
			ms = data['timestampms']
			self.setLabel(event['price'])

			if (self.price5 == 0.0):
				self.price5 = float(event['price'])
			if (self.price10 == 0.0):
				self.price10 = float(event['price'])
			if (self.price30 == 0.0):
				self.price30 = float(event['price'])
			if (self.price60 == 0.0):
				self.price60 = float(event['price'])

			if ms - self.time5 >= 300000:
				price = float(event['price'])
				change = (price / self.price5) - 1
				self.change5.set('{:.2f}'.format(change))
				self.price5 = price
				self.time5 = ms
			if ms - self.time10 >= 600000:
				price = float(event['price'])
				change = (price / self.price10) - 1
				self.change10.set('{:.2f}'.format(change))
				self.price10 = price
				self.time10 = ms
			if ms - self.time30 >= 1800000:
				price = float(event['price'])
				change = (price / self.price30) - 1
				self.change30.set('{:.2f}'.format(change))
				self.price30 = price
				self.time30 = ms
			if ms - self.time60 >= 3600000:
				price = float(event['price'])
				change = (price / self.price60) - 1
				self.change60.set('{:.2f}'.format(change))
				self.price60 = price
				self.time60 = ms

	def onError(self, ws, error):
		self.errorLabel.set(error)

	def setLabel(self, btc='-', eth='-'):
		self.btcLabel.set(btc)
		self.ethLabel.set(eth)

	def onClose(self, error=None):
		self._ws.keep_running = False;
		self.destroy()

	# def _apiCall(self):
	# 	self.start()
	# 	self.setLabel('x', 'y')

	# def startTimer(self):
	# 	self._timer = threading.Timer(1.0, self._apiCall)
	# 	self._timer.start()

	def OnButtonClick(self):
		pass

	def OnPressEnter(self,event):
		pass

if __name__ == "__main__":
	app = geminiApp(None)
	app.title('GEMAPI')
	app.attributes('-topmost', 'true')
	app.mainloop()