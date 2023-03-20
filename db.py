import json
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import relationship, DeclarativeBase, selectinload
from sqlalchemy import (
    event,
    Table,
    MetaData,
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    select,
    insert,
    update,
    delete,
    or_,
    and_,
    func,
    text,
    PrimaryKeyConstraint,
    ForeignKey
)

engine = create_async_engine("sqlite+aiosqlite:///./db.lite")
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
  pass

@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
  cursor = dbapi_connection.cursor()
  cursor.execute("PRAGMA foreign_keys=ON;")
  cursor.close()

class ModelsEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, SearchQuery):
      return {'id': obj.id, 'query_string': obj.query_string, 'datetime': obj.datetime, "status_id": obj.status_id, 'status': obj.status }
    if isinstance(obj, SearchResult):
      return {'id': obj.id, 'search_query_id': obj.search_query_id, 'img_src': obj.img_src, 'thumb_src': obj.thumb_src }
    if isinstance(obj, SearchQueryStatus):
      return {'id': obj.id, 'position': obj.position, 'description': obj.description }
    return json.JSONEncoder.default(self, obj)

class SearchQueryStatus(Base):
  __tablename__ = 'search_query_status'
  id = Column(String, primary_key=True, nullable=False)
  position = Column(Integer, nullable=False)
  description = Column(String, nullable=False)

class SearchQuery(Base):
  __tablename__ = 'search_query'
  id = Column(String, primary_key=True, nullable=False, sqlite_on_conflict_primary_key='REPLACE')
  query_string = Column(String, nullable=False)
  datetime = Column(String, nullable=False)
  status_id = Column(String, ForeignKey('search_query_status.id', ondelete='CASCADE'))
  status = relationship("SearchQueryStatus")

class SearchResult(Base):
  __tablename__ = 'search_result'
  id = Column(String, primary_key=True, nullable=False)
  search_query_id = Column(String, ForeignKey('search_query.id', ondelete='CASCADE'))
  img_src = Column(String, nullable=False)
  thumb_src = Column(String)

async def async_main():
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  await engine.dispose()

  async with async_session() as session:
    statusCountCoroutine = await session.execute(select(func.count("id")).select_from(SearchQueryStatus))
    if statusCountCoroutine.scalars().one() > 0:
      return
    
    sm = SearchQueryStatusManager()
    session.add_all([
      sm.obj.searching,
      sm.obj.searched,
      sm.obj.archiving,
      sm.obj.archived,
      sm.obj.error
    ])
    await session.commit()

class SearchQueryStatusManager:
  class Ids:
    def __init__(self):
      self.searching = '86a2f382-04ba-4552-b29e-b861d57f0903'
      self.searched = 'b48932c8-b36b-4bf8-a5a6-bc96bd13e9af'
      self.archiving = 'a8a16594-e506-4e9b-a0b0-b55ebc05bb69'
      self.archived = 'f02123ac-e487-499e-8e07-a8b8846092b7'
      self.error = '8c5cafc5-82a4-42d4-9f4b-d65321a16737'
      
  class Objects:
    def __init__(self):
      self.searching = SearchQueryStatus(id='86a2f382-04ba-4552-b29e-b861d57f0903', position=0, description='Поиск...')
      self.searched = SearchQueryStatus(id='b48932c8-b36b-4bf8-a5a6-bc96bd13e9af', position=1, description='Поиск выполнен') 
      self.archiving = SearchQueryStatus(id='a8a16594-e506-4e9b-a0b0-b55ebc05bb69', position=2, description='Скачивание...') 
      self.archived = SearchQueryStatus(id='f02123ac-e487-499e-8e07-a8b8846092b7', position=3, description='Скачивание выполнено')
      self.error = SearchQueryStatus(id='8c5cafc5-82a4-42d4-9f4b-d65321a16737', position=5, description='Завершено с ошибкой')

  def __init__(self):
    self.id = self.Ids()
    self.obj = self.Objects()

asyncio.run(async_main())