import asab
import asyncio
from .proxy import ProxyService, HttpProxyProvider, FileProxyProvider


class Application(asab.Application):

	def __init__(self):
		super().__init__()
		self.ProxyService = ProxyService(self)
		self.ProxyService.add_provider(HttpProxyProvider(self, "HttpProxyProvider"))
		self.ProxyService.add_provider(FileProxyProvider(self, "FileProxyProvider"))

	async def main(self):
		while 1:
			proxy = await self.ProxyService.get()
			if not proxy:
				break

		self.stop()
