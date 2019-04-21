import asyncio
from .abc import LocalProxyProvider
from ..proxy import Proxy



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

