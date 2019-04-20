import abc
import asyncio
import aiohttp
import asab

from .proxy import Proxy


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



class HttpProxyProvider(LocalProxyProvider):

	ConfigDefaults = {
		"url": ""
	}

	def __init__(self, app, id, config=None):
		super().__init__(app, id, config)
		self._url = self.Config["url"]
		self._buffer = ""
		asyncio.ensure_future(self._fetch_proxies())


	async def _fetch_proxies(self):
		# TODO: implement logic for graceful exit

		async with aiohttp.ClientSession() as session:
			async with session.get(self._url) as resp:
				if resp.status != 200:
					L.error("Received status {} fetching proxy list")
					return

				while 1:
					chunk = await resp.content.read(5)
					
					if not chunk:
						await self._finalize()
						break

					await self._read_chunk(chunk)


	async def _finalize(self):
		url = self._buffer
		if len(url) > 0:
			await self.enqueue(Proxy(self, url))
		self._buffer = ""


	async def _read_chunk(self, chunk):
		self._buffer += chunk.decode('utf-8')

		parts = self._buffer.rsplit('\n', 1)
		if len(parts) == 1:
			return

		_new_proxies, self._buffer = parts
		for url in _new_proxies.split('\n'):
			url = url.strip()
			if len(url) > 0:
				await self.enqueue(Proxy(self, url))



class FileProxyProvider(LocalProxyProvider):

	ConfigDefaults = {
		"path": ""
	}

	def __init__(self, app, id, config=None):
		super().__init__(app, id, config)
		self._path = self.Config["path"]
		asyncio.ensure_future(self._read_proxies())


	async def _read_proxies(self):
		with open(self._path, "rb") as f:
			while 1:
				url = f.readline()
				if not url:
					break
				url = url.decode("utf-8").strip()
				if len(url) > 0:
					await self.enqueue(Proxy(self, url))


