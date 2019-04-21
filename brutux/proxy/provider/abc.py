import abc
import asyncio
import asab



class ABCProxyProvider(abc.ABC, asab.ConfigObject):

	ConfigDefaults = {
	}

	def __init__(self, app, id, config=None):
		super().__init__("proxyprovider:{}".format(id if id is not None else self.__class__.__name__), config)
		self.App = app
		self.Id = id

	async def enqueue(self, proxy):
		raise NotImplemented()

	async def get(self):
		raise NotImplemented()



class LocalProxyProvider(ABCProxyProvider):

	ConfigDefaults = {
		"max_size": 1000
	}

	def __init__(self, app, id, config=None):
		super().__init__(app, id, config)
		self._queue = asyncio.Queue(maxsize=self.Config["max_size"])

		app.PubSub.subscribe("Application.stop!", self._on_application_stop)


	async def enqueue(self, proxy):
		await self._queue.put(proxy)


	async def get(self):
		proxy = await self._queue.get()
		return proxy


	def _on_application_stop(self, message_type, counter):
		self._queue.put_nowait(None)

