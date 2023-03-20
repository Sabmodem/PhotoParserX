import asyncio
import websockets
from logger import logging, loggerInit
from config import common as conf

class Server:
  def __init__(self):
    self.clients = set()

  async def register(self, ws):
    self.clients.add(ws)
    logging.info(f'{ws.remote_address} connects')

  async def unregister(self, ws):
    self.clients.remove(ws)
    logging.info(f'{ws.remote_address} disconnects')

  async def broadcast(self, msg):
    if self.clients:
      await asyncio.gather(*[client.send(msg) for client in self.clients])

  async def ws_handler(self, ws):
    await self.register(ws)
    try:
      await self.distribute(ws)
    finally:
      await self.unregister(ws)

  async def distribute(self, ws):
    async for msg in ws:
      await self.broadcast(msg)

async def main():
  loggerInit('wsserver.log')
  async with websockets.serve(Server().ws_handler, conf.ws_listen_addr, conf.ws_port):
      await asyncio.Future()

if __name__ == '__main__':
  asyncio.run(main())
