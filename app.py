from flask import Flask, render_template, request
import db
import json
from uuid import uuid4
from tasks.search import main as search
from tasks.download import main as download
import os
from rq import Queue
from redis import Redis
from logger import logging, loggerInit
from config import common as conf
from datetime import datetime
from asgiref.wsgi import WsgiToAsgi
from hypercorn.config import Config
from hypercorn.asyncio import serve
import asyncio
from math import ceil

loggerInit('app.log')

app = Flask(__name__)

def default_error():
  return {'error': True}, 500

def default_response():
  return {'status': 'ok'}

def to_json(obj):
  return json.dumps(obj, ensure_ascii=False, cls=db.ModelsEncoder)

@app.get("/")
async def default_route():
  return render_template('index.html')

@app.get('/config')
async def send_config():
  try:
    return to_json(conf.dict_config)
  except Exception as e:
    logging.error(e, exc_info=True)
    return default_error()

@app.post("/search")
async def exec_search():
  try:
    sq_id = str(uuid4())

    sm = db.SearchQueryStatusManager()
    async with db.async_session() as session:
      session.add(db.SearchQuery(id=sq_id, query_string=request.json['query'], status_id = sm.id.searching, datetime=datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))
      await session.commit()

    with Redis(host=conf.redis_host, port=conf.redis_port) as redis_conn:
      queue = Queue(connection=redis_conn)
      queue.enqueue(search, request.json['query'], request.json['pagesCount'], request.json['time'], request.json['language'], request.json['timeout'], sq_id, job_timeout=conf.search_task_timeout)
      logging.info(f'Поиск по запросу {request.json["query"]}')
    return default_response()
  except Exception as e:
    logging.error(e, exc_info=True)
    return default_error()

@app.post("/archives")
async def make_archive():
  try:
    sm = db.SearchQueryStatusManager()
    async with db.async_session() as session:
      queryObjectCoroutine = await session.execute(db.select(db.SearchQuery).where(db.SearchQuery.id == request.json['qid']))
      queryObject = queryObjectCoroutine.scalars().one()
      queryObject.status_id = sm.id.archiving
      await session.commit()

    with Redis(host=conf.redis_host, port=conf.redis_port) as redis_conn:
      queue = Queue(connection=redis_conn)
      queue.enqueue(download, request.json['qid'], job_timeout=conf.download_task_timeout)
    return default_response()
  except Exception as e:
    logging.error(e, exc_info=True)
    return default_error()

@app.get('/history/pages')
async def historyPagesCount():
  try:
    async with db.async_session() as session:
      historyItemsCountCoroutine = await session.execute(db.select(db.func.count("id")).select_from(db.SearchQuery))
      historyItemsCount = historyItemsCountCoroutine.scalars().one()
      return to_json({ 'pagesCount': ceil(historyItemsCount / conf.history_items_per_page), 'itemsCount': historyItemsCount })
  except Exception as e:
    logging.error(e, exc_info=True)
    return default_error()

@app.get('/history/<int:pagenum>')
async def all_history(pagenum):
  try:
    async with db.async_session() as session:
      queryHistoryCoroutine = await session.execute(db.select(db.SearchQuery).limit(conf.history_items_per_page).offset(conf.history_items_per_page * pagenum).options(db.selectinload(db.SearchQuery.status)))
      queryHistory = queryHistoryCoroutine.scalars().all()
      return to_json(queryHistory)
  except Exception as e:
    logging.error(e, exc_info=True)
    return default_error()

@app.get('/history/<string:qid>')
async def history_item(qid):
  try:
    async with db.async_session() as session:
      queryHistoryCoroutine = await session.execute(db.select(db.SearchQuery).where(db.SearchQuery.id == qid).options(db.selectinload(db.SearchQuery.status)))
      queryHistory = queryHistoryCoroutine.scalars().one()
      return to_json(queryHistory)
  except Exception as e:
    logging.error(e, exc_info=True)
    return default_error()

@app.delete('/history/<qid>')
async def delete_history_item(qid):
  try:
    async with db.async_session() as session:
      await session.execute(db.delete(db.SearchQuery).where(db.SearchQuery.id == qid))
      await session.commit()
      try:
        os.remove(os.path.join(os.getcwd(), 'static', 'archives', f'{qid}.tgz'))
      except FileNotFoundError as e:
        logging.info(f'archive {qid}.tgz does not exists - skipping')
      return default_response()
  except Exception as e:
    logging.error(e, exc_info=True)
    return default_error()

@app.get('/results/<string:qid>/<int:pagenum>')
async def get_results(qid, pagenum):
  try:
    async with db.async_session() as session:
      queryResultsCoroutine = await session.execute(db.select(db.SearchResult).where(db.SearchResult.search_query_id == qid).limit(conf.results_per_page).offset(conf.results_per_page * pagenum))
      queryResults = queryResultsCoroutine.scalars().all()
      return to_json(queryResults)
  except Exception as e:
    logging.error(e, exc_info=True)
    return default_error()
  
@app.get('/results/<qid>/pages')
async def resultsPagesCount(qid):
  try:
    async with db.async_session() as session:
      resultsCountCoroutine = await session.execute(db.select(db.func.count("id")).select_from(db.select(db.SearchResult).where(db.SearchResult.search_query_id == qid)))
      resultsCount = resultsCountCoroutine.scalars().one()
      return to_json({ 'pagesCount': ceil(resultsCount / conf.results_per_page), 'resultsCount': resultsCount })
  except Exception as e:
    logging.error(e, exc_info=True)
    return default_error()


async def main():
    await serve(WsgiToAsgi(app), Config().from_pyfile('config/common.py'))

if __name__ == '__main__':
  asyncio.run(main())