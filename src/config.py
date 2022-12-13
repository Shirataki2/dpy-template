from dataclasses import dataclass, field
import discord
from serde import serde
from serde.toml import from_toml

@serde
@dataclass
class BotPrivilegedIntentConfig:
    all: bool = field(default=False)

    # If all is True, these are ignored
    presence: bool = field(default=False)
    members: bool = field(default=False)
    messages: bool = field(default=False)

    def get_intents(self) -> discord.Intents:
        intents = discord.Intents.default()
        if self.all:
            intents.presences = True
            intents.members = True
            intents.message_content = True
        else:
            intents.presences = self.presence
            intents.members = self.members
            intents.message_content = self.messages
        return intents

@serde
@dataclass
class BotConfig:
    token: str
    prefix: str
    development_server_id: int
    privileged_intents: BotPrivilegedIntentConfig = field(default_factory=BotPrivilegedIntentConfig)

@serde
@dataclass
class AppConfig:
    bot: BotConfig
    dev: bool = field(default=False)

    @staticmethod
    def load(conf_path: str = "conf.toml") -> "AppConfig":
        """Load the config from a file"""
        with open(conf_path, "r") as f:
            return from_toml(AppConfig, f.read())
