import discord
from discord.ext import tasks
from discord import app_commands
import requests
import time
import urllib3
import warnings
import logging
import re
import random
from datetime import datetime, timezone, timedelta
from flask import Flask
import threading
import os

# ===== ĐẶT MÚI GIỜ VIỆT NAM =====
os.environ['TZ'] = 'Asia/Ho_Chi_Minh'
try:
    time.tzset()
except:
    pass

def gio_vn():
    return datetime.now(timezone(timedelta(hours=7)))

# ===== TẮT NHẬT KÝ =====
urllib3.disable_warnings()
warnings.filterwarnings("ignore")
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("discord").setLevel(logging.WARNING)

# ===== MÁY CHỦ WEB FLASK =====
ung_dung = Flask(__name__)

@ung_dung.route('/')
def trang_chu():
    return "Bot đang chạy!"

def chay_may_chu_web():
    ung_dung.run(host='0.0.0.0', port=8080)

# ===== CẤU HÌNH =====
MA_BOT = os.getenv('DISCORD_TOKEN')

ID_MAY_CHU = 1509102064784117821
ID_KENH_KIEM_TRA = 1523606725318676532
ID_KENH_DON = 1523604635816820856
ID_DANH_MUC_DON = 1523595672861933569
ID_QUAN_TRI = 1511311539896979466
ID_DIEU_HANH = 1523739463610536217
ID_VIP = 1523974551879417917
ID_NGUOI_NHAN_LOG = 1507006947755430069
ID_KENH_CHAO_MUNG = 1523598483632947281
ID_KENH_TAM_BIET = 1523602359605919746

# MÁY QUÉT DIVAZ
ID_KENH_QUET = 1523707366280003594
ID_MAP = "88323040672117"

# PHẢN ỨNG NHẬN VAI TRÒ
ID_KENH_PHAN_UNG = 1523970421819572345
ID_VAI_TRO_PHAN_UNG = 1523599853882703882

# EVENT
KENH_EVENT_ID = 1523605458068181083
KENH_KET_QUA_ID = 1523605663064915978

# EMOJI
EMOJI_CANH1 = "✨"
EMOJI_CANH2 = "✨"
EMOJI_BLINK2 = "✨"
EMOJI_BLINKK = "🔹"
EMOJI_TRON = "🔹"
EMOJI_COIN = "💰"
BIEU_TUONG_PHAN_UNG = "✅"

# ẢNH
ANH_GIF = "https://cdn.discordapp.com/attachments/1524068633255481387/1524080452049305713/da685c21e4f555bad69f52593c221dc7.gif"
ANH_CHAO_MUNG = "https://i.postimg.cc/sDh8Xcyp/a9e9538574064d128b604f643392d84b.gif"
ANH_TAM_BIET = "https://cdn.discordapp.com/attachments/1524068633255481387/1524068815518961825/c19d6274e1fd53c5ca46cdafccb4cbc9.gif"
ANH_NHO = "https://huyhieu08.online/uploads/20260707_054705_91412ed7.png"
ANH_LON = "https://i.postimg.cc/V6CFtBL0/no-Filter.webp"

# BIẾN TOÀN CỤC
dem_don = 0
dang_quet = True
id_tin_nhan_phan_ung = None
cac_map_da_gui = set()

# BIẾN EVENT
event_active = False
cho_phep_tham_gia = True
nguoi_tham_gia = {}
msg_event = None
so_event = 1

# ===== NẠP EMOJI =====
def nap_emoji_tu_may_chu(bot):
    global EMOJI_CANH1, EMOJI_CANH2, EMOJI_BLINK2, EMOJI_BLINKK, EMOJI_TRON, EMOJI_COIN, BIEU_TUONG_PHAN_UNG
    
    may_chu = bot.get_guild(ID_MAY_CHU)
    if not may_chu:
        return
    
    for emoji in may_chu.emojis:
        if emoji.name == "canh1": EMOJI_CANH1 = str(emoji)
        elif emoji.name == "canh2": EMOJI_CANH2 = str(emoji)
        elif emoji.name == "blink2": EMOJI_BLINK2 = str(emoji)
        elif emoji.name == "blinkk": EMOJI_BLINKK = str(emoji)
        elif emoji.name == "tron": EMOJI_TRON = str(emoji)
        elif emoji.name == "xu": EMOJI_COIN = str(emoji)
        elif emoji.name == "baibien": BIEU_TUONG_PHAN_UNG = str(emoji)

# ===== HÀM TIỆN ÍCH =====
def lam_tron_the(ngan_hang):
    the_tho = ngan_hang * 1.15 + 10000
    phan_du = the_tho % 10000
    if phan_du >= 5000:
        return ((the_tho // 10000) + 1) * 10000
    return (the_tho // 10000) * 10000

def lam_tron_ngan_hang(ngan_hang):
    return int(round(ngan_hang / 1000) * 1000)

def la_quan_tri(thanh_vien: discord.Member):
    return any(vai_tro.id == ID_QUAN_TRI for vai_tro in thanh_vien.roles)

def la_quan_tri_hoac_dieu_hanh(thanh_vien: discord.Member):
    return any(vai_tro.id in [ID_QUAN_TRI, ID_DIEU_HANH] for vai_tro in thanh_vien.roles)

def la_vip(thanh_vien: discord.Member):
    return any(vai_tro.id == ID_VIP for vai_tro in thanh_vien.roles)

def tinh_giam_gia(so_tien, thanh_vien):
    if la_vip(thanh_vien): return int(so_tien * 0.97)
    return so_tien

def dinh_dang_gia(gia_goc, gia_giam, la_vip):
    if la_vip and gia_giam != gia_goc:
        return f"**{gia_giam:,}** VND ~~{gia_goc:,} VND~~ (VIP)"
    return f"**{gia_goc:,}** VND"

async def gui_nhat_ky_don(bot, so_don, id_nguoi_tao, nguoi_dong, loai_dich_vu, ly_do="Không"):
    bay_gio = gio_vn()
    nguoi_nhan = bot.get_user(ID_NGUOI_NHAN_LOG) or await bot.fetch_user(ID_NGUOI_NHAN_LOG)
    bang_log = discord.Embed(title=f"# Đơn số {so_don}", color=0x3498db)
    bang_log.add_field(name="🧑‍🦱 Người mở đơn:", value=f"<@{id_nguoi_tao}>" if id_nguoi_tao else "Không xác định", inline=False)
    bang_log.add_field(name="🧑‍🦱 Người đóng đơn:", value=nguoi_dong, inline=False)
    bang_log.add_field(name="🔖 Dịch vụ:", value=loai_dich_vu, inline=False)
    bang_log.add_field(name="⏰ Thời gian đóng:", value=bay_gio.strftime('%H:%M:%S | %d - %m - %Y'), inline=False)
    bang_log.add_field(name="📝 Lí do:", value=ly_do, inline=False)
    try: await nguoi_nhan.send(embed=bang_log)
    except: pass

# ===== MODALS =====
class BangKiemTraTien(discord.ui.Modal, title="Kiểm tra giá tiền"):
    so_luong = discord.ui.TextInput(label="Nhập số tiền", placeholder="Ví dụ: 100000 (TIỀN)", required=True, max_length=20)
    
    async def on_submit(self, tuong_tac: discord.Interaction):
        try: tien = int(self.so_luong.value.replace(",", "").replace(".", ""))
        except ValueError: return await tuong_tac.response.send_message("❌ Vui lòng chỉ nhập số.", ephemeral=True)
        
        ngan_hang_goc = lam_tron_ngan_hang(int(tien * 0.12))
        the_goc = lam_tron_the(ngan_hang_goc)
        ngan_hang_giam = tinh_giam_gia(ngan_hang_goc, tuong_tac.user)
        the_giam = tinh_giam_gia(the_goc, tuong_tac.user)
        vip = la_vip(tuong_tac.user)
        bay_gio = gio_vn()
        
        bang = discord.Embed(title=f"{EMOJI_COIN} GIÁ CÀY TIỀN HIỆN TẠI {EMOJI_COIN}", color=0x3498db)
        mo_ta = (
            "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{EMOJI_COIN}ㆍ**Số tiền cần cày:** **{tien:,} TIỀN**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{EMOJI_COIN}ㆍ**Chuyển khoản (Bank):** {dinh_dang_gia(ngan_hang_goc, ngan_hang_giam, vip)}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{EMOJI_COIN}ㆍ**Thẻ cào (Card):** {dinh_dang_gia(the_goc, the_giam, vip)}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        if vip: mo_ta += f"\n👑 {tuong_tac.user.mention}, bạn là **Thành viên VIP** nên được giảm **3%**!\n"
        mo_ta += "\n‼️ **ÁP MÃ GIẢM GIÁ SẼ ĐƯỢC GIẢM TÙY THEO MÃ** ‼️"
        bang.description = mo_ta
        bang.set_image(url=ANH_GIF)
        bang.set_footer(text=f"{bay_gio.strftime('%H:%M:%S | %d-%m-%Y')} | {tuong_tac.user.display_name}")
        await tuong_tac.response.send_message(embed=bang, ephemeral=True)

class BangKiemTraSlay(discord.ui.Modal, title="Kiểm tra giá slay"):
    so_luong = discord.ui.TextInput(label="Nhập số slay", placeholder="Ví dụ: 2000 (SLAY)", required=True, max_length=20)
    
    async def on_submit(self, tuong_tac: discord.Interaction):
        try: slay = int(self.so_luong.value.replace(",", "").replace(".", ""))
        except ValueError: return await tuong_tac.response.send_message("❌ Vui lòng chỉ nhập số.", ephemeral=True)
        
        ngan_hang_goc = lam_tron_ngan_hang(int(slay * 25))
        vip = la_vip(tuong_tac.user)
        if ngan_hang_goc > 8000:
            the_goc = lam_tron_the(ngan_hang_goc)
            the_giam = tinh_giam_gia(the_goc, tuong_tac.user)
            chuoi_the = dinh_dang_gia(the_goc, the_giam, vip)
        else: chuoi_the = "Chỉ nhận thẻ từ 400 SLAY trở lên!"
        ngan_hang_giam = tinh_giam_gia(ngan_hang_goc, tuong_tac.user)
        bay_gio = gio_vn()
        
        bang = discord.Embed(title=f"{EMOJI_COIN} GIÁ CÀY SLAY HIỆN TẠI {EMOJI_COIN}", color=0x3498db)
        mo_ta = (
            "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{EMOJI_COIN}ㆍ**Số slay cần cày:** **{slay:,} SLAY**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{EMOJI_COIN}ㆍ**Chuyển khoản (Bank):** {dinh_dang_gia(ngan_hang_goc, ngan_hang_giam, vip)}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{EMOJI_COIN}ㆍ**Thẻ cào (Card):** {chuoi_the}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        if vip: mo_ta += f"\n👑 {tuong_tac.user.mention}, bạn là **Thành viên VIP** nên được giảm **3%**!\n"
        mo_ta += "\n‼️ **ÁP MÃ GIẢM GIÁ SẼ ĐƯỢC GIẢM TÙY THEO MÃ** ‼️"
        bang.description = mo_ta
        bang.set_image(url=ANH_GIF)
        bang.set_footer(text=f"{bay_gio.strftime('%H:%M:%S | %d-%m-%Y')} | {tuong_tac.user.display_name}")
        await tuong_tac.response.send_message(embed=bang, ephemeral=True)

class BangVndSangTien(discord.ui.Modal, title="VND → Tiền cần cày"):
    so_luong = discord.ui.TextInput(label="Nhập số tiền VND bạn muốn trả", placeholder="Ví dụ: 50000", required=True, max_length=20)
    
    async def on_submit(self, tuong_tac: discord.Interaction):
        try: vnd = int(self.so_luong.value.replace(",", "").replace(".", ""))
        except ValueError: return await tuong_tac.response.send_message("❌ Vui lòng chỉ nhập số.", ephemeral=True)
        
        vnd_sau_giam = tinh_giam_gia(vnd, tuong_tac.user)
        tien_nhan = int(vnd_sau_giam / 0.12)
        ngan_hang_goc = lam_tron_ngan_hang(vnd)
        ngan_hang_giam = tinh_giam_gia(ngan_hang_goc, tuong_tac.user)
        the_goc = lam_tron_the(ngan_hang_goc)
        the_giam = tinh_giam_gia(the_goc, tuong_tac.user)
        vip = la_vip(tuong_tac.user)
        bay_gio = gio_vn()
        
        bang = discord.Embed(title=f"{EMOJI_COIN} SỐ TIỀN CÀY BẠN NHẬN ĐƯỢC {EMOJI_COIN}", color=0xe67e22)
        mo_ta = (
            "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{EMOJI_COIN}ㆍ**Số VND bạn trả:** **{vnd:,} VND**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{EMOJI_COIN}ㆍ**Số tiền cày bạn nhận được:** **{tien_nhan:,} TIỀN**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{EMOJI_COIN}ㆍ**Thẻ cào (Card):** {dinh_dang_gia(the_goc, the_giam, vip)}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        if vip: mo_ta += f"\n👑 {tuong_tac.user.mention}, bạn là **Thành viên VIP** nên được giảm **3%**!\n"
        mo_ta += "\n‼️ **ÁP MÃ GIẢM GIÁ SẼ ĐƯỢC GIẢM TÙY THEO MÃ** ‼️"
        bang.description = mo_ta
        bang.set_image(url=ANH_GIF)
        bang.set_footer(text=f"{bay_gio.strftime('%H:%M:%S | %d-%m-%Y')} | {tuong_tac.user.display_name}")
        await tuong_tac.response.send_message(embed=bang, ephemeral=True)

class BangVndSangSlay(discord.ui.Modal, title="VND → Slay"):
    so_luong = discord.ui.TextInput(label="Nhập số tiền VND bạn muốn trả", placeholder="Ví dụ: 50000", required=True, max_length=20)
    
    async def on_submit(self, tuong_tac: discord.Interaction):
        try: vnd = int(self.so_luong.value.replace(",", "").replace(".", ""))
        except ValueError: return await tuong_tac.response.send_message("❌ Vui lòng chỉ nhập số.", ephemeral=True)
        
        vnd_sau_giam = tinh_giam_gia(vnd, tuong_tac.user)
        slay = int(vnd_sau_giam / 25)
        ngan_hang_goc = lam_tron_ngan_hang(vnd)
        ngan_hang_giam = tinh_giam_gia(ngan_hang_goc, tuong_tac.user)
        vip = la_vip(tuong_tac.user)
        if ngan_hang_goc > 8000:
            the_goc = lam_tron_the(ngan_hang_goc)
            the_giam = tinh_giam_gia(the_goc, tuong_tac.user)
            chuoi_the = dinh_dang_gia(the_goc, the_giam, vip)
        else: chuoi_the = "Chỉ nhận thẻ từ 400 SLAY trở lên!"
        bay_gio = gio_vn()
        
        bang = discord.Embed(title="💅 SỐ SLAY BẠN NHẬN ĐƯỢC 💅", color=0x9b59b6)
        mo_ta = (
            "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💳ㆍ**Số VND bạn trả:** **{vnd:,} VND**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💅ㆍ**Số slay bạn nhận được:** **{slay:,} SLAY**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔖ㆍ**Thẻ cào (Card):** {chuoi_the}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        if vip: mo_ta += f"\n👑 {tuong_tac.user.mention}, bạn là **Thành viên VIP** nên được giảm **3%**!\n"
        mo_ta += "\n‼️ **ÁP MÃ GIẢM GIÁ SẼ ĐƯỢC GIẢM TÙY THEO MÃ** ‼️"
        bang.description = mo_ta
        bang.set_image(url=ANH_GIF)
        bang.set_footer(text=f"{bay_gio.strftime('%H:%M:%S | %d-%m-%Y')} | {tuong_tac.user.display_name}")
        await tuong_tac.response.send_message(embed=bang, ephemeral=True)

class BangTaoDon(discord.ui.Modal, title="Tạo đơn"):
    dich_vu = discord.ui.TextInput(label="Bạn muốn cày tiền hay slay (Tiền/Slay):", placeholder="Tiền hoặc Slay", required=True, max_length=10)
    
    async def on_submit(self, tuong_tac: discord.Interaction):
        global dem_don
        loai_dich_vu = self.dich_vu.value
        may_chu = tuong_tac.guild
        nguoi_dung = tuong_tac.user
        
        for kenh in may_chu.channels:
            if kenh.name.startswith("đơn-") and kenh.topic and str(nguoi_dung.id) == kenh.topic:
                return await tuong_tac.response.send_message("❌ Bạn đã tạo đơn!", ephemeral=True)
        
        danh_muc = may_chu.get_channel(ID_DANH_MUC_DON)
        dem_don += 1
        if dem_don > 999: dem_don = 1
        
        so_don = f"{dem_don:03d}"
        bay_gio = gio_vn()
        ten_an_toan = nguoi_dung.display_name.replace(" ", "-")[:20]
        ten_kenh = f"đơn-{so_don}-{ten_an_toan}-{bay_gio.strftime('%H-%M')}"
        
        phan_quyen = {
            may_chu.default_role: discord.PermissionOverwrite(view_channel=False),
            nguoi_dung: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            may_chu.me: discord.PermissionOverwrite(view_channel=True),
        }
        
        kenh = await may_chu.create_text_channel(name=ten_kenh, category=danh_muc, overwrites=phan_quyen, topic=f"{nguoi_dung.id}|{loai_dich_vu}")
        nhac_quan_tri = f"<@&{ID_QUAN_TRI}>"
        await kenh.send(
            content=f"{nguoi_dung.mention} {nhac_quan_tri}",
            embed=discord.Embed(title="🎫 CÓ ĐƠN", description=f"Đơn số: **{so_don}**\nDịch vụ: **{loai_dich_vu}**\nNgười tạo: {nguoi_dung.mention}\nChờ admin rep nhé💞", color=0x3498db),
            view=DieuKhienDon()
        )
        await tuong_tac.response.send_message(f"✅ Tạo đơn: {kenh.mention}", ephemeral=True)

class BangLyDoDong(discord.ui.Modal, title="Đóng đơn - lý do"):
    ly_do = discord.ui.TextInput(label="Lý do", required=True)
    
    async def on_submit(self, tuong_tac: discord.Interaction):
        ten_kenh = tuong_tac.channel.name
        phan = ten_kenh.split("-")
        so_don = phan[1] if len(phan) > 1 else "???"
        du_lieu_chu_de = tuong_tac.channel.topic
        if du_lieu_chu_de and "|" in du_lieu_chu_de:
            id_nguoi_tao, loai_dich_vu = du_lieu_chu_de.split("|", 1)
        else: id_nguoi_tao = du_lieu_chu_de; loai_dich_vu = "Không xác định"
        await gui_nhat_ky_don(tuong_tac.client, so_don, id_nguoi_tao, tuong_tac.user.mention, loai_dich_vu, self.ly_do.value)
        await tuong_tac.channel.delete()

# ===== EVENT MODALS =====
class FormThamGia(discord.ui.Modal, title="Đăng ký tham gia"):
    username = discord.ui.TextInput(label="Username Roblox của bạn", placeholder="Nhập username Roblox", required=True, max_length=50)
    
    async def on_submit(self, tuong_tac: discord.Interaction):
        global nguoi_tham_gia, msg_event
        if not event_active: return await tuong_tac.response.send_message("❌ Event chưa bắt đầu!", ephemeral=True)
        if not cho_phep_tham_gia: return await tuong_tac.response.send_message("❌ Đã dừng tham gia!", ephemeral=True)
        if tuong_tac.user.id in nguoi_tham_gia: return await tuong_tac.response.send_message("❌ Bạn đã tham gia rồi!", ephemeral=True)
        nguoi_tham_gia[tuong_tac.user.id] = self.username.value
        await cap_nhat_event()
        await tuong_tac.response.send_message(f"✅ Đã đăng ký: **{self.username.value}**", ephemeral=True)

async def cap_nhat_event():
    global msg_event
    if not msg_event: return
    ds_text = ""
    if nguoi_tham_gia:
        for i, (uid, uname) in enumerate(nguoi_tham_gia.items(), 1):
            ds_text += f"**{i}.** **{uname}** (<@{uid}>)\n"
    else: ds_text = "Chưa có ai tham gia!"
    trang_thai = "✅ ĐANG MỞ" if cho_phep_tham_gia else "⏸️ ĐÃ DỪNG"
    embed = discord.Embed(
        title="⚔️ EVENT DIVAZ ĐẤU 1VS1 ⚔️",
        description=f"ㆍCó **{len(nguoi_tham_gia)}** đã tham gia.\nㆍTrạng thái: **{trang_thai}**\n\nㆍNhấn '💅Tham gia' bên dưới.",
        color=0xff0000
    )
    embed.add_field(name="📋 DANH SÁCH:", value=ds_text, inline=False)
    embed.set_footer(text="BotByPawPaw")
    await msg_event.edit(embed=embed)

# ===== EVENT VIEWS =====
class NutXacNhanBatDau(discord.ui.View):
    def __init__(self): super().__init__(timeout=30)
    @discord.ui.button(label="✅ Xác nhận", style=discord.ButtonStyle.green)
    async def xac_nhan(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        if not la_quan_tri(tuong_tac): return await tuong_tac.response.send_message("❌ Chỉ Admin!", ephemeral=True)
        await bat_dau_event(tuong_tac)
        try: await tuong_tac.message.delete()
        except: pass
    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.red)
    async def huy(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        try: await tuong_tac.message.delete()
        except: pass

class NutXacNhanDungThamGia(discord.ui.View):
    def __init__(self): super().__init__(timeout=30)
    @discord.ui.button(label="✅ Xác nhận", style=discord.ButtonStyle.red)
    async def xac_nhan(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        global cho_phep_tham_gia
        cho_phep_tham_gia = False
        await cap_nhat_event()
        try: await tuong_tac.message.delete()
        except: pass
    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.grey)
    async def huy(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        try: await tuong_tac.message.delete()
        except: pass

class NutEventChinh(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="💅 Tham gia", style=discord.ButtonStyle.green, custom_id="tham_gia_event")
    async def tham_gia(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        if not event_active: return await tuong_tac.response.send_message("❌ Event chưa bắt đầu!", ephemeral=True)
        if not cho_phep_tham_gia: return await tuong_tac.response.send_message("❌ Đã dừng!", ephemeral=True)
        await tuong_tac.response.send_modal(FormThamGia())
    @discord.ui.button(label="💅 Bắt đầu", style=discord.ButtonStyle.green, custom_id="bat_dau_event")
    async def bat_dau(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        if not la_quan_tri(tuong_tac): return await tuong_tac.response.send_message("❌ Chỉ Admin!", ephemeral=True)
        if len(nguoi_tham_gia) < 2: return await tuong_tac.response.send_message("❌ Cần ít nhất 2 người!", ephemeral=True)
        await tuong_tac.response.send_message(f"⚠️ **Xác nhận bắt đầu với {len(nguoi_tham_gia)} người?**", view=NutXacNhanBatDau(), ephemeral=True)
    @discord.ui.button(label="🚪 Rời Event", style=discord.ButtonStyle.red, custom_id="roi_event")
    async def roi_event(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        global nguoi_tham_gia
        if not event_active: return await tuong_tac.response.send_message("❌ Event chưa bắt đầu!", ephemeral=True)
        if tuong_tac.user.id not in nguoi_tham_gia: return await tuong_tac.response.send_message("❌ Bạn chưa tham gia!", ephemeral=True)
        del nguoi_tham_gia[tuong_tac.user.id]
        await cap_nhat_event()
        await tuong_tac.response.send_message("✅ Đã rời!", ephemeral=True)
    @discord.ui.button(label="⏸️ Dừng tham gia", style=discord.ButtonStyle.red, custom_id="dung_tham_gia")
    async def dung_tham_gia(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        if not la_quan_tri(tuong_tac): return await tuong_tac.response.send_message("❌ Chỉ Admin!", ephemeral=True)
        await tuong_tac.response.send_message("⚠️ **Xác nhận dừng?**", view=NutXacNhanDungThamGia(), ephemeral=True)

class NutChonThangVong(discord.ui.View):
    def __init__(self, uid1, uid2, so_vong, tran_so):
        super().__init__(timeout=600)
        self.uid1 = uid1; self.uid2 = uid2; self.so_vong = so_vong; self.tran_so = tran_so; self.da_chon = False
        ten1 = "ADMIN/MOD" if uid1 == "admin" else nguoi_tham_gia.get(uid1, "Unknown")
        ten2 = "ADMIN/MOD" if uid2 == "admin" else nguoi_tham_gia.get(uid2, "Unknown")
        nut1 = discord.ui.Button(label=f"🏆 {ten1}", style=discord.ButtonStyle.green); nut1.callback = self.chon1; self.add_item(nut1)
        nut2 = discord.ui.Button(label=f"🏆 {ten2}", style=discord.ButtonStyle.blurple); nut2.callback = self.chon2; self.add_item(nut2)
    
    async def chon1(self, tuong_tac: discord.Interaction):
        if not la_quan_tri(tuong_tac): return await tuong_tac.response.send_message("❌ Chỉ Admin!", ephemeral=True)
        if self.da_chon: return await tuong_tac.response.send_message("❌ Đã chọn!", ephemeral=True)
        await self.xu_ly(tuong_tac, self.uid1)
    
    async def chon2(self, tuong_tac: discord.Interaction):
        if not la_quan_tri(tuong_tac): return await tuong_tac.response.send_message("❌ Chỉ Admin!", ephemeral=True)
        if self.da_chon: return await tuong_tac.response.send_message("❌ Đã chọn!", ephemeral=True)
        await self.xu_ly(tuong_tac, self.uid2)
    
    async def xu_ly(self, tuong_tac, uid_thang):
        self.da_chon = True
        for child in self.children: child.disabled = True
        await tuong_tac.message.edit(view=self)
        await gui_ket_qua(uid_thang)
        await tuong_tac.response.send_message(f"✅ Đã ghi nhận Trận {self.tran_so}!", ephemeral=True)

async def gui_ket_qua(uid_thang):
    global so_event
    kenh_ket_qua = bot.get_channel(KENH_KET_QUA_ID) if hasattr(bot, 'get_channel') else None
    if not kenh_ket_qua: return
    ten_roblox = "ADMIN/MOD" if uid_thang == "admin" else nguoi_tham_gia.get(uid_thang, "Unknown")
    now = gio_vn()
    embed = discord.Embed(title="🎉 CONGRATULATIONS", description=f"<@{uid_thang}> **WIN IN EVENT {so_event}**", color=0xffd700)
    embed.add_field(name="🎮 **UserGame:**", value=f"```{ten_roblox}```", inline=False)
    embed.add_field(name="⏰ **Time:**", value=now.strftime('%H:%M:%S | %d/%m/%Y'), inline=False)
    embed.set_footer(text="BotByPawPaw")
    await kenh_ket_qua.send(embed=embed)

async def bat_dau_event(tuong_tac):
    global cho_phep_tham_gia
    cho_phep_tham_gia = False
    view_rong = discord.ui.View()
    await msg_event.edit(view=view_rong)
    await cap_nhat_event()
    ds_nguoi = list(nguoi_tham_gia.keys())
    await gui_vong(tuong_tac.channel, 1, ds_nguoi)

async def gui_vong(kenh, so_vong, ds_nguoi):
    random.shuffle(ds_nguoi)
    ds_copy = ds_nguoi.copy()
    if len(ds_copy) % 2 != 0: ds_copy.append("admin")
    cac_tran = [(ds_copy[i], ds_copy[i+1]) for i in range(0, len(ds_copy), 2)]
    tong_so_tran = len(cac_tran)
    await kenh.send(f"# 🔥 **VÒNG {so_vong}** 🔥\n📊 **{len(ds_nguoi)} người** → **{tong_so_tran} trận**")
    for i, (u1, u2) in enumerate(cac_tran, 1):
        ten1 = "ADMIN/MOD" if u1 == "admin" else nguoi_tham_gia.get(u1, "Unknown")
        ten2 = "ADMIN/MOD" if u2 == "admin" else nguoi_tham_gia.get(u2, "Unknown")
        embed = discord.Embed(title=f"🥊 TRẬN {i}:", description=f"```{ten1}``` **VS** ```{ten2}```", color=0xffaa00)
        embed.set_footer(text=f"Vòng {so_vong} • Trận {i}/{tong_so_tran}")
        await kenh.send(embed=embed, view=NutChonThangVong(u1, u2, so_vong, i))

# ===== VIEWS KHÁC =====
class XacNhanDongDon(discord.ui.View):
    def __init__(self, kenh, so_don, id_nguoi_tao, loai_dich_vu):
        super().__init__(timeout=30)
        self.kenh = kenh; self.so_don = so_don; self.id_nguoi_tao = id_nguoi_tao; self.loai_dich_vu = loai_dich_vu
    @discord.ui.button(label="✅ Xác nhận đóng", style=discord.ButtonStyle.red)
    async def xac_nhan(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        if not la_quan_tri_hoac_dieu_hanh(tuong_tac.user): return await tuong_tac.response.send_message("❌ Chỉ Quản trị/Điều hành!", ephemeral=True)
        await tuong_tac.response.send_message("🔒 Đang đóng...", ephemeral=True)
        await gui_nhat_ky_don(tuong_tac.client, self.so_don, self.id_nguoi_tao, tuong_tac.user.mention, self.loai_dich_vu)
        await self.kenh.delete()
    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.grey)
    async def huy(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        if not la_quan_tri_hoac_dieu_hanh(tuong_tac.user): return await tuong_tac.response.send_message("❌ Chỉ Quản trị/Điều hành!", ephemeral=True)
        await tuong_tac.message.delete()
        await tuong_tac.response.send_message("❌ Đã hủy!", ephemeral=True)

class BinhChonHoanThanh(discord.ui.View):
    def __init__(self, kenh, so_don, id_nguoi_tao, loai_dich_vu):
        super().__init__(timeout=120)
        self.kenh = kenh; self.so_don = so_don; self.id_nguoi_tao = id_nguoi_tao; self.loai_dich_vu = loai_dich_vu
        self.nguoi_bau = set(); self.da_co_admin = False; self.da_co_nguoi_tao = False
    @discord.ui.button(label="✅ Hoàn thành đơn", style=discord.ButtonStyle.green)
    async def hoan_thanh(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        nguoi_dung = tuong_tac.user
        la_admin = la_quan_tri_hoac_dieu_hanh(nguoi_dung)
        la_nguoi_tao = str(nguoi_dung.id) == str(self.id_nguoi_tao)
        if not la_admin and not la_nguoi_tao: return await tuong_tac.response.send_message("❌ Không có quyền!", ephemeral=True)
        if nguoi_dung.id in self.nguoi_bau: return await tuong_tac.response.send_message("❌ Đã bấm rồi!", ephemeral=True)
        self.nguoi_bau.add(nguoi_dung.id)
        if la_admin: self.da_co_admin = True
        if la_nguoi_tao: self.da_co_nguoi_tao = True
        if self.da_co_admin and self.da_co_nguoi_tao:
            await tuong_tac.response.send_message("✅ Hoàn thành! Đang đóng...", ephemeral=True)
            await gui_nhat_ky_don(tuong_tac.client, self.so_don, self.id_nguoi_tao, tuong_tac.user.mention, self.loai_dich_vu, "Đơn đã hoàn thành")
            await self.kenh.delete()
        else:
            con_thieu = []
            if not self.da_co_admin: con_thieu.append("**Quản trị/Điều hành**")
            if not self.da_co_nguoi_tao: con_thieu.append("**Người tạo đơn**")
            await tuong_tac.response.send_message(f"✅ Cần thêm {' và '.join(con_thieu)}!", ephemeral=True)
    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.grey)
    async def huy(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        if not la_quan_tri_hoac_dieu_hanh(tuong_tac.user) and str(tuong_tac.user.id) != str(self.id_nguoi_tao):
            return await tuong_tac.response.send_message("❌ Không có quyền!", ephemeral=True)
        await tuong_tac.message.delete(); await tuong_tac.response.send_message("❌ Đã hủy!", ephemeral=True)

class DieuKhienDon(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🔒 Đóng đơn", style=discord.ButtonStyle.red, custom_id="dong_don")
    async def dong(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        if not la_quan_tri_hoac_dieu_hanh(tuong_tac.user): return await tuong_tac.response.send_message("❌ Chỉ Quản trị/Điều hành!", ephemeral=True)
        ten_kenh = tuong_tac.channel.name; phan = ten_kenh.split("-"); so_don = phan[1] if len(phan) > 1 else "???"
        du_lieu_chu_de = tuong_tac.channel.topic
        if du_lieu_chu_de and "|" in du_lieu_chu_de: id_nguoi_tao, loai_dich_vu = du_lieu_chu_de.split("|", 1)
        else: id_nguoi_tao = du_lieu_chu_de; loai_dich_vu = "Không xác định"
        bang = discord.Embed(title="⚠️ XÁC NHẬN", description=f"Đóng đơn **#{so_don}**?", color=0xff0000)
        await tuong_tac.response.send_message(embed=bang, view=XacNhanDongDon(tuong_tac.channel, so_don, id_nguoi_tao, loai_dich_vu))
    @discord.ui.button(label="✅ Hoàn thành đơn", style=discord.ButtonStyle.green, custom_id="hoan_thanh_don")
    async def hoan_thanh(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        nguoi_dung = tuong_tac.user
        ten_kenh = tuong_tac.channel.name; phan = ten_kenh.split("-"); so_don = phan[1] if len(phan) > 1 else "???"
        du_lieu_chu_de = tuong_tac.channel.topic
        if du_lieu_chu_de and "|" in du_lieu_chu_de: id_nguoi_tao, loai_dich_vu = du_lieu_chu_de.split("|", 1)
        else: id_nguoi_tao = du_lieu_chu_de; loai_dich_vu = "Không xác định"
        la_admin = la_quan_tri_hoac_dieu_hanh(nguoi_dung); la_nguoi_tao = str(nguoi_dung.id) == str(id_nguoi_tao)
        if not la_admin and not la_nguoi_tao: return await tuong_tac.response.send_message("❌ Không có quyền!", ephemeral=True)
        bang = discord.Embed(title="✅ HOÀN THÀNH ĐƠN", description=f"Cần Quản trị/Điều hành VÀ Người tạo đơn xác nhận!", color=0x00ff00)
        await tuong_tac.response.send_message(embed=bang, view=BinhChonHoanThanh(tuong_tac.channel, so_don, id_nguoi_tao, loai_dich_vu))
    @discord.ui.button(label="🧾 Đóng đơn kèm lý do", style=discord.ButtonStyle.grey, custom_id="dong_don_ly_do")
    async def dong_ly_do(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        if not la_quan_tri_hoac_dieu_hanh(tuong_tac.user): return await tuong_tac.response.send_message("❌ Chỉ Quản trị/Điều hành!", ephemeral=True)
        await tuong_tac.response.send_modal(BangLyDoDong())

class GiaoDienKiemTraGia(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="💰 Tiền Divaz → VND", style=discord.ButtonStyle.green, custom_id="kiem_tra_tien")
    async def kiem_tra_tien(self, tuong_tac: discord.Interaction, nut: discord.ui.Button): await tuong_tac.response.send_modal(BangKiemTraTien())
    @discord.ui.button(label="💅 Slay → VND", style=discord.ButtonStyle.green, custom_id="kiem_tra_slay")
    async def kiem_tra_slay(self, tuong_tac: discord.Interaction, nut: discord.ui.Button): await tuong_tac.response.send_modal(BangKiemTraSlay())
    @discord.ui.button(label="💵 VND → Tiền cày", style=discord.ButtonStyle.blurple, custom_id="vnd_sang_tien")
    async def vnd_sang_tien(self, tuong_tac: discord.Interaction, nut: discord.ui.Button): await tuong_tac.response.send_modal(BangVndSangTien())
    @discord.ui.button(label="💳 VND → Slay", style=discord.ButtonStyle.blurple, custom_id="vnd_sang_slay")
    async def vnd_sang_slay(self, tuong_tac: discord.Interaction, nut: discord.ui.Button): await tuong_tac.response.send_modal(BangVndSangSlay())

class GiaoDienTaoDon(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🎫 Tạo đơn", style=discord.ButtonStyle.blurple, custom_id="tao_don")
    async def tao(self, tuong_tac: discord.Interaction, nut: discord.ui.Button): await tuong_tac.response.send_modal(BangTaoDon())

class GiaoDienServer(discord.ui.View):
    def __init__(self, may_chu):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.green if may_chu['so_nguoi_choi'] <= 3 else discord.ButtonStyle.blurple, label="THAM GIA", url=f"https://nuxwtghieux.github.io/Snipe/?jobid={may_chu['id_may']}"))

# ===== MÁY QUÉT DIVAZ =====
def quet_divaz():
    ket_qua = []
    con_tro = ""
    tieu_de = {'User-Agent': 'Mozilla/5.0'}
    while True:
        duong_dan = f"https://games.roblox.com/v1/games/{ID_MAP}/servers/Public?limit=100"
        if con_tro: duong_dan += f"&cursor={con_tro}"
        try:
            phan_hoi = requests.get(duong_dan, headers=tieu_de, timeout=15, verify=False)
            if phan_hoi.status_code == 200:
                du_lieu = phan_hoi.json(); cac_may = du_lieu.get('data', [])
                if not cac_may: break
                for may in cac_may:
                    so_nguoi = may.get('playing', 0)
                    if so_nguoi < 5 and may['id'] not in cac_map_da_gui:
                        ket_qua.append({'id_may': may['id'], 'so_nguoi_choi': so_nguoi, 'ping': may.get('ping', 'N/A'), 'fps': may.get('fps', 'N/A'), 'toi_da': may.get('maxPlayers', 'N/A')})
                con_tro = du_lieu.get('nextPageCursor')
                if not con_tro: break
                time.sleep(1)
            else: break
        except: time.sleep(3)
    return ket_qua

# ===== SLASH COMMANDS =====
@discord.app_commands.command(name="tat_tim_map", description="⏸️ Tạm dừng quét server Divaz")
async def lenh_tat_tim_map(tuong_tac: discord.Interaction):
    global dang_quet
    if not la_quan_tri(tuong_tac): return await tuong_tac.response.send_message("❌ Chỉ Quản trị!", ephemeral=True)
    dang_quet = False; await tuong_tac.response.send_message("⏸️ Đã tắt!", ephemeral=True)

@discord.app_commands.command(name="bat_tim_map", description="▶️ Bật lại quét server Divaz")
async def lenh_bat_tim_map(tuong_tac: discord.Interaction):
    global dang_quet
    if not la_quan_tri(tuong_tac): return await tuong_tac.response.send_message("❌ Chỉ Quản trị!", ephemeral=True)
    dang_quet = True; await tuong_tac.response.send_message("▶️ Đã bật!", ephemeral=True)

@discord.app_commands.command(name="startev", description="🎮 Bắt đầu event đấu 1vs1")
async def startev(tuong_tac: discord.Interaction):
    if not la_quan_tri(tuong_tac): return await tuong_tac.response.send_message("❌ Chỉ Quản trị!", ephemeral=True)
    global event_active, nguoi_tham_gia, msg_event, cho_phep_tham_gia, so_event
    so_event += 1; event_active = True; cho_phep_tham_gia = True; nguoi_tham_gia = {}
    kenh = bot.get_channel(KENH_EVENT_ID)
    if not kenh: return await tuong_tac.response.send_message("❌ Không tìm thấy kênh!", ephemeral=True)
    embed = discord.Embed(title="⚔️ EVENT DIVAZ ĐẤU 1VS1 ⚔️", description="ㆍCó **0** đã tham gia.\nㆍTrạng thái: **✅ ĐANG MỞ**\n\nㆍNhấn '💅Tham gia' bên dưới.", color=0xff0000)
    embed.add_field(name="📋 DANH SÁCH:", value="Chưa có ai!", inline=False)
    embed.set_footer(text="BotByPawPaw")
    msg_event = await kenh.send(embed=embed, view=NutEventChinh())
    await tuong_tac.response.send_message("✅ Event đã bắt đầu!", ephemeral=True)

@discord.app_commands.command(name="stopev", description="⏸️ Dừng event")
async def stopev(tuong_tac: discord.Interaction):
    if not la_quan_tri(tuong_tac): return await tuong_tac.response.send_message("❌ Chỉ Quản trị!", ephemeral=True)
    global event_active
    event_active = False; await tuong_tac.response.send_message("✅ Event đã dừng!", ephemeral=True)

# ===== BOT CHÍNH =====
class Bot(discord.Client):
    def __init__(self):
        quyen = discord.Intents.default()
        quyen.guilds = True; quyen.message_content = True; quyen.members = True; quyen.reactions = True
        super().__init__(intents=quyen)
        self.cay = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        may_chu = discord.Object(id=ID_MAY_CHU)
        self.cay.add_command(lenh_tat_tim_map); self.cay.add_command(lenh_bat_tim_map)
        self.cay.add_command(startev); self.cay.add_command(stopev)
        await self.cay.sync(guild=may_chu)
        self.add_view(GiaoDienKiemTraGia()); self.add_view(GiaoDienTaoDon()); self.add_view(DieuKhienDon())
        self.add_view(NutEventChinh())
    
    async def on_ready(self):
        nap_emoji_tu_may_chu(self)
        await self.bang_dieu_khien()
        self.vong_lap_quet.start()
        print(f"🚀 Bot sẵn sàng!")
    
    async def bang_dieu_khien(self):
        kenh_kiem_tra = self.get_channel(ID_KENH_KIEM_TRA)
        if kenh_kiem_tra:
            async for tin in kenh_kiem_tra.history(limit=50):
                if tin.author == self.user: await tin.delete()
            bang = discord.Embed(title="‼️ HƯỚNG DẪN KIỂM TRA GIÁ 📍", description="Nhấn nút bên dưới để check giá!", color=0x3498db)
            bang.set_footer(text=gio_vn().strftime('%H:%M:%S | %d-%m-%Y'))
            await kenh_kiem_tra.send(embed=bang, view=GiaoDienKiemTraGia())
        
        kenh_don = self.get_channel(ID_KENH_DON)
        if kenh_don:
            async for tin in kenh_don.history(limit=50):
                if tin.author == self.user: await tin.delete()
            await kenh_don.send(embed=discord.Embed(title="🛒 DỊCH VỤ", description="Tạo đơn bên dưới!", color=0x3498db), view=GiaoDienTaoDon())
        
        global id_tin_nhan_phan_ung
        kenh_phan_ung = self.get_channel(ID_KENH_PHAN_UNG)
        if kenh_phan_ung:
            tin_nhan_cu = None
            async for tin in kenh_phan_ung.history(limit=50):
                if tin.author == self.user and tin.embeds: tin_nhan_cu = tin; break
            if tin_nhan_cu:
                id_tin_nhan_phan_ung = tin_nhan_cu.id
                try: await tin_nhan_cu.add_reaction(BIEU_TUONG_PHAN_UNG)
                except: pass
            else:
                async for tin in kenh_phan_ung.history(limit=50):
                    if tin.author == self.user: await tin.delete()
                bang = discord.Embed(title="🎭 NHẬN VAI TRÒ", description="✅ **TICK VÀO BÊN DƯỚI ĐỂ XEM KÊNH CHAT ↓**", color=0x9b59b6)
                bang.set_footer(text="BotByPawPaw")
                tn = await kenh_phan_ung.send(embed=bang); await tn.add_reaction(BIEU_TUONG_PHAN_UNG)
                id_tin_nhan_phan_ung = tn.id
    
    @tasks.loop(seconds=180)
    async def vong_lap_quet(self):
        global dang_quet, cac_map_da_gui
        if not dang_quet: return
        kenh = self.get_channel(ID_KENH_QUET)
        if not kenh: return
        cac_may = quet_divaz()
        if cac_may:
            if len(cac_map_da_gui) > 50: cac_map_da_gui.clear()
            tot_nhat = cac_may[0]; so_nguoi = tot_nhat['so_nguoi_choi']; ma = tot_nhat['id_may'][-5:]
            mau_sac = 0x00ff00 if so_nguoi <= 3 else 0xffaa00; bay_gio = gio_vn()
            cac_map_da_gui.add(tot_nhat['id_may'])
            bang = discord.Embed(title="🎮 DIVAZ - MÁY CHỦ TRỐNG", description=f"**Mã:** `#{ma}`", color=mau_sac, timestamp=bay_gio)
            bang.add_field(name="👥 **NGƯỜI CHƠI**", value=f"🟢 {so_nguoi}/{tot_nhat['toi_da']}" if so_nguoi <= 3 else f"🟡 {so_nguoi}/{tot_nhat['toi_da']}", inline=True)
            bang.add_field(name="📶 **PING**", value=f"{tot_nhat['ping']}ms", inline=True)
            bang.add_field(name="🎯 **FPS**", value=f"{tot_nhat['fps']}", inline=True)
            bang.set_thumbnail(url=ANH_NHO); bang.set_image(url=ANH_LON)
            bang.set_footer(text=f"BotByPawPaw • {bay_gio.strftime('%H:%M:%S | %d/%m/%Y')}")
            await kenh.send(embed=bang, view=GiaoDienServer(tot_nhat))
    
    async def on_raw_reaction_add(self, du_lieu):
        global id_tin_nhan_phan_ung
        if du_lieu.message_id != id_tin_nhan_phan_ung: return
        if str(du_lieu.emoji) != BIEU_TUONG_PHAN_UNG: return
        may_chu = self.get_guild(du_lieu.guild_id)
        if not may_chu: return
        thanh_vien = may_chu.get_member(du_lieu.user_id)
        if not thanh_vien or thanh_vien.bot: return
        vai_tro = may_chu.get_role(ID_VAI_TRO_PHAN_UNG)
        if not vai_tro: return
        try: await thanh_vien.add_roles(vai_tro)
        except: pass
    
    async def on_raw_reaction_remove(self, du_lieu):
        global id_tin_nhan_phan_ung
        if du_lieu.message_id != id_tin_nhan_phan_ung: return
        if str(du_lieu.emoji) != BIEU_TUONG_PHAN_UNG: return
        may_chu = self.get_guild(du_lieu.guild_id)
        if not may_chu: return
        thanh_vien = may_chu.get_member(du_lieu.user_id)
        if not thanh_vien or thanh_vien.bot: return
        vai_tro = may_chu.get_role(ID_VAI_TRO_PHAN_UNG)
        if not vai_tro: return
        try: await thanh_vien.remove_roles(vai_tro)
        except: pass
    
    async def on_member_join(self, thanh_vien):
        kenh = self.get_channel(ID_KENH_CHAO_MUNG)
        if not kenh: return
        bay_gio = gio_vn(); may_chu = thanh_vien.guild
        bang = discord.Embed(color=0x2ecc71)
        bang.description = (
            f"# {EMOJI_CANH1} CHÀO MỪNG {EMOJI_CANH2}\n━━━━━━━━━━━━━━\n"
            f"# {EMOJI_TRON} THÔNG TIN:\n{EMOJI_BLINKK} Tên: {thanh_vien.mention}\n{EMOJI_BLINKK} ID: {thanh_vien.id}\n━━━━━━━━━━━━━━\n"
            f"# {EMOJI_TRON} PAWPAW:\n{EMOJI_BLINKK} Member thứ {may_chu.member_count}\n{EMOJI_BLINKK} Vào <#{ID_KENH_PHAN_UNG}> để get role!\n\n{EMOJI_BLINK2}{EMOJI_BLINK2} GOOD DAY {EMOJI_BLINK2}{EMOJI_BLINK2}"
        )
        bang.set_thumbnail(url=thanh_vien.display_avatar.url); bang.set_image(url=ANH_CHAO_MUNG)
        bang.set_footer(text=bay_gio.strftime('%H:%M:%S | %d-%m-%Y'))
        await kenh.send(embed=bang)
    
    async def on_member_remove(self, thanh_vien):
        kenh = self.get_channel(ID_KENH_TAM_BIET)
        if not kenh: return
        bay_gio = gio_vn(); may_chu = thanh_vien.guild
        bang = discord.Embed(title="😢 TẠM BIỆT", description=f"**{thanh_vien.mention}** đã rời!\n💔 Còn **{may_chu.member_count}** thành viên", color=0xe74c3c)
        bang.set_thumbnail(url=thanh_vien.display_avatar.url); bang.set_image(url=ANH_TAM_BIET)
        bang.set_footer(text=bay_gio.strftime('%H:%M:%S | %d-%m-%Y'))
        await kenh.send(embed=bang)

# ===== CHẠY =====
bot = Bot()

if __name__ == '__main__':
    luong = threading.Thread(target=chay_may_chu_web)
    luong.start()
    print("🌐 Web port 8080")
    bot.run(MA_BOT)
