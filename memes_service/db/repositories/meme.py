from functools import lru_cache

from db.repositories.base import BaseRepository
from db.models.meme import Meme
from schemas.meme import CRUDMeme



class MemeRepository(BaseRepository[Meme, CRUDMeme, CRUDMeme]):
    pass

@lru_cache
def get_meme_rep() -> MemeRepository:
    return MemeRepository(Meme)