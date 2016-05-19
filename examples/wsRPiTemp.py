import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import os
#import uart_service
######
import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART
import sys
sys.path.append('/home/pi/Adafruit_Python_BluefruitLE/examples/simon_speck')
from simon import SimonCipher

w = SimonCipher(0x1b1a1918131211100b0a090803020100, key_size=128, block_size=64)

# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()
######

def ble_ain():
	#global t
	# Clear any cached data because both bluez and CoreBluetooth have issues with
	# caching data and it going stale.
	ble.clear_cached_data()
	print 'ble_main()'
	# Get the first available BLE network adapter and make sure it's powered on.
	adapter = ble.get_default_adapter()
	adapter.power_on()
	print('Using adapter: {0}'.format(adapter.name))

 	# Disconnect any currently connected UART devices.  Good for cleaning up and
	# starting from a fresh state.
	print('Disconnecting any connected UART devices...')
	UART.disconnect_devices()

	# Scan for UART devices.
	print('Searching for UART device...')
	try:
		adapter.start_scan()
		# Search for the first UART device found (will time out after 60 seconds
		# but you can specify an optional timeout_sec parameter to change it).
		device = UART.find_device()
		if device is None:
			raise RuntimeError('Failed to find UART device!')
	finally:
		# Make sure scanning is stopped before exiting.
		adapter.stop_scan()

	print('Connecting to device...')
	device.connect()  # Will time out after 60 seconds, specify timeout_sec parameter to change the timeout.

    	# Once connected do everything else in a try/finally to make sure the device
	# is disconnected when done.
	try:
		# Wait for service discovery to complete for the UART service.  Will
		# time out after 60 seconds (specify timeout_sec parameter to override).
		print('Discovering services...')
		UART.discover(device,timeout_sec=5)
	
		# Once service discovery is complete create an instance of the service
		# and start interacting with it.
		uart = UART(device)
	
		# Write a string to the TX characteristic.
		# uart.write('Hello world!\r\n')
		#print("Send request to device...")
		#uart.write('r')
	
		# Now wait up to one minute to receive data from the device.
		print('Waiting up to 15 seconds to receive data from the device...')
		received = uart.read(timeout_sec=15)
		if received is not None:
			wd='0x'
			for i in reversed(received[0:8]):
				print('Received: {0}'.format(ord(i)))
				c=hex(ord(i))[2:]
				if len(c)<2:
					wd += '0'+c
				else:
					wd += c
				print(wd)
			t=w.decrypt(int(wd,16))
			print(hex(t))
			print("t-ul meu este")
			print(t)
			t1=hex(t)[2:]
			a=0
			b=2
			wsend=''
			for i in range(int(len(t1)/2)):
				wsend += str(int(t1[a:b],16))
				wsend+=';'
				a+=2
				b+=2
			print(wsend)
			wsSend(wsend)
			

		else:
			# Timeout waiting for data, None is returned.
			print('Received no data!')
	finally:
        	# Make sure device is disconnected on exit.
        	device.disconnect()
		#return 0
global ret	
ret=[]
def ble_setup():
	global ret
	# Clear any cached data because both bluez and CoreBluetooth have issues with
	# caching data and it going stale.
	ble.clear_cached_data()
	# Get the first available BLE network adapter and make sure it's powered on.
	adapter = ble.get_default_adapter()
	adapter.power_on()
	print('Using adapter: {0}'.format(adapter.name))

 	# Disconnect any currently connected UART devices.  Good for cleaning up and
	# starting from a fresh state.
	print('Disconnecting any connected UART devices...')
	UART.disconnect_devices()

	# Scan for UART devices.
	print('Searching for UART device...')
	try:
		adapter.start_scan()
		# Search for the first UART device found (will time out after 60 seconds
		# but you can specify an optional timeout_sec parameter to change it).
		device = UART.find_device()
		if device is None:
			raise RuntimeError('Failed to find UART device!')
	finally:
		# Make sure scanning is stopped before exiting.
		adapter.stop_scan()

	print('Connecting to device...')
	device.connect()  # Will time out after 60 seconds, specify timeout_sec parameter to change the timeout.

    	# Once connected do everything else in a try/finally to make sure the device
	# is disconnected when done.
	try:
		# Wait for service discovery to complete for the UART service.  Will
		# time out after 60 seconds (specify timeout_sec parameter to override).
		print('Discovering services...')
		UART.discover(device,timeout_sec=10)
	
		# Once service discovery is complete create an instance of the service
		# and start interacting with it.
		uart = UART(device)
		ret.append(uart)
		print("returning ret")
	finally:
		print(ret)
		return ret
        # Make sure device is disconnected on exit.
        #	device.disconnect()
		
global ctr
ctr = 0	
def ble_main():
	global ctr
	global ret
	print(ctr)
	print("ble_main()")
	if ctr==0:	
		ret=ble_setup()	
	ctr+=1
	print("ret in ble_main")
	print(ret)
	uart=ret[0]	
	#print("Send request to device...")
	#uart.write('r\r\n')
	
	# Now wait up to one minute to receive data from the device.
	print('Waiting up to 15 seconds to receive data from the device...')
	received = uart.read(timeout_sec=15)
	if received is not None:
		wd='0x'
		for i in reversed(received[0:8]):
			print('Received: {0}'.format(ord(i)))
			wd += hex(ord(i))[2:]
			print(wd)
		t=w.decrypt(int(wd,16))
		print(hex(t))
		print("t-ul meu este")
		print(t)
		t1=hex(t)[2:]
		a=0
		b=2
		mean=0
		for i in range(int(len(t1)/2)):
			mean += int(t1[a:b],16)
			a+=2
			b+=2
		mean /= 8
		print(mean)
		wsSend(str(float(mean))+';')
			

	else:
		# Timeout waiting for data, None is returned.
		print('Received no data!')
	

wss =[]
class WSHandler(tornado.websocket.WebSocketHandler):
	def check_origin(self, origin):
		return True
	def open(self):
		print('New user is connected.\n') 
		if self not in wss:
			wss.append(self)
	def on_close(self):
		print('connection closed\n')
		if self in wss:
			wss.remove(self)

application = tornado.web.Application([(r'/ws', WSHandler),])

  #os.system('modprobe w1-gpio')
  #os.system('modprobe w1-therm')
  
def wsSend(message):	
    	for ws in wss:
      		if not ws.ws_connection.stream.socket:
        		print("Web socket does not exist anymore!!!")
        		wss.remove(ws)
      		else:
        		ws.write_message(message)

def read_temp():
	try:
		print('start read_temp()')
		ble.initialize()
		ble.run_mainloop_with(ble_ain)
		print('end read_temp()')
	except:
		print(sys.exc_info()[0])
	#wsSend("-;-")

if __name__ == "__main__":

	interval_msec = 5000
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(8888)
    	
	main_loop = tornado.ioloop.IOLoop.instance()
	sched_temp = tornado.ioloop.PeriodicCallback(read_temp, interval_msec,   io_loop = main_loop)
	#ble.initialize()

	sched_temp.start()
	main_loop.start()
