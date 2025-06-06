# RECREATING THE WHOLE CONFIG SYSTEM FROM SCRATCH TO BE MORE MODULAR

import logging
import os
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from utils.autocomplete import (
    autocomplete_color,
    autocomplete_dice_modes,
    autocomplete_lang,
)
from utils.configmanager import gconfig, lang, uconfig
from utils.dices import dices
from utils.timeconverter import TimeConverter

__PRIORITY__ = 10
logger = logging.getLogger("guildconfig")

class GuildConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.default_permissions(administrator=True)
    class configure_automations(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "automations"
            self.description = "Automations for the server"

        @app_commands.command(name="automessage", description="Set an auto message, interval, and channel")  # noqa: E501
        async def set_message(self, interaction: discord.Interaction, message: str, interval: int, channel: discord.TextChannel, embed: bool = False,enable:bool=True):  # noqa: E501
            if enable:
                guild_id = str(interaction.guild_id)
                channel_id = str(channel.id)
                timestamp = (datetime.now() + timedelta(minutes=interval)).timestamp()  # noqa: E501

                gconfig.set(guild_id,f"automessages-{channel_id}", "embed", embed)
                gconfig.set(guild_id,f"automessages-{channel_id}", "message", message)  # noqa: E501
                gconfig.set(guild_id,f"automessages-{channel_id}", "interval", interval)  # noqa: E501
                gconfig.set(guild_id,f"automessages-{channel_id}", "timestamp", timestamp)  # noqa: E501

                await interaction.response.send_message(f"Auto message set to '{message}' with interval '{interval}' minutes in channel {channel.mention}",ephemeral=True)  # noqa: E501
            else:
                guild_id = str(interaction.guild_id)
                channel_id = str(channel.id)
                gconfig.delete(guild_id,f"automessages-{channel_id}")
                await interaction.response.send_message("Auto message deleted",ephemeral=True)  # noqa: E501

    @app_commands.default_permissions(administrator=True)
    class configure_sec(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "security"
            self.description = "Security configurations"

        @app_commands.command(
            name="anti-invite",
            description="No invites in the halls")
        async def anti_invites(self,interaction: discord.Interaction,value: bool):
            try:
                gconfig.set(
                    id=interaction.guild_id,
                    title="SECURITY",
                    key="anti-invite",
                    value=value,
                )
                await interaction.response.send_message(
                    content=f"Set value {str(value)}",
                    ephemeral=True,
                )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Failed configuring anti-invites: {e}",
                )
        @app_commands.command(
            name="anti-alts",
            description="No alts on the server allowed!",
        )
        async def antialts(self,interaction:discord.Interaction,enabled:bool,time:app_commands.Transform[str, TimeConverter]=None):  # noqa: E501
            try:
                gconfig.set(interaction.guild.id,"SECURITY","antialts-enabled",enabled)
                gconfig.set(interaction.guild.id,"SECURITY","antialts-time",time)
            except Exception as e:
                logger.info(f"There was error in settings {e}")

        @app_commands.command(
            name="anti-links",
            description="No links in the halls")
        async def anti_links(self,interaction: discord.Interaction,value: bool):
            try:
                gconfig.set(
                    id=interaction.guild_id,
                    title="SECURITY",
                    key="anti-links",
                    value=value,
                )
                await interaction.response.send_message(
                    content=f"Set value {str(value)}",
                    ephemeral=True,
                )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Failed configuring anti-links: {e}",
                )

    @app_commands.default_permissions(administrator=True)
    class configure_appear(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "appearance"
            self.description = "Appearance of bot on your server"

        @app_commands.command(
            name="color",
            description="Changes default color of embeds.")
        @app_commands.describe(color="The color to set")
        @app_commands.autocomplete(color=autocomplete_color)
        async def config_color_guild(
            self,
            interaction: discord.Interaction,
            color: str,
        ):
            try:
                gconfig.set(
                    id=interaction.guild_id,
                    title="APPEARANCE",
                    key="color",
                    value=color,
                )
                await interaction.response.send_message(
                    content=f"Set value {str(color)}",
                    ephemeral=True,
                )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Exception happened: {e}",
                    ephemeral=True,
                )

        @app_commands.command(
            name="language",
            description="Set server default language")
        @app_commands.describe(language="Language to set")
        @app_commands.autocomplete(language=autocomplete_lang)
        async def config_lang_guild(
            self,
            interaction: discord.Interaction,
            language: str,
        ):
            try:
                gconfig.set(
                    id=interaction.guild_id,
                    title="APPEARANCE",
                    key="language",
                    value=language,
                )
                await interaction.response.send_message(
                    content=f"Set value {str(language)}",
                    ephemeral=True,
                )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Exception happened: {e}",
                    ephemeral=True,
                )
    @app_commands.default_permissions(
        administrator=True,
    )
    class configure_fun(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "fun"
            self.description = "Configure fun options"

        @app_commands.command(name="dice",description="Default dice mode")
        @app_commands.autocomplete(mode=autocomplete_dice_modes)
        async def conf_fun_dice(self, interaction:discord.Interaction,mode:str):
            if mode is None or mode == "" and mode not in dices.keys():  # noqa: SIM118
                mode = "classic (6 sides)"
            gconfig.set(interaction.guild.id,"FUN","def_dice",mode)
            await interaction.response.send_message(content="Value set.")

    @app_commands.default_permissions(
        administrator=True,
    )
    class configure_ticketing(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "ticketing"
            self.description = "Configure ticketing options"

        @app_commands.command(
            name="reviews",
            description="Review system",
        )
        async def conf_ticketing_reviews(
            self,
            interaction: discord.Interaction,
            channel: discord.TextChannel = None,
            value: bool = None,
        ):
            try:
                lang_key = uconfig.get(
                    id=interaction.user.id,
                    title="Appearance",
                    key="language",
                )
                response_template = lang.get(
                    id=lang_key,
                    title="Responds",
                    key="value_set",
                )

                if channel is not None and value is not None:
                    gconfig.set(
                        id=interaction.guild_id,
                        title="Ticketing",
                        key="reviews-enabled",
                        value=value,
                    )
                    gconfig.set(
                        id=interaction.guild_id,
                        title="Ticketing",
                        key="reviews-channel",
                        value=channel.id,
                    )
                    response_message = response_template.format(
                        values=f"{value}, {channel}",
                    ) if response_template else "Value set"

                    await interaction.response.send_message(
                        content=response_message,
                        ephemeral=True,
                    )

                elif channel is None and value is not None:
                    gconfig.set(
                        id=interaction.guild_id,
                        title="Ticketing",
                        key="reviews-enabled",
                        value=value,
                    )
                    response_message = response_template.format(
                        values=f"{value}",
                    ) if response_template else "Value set"

                    await interaction.response.send_message(
                        content=response_message,
                        ephemeral=True,
                    )

                elif channel is not None and value is None:
                    gconfig.set(
                        id=interaction.guild_id,
                        title="Ticketing",
                        key="reviews-channel",
                        value=channel,
                    )
                    response_message = response_template.format(
                        values=f"{channel}",
                    ) if response_template else "Value set"

                    await interaction.response.send_message(
                        content=response_message,
                        ephemeral=True,
                    )

                else:
                    await interaction.response.send_message(
                        content="You have to choose",
                        ephemeral=True,
                    )
            except discord.Forbidden:
                logger.debug("No permissions")
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Exception happened: {e}",
                    ephemeral=True,
                )

    @app_commands.default_permissions(
        administrator=True,
    )
    class configure_members(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "members"
            self.description = "Configure bot actions on user"

        @app_commands.command(
            name="auto-role",
            description="Automatic role on join",
        )
        @app_commands.describe(
            role="Role to add on join",
            enabled="Should it be enabled?",
        )
        async def autorole(
            self,
            interaction: discord.Interaction,
            enabled: bool,
            role: discord.Role,
        ):
            try:
                gconfig.set(
                    id=str(interaction.guild_id),
                    title="MEMBERS",
                    key="autorole-role",
                    value=role.id,
                )
                gconfig.set(
                    id=str(interaction.guild_id),
                    title="MEMBERS",
                    key="autorole-enabled",
                    value=enabled,
                )
                await interaction.response.send_message(
                    content=f"Set value {str(role.name)}, {str(enabled)}",
                    ephemeral=True,
                )
            except Exception as e:
                logger.error("AUTOROLE-SAVE-ERR")
                await interaction.response.send_message(
                    content=f"Exception happened: {e}",
                    ephemeral=True,
                )
        @app_commands.command(name="welcome",description="Welcomes user on join")
        @app_commands.describe(text="Text used to welcome (placeholders support)",enabled="Should it be enabled?")  # noqa: E501
        async def welcome(
            self,
            interaction: discord.Interaction,
            enabled: bool,
            text: str,
            channel: discord.TextChannel,
            in_dms: bool = False,
            rich: bool= False,
        ):
            try:
                gconfig.set(
                    id=interaction.guild_id,
                    title="MEMBERS",
                    key="welcome-text",
                    value=text,
                )
                gconfig.set(
                    id=interaction.guild_id,
                    title="MEMBERS",
                    key="welcome-enabled",
                    value=enabled,
                )
                gconfig.set(
                    id=interaction.guild_id,
                    title="MEMBERS",
                    key="welcome-rich",
                    value=rich,
                )
                gconfig.set(
                    id=interaction.guild_id,
                    title="MEMBERS",
                    key="welcome-channel",
                    value=channel.id,
                )
                gconfig.set(
                    id=interaction.guild_id,
                    title="MEMBERS",
                    key="welcome-in_dms",
                    value=in_dms,
                )
                await interaction.response.send_message(
                    content="Set value/s",
                    ephemeral=True,
                )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Exception happened: {e}",
                    ephemeral=True,
                )

    @app_commands.default_permissions(
        administrator=True,
    )
    class configure(app_commands.Group):
        def __init__(self):
            super().__init__()
            self.name = "guildconfig"
            self.description = "Config for server"
            self.add_command(GuildConfig.configure_sec())
            self.add_command(GuildConfig.configure_appear())
            self.add_command(GuildConfig.configure_members())
            self.add_command(GuildConfig.configure_ticketing())
            self.add_command(GuildConfig.configure_fun())
            self.add_command(GuildConfig.configure_automations())

        @app_commands.command(
            name="reset",
            description="Resets the config. NO TAKIES BACKSIES, AS IT GETS DELETED PERMANENTLY, BREAKS ANY VERIFY SYSTEM",  # noqa: E501
        )
        async def reset_config(
            self,
            interaction: discord.Interaction,
        ):
            try:
                os.remove(f"data/guilds/{interaction.guild.id}.toml")
                gconfig._load_all_configs()
                await interaction.response.send_message(
                    content=lang.get(uconfig.get(interaction.user.id,"APPEARANCE","language"),"Responds","config_reset"),
                    ephemeral=True,
                )
            except FileNotFoundError:
                await interaction.response.send_message(
                    content="No config generated yet! Try configuring the server",
                    ephemeral=True,
                )
            except PermissionError:
                await interaction.response.send_message(
                    content="Permission Error! Ensure I have permissions for the file. If you're an administrator using Lorelei-bot, report this to Cosita Development!",  # noqa: E501
                    ephemeral=True,
                )

        @app_commands.command(
            name="export",
            description="Exports config",  # noqa: E501
        )
        async def export(self,interaction:discord.Interaction):
            try:
                if not interaction.guild:
                    await interaction.response.send_message("This command is runnable only from guilds")  # noqa: E501
                file = "data/guilds"+ str(interaction.guild.id) + ".toml"
                await interaction.response.send_message(
                    content="Here is exported content that bot has saved. Remember that exports of message id dependent functions will not be ported over.",  # noqa: E501
                    file=file,
                    ephemeral=True,
                )
            except PermissionError:
                await interaction.response.send_message(
                    content="Permission Error! Ensure I have permissions for the file. If you're an administrator using Lorelei-bot, report this to Cosita Development!",  # noqa: E501
                    ephemeral=True,
                )
            except FileNotFoundError:
                await interaction.response.send_message(
                    content="No config generated yet! Try configuring the server",
                    ephemeral=True,
                )
        @app_commands.command(
            name="import",
            description="Imports config",  # noqa: E501
        )
        async def import_config(self,interaction:discord.Interaction):  # noqa: E501
            try:
                if not interaction.guild:
                    await interaction.response.send_message("This command is runnable only from guilds")  # noqa: E501
                if not interaction.data['attachments']:
                    await interaction.response.send_message(
                        content="No file uploaded. Please upload a config file.",
                        ephemeral=True,
                    )
                    return
                attachment = interaction.data['attachments'][0]
                file_content = await attachment.read()
                with open("data/guilds"+ str(interaction.guild.id) + ".toml", "w") as f:  # noqa: E501
                    f.write(file_content)
                await interaction.response.send_message(
                    content="Config imported successfully.",
                    ephemeral=True,
                )
            except Exception as e:
                await interaction.response.send_message(
                    content=f"Error: {e}",
                    ephemeral=True,
                )

async def setup(bot:commands.Bot):
    cog = GuildConfig(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.configure())
