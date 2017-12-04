# test script

import tkinter
import threading
import websocket
import requests
import json
import time

class geminiApp(tkinter.Tk):
	def __init__(self,parent):
		tkinter.Tk.__init__(self,parent)

		self._ws = None
		self._rest = None
		self.parent = parent

		self.initializeUI()
		self.initializeWS()
		self.updatePriceHistory()
		self.setLabel()

	def initializeUI(self):
		self.grid()

		"""ROW 0"""

		self.btcLabel = tkinter.StringVar()
		tkinter.Label(self, text='BTC:', anchor='w', fg='white', bg='black', font=('Segoe UI', 12)) \
			.grid(column=0, row=0, sticky='EW')
		tkinter.Label(self, textvariable=self.btcLabel, width=8, anchor='w', fg='white', bg='black', font=('Segoe UI', 12)) \
			.grid(column=1, row=0, columnspan=2, sticky='EW')

		self.highVar = tkinter.DoubleVar()
		tkinter.Label(self, text='h:', anchor='w', fg='gray', bg='black', font=('Segoe UI', 8)) \
			.grid(column=3, row=0, sticky='E')
		tkinter.Label(self, textvariable=self.highVar, width=8, anchor='w', fg='gray', bg='black', font=('Segoe UI', 8)) \
			.grid(column=4, row=0, sticky='W')

		self.lowVar = tkinter.DoubleVar()
		tkinter.Label(self, text='l:', anchor='w', fg='gray', bg='black', font=('Segoe UI', 8)) \
			.grid(column=5, row=0, sticky='E')
		tkinter.Label(self, textvariable=self.lowVar, width=8, anchor='w', fg='gray', bg='black', font=('Segoe UI', 8)) \
			.grid(column=6, row=0, sticky='W')

		# self.errorLabel = tkinter.StringVar()
		# tkinter.Label(self, textvariable=self.errorLabel, width=8, anchor='w', fg='red', bg='black', font=('Segoe UI', 12)) \
		# 	.grid(column=6, row=0, columnspan=2, sticky='EW')

		"""ROW 1"""

		tkinter.Label(self, text='5m', anchor='w').grid(row=1, column=0, columnspan=2, sticky='EW')
		tkinter.Label(self, text='10m', anchor='w').grid(row=1, column=2, columnspan=2, sticky='EW')
		tkinter.Label(self, text='30m', anchor='w').grid(row=1, column=4, columnspan=2, sticky='EW')
		tkinter.Label(self, text='1h', anchor='w').grid(row=1, column=6, columnspan=2, sticky='EW')

		"""ROW 2"""

		self.price5 = tkinter.DoubleVar()
		self.price10 = tkinter.DoubleVar()
		self.price30 = tkinter.DoubleVar()
		self.price60 = tkinter.DoubleVar()

		self.change5 = tkinter.StringVar()
		self.change10 = tkinter.StringVar()
		self.change30 = tkinter.StringVar()
		self.change60 = tkinter.StringVar()

		self.price5label = tkinter.Label(self, textvariable=self.price5, fg='dim gray', width=8, anchor='w')
		self.price5label.grid(column=0, row=2, columnspan=2, sticky='EW')

		self.price10label = tkinter.Label(self, textvariable=self.price10, fg='dim gray', width=8, anchor='w')
		self.price10label.grid(column=2, row=2, columnspan=2, sticky='EW')

		self.price30label = tkinter.Label(self, textvariable=self.price30, fg='dim gray', width=8, anchor='w')
		self.price30label.grid(column=4, row=2, columnspan=2, sticky='EW')

		self.price60label = tkinter.Label(self, textvariable=self.price60, fg='dim gray', width=8, anchor='w')
		self.price60label.grid(column=6, row=2, columnspan=2, sticky='EW')

		self.change5label = tkinter.Label(self, textvariable=self.change5, anchor='w')
		self.change5label.grid(column=0, row=3, columnspan=2, sticky='EW')

		self.change10label = tkinter.Label(self, textvariable=self.change10, anchor='w')
		self.change10label.grid(column=2, row=3, columnspan=2, sticky='EW')

		self.change30label = tkinter.Label(self, textvariable=self.change30, anchor='w')
		self.change30label.grid(column=4, row=3, columnspan=2, sticky='EW')

		self.change60label = tkinter.Label(self, textvariable=self.change60, anchor='w')
		self.change60label.grid(column=6, row=3, columnspan=2, sticky='EW')

		"""ROW 2"""

		# priceLabel = tkinter.Label(self, text='Price:', width=6, anchor='e', fg='white', bg='black')
		# priceLabel.grid(column=0, row=2, sticky='EW')

		# self.priceVar = tkinter.StringVar()
		# priceEntry = tkinter.Entry(self, width=9, textvariable=self.priceVar)
		# priceEntry.grid(column=1, row=2, sticky='EW')

		# buyBtn = tkinter.Button(self,text='Buy', command=self.OnButtonClick)
		# buyBtn.grid(column=4, row=2)

		# self.grid_columnconfigure(0,weight=1)
		self.configure(bg = 'black')
		self.resizable(True,False)
		self.update()
		self.geometry(self.geometry())
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
			self.setLabel(event['price'])
			ms = data['timestampms']
			price = float(event['price'])

			if (self.highVar.get() == 0.0):
				self.highVar.set(price)
				self.lowVar.set(price)
			if (self.highVar.get() < price): self.highVar.set(price)
			if (self.lowVar.get() > price): self.lowVar.set(price)

			percent = lambda x, y: ((x - y) / x) * 100

			self.change5.set('{:.2f}'.format(percent(price, self.price5.get())) + '%') if self.price5.get() != 0.0 else self.change5.set('-')
			self.change5label.configure(fg='green') if percent(price, self.price5.get()) >= 0 else self.change5label.configure(fg='red')

			self.change10.set('{:.2f}'.format(percent(price, self.price10.get())) + '%') if self.price10.get() != 0.0 else self.change10.set('-')
			self.change10label.configure(fg='green') if percent(price, self.price10.get()) >= 0 else self.change10label.configure(fg='red')

			self.change30.set('{:.2f}'.format(percent(price, self.price30.get())) + '%') if self.price30.get() != 0.0 else self.change30.set('-')
			self.change30label.configure(fg='green') if percent(price, self.price30.get()) >= 0 else self.change30label.configure(fg='red')

			self.change60.set('{:.2f}'.format(percent(price, self.price60.get())) + '%') if self.price60.get() != 0.0 else self.change60.set('-')
			self.change60label.configure(fg='green') if percent(price, self.price60.get())>= 0 else self.change60label.configure(fg='red')

	def startRestThread(self):
		self._rest = threading.Timer(10, self.updatePriceHistory)
		self._rest.start()

	def updatePriceHistory(self):
		url = 'https://api.gemini.com/v1/trades/BTCUSD'
		currentms = lambda: int(round(time.time() * 1000))

		self.lastTimeUpdate = currentms()

		resp = requests.get(url + '?limit_trades=1&since=%d' % (currentms() - 300000))
		data = resp.json()
		if data:
			price = float(data[0]['price'])
			self.price5.set(price)

		resp = requests.get(url + '?limit_trades=1&since=%d' % (currentms() - 600000))
		data = resp.json()
		if data:
			price = float(data[0]['price'])
			self.price10.set(price)

		resp = requests.get(url + '?limit_trades=1&since=%d' % (currentms() - 1800000))
		data = resp.json()
		if data:
			price = float(data[0]['price'])
			self.price30.set(price)

		resp = requests.get(url + '?limit_trades=1&since=%d' % (currentms() - 3600000))
		data = resp.json()
		if data:
			price = float(data[0]['price'])
			self.price60.set(price)

		self.startRestThread()

	def onError(self, ws, error):
		self.errorLabel.set(error)

	def setLabel(self, btc='-'):
		self.btcLabel.set(btc)

	def onClose(self, error=None):
		self._ws.keep_running = False;
		self._rest.cancel()
		self.destroy()

	def OnButtonClick(self):
		pass

	def OnPressEnter(self,event):
		pass

if __name__ == "__main__":
	app = geminiApp(None)
	app.title('GEMAPI')
	app.attributes('-topmost', 'true')
	app.mainloop()