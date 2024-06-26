import httpx

from typing import List, Optional

BASE_URL = "https://openlibrary.org"


class BookDto:
    def __init__(self, id:str, title: str, author_name: str, publish_year: int, tags: List[str], cover_link: str):
        self.id = id
        self.title = title
        self.author_name = author_name
        self.publish_year = publish_year
        self.tags = tags
        self.cover_link = cover_link

    @classmethod
    def from_list_dict(cls, data:dict):
        cover = data.get('cover_i')
        cover_link = ""
        if cover is not None:
            cover_link = 'https://covers.openlibrary.org/b/id/' + str(cover) + '-M.jpg'
        return cls(
            id = data.get("editions").get("docs")[0].get("key").split('/')[-1],
            title = data.get('title'),
            author_name = ", ".join(data.get('author_name', [''])) if isinstance(data.get('author_name'), list) and data.get('author_name') else '',
            publish_year = str(data.get('first_publish_year')),
            tags = data.get('subject', []),
            cover_link = cover_link
        )
    
    @classmethod
    def from_single_json(cls, data:dict):
        covers = data.get("covers")
        cover_link = ""
        if covers is not None and len(covers) != 0:
            cover_link = 'https://covers.openlibrary.org/b/id/' + str(covers[0]) + '-M.jpg'
        return cls(
            id = data.get("key").split('/')[-1],
            title = data.get("title"),
            author_name = data.get("authors_name"),
            publish_year = data.get("publish_date"),
            tags = data.get("subjects", []),
            cover_link = cover_link
        )


class Books:


    @staticmethod
    async def get_book_by_id(id:str):
        url = f"{BASE_URL}/books/{id}.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            authors = data.get("authors")
            authors_name = ""
            for author in authors:
                response_author = await client.get(BASE_URL+author.get("key")+".json")
                response_author.raise_for_status()
                authors_data = response_author.json()
                if authors_name != "":
                    authors_name += ", " 
                authors_name += authors_data.get("name")
            data["authors_name"] = authors_name

            works = data.get("works")
            if works is not None and len(works) != 0:
                response_tags = await client.get(BASE_URL+works[0].get("key")+".json")
                response_tags.raise_for_status()
                tags_data = response_tags.json()
                data["subjects"] = tags_data.get("subjects") if tags_data.get("subjects") else []
            
            return BookDto.from_single_json(data)


    @staticmethod
    async def search_books(name: str, author: str, tags: [str], page:int, size:int):
        url = f"{BASE_URL}/search.json"
        params = {}
        if name is not None:
            params['title'] = name
        if author is not None:
            params['author'] = author
        if tags is not None:
            params['subject'] = ",".join(tags)
        params['page'] = page
        params['limit'] = size
        params['fields'] = "key,title,author_name,first_publish_year,editions,cover_i, subject"
        async with httpx.AsyncClient() as client:
            print(params)
            response = await client.get(url, params = params)
            response.raise_for_status()
            data = response.json()
            books = [BookDto.from_list_dict(book) for book in data.get('docs', [])]
            total_size = data.get('num_found')
            result = {}
            result['total_size'] = total_size
            result['data'] = books
            return result

