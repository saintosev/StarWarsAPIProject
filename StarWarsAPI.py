import aiohttp
import asyncio
from datetime import datetime
from typing import Dict, Set, Optional


class SavingCharactersToFile:
    """Saving the names of the desired characters to a text file"""

    base_url = "https://swapi.dev/api/"

    async def fetch_data(self, url: str) -> Optional[Dict]:
        """Asynchronous sending of a GET request and receiving data in JSON format"""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Error: status {response.status} for the request {url}")
                        return None
        except Exception as e:
            print(f"Exception when requesting to {url}: {e}")
            return None

    async def get_character(self, character_id: int) -> Optional[Dict]:
        """Getting character data by id"""

        character_url = f"{self.base_url}people/{character_id}/"
        print(character_url)
        character_data = await self.fetch_data(character_url)

        if character_data:
            print(f"Success! The found character is {character_data['name']}.")
            return character_data
        else:
            print(f"Error! The character with id {character_id} doesn't exist.")
            return None

    async def get_characters_from_movie(self, json: Dict) -> Set[str]:
        """Getting the names of characters from films in which a given character participated"""

        characters_names = set()

        if 'films' in json:
            tasks = [self.fetch_data(film_url) for film_url in json['films']]
            films_data = await asyncio.gather(*tasks)

            for film_data in films_data:
                if film_data:
                    characters_tasks = [self.fetch_data(character_url) for character_url in film_data['characters']]
                    characters_data = await asyncio.gather(*characters_tasks)

                    for character_data in characters_data:
                        if character_data:
                            characters_names.add(character_data['name'])

            characters_names_str = ', '.join(characters_names)
            print(f"Along with {json['name']}, the following characters appeared on the screen: {characters_names_str}.")
        else:
            print("It is impossible to get a list of movies.")

        return characters_names

    @staticmethod
    def save_names_in_file(names_set: Set[str]):
        """Writing the names of characters from the set to a text file"""

        if names_set:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'characters_{timestamp}.txt'

            with open(filename, 'w', encoding='utf-8') as file:
                for name in names_set:
                    file.write(f"{name}\n")

            print(f"The names of all the characters are saved in the {filename}")
        else:
            print("There are no names to save to the file.")


async def main():
    start = SavingCharactersToFile()
    darth_vader_json = await start.get_character(4)
    if darth_vader_json:
        starwars_names = await start.get_characters_from_movie(darth_vader_json)
        start.save_names_in_file(starwars_names)

asyncio.run(main())
