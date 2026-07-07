import discord
from discord.ext import tasks
from discord import app_commands
import requests
import time
import urllib3
import warnings
import logging
import re
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

# EMOJI - SẼ TỰ ĐỘNG NẠP TỪ SERVER
EMOJI_CANH1 = "✨"
EMOJI_CANH2 = "✨"
EMOJI_TRON = "🔹"
EMOJI_COIN = "💰"
BIEU_TUONG_PHAN_UNG = "✅"

# ẢNH
ANH_GIF = "https://cdn.discordapp.com/attachments/1524068633255481387/1524080452049305713/da685c21e4f555bad69f52593c221dc7.gif?ex=6a4e7207&is=6a4d2087&hm=e842d1cb89a17a009dc8355e701312ada2cec098742baaebbc50b670e411b04f&"
ANH_CHAO_MUNG = "https://i.postimg.cc/sDh8Xcyp/a9e9538574064d128b604f643392d84b.gif"
ANH_TAM_BIET = "https://cdn.discordapp.com/attachments/1524068633255481387/1524068815518961825/c19d6274e1fd53c5ca46cdafccb4cbc9.gif?ex=6a4e6731&is=6a4d15b1&hm=08400fdee01197bd79ea4d238de02ae5671f3f79573f6ebf0a7fa83957462ff8&"
ANH_NHO = "https://huyhieu08.online/uploads/20260707_054705_91412ed7.png"
ANH_LON = "https://i.postimg.cc/V6CFtBL0/no-Filter.webp"

dem_don = 0
dang_quet = True
id_tin_nhan_phan_ung = None
cac_map_da_gui = set()

# ===== NẠP EMOJI TỰ ĐỘNG =====
def nap_emoji_tu_may_chu(bot):
    global EMOJI_CANH1, EMOJI_CANH2, EMOJI_TRON, EMOJI_COIN, BIEU_TUONG_PHAN_UNG
    
    may_chu = bot.get_guild(ID_MAY_CHU)
    if not may_chu:
        return
    
    for emoji in may_chu.emojis:
        if emoji.name == "canh1":
            EMOJI_CANH1 = str(emoji)
        elif emoji.name == "canh2":
            EMOJI_CANH2 = str(emoji)
        elif emoji.name == "tron":
            EMOJI_TRON = str(emoji)
        elif emoji.name == "coin":
            EMOJI_COIN = str(emoji)
        elif emoji.name == "baibien":
            BIEU_TUONG_PHAN_UNG = str(emoji)
    
    print(f"✅ Đã nạp emoji: canh1={EMOJI_CANH1}, canh2={EMOJI_CANH2}, tron={EMOJI_TRON}, coin={EMOJI_COIN}, baibien={BIEU_TUONG_PHAN_UNG}")

# ===== CÁC HÀM TIỆN ÍCH =====
def lam_tron_the(ngan_hang):
    the_tho = ngan_hang * 1.15 + 10000
    phan_du = the_tho % 10000
    
    if phan_du >= 5000:
        the_tron = ((the_tho // 10000) + 1) * 10000
    else:
        the_tron = (the_tho // 10000) * 10000
    
    return the_tron

def lam_tron_ngan_hang(ngan_hang):
    return int(round(ngan_hang / 1000) * 1000)

def la_quan_tri(thanh_vien: discord.Member):
    return any(vai_tro.id == ID_QUAN_TRI for vai_tro in thanh_vien.roles)

def la_quan_tri_hoac_dieu_hanh(thanh_vien: discord.Member):
    return any(vai_tro.id in [ID_QUAN_TRI, ID_DIEU_HANH] for vai_tro in thanh_vien.roles)

def la_vip(thanh_vien: discord.Member):
    return any(vai_tro.id == ID_VIP for vai_tro in thanh_vien.roles)

def tinh_giam_gia(so_tien, thanh_vien):
    if la_vip(thanh_vien):
        return int(so_tien * 0.97)
    return so_tien

def dinh_dang_gia(gia_goc, gia_giam, la_vip):
    if la_vip and gia_giam != gia_goc:
        return f"**{gia_giam:,}** VND ~~{gia_goc:,} VND~~ (VIP)"
    return f"**{gia_goc:,}** VND"

async def nap_du_lieu_tu_dm(bot):
    global dem_don, cac_map_da_gui
    
    try:
        nguoi_nhan = bot.get_user(ID_NGUOI_NHAN_LOG) or await bot.fetch_user(ID_NGUOI_NHAN_LOG)
        async for tin_nhan in nguoi_nhan.history(limit=100):
            if tin_nhan.author == bot.user and tin_nhan.embeds:
                bang = tin_nhan.embeds[0]
                
                if bang.title and "Đơn số" in bang.title:
                    ket_qua = re.search(r'Đơn số (\d+)', bang.title)
                    if ket_qua:
                        don_cuoi = int(ket_qua.group(1))
                        if don_cuoi > dem_don:
                            dem_don = don_cuoi
                
                if bang.footer and "MapID:" in (bang.footer.text or ""):
                    map_id = bang.footer.text.split("MapID:")[-1].strip()
                    if map_id:
                        cac_map_da_gui.add(map_id)
                        
        print(f"✅ Khôi phục: {dem_don} đơn, {len(cac_map_da_gui)} map đã gửi")
    except Exception as e:
        print(f"❌ Lỗi đọc DM: {e}")

async def gui_nhat_ky_don(bot, so_don, id_nguoi_tao, nguoi_dong, loai_dich_vu, ly_do="Không"):
    bay_gio = gio_vn()
    nguoi_nhan = bot.get_user(ID_NGUOI_NHAN_LOG) or await bot.fetch_user(ID_NGUOI_NHAN_LOG)
    
    bang_log = discord.Embed(title=f"# Đơn số {so_don}", color=0x3498db)
    bang_log.add_field(name="🧑‍🦱 Người mở đơn:", value=f"<@{id_nguoi_tao}>" if id_nguoi_tao else "Không xác định", inline=False)
    bang_log.add_field(name="🧑‍🦱 Người đóng đơn:", value=nguoi_dong, inline=False)
    bang_log.add_field(name="🔖 Dịch vụ:", value=loai_dich_vu, inline=False)
    bang_log.add_field(name="⏰ Thời gian đóng:", value=bay_gio.strftime('%H:%M:%S | %d - %m - %Y'), inline=False)
    bang_log.add_field(name="📝 Lí do:", value=ly_do, inline=False)
    
    try:
        await nguoi_nhan.send(embed=bang_log)
    except:
        pass

# ===== BIỂU MẪU =====
class BangKiemTraTien(discord.ui.Modal, title="Kiểm tra giá tiền"):
    so_luong = discord.ui.TextInput(label="Nhập số tiền", placeholder="Ví dụ: 100000 (TIỀN)", required=True, max_length=20)
    
    async def on_submit(self, tuong_tac: discord.Interaction):
        try:
            tien = int(self.so_luong.value.replace(",", "").replace(".", ""))
        except ValueError:
            return await tuong_tac.response.send_message("❌ Vui lòng chỉ nhập số.", ephemeral=True)
        
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
        
        if vip:
            mo_ta += f"\n👑 {tuong_tac.user.mention}, bạn là **Thành viên VIP** nên được giảm **3%**!\n"
        
        mo_ta += "\n‼️ **ÁP MÃ GIẢM GIÁ SẼ ĐƯỢC GIẢM TÙY THEO MÃ** ‼️"
        
        bang.description = mo_ta
        bang.set_image(url=ANH_GIF)
        bang.set_footer(text=f"{bay_gio.strftime('%H:%M:%S | %d-%m-%Y')} | {tuong_tac.user.display_name}")
        await tuong_tac.response.send_message(embed=bang, ephemeral=True)

class BangKiemTraSlay(discord.ui.Modal, title="Kiểm tra giá slay"):
    so_luong = discord.ui.TextInput(label="Nhập số slay", placeholder="Ví dụ: 2000 (SLAY)", required=True, max_length=20)
    
    async def on_submit(self, tuong_tac: discord.Interaction):
        try:
            slay = int(self.so_luong.value.replace(",", "").replace(".", ""))
        except ValueError:
            return await tuong_tac.response.send_message("❌ Vui lòng chỉ nhập số.", ephemeral=True)
        
        ngan_hang_goc = lam_tron_ngan_hang(int(slay * 25))
        vip = la_vip(tuong_tac.user)
        
        if ngan_hang_goc > 8000:
            the_goc = lam_tron_the(ngan_hang_goc)
            the_giam = tinh_giam_gia(the_goc, tuong_tac.user)
            chuoi_the = dinh_dang_gia(the_goc, the_giam, vip)
        else:
            chuoi_the = "Chỉ nhận thẻ từ 400 SLAY trở lên!"
        
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
        
        if vip:
            mo_ta += f"\n👑 {tuong_tac.user.mention}, bạn là **Thành viên VIP** nên được giảm **3%**!\n"
        
        mo_ta += "\n‼️ **ÁP MÃ GIẢM GIÁ SẼ ĐƯỢC GIẢM TÙY THEO MÃ** ‼️"
        
        bang.description = mo_ta
        bang.set_image(url=ANH_GIF)
        bang.set_footer(text=f"{bay_gio.strftime('%H:%M:%S | %d-%m-%Y')} | {tuong_tac.user.display_name}")
        await tuong_tac.response.send_message(embed=bang, ephemeral=True)

class BangVndSangTien(discord.ui.Modal, title="VND → Tiền cần cày"):
    so_luong = discord.ui.TextInput(label="Nhập số tiền VND bạn muốn trả", placeholder="Ví dụ: 50000", required=True, max_length=20)
    
    async def on_submit(self, tuong_tac: discord.Interaction):
        try:
            vnd = int(self.so_luong.value.replace(",", "").replace(".", ""))
        except ValueError:
            return await tuong_tac.response.send_message("❌ Vui lòng chỉ nhập số.", ephemeral=True)
        
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
        
        if vip:
            mo_ta += f"\n👑 {tuong_tac.user.mention}, bạn là **Thành viên VIP** nên được giảm **3%**!\n"
        
        mo_ta += "\n‼️ **ÁP MÃ GIẢM GIÁ SẼ ĐƯỢC GIẢM TÙY THEO MÃ** ‼️"
        
        bang.description = mo_ta
        bang.set_image(url=ANH_GIF)
        bang.set_footer(text=f"{bay_gio.strftime('%H:%M:%S | %d-%m-%Y')} | {tuong_tac.user.display_name}")
        await tuong_tac.response.send_message(embed=bang, ephemeral=True)

class BangVndSangSlay(discord.ui.Modal, title="VND → Slay"):
    so_luong = discord.ui.TextInput(label="Nhập số tiền VND bạn muốn trả", placeholder="Ví dụ: 50000", required=True, max_length=20)
    
    async def on_submit(self, tuong_tac: discord.Interaction):
        try:
            vnd = int(self.so_luong.value.replace(",", "").replace(".", ""))
        except ValueError:
            return await tuong_tac.response.send_message("❌ Vui lòng chỉ nhập số.", ephemeral=True)
        
        vnd_sau_giam = tinh_giam_gia(vnd, tuong_tac.user)
        slay = int(vnd_sau_giam / 25)
        ngan_hang_goc = lam_tron_ngan_hang(vnd)
        ngan_hang_giam = tinh_giam_gia(ngan_hang_goc, tuong_tac.user)
        vip = la_vip(tuong_tac.user)
        
        if ngan_hang_goc > 8000:
            the_goc = lam_tron_the(ngan_hang_goc)
            the_giam = tinh_giam_gia(the_goc, tuong_tac.user)
            chuoi_the = dinh_dang_gia(the_goc, the_giam, vip)
        else:
            chuoi_the = "Chỉ nhận thẻ từ 400 SLAY trở lên!"
        
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
        
        if vip:
            mo_ta += f"\n👑 {tuong_tac.user.mention}, bạn là **Thành viên VIP** nên được giảm **3%**!\n"
        
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
        if dem_don > 999:
            dem_don = 1
        
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
        else:
            id_nguoi_tao = du_lieu_chu_de
            loai_dich_vu = "Không xác định"
        
        await gui_nhat_ky_don(tuong_tac.client, so_don, id_nguoi_tao, tuong_tac.user.mention, loai_dich_vu, self.ly_do.value)
        await tuong_tac.channel.delete()

# ===== GIAO DIỆN =====
class XacNhanDongDon(discord.ui.View):
    def __init__(self, kenh, so_don, id_nguoi_tao, loai_dich_vu):
        super().__init__(timeout=30)
        self.kenh = kenh
        self.so_don = so_don
        self.id_nguoi_tao = id_nguoi_tao
        self.loai_dich_vu = loai_dich_vu
    
    @discord.ui.button(label="✅ Xác nhận đóng", style=discord.ButtonStyle.red)
    async def xac_nhan(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        if not la_quan_tri_hoac_dieu_hanh(tuong_tac.user):
            return await tuong_tac.response.send_message("❌ Chỉ Quản trị/Điều hành mới có quyền!", ephemeral=True)
        await tuong_tac.response.send_message("🔒 Đang đóng...", ephemeral=True)
        await gui_nhat_ky_don(tuong_tac.client, self.so_don, self.id_nguoi_tao, tuong_tac.user.mention, self.loai_dich_vu)
        await self.kenh.delete()
    
    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.grey)
    async def huy(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        if not la_quan_tri_hoac_dieu_hanh(tuong_tac.user):
            return await tuong_tac.response.send_message("❌ Chỉ Quản trị/Điều hành mới có quyền!", ephemeral=True)
        await tuong_tac.message.delete()
        await tuong_tac.response.send_message("❌ Đã hủy đóng đơn!", ephemeral=True)

class BinhChonHoanThanh(discord.ui.View):
    def __init__(self, kenh, so_don, id_nguoi_tao, loai_dich_vu):
        super().__init__(timeout=120)
        self.kenh = kenh
        self.so_don = so_don
        self.id_nguoi_tao = id_nguoi_tao
        self.loai_dich_vu = loai_dich_vu
        self.nguoi_bau = set()
        self.da_co_admin = False
        self.da_co_nguoi_tao = False
    
    @discord.ui.button(label="✅ Hoàn thành đơn", style=discord.ButtonStyle.green)
    async def hoan_thanh(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        nguoi_dung = tuong_tac.user
        la_admin = la_quan_tri_hoac_dieu_hanh(nguoi_dung)
        la_nguoi_tao = str(nguoi_dung.id) == str(self.id_nguoi_tao)
        
        if not la_admin and not la_nguoi_tao:
            return await tuong_tac.response.send_message("❌ Chỉ Quản trị/Điều hành hoặc Người tạo đơn mới có quyền!", ephemeral=True)
        if nguoi_dung.id in self.nguoi_bau:
            return await tuong_tac.response.send_message("❌ Bạn đã bấm rồi!", ephemeral=True)
        
        self.nguoi_bau.add(nguoi_dung.id)
        if la_admin: self.da_co_admin = True
        if la_nguoi_tao: self.da_co_nguoi_tao = True
        
        if self.da_co_admin and self.da_co_nguoi_tao:
            await tuong_tac.response.send_message("✅ Đơn đã hoàn thành! Đang đóng...", ephemeral=True)
            await gui_nhat_ky_don(tuong_tac.client, self.so_don, self.id_nguoi_tao, tuong_tac.user.mention, self.loai_dich_vu, "Đơn đã hoàn thành")
            await self.kenh.delete()
        else:
            con_thieu = []
            if not self.da_co_admin: con_thieu.append("**Quản trị/Điều hành**")
            if not self.da_co_nguoi_tao: con_thieu.append("**Người tạo đơn**")
            await tuong_tac.response.send_message(f"✅ Đã ghi nhận! Cần thêm {' và '.join(con_thieu)} xác nhận.", ephemeral=True)
    
    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.grey)
    async def huy(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        if not la_quan_tri_hoac_dieu_hanh(tuong_tac.user) and str(tuong_tac.user.id) != str(self.id_nguoi_tao):
            return await tuong_tac.response.send_message("❌ Không có quyền!", ephemeral=True)
        await tuong_tac.message.delete()
        await tuong_tac.response.send_message("❌ Đã hủy!", ephemeral=True)

class DieuKhienDon(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🔒 Đóng đơn", style=discord.ButtonStyle.red, custom_id="dong_don")
    async def dong(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        if not la_quan_tri_hoac_dieu_hanh(tuong_tac.user):
            return await tuong_tac.response.send_message("❌ Chỉ Quản trị/Điều hành mới có quyền!", ephemeral=True)
        
        ten_kenh = tuong_tac.channel.name
        phan = ten_kenh.split("-")
        so_don = phan[1] if len(phan) > 1 else "???"
        du_lieu_chu_de = tuong_tac.channel.topic
        if du_lieu_chu_de and "|" in du_lieu_chu_de:
            id_nguoi_tao, loai_dich_vu = du_lieu_chu_de.split("|", 1)
        else:
            id_nguoi_tao = du_lieu_chu_de
            loai_dich_vu = "Không xác định"
        
        bang = discord.Embed(title="⚠️ XÁC NHẬN ĐÓNG ĐƠN", description=f"Bạn có chắc muốn đóng đơn **#{so_don}**?", color=0xff0000)
        await tuong_tac.response.send_message(embed=bang, view=XacNhanDongDon(tuong_tac.channel, so_don, id_nguoi_tao, loai_dich_vu), ephemeral=False)
    
    @discord.ui.button(label="✅ Hoàn thành đơn", style=discord.ButtonStyle.green, custom_id="hoan_thanh_don")
    async def hoan_thanh(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        nguoi_dung = tuong_tac.user
        ten_kenh = tuong_tac.channel.name
        phan = ten_kenh.split("-")
        so_don = phan[1] if len(phan) > 1 else "???"
        du_lieu_chu_de = tuong_tac.channel.topic
        if du_lieu_chu_de and "|" in du_lieu_chu_de:
            id_nguoi_tao, loai_dich_vu = du_lieu_chu_de.split("|", 1)
        else:
            id_nguoi_tao = du_lieu_chu_de
            loai_dich_vu = "Không xác định"
        
        la_admin = la_quan_tri_hoac_dieu_hanh(nguoi_dung)
        la_nguoi_tao = str(nguoi_dung.id) == str(id_nguoi_tao)
        
        if not la_admin and not la_nguoi_tao:
            return await tuong_tac.response.send_message("❌ Chỉ Quản trị/Điều hành hoặc Người tạo đơn mới có quyền!", ephemeral=True)
        
        bang = discord.Embed(title="✅ HOÀN THÀNH ĐƠN", description=f"**Cần Quản trị/Điều hành VÀ Người tạo đơn xác nhận** để hoàn thành đơn **#{so_don}**", color=0x00ff00)
        await tuong_tac.response.send_message(embed=bang, view=BinhChonHoanThanh(tuong_tac.channel, so_don, id_nguoi_tao, loai_dich_vu), ephemeral=False)
    
    @discord.ui.button(label="🧾 Đóng đơn kèm lý do", style=discord.ButtonStyle.grey, custom_id="dong_don_ly_do")
    async def dong_ly_do(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        if not la_quan_tri_hoac_dieu_hanh(tuong_tac.user):
            return await tuong_tac.response.send_message("❌ Chỉ Quản trị/Điều hành mới có quyền!", ephemeral=True)
        await tuong_tac.response.send_modal(BangLyDoDong())

# ===== GIAO DIỆN KHÁC =====
class GiaoDienKiemTraGia(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="💰 Tiền Divaz → VND", style=discord.ButtonStyle.green, custom_id="kiem_tra_tien")
    async def kiem_tra_tien(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        await tuong_tac.response.send_modal(BangKiemTraTien())
    
    @discord.ui.button(label="💅 Slay → VND", style=discord.ButtonStyle.green, custom_id="kiem_tra_slay")
    async def kiem_tra_slay(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        await tuong_tac.response.send_modal(BangKiemTraSlay())
    
    @discord.ui.button(label="💵 VND → Tiền cày", style=discord.ButtonStyle.blurple, custom_id="vnd_sang_tien")
    async def vnd_sang_tien(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        await tuong_tac.response.send_modal(BangVndSangTien())
    
    @discord.ui.button(label="💳 VND → Slay", style=discord.ButtonStyle.blurple, custom_id="vnd_sang_slay")
    async def vnd_sang_slay(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        await tuong_tac.response.send_modal(BangVndSangSlay())

class GiaoDienTaoDon(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🎫 Tạo đơn", style=discord.ButtonStyle.blurple, custom_id="tao_don")
    async def tao(self, tuong_tac: discord.Interaction, nut: discord.ui.Button):
        await tuong_tac.response.send_modal(BangTaoDon())

class GiaoDienServer(discord.ui.View):
    def __init__(self, may_chu):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(
            style=discord.ButtonStyle.green if may_chu['so_nguoi_choi'] <= 3 else discord.ButtonStyle.blurple,
            label="THAM GIA",
            url=f"https://nuxwtghieux.github.io/Snipe/?jobid={may_chu['id_may']}"
        ))

# ===== MÁY QUÉT DIVAZ =====
def quet_divaz():
    ket_qua = []
    con_tro = ""
    tieu_de = {'User-Agent': 'Mozilla/5.0'}
    
    while True:
        duong_dan = f"https://games.roblox.com/v1/games/{ID_MAP}/servers/Public?limit=100"
        if con_tro:
            duong_dan += f"&cursor={con_tro}"
        
        try:
            phan_hoi = requests.get(duong_dan, headers=tieu_de, timeout=15, verify=False)
            
            if phan_hoi.status_code == 200:
                du_lieu = phan_hoi.json()
                cac_may = du_lieu.get('data', [])
                
                if not cac_may:
                    break
                
                for may in cac_may:
                    so_nguoi = may.get('playing', 0)
                    
                    if so_nguoi < 5 and may['id'] not in cac_map_da_gui:
                        ket_qua.append({
                            'id_may': may['id'],
                            'so_nguoi_choi': so_nguoi,
                            'ping': may.get('ping', 'N/A'),
                            'fps': may.get('fps', 'N/A'),
                            'toi_da': may.get('maxPlayers', 'N/A')
                        })
                
                con_tro = du_lieu.get('nextPageCursor')
                if not con_tro:
                    break
                
                time.sleep(1)
            else:
                break
        except:
            time.sleep(3)
    
    return ket_qua

# ===== LỆNH SLASH =====
@discord.app_commands.command(name="tat_tim_map", description="⏸️ Tạm dừng quét server Divaz")
async def lenh_tat_tim_map(tuong_tac: discord.Interaction):
    global dang_quet
    if not la_quan_tri(tuong_tac.user):
        return await tuong_tac.response.send_message("❌ Chỉ Quản trị mới dùng được lệnh này!", ephemeral=True)
    dang_quet = False
    await tuong_tac.response.send_message("⏸️ Đã **tắt** quét map Divaz!", ephemeral=True)

@discord.app_commands.command(name="bat_tim_map", description="▶️ Bật lại quét server Divaz")
async def lenh_bat_tim_map(tuong_tac: discord.Interaction):
    global dang_quet
    if not la_quan_tri(tuong_tac.user):
        return await tuong_tac.response.send_message("❌ Chỉ Quản trị mới dùng được lệnh này!", ephemeral=True)
    dang_quet = True
    await tuong_tac.response.send_message("▶️ Đã **bật** quét map Divaz!", ephemeral=True)

# ===== BOT CHÍNH =====
class Bot(discord.Client):
    def __init__(self):
        quyen = discord.Intents.default()
        quyen.guilds = True
        quyen.message_content = True
        quyen.members = True
        quyen.reactions = True
        super().__init__(intents=quyen)
        self.cay = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        may_chu = discord.Object(id=ID_MAY_CHU)
        self.cay.add_command(lenh_tat_tim_map)
        self.cay.add_command(lenh_bat_tim_map)
        await self.cay.sync(guild=may_chu)
        self.add_view(GiaoDienKiemTraGia())
        self.add_view(GiaoDienTaoDon())
        self.add_view(DieuKhienDon())
    
    async def on_ready(self):
        nap_emoji_tu_may_chu(self)
        await nap_du_lieu_tu_dm(self)
        await self.bang_dieu_khien()
        self.vong_lap_quet.start()
        print(f"🚀 Bot sẵn sàng! Đơn tiếp theo: {dem_don + 1}")
    
    async def bang_dieu_khien(self):
        kenh_kiem_tra = self.get_channel(ID_KENH_KIEM_TRA)
        if kenh_kiem_tra:
            async for tin in kenh_kiem_tra.history(limit=50):
                if tin.author == self.user:
                    await tin.delete()
            
            bang_kiem_tra = discord.Embed(
                title="‼️ HƯỚNG DẪN KIỂM TRA GIÁ 📍",
                description="━━━━━━━━━━━━━━━━━━━━━━\n"
                           "📌 BƯỚC 1ㆍNhấn '💰 Tiền Divaz → VND' hoặc '💅 Slay → VND' để xem giá.\n\n"
                           "📌 BƯỚC 2ㆍNhập số tiền/slay bạn muốn cày.\n\n"
                           "📌 BƯỚC 3ㆍSau đó 'gửi' sẽ biết ngay số tiền phải trả.\n\n"
                           "💡 **Nút phụ:** '💵 VND → Tiền cày' và '💳 VND → Slay' để tính ngược từ VND.",
                color=0x3498db
            )
            bang_kiem_tra.set_footer(text=gio_vn().strftime('%H:%M:%S | %d-%m-%Y'))
            await kenh_kiem_tra.send(embed=bang_kiem_tra, view=GiaoDienKiemTraGia())
        
        kenh_don = self.get_channel(ID_KENH_DON)
        if kenh_don:
            async for tin in kenh_don.history(limit=50):
                if tin.author == self.user:
                    await tin.delete()
            await kenh_don.send(
                embed=discord.Embed(title="🛒 DỊCH VỤ CÀY TIỀN & SLAY", description="━━━━━━━━━━━━━━━━━━━━━━\n✅ HÃY TẠO ĐƠN Ở NÚT BÊN DƯỚI!", color=0x3498db),
                view=GiaoDienTaoDon()
            )
        
        global id_tin_nhan_phan_ung
        kenh_phan_ung = self.get_channel(ID_KENH_PHAN_UNG)
        if kenh_phan_ung:
            tin_nhan_cu = None
            async for tin in kenh_phan_ung.history(limit=50):
                if tin.author == self.user and tin.embeds:
                    tin_nhan_cu = tin
                    break
            
            if tin_nhan_cu:
                id_tin_nhan_phan_ung = tin_nhan_cu.id
                try:
                    await tin_nhan_cu.add_reaction(BIEU_TUONG_PHAN_UNG)
                except:
                    pass
                print(f"✅ Giữ nguyên embed phản ứng cũ: {tin_nhan_cu.id}")
            else:
                async for tin in kenh_phan_ung.history(limit=50):
                    if tin.author == self.user:
                        await tin.delete()
                
                bang_vai_tro = discord.Embed(
                    title="🎭 NHẬN VAI TRÒ",
                    description="━━━━━━━━━━━━━━━━━━━━━━\n"
                               "✅ **ĐỂ XEM CÁC KÊNH CHAT, HÃY TICK VÀO BÊN DƯỚI ↓**\n"
                               "━━━━━━━━━━━━━━━━━━━━━━",
                    color=0x9b59b6
                )
                bang_vai_tro.set_footer(text="BotByPawPaw")
                
                tin_nhan_moi = await kenh_phan_ung.send(embed=bang_vai_tro)
                await tin_nhan_moi.add_reaction(BIEU_TUONG_PHAN_UNG)
                id_tin_nhan_phan_ung = tin_nhan_moi.id
                print(f"✅ Đã tạo tin nhắn phản ứng mới: {tin_nhan_moi.id}")
    
    @tasks.loop(seconds=180)
    async def vong_lap_quet(self):
        global dang_quet, cac_map_da_gui
        
        if not dang_quet:
            return
        
        kenh = self.get_channel(ID_KENH_QUET)
        if not kenh:
            return
        
        cac_may = quet_divaz()
        
        if cac_may:
            if len(cac_map_da_gui) > 50:
                cac_map_da_gui.clear()
            
            tot_nhat = cac_may[0]
            so_nguoi = tot_nhat['so_nguoi_choi']
            ma = tot_nhat['id_may'][-5:]
            mau_sac = 0x00ff00 if so_nguoi <= 3 else 0xffaa00
            bay_gio = gio_vn()
            
            cac_map_da_gui.add(tot_nhat['id_may'])
            
            print(f"✅ Gửi server MỚI: #{ma} | {so_nguoi}/{tot_nhat['toi_da']} người")
            
            bang = discord.Embed(
                title="🎮 DIVAZ - MÁY CHỦ TRỐNG",
                description=f"**Mã Máy Chủ:** `#{ma}`",
                color=mau_sac,
                timestamp=bay_gio
            )
            trang_thai = f"🟢 {so_nguoi}/{tot_nhat['toi_da']}" if so_nguoi <= 3 else f"🟡 {so_nguoi}/{tot_nhat['toi_da']}"
            bang.add_field(name="👥 **NGƯỜI CHƠI**", value=trang_thai, inline=True)
            bang.add_field(name="📶 **PING**", value=f"{tot_nhat['ping']}ms", inline=True)
            bang.add_field(name="🎯 **FPS**", value=f"{tot_nhat['fps']}", inline=True)
            
            bang.set_thumbnail(url=ANH_NHO)
            bang.set_image(url=ANH_LON)
            bang.set_footer(text=f"BotByPawPaw • {bay_gio.strftime('%H:%M:%S | %d/%m/%Y')}")
            
            await kenh.send(embed=bang, view=GiaoDienServer(tot_nhat))
        else:
            print("❌ Không tìm thấy máy chủ mới!")
    
    async def on_raw_reaction_add(self, du_lieu):
        global id_tin_nhan_phan_ung
        
        if du_lieu.message_id != id_tin_nhan_phan_ung:
            return
        
        if str(du_lieu.emoji) != BIEU_TUONG_PHAN_UNG:
            return
        
        may_chu = self.get_guild(du_lieu.guild_id)
        if not may_chu:
            return
        
        thanh_vien = may_chu.get_member(du_lieu.user_id)
        if not thanh_vien or thanh_vien.bot:
            return
        
        vai_tro = may_chu.get_role(ID_VAI_TRO_PHAN_UNG)
        if not vai_tro:
            return
        
        try:
            await thanh_vien.add_roles(vai_tro)
            print(f"✅ Đã gán vai trò cho {thanh_vien.display_name}")
        except Exception as e:
            print(f"❌ Lỗi gán vai trò: {e}")
    
    async def on_raw_reaction_remove(self, du_lieu):
        global id_tin_nhan_phan_ung
        
        if du_lieu.message_id != id_tin_nhan_phan_ung:
            return
        
        if str(du_lieu.emoji) != BIEU_TUONG_PHAN_UNG:
            return
        
        may_chu = self.get_guild(du_lieu.guild_id)
        if not may_chu:
            return
        
        thanh_vien = may_chu.get_member(du_lieu.user_id)
        if not thanh_vien or thanh_vien.bot:
            return
        
        vai_tro = may_chu.get_role(ID_VAI_TRO_PHAN_UNG)
        if not vai_tro:
            return
        
        try:
            await thanh_vien.remove_roles(vai_tro)
            print(f"✅ Đã gỡ vai trò của {thanh_vien.display_name}")
        except Exception as e:
            print(f"❌ Lỗi gỡ vai trò: {e}")
    
    async def on_member_join(self, thanh_vien):
        kenh = self.get_channel(ID_KENH_CHAO_MUNG)
        if not kenh:
            return
        
        bay_gio = gio_vn()
        may_chu = thanh_vien.guild
        nhac_quan_tri = f"<@&{ID_QUAN_TRI}>"
        nhac_dieu_hanh = f"<@&{ID_DIEU_HANH}>"
        
        # Bỏ title, dùng description làm welcome
        bang = discord.Embed(color=0x2ecc71)
        bang.description = (
            f"# {EMOJI_CANH1} CHÀO MỪNG THÀNH VIÊN MỚI {EMOJI_CANH2}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"# {EMOJI_TRON}┆THÔNG TIN CỦA BẠN:\n"
            f"ㆍ*Tên*: {thanh_vien.mention}\n"
            f"ㆍ*Người dùng*: {thanh_vien.name}\n"
            f"ㆍ*ID*: {thanh_vien.id}\n"
            f"ㆍ*Ngày tạo*: {thanh_vien.created_at.strftime('%d-%m-%Y')}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"# {EMOJI_TRON}┆CỬA HÀNG PAWPAW:\n"
            f"ㆍChào mừng bạn đã đến với {may_chu.name}!\n"
            f"ㆍBạn là thành viên thứ {may_chu.member_count} của {may_chu.name}\n"
            f"ㆍNếu thắc mắc và cần hỗ trợ, hãy liên hệ {nhac_quan_tri} và {nhac_dieu_hanh}.\n"
            f"ㆍNếu muốn tham gia các kênh trò chuyện, hãy vào kênh <#{ID_KENH_PHAN_UNG}> để nhận vai trò.\n\n"
            "✨✨CHÚC BẠN MỘT NGÀY TỐT LÀNH✨✨"
        )
        bang.set_thumbnail(url=thanh_vien.display_avatar.url)
        bang.set_image(url=ANH_CHAO_MUNG)
        bang.set_footer(text=bay_gio.strftime('%H:%M:%S | %d-%m-%Y'))
        await kenh.send(embed=bang)
    
    async def on_member_remove(self, thanh_vien):
        kenh = self.get_channel(ID_KENH_TAM_BIET)
        if not kenh:
            return
        
        bay_gio = gio_vn()
        may_chu = thanh_vien.guild
        
        bang = discord.Embed(
            title="😢 TẠM BIỆT",
            description=f"**{thanh_vien.mention}** đã rời máy chủ!\n\n"
                       f"👋 Tạm biệt **{thanh_vien.display_name}**\n"
                       f"💔 Máy chủ còn **{may_chu.member_count}** thành viên",
            color=0xe74c3c
        )
        bang.set_thumbnail(url=thanh_vien.display_avatar.url)
        bang.set_image(url=ANH_TAM_BIET)
        bang.set_footer(text=bay_gio.strftime('%H:%M:%S | %d-%m-%Y'))
        await kenh.send(embed=bang)

# ===== CHẠY =====
if __name__ == '__main__':
    luong = threading.Thread(target=chay_may_chu_web)
    luong.start()
    print("🌐 Máy chủ web cổng 8080")
    
    bot = Bot()
    bot.run(MA_BOT)
