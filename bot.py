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
import asyncio
import traceback
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
ID_MEMBER_PAW = 1523599853882703882
ID_NGUOI_NHAN_LOG = 1507006947755430069
ID_KENH_CHAO_MUNG = 1523598483632947281
ID_KENH_TAM_BIET = 1523602359605919746
ID_KENH_QUET = 1523707366280003594
ID_MAP = "88323040672117"
ID_KENH_PHAN_UNG = 1523970421819572345
ID_VAI_TRO_PHAN_UNG = 1523599853882703882
KENH_EVENT_ID = 1523605458068181083
KENH_KET_QUA_ID = 1523605663064915978

EMOJI_CANH1 = "✨"
EMOJI_CANH2 = "✨"
EMOJI_BLINK2 = "✨"
EMOJI_BLINKK = "🔹"
EMOJI_TRON = "🔹"
EMOJI_COIN = "💰"
BIEU_TUONG_PHAN_UNG = "✅"

ANH_GIF = "https://cdn.discordapp.com/attachments/1524068633255481387/1524080452049305713/da685c21e4f555bad69f52593c221dc7.gif"
ANH_CHAO_MUNG = "https://i.postimg.cc/sDh8Xcyp/a9e9538574064d128b604f643392d84b.gif"
ANH_TAM_BIET = "https://cdn.discordapp.com/attachments/1524068633255481387/1524068815518961825/c19d6274e1fd53c5ca46cdafccb4cbc9.gif"
ANH_NHO = "https://huyhieu08.online/uploads/20260707_054705_91412ed7.png"
ANH_LON = "https://i.postimg.cc/V6CFtBL0/no-Filter.webp"

# ===== BIẾN TOÀN CỤC =====
dem_don = 0
dang_quet = True
id_tin_nhan_phan_ung = None
cac_map_da_gui = []

# ===== BIẾN EVENT =====
event_active = False
cho_phep_tham_gia = True
nguoi_tham_gia = {}
msg_event = None
so_event = 1
vong_hien_tai = 1
ds_da_thang = []
lich_su_event = []

# ===== HÀM LỊCH SỬ =====
def them_lich_su(action, nguoi, nguoi_thuc_hien, **kwargs):
    lich_su_event.append({
        "action": action,
        "nguoi": nguoi,
        "nguoi_thuc_hien": nguoi_thuc_hien,
        "time": gio_vn().strftime("%H:%M:%S %d/%m/%Y"),
        **kwargs
    })

# ===== HÀM KHÔI PHỤC EVENT =====
async def phuc_hoi_event_tu_tin_nhan(bot):
    global event_active, cho_phep_tham_gia, nguoi_tham_gia, msg_event, so_event, vong_hien_tai, ds_da_thang
    try:
        k = bot.get_channel(KENH_EVENT_ID)
        if not k:
            print("❌ Không tìm thấy kênh event!")
            return False

        async for msg in k.history(limit=100):
            if msg.author == bot.user and msg.embeds:
                embed = msg.embeds[0]
                if "EVENT DIVAZ" in embed.title:
                    msg_event = msg
                    print(f"✅ Tìm thấy event tại: {msg.jump_url}")
                    for field in embed.fields:
                        if field.name == "📋 DANH SÁCH:":
                            ds_text = field.value
                            nguoi_tham_gia = {}
                            for line in ds_text.split("\n"):
                                if "**" in line and "(" in line:
                                    match = re.search(r'\(`(\d+)`\)', line)
                                    if match:
                                        uid = int(match.group(1))
                                        ten = line.split("**")[1] if "**" in line else "Unknown"
                                        nguoi_tham_gia[uid] = ten
                            break
                    for field in embed.fields:
                        if field.name == "📌 TRẠNG THÁI":
                            cho_phep_tham_gia = "mở" in field.value.lower()
                            break
                    event_active = True
                    print(f"✅ Đã khôi phục event với {len(nguoi_tham_gia)} người")
                    try:
                        await msg.edit(view=NutEventChinh())
                    except Exception as e:
                        print(f"❌ Lỗi edit message: {e}")
                    return True
    except Exception as e:
        print(f"❌ Lỗi khôi phục event: {e}")
        traceback.print_exc()
    return False

# ===== CÁC HÀM TIỆN ÍCH =====
def nap_emoji_tu_may_chu(bot):
    global EMOJI_CANH1, EMOJI_CANH2, EMOJI_BLINK2, EMOJI_BLINKK, EMOJI_TRON, EMOJI_COIN, BIEU_TUONG_PHAN_UNG
    try:
        may_chu = bot.get_guild(ID_MAY_CHU)
        if not may_chu:
            return
        for emoji in may_chu.emojis:
            if emoji.name == "canh1":
                EMOJI_CANH1 = str(emoji)
            elif emoji.name == "canh2":
                EMOJI_CANH2 = str(emoji)
            elif emoji.name == "blink2":
                EMOJI_BLINK2 = str(emoji)
            elif emoji.name == "blinkk":
                EMOJI_BLINKK = str(emoji)
            elif emoji.name == "tron":
                EMOJI_TRON = str(emoji)
            elif emoji.name == "xu":
                EMOJI_COIN = str(emoji)
            elif emoji.name == "baibien":
                BIEU_TUONG_PHAN_UNG = str(emoji)
    except Exception as e:
        print(f"❌ Lỗi nap_emoji: {e}")
        traceback.print_exc()

def lam_tron_the(ngan_hang):
    the_tho = ngan_hang * 1.15 + 10000
    phan_du = the_tho % 10000
    return ((the_tho // 10000) + 1) * 10000 if phan_du >= 5000 else (the_tho // 10000) * 10000

def lam_tron_ngan_hang(ngan_hang):
    return int(round(ngan_hang / 1000) * 1000)

def la_quan_tri(tt: discord.Interaction):
    try:
        tv = tt.user
        if tv.guild_permissions.administrator:
            return True
        return any(r.id == ID_QUAN_TRI for r in tv.roles)
    except Exception as e:
        print(f"❌ Lỗi la_quan_tri: {e}")
        traceback.print_exc()
        return False

def la_quan_tri_hoac_dieu_hanh(tt: discord.Interaction):
    try:
        tv = tt.user
        return any(r.id in [ID_QUAN_TRI, ID_DIEU_HANH] for r in tv.roles)
    except Exception as e:
        print(f"❌ Lỗi la_quan_tri_hoac_dieu_hanh: {e}")
        traceback.print_exc()
        return False

def la_vip_nd(tt: discord.Interaction):
    try:
        return any(r.id == ID_VIP for r in tt.user.roles)
    except Exception as e:
        print(f"❌ Lỗi la_vip_nd: {e}")
        traceback.print_exc()
        return False

def tinh_giam_gia(st, tt):
    return int(st * 0.97) if la_vip_nd(tt) else st

def dinh_dang_gia(gg, giam, vip):
    return f"**{giam:,}** VND ~~{gg:,} VND~~ (VIP)" if vip and giam != gg else f"**{gg:,}** VND"

async def gui_nhat_ky_don(bot, so_don, id_nt, nguoi_dong, ldv, ly_do="Không"):
    try:
        now = gio_vn()
        nguoi_nhan = bot.get_user(ID_NGUOI_NHAN_LOG) or await bot.fetch_user(ID_NGUOI_NHAN_LOG)
        bang = discord.Embed(title=f"# Đơn số {so_don}", color=0x3498db)
        bang.add_field(name="🧑‍🦱 Người mở:", value=f"<@{id_nt}>" if id_nt else "?", inline=False)
        bang.add_field(name="🧑‍🦱 Người đóng:", value=nguoi_dong, inline=False)
        bang.add_field(name="🔖 Dịch vụ:", value=ldv, inline=False)
        bang.add_field(name="⏰ Thời gian:", value=now.strftime('%H:%M:%S | %d-%m-%Y'), inline=False)
        bang.add_field(name="📝 Lí do:", value=ly_do, inline=False)
        await nguoi_nhan.send(embed=bang)
    except Exception as e:
        print(f"❌ Lỗi gui_nhat_ky_don: {e}")
        traceback.print_exc()

# ===== MODALS =====
class BangKiemTraTien(discord.ui.Modal, title="Kiểm tra giá tiền"):
    sl = discord.ui.TextInput(label="Nhập số tiền", placeholder="100000", required=True, max_length=20)

    async def on_submit(self, tt):
        try:
            tien = int(self.sl.value.replace(",", "").replace(".", ""))
        except:
            return await tt.response.send_message("❌ Số không hợp lệ!", ephemeral=True)
        try:
            ngan_hang_goc = lam_tron_ngan_hang(int(tien * 0.12))
            the_goc = lam_tron_the(ngan_hang_goc)
            ngan_hang_giam = tinh_giam_gia(ngan_hang_goc, tt)
            the_giam = tinh_giam_gia(the_goc, tt)
            vip = la_vip_nd(tt)
            now = gio_vn()
            bang = discord.Embed(title=f"💰 GIÁ CÀY TIỀN HIỆN TẠI 💰", color=0x3498db)
            mo_ta = (
                "\n━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💵ㆍ**Số tiền cần cày:** **{tien:,} TIỀN**\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💳ㆍ**Chuyển khoản (Bank):** {dinh_dang_gia(ngan_hang_goc, ngan_hang_giam, vip)}\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔖ㆍ**Thẻ cào (Card):** {dinh_dang_gia(the_goc, the_giam, vip)}\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
            )
            if vip:
                mo_ta += f"\n👑 {tt.user.mention}, bạn là **Thành viên VIP** nên được giảm **3%**!\n"
            mo_ta += "\n‼️ **ÁP MÃ GIẢM GIÁ SẼ ĐƯỢC GIẢM TÙY THEO MÃ** ‼️"
            bang.description = mo_ta
            bang.set_image(url=ANH_GIF)
            bang.set_footer(text=f"{now.strftime('%H:%M:%S | %d-%m-%Y')} | {tt.user.display_name}")
            await tt.response.send_message(embed=bang, ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi BangKiemTraTien: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

class BangKiemTraSlay(discord.ui.Modal, title="Kiểm tra giá slay"):
    sl = discord.ui.TextInput(label="Nhập số slay", placeholder="2000", required=True, max_length=20)

    async def on_submit(self, tt):
        try:
            slay = int(self.sl.value.replace(",", "").replace(".", ""))
        except:
            return await tt.response.send_message("❌ Số không hợp lệ!", ephemeral=True)
        try:
            ngan_hang_goc = lam_tron_ngan_hang(int(slay * 25))
            vip = la_vip_nd(tt)
            ngan_hang_giam = tinh_giam_gia(ngan_hang_goc, tt)
            if ngan_hang_goc > 8000:
                chuoi_the = dinh_dang_gia(lam_tron_the(ngan_hang_goc), tinh_giam_gia(lam_tron_the(ngan_hang_goc), tt), vip)
            else:
                chuoi_the = "Chỉ nhận card từ 400 SLAY!"
            now = gio_vn()
            bang = discord.Embed(title=f"💅 GIÁ CÀY SLAY HIỆN TẠI 💅", color=0x3498db)
            mo_ta = (
                "\n━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💅ㆍ**Số slay cần cày:** **{slay:,} SLAY**\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💳ㆍ**Chuyển khoản (Bank):** {dinh_dang_gia(ngan_hang_goc, ngan_hang_giam, vip)}\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔖ㆍ**Thẻ cào (Card):** {chuoi_the}\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
            )
            if vip:
                mo_ta += f"\n👑 {tt.user.mention}, bạn là **Thành viên VIP** nên được giảm **3%**!\n"
            mo_ta += "\n‼️ **ÁP MÃ GIẢM GIÁ SẼ ĐƯỢC GIẢM TÙY THEO MÃ** ‼️"
            bang.description = mo_ta
            bang.set_image(url=ANH_GIF)
            bang.set_footer(text=f"{now.strftime('%H:%M:%S | %d-%m-%Y')} | {tt.user.display_name}")
            await tt.response.send_message(embed=bang, ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi BangKiemTraSlay: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

class BangVndSangTien(discord.ui.Modal, title="VND → Tiền cần cày"):
    sl = discord.ui.TextInput(label="Nhập số VND", placeholder="50000", required=True, max_length=20)

    async def on_submit(self, tt):
        try:
            vnd = int(self.sl.value.replace(",", "").replace(".", ""))
        except:
            return await tt.response.send_message("❌ Số không hợp lệ!", ephemeral=True)
        try:
            vnd_sau_giam = tinh_giam_gia(vnd, tt)
            tien_nhan = int(vnd_sau_giam / 0.12)
            ngan_hang_goc = lam_tron_ngan_hang(vnd_sau_giam)
            ngan_hang_giam = tinh_giam_gia(ngan_hang_goc, tt)
            the_goc = lam_tron_the(ngan_hang_goc)
            the_giam = tinh_giam_gia(the_goc, tt)
            vip = la_vip_nd(tt)
            now = gio_vn()
            bang = discord.Embed(title=f"💵 SỐ TIỀN CÀY BẠN NHẬN ĐƯỢC 💵", color=0xe67e22)
            mo_ta = (
                "\n━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💳ㆍ**Số VND bạn trả:** **{vnd:,} VND**\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💰ㆍ**Số tiền cày bạn nhận được:** **{tien_nhan:,} TIỀN**\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔖ㆍ**Thẻ cào (Card):** {dinh_dang_gia(the_goc, the_giam, vip)}\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
            )
            if vip:
                mo_ta += f"\n👑 {tt.user.mention}, bạn là **Thành viên VIP** nên được giảm **3%**!\n"
            mo_ta += "\n‼️ **ÁP MÃ GIẢM GIÁ SẼ ĐƯỢC GIẢM TÙY THEO MÃ** ‼️"
            bang.description = mo_ta
            bang.set_image(url=ANH_GIF)
            bang.set_footer(text=f"{now.strftime('%H:%M:%S | %d-%m-%Y')} | {tt.user.display_name}")
            await tt.response.send_message(embed=bang, ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi BangVndSangTien: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

class BangVndSangSlay(discord.ui.Modal, title="VND → Slay"):
    sl = discord.ui.TextInput(label="Nhập số VND", placeholder="50000", required=True, max_length=20)

    async def on_submit(self, tt):
        try:
            vnd = int(self.sl.value.replace(",", "").replace(".", ""))
        except:
            return await tt.response.send_message("❌ Số không hợp lệ!", ephemeral=True)
        try:
            vnd_sau_giam = tinh_giam_gia(vnd, tt)
            slay = int(vnd_sau_giam / 25)
            ngan_hang_goc = lam_tron_ngan_hang(vnd_sau_giam)
            ngan_hang_giam = tinh_giam_gia(ngan_hang_goc, tt)
            vip = la_vip_nd(tt)
            if ngan_hang_goc > 8000:
                chuoi_the = dinh_dang_gia(lam_tron_the(ngan_hang_goc), tinh_giam_gia(lam_tron_the(ngan_hang_goc), tt), vip)
            else:
                chuoi_the = "Chỉ nhận card từ 400 SLAY!"
            now = gio_vn()
            bang = discord.Embed(title=f"💅 SỐ SLAY BẠN NHẬN ĐƯỢC 💅", color=0x9b59b6)
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
                mo_ta += f"\n👑 {tt.user.mention}, bạn là **Thành viên VIP** nên được giảm **3%**!\n"
            mo_ta += "\n‼️ **ÁP MÃ GIẢM GIÁ SẼ ĐƯỢC GIẢM TÙY THEO MÃ** ‼️"
            bang.description = mo_ta
            bang.set_image(url=ANH_GIF)
            bang.set_footer(text=f"{now.strftime('%H:%M:%S | %d-%m-%Y')} | {tt.user.display_name}")
            await tt.response.send_message(embed=bang, ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi BangVndSangSlay: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

class BangTaoDon(discord.ui.Modal, title="Tạo đơn"):
    dv = discord.ui.TextInput(label="Tiền/Slay:", placeholder="Tiền hoặc Slay", required=True, max_length=10)

    async def on_submit(self, tt):
        global dem_don
        try:
            ldv = self.dv.value
            mc = tt.guild
            nd = tt.user
            for k in mc.channels:
                if k.name.startswith("đơn-") and k.topic and str(nd.id) == k.topic:
                    return await tt.response.send_message("❌ Đã có đơn!", ephemeral=True)
            dm = mc.get_channel(ID_DANH_MUC_DON)
            dem_don += 1
            if dem_don > 999:
                dem_don = 1
            sd = f"{dem_don:03d}"
            now = gio_vn()
            ten = nd.display_name.replace(" ", "-")[:20]
            tn = f"đơn-{sd}-{ten}-{now.strftime('%H-%M')}"
            pq = {
                mc.default_role: discord.PermissionOverwrite(view_channel=False),
                nd: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                mc.me: discord.PermissionOverwrite(view_channel=True)
            }
            k = await mc.create_text_channel(name=tn, category=dm, overwrites=pq, topic=f"{nd.id}|{ldv}")
            await k.send(
                content=f"{nd.mention} <@&{ID_QUAN_TRI}>",
                embed=discord.Embed(
                    title="🎫 CÓ ĐƠN",
                    description=f"Đơn: **{sd}**\nDịch vụ: **{ldv}**\nNgười tạo: {nd.mention}",
                    color=0x3498db
                ),
                view=DieuKhienDon()
            )
            await tt.response.send_message(f"✅ {k.mention}", ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi BangTaoDon: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

class BangLyDoDong(discord.ui.Modal, title="Lý do đóng đơn"):
    ld = discord.ui.TextInput(label="Lý do", required=True)

    async def on_submit(self, tt):
        try:
            tn = tt.channel.name
            p = tn.split("-")
            sd = p[1] if len(p) > 1 else "???"
            dl = tt.channel.topic
            if dl and "|" in dl:
                id_nt, ldv = dl.split("|", 1)
            else:
                id_nt = dl
                ldv = "?"
            await gui_nhat_ky_don(tt.client, sd, id_nt, tt.user.mention, ldv, self.ld.value)
            await tt.channel.delete()
        except Exception as e:
            print(f"❌ Lỗi BangLyDoDong: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

# ===== MODALS EVENT =====
class FormThamGia(discord.ui.Modal, title="Tham gia Event"):
    ten = discord.ui.TextInput(
        label="Hãy điền tên của bạn",
        placeholder="Nhập tên hiển thị trong game",
        required=True,
        max_length=50
    )

    async def on_submit(self, tt):
        global nguoi_tham_gia
        try:
            if not event_active:
                return await tt.response.send_message("❌ Event chưa bắt đầu!", ephemeral=True)
            if not cho_phep_tham_gia:
                return await tt.response.send_message("❌ Event đã đóng tham gia!", ephemeral=True)
            if tt.user.id in nguoi_tham_gia:
                return await tt.response.send_message("❌ Bạn đã tham gia rồi!", ephemeral=True)
            nguoi_tham_gia[tt.user.id] = self.ten.value
            them_lich_su("tham_gia", tt.user.id, tt.user.id, ten=self.ten.value)
            await cap_nhat_event()
            await tt.response.send_message(f"✅ Đã đăng ký với tên: **{self.ten.value}**", ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi FormThamGia: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

class SuaTenModal(discord.ui.Modal, title="Chỉnh sửa tên"):
    ten_moi = discord.ui.TextInput(
        label="Tên mới của bạn",
        placeholder="Nhập tên muốn đổi",
        required=True,
        max_length=50
    )

    async def on_submit(self, tt):
        global nguoi_tham_gia
        try:
            uid = tt.user.id
            if uid not in nguoi_tham_gia:
                return await tt.response.send_message("❌ Bạn chưa tham gia event!", ephemeral=True)
            ten_cu = nguoi_tham_gia[uid]
            nguoi_tham_gia[uid] = self.ten_moi.value
            them_lich_su("sua_ten", uid, uid, old_name=ten_cu, new_name=self.ten_moi.value)
            await cap_nhat_event()
            await tt.response.send_message(f"✅ Đã đổi tên từ **{ten_cu}** thành **{self.ten_moi.value}**!", ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi SuaTenModal: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

class ThemNguoiModal(discord.ui.Modal, title="Thêm người vào danh sách"):
    user_id = discord.ui.TextInput(
        label="ID Discord của người cần thêm",
        placeholder="Nhập ID (ví dụ: 123456789012345678)",
        required=True,
        max_length=20
    )
    ten = discord.ui.TextInput(
        label="Tên Roblox",
        placeholder="Nhập tên Roblox của họ",
        required=True,
        max_length=50
    )

    async def on_submit(self, tt):
        global nguoi_tham_gia
        try:
            uid = int(self.user_id.value)
            if uid in nguoi_tham_gia:
                return await tt.response.send_message("❌ Người này đã có trong danh sách!", ephemeral=True)
            nguoi_tham_gia[uid] = self.ten.value
            them_lich_su("them", uid, tt.user.id, ten=self.ten.value)
            await cap_nhat_event()
            await tt.response.send_message(f"✅ Đã thêm <@{uid}> với tên **{self.ten.value}**!", ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi ThemNguoiModal: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

class XoaNguoiModal(discord.ui.Modal, title="Xoá người khỏi danh sách"):
    user_id = discord.ui.TextInput(
        label="ID Discord của người cần xoá",
        placeholder="Nhập ID",
        required=True,
        max_length=20
    )

    async def on_submit(self, tt):
        global nguoi_tham_gia
        try:
            uid = int(self.user_id.value)
            if uid not in nguoi_tham_gia:
                return await tt.response.send_message("❌ Không tìm thấy người này trong danh sách!", ephemeral=True)
            ten = nguoi_tham_gia[uid]
            del nguoi_tham_gia[uid]
            them_lich_su("xoa", uid, tt.user.id, ten=ten)
            await cap_nhat_event()
            await tt.response.send_message(f"✅ Đã xoá <@{uid}> khỏi danh sách!", ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi XoaNguoiModal: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

# ===== HÀM CẬP NHẬT EVENT =====
async def cap_nhat_event():
    global msg_event, nguoi_tham_gia, cho_phep_tham_gia
    try:
        if not msg_event:
            return
        ds = ""
        if nguoi_tham_gia:
            for i, (uid, ten) in enumerate(nguoi_tham_gia.items(), 1):
                user = bot.get_user(uid)
                ten_hien_thi = user.display_name if user else ten
                ds += f"**{i}.** {ten_hien_thi} (`{uid}`)\n"
        else:
            ds = "Chưa có ai tham gia!"
        trang_thai = "Event đang mở tham gia" if cho_phep_tham_gia else "Event đã đóng tham gia"
        embed = discord.Embed(
            title="⚔️ EVENT DIVAZ ĐẤU 1VS1 ⚔️",
            description=f"ㆍNhấn nút '💅 Tham gia' bên dưới để tham gia vào event này!\nㆍĐã có **{len(nguoi_tham_gia)}** người tham gia.",
            color=0xff0000
        )
        embed.add_field(name="📋 DANH SÁCH:", value=ds, inline=False)
        embed.add_field(name="📌 TRẠNG THÁI", value=f"ㆍ{trang_thai}", inline=False)
        embed.set_footer(text="BotByPawPaw")
        await msg_event.edit(embed=embed)
    except Exception as e:
        print(f"❌ Lỗi cap_nhat_event: {e}")
        traceback.print_exc()

# ===== NÚT EVENT CHÍNH (FIX LỖI custom_id) =====
class NutEventChinh(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        # HÀNG 0: 1 nút
        self.add_item(discord.ui.Button(
            label="💅 Tham gia",
            style=discord.ButtonStyle.green
        ))

        # HÀNG 1: 1 nút
        self.add_item(discord.ui.Button(
            label="🚪 Rời đi",
            style=discord.ButtonStyle.red,
            row=1
        ))

        # HÀNG 2: 2 nút Admin
        self.add_item(discord.ui.Button(
            label="👑 Tham gia",
            style=discord.ButtonStyle.green,
            row=2
        ))
        self.add_item(discord.ui.Button(
            label="📋 Quản lý",
            style=discord.ButtonStyle.blurple,
            row=2
        ))

        # HÀNG 3: 2 nút Admin
        self.add_item(discord.ui.Button(
            label="▶️ Bắt đầu",
            style=discord.ButtonStyle.green,
            row=3
        ))
        self.add_item(discord.ui.Button(
            label="⏸️ Đóng/Mở",
            style=discord.ButtonStyle.red,
            row=3
        ))

        # HÀNG 4: 1 nút Admin
        self.add_item(discord.ui.Button(
            label="❌ Hủy Event",
            style=discord.ButtonStyle.red,
            row=4
        ))

    async def interaction_check(self, interaction):
        try:
            custom_id = interaction.data.get("custom_id")
            user = interaction.user

            la_admin = la_quan_tri(interaction)
            la_mod = la_quan_tri_hoac_dieu_hanh(interaction)
            la_paw = any(r.id == ID_MEMBER_PAW for r in user.roles)

            if custom_id in ["roi_ev"]:
                if la_admin or la_mod:
                    await interaction.response.send_message("❌ Admin/Mod không thể rời đi!", ephemeral=True)
                    return False
                if not la_paw:
                    await interaction.response.send_message("❌ Bạn không có quyền!", ephemeral=True)
                    return False
                return True

            if custom_id in ["admin_tham_gia_ev", "quan_ly_ev", "bat_dau_ev", "dung_mo_ev", "huy_ev"]:
                if not la_admin and not la_mod:
                    await interaction.response.send_message("❌ Chỉ Admin/Mod!", ephemeral=True)
                    return False

            return True
        except Exception as e:
            print(f"❌ Lỗi interaction_check: {e}")
            traceback.print_exc()
            await interaction.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)
            return False

    @discord.ui.button(label="💅 Tham gia", style=discord.ButtonStyle.green)
    async def tham_gia(self, tt, n):
        try:
            if not event_active:
                return await tt.response.send_message("❌ Event chưa bắt đầu!", ephemeral=True)
            if not cho_phep_tham_gia:
                return await tt.response.send_message("❌ Event đã đóng tham gia!", ephemeral=True)
            if tt.user.id in nguoi_tham_gia:
                return await tt.response.send_message("❌ Bạn đã tham gia rồi!", ephemeral=True)
            await tt.response.send_modal(FormThamGia())
        except Exception as e:
            print(f"❌ Lỗi tham_gia: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="🚪 Rời đi", style=discord.ButtonStyle.red, row=1)
    async def roi(self, tt, n):
        try:
            if tt.user.id not in nguoi_tham_gia:
                return await tt.response.send_message("❌ Bạn chưa tham gia!", ephemeral=True)
            ten = nguoi_tham_gia[tt.user.id]
            del nguoi_tham_gia[tt.user.id]
            them_lich_su("roi", tt.user.id, tt.user.id, ten=ten)
            await cap_nhat_event()
            await tt.response.send_message("✅ Đã rời khỏi event!", ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi roi: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="👑 Tham gia", style=discord.ButtonStyle.green, row=2)
    async def admin_tham_gia(self, tt, n):
        try:
            await tt.response.send_modal(FormThamGia())
        except Exception as e:
            print(f"❌ Lỗi admin_tham_gia: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="📋 Quản lý", style=discord.ButtonStyle.blurple, row=2)
    async def quan_ly(self, tt, n):
        try:
            view = SuaDSView()
            await tt.response.send_message("🧑‍🤝‍🧑 **Chọn hành động quản lý:**", view=view, ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi quan_ly: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="▶️ Bắt đầu", style=discord.ButtonStyle.green, row=3)
    async def bat_dau(self, tt, n):
        try:
            if len(nguoi_tham_gia) < 2:
                return await tt.response.send_message("❌ Cần ít nhất 2 người tham gia!", ephemeral=True)
            global cho_phep_tham_gia, vong_hien_tai, ds_da_thang
            cho_phep_tham_gia = False
            vong_hien_tai = 1
            ds_da_thang = []
            await cap_nhat_event()
            await tt.response.send_message(f"✅ Bắt đầu event với {len(nguoi_tham_gia)} người!", ephemeral=True)
            await gui_tran_dau_moi()
        except Exception as e:
            print(f"❌ Lỗi bat_dau: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="⏸️ Đóng/Mở", style=discord.ButtonStyle.red, row=3)
    async def dong_mo(self, tt, n):
        try:
            global cho_phep_tham_gia
            cho_phep_tham_gia = not cho_phep_tham_gia
            await cap_nhat_event()
            status = "mở" if cho_phep_tham_gia else "đóng"
            await tt.response.send_message(f"✅ Đã {status} tham gia!", ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi dong_mo: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="❌ Hủy Event", style=discord.ButtonStyle.red, row=4)
    async def huy_event(self, tt, n):
        try:
            global event_active, nguoi_tham_gia, msg_event, cho_phep_tham_gia
            event_active = False
            nguoi_tham_gia = {}
            cho_phep_tham_gia = True
            try:
                await msg_event.delete()
            except:
                pass
            await tt.response.send_message("✅ Đã hủy event!", ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi huy_event: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

# ===== XỬ LÝ NÚT PHỤ CỦA CHỈNH SỬA DS =====
class SuaDSView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(discord.ui.Button(label="➕ Thêm người", style=discord.ButtonStyle.green, custom_id="them_nguoi_ev"))
        self.add_item(discord.ui.Button(label="➖ Xoá người", style=discord.ButtonStyle.red, custom_id="xoa_nguoi_ev"))
        self.add_item(discord.ui.Button(label="📜 Lịch sử", style=discord.ButtonStyle.grey, custom_id="lich_su_ev2"))

    @discord.ui.button(label="➕ Thêm người", style=discord.ButtonStyle.green, custom_id="them_nguoi_ev")
    async def them_nguoi(self, tt, n):
        try:
            await tt.response.send_modal(ThemNguoiModal())
        except Exception as e:
            print(f"❌ Lỗi them_nguoi: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="➖ Xoá người", style=discord.ButtonStyle.red, custom_id="xoa_nguoi_ev")
    async def xoa_nguoi(self, tt, n):
        try:
            await tt.response.send_modal(XoaNguoiModal())
        except Exception as e:
            print(f"❌ Lỗi xoa_nguoi: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="📜 Lịch sử", style=discord.ButtonStyle.grey, custom_id="lich_su_ev2")
    async def lich_su(self, tt, n):
        try:
            if not lich_su_event:
                return await tt.response.send_message("📭 Chưa có lịch sử nào!", ephemeral=True)
            embed = discord.Embed(title="📜 LỊCH SỬ EVENT", color=0x3498db)
            history_text = ""
            for item in lich_su_event[-20:]:
                action = item["action"]
                nguoi = f"<@{item['nguoi']}>"
                nguoi_th = f"<@{item['nguoi_thuc_hien']}>"
                time = item["time"]
                if action == "tham_gia":
                    history_text += f"✅ {nguoi} đã tham gia lúc {time}\n"
                elif action == "roi":
                    history_text += f"❌ {nguoi} đã rời lúc {time}\n"
                elif action == "sua_ten":
                    history_text += f"✏️ {nguoi} đổi tên từ **{item['old_name']}** → **{item['new_name']}** lúc {time}\n"
                elif action == "them":
                    history_text += f"➕ {nguoi_th} đã thêm {nguoi} ({item['ten']}) lúc {time}\n"
                elif action == "xoa":
                    history_text += f"➖ {nguoi_th} đã xoá {nguoi} ({item['ten']}) lúc {time}\n"
            if history_text:
                embed.description = history_text
            else:
                embed.description = "📭 Chưa có lịch sử nào!"
            await tt.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi lich_su: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

# ===== QUẢN LÝ TRẬN ĐẤU =====
async def gui_tran_dau_moi():
    global vong_hien_tai, ds_da_thang
    try:
        ds_chua_thang = [uid for uid in nguoi_tham_gia.keys() if uid not in ds_da_thang]
        if len(ds_chua_thang) <= 1:
            if len(ds_chua_thang) == 1:
                ds_da_thang.append(ds_chua_thang[0])
            await ket_thuc_event()
            return
        random.shuffle(ds_chua_thang)
        cap_dau = (ds_chua_thang[0], ds_chua_thang[1] if len(ds_chua_thang) > 1 else "admin")
        await gui_tran_dau(cap_dau[0], cap_dau[1])
    except Exception as e:
        print(f"❌ Lỗi gui_tran_dau_moi: {e}")
        traceback.print_exc()

async def gui_tran_dau(u1, u2):
    try:
        k = bot.get_channel(KENH_EVENT_ID)
        if not k:
            return
        t1 = "ADMIN/MOD" if u1 == "admin" else nguoi_tham_gia.get(u1, "?")
        t2 = "ADMIN/MOD" if u2 == "admin" else nguoi_tham_gia.get(u2, "?")
        u1_ten = "ADMIN/MOD" if u1 == "admin" else (bot.get_user(u1).display_name if bot.get_user(u1) else t1)
        u2_ten = "ADMIN/MOD" if u2 == "admin" else (bot.get_user(u2).display_name if bot.get_user(u2) else t2)
        embed = discord.Embed(
            title=f"🥊 TRẬN {len(ds_da_thang) + 1} - VÒNG {vong_hien_tai}",
            description=f"```{u1_ten}``` **VS** ```{u2_ten}```",
            color=0xffaa00
        )
        embed.set_footer(text=f"Vòng {vong_hien_tai} • Trận {len(ds_da_thang) + 1}")
        view = NutChonThang(u1, u2, vong_hien_tai, len(ds_da_thang) + 1)
        await k.send(embed=embed, view=view)
    except Exception as e:
        print(f"❌ Lỗi gui_tran_dau: {e}")
        traceback.print_exc()

class NutChonThang(discord.ui.View):
    def __init__(self, u1, u2, vong, so_tran):
        super().__init__(timeout=600)
        self.u1 = u1
        self.u2 = u2
        self.vong = vong
        self.so_tran = so_tran
        self.da_chon = False
        t1 = "ADMIN/MOD" if u1 == "admin" else nguoi_tham_gia.get(u1, "?")
        t2 = "ADMIN/MOD" if u2 == "admin" else nguoi_tham_gia.get(u2, "?")
        self.add_item(discord.ui.Button(label=f"🏆 {t1}", style=discord.ButtonStyle.green, custom_id="chon_1"))
        self.add_item(discord.ui.Button(label=f"🏆 {t2}", style=discord.ButtonStyle.blurple, custom_id="chon_2"))

    async def interaction_check(self, interaction):
        try:
            if not la_quan_tri(interaction):
                await interaction.response.send_message("❌ Chỉ Admin/Mod!", ephemeral=True)
                return False
            return True
        except Exception as e:
            print(f"❌ Lỗi interaction_check NutChonThang: {e}")
            traceback.print_exc()
            await interaction.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)
            return False

    @discord.ui.button(label="🏆 {t1}", style=discord.ButtonStyle.green, custom_id="chon_1")
    async def chon_1(self, tt, n):
        try:
            if self.da_chon:
                return await tt.response.send_message("❌ Trận này đã có kết quả!", ephemeral=True)
            await self.xu_ly_chon(tt, self.u1)
        except Exception as e:
            print(f"❌ Lỗi chon_1: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="🏆 {t2}", style=discord.ButtonStyle.blurple, custom_id="chon_2")
    async def chon_2(self, tt, n):
        try:
            if self.da_chon:
                return await tt.response.send_message("❌ Trận này đã có kết quả!", ephemeral=True)
            await self.xu_ly_chon(tt, self.u2)
        except Exception as e:
            print(f"❌ Lỗi chon_2: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    async def xu_ly_chon(self, tt, nguoi_thang):
        global ds_da_thang, vong_hien_tai
        try:
            self.da_chon = True
            for child in self.children:
                child.disabled = True
            await tt.message.edit(view=self)
            if nguoi_thang != "admin" and nguoi_thang not in ds_da_thang:
                ds_da_thang.append(nguoi_thang)
            await tt.response.send_message(f"✅ Đã chọn người thắng trận {self.so_tran}!", ephemeral=True)
            await gui_ket_qua(nguoi_thang)
            ds_con_lai = [uid for uid in nguoi_tham_gia.keys() if uid not in ds_da_thang]
            if len(ds_con_lai) <= 1:
                if len(ds_con_lai) == 1:
                    ds_da_thang.append(ds_con_lai[0])
                await ket_thuc_event()
            else:
                vong_hien_tai += 1
                await gui_tran_dau_moi()
        except Exception as e:
            print(f"❌ Lỗi xu_ly_chon: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

async def gui_ket_qua(ut):
    try:
        kq = bot.get_channel(KENH_KET_QUA_ID)
        if not kq:
            return
        tr = "ADMIN/MOD" if ut == "admin" else nguoi_tham_gia.get(ut, "?")
        now = gio_vn()
        embed = discord.Embed(
            title="🎉 CONGRATULATIONS",
            description=f"<@{ut}> **WIN IN EVENT {so_event}**",
            color=0xffd700
        )
        embed.add_field(name="🎮 UserGame:", value=f"```{tr}```", inline=False)
        embed.add_field(name="⏰ Time:", value=now.strftime('%H:%M:%S | %d/%m/%Y'), inline=False)
        embed.set_footer(text="BotByPawPaw")
        await kq.send(content="@everyone", embed=embed)
    except Exception as e:
        print(f"❌ Lỗi gui_ket_qua: {e}")
        traceback.print_exc()

async def ket_thuc_event():
    global event_active
    try:
        event_active = False
        k = bot.get_channel(KENH_EVENT_ID)
        if k:
            await k.send("🏆 **EVENT KẾT THÚC!** Cảm ơn mọi người đã tham gia!")
    except Exception as e:
        print(f"❌ Lỗi ket_thuc_event: {e}")
        traceback.print_exc()

# ===== VIEWS KHÁC =====
class XacNhanDongDon(discord.ui.View):
    def __init__(self, k, sd, id_nt, ldv):
        super().__init__(timeout=30)
        self.k = k
        self.sd = sd
        self.id_nt = id_nt
        self.ldv = ldv

    @discord.ui.button(label="✅ Xác nhận đóng", style=discord.ButtonStyle.red)
    async def xn(self, tt, n):
        try:
            if not la_quan_tri_hoac_dieu_hanh(tt):
                return await tt.response.send_message("❌ Không có quyền!", ephemeral=True)
            await tt.response.send_message("🔒 Đang đóng...", ephemeral=True)
            await gui_nhat_ky_don(tt.client, self.sd, self.id_nt, tt.user.mention, self.ldv)
            await self.k.delete()
        except Exception as e:
            print(f"❌ Lỗi xn: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.grey)
    async def huy(self, tt, n):
        try:
            if not la_quan_tri_hoac_dieu_hanh(tt):
                return await tt.response.send_message("❌ Không có quyền!", ephemeral=True)
            await tt.message.delete()
            await tt.response.send_message("❌ Đã hủy!", ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi huy: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

class BinhChonHoanThanh(discord.ui.View):
    def __init__(self, k, sd, id_nt, ldv):
        super().__init__(timeout=120)
        self.k = k
        self.sd = sd
        self.id_nt = id_nt
        self.ldv = ldv
        self.nb = set()
        self.dca = False
        self.dcnt = False

    @discord.ui.button(label="✅ Hoàn thành", style=discord.ButtonStyle.green)
    async def ht(self, tt, n):
        try:
            nd = tt.user
            la = la_quan_tri_hoac_dieu_hanh(tt)
            lnt = str(nd.id) == str(self.id_nt)
            if not la and not lnt:
                return await tt.response.send_message("❌ Không có quyền!", ephemeral=True)
            if nd.id in self.nb:
                return await tt.response.send_message("❌ Đã bấm!", ephemeral=True)
            self.nb.add(nd.id)
            if la:
                self.dca = True
            if lnt:
                self.dcnt = True
            if self.dca and self.dcnt:
                await tt.response.send_message("✅ Hoàn thành!", ephemeral=True)
                await gui_nhat_ky_don(tt.client, self.sd, self.id_nt, tt.user.mention, self.ldv, "Đơn đã hoàn thành")
                await self.k.delete()
            else:
                ct = []
                if not self.dca:
                    ct.append("Admin/Mod")
                if not self.dcnt:
                    ct.append("Người tạo")
                await tt.response.send_message(f"✅ Cần thêm {' và '.join(ct)}!", ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi ht: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.grey)
    async def huy(self, tt, n):
        try:
            if not la_quan_tri_hoac_dieu_hanh(tt) and str(tt.user.id) != str(self.id_nt):
                return await tt.response.send_message("❌ Không có quyền!", ephemeral=True)
            await tt.message.delete()
            await tt.response.send_message("❌ Đã hủy!", ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi huy: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

class DieuKhienDon(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Đóng đơn", style=discord.ButtonStyle.red, custom_id="dong_don")
    async def dong(self, tt, n):
        try:
            if not la_quan_tri_hoac_dieu_hanh(tt):
                return await tt.response.send_message("❌ Không có quyền!", ephemeral=True)
            tn = tt.channel.name
            p = tn.split("-")
            sd = p[1] if len(p) > 1 else "???"
            dl = tt.channel.topic
            if dl and "|" in dl:
                id_nt, ldv = dl.split("|", 1)
            else:
                id_nt = dl
                ldv = "?"
            await tt.response.send_message(
                embed=discord.Embed(title="⚠️ XÁC NHẬN", description=f"Đóng đơn **#{sd}**?", color=0xff0000),
                view=XacNhanDongDon(tt.channel, sd, id_nt, ldv)
            )
        except Exception as e:
            print(f"❌ Lỗi dong: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="✅ Hoàn thành đơn", style=discord.ButtonStyle.green, custom_id="hoan_thanh_don")
    async def ht(self, tt, n):
        try:
            nd = tt.user
            tn = tt.channel.name
            p = tn.split("-")
            sd = p[1] if len(p) > 1 else "???"
            dl = tt.channel.topic
            if dl and "|" in dl:
                id_nt, ldv = dl.split("|", 1)
            else:
                id_nt = dl
                ldv = "?"
            if not la_quan_tri_hoac_dieu_hanh(tt) and str(nd.id) != str(id_nt):
                return await tt.response.send_message("❌ Không có quyền!", ephemeral=True)
            await tt.response.send_message(
                embed=discord.Embed(title="✅ HOÀN THÀNH", description="Cần Admin/Mod VÀ Người tạo xác nhận!", color=0x00ff00),
                view=BinhChonHoanThanh(tt.channel, sd, id_nt, ldv)
            )
        except Exception as e:
            print(f"❌ Lỗi ht: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="🧾 Đóng kèm lý do", style=discord.ButtonStyle.grey, custom_id="dong_ly_do")
    async def dld(self, tt, n):
        try:
            if not la_quan_tri_hoac_dieu_hanh(tt):
                return await tt.response.send_message("❌ Không có quyền!", ephemeral=True)
            await tt.response.send_modal(BangLyDoDong())
        except Exception as e:
            print(f"❌ Lỗi dld: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

class GiaoDienKiemTraGia(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="💰 Tiền→VND", style=discord.ButtonStyle.green, custom_id="kt_tien")
    async def kt(self, tt, n):
        try:
            await tt.response.send_modal(BangKiemTraTien())
        except Exception as e:
            print(f"❌ Lỗi kt: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="💅 Slay→VND", style=discord.ButtonStyle.green, custom_id="kt_slay")
    async def ks(self, tt, n):
        try:
            await tt.response.send_modal(BangKiemTraSlay())
        except Exception as e:
            print(f"❌ Lỗi ks: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="💵 VND→Tiền", style=discord.ButtonStyle.blurple, custom_id="vnd_tien")
    async def vt(self, tt, n):
        try:
            await tt.response.send_modal(BangVndSangTien())
        except Exception as e:
            print(f"❌ Lỗi vt: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="💳 VND→Slay", style=discord.ButtonStyle.blurple, custom_id="vnd_slay")
    async def vs(self, tt, n):
        try:
            await tt.response.send_modal(BangVndSangSlay())
        except Exception as e:
            print(f"❌ Lỗi vs: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

class GiaoDienTaoDon(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Tạo đơn", style=discord.ButtonStyle.blurple, custom_id="tao_don")
    async def td(self, tt, n):
        try:
            await tt.response.send_modal(BangTaoDon())
        except Exception as e:
            print(f"❌ Lỗi td: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

class GiaoDienServer(discord.ui.View):
    def __init__(self, mc):
        super().__init__(timeout=None)
        try:
            ms = discord.ButtonStyle.green if mc['so_nguoi_choi'] <= 3 else discord.ButtonStyle.blurple
            self.add_item(discord.ui.Button(style=ms, label="THAM GIA", url=f"https://nuxwtghieux.github.io/Snipe/?jobid={mc['id_may']}"))
        except Exception as e:
            print(f"❌ Lỗi GiaoDienServer: {e}")
            traceback.print_exc()

# ===== QUÉT MAP =====
MAX_MAPS = 15

def quet_divaz():
    kq = []
    ct = ""
    td = {'User-Agent': 'Mozilla/5.0'}
    while True:
        dd = f"https://games.roblox.com/v1/games/{ID_MAP}/servers/Public?limit=100"
        if ct:
            dd += f"&cursor={ct}"
        try:
            ph = requests.get(dd, headers=td, timeout=15, verify=False)
            if ph.status_code == 200:
                dl = ph.json()
                cm = dl.get('data', [])
                if not cm:
                    break
                for m in cm:
                    sn = m.get('playing', 0)
                    if sn < 5:
                        existed = False
                        for cached in cac_map_da_gui:
                            if cached['id_may'] == m['id']:
                                cached['so_nguoi_choi'] = sn
                                existed = True
                                break
                        if not existed:
                            kq.append({
                                'id_may': m['id'],
                                'so_nguoi_choi': sn,
                                'ping': m.get('ping', '?'),
                                'fps': m.get('fps', '?'),
                                'toi_da': m.get('maxPlayers', '?')
                            })
                ct = dl.get('nextPageCursor')
                if not ct:
                    break
                time.sleep(1)
            else:
                break
        except Exception as e:
            print(f"❌ Lỗi quet_divaz: {e}")
            traceback.print_exc()
            time.sleep(3)
    all_maps = cac_map_da_gui + kq
    if len(all_maps) > MAX_MAPS:
        all_maps.sort(key=lambda x: x['so_nguoi_choi'], reverse=True)
        all_maps = all_maps[:MAX_MAPS]
    return all_maps

# ===== SLASH COMMANDS =====
@discord.app_commands.command(name="tat_tim_map", description="⏸️ Tạm dừng quét server Divaz")
async def lenh_tat_tim_map(tt):
    try:
        if not la_quan_tri(tt):
            return await tt.response.send_message("❌ Admin only!", ephemeral=True)
        global dang_quet
        dang_quet = False
        await tt.response.send_message("⏸️ Đã tắt!", ephemeral=True)
    except Exception as e:
        print(f"❌ Lỗi lenh_tat_tim_map: {e}")
        traceback.print_exc()
        await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

@discord.app_commands.command(name="bat_tim_map", description="▶️ Bật lại quét server Divaz")
async def lenh_bat_tim_map(tt):
    try:
        if not la_quan_tri(tt):
            return await tt.response.send_message("❌ Admin only!", ephemeral=True)
        global dang_quet
        dang_quet = True
        await tt.response.send_message("▶️ Đã bật! Đang quét ngay...", ephemeral=True)
        await bot.vong_lap_quet()
    except Exception as e:
        print(f"❌ Lỗi lenh_bat_tim_map: {e}")
        traceback.print_exc()
        await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

@discord.app_commands.command(name="startev", description="🎮 Bắt đầu event đấu 1vs1")
async def startev(tt):
    try:
        if not la_quan_tri(tt):
            return await tt.response.send_message("❌ Admin only!", ephemeral=True)
        global event_active, nguoi_tham_gia, msg_event, cho_phep_tham_gia, so_event, vong_hien_tai, ds_da_thang, lich_su_event
        so_event += 1
        event_active = True
        cho_phep_tham_gia = True
        nguoi_tham_gia = {}
        vong_hien_tai = 1
        ds_da_thang = []
        lich_su_event = []
        k = bot.get_channel(KENH_EVENT_ID)
        if not k:
            return await tt.response.send_message("❌ Không tìm thấy kênh!", ephemeral=True)
        embed = discord.Embed(
            title="⚔️ EVENT DIVAZ ĐẤU 1VS1 ⚔️",
            description="ㆍNhấn nút '💅 Tham gia' bên dưới để tham gia vào event này!\nㆍĐã có **0** người tham gia.",
            color=0xff0000
        )
        embed.add_field(name="📋 DANH SÁCH:", value="Chưa có ai tham gia!", inline=False)
        embed.add_field(name="📌 TRẠNG THÁI", value="ㆍEvent đang mở tham gia", inline=False)
        embed.set_footer(text="BotByPawPaw")
        msg_event = await k.send(content="@everyone", embed=embed, view=NutEventChinh())
        await tt.response.send_message("✅ Event đã bắt đầu!", ephemeral=True)
    except Exception as e:
        print(f"❌ Lỗi startev: {e}")
        traceback.print_exc()
        await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

@discord.app_commands.command(name="stopev", description="⏸️ Dừng event")
async def stopev(tt):
    try:
        if not la_quan_tri(tt):
            return await tt.response.send_message("❌ Admin only!", ephemeral=True)
        global event_active
        event_active = False
        await tt.response.send_message("✅ Event đã dừng!", ephemeral=True)
    except Exception as e:
        print(f"❌ Lỗi stopev: {e}")
        traceback.print_exc()
        await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

# ===== BOT CHÍNH =====
class Bot(discord.Client):
    def __init__(self):
        q = discord.Intents.default()
        q.guilds = True
        q.message_content = True
        q.members = True
        q.reactions = True
        super().__init__(intents=q)
        self.cay = app_commands.CommandTree(self)

    async def setup_hook(self):
        try:
            mc = discord.Object(id=ID_MAY_CHU)
            self.cay.add_command(lenh_tat_tim_map)
            self.cay.add_command(lenh_bat_tim_map)
            self.cay.add_command(startev)
            self.cay.add_command(stopev)
            await self.cay.sync(guild=mc)
            await self.cay.sync()
            self.add_view(GiaoDienKiemTraGia())
            self.add_view(GiaoDienTaoDon())
            self.add_view(DieuKhienDon())
            self.add_view(NutEventChinh())
        except Exception as e:
            print(f"❌ Lỗi setup_hook: {e}")
            traceback.print_exc()

    async def on_ready(self):
        try:
            nap_emoji_tu_may_chu(self)
            await phuc_hoi_event_tu_tin_nhan(self)
            if event_active and msg_event:
                try:
                    await msg_event.edit(view=NutEventChinh())
                except Exception as e:
                    print(f"❌ Lỗi edit msg_event: {e}")
                    traceback.print_exc()
            await self.bang_dieu_khien()
            if not self.vong_lap_quet.is_running():
                self.vong_lap_quet.start()
            print(f"🚀 Bot sẵn sàng!")
        except Exception as e:
            print(f"❌ Lỗi on_ready: {e}")
            traceback.print_exc()

    async def bang_dieu_khien(self):
        try:
            kkt = self.get_channel(ID_KENH_KIEM_TRA)
            if kkt:
                async for t in kkt.history(limit=50):
                    if t.author == self.user:
                        try:
                            await t.delete()
                            await asyncio.sleep(0.5)
                        except:
                            pass
                bang_kiem_tra = discord.Embed(
                    title="‼️ HƯỚNG DẪN KIỂM TRA GIÁ 📍",
                    description="━━━━━━━━━━━━━━━━━━━━━━\n"
                               "📌 BƯỚC 1ㆍNhấn '💰 Tiền Divaz → VND' hoặc '💅 Slay → VND' để xem giá.\n\n"
                               "📌 BƯỚC 2ㆍNhập số tiền/slay bạn muốn cày (VD: 100.000K, 2000 slay).\n\n"
                               "📌 BƯỚC 3ㆍSau đó 'gửi' sẽ biết ngay số tiền phải trả.\n\n"
                               "💡 **Nút phụ:** '💵 VND → Tiền cày' và '💳 VND → Slay' để tính ngược từ VND.",
                    color=0x3498db
                )
                bang_kiem_tra.set_footer(text=gio_vn().strftime('%H:%M:%S | %d-%m-%Y'))
                await kkt.send(embed=bang_kiem_tra, view=GiaoDienKiemTraGia())

            kd = self.get_channel(ID_KENH_DON)
            if kd:
                async for t in kd.history(limit=50):
                    if t.author == self.user:
                        try:
                            await t.delete()
                            await asyncio.sleep(0.5)
                        except:
                            pass
                await kd.send(
                    embed=discord.Embed(
                        title="🛒 DỊCH VỤ CÀY TIỀN & SLAY",
                        description="━━━━━━━━━━━━━━━━━━━━━━\n✅ HÃY TẠO ĐƠN Ở NÚT BÊN DƯỚI NẾU BẠN CÓ NHU CẦU CẦN CÀY TIỀN HOẶC SLAY DIVAZ 💤",
                        color=0x3498db
                    ),
                    view=GiaoDienTaoDon()
                )

            global id_tin_nhan_phan_ung
            kpu = self.get_channel(ID_KENH_PHAN_UNG)
            if kpu:
                tnc = None
                async for t in kpu.history(limit=50):
                    if t.author == self.user and t.embeds:
                        tnc = t
                        break
                if tnc:
                    id_tin_nhan_phan_ung = tnc.id
                    try:
                        await tnc.add_reaction(BIEU_TUONG_PHAN_UNG)
                    except:
                        pass
                else:
                    async for t in kpu.history(limit=50):
                        if t.author == self.user:
                            try:
                                await t.delete()
                                await asyncio.sleep(0.5)
                            except:
                                pass
                    bang_vai_tro = discord.Embed(
                        title="🎭 GET ROLE MEMBER",
                        description="━━━━━━━━━━━━━━━━━━━━━━\n"
                               "🌟**ĐỂ XEM CÁC KÊNH CHAT VÀ CHAT, HÃY TICK VÀO BÊN DƯỚI ĐỂ ĐƯỢC NHẬN ROLE↓**\n"
                               "━━━━━━━━━━━━━━━━━━━━━━",
                        color=0x9b59b6
                    )
                    bang_vai_tro.set_footer(text="BotByPawPaw")
                    tn = await kpu.send(embed=bang_vai_tro)
                    await tn.add_reaction(BIEU_TUONG_PHAN_UNG)
                    id_tin_nhan_phan_ung = tn.id
        except Exception as e:
            print(f"❌ Lỗi bang_dieu_khien: {e}")
            traceback.print_exc()

    @tasks.loop(seconds=360)
    async def vong_lap_quet(self):
        global dang_quet, cac_map_da_gui
        if not dang_quet:
            return

        try:
            k = self.get_channel(ID_KENH_QUET)
            if k is None:
                print("❌ Không tìm thấy channel:", ID_KENH_QUET)
                return

            async for msg in k.history(limit=100):
                if msg.author == self.user:
                    try:
                        await msg.delete()
                        await asyncio.sleep(0.5)
                    except discord.HTTPException:
                        pass

            map_moi = quet_divaz()
            if map_moi:
                cac_map_da_gui = map_moi
                for tn in cac_map_da_gui[:MAX_MAPS]:
                    sn = tn['so_nguoi_choi']
                    ma = tn['id_may'][-5:]
                    ms = 0x00ff00 if sn <= 3 else 0xffaa00
                    now = gio_vn()
                    b = discord.Embed(
                        title="🎮 DIVAZ - MÁY CHỦ TRỐNG",
                        description=f"**Mã:** `#{ma}`",
                        color=ms,
                        timestamp=now
                    )
                    b.add_field(
                        name="👥 NGƯỜI CHƠI",
                        value=f"🟢 {sn}/{tn['toi_da']}" if sn <= 3 else f"🟡 {sn}/{tn['toi_da']}",
                        inline=True
                    )
                    b.add_field(name="📶 PING", value=f"{tn['ping']}ms", inline=True)
                    b.add_field(name="🎯 FPS", value=f"{tn['fps']}", inline=True)
                    b.set_thumbnail(url=ANH_NHO)
                    b.set_image(url=ANH_LON)
                    b.set_footer(text=f"BotByPawPaw • {now.strftime('%H:%M:%S | %d/%m/%Y')}")
                    try:
                        await k.send(embed=b, view=GiaoDienServer(tn))
                        await asyncio.sleep(0.3)
                    except Exception as e:
                        print(f"❌ Lỗi gửi embed: {e}")
                        traceback.print_exc()
        except Exception as e:
            print(f"❌ Lỗi vong_lap_quet: {e}")
            traceback.print_exc()

    async def on_raw_reaction_add(self, dl):
        try:
            if dl.message_id != id_tin_nhan_phan_ung:
                return
            if str(dl.emoji) != BIEU_TUONG_PHAN_UNG:
                return
            mc = self.get_guild(dl.guild_id)
            if not mc:
                return
            tv = mc.get_member(dl.user_id)
            if not tv or tv.bot:
                return
            vt = mc.get_role(ID_VAI_TRO_PHAN_UNG)
            if not vt:
                return
            await tv.add_roles(vt)
        except Exception as e:
            print(f"❌ Lỗi on_raw_reaction_add: {e}")
            traceback.print_exc()

    async def on_raw_reaction_remove(self, dl):
        try:
            if dl.message_id != id_tin_nhan_phan_ung:
                return
            if str(dl.emoji) != BIEU_TUONG_PHAN_UNG:
                return
            mc = self.get_guild(dl.guild_id)
            if not mc:
                return
            tv = mc.get_member(dl.user_id)
            if not tv or tv.bot:
                return
            vt = mc.get_role(ID_VAI_TRO_PHAN_UNG)
            if not vt:
                return
            await tv.remove_roles(vt)
        except Exception as e:
            print(f"❌ Lỗi on_raw_reaction_remove: {e}")
            traceback.print_exc()

    async def on_member_join(self, tv):
        try:
            k = self.get_channel(ID_KENH_CHAO_MUNG)
            if not k:
                return
            now = gio_vn()
            mc = tv.guild
            bang = discord.Embed(color=0x2ecc71)
            bang.description = (
                f"# {EMOJI_CANH1}WELCOME{EMOJI_CANH2}\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"# {EMOJI_TRON}┆THÔNG TIN CỦA BẠN:\n"
                f"{EMOJI_BLINKK} *Tên*: {tv.mention}\n"
                f"{EMOJI_BLINKK} *Người dùng*: {tv.name}\n"
                f"{EMOJI_BLINKK} *ID*: `{tv.id}`\n"
                f"{EMOJI_BLINKK} *Ngày tạo*: {tv.created_at.strftime('%d-%m-%Y')}\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"# {EMOJI_TRON}┆CỬA HÀNG PAWPAW:\n"
                f"{EMOJI_BLINKK} Chào mừng bạn đã đến với {mc.name}!\n"
                f"{EMOJI_BLINKK} Bạn là thành viên thứ {mc.member_count} của {mc.name}\n"
                f"{EMOJI_BLINKK} Nếu thắc mắc và cần hỗ trợ, hãy liên hệ <@&{ID_QUAN_TRI}> và <@&{ID_DIEU_HANH}>.\n"
                f"{EMOJI_BLINKK} Nếu muốn tham gia các kênh trò chuyện, hãy vào kênh <#{ID_KENH_PHAN_UNG}> để nhận vai trò.\n\n"
                f"{EMOJI_BLINK2}{EMOJI_BLINK2} CHÚC BẠN MỘT NGÀY TỐT LÀNH {EMOJI_BLINK2}{EMOJI_BLINK2}"
            )
            bang.set_thumbnail(url=tv.display_avatar.url)
            bang.set_image(url=ANH_CHAO_MUNG)
            bang.set_footer(text=now.strftime('%H:%M:%S | %d-%m-%Y'))
            await k.send(embed=bang)
        except Exception as e:
            print(f"❌ Lỗi on_member_join: {e}")
            traceback.print_exc()

    async def on_member_remove(self, tv):
        try:
            k = self.get_channel(ID_KENH_TAM_BIET)
            if not k:
                return
            now = gio_vn()
            mc = tv.guild
            b = discord.Embed(
                title="😢 TẠM BIỆT",
                description=f"**{tv.mention}** đã rời!\n💔 Còn **{mc.member_count}** thành viên",
                color=0xe74c3c
            )
            b.set_thumbnail(url=tv.display_avatar.url)
            b.set_image(url=ANH_TAM_BIET)
            b.set_footer(text=now.strftime('%H:%M:%S | %d-%m-%Y'))
            await k.send(embed=b)
        except Exception as e:
            print(f"❌ Lỗi on_member_remove: {e}")
            traceback.print_exc()


bot = Bot()

if __name__ == '__main__':
    luong = threading.Thread(target=chay_may_chu_web)
    luong.start()
    print("🌐 Web port 8080")
    bot.run(MA_BOT)
