import discord
from discord.ext import commands
import json
import os
import asyncio
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

START_TIME = datetime.now()

TICKETS_FILE = "tickets.json"
WARNINGS_FILE = "warnings.json"

BAD_WORDS = [
    "блять", "блядь", "бля", "хуй", "хуя", "хуйни", "хуе",
    "пизда", "пиздец", "пизд", "ёб", "еб", "ебать", "ебан",
    "сука", "суки", "сук", "нахуй", "нах", "падла", "гандон",
    "уёб", "ебанат", "долбоёб", "мудак", "шлюха", "урод",
    "тварь", "подонок", "мерзавец", "скотина", "проститутка",
    "кончена", "конченный", "дебил", "идиот", "дурак", "кретин"
]

EIGHT_BALL_ANSWERS = [
    "🔮 Да, конечно!",
    "🔮 Нет, даже не думай!",
    "🔮 Возможно...",
    "🔮 Спроси позже",
    "🔮 Определённо да!",
    "🔮 Никаких шансов",
    "🔮 Звёзды говорят да",
    "🔮 Не стоит",
    "🔮 Да, но осторожно",
    "🔮 Мой ответ - нет"
]

MEMES = [
    "Когда тебя удалили из голосового, а ты вернулся через 5 секунд 😎",
    "POV: Ты написал в чат, а тебе лайк поставили 🔥",
    "Когда лидер сказал 'все на рейд', а ты в реале спишь 😴",
    "Когда новый написал в чат и ему сразу дали роль huesos 💀",
    "Когда ты выжил в перестрелке с 1 HP 🏥",
    "Когда бан за мат, а ты писал 'спасибо' 🤡",
    "Когда Dep написал объявление, а его никто не прочитал 📰",
    "Когда ты подал заявку и ждёшь 3 дня ⏳",
    "Когда лидер кикнул за то, что ты не на рейде 🚪",
    "Когда бот выдал роль huesos всем новым 💀"
]

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")
    await bot.change_presence(activity=discord.Game(name="ДС Чат Бот | !help"))
    bot.add_view(TicketButton())
    bot.add_view(TicketActionsView(0, 0))

@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="huesos")
    if role:
        try:
            await member.add_roles(role)
        except:
            pass

    channel = member.guild.system_channel
    if channel:
        embed = discord.Embed(
            title="👋 Добро пожаловать!",
            description=f"{member.mention} присоединился к серверу!\nТебе выдана роль **huesos**.\n\n📜 Прочитай правила в канале **📜・правила**",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Участников: {member.guild.member_count}")
        await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    channel = member.guild.system_channel
    if channel:
        embed = discord.Embed(
            title="👋 До встречи!",
            description=f"**{member.name}** покинул сервер.",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if check_bad_words(message.content):
        huesos_role = discord.utils.get(message.guild.roles, name="huesos")
        if not huesos_role or huesos_role not in message.author.roles:
            await bot.process_commands(message)
            return

        warnings = load_warnings()
        user_id = str(message.author.id)

        if user_id not in warnings:
            warnings[user_id] = {"count": 0, "reasons": []}

        warnings[user_id]["count"] += 1
        warnings[user_id]["reasons"].append({
            "text": message.content[:100],
            "date": datetime.now().strftime("%d.%m.%Y %H:%M")
        })
        save_warnings(warnings)

        count = warnings[user_id]["count"]

        if count == 1:
            embed = discord.Embed(
                title="⚠️ Предупреждение 1/3",
                description=f"{message.author.mention}, не материтесь в чате!",
                color=discord.Color.orange()
            )
            embed.set_footer(text="Следующее нарушение = мут на 5 минут")
            await message.delete()
            await message.channel.send(embed=embed)

        elif count == 2:
            embed = discord.Embed(
                title="⚠️ Предупреждение 2/3",
                description=f"{message.author.mention}, это последнее предупреждение!",
                color=discord.Color.red()
            )
            embed.set_footer(text="Следующее нарушение = мут на 10 минут")
            await message.delete()
            await message.channel.send(embed=embed)

        elif count >= 3:
            try:
                await message.author.timeout(timedelta(minutes=10), reason="Повторное нарушение правил")
                embed = discord.Embed(
                    title="🔇 Мут на 10 минут",
                    description=f"{message.author.mention} замьючен за повторные нарушения!",
                    color=discord.Color.dark_red()
                )
                await message.delete()
                await message.channel.send(embed=embed)
            except:
                pass

        return

    await bot.process_commands(message)

def load_tickets():
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tickets": [], "counter": 0}

def save_tickets(data):
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_warnings():
    if os.path.exists(WARNINGS_FILE):
        with open(WARNINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_warnings(data):
    with open(WARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def check_bad_words(text):
    text_lower = text.lower()
    for word in BAD_WORDS:
        if word.lower() in text_lower:
            return True
    return False

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📝 Подать заявку", style=discord.ButtonStyle.green, custom_id="ticket_create")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_tickets()

        user_id = interaction.user.id
        for ticket in reversed(data["tickets"]):
            if ticket["user_id"] == user_id and ticket["status"] == "open":
                await interaction.response.send_message("❌ У вас уже есть открытая заявка!", ephemeral=True)
                return

        for ticket in reversed(data["tickets"]):
            if ticket["user_id"] == user_id:
                last_time = datetime.strptime(ticket["created_at"], "%d.%m.%Y %H:%M")
                if datetime.now() - last_time < timedelta(hours=1):
                    remaining = timedelta(hours=1) - (datetime.now() - last_time)
                    minutes = remaining.seconds // 60
                    await interaction.response.send_message(
                        f"⏳ Подождите ещё **{minutes} мин.** перед следующей заявкой!",
                        ephemeral=True
                    )
                    return
                break

        data["counter"] += 1
        ticket_id = data["counter"]

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, manage_channels=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        for role_name in ["Sad", "Dep", "leader"]:
            role = discord.utils.get(interaction.guild.roles, name=role_name)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket_category = discord.utils.get(interaction.guild.categories, name="📋 ЗАЯВКИ")
        if not ticket_category:
            ticket_category = await interaction.guild.create_category("📋 ЗАЯВКИ")

        channel = await interaction.guild.create_text_channel(
            f"заявка-{ticket_id}",
            category=ticket_category,
            overwrites=overwrites,
            topic=f"Заявка от {interaction.user.name}"
        )

        ticket = {
            "id": ticket_id,
            "user_id": interaction.user.id,
            "user_name": interaction.user.name,
            "channel_id": channel.id,
            "status": "open",
            "created_at": datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        data["tickets"].append(ticket)
        save_tickets(data)

        embed = discord.Embed(
            title=f"📋 Заявка #{ticket_id}",
            description=f"Заявка от {interaction.user.mention}",
            color=discord.Color.orange()
        )
        embed.add_field(name="📅 Дата", value=ticket["created_at"], inline=True)
        embed.add_field(name="👤 Статус", value="Открыта", inline=True)
        embed.add_field(
            name="📝 Напишите",
            value="Опишите почему вы хотите вступить в семью.\nОжидайте ответа от лидеров.",
            inline=False
        )

        view = TicketActionsView(ticket_id, channel.id)
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"✅ Заявка создана: {channel.mention}", ephemeral=True)

class TicketActionsView(discord.ui.View):
    def __init__(self, ticket_id=None, channel_id=None):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id
        self.channel_id = channel_id

    def check_permission(self, interaction):
        for role_name in ["Sad", "Dep", "leader"]:
            role = discord.utils.get(interaction.guild.roles, name=role_name)
            if role and role in interaction.user.roles:
                return True
        return False

    def get_ticket_data(self, interaction):
        data = load_tickets()
        for ticket in data["tickets"]:
            if ticket["channel_id"] == interaction.channel.id:
                return ticket, data
        return None, data

    @discord.ui.button(label="✅ Принять", style=discord.ButtonStyle.green, custom_id="ticket_accept")
    async def accept_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.check_permission(interaction):
            await interaction.response.send_message("❌ У вас нет прав!", ephemeral=True)
            return

        ticket, data = self.get_ticket_data(interaction)
        if not ticket:
            await interaction.response.send_message("❌ Заявка не найдена!", ephemeral=True)
            return

        ticket["status"] = "accepted"
        save_tickets(data)

        user = interaction.guild.get_member(ticket["user_id"])
        if user:
            role = discord.utils.get(interaction.guild.roles, name="Frend")
            if role:
                await user.add_roles(role)
            await interaction.channel.send(f"✅ **{user.mention}** принят в семью!")

        embed = discord.Embed(
            title=f"✅ Заявка #{ticket['id']} Принята",
            description=f"Принято: {interaction.user.mention}",
            color=discord.Color.green()
        )
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ Заявка принята!", ephemeral=True)

    @discord.ui.button(label="❌ Отклонить", style=discord.ButtonStyle.red, custom_id="ticket_reject")
    async def reject_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.check_permission(interaction):
            await interaction.response.send_message("❌ У вас нет прав!", ephemeral=True)
            return

        ticket, data = self.get_ticket_data(interaction)
        if not ticket:
            await interaction.response.send_message("❌ Заявка не найдена!", ephemeral=True)
            return

        ticket["status"] = "rejected"
        save_tickets(data)

        embed = discord.Embed(
            title=f"❌ Заявка #{ticket['id']} Отклонена",
            description=f"Отклонено: {interaction.user.mention}",
            color=discord.Color.red()
        )
        await interaction.channel.send(embed=embed)
        await interaction.channel.send("Канал будет удалён через 5 секунд...")
        await asyncio.sleep(5)
        await interaction.channel.delete()
        await interaction.response.send_message("❌ Заявка отклонена!", ephemeral=True)

    @discord.ui.button(label="🔒 Закрыть", style=discord.ButtonStyle.grey, custom_id="ticket_close")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.check_permission(interaction):
            await interaction.response.send_message("❌ У вас нет прав!", ephemeral=True)
            return

        ticket, data = self.get_ticket_data(interaction)
        if not ticket:
            await interaction.response.send_message("❌ Заявка не найдена!", ephemeral=True)
            return

        ticket["status"] = "closed"
        save_tickets(data)

        embed = discord.Embed(
            title=f"🔒 Заявка #{ticket['id']} Закрыта",
            description=f"Закрыто: {interaction.user.mention}",
            color=discord.Color.grey()
        )
        await interaction.channel.send(embed=embed)
        await interaction.channel.send("Канал будет удалён через 5 секунд...")
        await asyncio.sleep(5)
        await interaction.channel.delete()
        await interaction.response.send_message("🔒 Заявка закрыта!", ephemeral=True)

# ==================== КОМАНДЫ ====================

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📚 КОМАНДЫ БОТА",
        description="Все команды для управления сервером",
        color=discord.Color.purple()
    )

    admin_commands = [
        ("`!rules`", "Создать каналы с правилами"),
        ("`!ticket_panel`", "Создать панель заявок"),
        ("`!tickets`", "Список открытых заявок"),
        ("`!addrole @user [роль]`", "Выдать роль"),
        ("`!removerole @user [роль]`", "Снять роль"),
        ("`!warnings @user`", "Посмотреть предупреждения"),
        ("`!clearwarnings @user`", "Очистить предупреждения"),
    ]

    fun_commands = [
        ("`!avatar [@user]`", "Аватар пользователя"),
        ("`!serverinfo`", "Информация о сервере"),
        ("`!userinfo [@user]`", "Информация о пользователе"),
        ("`!ping`", "Пинг бота"),
        ("`!uptime`", "Время работы бота"),
        ("`!8ball [вопрос]`", "Магический шар"),
        ("`!meme`", "Случайный мем"),
        ("`!coinflip`", "Подбросить монетку"),
        ("`!say [текст]`", "Бот повторяет текст"),
        ("`!random [число]`", "Случайное число"),
    ]

    for name, value in admin_commands:
        embed.add_field(name=f"⚙️ {name}", value=value, inline=False)

    for name, value in fun_commands:
        embed.add_field(name=f"🎮 {name}", value=value, inline=False)

    embed.set_footer(text="Создано для GTA 5 RP семьи | !help")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def rules(ctx):
    guild = ctx.guild

    dep_role = discord.utils.get(guild.roles, name="Dep")
    leader_role = discord.utils.get(guild.roles, name="leader")
    sad_role = discord.utils.get(guild.roles, name="Sad")
    vzp_role = discord.utils.get(guild.roles, name="VZP")
    frend_role = discord.utils.get(guild.roles, name="Frend")
    huesos_role = discord.utils.get(guild.roles, name="huesos")

    rules_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
    }
    if dep_role:
        rules_overwrites[dep_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    if leader_role:
        rules_overwrites[leader_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    rules_channel = await guild.create_text_channel("📜・правила", overwrites=rules_overwrites)

    embed = discord.Embed(
        title="📜 ПРАВИЛА СЕРВЕРА",
        description="**Добро пожаловать в семью GTA 5 RP!**",
        color=discord.Color.dark_red()
    )

    rules_list = [
        ("1️⃣", "Не ругаться и не материться в чатах"),
        ("2️⃣", "Уважать других участников сервера"),
        ("3️⃣", "Не спамить и не флудить"),
        ("4️⃣", "Не рекламовать другие серверы"),
        ("5️⃣", "Не оскорблять участников семьи"),
        ("6️⃣", "Слушать лидеров и старших"),
        ("7️⃣", "Не распространять личную информацию других"),
        ("8️⃣", "Быть активным и участвовать в жизни семьи"),
        ("9️⃣", "Не использовать баги и читы в игре"),
        ("🔟", "Решать конфликты мирным путём"),
    ]

    for emoji, rule in rules_list:
        embed.add_field(name=emoji, value=rule, inline=False)

    embed.add_field(
        name="⚠️ Наказание",
        value="За нарушение правил: предупреждение → мут → кик → бан",
        inline=False
    )
    embed.set_footer(text="Незнание правил не освобождает от ответственности")

    await rules_channel.send(embed=embed)

    news_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
    }
    if dep_role:
        news_overwrites[dep_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    if leader_role:
        news_overwrites[leader_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    await guild.create_text_channel("📰・новости", overwrites=news_overwrites)

    announce_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
    }
    if dep_role:
        announce_overwrites[dep_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    if leader_role:
        announce_overwrites[leader_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    await guild.create_text_channel("📢・объявления", overwrites=announce_overwrites)

    flood_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
    }
    if huesos_role:
        flood_overwrites[huesos_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    if frend_role:
        flood_overwrites[frend_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    if vzp_role:
        flood_overwrites[vzp_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    if leader_role:
        flood_overwrites[leader_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    if dep_role:
        flood_overwrites[dep_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    if sad_role:
        flood_overwrites[sad_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    await guild.create_text_channel("💬・флуд", overwrites=flood_overwrites)

    await ctx.send("✅ Каналы созданы!")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def ticket_panel(ctx):
    embed = discord.Embed(
        title="📋 Панель заявок",
        description="Нажмите на кнопку чтобы подать заявку на вступление в семью.",
        color=discord.Color.orange()
    )
    embed.add_field(
        name="📝 Как подать заявку?",
        value="1. Нажмите кнопку ниже\n2. Напишите почему хотите вступить\n3. Ожидайте ответа от лидеров",
        inline=False
    )
    embed.set_footer(text="Заявки рассматриваются лидерами и департаментом")

    view = TicketButton()
    await ctx.send(embed=embed, view=view)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def tickets(ctx):
    data = load_tickets()
    open_tickets = [t for t in data["tickets"] if t["status"] == "open"]

    embed = discord.Embed(title="📋 Открытые заявки", color=discord.Color.blue())
    if open_tickets:
        for ticket in open_tickets:
            embed.add_field(
                name=f"Заявка #{ticket['id']}",
                value=f"От: <@{ticket['user_id']}>\nСтатус: {ticket['status']}\nДата: {ticket['created_at']}",
                inline=False
            )
    else:
        embed.add_field(name="Нет заявок", value="Все заявки обработаны", inline=False)

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, role_name: str = "Frend"):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send(f"❌ Роль **{role_name}** не найдена")
        return
    await member.add_roles(role)
    await ctx.send(f"✅ Роль **{role_name}** выдана {member.mention}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, role_name: str = "Frend"):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send(f"❌ Роль **{role_name}** не найдена")
        return
    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"❌ Роль **{role_name}** снята с {member.mention}")
    else:
        await ctx.send(f"У {member.mention} нет роли **{role_name}**")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def warnings(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("❌ Укажите пользователя: `!warnings @user`")
        return

    warnings_data = load_warnings()
    user_id = str(member.id)

    if user_id not in warnings_data or warnings_data[user_id]["count"] == 0:
        await ctx.send(f"✅ У {member.mention} нет предупреждений")
        return

    data = warnings_data[user_id]
    embed = discord.Embed(
        title=f"⚠️ Предупреждения {member.name}",
        description=f"Всего: {data['count']}/3",
        color=discord.Color.orange()
    )

    for i, reason in enumerate(data["reasons"][-5:], 1):
        embed.add_field(
            name=f"#{i}",
            value=f"Текст: `{reason['text']}`\nДата: {reason['date']}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def clearwarnings(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("❌ Укажите пользователя: `!clearwarnings @user`")
        return

    warnings_data = load_warnings()
    user_id = str(member.id)

    if user_id in warnings_data:
        warnings_data[user_id] = {"count": 0, "reasons": []}
        save_warnings(warnings_data)

    await ctx.send(f"✅ Предупреждения {member.mention} очищены")

# ==================== ИГРОВЫЕ КОМАНДЫ ====================

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"🖼️ Аватар {member.name}", color=discord.Color.blue())
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"📊 {guild.name}", color=discord.Color.blue())

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(name="👑 Владелец", value=guild.owner.mention if guild.owner else "Неизвестен", inline=True)
    embed.add_field(name="👥 Участников", value=guild.member_count, inline=True)
    embed.add_field(name="💬 Каналов", value=len(guild.channels), inline=True)
    embed.add_field(name="🏷️ Ролей", value=len(guild.roles), inline=True)
    embed.add_field(name="📅 Создан", value=guild.created_at.strftime("%d.%m.%Y"), inline=True)
    embed.add_field(name="🌐 Регион", value=str(guild.preferred_locale), inline=True)

    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 {member.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=member.display_avatar.url)

    roles = [role.mention for role in member.roles[1:]]
    roles_text = ", ".join(roles) if roles else "Нет ролей"

    embed.add_field(name="🆔 ID", value=member.id, inline=True)
    embed.add_field(name="📅 Аккаунт создан", value=member.created_at.strftime("%d.%m.%Y"), inline=True)
    embed.add_field(name="📥 Вошёл", value=member.joined_at.strftime("%d.%m.%Y") if member.joined_at else "Неизвестно", inline=True)
    embed.add_field(name="🏷️ Роли", value=roles_text, inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(title="🏓 Пинг", color=discord.Color.green())
    embed.add_field(name="Задержка", value=f"{latency}ms", inline=True)

    if latency < 100:
        embed.add_field(name="Статус", value="🟢 Отлично", inline=True)
    elif latency < 200:
        embed.add_field(name="Статус", value="🟡 Хорошо", inline=True)
    else:
        embed.add_field(name="Статус", value="🔴 Плохо", inline=True)

    await ctx.send(embed=embed)

@bot.command()
async def uptime(ctx):
    delta = datetime.now() - START_TIME
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    embed = discord.Embed(title="⏱️ Время работы", color=discord.Color.green())
    embed.add_field(name="Аптайм", value=f"{hours}ч {minutes}м {seconds}с", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="8ball")
async def eight_ball(ctx, *, question: str):
    answer = random.choice(EIGHT_BALL_ANSWERS)
    embed = discord.Embed(title="🎱 Магический шар", color=discord.Color.purple())
    embed.add_field(name="❓ Вопрос", value=question, inline=False)
    embed.add_field(name="🔮 Ответ", value=answer, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def meme(ctx):
    meme_text = random.choice(MEMES)
    embed = discord.Embed(title="😂 Мем дня", description=meme_text, color=discord.Color.gold())
    await ctx.send(embed=embed)

@bot.command()
async def coinflip(ctx):
    result = random.choice(["🪙 Орёл!", "🪙 Решка!"])
    embed = discord.Embed(title="🎲 Подброс монетки", description=result, color=discord.Color.gold())
    await ctx.send(embed=embed)

@bot.command()
async def say(ctx, *, text: str):
    await ctx.message.delete()
    await ctx.send(text)

@bot.command()
async def random(ctx, number: int = 100):
    result = random.randint(1, number)
    embed = discord.Embed(title="🎲 Случайное число", description=f"**{result}** (от 1 до {number})", color=discord.Color.gold())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"✅ Удалено {amount} сообщений!")
    await asyncio.sleep(3)
    await msg.delete()

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = "Не указана"):
    await member.kick(reason=reason)
    embed = discord.Embed(title="🚪 Кик", color=discord.Color.orange())
    embed.add_field(name="Участник", value=member.mention, inline=True)
    embed.add_field(name="Причина", value=reason, inline=True)
    embed.add_field(name="Кем", value=ctx.author.mention, inline=True)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "Не указана"):
    await member.ban(reason=reason)
    embed = discord.Embed(title="🔨 Бан", color=discord.Color.red())
    embed.add_field(name="Участник", value=member.mention, inline=True)
    embed.add_field(name="Причина", value=reason, inline=True)
    embed.add_field(name="Кем", value=ctx.author.mention, inline=True)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    embed = discord.Embed(title="🔓 Анбан", color=discord.Color.green())
    embed.add_field(name="Пользователь", value=user.mention, inline=True)
    await ctx.send(embed=embed)

bot.run(os.getenv("TOKEN"))
