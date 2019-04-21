
import asyncio
import aiohttp


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


