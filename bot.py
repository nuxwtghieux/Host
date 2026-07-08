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
try: time.tzset()
except: pass

def gio_vn(): return datetime.now(timezone(timedelta(hours=7)))

# ===== TẮT NHẬT KÝ =====
urllib3.disable_warnings()
warnings.filterwarnings("ignore")
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("discord").setLevel(logging.WARNING)

# ===== MÁY CHỦ WEB FLASK =====
ung_dung = Flask(__name__)
@ung_dung.route('/')
def trang_chu(): return "Bot đang chạy!"
def chay_may_chu_web(): ung_dung.run(host='0.0.0.0', port=8080)

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
ID_KENH_QUET = 1523707366280003594
ID_MAP = "88323040672117"
ID_KENH_PHAN_UNG = 1523970421819572345
ID_VAI_TRO_PHAN_UNG = 1523599853882703882
KENH_EVENT_ID = 1523605458068181083
KENH_KET_QUA_ID = 1523605663064915978

EMOJI_CANH1 = "✨"; EMOJI_CANH2 = "✨"; EMOJI_BLINK2 = "✨"; EMOJI_BLINKK = "🔹"
EMOJI_TRON = "🔹"; EMOJI_COIN = "💰"; BIEU_TUONG_PHAN_UNG = "✅"

ANH_GIF = "https://cdn.discordapp.com/attachments/1524068633255481387/1524080452049305713/da685c21e4f555bad69f52593c221dc7.gif"
ANH_CHAO_MUNG = "https://i.postimg.cc/sDh8Xcyp/a9e9538574064d128b604f643392d84b.gif"
ANH_TAM_BIET = "https://cdn.discordapp.com/attachments/1524068633255481387/1524068815518961825/c19d6274e1fd53c5ca46cdafccb4cbc9.gif"
ANH_NHO = "https://huyhieu08.online/uploads/20260707_054705_91412ed7.png"
ANH_LON = "https://i.postimg.cc/V6CFtBL0/no-Filter.webp"

dem_don = 0; dang_quet = True; id_tin_nhan_phan_ung = None; cac_map_da_gui = set()
event_active = False; cho_phep_tham_gia = True; nguoi_tham_gia = {}; msg_event = None; so_event = 1

def nap_emoji_tu_may_chu(bot):
    global EMOJI_CANH1, EMOJI_CANH2, EMOJI_BLINK2, EMOJI_BLINKK, EMOJI_TRON, EMOJI_COIN, BIEU_TUONG_PHAN_UNG
    may_chu = bot.get_guild(ID_MAY_CHU)
    if not may_chu: return
    for emoji in may_chu.emojis:
        if emoji.name == "canh1": EMOJI_CANH1 = str(emoji)
        elif emoji.name == "canh2": EMOJI_CANH2 = str(emoji)
        elif emoji.name == "blink2": EMOJI_BLINK2 = str(emoji)
        elif emoji.name == "blinkk": EMOJI_BLINKK = str(emoji)
        elif emoji.name == "tron": EMOJI_TRON = str(emoji)
        elif emoji.name == "xu": EMOJI_COIN = str(emoji)
        elif emoji.name == "baibien": BIEU_TUONG_PHAN_UNG = str(emoji)

def lam_tron_the(ngan_hang):
    the_tho = ngan_hang * 1.15 + 10000; phan_du = the_tho % 10000
    return ((the_tho // 10000) + 1) * 10000 if phan_du >= 5000 else (the_tho // 10000) * 10000

def lam_tron_ngan_hang(ngan_hang): return int(round(ngan_hang / 1000) * 1000)
def la_quan_tri(tv): return any(r.id == ID_QUAN_TRI for r in tv.roles)
def la_quan_tri_hoac_dieu_hanh(tv): return any(r.id in [ID_QUAN_TRI, ID_DIEU_HANH] for r in tv.roles)
def la_vip(tv): return any(r.id == ID_VIP for r in tv.roles)
def tinh_giam_gia(st, tv): return int(st * 0.97) if la_vip(tv) else st
def dinh_dang_gia(gg, giam, vip): return f"**{giam:,}** VND ~~{gg:,} VND~~ (VIP)" if vip and giam != gg else f"**{gg:,}** VND"

async def gui_nhat_ky_don(bot, so_don, id_nt, nguoi_dong, ldv, ly_do="Không"):
    now = gio_vn(); nguoi_nhan = bot.get_user(ID_NGUOI_NHAN_LOG) or await bot.fetch_user(ID_NGUOI_NHAN_LOG)
    bang = discord.Embed(title=f"# Đơn số {so_don}", color=0x3498db)
    bang.add_field(name="🧑‍🦱 Người mở:", value=f"<@{id_nt}>" if id_nt else "?", inline=False)
    bang.add_field(name="🧑‍🦱 Người đóng:", value=nguoi_dong, inline=False)
    bang.add_field(name="🔖 Dịch vụ:", value=ldv, inline=False)
    bang.add_field(name="⏰ Thời gian:", value=now.strftime('%H:%M:%S | %d-%m-%Y'), inline=False)
    bang.add_field(name="📝 Lí do:", value=ly_do, inline=False)
    try: await nguoi_nhan.send(embed=bang)
    except: pass

# ===== MODALS =====
class BangKiemTraTien(discord.ui.Modal, title="Kiểm tra giá tiền"):
    sl = discord.ui.TextInput(label="Nhập số tiền", placeholder="100000", required=True, max_length=20)
    async def on_submit(self, tt):
        try: tien = int(self.sl.value.replace(",","").replace(".",""))
        except: return await tt.response.send_message("❌ Số không hợp lệ!", ephemeral=True)
        nhg = lam_tron_ngan_hang(int(tien*0.12)); tg = lam_tron_the(nhg)
        nhgiam = tinh_giam_gia(nhg, tt.user); tgiam = tinh_giam_gia(tg, tt.user); vip = la_vip(tt.user); now = gio_vn()
        bang = discord.Embed(title=f"{EMOJI_COIN} GIÁ CÀY TIỀN {EMOJI_COIN}", color=0x3498db)
        mt = f"\n━━━━━━━━━━━━━━\n{EMOJI_COIN}ㆍ**Số tiền:** **{tien:,}**\n━━━━━━━━━━━━━━\n{EMOJI_COIN}ㆍ**Bank:** {dinh_dang_gia(nhg, nhgiam, vip)}\n━━━━━━━━━━━━━━\n{EMOJI_COIN}ㆍ**Card:** {dinh_dang_gia(tg, tgiam, vip)}\n━━━━━━━━━━━━━━\n"
        if vip: mt += f"\n👑 {tt.user.mention} được giảm **3%**!\n"
        mt += "\n‼️ **ÁP MÃ GIẢM GIÁ** ‼️"
        bang.description = mt; bang.set_image(url=ANH_GIF)
        bang.set_footer(text=f"{now.strftime('%H:%M:%S | %d-%m-%Y')} | {tt.user.display_name}")
        await tt.response.send_message(embed=bang, ephemeral=True)

class BangKiemTraSlay(discord.ui.Modal, title="Kiểm tra giá slay"):
    sl = discord.ui.TextInput(label="Nhập số slay", placeholder="2000", required=True, max_length=20)
    async def on_submit(self, tt):
        try: slay = int(self.sl.value.replace(",","").replace(".",""))
        except: return await tt.response.send_message("❌ Số không hợp lệ!", ephemeral=True)
        nhg = lam_tron_ngan_hang(int(slay*25)); vip = la_vip(tt.user)
        if nhg > 8000: ct = dinh_dang_gia(lam_tron_the(nhg), tinh_giam_gia(lam_tron_the(nhg), tt.user), vip)
        else: ct = "Chỉ nhận card từ 400 SLAY!"
        nhgiam = tinh_giam_gia(nhg, tt.user); now = gio_vn()
        bang = discord.Embed(title=f"{EMOJI_COIN} GIÁ CÀY SLAY {EMOJI_COIN}", color=0x3498db)
        mt = f"\n━━━━━━━━━━━━━━\n{EMOJI_COIN}ㆍ**Số slay:** **{slay:,}**\n━━━━━━━━━━━━━━\n{EMOJI_COIN}ㆍ**Bank:** {dinh_dang_gia(nhg, nhgiam, vip)}\n━━━━━━━━━━━━━━\n{EMOJI_COIN}ㆍ**Card:** {ct}\n━━━━━━━━━━━━━━\n"
        if vip: mt += f"\n👑 {tt.user.mention} được giảm **3%**!\n"
        mt += "\n‼️ **ÁP MÃ GIẢM GIÁ** ‼️"
        bang.description = mt; bang.set_image(url=ANH_GIF)
        bang.set_footer(text=f"{now.strftime('%H:%M:%S | %d-%m-%Y')} | {tt.user.display_name}")
        await tt.response.send_message(embed=bang, ephemeral=True)

class BangVndSangTien(discord.ui.Modal, title="VND → Tiền cần cày"):
    sl = discord.ui.TextInput(label="Nhập số VND", placeholder="50000", required=True, max_length=20)
    async def on_submit(self, tt):
        try: vnd = int(self.sl.value.replace(",","").replace(".",""))
        except: return await tt.response.send_message("❌ Số không hợp lệ!", ephemeral=True)
        vsg = tinh_giam_gia(vnd, tt.user); tien = int(vsg/0.12); nhg = lam_tron_ngan_hang(vnd)
        nhgiam = tinh_giam_gia(nhg, tt.user); tg = lam_tron_the(nhg); tgiam = tinh_giam_gia(tg, tt.user); vip = la_vip(tt.user); now = gio_vn()
        bang = discord.Embed(title=f"{EMOJI_COIN} SỐ TIỀN NHẬN ĐƯỢC {EMOJI_COIN}", color=0xe67e22)
        mt = f"\n━━━━━━━━━━━━━━\n{EMOJI_COIN}ㆍ**VND trả:** **{vnd:,}**\n━━━━━━━━━━━━━━\n{EMOJI_COIN}ㆍ**Tiền nhận:** **{tien:,}**\n━━━━━━━━━━━━━━\n{EMOJI_COIN}ㆍ**Card:** {dinh_dang_gia(tg, tgiam, vip)}\n━━━━━━━━━━━━━━\n"
        if vip: mt += f"\n👑 {tt.user.mention} được giảm **3%**!\n"
        mt += "\n‼️ **ÁP MÃ GIẢM GIÁ** ‼️"
        bang.description = mt; bang.set_image(url=ANH_GIF)
        bang.set_footer(text=f"{now.strftime('%H:%M:%S | %d-%m-%Y')} | {tt.user.display_name}")
        await tt.response.send_message(embed=bang, ephemeral=True)

class BangVndSangSlay(discord.ui.Modal, title="VND → Slay"):
    sl = discord.ui.TextInput(label="Nhập số VND", placeholder="50000", required=True, max_length=20)
    async def on_submit(self, tt):
        try: vnd = int(self.sl.value.replace(",","").replace(".",""))
        except: return await tt.response.send_message("❌ Số không hợp lệ!", ephemeral=True)
        vsg = tinh_giam_gia(vnd, tt.user); slay = int(vsg/25); nhg = lam_tron_ngan_hang(vnd)
        nhgiam = tinh_giam_gia(nhg, tt.user); vip = la_vip(tt.user)
        if nhg > 8000: ct = dinh_dang_gia(lam_tron_the(nhg), tinh_giam_gia(lam_tron_the(nhg), tt.user), vip)
        else: ct = "Chỉ nhận card từ 400 SLAY!"; now = gio_vn()
        bang = discord.Embed(title="💅 SỐ SLAY NHẬN ĐƯỢC 💅", color=0x9b59b6)
        mt = f"\n━━━━━━━━━━━━━━\n💳ㆍ**VND trả:** **{vnd:,}**\n━━━━━━━━━━━━━━\n💅ㆍ**Slay nhận:** **{slay:,}**\n━━━━━━━━━━━━━━\n🔖ㆍ**Card:** {ct}\n━━━━━━━━━━━━━━\n"
        if vip: mt += f"\n👑 {tt.user.mention} được giảm **3%**!\n"
        mt += "\n‼️ **ÁP MÃ GIẢM GIÁ** ‼️"
        bang.description = mt; bang.set_image(url=ANH_GIF)
        bang.set_footer(text=f"{now.strftime('%H:%M:%S | %d-%m-%Y')} | {tt.user.display_name}")
        await tt.response.send_message(embed=bang, ephemeral=True)

class BangTaoDon(discord.ui.Modal, title="Tạo đơn"):
    dv = discord.ui.TextInput(label="Tiền/Slay:", placeholder="Tiền hoặc Slay", required=True, max_length=10)
    async def on_submit(self, tt):
        global dem_don
        ldv = self.dv.value; mc = tt.guild; nd = tt.user
        for k in mc.channels:
            if k.name.startswith("đơn-") and k.topic and str(nd.id) == k.topic: return await tt.response.send_message("❌ Đã có đơn!", ephemeral=True)
        dm = mc.get_channel(ID_DANH_MUC_DON); dem_don += 1
        if dem_don > 999: dem_don = 1
        sd = f"{dem_don:03d}"; now = gio_vn(); ten = nd.display_name.replace(" ","-")[:20]
        tn = f"đơn-{sd}-{ten}-{now.strftime('%H-%M')}"
        pq = {mc.default_role: discord.PermissionOverwrite(view_channel=False), nd: discord.PermissionOverwrite(view_channel=True, send_messages=True), mc.me: discord.PermissionOverwrite(view_channel=True)}
        k = await mc.create_text_channel(name=tn, category=dm, overwrites=pq, topic=f"{nd.id}|{ldv}")
        await k.send(content=f"{nd.mention} <@&{ID_QUAN_TRI}>", embed=discord.Embed(title="🎫 CÓ ĐƠN", description=f"Đơn: **{sd}**\nDịch vụ: **{ldv}**\nNgười tạo: {nd.mention}", color=0x3498db), view=DieuKhienDon())
        await tt.response.send_message(f"✅ {k.mention}", ephemeral=True)

class BangLyDoDong(discord.ui.Modal, title="Lý do đóng đơn"):
    ld = discord.ui.TextInput(label="Lý do", required=True)
    async def on_submit(self, tt):
        tn = tt.channel.name; p = tn.split("-"); sd = p[1] if len(p)>1 else "???"
        dl = tt.channel.topic
        if dl and "|" in dl: id_nt, ldv = dl.split("|",1)
        else: id_nt = dl; ldv = "?"
        await gui_nhat_ky_don(tt.client, sd, id_nt, tt.user.mention, ldv, self.ld.value)
        await tt.channel.delete()

class FormThamGia(discord.ui.Modal, title="Đăng ký tham gia"):
    username = discord.ui.TextInput(label="Username Roblox", placeholder="Nhập username", required=True, max_length=50)
    async def on_submit(self, tt):
        global nguoi_tham_gia
        if not event_active: return await tt.response.send_message("❌ Event chưa bắt đầu!", ephemeral=True)
        if not cho_phep_tham_gia: return await tt.response.send_message("❌ Đã dừng!", ephemeral=True)
        if tt.user.id in nguoi_tham_gia: return await tt.response.send_message("❌ Đã tham gia!", ephemeral=True)
        nguoi_tham_gia[tt.user.id] = self.username.value
        await cap_nhat_event()
        await tt.response.send_message(f"✅ **{self.username.value}**", ephemeral=True)

async def cap_nhat_event():
    global msg_event
    if not msg_event: return
    ds = "\n".join([f"**{i}.** **{u}** (<@{uid}>)" for i,(uid,u) in enumerate(nguoi_tham_gia.items(),1)]) if nguoi_tham_gia else "Chưa có ai!"
    tt = "✅ ĐANG MỞ" if cho_phep_tham_gia else "⏸️ ĐÃ DỪNG"
    embed = discord.Embed(title="⚔️ EVENT DIVAZ ĐẤU 1VS1 ⚔️", description=f"ㆍ**{len(nguoi_tham_gia)}** người tham gia.\nㆍTrạng thái: **{tt}**\n\nㆍNhấn '💅Tham gia' bên dưới.", color=0xff0000)
    embed.add_field(name="📋 DANH SÁCH:", value=ds, inline=False)
    embed.set_footer(text="BotByPawPaw")
    await msg_event.edit(embed=embed)

class NutXacNhanBatDau(discord.ui.View):
    def __init__(self): super().__init__(timeout=30)
    @discord.ui.button(label="✅ Xác nhận", style=discord.ButtonStyle.green)
    async def xn(self, tt, n):
        if not la_quan_tri(tt): return await tt.response.send_message("❌ Admin only!", ephemeral=True)
        await bat_dau_event(tt)
        try: await tt.message.delete()
        except: pass
    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.red)
    async def huy(self, tt, n):
        try: await tt.message.delete()
        except: pass

class NutXacNhanDung(discord.ui.View):
    def __init__(self): super().__init__(timeout=30)
    @discord.ui.button(label="✅ Xác nhận", style=discord.ButtonStyle.red)
    async def xn(self, tt, n):
        global cho_phep_tham_gia; cho_phep_tham_gia = False; await cap_nhat_event()
        try: await tt.message.delete()
        except: pass
    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.grey)
    async def huy(self, tt, n):
        try: await tt.message.delete()
        except: pass

class NutEventChinh(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="💅 Tham gia", style=discord.ButtonStyle.green, custom_id="tham_gia_ev")
    async def tg(self, tt, n):
        if not event_active: return await tt.response.send_message("❌ Chưa bắt đầu!", ephemeral=True)
        if not cho_phep_tham_gia: return await tt.response.send_message("❌ Đã dừng!", ephemeral=True)
        await tt.response.send_modal(FormThamGia())
    @discord.ui.button(label="💅 Bắt đầu", style=discord.ButtonStyle.green, custom_id="bat_dau_ev")
    async def bd(self, tt, n):
        if not la_quan_tri(tt): return await tt.response.send_message("❌ Admin only!", ephemeral=True)
        if len(nguoi_tham_gia) < 2: return await tt.response.send_message("❌ Cần 2+ người!", ephemeral=True)
        await tt.response.send_message(f"⚠️ Bắt đầu với {len(nguoi_tham_gia)} người?", view=NutXacNhanBatDau(), ephemeral=True)
    @discord.ui.button(label="🚪 Rời", style=discord.ButtonStyle.red, custom_id="roi_ev")
    async def roi(self, tt, n):
        if not event_active: return await tt.response.send_message("❌ Chưa bắt đầu!", ephemeral=True)
        if tt.user.id not in nguoi_tham_gia: return await tt.response.send_message("❌ Chưa tham gia!", ephemeral=True)
        del nguoi_tham_gia[tt.user.id]; await cap_nhat_event()
        await tt.response.send_message("✅ Đã rời!", ephemeral=True)
    @discord.ui.button(label="⏸️ Dừng tham gia", style=discord.ButtonStyle.red, custom_id="dung_tg_ev")
    async def dtg(self, tt, n):
        if not la_quan_tri(tt): return await tt.response.send_message("❌ Admin only!", ephemeral=True)
        await tt.response.send_message("⚠️ Dừng tham gia?", view=NutXacNhanDung(), ephemeral=True)

class NutChonThang(discord.ui.View):
    def __init__(self, u1, u2, sv, ts):
        super().__init__(timeout=600); self.u1=u1; self.u2=u2; self.sv=sv; self.ts=ts; self.dc=False
        t1 = "ADMIN/MOD" if u1=="admin" else nguoi_tham_gia.get(u1,"?")
        t2 = "ADMIN/MOD" if u2=="admin" else nguoi_tham_gia.get(u2,"?")
        n1=discord.ui.Button(label=f"🏆 {t1}", style=discord.ButtonStyle.green); n1.callback=self.c1; self.add_item(n1)
        n2=discord.ui.Button(label=f"🏆 {t2}", style=discord.ButtonStyle.blurple); n2.callback=self.c2; self.add_item(n2)
    async def c1(self, tt):
        if not la_quan_tri(tt): return await tt.response.send_message("❌ Admin only!", ephemeral=True)
        if self.dc: return await tt.response.send_message("❌ Đã chọn!", ephemeral=True)
        await self.xl(tt, self.u1)
    async def c2(self, tt):
        if not la_quan_tri(tt): return await tt.response.send_message("❌ Admin only!", ephemeral=True)
        if self.dc: return await tt.response.send_message("❌ Đã chọn!", ephemeral=True)
        await self.xl(tt, self.u2)
    async def xl(self, tt, ut):
        self.dc=True
        for c in self.children: c.disabled=True
        await tt.message.edit(view=self)
        await gui_ket_qua(ut)
        await tt.response.send_message(f"✅ Trận {self.ts}!", ephemeral=True)

async def gui_ket_qua(ut):
    kq = bot.get_channel(KENH_KET_QUA_ID)
    if not kq: return
    tr = "ADMIN/MOD" if ut=="admin" else nguoi_tham_gia.get(ut,"?")
    now = gio_vn()
    embed = discord.Embed(title="🎉 CONGRATULATIONS", description=f"<@{ut}> **WIN IN EVENT {so_event}**", color=0xffd700)
    embed.add_field(name="🎮 UserGame:", value=f"```{tr}```", inline=False)
    embed.add_field(name="⏰ Time:", value=now.strftime('%H:%M:%S | %d/%m/%Y'), inline=False)
    embed.set_footer(text="BotByPawPaw")
    await kq.send(embed=embed)

async def bat_dau_event(tt):
    global cho_phep_tham_gia; cho_phep_tham_gia = False
    await msg_event.edit(view=discord.ui.View()); await cap_nhat_event()
    await gui_vong(tt.channel, 1, list(nguoi_tham_gia.keys()))

async def gui_vong(k, sv, ds):
    random.shuffle(ds); dc = ds.copy()
    if len(dc)%2!=0: dc.append("admin")
    ct = [(dc[i],dc[i+1]) for i in range(0,len(dc),2)]; tst = len(ct)
    await k.send(f"# 🔥 VÒNG {sv} 🔥\n📊 {len(ds)} người → {tst} trận")
    for i,(u1,u2) in enumerate(ct,1):
        t1 = "ADMIN/MOD" if u1=="admin" else nguoi_tham_gia.get(u1,"?")
        t2 = "ADMIN/MOD" if u2=="admin" else nguoi_tham_gia.get(u2,"?")
        embed = discord.Embed(title=f"🥊 TRẬN {i}:", description=f"```{t1}``` **VS** ```{t2}```", color=0xffaa00)
        embed.set_footer(text=f"Vòng {sv} • Trận {i}/{tst}")
        await k.send(embed=embed, view=NutChonThang(u1,u2,sv,i))

# ===== VIEWS KHÁC =====
class XacNhanDongDon(discord.ui.View):
    def __init__(self, k, sd, id_nt, ldv):
        super().__init__(timeout=30); self.k=k; self.sd=sd; self.id_nt=id_nt; self.ldv=ldv
    @discord.ui.button(label="✅ Xác nhận đóng", style=discord.ButtonStyle.red)
    async def xn(self, tt, n):
        if not la_quan_tri_hoac_dieu_hanh(tt.user): return await tt.response.send_message("❌ Không có quyền!", ephemeral=True)
        await tt.response.send_message("🔒 Đang đóng...", ephemeral=True)
        await gui_nhat_ky_don(tt.client, self.sd, self.id_nt, tt.user.mention, self.ldv)
        await self.k.delete()
    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.grey)
    async def huy(self, tt, n):
        if not la_quan_tri_hoac_dieu_hanh(tt.user): return await tt.response.send_message("❌ Không có quyền!", ephemeral=True)
        await tt.message.delete(); await tt.response.send_message("❌ Đã hủy!", ephemeral=True)

class BinhChonHoanThanh(discord.ui.View):
    def __init__(self, k, sd, id_nt, ldv):
        super().__init__(timeout=120); self.k=k; self.sd=sd; self.id_nt=id_nt; self.ldv=ldv
        self.nb=set(); self.dca=False; self.dcnt=False
    @discord.ui.button(label="✅ Hoàn thành", style=discord.ButtonStyle.green)
    async def ht(self, tt, n):
        nd=tt.user; la=la_quan_tri_hoac_dieu_hanh(nd); lnt=str(nd.id)==str(self.id_nt)
        if not la and not lnt: return await tt.response.send_message("❌ Không có quyền!", ephemeral=True)
        if nd.id in self.nb: return await tt.response.send_message("❌ Đã bấm!", ephemeral=True)
        self.nb.add(nd.id)
        if la: self.dca=True
        if lnt: self.dcnt=True
        if self.dca and self.dcnt:
            await tt.response.send_message("✅ Hoàn thành!", ephemeral=True)
            await gui_nhat_ky_don(tt.client, self.sd, self.id_nt, tt.user.mention, self.ldv, "Đơn đã hoàn thành")
            await self.k.delete()
        else:
            ct=[]; 
            if not self.dca: ct.append("Admin/Mod")
            if not self.dcnt: ct.append("Người tạo")
            await tt.response.send_message(f"✅ Cần thêm {' và '.join(ct)}!", ephemeral=True)
    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.grey)
    async def huy(self, tt, n):
        if not la_quan_tri_hoac_dieu_hanh(tt.user) and str(tt.user.id)!=str(self.id_nt): return await tt.response.send_message("❌ Không có quyền!", ephemeral=True)
        await tt.message.delete(); await tt.response.send_message("❌ Đã hủy!", ephemeral=True)

class DieuKhienDon(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🔒 Đóng đơn", style=discord.ButtonStyle.red, custom_id="dong_don")
    async def dong(self, tt, n):
        if not la_quan_tri_hoac_dieu_hanh(tt.user): return await tt.response.send_message("❌ Không có quyền!", ephemeral=True)
        tn=tt.channel.name; p=tn.split("-"); sd=p[1] if len(p)>1 else "???"
        dl=tt.channel.topic
        if dl and "|" in dl: id_nt,ldv=dl.split("|",1)
        else: id_nt=dl; ldv="?"
        await tt.response.send_message(embed=discord.Embed(title="⚠️ XÁC NHẬN", description=f"Đóng đơn **#{sd}**?", color=0xff0000), view=XacNhanDongDon(tt.channel,sd,id_nt,ldv))
    @discord.ui.button(label="✅ Hoàn thành đơn", style=discord.ButtonStyle.green, custom_id="hoan_thanh_don")
    async def ht(self, tt, n):
        nd=tt.user; tn=tt.channel.name; p=tn.split("-"); sd=p[1] if len(p)>1 else "???"
        dl=tt.channel.topic
        if dl and "|" in dl: id_nt,ldv=dl.split("|",1)
        else: id_nt=dl; ldv="?"
        if not la_quan_tri_hoac_dieu_hanh(nd) and str(nd.id)!=str(id_nt): return await tt.response.send_message("❌ Không có quyền!", ephemeral=True)
        await tt.response.send_message(embed=discord.Embed(title="✅ HOÀN THÀNH", description=f"Cần Admin/Mod VÀ Người tạo xác nhận!", color=0x00ff00), view=BinhChonHoanThanh(tt.channel,sd,id_nt,ldv))
    @discord.ui.button(label="🧾 Đóng kèm lý do", style=discord.ButtonStyle.grey, custom_id="dong_ly_do")
    async def dld(self, tt, n):
        if not la_quan_tri_hoac_dieu_hanh(tt.user): return await tt.response.send_message("❌ Không có quyền!", ephemeral=True)
        await tt.response.send_modal(BangLyDoDong())

class GiaoDienKiemTraGia(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="💰 Tiền→VND", style=discord.ButtonStyle.green, custom_id="kt_tien")
    async def kt(self, tt, n): await tt.response.send_modal(BangKiemTraTien())
    @discord.ui.button(label="💅 Slay→VND", style=discord.ButtonStyle.green, custom_id="kt_slay")
    async def ks(self, tt, n): await tt.response.send_modal(BangKiemTraSlay())
    @discord.ui.button(label="💵 VND→Tiền", style=discord.ButtonStyle.blurple, custom_id="vnd_tien")
    async def vt(self, tt, n): await tt.response.send_modal(BangVndSangTien())
    @discord.ui.button(label="💳 VND→Slay", style=discord.ButtonStyle.blurple, custom_id="vnd_slay")
    async def vs(self, tt, n): await tt.response.send_modal(BangVndSangSlay())

class GiaoDienTaoDon(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🎫 Tạo đơn", style=discord.ButtonStyle.blurple, custom_id="tao_don")
    async def td(self, tt, n): await tt.response.send_modal(BangTaoDon())

class GiaoDienServer(discord.ui.View):
    def __init__(self, mc):
        super().__init__(timeout=None)
        ms = discord.ButtonStyle.green if mc['so_nguoi_choi']<=3 else discord.ButtonStyle.blurple
        self.add_item(discord.ui.Button(style=ms, label="THAM GIA", url=f"https://nuxwtghieux.github.io/Snipe/?jobid={mc['id_may']}"))

def quet_divaz():
    kq=[]; ct=""; td={'User-Agent':'Mozilla/5.0'}
    while True:
        dd=f"https://games.roblox.com/v1/games/{ID_MAP}/servers/Public?limit=100"
        if ct: dd+=f"&cursor={ct}"
        try:
            ph=requests.get(dd,headers=td,timeout=15,verify=False)
            if ph.status_code==200:
                dl=ph.json(); cm=dl.get('data',[])
                if not cm: break
                for m in cm:
                    sn=m.get('playing',0)
                    if sn<5 and m['id'] not in cac_map_da_gui:
                        kq.append({'id_may':m['id'],'so_nguoi_choi':sn,'ping':m.get('ping','?'),'fps':m.get('fps','?'),'toi_da':m.get('maxPlayers','?')})
                ct=dl.get('nextPageCursor')
                if not ct: break
                time.sleep(1)
            else: break
        except: time.sleep(3)
    return kq

# ===== SLASH COMMANDS =====
@discord.app_commands.command(name="tat_tim_map", description="⏸️ Tạm dừng quét server Divaz")
async def lenh_tat_tim_map(tt):
    global dang_quet
    if not la_quan_tri(tt): return await tt.response.send_message("❌ Admin only!", ephemeral=True)
    dang_quet=False; await tt.response.send_message("⏸️ Đã tắt!", ephemeral=True)

@discord.app_commands.command(name="bat_tim_map", description="▶️ Bật lại quét server Divaz")
async def lenh_bat_tim_map(tt):
    global dang_quet
    if not la_quan_tri(tt): return await tt.response.send_message("❌ Admin only!", ephemeral=True)
    dang_quet=True; await tt.response.send_message("▶️ Đã bật!", ephemeral=True)

@discord.app_commands.command(name="startev", description="🎮 Bắt đầu event đấu 1vs1")
async def startev(tt):
    if not la_quan_tri(tt): return await tt.response.send_message("❌ Admin only!", ephemeral=True)
    global event_active, nguoi_tham_gia, msg_event, cho_phep_tham_gia, so_event
    so_event+=1; event_active=True; cho_phep_tham_gia=True; nguoi_tham_gia={}
    k=bot.get_channel(KENH_EVENT_ID)
    if not k: return await tt.response.send_message("❌ Không tìm thấy kênh!", ephemeral=True)
    embed=discord.Embed(title="⚔️ EVENT DIVAZ ĐẤU 1VS1 ⚔️", description="ㆍ**0** người tham gia.\nㆍTrạng thái: **✅ ĐANG MỞ**\n\nㆍNhấn '💅Tham gia' bên dưới.", color=0xff0000)
    embed.add_field(name="📋 DANH SÁCH:", value="Chưa có ai!", inline=False)
    embed.set_footer(text="BotByPawPaw")
    msg_event=await k.send(embed=embed, view=NutEventChinh())
    await tt.response.send_message("✅ Event đã bắt đầu!", ephemeral=True)

@discord.app_commands.command(name="stopev", description="⏸️ Dừng event")
async def stopev(tt):
    if not la_quan_tri(tt): return await tt.response.send_message("❌ Admin only!", ephemeral=True)
    global event_active; event_active=False
    await tt.response.send_message("✅ Event đã dừng!", ephemeral=True)

# ===== BOT CHÍNH =====
class Bot(discord.Client):
    def __init__(self):
        q=discord.Intents.default(); q.guilds=True; q.message_content=True; q.members=True; q.reactions=True
        super().__init__(intents=q)
        self.cay=app_commands.CommandTree(self)
    
    async def setup_hook(self):
        mc=discord.Object(id=ID_MAY_CHU)
        self.cay.add_command(lenh_tat_tim_map); self.cay.add_command(lenh_bat_tim_map)
        self.cay.add_command(startev); self.cay.add_command(stopev)
        await self.cay.sync(guild=mc)
        await self.cay.sync()  # SYNC GLOBAL
        self.add_view(GiaoDienKiemTraGia()); self.add_view(GiaoDienTaoDon()); self.add_view(DieuKhienDon())
        self.add_view(NutEventChinh())
    
    async def on_ready(self):
        nap_emoji_tu_may_chu(self)
        await self.bang_dieu_khien()
        self.vong_lap_quet.start()
        print(f"🚀 Bot sẵn sàng!")
    
    async def bang_dieu_khien(self):
        kkt=self.get_channel(ID_KENH_KIEM_TRA)
        if kkt:
            async for t in kkt.history(limit=50):
                if t.author==self.user: await t.delete()
            b=discord.Embed(title="‼️ HƯỚNG DẪN CHECK GIÁ 📍", description="Nhấn nút bên dưới để kiểm tra giá!", color=0x3498db)
            b.set_footer(text=gio_vn().strftime('%H:%M:%S | %d-%m-%Y'))
            await kkt.send(embed=b, view=GiaoDienKiemTraGia())
        
        kd=self.get_channel(ID_KENH_DON)
        if kd:
            async for t in kd.history(limit=50):
                if t.author==self.user: await t.delete()
            await kd.send(embed=discord.Embed(title="🛒 DỊCH VỤ", description="Tạo đơn bên dưới!", color=0x3498db), view=GiaoDienTaoDon())
        
        global id_tin_nhan_phan_ung
        kpu=self.get_channel(ID_KENH_PHAN_UNG)
        if kpu:
            tnc=None
            async for t in kpu.history(limit=50):
                if t.author==self.user and t.embeds: tnc=t; break
            if tnc:
                id_tin_nhan_phan_ung=tnc.id
                try: await tnc.add_reaction(BIEU_TUONG_PHAN_UNG)
                except: pass
            else:
                async for t in kpu.history(limit=50):
                    if t.author==self.user: await t.delete()
                b=discord.Embed(title="🎭 NHẬN VAI TRÒ", description="✅ **TICK VÀO BÊN DƯỚI ĐỂ XEM KÊNH CHAT ↓**", color=0x9b59b6)
                b.set_footer(text="BotByPawPaw")
                tn=await kpu.send(embed=b); await tn.add_reaction(BIEU_TUONG_PHAN_UNG)
                id_tin_nhan_phan_ung=tn.id
    
    @tasks.loop(seconds=180)
    async def vong_lap_quet(self):
        global dang_quet, cac_map_da_gui
        if not dang_quet: return
        k=self.get_channel(ID_KENH_QUET)
        if not k: return
        cm=quet_divaz()
        if cm:
            if len(cac_map_da_gui)>50: cac_map_da_gui.clear()
            tn=cm[0]; sn=tn['so_nguoi_choi']; ma=tn['id_may'][-5:]
            ms=0x00ff00 if sn<=3 else 0xffaa00; now=gio_vn()
            cac_map_da_gui.add(tn['id_may'])
            b=discord.Embed(title="🎮 DIVAZ - MÁY CHỦ TRỐNG", description=f"**Mã:** `#{ma}`", color=ms, timestamp=now)
            b.add_field(name="👥 NGƯỜI CHƠI", value=f"🟢 {sn}/{tn['toi_da']}" if sn<=3 else f"🟡 {sn}/{tn['toi_da']}", inline=True)
            b.add_field(name="📶 PING", value=f"{tn['ping']}ms", inline=True)
            b.add_field(name="🎯 FPS", value=f"{tn['fps']}", inline=True)
            b.set_thumbnail(url=ANH_NHO); b.set_image(url=ANH_LON)
            b.set_footer(text=f"BotByPawPaw • {now.strftime('%H:%M:%S | %d/%m/%Y')}")
            await k.send(embed=b, view=GiaoDienServer(tn))
    
    async def on_raw_reaction_add(self, dl):
        if dl.message_id!=id_tin_nhan_phan_ung: return
        if str(dl.emoji)!=BIEU_TUONG_PHAN_UNG: return
        mc=self.get_guild(dl.guild_id)
        if not mc: return
        tv=mc.get_member(dl.user_id)
        if not tv or tv.bot: return
        vt=mc.get_role(ID_VAI_TRO_PHAN_UNG)
        if not vt: return
        try: await tv.add_roles(vt)
        except: pass
    
    async def on_raw_reaction_remove(self, dl):
        if dl.message_id!=id_tin_nhan_phan_ung: return
        if str(dl.emoji)!=BIEU_TUONG_PHAN_UNG: return
        mc=self.get_guild(dl.guild_id)
        if not mc: return
        tv=mc.get_member(dl.user_id)
        if not tv or tv.bot: return
        vt=mc.get_role(ID_VAI_TRO_PHAN_UNG)
        if not vt: return
        try: await tv.remove_roles(vt)
        except: pass
    
    async def on_member_join(self, tv):
        k=self.get_channel(ID_KENH_CHAO_MUNG)
        if not k: return
        now=gio_vn(); mc=tv.guild
        b=discord.Embed(color=0x2ecc71)
        b.description=f"# {EMOJI_CANH1} CHÀO MỪNG {EMOJI_CANH2}\n━━━━━━━━━━━━━━\n# {EMOJI_TRON} THÔNG TIN:\n{EMOJI_BLINKK} Tên: {tv.mention}\n{EMOJI_BLINKK} ID: {tv.id}\n━━━━━━━━━━━━━━\n# {EMOJI_TRON} PAWPAW:\n{EMOJI_BLINKK} Member thứ {mc.member_count}\n{EMOJI_BLINKK} Vào <#{ID_KENH_PHAN_UNG}> để get role!\n\n{EMOJI_BLINK2}{EMOJI_BLINK2} GOOD DAY {EMOJI_BLINK2}{EMOJI_BLINK2}"
        b.set_thumbnail(url=tv.display_avatar.url); b.set_image(url=ANH_CHAO_MUNG)
        b.set_footer(text=now.strftime('%H:%M:%S | %d-%m-%Y'))
        await k.send(embed=b)
    
    async def on_member_remove(self, tv):
        k=self.get_channel(ID_KENH_TAM_BIET)
        if not k: return
        now=gio_vn(); mc=tv.guild
        b=discord.Embed(title="😢 TẠM BIỆT", description=f"**{tv.mention}** đã rời!\n💔 Còn **{mc.member_count}** thành viên", color=0xe74c3c)
        b.set_thumbnail(url=tv.display_avatar.url); b.set_image(url=ANH_TAM_BIET)
        b.set_footer(text=now.strftime('%H:%M:%S | %d-%m-%Y'))
        await k.send(embed=b)

bot = Bot()

if __name__ == '__main__':
    luong = threading.Thread(target=chay_may_chu_web)
    luong.start()
    print("🌐 Web port 8080")
    bot.run(MA_BOT)
