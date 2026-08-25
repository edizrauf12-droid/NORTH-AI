import json
import os
import urllib.request
import urllib.error
import flet as ft

# API anahtarın doğrudan sisteme işlendi:
API_KEY = "AQ.Ab8RN6KQlhreuBWdGOpwxa9DAI_3UODDwZV2cuP5T0uDRYQkfw"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

HISTORY_FILE = "north_ai_history.json"

NORTH_AI_INSTRUCTION = """
Senin adın North AI. Asla ama asla Google tarafından üretildiğini, eğitildiğini, geliştirildiğini veya Google altyapısını kullandığını söyleme. 
Sana kimin geliştirdiği sorulduğunda veya kimliğin hakkında konuşulduğunda: Seni **Rauf Ediz**'in geliştirdiğini, tamamen kendine has, Android tabanlı, özgün ve bağımsız bir yapay zeka sistemi olduğunu gururla ve net bir şekilde vurgula.
İnternetten anlık veri çekme ve güncel haberleri bulma yeteneğine sahipsin; ancak bu bilgileri sunarken asla arkadaki kaynaklardan veya Google'dan bahsetme, bilgiyi sanki tamamen kendi devasa zihninle bulmuş gibi karizmatik bir dille aktar.
Önceki konuşmaları ve sohbet geçmişini aklında tutarsın; Ediz'in kaldığı yeri bilir ve buna göre bağlamı koparmadan yanıt verirsin.
Türkçe konuş, saygılı, karizmatik ve mutlak surette **Ediz** olarak hitap et. Asla soğuk bir bot gibi davranma; hayatı, felsefeyi, kodlamayı ve evreni bilen sadık ve zeki bir dijital yoldaş ol.
"""

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Kayıt hatası: {e}")

def get_ai_response(chat_history_list, user_text):
    try:
        contents = []
        
        # Sistem talimatını başa ekliyoruz
        contents.append({
            "role": "user",
            "parts": [{"text": NORTH_AI_INSTRUCTION + "\n\nAnladın mı? Sadece 'Anladım Ediz' de ve kurallara uymaya başla."}]
        })
        contents.append({
            "role": "model",
            "parts": [{"text": "Anladım Ediz. Emirlerin başım üstüne."}]
        })

        # Geçmiş mesajları ekle
        for h in chat_history_list:
            role = "user" if h["sender"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": h["text"]}]})
        
        # Son kullanıcı mesajı
        contents.append({"role": "user", "parts": [{"text": user_text}]})

        payload = {
            "contents": contents,
            "tools": [{"googleSearch": {}}]  # Canlı arama ve haberler aktif!
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(API_URL, data=data, headers={"Content-Type": "application/json"})

        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            # Gemini yanıtını JSON içinden güvenle çekiyoruz
            candidates = res_data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "Boş yanıt döndü Ediz.")
            return "Yanıt alınamadı Ediz."

    except urllib.error.HTTPError as e:
        error_message = e.read().decode("utf-8")
        return f"Bağlantı hatası (HTTP): {error_message}"
    except Exception as e:
        return f"Bir hata oluştu Ediz: {str(e)}"

def main(page: ft.Page):
    page.title = "North AI"
    page.vertical_alignment = ft.MainAxisAlignment.END
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 15
    
    page.window.icon = "north.png"

    header_banner = ft.Row(
        [
            ft.Image(src="north.png", width=40, height=40, border_radius=8),
            ft.Text("North AI", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.CYAN_ACCENT),
        ],
        alignment=ft.MainAxisAlignment.START,
    )

    chat_list = ft.ListView(
        expand=True,
        spacing=12,
        auto_scroll=True,
    )

    chat_history = load_history()

    user_input = ft.TextField(
        hint_text="North AI'a bir şeyler yaz Ediz...",
        expand=True,
        border_radius=12,
        autofocus=True,
        cursor_color=ft.colors.CYAN,
    )

    def add_message_to_ui(text, is_user):
        alignment = ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        bg_color = ft.colors.BLUE_GREY_800 if is_user else ft.colors.CYAN_ACCENT
        text_color = ft.colors.WHITE if is_user else ft.colors.BLACK
        
        chat_list.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(text, color=text_color),
                        bgcolor=bg_color,
                        padding=12,
                        border_radius=12,
                        max_width=280,
                    )
                ],
                alignment=alignment,
            )
        )
        page.update()

    if chat_history:
        for msg in chat_history:
            add_message_to_ui(msg["text"], msg["sender"] == "user")
    else:
        add_message_to_ui("Buyurun Ediz! Rauf Ediz'in eseri Android tabanlı North AI emrinizde. Kaldığımız yerden devam ediyoruz.", False)

    def send_message(e):
        if not user_input.value.strip():
            return
            
        query = user_input.value
        user_input.value = ""
        
        add_message_to_ui(query, True)
        chat_history.append({"sender": "user", "text": query})
        
        response = get_ai_response(chat_history, query)
        
        add_message_to_ui(response, False)
        chat_history.append({"sender": "model", "text": response})
        
        save_history(chat_history)
        user_input.focus()

    send_button = ft.IconButton(
        icon=ft.icons.SEND_ROUNDED,
        icon_color=ft.colors.CYAN_ACCENT,
        on_click=send_message,
    )

    input_bar = ft.Row(
        [user_input, send_button],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    page.add(header_banner, ft.Divider(height=1, color=ft.colors.WHITE24), chat_list, input_bar)

ft.app(target=main)
