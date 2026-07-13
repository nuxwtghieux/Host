# ============================================================
# PHẦN 1: IMPORT & CẤU HÌNH
# ============================================================
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
import json
import os
import io
import base64
import threading
import aiohttp
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify

# Đường dẫn API của Replit (đã có sẵn route /api/nap)
REPLIT_NAP_API = "https://flask-webhook-service--trunghieugun09.replit.app/api/nap"

def luu_du_lieu():
    """Gửi dữ liệu lên Replit để lưu trữ (tự động cộng dồn)"""
    try:
        for user_id, so_tien in vi_tien.items():
            nap_id = f"SYNC_{user_id}_{int(time.time())}"
            data = {
                "user_id": str(user_id),
                "amount": so_tien,
                "nap_id": nap_id,
                "status": "success"
            }
            requests.post(REPLIT_NAP_API, json=data, timeout=5)
        print("✅ Đã đồng bộ dữ liệu lên Replit")
    except Exception as e:
        print(f"❌ Lỗi đồng bộ lên Replit: {e}")

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

# ============================================================
# PHẦN 2: CẤU HÌNH
# ============================================================
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
ADMIN_ID = 1507006947755430069

# ===== CẤU HÌNH DOITHEGIATOT =====
DOITHEGIATOT_API_KEY = "49a4cf521676fc72aed3daf8804362ea"
DOITHEGIATOT_API_URL = "https://doithegiatot.com/api"

# ===== EMOJI & ẢNH =====
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

# ===== LOẠI THẺ =====
LOAI_THE = [
    {"name": "Zing", "value": 14},
    {"name": "Viettel", "value": 1},
    {"name": "Vinaphone", "value": 3},
    {"name": "Mobifone", "value": 2},
    {"name": "Gate", "value": 15},
    {"name": "Vcoin", "value": 4},
    {"name": "Garena", "value": 6},
    {"name": "Vietnamobile", "value": 16}
]

MENH_GIA = [5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000]

# ============================================================
# PHẦN 3: BIẾN TOÀN CỤC
# ============================================================
dem_don = 0
dang_quet = True
id_tin_nhan_phan_ung = None
cac_map_da_gui = []

# ===== BIẾN NẠP CARD =====
danh_sach_cam = {}
nguoi_dung_bi_cam = set()
lich_su_nap = {}
pending_transactions = {}
vi_tien = {}
temp_data = {}
dang_check = {}

# ===== BIẾN EVENT =====
event_active = False
cho_phep_tham_gia = True
nguoi_tham_gia = {}
msg_event = None
so_event = 1
vong_hien_tai = 1
ds_da_thang = []
lich_su_event = []

# ============================================================
# PHẦN 4: HÀM LỊCH SỬ & KHÔI PHỤC EVENT
# ============================================================
def them_lich_su(action, nguoi, nguoi_thuc_hien, **kwargs):
    lich_su_event.append({
        "action": action,
        "nguoi": nguoi,
        "nguoi_thuc_hien": nguoi_thuc_hien,
        "time": gio_vn().strftime("%H:%M:%S %d/%m/%Y"),
        **kwargs
    })

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
                                if "**" in line and "<@" in line:
                                    match_uid = re.search(r'<@(\d+)>', line)
                                    match_ten = re.search(r'\*\*\d+\.\*\*\s+(.+?)\s+\(<@', line)
                                    if match_uid and match_ten:
                                        uid = int(match_uid.group(1))
                                        ten = match_ten.group(1).strip()
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

# ============================================================
# PHẦN 5: CÁC HÀM TIỆN ÍCH
# ============================================================
    
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
        if tt.guild is not None:
            if tv.guild_permissions.administrator:
                return True
            return any(r.id == ID_QUAN_TRI for r in tv.roles)
        else:
            return tv.id == ADMIN_ID
    except Exception as e:
        print(f"❌ Lỗi la_quan_tri: {e}")
        traceback.print_exc()
        return False

def la_quan_tri_hoac_dieu_hanh(tt: discord.Interaction):
    try:
        tv = tt.user
        if tt.guild is not None:
            return any(r.id in [ID_QUAN_TRI, ID_DIEU_HANH] for r in tv.roles)
        else:
            return tv.id == ADMIN_ID
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

def lay_chiet_khau_tu_api(loai_the, menhgia):
    url = f"https://doithegiatot.com/api/cardrate?apikey={DOITHEGIATOT_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('Code') == 1:
                for card in data.get('Data', []):
                    if card.get('id') == loai_the:
                        for price in card.get('prices', []):
                            if price.get('price') == menhgia and price.get('status') is True:
                                return price.get('rate')
        return None
    except Exception as e:
        print(f"❌ Lỗi lấy chiết khấu: {e}")
        return None

def gui_the_doithegiatot(pin, seri, card_type, amount, requestid):
    url = f"{DOITHEGIATOT_API_URL}/card"
    payload = {
        "ApiKey": DOITHEGIATOT_API_KEY,
        "Pin": pin,
        "Seri": seri,
        "CardType": card_type,
        "CardValue": amount,
        "requestid": requestid
    }
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        print(f"📤 [GỬI THẺ] Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"❌ Lỗi gửi thẻ: {e}")
        return None

def kiem_tra_bi_cam(user_id):
    if user_id in nguoi_dung_bi_cam:
        return True
    if user_id in danh_sach_cam and danh_sach_cam[user_id].get('bi_cam', False):
        return True
    return False

def cap_nhat_lan_sai(user_id, pin, seri):
    if user_id not in danh_sach_cam:
        danh_sach_cam[user_id] = {'so_lan_sai': 0, 'bi_cam': False}
    danh_sach_cam[user_id]['so_lan_sai'] += 1
    if danh_sach_cam[user_id]['so_lan_sai'] >= 2:
        danh_sach_cam[user_id]['bi_cam'] = True
        nguoi_dung_bi_cam.add(user_id)
        return True
    return False

def cap_nhat_webhook(user_id, amount, nap_id, status="success"):
    try:
        url = "https://flask-webhook-service--trunghieugun09.replit.app/api/nap"
        data = {
            "user_id": str(user_id),
            "amount": amount,
            "nap_id": nap_id,
            "status": status,
            "time": datetime.now().strftime('%H:%M:%S %d/%m/%Y')
        }
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print(f"✅ Đã cập nhật webhook: {nap_id}")
        else:
            print(f"⚠️ Lỗi cập nhật webhook: {response.status_code}")
    except Exception as e:
        print(f"❌ Lỗi gửi webhook: {e}")

async def gui_bao_cao_admin(bot, title, description, color, fields=None):
    try:
        admin = await bot.fetch_user(ADMIN_ID)
        embed = discord.Embed(title=title, description=description, color=color)
        if fields:
            for name, value in fields:
                embed.add_field(name=name, value=value, inline=False)
        embed.set_footer(text=f"BotPawPank • {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
        await admin.send(embed=embed)
        print(f"✅ Đã gửi báo cáo cho Admin")
    except Exception as e:
        print(f"❌ Lỗi gửi báo cáo Admin: {e}")

# ============================================================
# PHẦN 7: MODALS
# ============================================================
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
                embed=discord.Embed(title="🎫 CÓ ĐƠN", description=f"Đơn: **{sd}**\nDịch vụ: **{ldv}**\nNgười tạo: {nd.mention}", color=0x3498db),
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

# ============================================================
# PHẦN 8: MODALS EVENT
# ============================================================
class FormThamGia(discord.ui.Modal, title="Tham gia Event"):
    ten = discord.ui.TextInput(label="Hãy điền tên của bạn", placeholder="Nhập tên hiển thị trong game", required=True, max_length=50)
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
    ten_moi = discord.ui.TextInput(label="Tên mới của bạn", placeholder="Nhập tên muốn đổi", required=True, max_length=50)
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
    user_id = discord.ui.TextInput(label="ID Discord của người cần thêm", placeholder="Nhập ID (ví dụ: 123456789012345678)", required=True, max_length=20)
    ten = discord.ui.TextInput(label="Tên Roblox", placeholder="Nhập tên Roblox của họ", required=True, max_length=50)
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
    user_id = discord.ui.TextInput(label="ID Discord của người cần xoá", placeholder="Nhập ID", required=True, max_length=20)
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
            
class NhapTheModal(discord.ui.Modal, title="💳 Nhập thông tin thẻ"):
    pin = discord.ui.TextInput(label="🔢 Mã thẻ", placeholder="Nhập mã số trên thẻ", required=True, max_length=30)
    seri = discord.ui.TextInput(label="🔢 Seri thẻ", placeholder="Nhập seri trên thẻ", required=True, max_length=30)

    async def on_submit(self, interaction):
        user_id = interaction.user.id
        
        # Lấy dữ liệu từ bot (tuyệt đối không dùng biến toàn cục temp_data)
        if user_id not in interaction.client.temp_data:
            await interaction.response.send_message("⏳ Phiên làm việc đã hết. Vui lòng dùng lại `/naptien card` để bắt đầu lại từ đầu nhé!", ephemeral=True)
            return
            
        data = interaction.client.temp_data[user_id]
        
        if kiem_tra_bi_cam(user_id):
            embed_error = discord.Embed(title="🚫 BỊ CẤM", description="Bạn đã bị cấm nạp thẻ! Liên hệ Admin!", color=0xff0000)
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
            return
            
        # Lưu lại dữ liệu vào Bot để xác nhận
        interaction.client.temp_data[user_id] = {
            "loai_the": data["loai_the"],
            "loai_the_name": data["loai_the_name"],
            "menhgia": data["menhgia"],
            "rate": data["rate"],
            "tien_nhan_du_kien": data["tien_nhan_du_kien"],
            "pin": self.pin.value,
            "seri": self.seri.value
        }
        
        embed = discord.Embed(
            title="**📋 XÁC NHẬN THÔNG TIN CARD**",
            description="Hãy xem lại đã đúng mệnh giá, mã thẻ, serial hay chưa rồi mới gửi thẻ đi!",
            color=0xffaa00
        )
        embed.add_field(name="**💳 LOẠI THẺ**", value=f"```{data['loai_the_name']}```", inline=True)
        embed.add_field(name="💰 MỆNH GIÁ", value=f"```{data['menhgia']:,} VND```", inline=True)
        embed.add_field(name="🔢 MÃ THẺ", value=f"```{self.pin.value}```", inline=True)
        embed.add_field(name="🔢 SERI", value=f"```{self.seri.value}```", inline=True)
        embed.add_field(name="💰 SỐ TIỀN NHẬN ĐƯỢC", value=f"```{data['tien_nhan_du_kien']:,} VND``` *(Chiết khấu {data['rate']}%)*", inline=False)
        embed.add_field(name="⚠️ LƯU Ý", value="**• Sai mã thẻ bị trừ 50%!**\n**• Sai mệnh giá không cộng tiền!**\n**• Quá 2 lần sai bị cấm!**", inline=False)
        embed.set_footer(text=f"PawPank • {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
        view = XacNhanTheView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
# ============================================================
# PHẦN 9: HÀM CẬP NHẬT EVENT
# ============================================================
async def cap_nhat_event():
    global msg_event, nguoi_tham_gia, cho_phep_tham_gia
    try:
        if not msg_event:
            return
        ds = ""
        if nguoi_tham_gia:
            for i, (uid, ten) in enumerate(nguoi_tham_gia.items(), 1):
                ds += f"**{i}.** {ten} (<@{uid}>)\n"
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

# ============================================================
# PHẦN 10: VIEWS
# ============================================================
class NutEventChinh(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: discord.Interaction):
        try:
            custom_id = interaction.data.get("custom_id")
            if custom_id == "roi_ev":
                la_admin = la_quan_tri(interaction)
                la_mod = la_quan_tri_hoac_dieu_hanh(interaction)
                if la_admin or la_mod:
                    await interaction.response.send_message("❌ Admin/Mod không thể rời đi! Hãy dùng /csds để quản lý!", ephemeral=True)
                    return False
                la_paw = any(r.id == ID_MEMBER_PAW for r in interaction.user.roles)
                if not la_paw:
                    await interaction.response.send_message("❌ Bạn không có quyền!", ephemeral=True)
                    return False
            return True
        except Exception:
            traceback.print_exc()
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)
            return False

    @discord.ui.button(label="💅 Tham gia", style=discord.ButtonStyle.green, custom_id="tham_gia_ev", row=0)
    async def tham_gia(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if not event_active:
                return await interaction.response.send_message("❌ Event chưa bắt đầu!", ephemeral=True)
            if not cho_phep_tham_gia:
                return await interaction.response.send_message("❌ Event đã đóng tham gia!", ephemeral=True)
            if interaction.user.id in nguoi_tham_gia:
                return await interaction.response.send_message("❌ Bạn đã tham gia rồi!", ephemeral=True)
            await interaction.response.send_modal(FormThamGia())
        except Exception as e:
            print(f"❌ Lỗi tham_gia: {e}")
            traceback.print_exc()
            await interaction.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="🚪 Rời đi", style=discord.ButtonStyle.red, custom_id="roi_ev", row=0)
    async def roi(self, interaction: discord.Interaction, button: discord.ui.Button):
        global nguoi_tham_gia
        try:
            if not event_active:
                return await interaction.response.send_message("❌ Event chưa bắt đầu!", ephemeral=True)
            if interaction.user.id not in nguoi_tham_gia:
                return await interaction.response.send_message("❌ Bạn chưa tham gia event!", ephemeral=True)
            ten = nguoi_tham_gia[interaction.user.id]
            del nguoi_tham_gia[interaction.user.id]
            them_lich_su("roi", interaction.user.id, interaction.user.id, ten=ten)
            await cap_nhat_event()
            await interaction.response.send_message("✅ Bạn đã rời khỏi event!", ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi roi: {e}")
            traceback.print_exc()
            await interaction.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="✏️ Chỉnh sửa tên", style=discord.ButtonStyle.grey, custom_id="sua_ten_ev", row=0)
    async def sua_ten(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if not event_active:
                return await interaction.response.send_message("❌ Event chưa bắt đầu!", ephemeral=True)
            if interaction.user.id not in nguoi_tham_gia:
                return await interaction.response.send_message("❌ Bạn chưa tham gia event!", ephemeral=True)
            await interaction.response.send_modal(SuaTenModal())
        except Exception as e:
            print(f"❌ Lỗi sua_ten: {e}")
            traceback.print_exc()
            await interaction.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

class SuaDSView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="➕ Thêm người", style=discord.ButtonStyle.green, custom_id="them_nguoi_ev")
    async def them_nguoi(self, tt: discord.Interaction, button: discord.ui.Button):
        try:
            await tt.response.send_modal(ThemNguoiModal())
        except Exception as e:
            print(f"❌ Lỗi them_nguoi: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="➖ Xoá người", style=discord.ButtonStyle.red, custom_id="xoa_nguoi_ev")
    async def xoa_nguoi(self, tt: discord.Interaction, button: discord.ui.Button):
        try:
            await tt.response.send_modal(XoaNguoiModal())
        except Exception as e:
            print(f"❌ Lỗi xoa_nguoi: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="📜 Lịch sử", style=discord.ButtonStyle.grey, custom_id="lich_su_ev2")
    async def lich_su(self, tt: discord.Interaction, button: discord.ui.Button):
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

class ChonTheView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.add_item(discord.ui.Button(label="💳 Điền Seri/Mã thẻ", style=discord.ButtonStyle.green, custom_id="nhap_the"))
        self.add_item(discord.ui.Button(label="❌ Hủy", style=discord.ButtonStyle.red, custom_id="huy_the"))

class XacNhanTheView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="✅ Đồng ý gửi thẻ", style=discord.ButtonStyle.green, custom_id="gui_the")
    async def gui_the_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.red, custom_id="huy_the")
    async def huy_the_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
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

# ============================================================
# PHẦN 11: QUẢN LÝ TRẬN ĐẤU
# ============================================================
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

    @discord.ui.button(label="🏆 Người 1", style=discord.ButtonStyle.green, custom_id="chon_1")
    async def chon_1(self, tt, n):
        try:
            if self.da_chon:
                return await tt.response.send_message("❌ Trận này đã có kết quả!", ephemeral=True)
            await self.xu_ly_chon(tt, self.u1)
        except Exception as e:
            print(f"❌ Lỗi chon_1: {e}")
            traceback.print_exc()
            await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

    @discord.ui.button(label="🏆 Người 2", style=discord.ButtonStyle.blurple, custom_id="chon_2")
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

# ============================================================
# PHẦN 13: QUÉT MAP
# ============================================================
MAX_MAPS = 15

def quet_divaz():
    """Quét TẤT CẢ server Divaz để tìm server trống nhất"""
    td = {'User-Agent': 'Mozilla/5.0'}
    tat_ca_server = []
    cursor = ""
    
    try:
        while True:
            url = f"https://games.roblox.com/v1/games/{ID_MAP}/servers/Public?limit=100"
            if cursor:
                url += f"&cursor={cursor}"
            
            ph = requests.get(url, headers=td, timeout=15, verify=False)
            
            if ph.status_code != 200:
                break
            
            dl = ph.json()
            cm = dl.get('data', [])
            
            if not cm:
                break
            
            tat_ca_server.extend(cm)
            
            cursor = dl.get('nextPageCursor')
            if not cursor:
                break
            
            time.sleep(0.5)
    
    except:
        pass
    
    if tat_ca_server:
        # Sắp xếp server theo số người chơi tăng dần (ít người nhất lên đầu)
        tat_ca_server.sort(key=lambda x: x.get('playing', 999))
        
        # Chọn server ít người nhất
        for m in tat_ca_server:
            sn = m.get('playing', 0)
            if sn < 5:
                return {
                    'id_may': m['id'],
                    'so_nguoi_choi': sn,
                    'ping': m.get('ping', '?'),
                    'fps': m.get('fps', '?'),
                    'toi_da': m.get('maxPlayers', '?')
                }
    
    return None
    
# ============================================================
# PHẦN 14: SLASH COMMANDS
# ============================================================
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

@discord.app_commands.command(name="bdev", description="▶️ Bắt đầu Event (Admin/Mod)")
async def bdev(tt: discord.Interaction):
    try:
        if not (la_quan_tri(tt) or la_quan_tri_hoac_dieu_hanh(tt)):
            return await tt.response.send_message("❌ Chỉ Admin/Mod mới dùng được!", ephemeral=True)
        global vong_hien_tai, ds_da_thang, cho_phep_tham_gia
        if not event_active:
            return await tt.response.send_message("❌ Event chưa bắt đầu!", ephemeral=True)
        if len(nguoi_tham_gia) < 2:
            return await tt.response.send_message("❌ Cần ít nhất 2 người tham gia!", ephemeral=True)
        cho_phep_tham_gia = False
        await cap_nhat_event()
        vong_hien_tai = 1
        ds_da_thang = []
        await gui_tran_dau_moi()
        await tt.response.send_message("✅ Event đã bắt đầu!", ephemeral=True)
    except Exception as e:
        print(f"❌ Lỗi bdev: {e}")
        traceback.print_exc()
        await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

@discord.app_commands.command(name="csds", description="📋 Chỉnh sửa danh sách người chơi (Admin/Mod)")
async def csds(tt: discord.Interaction):
    try:
        if not (la_quan_tri(tt) or la_quan_tri_hoac_dieu_hanh(tt)):
            return await tt.response.send_message("❌ Chỉ Admin/Mod mới dùng được!", ephemeral=True)
        if not event_active:
            return await tt.response.send_message("❌ Event chưa bắt đầu!", ephemeral=True)
        view = SuaDSView()
        await tt.response.send_message("📋 **Chỉnh sửa danh sách người chơi:**", view=view, ephemeral=True)
    except Exception as e:
        print(f"❌ Lỗi csds: {e}")
        traceback.print_exc()
        await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

@discord.app_commands.command(name="offjoin", description="🔒 Đóng tham gia Event (Admin/Mod)")
async def offjoin(tt: discord.Interaction):
    try:
        if not (la_quan_tri(tt) or la_quan_tri_hoac_dieu_hanh(tt)):
            return await tt.response.send_message("❌ Chỉ Admin/Mod mới dùng được!", ephemeral=True)
        global cho_phep_tham_gia
        if not event_active:
            return await tt.response.send_message("❌ Event chưa bắt đầu!", ephemeral=True)
        cho_phep_tham_gia = False
        await cap_nhat_event()
        await tt.response.send_message("🔒 Đã đóng tham gia Event!", ephemeral=True)
    except Exception as e:
        print(f"❌ Lỗi offjoin: {e}")
        traceback.print_exc()
        await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

@discord.app_commands.command(name="onjoin", description="🔓 Mở tham gia Event (Admin/Mod)")
async def onjoin(tt: discord.Interaction):
    try:
        if not (la_quan_tri(tt) or la_quan_tri_hoac_dieu_hanh(tt)):
            return await tt.response.send_message("❌ Chỉ Admin/Mod mới dùng được!", ephemeral=True)
        global cho_phep_tham_gia
        if not event_active:
            return await tt.response.send_message("❌ Event chưa bắt đầu!", ephemeral=True)
        cho_phep_tham_gia = True
        await cap_nhat_event()
        await tt.response.send_message("🔓 Đã mở tham gia Event!", ephemeral=True)
    except Exception as e:
        print(f"❌ Lỗi onjoin: {e}")
        traceback.print_exc()
        await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

@discord.app_commands.command(name="cancelev", description="❌ Hủy Event (Admin/Mod)")
async def cancelev(tt: discord.Interaction):
    try:
        if not (la_quan_tri(tt) or la_quan_tri_hoac_dieu_hanh(tt)):
            return await tt.response.send_message("❌ Chỉ Admin/Mod mới dùng được!", ephemeral=True)
        global event_active, nguoi_tham_gia, msg_event
        if not event_active:
            return await tt.response.send_message("❌ Không có event nào đang chạy!", ephemeral=True)
        nguoi_tham_gia.clear()
        event_active = False
        if msg_event:
            try:
                await msg_event.delete()
                msg_event = None
            except:
                pass
        await tt.response.send_message("❌ Đã hủy Event!", ephemeral=True)
    except Exception as e:
        print(f"❌ Lỗi cancelev: {e}")
        traceback.print_exc()
        await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

@discord.app_commands.command(name="lsnew", description="📜 Hiển thị lịch sử mới nhất (Admin/Mod)")
async def lsnew(tt: discord.Interaction):
    try:
        if not (la_quan_tri(tt) or la_quan_tri_hoac_dieu_hanh(tt)):
            return await tt.response.send_message("❌ Chỉ Admin/Mod mới dùng được!", ephemeral=True)
        if not lich_su_event:
            return await tt.response.send_message("📭 Chưa có lịch sử nào!", ephemeral=True)
        item = lich_su_event[-1]
        action = item["action"]
        nguoi = f"<@{item['nguoi']}>"
        nguoi_th = f"<@{item['nguoi_thuc_hien']}>"
        time = item["time"]
        embed = discord.Embed(title="📜 LỊCH SỬ MỚI NHẤT", color=0x3498db)
        if action == "tham_gia":
            embed.add_field(name="Hành động", value="✅ Tham gia", inline=False)
            embed.add_field(name="Người thực hiện", value=nguoi, inline=True)
            embed.add_field(name="Người bị tác động", value=nguoi, inline=True)
            embed.add_field(name="Tên", value=item.get('ten', 'N/A'), inline=True)
        elif action == "roi":
            embed.add_field(name="Hành động", value="❌ Rời đi", inline=False)
            embed.add_field(name="Người thực hiện", value=nguoi, inline=True)
            embed.add_field(name="Người bị tác động", value=nguoi, inline=True)
            embed.add_field(name="Tên", value=item.get('ten', 'N/A'), inline=True)
        elif action == "sua_ten":
            embed.add_field(name="Hành động", value="✏️ Sửa tên", inline=False)
            embed.add_field(name="Người thực hiện", value=nguoi, inline=True)
            embed.add_field(name="Tên cũ", value=item.get('old_name', 'N/A'), inline=True)
            embed.add_field(name="Tên mới", value=item.get('new_name', 'N/A'), inline=True)
        elif action == "them":
            embed.add_field(name="Hành động", value="➕ Thêm người", inline=False)
            embed.add_field(name="Người thực hiện", value=nguoi_th, inline=True)
            embed.add_field(name="Người bị tác động", value=nguoi, inline=True)
            embed.add_field(name="Tên", value=item.get('ten', 'N/A'), inline=True)
        elif action == "xoa":
            embed.add_field(name="Hành động", value="➖ Xoá người", inline=False)
            embed.add_field(name="Người thực hiện", value=nguoi_th, inline=True)
            embed.add_field(name="Người bị tác động", value=nguoi, inline=True)
            embed.add_field(name="Tên", value=item.get('ten', 'N/A'), inline=True)
        embed.add_field(name="⏰ Thời gian", value=time, inline=False)
        embed.set_footer(text=f"Tổng số lịch sử: {len(lich_su_event)}")
        await tt.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"❌ Lỗi lsnew: {e}")
        traceback.print_exc()
        await tt.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

# ============================================================
# PHẦN 15: NHÓM LỆNH NẠP TIỀN
# ============================================================
class NapTienGroup(app_commands.Group):
    """💰 Nạp tiền vào PawPank"""
    
    @app_commands.command(name="bank", description="💰 Nạp qua ngân hàng")
    @app_commands.describe(so_tien="Số tiền (VD: 100000, 200k)")
    async def bank(self, interaction: discord.Interaction, so_tien: str):
        await interaction.response.send_message("⏳ Đang phát triển!", ephemeral=True)
    
    @app_commands.command(name="card", description="💳 Nạp qua thẻ cào")
    @app_commands.describe(loai_the="Chọn loại thẻ", menhgia="Chọn mệnh giá")
    @app_commands.choices(
        loai_the=[app_commands.Choice(name=item["name"], value=str(item["value"])) for item in LOAI_THE],
        menhgia=[app_commands.Choice(name=f"{v:,} VND", value=str(v)) for v in MENH_GIA]
    )
    async def card(self, interaction: discord.Interaction, loai_the: app_commands.Choice[str], menhgia: app_commands.Choice[str]):
        user = interaction.user
        
        if interaction.guild is not None:
            embed_error = discord.Embed(
                title="❌ LỖI",
                description="Lệnh này chỉ được sử dụng trong **tin nhắn riêng** với bot!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
            return
        
        if kiem_tra_bi_cam(user.id):
            embed_error = discord.Embed(
                title="🚫 BỊ CẤM NẠP THẺ",
                description="Bạn đã nhập sai quá 2 lần. Vui lòng liên hệ Admin!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
            return
        
        so_tien = int(menhgia.value)
        loai_the_value = int(loai_the.value)
        loai_the_name = loai_the.name
        
        rate = lay_chiet_khau_tu_api(loai_the_value, so_tien)
        if rate is None:
            embed_error = discord.Embed(
                title="❌ LỖI",
                description=f"Không tìm thấy chiết khấu cho {loai_the_name} mệnh giá {so_tien:,} VND!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
            return
        
        tien_nhan_du_kien = int(so_tien - (so_tien * rate / 100))
        
        interaction.client.temp_data[user.id] = {
            "loai_the": loai_the_value,
            "loai_the_name": loai_the_name,
            "menhgia": so_tien,
            "rate": rate,
            "tien_nhan_du_kien": tien_nhan_du_kien
        }
        
        view = ChonTheView(user.id)
        
        embed = discord.Embed(
            title="**💳 NẠP CARD**",
            description=f"**Loại thẻ:** {loai_the_name}\n**Mệnh giá:** {so_tien:,} VND\n**Số tiền nhận được: {tien_nhan_du_kien:,} VND** *(Chiết khấu {rate}%)*",
            color=0x00ff00
        )
        embed.add_field(
            name="⚠️ LƯU Ý",
            value="**❌ Không spam! Quá 2 lần sai sẽ bị cấm!**\n**❌ Sai mã thẻ bị trừ 50%!**\n**❌ Sai mệnh giá không cộng tiền!**",
            inline=False
        )
        embed.add_field(
            name="📌 HƯỚNG DẪN",
            value="1. Bấm nút **'Điền Seri/Mã thẻ'**\n2. Nhập **Mã thẻ** và **Seri**\n3. Xác nhận thông tin\n4. Chờ xử lý",
            inline=False
        )
        embed.set_footer(text=f"BotPawPank • {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
        
        await interaction.response.send_message(content=f"🔔 **{user.mention}**", embed=embed, view=view)

@discord.app_commands.command(name="sodu", description="💰 Xem số dư ví của bạn")
async def sodu(interaction: discord.Interaction):
    user = interaction.user
    so_tien = vi_tien.get(user.id, 0)
    
    embed = discord.Embed(
        title="💰 SỐ DƯ VÍ",
        description=f"**{user.mention}**",
        color=0x00ff00
    )
    embed.add_field(name="Số dư hiện tại", value=f"**{so_tien:,} VND**", inline=False)
    embed.set_footer(text=f"BotPawPank • {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
    
    if interaction.guild is not None:
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)

@discord.app_commands.command(name="lichsunap", description="📋 Xem lịch sử nạp tiền")
async def lichsunap(interaction: discord.Interaction):
    user = interaction.user
    if user.id not in lich_su_nap or not lich_su_nap[user.id]:
        embed_empty = discord.Embed(
            title="📭 LỊCH SỬ TRỐNG",
            description="Bạn chưa có lịch sử nạp tiền nào!",
            color=0xffaa00
        )
        await interaction.response.send_message(embed=embed_empty, ephemeral=True)
        return
    
    ls = lich_su_nap[user.id][-10:]
    tong_tien = sum(item['amount'] for item in lich_su_nap[user.id])
    
    embed = discord.Embed(
        title="📋 LỊCH SỬ NẠP TIỀN",
        description=f"**Tổng:** {tong_tien:,} VND | **Số lần:** {len(lich_su_nap[user.id])}",
        color=0x3498db
    )
    for i, item in enumerate(reversed(ls), 1):
        embed.add_field(name=f"💰 Lần {i}", value=f"**Số tiền:** {item['amount']:,} VND\n**Thời gian:** {item['time']}", inline=False)
    embed.set_footer(text="Hiển thị 10 lịch sử gần nhất")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@discord.app_commands.command(name="tru", description="💸 Trừ tiền của user (Admin)")
@app_commands.describe(
    user="Chọn user cần trừ tiền",
    so_tien="Số tiền cần trừ (VND)",
    ly_do="Lý do trừ tiền (tùy chọn)"
)
async def tru_tien(
    interaction: discord.Interaction,
    user: discord.User,
    so_tien: int,
    ly_do: str = None
):
    try:
        if not la_quan_tri(interaction):
            embed_error = discord.Embed(
                title="❌ LỖI",
                description="Chỉ Admin mới có quyền sử dụng lệnh này!",
                color=0xff0000
            )
            return await interaction.response.send_message(embed=embed_error, ephemeral=True)
        
        if so_tien <= 0:
            embed_error = discord.Embed(
                title="❌ LỖI",
                description="Số tiền phải lớn hơn 0!",
                color=0xff0000
            )
            return await interaction.response.send_message(embed=embed_error, ephemeral=True)
        
        user_id = user.id
        so_du_hien_tai = vi_tien.get(user_id, 0)
        
        if so_du_hien_tai < so_tien:
            embed_error = discord.Embed(
                title="❌ LỖI",
                description=f"User {user.mention} không đủ tiền!\n**Số dư hiện tại:** {so_du_hien_tai:,} VND\n**Cần trừ:** {so_tien:,} VND",
                color=0xff0000
            )
            return await interaction.response.send_message(embed=embed_error, ephemeral=True)
        
        so_du_moi = so_du_hien_tai - so_tien
        vi_tien[user_id] = so_du_moi
        
        if user_id not in lich_su_nap:
            lich_su_nap[user_id] = []
        lich_su_nap[user_id].append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'amount': -so_tien,
            'content': f"TRỪ TIỀN - {ly_do if ly_do else 'Không có lý do'}",
            'admin': interaction.user.id
        })
        
        embed_success = discord.Embed(
            title="✅ TRỪ TIỀN THÀNH CÔNG!",
            description=f"Đã trừ **{so_tien:,} VND** của {user.mention}",
            color=0x00ff00
        )
        embed_success.add_field(name="📊 THÔNG TIN", 
            value=f"**User:** {user.mention} (`{user_id}`)\n"
                  f"**Số tiền trừ:** {so_tien:,} VND\n"
                  f"**Số dư cũ:** {so_du_hien_tai:,} VND\n"
                  f"**Số dư mới:** {so_du_moi:,} VND\n"
                  f"**Lý do:** {ly_do if ly_do else 'Không có'}\n"
                  f"**Admin:** {interaction.user.mention}", 
            inline=False
        )
        embed_success.set_footer(text=f"BotPawPank • {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
        await interaction.response.send_message(embed=embed_success)
        
        try:
            dm_embed = discord.Embed(
                title="💸 BẠN ĐÃ BỊ TRỪ TIỀN",
                description=f"Admin {interaction.user.mention} đã trừ **{so_tien:,} VND** trong ví của bạn!",
                color=0xff0000
            )
            dm_embed.add_field(name="📊 CHI TIẾT", 
                value=f"**Số tiền trừ:** {so_tien:,} VND\n"
                      f"**Số dư cũ:** {so_du_hien_tai:,} VND\n"
                      f"**Số dư mới:** {so_du_moi:,} VND\n"
                      f"**Lý do:** {ly_do if ly_do else 'Không có'}\n"
                      f"**Thời gian:** {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}",
                inline=False
            )
            dm_embed.set_footer(text="BotPawPank")
            await user.send(embed=dm_embed)
        except:
            pass
        
        await gui_bao_cao_admin(
            bot,
            title="📊 THÔNG BÁO TRỪ TIỀN",
            description=f"Admin {interaction.user.mention} đã trừ tiền của {user.mention}",
            color=0xffaa00,
            fields=[
                ("👤 User bị trừ", f"{user.mention} (`{user_id}`)"),
                ("💰 Số tiền trừ", f"{so_tien:,} VND"),
                ("📊 Số dư mới", f"{so_du_moi:,} VND"),
                ("📝 Lý do", ly_do if ly_do else "Không có"),
                ("👤 Admin thực hiện", interaction.user.mention)
            ]
        )
        
    except Exception as e:
        print(f"❌ Lỗi tru_tien: {e}")
        traceback.print_exc()
        embed_error = discord.Embed(
            title="❌ LỖI",
            description=f"Đã xảy ra lỗi: {str(e)}",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed_error, ephemeral=True)


@discord.app_commands.command(name="congtien", description="💰 Cộng tiền vào ví user (Admin)")
@app_commands.describe(
    user="Chọn user cần cộng tiền",
    so_tien="Số tiền cần cộng (VND)",
    ly_do="Lý do cộng tiền (tùy chọn)"
)
async def cong_tien(
    interaction: discord.Interaction,
    user: discord.User,
    so_tien: int,
    ly_do: str = None
):
    try:
        if not la_quan_tri(interaction):
            embed_error = discord.Embed(
                title="❌ LỖI",
                description="Chỉ Admin mới có quyền sử dụng lệnh này!",
                color=0xff0000
            )
            return await interaction.response.send_message(embed=embed_error, ephemeral=True)
        
        if so_tien <= 0:
            embed_error = discord.Embed(
                title="❌ LỖI",
                description="Số tiền phải lớn hơn 0!",
                color=0xff0000
            )
            return await interaction.response.send_message(embed=embed_error, ephemeral=True)
        
        user_id = user.id
        so_du_hien_tai = vi_tien.get(user_id, 0)
        
        so_du_moi = so_du_hien_tai + so_tien
        vi_tien[user_id] = so_du_moi
        luu_du_lieu()
        
        if user_id not in lich_su_nap:
            lich_su_nap[user_id] = []
        lich_su_nap[user_id].append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'amount': so_tien,
            'content': f"CỘNG TIỀN - {ly_do if ly_do else 'Không có lý do'}",
            'admin': interaction.user.id
        })
        
        cap_nhat_webhook(user_id, so_du_moi, f"DISCORD_ADMIN_{int(time.time())}", "success")

        embed_success = discord.Embed(
            title="✅ CỘNG TIỀN THÀNH CÔNG!",
            description=f"Đã cộng **{so_tien:,} VND** vào ví {user.mention}",
            color=0x00ff00
        )
        embed_success.add_field(name="📊 THÔNG TIN",
            value=f"**User:** {user.mention} (`{user_id}`)\n"
                  f"**Số tiền cộng:** {so_tien:,} VND\n"
                  f"**Số dư cũ:** {so_du_hien_tai:,} VND\n"
                  f"**Số dư mới:** {so_du_moi:,} VND\n"
                  f"**Lý do:** {ly_do if ly_do else 'Không có'}\n"
                  f"**Admin:** {interaction.user.mention}",
            inline=False
        )
        embed_success.set_footer(text=f"BotPawPank • {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
        await interaction.response.send_message(embed=embed_success)
        
        try:
            dm_embed = discord.Embed(
                title="**✅ NẠP THẺ THÀNH CÔNG!**",
                description=f"🎉 Bạn đã được cộng **{so_tien:,} VND** vào ví!\n*(Giao dịch thủ công bởi {interaction.user.mention})*",
                color=0x00ff00
            )
            dm_embed.add_field(name="📝 Mã Giao Dịch", value=f"`ADMIN_{user_id}_{int(time.time())}`", inline=False)
            if ly_do:
                dm_embed.add_field(name="📝 Lý do", value=ly_do, inline=False)
            dm_embed.set_footer(text=f"BotPawPank • {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
            await user.send(embed=dm_embed)
        except:
            pass
        
        await gui_bao_cao_admin(
            bot,
            title="📊 THÔNG BÁO CỘNG TIỀN",
            description=f"Admin {interaction.user.mention} đã cộng tiền cho {user.mention}",
            color=0x00ff00,
            fields=[
                ("👤 User được cộng", f"{user.mention} (`{user_id}`)"),
                ("💰 Số tiền cộng", f"{so_tien:,} VND"),
                ("📊 Số dư mới", f"{so_du_moi:,} VND"),
                ("📝 Lý do", ly_do if ly_do else "Không có"),
                ("👤 Admin thực hiện", interaction.user.mention)
            ]
        )
        
    except Exception as e:
        print(f"❌ Lỗi cong_tien: {e}")
        traceback.print_exc()
        embed_error = discord.Embed(
            title="❌ LỖI",
            description=f"Đã xảy ra lỗi: {str(e)}",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed_error, ephemeral=True)

# ============================================================
# PHẦN 16: BOT CHÍNH
# ============================================================
class Bot(discord.Client):
    def __init__(self):
        q = discord.Intents.default()
        q.guilds = True
        q.message_content = True
        q.members = True
        q.reactions = True
        super().__init__(intents=q)
        self.tree = app_commands.CommandTree(self)
        self.pending_messages = {}
        self.dang_check = {}
        self.temp_data = {}

    async def setup_hook(self):
        try:
            mc = discord.Object(id=ID_MAY_CHU)
            self.tree.add_command(lenh_tat_tim_map)
            self.tree.add_command(lenh_bat_tim_map)
            self.tree.add_command(startev)
            self.tree.add_command(stopev)
            self.tree.add_command(bdev)
            self.tree.add_command(csds)
            self.tree.add_command(offjoin)
            self.tree.add_command(onjoin)
            self.tree.add_command(cancelev)
            self.tree.add_command(lsnew)
            self.tree.add_command(sodu)
            self.tree.add_command(tru_tien)
            self.tree.add_command(cong_tien)
            self.tree.add_command(NapTienGroup(name="naptien", description="💰 Nạp tiền vào PawPank"))
            await self.tree.sync(guild=mc)
            await self.tree.sync()
            self.add_view(GiaoDienKiemTraGia())
            self.add_view(GiaoDienTaoDon())
            self.add_view(DieuKhienDon())
            self.add_view(NutEventChinh())
            self.add_view(SuaDSView())
            self.loop.create_task(self.check_giao_dich())
        except Exception as e:
            print(f"❌ Lỗi setup_hook: {e}")
            traceback.print_exc()

    async def on_ready(self):
        global cac_map_da_gui
        try:
            nap_emoji_tu_may_chu(self)
            await phuc_hoi_event_tu_tin_nhan(self)
            if event_active and msg_event:
                try:
                    await msg_event.edit(view=NutEventChinh())
                except Exception as e:
                    print(f"❌ Lỗi edit msg_event: {e}")
                    traceback.print_exc()
            
            cac_map_da_gui = []
            
            await self.bang_dieu_khien()
            if not self.vong_lap_quet.is_running():
                self.vong_lap_quet.start()
            
            # === THÊM AUTO SAVE RA NGOÀI TRY, NGAY TRƯỚC KHI IN "BOT SẴN SÀNG" ===
            @tasks.loop(seconds=10)
            async def auto_save_data():
                luu_du_lieu()
            auto_save_data.start()
            # =========================================================
            
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
                            await asyncio.sleep(1)
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
                            await asyncio.sleep(1)
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
                                await asyncio.sleep(1)
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

    async def check_giao_dich(self):
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                if not self.dang_check:
                    await asyncio.sleep(5)
                    continue
                
                for task_id, info in list(self.dang_check.items()):
                    data = await self.kiem_tra_trang_thai(task_id)
                    if not data:
                        continue
                    
                    code = data.get('Code')
                    
                    if code == 2:
                        user_id = info["user_id"]
                        nap_id = info["nap_id"]
                        loai_the = info.get("loai_the", "")
                        card_value = data.get('CardValue', 0)
                        rate = info.get("rate", 13)
                        tien_nhan = int(card_value - (card_value * rate / 100))
                        
                        if user_id not in vi_tien:
                            vi_tien[user_id] = 0
                        vi_tien[user_id] += tien_nhan
                        luu_du_lieu()
                        
                        cap_nhat_webhook(user_id, tien_nhan, nap_id, "success")
                        
                        await self.xoa_message_cu(user_id)
                        await self.send_dm_thanh_cong(user_id, tien_nhan, nap_id, loai_the)
                        
                        await gui_bao_cao_admin(
                            self,
                            title="**📊 THÔNG BÁO NẠP THẺ THÀNH CÔNG**",
                            description=f"User <@{user_id}> đã nạp thẻ thành công!",
                            color=0x00ff00,
                            fields=[
                                ("👤 User", f"ID: `{user_id}`"),
                                ("💳 Loại thẻ", loai_the),
                                ("💰 Số tiền nhận", f"{tien_nhan:,} VND"),
                                ("📝 Mã GD", f"`{nap_id}`")
                            ]
                        )
                        
                        del self.dang_check[task_id]
                        
                    elif code == 3:
                        user_id = info["user_id"]
                        nap_id = info["nap_id"]
                        
                        await self.xoa_message_cu(user_id)
                        await self.send_dm_that_bai(user_id, nap_id, data.get('Message', 'Thẻ không hợp lệ'))
                        
                        del self.dang_check[task_id]
                
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"❌ Lỗi check: {e}")
                await asyncio.sleep(5)

    async def kiem_tra_trang_thai(self, task_id):
        url = f"https://doithegiatot.com/api/card/{task_id}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"📊 [CHECK] Task {task_id}: {data}")
                        return data
        except Exception as e:
            print(f"❌ Lỗi check {task_id}: {e}")
        return None

    async def xoa_message_cu(self, user_id):
        if user_id in self.pending_messages:
            try:
                msg = self.pending_messages[user_id]
                await msg.delete()
                del self.pending_messages[user_id]
            except:
                pass

    async def send_dm_thanh_cong(self, user_id, amount, nap_id, loai_the):
        try:
            user = await self.fetch_user(user_id)
            embed = discord.Embed(
                title="**✅ NẠP THẺ THÀNH CÔNG!**",
                description=f"🎉 Bạn đã nạp thành công thẻ *{loai_the}*, nhận **{amount:,} VND**",
                color=0x00ff00
            )
            embed.add_field(name="📝 Mã Giao Dịch", value=f"`{nap_id}`", inline=False)
            embed.set_footer(text=f"BotPawPank • {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
            await user.send(embed=embed)
            print(f"✅ Đã gửi DM thành công cho user {user_id}")
        except Exception as e:
            print(f"❌ Lỗi gửi DM thành công: {e}")

    async def send_dm_that_bai(self, user_id, nap_id, ly_do):
        try:
            user = await self.fetch_user(user_id)
            embed = discord.Embed(
                title="**❌ NẠP THẺ THẤT BẠI!**",
                description=f"⚠️ {ly_do}",
                color=0xff0000
            )
            embed.add_field(name="📝 Mã GD", value=f"`{nap_id}`", inline=False)
            embed.set_footer(text=f"BotPawPank • {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
            await user.send(embed=embed)
            print(f"✅ Đã gửi DM thất bại cho user {user_id}")
        except Exception as e:
            print(f"❌ Lỗi gửi DM thất bại: {e}")

    @tasks.loop(seconds=120)
    async def vong_lap_quet(self):
        global dang_quet, cac_map_da_gui
        if not dang_quet:
            return

        try:
            k = self.get_channel(ID_KENH_QUET)
            if k is None:
                print("❌ Không tìm thấy channel:", ID_KENH_QUET)
                return

            map_moi = quet_divaz()
            if map_moi:
                cac_map_da_gui.append(map_moi)
                
                if len(cac_map_da_gui) > MAX_MAPS:
                    cac_map_da_gui = cac_map_da_gui[-MAX_MAPS:]
                
                sn = map_moi['so_nguoi_choi']
                ma = map_moi['id_may'][-5:]
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
                    value=f"🟢 {sn}/{map_moi['toi_da']}" if sn <= 3 else f"🟡 {sn}/{map_moi['toi_da']}",
                    inline=True
                )
                b.add_field(name="📶 PING", value=f"{map_moi['ping']}ms", inline=True)
                b.add_field(name="🎯 FPS", value=f"{map_moi['fps']}", inline=True)
                b.set_thumbnail(url=ANH_NHO)
                b.set_image(url=ANH_LON)
                b.set_footer(text=f"BotByPawPaw • {now.strftime('%H:%M:%S | %d/%m/%Y')}")
                
                await k.send(embed=b, view=GiaoDienServer(map_moi))
                
                if len(cac_map_da_gui) > MAX_MAPS:
                    so_can_xoa = len(cac_map_da_gui) - MAX_MAPS
                    async for msg in k.history(limit=100):
                        if msg.author == self.user and so_can_xoa > 0:
                            try:
                                await msg.delete()
                                await asyncio.sleep(2)
                                so_can_xoa -= 1
                            except discord.HTTPException as e:
                                if e.status == 429:
                                    print("⚠️ Rate limit, chờ 5 giây...")
                                    await asyncio.sleep(5)
                                pass
                        else:
                            break
                    
                    cac_map_da_gui = cac_map_da_gui[-MAX_MAPS:]
                        
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

    async def on_interaction(self, interaction):
        if interaction.type == discord.InteractionType.component:
            custom_id = interaction.data.get("custom_id")
            user_id = interaction.user.id
            
            if custom_id == "nhap_the":
                
                if user_id not in self.temp_data:
                    await interaction.response.send_message("⏳ Có vẻ bạn đã bấm Hủy trước đó hoặc phiên làm việc bị hết. Vui lòng dùng lại `/naptien card` từ đầu để hệ thống đảm bảo chính xác nhé!", ephemeral=True)
                    return
                await interaction.response.send_modal(NhapTheModal())
            elif custom_id == "huy_the":
                try:
                    await interaction.message.delete()
                except:
                    pass
                if user_id in self.temp_data:
                    del self.temp_data[user_id]
                if user_id in self.pending_messages:
                    try:
                        await self.pending_messages[user_id].delete()
                        del self.pending_messages[user_id]
                    except:
                        pass
            
            elif custom_id == "gui_the":
                data = self.temp_data.get(user_id)
                if not data:
                    await interaction.response.send_message("❌ Hết phiên! Vui lòng thử lại.", ephemeral=True)
                    return
                
                pin = data["pin"]
                seri = data["seri"]
                loai_the = data["loai_the"]
                loai_the_name = data["loai_the_name"]
                menhgia = data["menhgia"]
                rate = data["rate"]
                tien_nhan_du_kien = data["tien_nhan_du_kien"]
                requestid = f"THE{user_id}{menhgia}{int(time.time())}"[:25]
                
                # Xoá dữ liệu tạm
                del self.temp_data[user_id]
                if user_id in self.temp_data:
                    del self.temp_data[user_id]
                
                if user_id in self.pending_messages:
                    try:
                        await self.pending_messages[user_id].delete()
                        del self.pending_messages[user_id]
                    except:
                        pass
                
                ket_qua = gui_the_doithegiatot(pin, seri, loai_the, menhgia, requestid)
                
                if not ket_qua:
                    embed_error = discord.Embed(title="❌ GỬI THẺ THẤT BẠI", description="Không thể kết nối đến Doithegiatot!", color=0xff0000)
                    try:
                        await interaction.message.delete()
                    except:
                        pass
                    await interaction.followup.send(embed=embed_error)
                    return
                
                code = ket_qua.get('Code', 0)
                message = ket_qua.get('Message', 'Lỗi không xác định')
                task_id = ket_qua.get('TaskId')
                wrong_price = ket_qua.get('wrongPrice', False)
                
                if code == 1:
                    if user_id not in pending_transactions:
                        pending_transactions[user_id] = []
                    pending_transactions[user_id].append({
                        "nap_id": requestid,
                        "amount": menhgia,
                        "status": "pending",
                        "type": "card",
                        "card_type": loai_the_name,
                        "card_type_id": loai_the,
                        "time": datetime.now().strftime('%H:%M:%S %d/%m/%Y'),
                        "pin": pin,
                        "seri": seri,
                        "rate": rate,
                        "tien_nhan_du_kien": tien_nhan_du_kien,
                        "task_id": task_id
                    })
                    
                    self.dang_check[task_id] = {
                        "user_id": user_id,
                        "nap_id": requestid,
                        "amount": menhgia,
                        "rate": rate,
                        "loai_the": loai_the_name
                    }
                    print(f"📌 Đã thêm task {task_id} vào danh sách check")
                    
                    embed_success = discord.Embed(
                        title="**✅ ĐÃ GỬI THẺ**",
                        description=f"💳 Loại thẻ *{loai_the_name}*\nMệnh giá *{menhgia:,} VND*\nTiền nhận được: **{tien_nhan_du_kien:,} VND** *(Chiết khấu {rate}%)*",
                        color=0x00ff00
                    )
                    embed_success.add_field(name="📝 Mã Giao Dịch", value=f"`{requestid}`", inline=False)
                    embed_success.set_footer(text=f"BotPawPank • {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
                    
                    # Xoá tin nhắn cũ (embed xác nhận)
                    try:
                        await interaction.message.delete()
                    except:
                        pass
                    
                    # Gửi embed mới (không phải ephemeral)
                    msg = await interaction.followup.send(embed=embed_success)
                    self.pending_messages[user_id] = msg
                    
                else:
                    so_lan_sai = cap_nhat_lan_sai(user_id, pin, seri)
                    if so_lan_sai:
                        asyncio.run_coroutine_threadsafe(
                            gui_bao_cao_admin(
                                self,
                                title="🚫 CẢNH BÁO: USER BỊ CẤM NẠP THẺ",
                                description=f"User <@{user_id}> đã bị **CẤM** nạp thẻ!",
                                color=0xff0000,
                                fields=[
                                    ("👤 User", f"ID: `{user_id}`"),
                                    ("📊 Số lần sai", "2/2"),
                                    ("🔢 Mã thẻ sai", f"`{pin}`"),
                                    ("🔢 Seri sai", f"`{seri}`")
                                ]
                            ),
                            self.loop
                        )
                    
                    embed_error = discord.Embed(title="❌ GỬI THẺ THẤT BẠI", description=f"{message}", color=0xff0000)
                    if wrong_price:
                        embed_error.add_field(name="⚠️ LƯU Ý", value="Thẻ đúng nhưng **sai mệnh giá**! Vui lòng kiểm tra lại.", inline=False)
                    embed_error.add_field(name="📊 SỐ LẦN SAI", value=f"{danh_sach_cam.get(user_id, {}).get('so_lan_sai', 0)}/2", inline=False)
                    if so_lan_sai:
                        embed_error.add_field(name="🚫 CẢNH BÁO", value="Bạn đã bị **CẤM** nạp thẻ! Liên hệ Admin!", inline=False)
                    
                    try:
                        await interaction.message.delete()
                    except:
                        pass
                    await interaction.followup.send(embed=embed_error)
                    
# ============================================================
# PHẦN 17: CHẠY BOT
# ============================================================
bot = Bot()

if __name__ == '__main__':
    luong = threading.Thread(target=chay_may_chu_web)
    luong.start()
    print("🌐 Web port 8080")
    bot.run(MA_BOT)
