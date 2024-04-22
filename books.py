import httpx
import requests
from typing import List, Optional


class BookDto:
    def __init__(self, title: str, author_name: str, publish_year: int, tags: List[str], cover_link: str):
        self.title = title
        self.author_name = author_name
        self.publish_year = publish_year
        self.tags = tags
        self.cover_link = cover_link

    @classmethod
    def from_dict(cls, data:dict):
        return cls(
            title = data.get('title'),
            author_name = data.get('author_name', [''])[0] if isinstance(data.get('author_name'), list) and data.get('author_name') else '',
            publish_year = data.get('first_publish_year'),
            tags = data.get('subject', []),
            cover_link = 'https://covers.openlibrary.org/b/id/' + str(data.get('cover_i')) + '-M.jpg'
        )

class Books:
    BASE_URL = "https://openlibrary.org"



    @staticmethod
    async def search_books(name: str, author: str, tags: [str], publish_year: int, page:int, size:int):
        url = f"{Books.BASE_URL}/search.json"
        params = {}
        if name is not None:
            params['title'] = name
        if author is not None:
            params['author'] = author
        if tags is not None:
            params['subject'] = ",".join(tags)
        if publish_year is not None:
            params['publishYear'] = publish_year
        params['page'] = page
        params['limit'] = size
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params = params)
            response.raise_for_status()
            data = response.json()
            books = [BookDto.from_dict(book) for book in data.get('docs', [])]
            total_size = data.get('num_found')
            result = {}
            result['total_size'] = total_size
            result['data'] = books
            return result

