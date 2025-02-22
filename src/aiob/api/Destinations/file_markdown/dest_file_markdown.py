from __future__ import annotations

import dataclasses
import os
import pathlib

import aiofiles
import frontmatter

from aiob.api.model import Data, DestinationBase, data_metas
from aiob.api.plugin_loader import destination_class


@destination_class
class Destination(DestinationBase):
    name = "dest_file_markdown"

    @classmethod
    def get_path(cls, data: Data) -> pathlib.Path:
        path = pathlib.Path(Destination.get_conf(
            "path", os.getcwd() + "/") + data.title + ".md")
        return path

    @classmethod
    async def add(cls, data: Data) -> None:
        path = cls.get_path(data)
        path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(path, "w+") as f:
            await f.write(cls._parse(data))

    @classmethod
    async def delete(cls, data: Data) -> None:
        path = cls.get_path(data)
        os.remove(path)

    @classmethod
    async def change(cls, data: Data) -> None:
        path = cls.get_path(data)
        path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(path, "w+") as f:
            await f.write(cls._parse(data))

    @classmethod
    def _parse(cls, data: Data) -> str:
        if not cls.get_conf("frontmatter", True):
            return data.content

        post = frontmatter.Post(data.content)

        for x in dataclasses.fields(data):
            if x.name in data_metas and getattr(data, x.name) != x.default:
                post.metadata[x.name] = getattr(data, x.name)

        del post.metadata["title"]
        if post.metadata["tags"] == []:
            del post.metadata["tags"]
        if len(post.metadata["extras"].keys()) == 0:
            del post.metadata["extras"]

        if len(post.metadata.keys()) > 0:
            return frontmatter.dumps(post)
        else:
            return data.content
