__version__ = (1, 3, 1)

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

import asyncio
import aiohttp
import os
from telethon.tl.types import Message
from .. import loader, utils

@loader.tds
class YouTubeDownloaderMod(loader.Module):
    """Working with YouTube: Search and Download Audio"""

    strings = {
        "name": "YouTubeDownloader",
        "processing": "🔄 <b>Processing your request...</b>",
        "invalid_query": "❌ <b>Invalid query provided.</b>",
        "error": "❌ <b>Error occurred while processing your request.</b>",
        "results_found": "🔎 <b>Found results for:</b> {query}",
        "no_results": "❌ <b>No results found for '{query}'.</b>",
        "audio_success": "🎵 <b>Audio downloaded successfully:</b>",
    }

    strings_ru = {
        "processing": "🔄 <b>Обрабатываю ваш запрос...</b>",
        "invalid_query": "❌ <b>Неверный запрос.</b>",
        "error": "❌ <b>Произошла ошибка при обработке запроса.</b>",
        "results_found": "🔎 <b>Найдено результаты для:</b> {query}",
        "no_results": "❌ <b>Ничего не найдено по запросу '{query}'.</b>",
        "audio_success": "🎵 <b>Аудио успешно скачано:</b>",
        "_cls_doc": "Работа с YouTube: поиск и скачивание аудио",
    }

    @loader.command(ru_doc="<Ссылка на YouTube> Скачать видео MP4 из другого источника")
    async def ytvideo(self, message: Message):
        """<YouTube URL> Скачать MP4 файл из раздела other"""
        url = utils.get_args_raw(message)
        if not url or not url.startswith("http"):
            await utils.answer(message, self.strings("invalid_query"))
            return

        await utils.answer(message, self.strings("processing"))

        api_url = f"https://api.paxsenix.biz.id/yt/yttomp4?url={url}"
        headers = {"accept": "*/*"}

        max_retries = 3  # Максимальное количество попыток
        retries = 0

        while retries < max_retries:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url, headers=headers) as resp:
                        if resp.status != 200:
                            raise Exception(f"API request failed with status {resp.status}")

                        data = await resp.json()
                        if not data.get("ok", False) or "other" not in data:
                            await utils.answer(message, self.strings("error"))
                            return

                        # Берём первый MP4 файл из раздела 'other'
                        video_url = data["other"][0]["url"]
                        video_name = data["other"][0]["name"]
                        video_size = data["other"][0]["size"]

                        # Скачиваем видео
                        async with session.get(video_url) as file_resp:
                            if file_resp.status != 200:
                                await utils.answer(message, "❌ Не удалось скачать видео.")
                                return

                            file_path = f"/tmp/{video_name.replace(' ', '_')}.mp4"
                            with open(file_path, "wb") as file:
                                file.write(await file_resp.read())

                            # Отправляем файл в чат
                            await message.client.send_file(
                                message.peer_id,
                                file_path,
                                caption=(
                                    f"🎬 Видео: <b>{data['title']}</b>\n"
                                    f"🕒 Продолжительность: {data['duration']}\n"
                                    f"📂 Размер: {video_size}\n"
                                    f"📥 Качество: {video_name}"
                                ),
                            )

                            # Удаляем файл после отправки
                            if os.path.exists(file_path):
                                os.remove(file_path)

                            await message.delete()
                            return  # Успех, выходим

            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    await utils.answer(message, f"❌ Произошла ошибка: {str(e)}")
                    return
                await asyncio.sleep(3)  # Пауза перед повторной попыткой

            
    @loader.command(ru_doc="<Запрос> Найти видео на YouTube")
    async def ytsearch(self, message: Message):
        """<Query> Search for YouTube videos"""
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

    @loader.command(ru_doc="<Ссылка на YouTube> Скачать MP3")
    async def ytaudio(self, message: Message):
        """<YouTube URL> Download MP3 from YouTube"""
        url = utils.get_args_raw(message)
        if not url or not url.startswith("http"):
            await utils.answer(message, self.strings("invalid_query"))
            return

        await utils.answer(message, self.strings("processing"))

        api_url = f"https://api.paxsenix.biz.id/yt/ytconvert?url={url}"
        headers = {"accept": "*/*"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()

                        if not data.get("ok", False) or "url" not in data:
                            await utils.answer(message, self.strings("error"))
                            return

                        download_url = data["url"]

                        async with session.get(download_url) as file_resp:
                            if file_resp.status == 200:
                                file_name = download_url.split("/")[-1].split("?")[0]
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
        except Exception as e:
            await utils.answer(message, self.strings("error"))
            raise e
