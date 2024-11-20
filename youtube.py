__version__ = (1, 3, 0)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2024
#           https://t.me/apcecoc
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://example.com/youtube_icon.png
# meta banner: https://example.com/youtube_banner.jpg
# meta developer: @apcecoc
# scope: hikka_only
# scope: hikka_min 1.2.10

import aiohttp
import os
from telethon.tl.types import Message
from .. import loader, utils

@loader.tds
class YouTubeDownloaderMod(loader.Module):
    """Working with YouTube: Search, Download Video, Get Channel Info"""

    strings = {
        "name": "YouTubeDownloader",
        "processing": "🔄 <b>Fetching YouTube data...</b>",
        "invalid_query": "❌ <b>Invalid query provided.</b>",
        "error": "❌ <b>Error occurred while processing your request.</b>",
        "results_found": "🔎 <b>Found results for:</b> {query}",
        "no_results": "❌ <b>No results found for '{query}'.</b>",
        "video_success": "🎥 <b>Video downloaded successfully:</b>",
        "audio_success": "🎵 <b>Audio downloaded successfully:</b>",
    }

    strings_ru = {
        "processing": "🔄 <b>Загружаю данные с YouTube...</b>",
        "invalid_query": "❌ <b>Неверный запрос.</b>",
        "error": "❌ <b>Произошла ошибка при обработке запроса.</b>",
        "results_found": "🔎 <b>Найдено результаты для:</b> {query}",
        "no_results": "❌ <b>Ничего не найдено по запросу '{query}'.</b>",
        "video_success": "🎥 <b>Видео успешно скачано:</b>",
        "audio_success": "🎵 <b>Аудио успешно скачано:</b>",
        "_cls_doc": "Работа с YouTube: поиск, скачивание видео",
    }

    @loader.command(ru_doc="<Запрос> Найти видео на YouTube")
    async def ytsearch(self, message: Message):
        """<Query> Search for YouTube videos"""
        await self._search_youtube(message)

    @loader.command(ru_doc="<Ссылка на видео> Скачать видео с YouTube")
    async def ytvideo(self, message: Message):
        """<YouTube URL> Download YouTube video"""
        await self._download_video(message)

    @loader.command(ru_doc="<Ссылка на видео> Скачать аудио с YouTube")
    async def ytaudio(self, message: Message):
        """<YouTube URL> Download YouTube audio"""
        await self._download_audio(message)

    async def _search_youtube(self, message: Message):
        query = utils.get_args_raw(message)
        if not query:
            await utils.answer(message, self.strings("invalid_query"))
            return

        await utils.answer(message, self.strings("processing"))

        api_url = f"https://api.paxsenix.biz.id/yt/search?q={query}"
        headers = {"accept": "*/*"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()

                        if not data.get("ok", False):
                            await utils.answer(message, self.strings("error"))
                            return

                        results = data.get("results", [])
                        if results:
                            result_text = self.strings("results_found").format(query=query)
                            for idx, result in enumerate(results, 1):
                                result_text += f"\n\n{idx}. <b>{result['title']}</b>"
                                result_text += f"\n🔗 <a href='{result['url']}'>Ссылка на видео</a>"
                                result_text += f"\n👤 Канал: {result['channelName']}"
                                result_text += f"\n👀 Просмотров: {result['viewCount']}"
                                result_text += f"\n📷 Миниатюра: {result['thumbnails'][0]['url']}"
                            
                            await utils.answer(message, result_text)
                        else:
                            await utils.answer(message, self.strings("no_results").format(query=query))
                    else:
                        await utils.answer(message, self.strings("error"))
        except Exception as e:
            await utils.answer(message, self.strings("error"))
            raise e

    async def _download_video(self, message: Message):
        url = utils.get_args_raw(message)
        if not url or not url.startswith("http"):
            await utils.answer(message, self.strings("invalid_query"))
            return

        await utils.answer(message, self.strings("processing"))

        api_url = f"https://api.paxsenix.biz.id/yt/savetube?url={url}&type=video&quality=6"
        headers = {"accept": "*/*"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()

                        if not data.get("ok", False):
                            await utils.answer(message, self.strings("error"))
                            return

                        download_url = data.get("link")
                        if download_url:
                            async with session.get(download_url) as file_resp:
                                if file_resp.status == 200:
                                    file_name = download_url.split("/")[-1]
                                    file_path = f"/tmp/{file_name}"
                                    with open(file_path, "wb") as file:
                                        file.write(await file_resp.read())
                                    
                                    await message.client.send_file(
                                        message.peer_id,
                                        file_path,
                                        caption=self.strings("video_success"),
                                    )

                                    # Удаление файла после отправки
                                    if os.path.exists(file_path):
                                        os.remove(file_path)

                                    await message.delete()
                                else:
                                    await utils.answer(message, self.strings("error"))
                        else:
                            await utils.answer(message, self.strings("error"))
                    else:
                        await utils.answer(message, self.strings("error"))
        except Exception as e:
            await utils.answer(message, self.strings("error"))
            raise e

    async def _download_audio(self, message: Message):
        url = utils.get_args_raw(message)
        if not url or not url.startswith("http"):
            await utils.answer(message, self.strings("invalid_query"))
            return

        await utils.answer(message, self.strings("processing"))

        api_url = f"https://api.paxsenix.biz.id/yt/savetube?url={url}&type=audio&quality=4"
        headers = {"accept": "*/*"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()

                        if not data.get("ok", False):
                            await utils.answer(message, self.strings("error"))
                            return

                        download_url = data.get("link")
                        if download_url:
                            async with session.get(download_url) as file_resp:
                                if file_resp.status == 200:
                                    file_name = download_url.split("/")[-1]
                                    file_path = f"/tmp/{file_name}"
                                    with open(file_path, "wb") as file:
                                        file.write(await file_resp.read())
                                    
                                    await message.client.send_file(
                                        message.peer_id,
                                        file_path,
                                        caption=self.strings("audio_success"),
                                    )

                                    # Удаление файла после отправки
                                    if os.path.exists(file_path):
                                        os.remove(file_path)

                                    await message.delete()
                                else:
                                    await utils.answer(message, self.strings("error"))
                        else:
                            await utils.answer(message, self.strings("error"))
                    else:
                        await utils.answer(message, self.strings("error"))
        except Exception as e:
            await utils.answer(message, self.strings("error"))
            raise e
