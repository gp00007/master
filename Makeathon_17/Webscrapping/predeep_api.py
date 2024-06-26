import random
import time
from typing import Any, Optional, Literal, List
import requests



_SERPER_URL = 'https://google.serper.dev'
NO_RESULT_MSG = 'No good Google Search result was found'


class SerperAPI:
    def __init__(
        self,
        serper_api_key: str,
        gl: str = 'us',
        hl: str = 'en',
        k: int = 1,
        tbs: Optional[str] = None,
        search_type: Literal['news', 'search', 'places', 'images'] = 'search',
    ):
        self.serper_api_key = serper_api_key
        self.gl = gl
        self.hl = hl
        self.k = k
        self.tbs = tbs
        self.search_type = search_type
        self.result_key_for_type = {
            'news': 'news',
            'places': 'places',
            'images': 'images',
            'search': 'organic',
        }

    def run(self, query: str, **kwargs: Any) -> str:
        """Run query through GoogleSearch and parse result."""

        assert self.serper_api_key, 'Missing serper_api_key.'
        results = self._google_serper_api_results(
            query,
            gl=self.gl,
            hl=self.hl,
            num=self.k,
            tbs=self.tbs,
            search_type=self.search_type,
            **kwargs,
        )

        return self._parse_results(results)

    def _google_serper_api_results(
        self,
        search_term: str,
        search_type: str = 'search',
        max_retries: int = 20,
        **kwargs: Any,
        ) -> dict[Any, Any]:

        """Run query through Google Serper."""
        headers = {
            'X-API-KEY': self.serper_api_key or '',
            'Content-Type': 'application/json',
        }
        params = {
            'q': search_term,
            **{key: value for key, value in kwargs.items() if value is not None},
        }
        response, num_fails, sleep_time = None, 0, 0

        while not response and num_fails < max_retries:
            try:
                response = requests.post(
                    f'{_SERPER_URL}/{search_type}', headers=headers, json=params, verify=False
                )

                response.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                print ("Http Error:",errh)
                response = None
            except requests.exceptions.ConnectionError as errc:
                print ("Error Connecting:",errc)
                response = None
            except requests.exceptions.Timeout as errt:
                print ("Timeout Error:",errt)
                response = None
            except requests.exceptions.RequestException as err:
                print ("Something went wrong",err)
                response = None
            finally:
                num_fails += 1
                sleep_time = min(sleep_time * 2, 600)
                sleep_time = random.uniform(1, 10) if not sleep_time else sleep_time
                time.sleep(sleep_time)

        if not response:
            raise ValueError('Failed to get result from Google Serper API')

        search_results = response.json()

        return search_results

    def _parse_snippets(self, results: dict[Any, Any]) -> list[str]:
        """Parse results."""
        snippets = []
        link= None

        if results.get('answerBox'):
            answer_box = results.get('answerBox', {})
            answer = answer_box.get('answer')
            snippet = answer_box.get('snippet')
            snippet_highlighted = answer_box.get('snippetHighlighted')

            if answer and isinstance(answer, str):
                snippets.append(answer)
            if snippet and isinstance(snippet, str):
                snippets.append(snippet.replace('\n', ' '))
            if snippet_highlighted:
                snippets.append(snippet_highlighted)

        if results.get('knowledgeGraph'):
            kg = results.get('knowledgeGraph', {})
            title = kg.get('title')
            entity_type = kg.get('type')
            description = kg.get('description')

            if entity_type:
                snippets.append(f'{title}: {entity_type}.')

            if description:
                snippets.append(description)

            for attribute, value in kg.get('attributes', {}).items():
                snippets.append(f'{title} {attribute}: {value}.')

        result_key = self.result_key_for_type[self.search_type]

        if result_key in results:

            for result in results[result_key][:self.k]:
                if 'snippet' in result:
                    link = result.get('link', '')
                    snippets.append(result['snippet'])

            for attribute, value in result.get('attributes', {}).items():
                snippets.append(f'{attribute}: {value}.')

        if not snippets:
            return [NO_RESULT_MSG]

        return snippets, link

    def _parse_results(self, results: dict[Any, Any]):
        return self._parse_snippets(results)

serper = SerperAPI(serper_api_key="a55375ff1596c1d9b24880c1c5a07b3026d8cf6a")

# run the input text through the serper API
output,link = serper.run("what is the price of dell XPS 360 laptop in Amazon India ?")

print(output)
print(link)