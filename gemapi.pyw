# GemAPI.pyw

import tkinter
import threading
import websocket
import requests
import json
import time
import importlib

gemutils = importlib.import_module('gemutils')

class GemAPI(tkinter.Tk):
	def __init__(self,parent):
		tkinter.Tk.__init__(self,parent)

		self._gs = gemutils.GemSocket(self.onMessage, self.onError)
		self._gs.start()
		self._rest = None
		self.parent = parent

		self.initializeUI()
		self.updatePriceHistory()

	def initializeUI(self):
		self.grid()

		# Row 0

		self.btcVar = tkinter.DoubleVar()
		self.btcVar.set('-')
		tkinter.Label(self, text='BTC:', anchor='w', fg='white', bg='black', font=('Segoe UI', 12)) \
			.grid(column=0, row=0, sticky='EW')
		tkinter.Label(self, textvariable=self.btcVar, width=8, anchor='w', fg='white', bg='black', font=('Segoe UI', 12)) \
			.grid(column=1, row=0, columnspan=2, sticky='EW')

		self.highVar = tkinter.DoubleVar()
		tkinter.Label(self, text='h:', anchor='w', fg='gray', bg='black', font=('Segoe UI', 8)) \
			.grid(column=5, row=0, sticky='E')
		tkinter.Label(self, textvariable=self.highVar, width=8, anchor='w', fg='gray', bg='black', font=('Segoe UI', 8)) \
			.grid(column=6, row=0, sticky='W')

		self.lowVar = tkinter.DoubleVar()
		tkinter.Label(self, text='l:', anchor='w', fg='gray', bg='black', font=('Segoe UI', 8)) \
			.grid(column=3, row=0, sticky='E')
		tkinter.Label(self, textvariable=self.lowVar, width=8, anchor='w', fg='gray', bg='black', font=('Segoe UI', 8)) \
			.grid(column=4, row=0, sticky='W')

		# Row 1
		tkinter.Label(self, text='5m', anchor='w').grid(row=1, column=0, columnspan=2, sticky='EW')
		tkinter.Label(self, text='10m', anchor='w').grid(row=1, column=2, columnspan=2, sticky='EW')
		tkinter.Label(self, text='30m', anchor='w').grid(row=1, column=4, columnspan=2, sticky='EW')
		tkinter.Label(self, text='1h', anchor='w').grid(row=1, column=6, columnspan=2, sticky='EW')

		# Row 2

		self.change = {
			5: {'price': tkinter.DoubleVar(), 'percent': tkinter.StringVar(), 'label': tkinter.Label()},
			10: {'price': tkinter.DoubleVar(), 'percent': tkinter.StringVar(), 'label': tkinter.Label()},
			30: {'price': tkinter.DoubleVar(), 'percent': tkinter.StringVar(), 'label': tkinter.Label()},
			60: {'price': tkinter.DoubleVar(), 'percent': tkinter.StringVar(), 'label': tkinter.Label()}
		}

		tkinter.Label(self, textvariable=self.change[5]['price'], fg='dim gray', width=8, anchor='w') \
			.grid(column=0, row=2, columnspan=2, sticky='EW')

		tkinter.Label(self, textvariable=self.change[10]['price'], fg='dim gray', width=8, anchor='w') \
			.grid(column=2, row=2, columnspan=2, sticky='EW')

		tkinter.Label(self, textvariable=self.change[30]['price'], fg='dim gray', width=8, anchor='w') \
			.grid(column=4, row=2, columnspan=2, sticky='EW')

		tkinter.Label(self, textvariable=self.change[60]['price'], fg='dim gray', width=8, anchor='w') \
			.grid(column=6, row=2, columnspan=2, sticky='EW')

		self.change[5]['label'] = tkinter.Label(self, textvariable=self.change[5]['percent'], anchor='w')
		self.change[5]['label'].grid(column=0, row=3, columnspan=2, sticky='EW')

		self.change[10]['label'] = tkinter.Label(self, textvariable=self.change[10]['percent'], anchor='w')
		self.change[10]['label'].grid(column=2, row=3, columnspan=2, sticky='EW')

		self.change[30]['label'] = tkinter.Label(self, textvariable=self.change[30]['percent'], anchor='w')
		self.change[30]['label'].grid(column=4, row=3, columnspan=2, sticky='EW')

		self.change[60]['label'] = tkinter.Label(self, textvariable=self.change[60]['percent'], anchor='w')
		self.change[60]['label'].grid(column=6, row=3, columnspan=2, sticky='EW')

		self.errorVar = tkinter.StringVar()
		self.errorLabel = tkinter.Label(self, textvariable=self.errorVar, anchor='w') \
			.grid(column=0, row=4, columnspan=8, sticky='EW')


		# Row 4

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

	def onMessage(self, message):
		price = float(message['price'])
		timestamp = message['timestampms']

		self.btcVar.set(price)

		if (not self.lowVar.get() or self.lowVar.get() > price):
			self.lowVar.set(price)

		if (not self.highVar.get() or self.highVar.get() < price):
			self.highVar.set(price)

		self.updateChange(5, price)
		self.updateChange(10, price)
		self.updateChange(30, price)
		self.updateChange(60, price)

	def updateChange(self, cat, price):
		percent = lambda x, y: ((x - y) / x) * 100
		p = self.change[cat]['price'].get()
		if p:
			c = percent(price, p)
			self.change[cat]['label'].configure(fg='green') if c >= 0 else self.change[cat]['label'].configure(fg='red')
			self.change[cat]['percent'].set( self.formatPrice( c ) + '%')

	def formatPrice(self, dbl):
		return '{:.2f}'.format(dbl)

	def onSocketError(self, error):
		print(error)

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
			self.change[5]['price'].set(price)

		resp = requests.get(url + '?limit_trades=1&since=%d' % (currentms() - 600000))
		data = resp.json()
		if data:
			price = float(data[0]['price'])
			self.change[10]['price'].set(price)

		resp = requests.get(url + '?limit_trades=1&since=%d' % (currentms() - 1800000))
		data = resp.json()
		if data:
			price = float(data[0]['price'])
			self.change[30]['price'].set(price)

		resp = requests.get(url + '?limit_trades=1&since=%d' % (currentms() - 3600000))
		data = resp.json()
		if data:
			price = float(data[0]['price'])
			self.change[60]['price'].set(price)

		self.startRestThread()

	def onError(self, ws, error):
		self.errorVar.set(error)

	def onClose(self, error=None):
		# self._ws.keep_running = False;
		self._gs.stop()
		self._rest.cancel()
		self.destroy()

	def OnButtonClick(self):
		pass

	def OnPressEnter(self,event):
		pass

if __name__ == "__main__":
	app = GemAPI(None)
	app.title('GEMAPI')
	app.attributes('-topmost', 'true')
	app.mainloop()