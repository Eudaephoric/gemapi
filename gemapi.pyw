# GemAPI.pyw

import tkinter
import importlib
import signal

gemutils = importlib.import_module('gemutils')

class GemAPI(tkinter.Tk):
	def __init__(self,parent):
		tkinter.Tk.__init__(self,parent)

		self._rest = None
		self.parent = parent
		self.initializeUI()

		self._gs = gemutils.GemSocket(self.onMessage, self.onError)
		self._gs.start()
		self._gr = gemutils.GemRest(self.history, self.historyCallback)
		self._gr.start()

		signal.signal(signal.SIGINT, self.onClose)

	def initializeUI(self):
		self.grid()

		# Row 0

		self.btcVar = tkinter.DoubleVar()
		self.btcVar.set('0.0')
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
		tkinter.Label(self, text='1m', anchor='w').grid(row=1, column=0, columnspan=2, sticky='EW')
		tkinter.Label(self, text='5m', anchor='w').grid(row=1, column=2, columnspan=2, sticky='EW')
		tkinter.Label(self, text='10m', anchor='w').grid(row=1, column=4, columnspan=2, sticky='EW')
		tkinter.Label(self, text='30m', anchor='w').grid(row=1, column=6, columnspan=2, sticky='EW')
		tkinter.Label(self, text='1h', anchor='w').grid(row=1, column=8, columnspan=2, sticky='EW')

		# Row 2

		self.history = [
			{'time': 60, 'price': tkinter.DoubleVar(), 'percent': tkinter.StringVar(), 'label': tkinter.Label()},
			{'time': 300, 'price': tkinter.DoubleVar(), 'percent': tkinter.StringVar(), 'label': tkinter.Label()},
			{'time': 600, 'price': tkinter.DoubleVar(), 'percent': tkinter.StringVar(), 'label': tkinter.Label()},
			{'time': 1800, 'price': tkinter.DoubleVar(), 'percent': tkinter.StringVar(), 'label': tkinter.Label()},
			{'time': 3600, 'price': tkinter.DoubleVar(), 'percent': tkinter.StringVar(), 'label': tkinter.Label()}
		]

		for x in range(0, len(self.history)):
			tkinter.Label(self, textvariable=self.history[x]['price'], fg='dim gray', width=8, anchor='w') \
				.grid(column=x*2, row=2, columnspan=2, sticky='EW')

			self.history[x]['label'] = tkinter.Label(self, textvariable=self.history[x]['percent'], anchor='w')
			self.history[x]['label'].grid(column=x*2, row=3, columnspan=2, sticky='EW')

		self.errorVar = tkinter.StringVar()
		self.errorLabel = tkinter.Label(self, textvariable=self.errorVar, anchor='w') \
			.grid(column=0, row=4, columnspan=10, sticky='EW')


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

	def historyCallback(self, history):
		self.history = history
		self.updateHistory()

	def onMessage(self, message):
		price = float(message['price'])
		timestamp = message['timestampms']

		self.btcVar.set(price)

		if (not self.lowVar.get() or self.lowVar.get() > price):
			self.lowVar.set(price)

		if (not self.highVar.get() or self.highVar.get() < price):
			self.highVar.set(price)

		self.updateHistory()

	def updateHistory(self):
		percent = lambda x, y: ((x - y) / x) * 100
		price = self.btcVar.get()

		for x in range(0, len(self.history)):
			p = self.history[x]['price'].get()
			if p and price:
				c = percent(price, p)
				self.history[x]['label'].configure(fg='green') if c >= 0 else self.history[x]['label'].configure(fg='red')
				self.history[x]['percent'].set( self.formatPrice( c ) + '%')

	def formatPrice(self, dbl):
		return '{:.2f}'.format(dbl)

	def onError(self, ws, error):
		self.errorVar.set(error)

	def onClose(self, signal = None, frame = None):
		# self._ws.keep_running = False;
		self._gs.stop()
		self._gr.stop()
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