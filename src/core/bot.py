import discord
from discord.ext import commands
import os
import asyncio
from glob import glob
from src.core.logger import get_logger
from src.config import AppConfig

logger = get_logger(__name__)

class Bot(commands.Bot):
    conf: AppConfig
    dev_server_id: discord.Object

    def __init__(
        self,
        config_path = "conf.toml",
        *args, **kwargs
    ):
        self.conf = AppConfig.load(config_path)

        logger.info(f"Loaded config from {config_path}")
        logger.debug(f"Config: {self.conf}")
        command_prefix = self.conf.bot.prefix
        intents = self.conf.bot.privileged_intents.get_intents()
        self.dev_server_id = discord.Object(id=self.conf.bot.development_server_id)

        super().__init__(command_prefix=command_prefix, intents=intents, *args, **kwargs)

    async def setup_hook(self) -> None:
        if self.conf.dev:
            await self.tree.sync(guild=self.dev_server_id)
        else:
            await self.tree.sync()

    async def load_all_cogs(self, /, loop=None):
        if loop is None:
            loop = self.loop
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        cogs = glob(os.path.join(cur_dir, "..", "cogs", "*.py"))
        futs = []
        for cog in cogs:
            cog_name = os.path.basename(os.path.splitext(cog)[0])
            if cog_name[:2] == "__":
                continue
            module_name = f"src.cogs.{cog_name}"
            async def load_hook(module_name):
                try:
                    await self.load_extension(module_name)
                    logger.info(f"Cog loaded: {module_name}")
                except Exception as e:
                    logger.error(f"Error loading {module_name}: {e}")
            futs.append(load_hook(module_name))
        await asyncio.gather(*futs)

    async def on_ready(self):
        user = self.user
        if user:
            logger.info(f"Logged in as {user.name}#{user.discriminator}")
            logger.info(f"ID: {user.id}")
        logger.info(f"Prefix: {self.command_prefix}")
        logger.info(f"Intent bits: {self.intents.value}")
        logger.info(f"Development mode: {self.conf.dev}")
        logger.info(f"Development server ID: {self.dev_server_id.id}")
        if self.conf.dev:
            await self.change_presence(activity=discord.Game(name="Development mode"))

    async def run(self, *args, **kwargs):
        await self.load_all_cogs()
        try:
            await super().start(self.conf.bot.token, *args, **kwargs)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt")
        finally:
            await self.close()

    async def close(self):
        loop = self.loop
        for task in asyncio.all_tasks(loop):
            task.cancel()
            logger.info(f"Task canceled: {task}")
        logger.info("Closing bot")
