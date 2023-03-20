import httpx
from uuid import uuid4
import asyncio
import db
from random import randrange
import os
import aiofiles
from base64 import b64decode
from random_user_agent.user_agent import UserAgent
import websockets
import json
from logger import logging, loggerInit
from config import common as conf
import tarfile

user_agent_rotator = UserAgent()

async def get_results(sq_id):
  async with db.async_session() as session:
    queryResultsCoroutine = await session.execute(db.select(db.SearchResult).where(db.SearchResult.search_query_id == sq_id))
    return queryResultsCoroutine.scalars().all()

async def notifyStatusChange(id):
  async with websockets.connect(conf.ws_url) as websocket:
    await websocket.send(json.dumps({ 'type': 'status', 'id' : id }))

def rmdir(dir):
  for file in os.listdir(dir):
    os.remove(os.path.join(dir, file))
  os.rmdir(dir)

async def get_img(client, outfile, results, index, link):
  if not link:
    logging.info(f'Попытка скачивания №{index} не была осуществлена - ссылка пустая.')
    results.append(False)
    return
  try:
    p = await client.get(link)
    await outfile.write(p.content)
    results.append(True)
    logging.info(f'Попытка скачивания №{index} успешна.')
    return
  except httpx.InvalidURL:
    await outfile.write(b64decode(link[22:]))
    results.append(True)
    logging.info(f'Попытка скачивания №{index} успешна.')
    return

async def download_image(data, index, count, results, destination):
  try:
    logging.info(f'Попытка скачивания №{index}. Всего попыток: {count}')
    filename = os.path.join(os.getcwd(), destination, f'{uuid4()}.jpg')
    headers = { 'user-agent': user_agent_rotator.get_random_user_agent() }
    async with httpx.AsyncClient(verify=False, timeout=httpx.Timeout(60, connect=60, read=60, write=60, pool=60), headers=headers) as client, aiofiles.open(filename,'wb') as outfile:
      try:
        await get_img(client, outfile, results, index, data.img_src)
      except Exception as e:
        logging.error(f'Попытка скачивания №{index} провалилась. Будет предпринята попытка скачать thumbnail. URL: {data.img_src}. THUMB_URL: {data.thumb_src}', exc_info=True)
        await asyncio.sleep(randrange(2,5))    
      try:
        await get_img(client, outfile, results, index, data.img_src)
      except Exception as e:
        results.append(False)
        logging.error(f'Попытка скачивания №{index} провалилась. URL: {data.img_src}. THUMB_URL: {data.thumb_src}', exc_info=True)
  except Exception as e:
    logging.error(e, exc_info=True)    

async def main(sq_id):
  try:
    loggerInit('download.log')
    sm = db.SearchQueryStatusManager()
    async with db.async_session() as session:
      if not os.path.exists(conf.img_dir):
        os.mkdir(conf.img_dir)

      destination = os.path.join(conf.img_dir, sq_id)

      if not os.path.exists(destination):
        os.mkdir(destination)

      if not os.path.exists(conf.archives_dir):
        os.mkdir(conf.archives_dir)

      results = []
      images = await get_results(sq_id)
      logging.info(f'Найдено результатов: {len(images)}')

      await asyncio.gather(*[download_image(img, i, len(images), results, destination) for i, img in enumerate(images)])

      logging.info(f'Всего попыток: {len(results)}. Успешно: {results.count(True)}. Завершено с ошибкой: {results.count(False)}')
      logging.info('Выполняется архивация файлов...')
      with tarfile.open(os.path.join(conf.archives_dir, f'{sq_id}.tgz'), 'w:gz') as tgz:
        for file in os.listdir(destination):
          tgz.add(os.path.join(destination, file))
      rmdir(destination)
      logging.info('Архивация завершена')
      
      queryObjectCoroutine = await session.execute(db.select(db.SearchQuery).where(db.SearchQuery.id == sq_id))
      queryObject = queryObjectCoroutine.scalars().one()
      queryObject.status_id = sm.id.archived
      await session.commit()

  except Exception as e:
    logging.error(e, exc_info=True)
    async with db.async_session() as session:
      queryObjectCoroutine = await session.execute(db.select(db.SearchQuery).where(db.SearchQuery.id == sq_id))
      queryObject = queryObjectCoroutine.scalars().one()
      queryObject.status_id = sm.id.error
      await session.commit()
  finally:
    await notifyStatusChange(sq_id)
