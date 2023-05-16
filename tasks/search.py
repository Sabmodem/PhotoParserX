import httpx
from uuid import uuid4
import asyncio
import json
from datetime import datetime
import db
from itertools import chain
from random import randrange
import websockets
from logger import logging, loggerInit
from config import common as conf

def errCount():
  errCount = 0
  while 1:
    yield errCount
    errCount = (errCount + 1) % 5

async def notifyStatusChange(id):
  async with websockets.connect(conf.ws_url) as websocket:
    await websocket.send(json.dumps({ 'type': 'status', 'id' : id }))

async def execSearchQuery(q, client, page, time, lang):
  images = []
  errCountGen = errCount()
  while not images:
    try:
      response = await client.post(f'{conf.searx_url}/search', data={
        'category_images': 1,
        'q': q,
        'pageno': page,
        'time_range': time,
        'language': lang,
        'format': 'json',
      })
      result = response.json()
      images = result['results']
    except Exception as e:
      if next(errCountGen) == 4:
        logging.error(f'query "{q}, page "{page}" failed')
        return []
      logging.error(f'Запрос к searx провалился, errCount: {errCount}', exc_info=True)
      await asyncio.sleep(randrange(3,10))
  return images

async def main(query, pages, time, lang, timeout, sq_id):
  try:
    loggerInit('pars.log')
    sm = db.SearchQueryStatusManager()
    async with httpx.AsyncClient(verify=False, timeout=httpx.Timeout(timeout, connect=timeout, read=timeout, write=timeout, pool=timeout)) as client, db.async_session() as session:
      await session.commit()
      results_list = await asyncio.gather(*[execSearchQuery(query, client, i, time, lang) for i in range(1,pages)], return_exceptions=True)
      result = list(chain(*results_list))
      for i in result:
        session.add(db.SearchResult(id=str(uuid4()), search_query_id=sq_id, img_src=i['img_src'], thumb_src=i.get('thumbnail_src', None)))
      queryObjectCoroutine = await session.execute(db.select(db.SearchQuery).where(db.SearchQuery.id == sq_id))
      queryObject = queryObjectCoroutine.scalars().one()
      queryObject.status_id = sm.id.searched
      await session.commit()
      return result
  except Exception as e:
    logging.error(e, exc_info=True)
    async with db.async_session() as session:
      queryObjectCoroutine = await session.execute(db.select(db.SearchQuery).where(db.SearchQuery.id == sq_id))
      queryObject = queryObjectCoroutine.scalars().one()
      queryObject.status_id = sm.id.error
      await session.commit()
  finally:
    await notifyStatusChange(sq_id)
