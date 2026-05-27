from flask import Flask, request, jsonify
import requests
import os
import json
import asyncio
import jwt
import urllib3
import ssl
import gzip
import http.client
import time
from io import BytesIO
import threading
from datetime import datetime
from protobuf_decoder.protobuf_decoder import Parser
from byte import *
import xKEys
from google.protobuf.timestamp_pb2 import Timestamp

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Lưu trạng thái spam
spam_sessions = {}

# ==================== GIỮ NGUYÊN CODE CŨ ====================
def G_AccEss(U, P):
    UrL = "https://100067.connect.garena.com/oauth/guest/token/grant"
    HE = {
        "Host": "100067.connect.garena.com",
        "User-Agent": Ua(),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
    }
    dT = {
        "uid": f"{U}",
        "password": f"{P}",
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067",
    }
    try:
        R = requests.post(UrL, headers=HE, data=dT)
        if R.status_code == 200:
            return R.json()["access_token"], R.json()["open_id"]
    except Exception as e:
        print(f"[-] Lỗi G_AccEss: {e}")
    return None, None

def MajorLoGin(PyL):
    context = ssl._create_unverified_context()
    conn = http.client.HTTPSConnection("loginbp.ggpolarbear.com", context=context)
    headers = {
        "X-Unity-Version": "2018.4.11f1",
        "ReleaseVersion": "OB53",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-GA": "v1 1",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)",
        "Host": "loginbp.ggpolarbear.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }
    try:
        conn.request("POST", "/MajorLogin", body=PyL, headers=headers)
        response = conn.getresponse()
        raw_data = response.read()
        if response.getheader("Content-Encoding") == "gzip":
            with gzip.GzipFile(fileobj=BytesIO(raw_data)) as f:
                raw_data = f.read()
        TexT = raw_data.decode(errors="ignore")
        if "BR_PLATFORM_INVALID_OPENID" in TexT or "BR_GOP_TOKEN_AUTH_FAILED" in TexT:
            return None
        return raw_data.hex() if response.status in [200, 201] else None
    finally:
        conn.close()

class FF_CLient:
    def __init__(self, U, P, target_uid, bot_index, session_id):
        self.target_uid = target_uid
        self.bot_index = bot_index
        self.session_id = session_id
        self.result = {"success": False, "message": "", "bot_uid": None}
        self.Get_FiNal_ToKen_0115(U, P)

    async def ExeCuTe_InViTe(self, tok, ip, port, ip2, port2, key, iv, bot_uid):
        if not self.target_uid:
            self.result["message"] = "No target UID"
            return

        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            writer.write(bytes.fromhex(tok))
            await writer.drain()
            await asyncio.sleep(0.4)
            writer.write(GLobaL("fr", key, iv))
            await writer.drain()

            reader2, writer2 = await asyncio.open_connection(ip2, int(port2))
            writer2.write(bytes.fromhex(tok))
            await writer2.drain()
            await asyncio.sleep(0.4)

            self.result["message"] = f"Bot {bot_uid} đang gửi invite tới {self.target_uid}"
            
            success_count = 0
            for i in range(6):
                try:
                    writer2.write(RedZed_SendInv(int(self.target_uid), key, iv))
                    await writer2.drain()
                    success_count += 1
                    await asyncio.sleep(0.2)
                except Exception as e:
                    print(f"Lần {i+1} lỗi: {e}")

            self.result["success"] = success_count > 0
            self.result["message"] += f" | Đã gửi {success_count}/6 invite"
            self.result["bot_uid"] = bot_uid

            writer.close()
            writer2.close()
            await writer.wait_closed()
            await writer2.wait_closed()

        except Exception as e:
            self.result["message"] = f"Lỗi Socket: {e}"

    def GeT_Key_Iv(self, serialized_data):
        my_message = xKEys.MyMessage()
        my_message.ParseFromString(serialized_data)
        timestamp, key, iv = my_message.field21, my_message.field22, my_message.field23
        timestamp_obj = Timestamp()
        timestamp_obj.FromNanoseconds(timestamp)
        timestamp_seconds = timestamp_obj.seconds
        timestamp_nanos = timestamp_obj.nanos
        combined_timestamp = timestamp_seconds * 1_000_000_000 + timestamp_nanos
        return combined_timestamp, key, iv

    def GeT_LoGin_PorTs(self, JwT_ToKen, PayLoad):
        UrL = "https://clientbp.ggpolarbear.com/GetLoginData"
        HeadErs = {
            "Expect": "100-continue",
            "Authorization": f"Bearer {JwT_ToKen}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB53",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
            "Host": "clientbp.ggpolarbear.com",
            "Connection": "close",
            "Accept-Encoding": "gzip, deflate, br",
        }
        try:
            Res = requests.post(UrL, headers=HeadErs, data=PayLoad, verify=False)
            BesTo_data = json.loads(DeCode_PackEt(Res.content.hex()))
            address, address2 = BesTo_data["32"]["data"], BesTo_data["14"]["data"]
            ip, ip2 = address[: len(address) - 6], address2[: len(address2) - 6]
            port, port2 = address[len(address) - 5:], address2[len(address2) - 5:]
            return ip, port, ip2, port2
        except Exception:
            return None, None, None, None

    def ToKen_GeneRaTe(self, U, P):
        try:
            self.A, self.O = G_AccEss(U, P)
            if not self.A:
                return None
            
            PLaFTrom = 4
            Version, V = "2019120270", "1.123.1"
            
            PyL = {
                3: str(datetime.now())[:-7], 4: "free fire", 5: 4, 7: V,
                8: "Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)",
                9: "Handheld", 10: "Verizon Wireless", 11: "WIFI", 12: 1280, 13: 960,
                14: "240", 15: "x86-64 SSE3 SSE4.1 SSE4.2 AVX AVX2 | 2400 | 4",
                16: 5951, 17: "Adreno (TM) 640", 18: "OpenGL ES 3.0",
                19: "Google|0fc0e446-ca27-4faa-824a-d40d77767de9",
                20: "20.171.73.202", 21: "fr", 22: self.O, 23: PLaFTrom,
                24: "Handheld", 25: "google G011A", 29: self.A, 30: 1,
                41: "Verizon Wireless", 42: "WIFI", 57: "1ac4b80ecf0478a44203bf8fac6120f5",
                60: 32966, 61: 29779, 62: 2479, 63: 914, 64: 31176,
                65: 32966, 66: 31176, 67: 32966, 70: 4, 73: 2,
                74: "/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/lib/arm",
                76: 1, 77: "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/base.apk",
                78: 6, 79: 1, 81: "32", 83: Version, 86: "OpenGLES2",
                87: 255, 88: PLaFTrom, 89: "J\u0003FD\u0004\r_UH\u0003\u000b\u0016_\u0003D^J>\u000fWT\u0000\\=\nQ_;\u0000\r;Z\u0005a",
                90: "Phoenix", 91: "AZ", 92: 10214, 93: "3rd_party",
                94: "KqsHT7gtKWkK0gY/HwmdwXIhSiz4fQldX3YjZeK86XBTthKAf1bW4Vsz6Di0S8vqr0Jc4HX3TMQ8KaUU3GeVvYzWF9I=",
                95: 111207, 97: 1, 98: 1, 99: f"{PLaFTrom}", 100: f"{PLaFTrom}",
            }
            
            PyL_hex = CrEaTe_ProTo(PyL).hex()
            PaYload = bytes.fromhex(EnC_AEs(PyL_hex))
            ResPonse = MajorLoGin(PaYload)
            
            if ResPonse:
                BesTo_data = json.loads(DeCode_PackEt(ResPonse))
                bot_uid = BesTo_data["4"]["data"]
                JwT_ToKen = BesTo_data["8"]["data"]
                combined_timestamp, key, iv = self.GeT_Key_Iv(bytes.fromhex(ResPonse))
                ip, port, ip2, port2 = self.GeT_LoGin_PorTs(JwT_ToKen, PaYload)
                return JwT_ToKen, key, iv, combined_timestamp, ip, port, ip2, port2, bot_uid
        except Exception as e:
            print(f"Lỗi Login: {e}")
        return None

    def Get_FiNal_ToKen_0115(self, U, P):
        data = self.ToKen_GeneRaTe(U, P)
        if not data:
            self.result["message"] = "Login failed"
            return
        
        token, key, iv, Timestamp, ip, port, ip2, port2, bot_uid = data

        try:
            AfTer_DeC_JwT = jwt.decode(token, options={"verify_signature": False})
            AccounT_Uid = AfTer_DeC_JwT.get("account_id")
            EncoDed_AccounT = hex(AccounT_Uid)[2:]
            TimE_HEx = DecodE_HeX(Timestamp)
            JwT_ToKen_ = token.encode().hex()
            
            Header = hex(len(EnC_PacKeT(JwT_ToKen_, key, iv)) // 2)[2:]
            length = len(EncoDed_AccounT)
            __ = "00000000"
            if length == 9:
                __ = "0000000"
            elif length == 8:
                __ = "00000000"
            elif length == 10:
                __ = "000000"
            elif length == 7:
                __ = "000000000"

            Header = f"0115{__}{EncoDed_AccounT}{TimE_HEx}00000{Header}"
            AutH_ToKen = Header + EnC_PacKeT(JwT_ToKen_, key, iv)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.ExeCuTe_InViTe(AutH_ToKen, ip, port, ip2, port2, key, iv, bot_uid))
            loop.close()
            
        except Exception as e:
            self.result["message"] = f"Lỗi tạo token: {e}"


def load_accounts():
    """Load accounts from acc.json"""
    file_path = "acc.json"
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ==================== API ENDPOINTS ====================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "running",
        "service": "FF Spam Bot API",
        "how_to_use": {
            "spam": "/spam?uid=123456789",
            "spam_with_limit": "/spam?uid=123456789&limit=10",
            "status": "/spam/status/<session_id>",
            "accounts": "/accounts",
            "health": "/health"
        }
    })


@app.route('/spam', methods=['GET'])
def start_spam():
    """Bắt đầu spam invite tới UID mục tiêu (dùng query parameter ?uid=xxx)"""
    target_uid = request.args.get('uid')
    
    if not target_uid:
        return jsonify({"error": "Thiếu tham số 'uid'. Dùng: /spam?uid=123456789"}), 400
    
    # Lấy số lượng bot muốn dùng (tùy chọn)
    bot_count = request.args.get('limit', 0, type=int)
    
    accounts = load_accounts()
    if not accounts:
        return jsonify({"error": "Không tìm thấy accounts trong acc.json"}), 404
    
    # Giới hạn số bot nếu có
    account_items = list(accounts.items())
    if bot_count > 0 and bot_count < len(account_items):
        account_items = account_items[:bot_count]
    
    # Tạo session ID
    import uuid
    session_id = str(uuid.uuid4())
    
    # Chạy spam trong thread riêng
    def run_spam():
        results = []
        for i, (uid, pwd) in enumerate(account_items):
            try:
                client = FF_CLient(uid, pwd, target_uid, i + 1, session_id)
                results.append(client.result)
            except Exception as e:
                results.append({
                    "success": False,
                    "message": f"Lỗi: {e}",
                    "bot_uid": None
                })
        
        spam_sessions[session_id] = {
            "status": "completed",
            "target_uid": target_uid,
            "total_bots": len(account_items),
            "results": results,
            "completed_at": datetime.now().isoformat()
        }
    
    thread = threading.Thread(target=run_spam)
    thread.start()
    
    spam_sessions[session_id] = {
        "status": "running",
        "target_uid": target_uid,
        "total_bots": len(account_items),
        "results": [],
        "started_at": datetime.now().isoformat()
    }
    
    return jsonify({
        "success": True,
        "session_id": session_id,
        "message": f"Đã bắt đầu spam tới {target_uid} với {len(account_items)} bots",
        "status_url": f"/spam/status/{session_id}"
    })


@app.route('/spam/status/<session_id>', methods=['GET'])
def get_spam_status(session_id):
    """Lấy trạng thái spam session"""
    if session_id not in spam_sessions:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(spam_sessions[session_id])


@app.route('/spam/stop/<session_id>', methods=['POST'])
def stop_spam(session_id):
    """Dừng spam session"""
    if session_id not in spam_sessions:
        return jsonify({"error": "Session not found"}), 404
    
    spam_sessions[session_id]["status"] = "stopped"
    spam_sessions[session_id]["stopped_at"] = datetime.now().isoformat()
    
    return jsonify({
        "success": True,
        "message": f"Đã dừng session {session_id}"
    })


@app.route('/accounts', methods=['GET'])
def get_accounts():
    """Xem danh sách accounts (ẩn password)"""
    accounts = load_accounts()
    
    safe_accounts = {
        uid: "***HIDDEN***" for uid in accounts.keys()
    }
    
    return jsonify({
        "total": len(accounts),
        "accounts": safe_accounts
    })


@app.route('/accounts/count', methods=['GET'])
def get_accounts_count():
    """Đếm số lượng accounts"""
    accounts = load_accounts()
    return jsonify({"total": len(accounts)})


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    accounts = load_accounts()
    return jsonify({
        "status": "healthy",
        "accounts_loaded": len(accounts),
        "active_sessions": len([s for s in spam_sessions.values() if s["status"] == "running"])
    })


if __name__ == "__main__":
    print("=" * 50)
    print("   FF SPAM BOT API (Original)")
    print("=" * 50)
    print(f"Loaded {len(load_accounts())} accounts from acc.json")
    print("")
    print("📌 Cách dùng:")
    print(f"   - Spam: curl 'http://localhost:5000/spam?uid=123456789'")
    print(f"   - Spam 10 bot: curl 'http://localhost:5000/spam?uid=123456789&limit=10'")
    print(f"   - Xem accounts: curl 'http://localhost:5000/accounts'")
    print(f"   - Health check: curl 'http://localhost:5000/health'")
    print("=" * 50)
    print("🌐 API running on http://0.0.0.0:5000")
    print("=" * 50)
    
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)