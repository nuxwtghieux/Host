import discord
from discord.ext import tasks
from discord import app_commands
import requests
import time
import urllib3
import warnings
import logging
import re
from datetime import datetime
from flask import Flask
import threading
import os

# ===== TẮT LOG =====
urllib3.disable_warnings()
warnings.filterwarnings("ignore")
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("discord").setLevel(logging.WARNING)

# ===== FLASK WEB SERVER =====
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host='0.0.0.0', port=8080)
# ============================

TOKEN = os.getenv('DISCORD_TOKEN')

GUILD_ID = 1509102064784117821
CHECK_CHANNEL_ID = 1523606725318676532
TICKET_CHANNEL_ID = 1523604635816820856
TICKET_CATEGORY_ID = 1523595672861933569
ADMIN_ROLE_ID = 1511311539896979466
LOG_USER_ID = 1507006947755430069
WELCOME_CHANNEL_ID = 1523598483632947281
GOODBYE_CHANNEL_ID = 1523602359605919746

# DIVAZ SCANNER
SCAN_CHANNEL_ID = 1523707366280003594
PLACE_ID = "88323040672117"

GIF_URL = "https://s7.ezgif.com/tmp/ezgif-7da15b9e2a77cc53.gif"
WELCOME_GIF_URL = "https://s7.ezgif.com/tmp/ezgif-7470538eb37502c7.gif"
GOOBBYE_URL = "https://i.imgur.com/LL8i48j.gif"
THUMBNAIL_URL = "https://huyhieu08.online/uploads/20260707_054705_91412ed7.png"
IMAGE_URL = "https://i.postimg.cc/V6CFtBL0/no-Filter.webp"

ticket_counter = 0
scan_active = True

# ===== CÁC HÀM TÍNH TOÁN =====
def round_card(bank):
    card_raw = bank * 1.15
    return int(round(card_raw / 10000) * 10000)

def round_bank(bank):
    return int(round(bank / 1000) * 1000)

def is_admin(member: discord.Member):
    return any(role.id == ADMIN_ROLE_ID for role in member.roles)

async def load_ticket_counter_from_dm(bot):
    global ticket_counter
    try:
        log_user = bot.get_user(LOG_USER_ID) or await bot.fetch_user(LOG_USER_ID)
        async for msg in log_user.history(limit=50):
            if msg.author == bot.user and msg.embeds:
                embed = msg.embeds[0]
                if embed.title and "Ticket số" in embed.title:
                    match = re.search(r'Ticket số (\d+)', embed.title)
                    if match:
                        last_ticket = int(match.group(1))
                        if last_ticket > ticket_counter:
                            ticket_counter = last_ticket
        print(f"✅ Số ticket hiện tại: {ticket_counter}")
    except Exception as e:
        print(f"❌ Lỗi đọc DM: {e}")

async def send_ticket_log(bot, ticket_number, creator_id, closer_mention, service_type, reason="Không"):
    now = datetime.now()
    log_user = bot.get_user(LOG_USER_ID) or await bot.fetch_user(LOG_USER_ID)
    
    embed_log = discord.Embed(title=f"# Ticket số {ticket_number}", color=0x3498db)
    embed_log.add_field(name="🧑‍🦱 Người mở ticket:", value=f"<@{creator_id}>" if creator_id else "Không xác định", inline=False)
    embed_log.add_field(name="🧑‍🦱 Người đóng ticket:", value=closer_mention, inline=False)
    embed_log.add_field(name="🔖 Dịch vụ:", value=service_type, inline=False)
    embed_log.add_field(name="⏰ Thời gian đóng:", value=now.strftime('%H:%M:%S | %d - %m - %Y'), inline=False)
    embed_log.add_field(name="📝 Lí do:", value=reason, inline=False)
    
    try:
        await log_user.send(embed=embed_log)
    except:
        pass

# ===== MODALS =====
class PriceMoneyModal(discord.ui.Modal, title="Check giá tiền"):
    amount = discord.ui.TextInput(label="Nhập số tiền", placeholder="Ví dụ: 100000 (TIỀN)", required=True, max_length=20)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            money = int(self.amount.value.replace(",", "").replace(".", ""))
        except ValueError:
            return await interaction.response.send_message("❌ Vui lòng chỉ nhập số.", ephemeral=True)
        
        bank = round_bank(int(money * 0.12))
        card = round_card(bank)
        now = datetime.now()
        
        embed = discord.Embed(title="💰 GIÁ CÀY TIỀN HIỆN TẠI 💰", color=0x3498db)
        embed.description = (
            "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵ㆍ**Số tiền cần cày:** **{money:,} TIỀN**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💳ㆍ**Chuyển khoản (Bank):** **{bank:,} VND**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔖ㆍ**Thẻ cào (Card):** **{card:,} VND**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "‼️ **ÁP MÃ GIẢM GIÁ SẼ ĐƯỢC GIẢM TÙY THEO MÃ** ‼️"
        )
        embed.set_image(url=GIF_URL)
        embed.set_footer(text=f"{now.strftime('%H:%M:%S | %d-%m-%Y')} | {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class PriceSlayModal(discord.ui.Modal, title="Check giá slay"):
    amount = discord.ui.TextInput(label="Nhập số slay", placeholder="Ví dụ: 2000 (SLAY)", required=True, max_length=20)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            slay = int(self.amount.value.replace(",", "").replace(".", ""))
        except ValueError:
            return await interaction.response.send_message("❌ Vui lòng chỉ nhập số.", ephemeral=True)
        
        bank = round_bank(int(slay * 25))
        card = round_card(bank) if bank > 8000 else 0
        now = datetime.now()
        
        card_text = f"{card:,} VND" if card > 0 else "Chỉ nhận card từ 400 SLAY trở lên!"
        
        embed = discord.Embed(title="💅 GIÁ CÀY SLAY HIỆN TẠI 💅", color=0x3498db)
        embed.description = (
            "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💅ㆍ**Số slay cần cày:** **{slay:,} SLAY**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💳ㆍ**Chuyển khoản (Bank):** **{bank:,} VND**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔖ㆍ**Thẻ cào (Card):** **{card_text}**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "‼️ **ÁP MÃ GIẢM GIÁ SẼ ĐƯỢC GIẢM TÙY THEO MÃ** ‼️"
        )
        embed.set_image(url=GIF_URL)
        embed.set_footer(text=f"{now.strftime('%H:%M:%S | %d-%m-%Y')} | {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class VndToMoneyModal(discord.ui.Modal, title="VND → Tiền cần cày"):
    amount = discord.ui.TextInput(label="Nhập số tiền VND bạn muốn trả", placeholder="Ví dụ: 50000", required=True, max_length=20)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            vnd = int(self.amount.value.replace(",", "").replace(".", ""))
        except ValueError:
            return await interaction.response.send_message("❌ Vui lòng chỉ nhập số.", ephemeral=True)
        
        money = int(vnd / 0.12)
        bank = round_bank(vnd)
        card = round_card(bank)
        now = datetime.now()
        
        embed = discord.Embed(title="💵 SỐ TIỀN CÀY BẠN NHẬN ĐƯỢC 💵", color=0xe67e22)
        embed.description = (
            "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💳ㆍ**Số VND bạn trả:** **{vnd:,} VND**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰ㆍ**Số tiền cày bạn nhận được:** **{money:,} TIỀN**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔖ㆍ**Thẻ cào (Card):** **{card:,} VND**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "‼️ **ÁP MÃ GIẢM GIÁ SẼ ĐƯỢC GIẢM TÙY THEO MÃ** ‼️"
        )
        embed.set_image(url=GIF_URL)
        embed.set_footer(text=f"{now.strftime('%H:%M:%S | %d-%m-%Y')} | {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class VndToSlayModal(discord.ui.Modal, title="VND → Slay"):
    amount = discord.ui.TextInput(label="Nhập số tiền VND bạn muốn trả", placeholder="Ví dụ: 50000", required=True, max_length=20)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            vnd = int(self.amount.value.replace(",", "").replace(".", ""))
        except ValueError:
            return await interaction.response.send_message("❌ Vui lòng chỉ nhập số.", ephemeral=True)
        
        slay = int(vnd / 25)
        bank = round_bank(vnd)
        card = round_card(bank) if bank > 8000 else 0
        now = datetime.now()
        
        card_text = f"{card:,} VND" if card > 0 else "Chỉ nhận card từ 400 SLAY trở lên!"
        
        embed = discord.Embed(title="💅 SỐ SLAY BẠN NHẬN ĐƯỢC 💅", color=0x9b59b6)
        embed.description = (
            "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💳ㆍ**Số VND bạn trả:** **{vnd:,} VND**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💅ㆍ**Số slay bạn nhận được:** **{slay:,} SLAY**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔖ㆍ**Thẻ cào (Card):** **{card_text}**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "‼️ **ÁP MÃ GIẢM GIÁ SẼ ĐƯỢC GIẢM TÙY THEO MÃ** ‼️"
        )
        embed.set_image(url=GIF_URL)
        embed.set_footer(text=f"{now.strftime('%H:%M:%S | %d-%m-%Y')} | {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class TicketCreateModal(discord.ui.Modal, title="Tạo đơn"):
    service = discord.ui.TextInput(label="Bạn muốn cày tiền hay slay (Tiền/Slay):", placeholder="Tiền hoặc Slay", required=True, max_length=10)
    
    async def on_submit(self, interaction: discord.Interaction):
        global ticket_counter
        service_type = self.service.value
        guild = interaction.guild
        user = interaction.user
        
        for ch in guild.channels:
            if ch.name.startswith("đơn-") and ch.topic and str(user.id) == ch.topic:
                return await interaction.response.send_message("❌ Bạn đã tạo đơn!", ephemeral=True)
        
        category = guild.get_channel(TICKET_CATEGORY_ID)
        ticket_counter += 1
        if ticket_counter > 999:
            ticket_counter = 1
        
        ticket_number = f"{ticket_counter:03d}"
        now = datetime.now()
        safe_display_name = user.display_name.replace(" ", "-")[:20]
        channel_name = f"đơn-{ticket_number}-{safe_display_name}-{now.strftime('%H-%M')}"
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True),
        }
        
        channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites, topic=f"{user.id}|{service_type}")
        
        admin_ping = f"<@&{ADMIN_ROLE_ID}>"
        await channel.send(
            content=f"{user.mention} {admin_ping}",
            embed=discord.Embed(title="🎫 CÓ ĐƠN", description=f"Đơn số: **{ticket_number}**\nDịch vụ: **{service_type}**\nNgười tạo: {user.mention}\nChờ admin rep nhé💞", color=0x3498db),
            view=TicketControl()
        )
        await interaction.response.send_message(f"✅ Tạo ticket: {channel.mention}", ephemeral=True)

class CloseReason(discord.ui.Modal, title="Đóng ticket - lý do"):
    reason = discord.ui.TextInput(label="Lý do", required=True)
    
    async def on_submit(self, interaction: discord.Interaction):
        channel_name = interaction.channel.name
        parts = channel_name.split("-")
        ticket_number = parts[1] if len(parts) > 1 else "???"
        
        topic_data = interaction.channel.topic
        if topic_data and "|" in topic_data:
            creator_id, service_type = topic_data.split("|", 1)
        else:
            creator_id = topic_data
            service_type = "Không xác định"
        
        await send_ticket_log(interaction.client, ticket_number, creator_id, interaction.user.mention, service_type, self.reason.value)
        await interaction.channel.delete()

# ===== VIEWS =====
class PriceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="💰 Tiền Divaz → VND", style=discord.ButtonStyle.green, custom_id="check_price_money")
    async def check_price_money(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PriceMoneyModal())
    
    @discord.ui.button(label="💅 Slay → VND", style=discord.ButtonStyle.green, custom_id="check_price_slay")
    async def check_price_slay(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PriceSlayModal())
    
    @discord.ui.button(label="💵 VND → Tiền cày", style=discord.ButtonStyle.blurple, custom_id="vnd_to_money")
    async def vnd_to_money(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VndToMoneyModal())
    
    @discord.ui.button(label="💳 VND → Slay", style=discord.ButtonStyle.blurple, custom_id="vnd_to_slay")
    async def vnd_to_slay(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VndToSlayModal())

class TicketControl(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🔒 Đóng đơn", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin(interaction.user):
            return await interaction.response.send_message("❌ Chỉ admin", ephemeral=True)
        
        channel_name = interaction.channel.name
        parts = channel_name.split("-")
        ticket_number = parts[1] if len(parts) > 1 else "???"
        
        topic_data = interaction.channel.topic
        if topic_data and "|" in topic_data:
            creator_id, service_type = topic_data.split("|", 1)
        else:
            creator_id = topic_data
            service_type = "Không xác định"
        
        await interaction.response.send_message("🔒 Đang đóng...", ephemeral=True)
        await send_ticket_log(interaction.client, ticket_number, creator_id, interaction.user.mention, service_type)
        await interaction.channel.delete()
    
    @discord.ui.button(label="🧾 Đóng đơn kèm lý do", style=discord.ButtonStyle.grey, custom_id="close_reason")
    async def close_reason(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin(interaction.user):
            return await interaction.response.send_message("❌ Chỉ admin", ephemeral=True)
        await interaction.response.send_modal(CloseReason())

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🎫 Tạo đơn", style=discord.ButtonStyle.blurple, custom_id="create_ticket")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketCreateModal())

class ServerView(discord.ui.View):
    def __init__(self, server):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(
            style=discord.ButtonStyle.green if server['players'] <= 3 else discord.ButtonStyle.blurple,
            label="JOIN",
            url=f"https://nuxwtghieux.github.io/Snipe/?jobid={server['job_id']}"
        ))

# ===== DIVAZ SCANNER =====
def scan_divaz():
    found = []
    cursor = ""
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    while True:
        url = f"https://games.roblox.com/v1/games/{PLACE_ID}/servers/Public?limit=100"
        if cursor:
            url += f"&cursor={cursor}"
        
        try:
            response = requests.get(url, headers=headers, timeout=15, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                servers = data.get('data', [])
                
                if not servers:
                    break
                
                for server in servers:
                    players = server.get('playing', 0)
                    
                    if players < 5:
                        found.append({
                            'job_id': server['id'],
                            'players': players,
                            'ping': server.get('ping', 'N/A'),
                            'fps': server.get('fps', 'N/A'),
                            'max': server.get('maxPlayers', 'N/A')
                        })
                
                cursor = data.get('nextPageCursor')
                if not cursor:
                    break
                
                time.sleep(1)
            else:
                break
        except:
            time.sleep(3)
    
    return found

# ===== BOT CHÍNH =====
class Bot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        self.tree.add_command(tattimmap_cmd)
        self.tree.add_command(battimmap_cmd)
        await self.tree.sync(guild=guild)
        self.add_view(PriceView())
        self.add_view(TicketView())
        self.add_view(TicketControl())
    
    async def on_ready(self):
        await load_ticket_counter_from_dm(self)
        await self.panel()
        self.scan_loop.start()
        print(f"🚀 Bot ready! Ticket tiếp theo: {ticket_counter + 1}")
    
    async def panel(self):
        ch_check = self.get_channel(CHECK_CHANNEL_ID)
        if ch_check:
            async for m in ch_check.history(limit=50):
                if m.author == self.user:
                    await m.delete()
            
            embed_check = discord.Embed(
                title="‼️ HƯỚNG DẪN CHECK GIÁ 📍",
                description="━━━━━━━━━━━━━━━━━━━━━━\n"
                           "📌 BƯỚC 1ㆍNhấn '💰 Tiền Divaz → VND' hoặc '💅 Slay → VND' để xem giá.\n\n"
                           "📌 BƯỚC 2ㆍNhập số tiền/slay bạn muốn cày (VD: 100.000K, 2000 slay).\n\n"
                           "📌 BƯỚC 3ㆍSau đó 'gửi' sẽ biết ngay số tiền phải trả.\n\n"
                           "💡 **Nút phụ:** '💵 VND → Tiền cày' và '💳 VND → Slay' để tính ngược từ VND.",
                color=0x3498db
            )
            embed_check.set_footer(text=datetime.now().strftime('%H:%M:%S | %d-%m-%Y'))
            await ch_check.send(embed=embed_check, view=PriceView())
        
        ch_ticket = self.get_channel(TICKET_CHANNEL_ID)
        if ch_ticket:
            async for m in ch_ticket.history(limit=50):
                if m.author == self.user:
                    await m.delete()
            
            await ch_ticket.send(
                embed=discord.Embed(
                    title="🛒 DỊCH VỤ CÀY TIỀN & SLAY",
                    description="━━━━━━━━━━━━━━━━━━━━━━\n✅ HÃY TẠO ĐƠN Ở NÚT BÊN DƯỚI NẾU BẠN CÓ NHU CẦU CẦN CÀY TIỀN HOẶC SLAY DIVAZ 💤",
                    color=0x3498db
                ),
                view=TicketView()
            )
    
    @tasks.loop(seconds=150)  # ĐÚNG 150 GIÂY
    async def scan_loop(self):
        global scan_active
        
        if not scan_active:
            return
        
        channel = self.get_channel(SCAN_CHANNEL_ID)
        if not channel:
            return
        
        servers = scan_divaz()
        
        if servers:
            best = servers[0]
            p = best['players']
            code = best['job_id'][-5:]
            color = 0x00ff00 if p <= 3 else 0xffaa00
            now = datetime.now()
            
            print(f"✅ Gửi server: #{code} | {p}/{best['max']} người")
            
            embed = discord.Embed(
                title="🎮 DIVAZ - SERVER TRỐNG",
                description=f"**Mã Server:** `#{code}`",
                color=color,
                timestamp=now
            )
            status = f"🟢 {p}/{best['max']}" if p <= 3 else f"🟡 {p}/{best['max']}"
            embed.add_field(name="👥 **NGƯỜI CHƠI**", value=status, inline=True)
            embed.add_field(name="📶 **PING**", value=f"{best['ping']}ms", inline=True)
            embed.add_field(name="🎯 **FPS**", value=f"{best['fps']}", inline=True)
            
            embed.set_thumbnail(url=THUMBNAIL_URL)
            embed.set_image(url=IMAGE_URL)
            embed.set_footer(text=f"BotByPawPaw • {now.strftime('%H:%M:%S | %d/%m/%Y')}")
            
            await channel.send(embed=embed, view=ServerView(best))
        else:
            print("❌ Không tìm thấy server nào!")
    
    async def on_member_join(self, member):
        channel = self.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return
        
        now = datetime.now()
        guild = member.guild
        admin_mention = f"<@&{ADMIN_ROLE_ID}>"
        owner_mention = f"<@{LOG_USER_ID}>"
        
        embed = discord.Embed(title="# 🐬 WELCOME 🐬", color=0x2ecc71)
        embed.description = (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "# 🐳┆YOUR INFO:\n"
            f"ㆍ*Name*: {member.mention}\n"
            f"ㆍ*User*: {member.name}\n"
            f"ㆍ*ID*: {member.id}\n"
            f"ㆍ*Ngày tạo*: {member.created_at.strftime('%d-%m-%Y')}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "# 🐳┆PAWPAW'S STORE:\n"
            f"ㆍChào mừng cậu đã đến với {guild.name}!\n"
            f"ㆍCậu là thành viên thứ {guild.member_count} của {guild.name}\n"
            f"ㆍNếu thắc mắc, liên hệ {admin_mention} và {owner_mention}.\n\n"
            "✨✨GOOD DAYY✨✨"
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url=WELCOME_GIF_URL)
        embed.set_footer(text=now.strftime('%H:%M:%S | %d-%m-%Y'))
        await channel.send(embed=embed)
    
    async def on_member_remove(self, member):
        channel = self.get_channel(GOODBYE_CHANNEL_ID)
        if not channel:
            return
        
        now = datetime.now()
        guild = member.guild
        
        embed = discord.Embed(
            title="😢 TẠM BIỆT",
            description=f"**{member.mention}** đã rời server!\n\n"
                       f"👋 Tạm biệt **{member.display_name}**\n"
                       f"💔 Server còn **{guild.member_count}** thành viên",
            color=0xe74c3c
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url=GOOBBYE_URL)
        embed.set_footer(text=now.strftime('%H:%M:%S | %d-%m-%Y'))
        await channel.send(embed=embed)

# ===== SLASH COMMANDS =====
@discord.app_commands.Command(
    name="tattimmap",
    description="⏸️ Tạm dừng quét server Divaz"
)
async def tattimmap_cmd(interaction: discord.Interaction):
    global scan_active
    if not is_admin(interaction.user):
        return await interaction.response.send_message("❌ Chỉ admin mới dùng được lệnh này!", ephemeral=True)
    
    scan_active = False
    await interaction.response.send_message("⏸️ Đã **tắt** quét map Divaz!", ephemeral=True)

@discord.app_commands.Command(
    name="battimmap",
    description="▶️ Bật lại quét server Divaz"
)
async def battimmap_cmd(interaction: discord.Interaction):
    global scan_active
    if not is_admin(interaction.user):
        return await interaction.response.send_message("❌ Chỉ admin mới dùng được lệnh này!", ephemeral=True)
    
    scan_active = True
    await interaction.response.send_message("▶️ Đã **bật** quét map Divaz!", ephemeral=True)

# ===== CHẠY =====
if __name__ == '__main__':
    t = threading.Thread(target=run_web)
    t.start()
    print("🌐 Web server port 8080")
    
    bot = Bot()
    bot.run(TOKEN)
