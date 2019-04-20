import asab
import asyncio
import aiohttp
import logging

###

L = logging.getLogger(__name__)

###

class ProxyService(asab.Service):

	def __init__(self, app):
		super().__init__(app, "ProxiesService")
		self._providers = []
		self._index = 0


	def add_provider(self, provider):
		for p in self._providers:
			if p.Id == provider.Id:
				raise RuntimeError("Provider '{}' already added.".format(p.Id))
		self._providers.append(provider)


	async def enqueue(self, proxy):
		await proxy.Provider.enqueue(proxy)


	async def get(self):
		if len(self._providers) == 0:
			return None

		proxy = await self._providers[self._index].get()
		
		# Round robin
		self._index += 1
		if self._index == len(self._providers):
			self._index = 0

		return proxy

