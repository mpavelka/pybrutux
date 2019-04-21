import asyncio
import aiohttp
from .abc import LocalProxyProvider
from ..proxy import Proxy



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
