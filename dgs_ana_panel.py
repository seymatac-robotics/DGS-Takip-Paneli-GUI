import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import date, datetime, timedelta
import json
import os
import calendar

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


APP_TITLE = "DGS 2027 Takip Paneli"
EXAM_DATE = date(2027, 7, 19)
DATA_FILE = "dgs_verileri.json"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


DEFAULT_DATA = {
    "gunluk_kayitlar": {},
    "konu_soru_kayitlari": {},
    "deneme_kayitlari": [],
    "hedefler": {
        "gunluk_soru": 120,
        "gunluk_dakika": 90,
        "haftalik_soru": 750,
        "haftalik_dakika": 540
    },
    "pomodoro": {
        "bugun_tamamlanan": 0,
        "son_tarih": date.today().isoformat()
    },
    "konular": {
        "Matematik": {
            "Temel Kavramlar": False,
            "Sayı Basamakları": False,
            "Bölme ve Bölünebilme": False,
            "Asal Çarpanlara Ayırma": False,
            "EBOB - EKOK": False,
            "Rasyonel Sayılar": False,
            "Basit Eşitsizlikler": False,
            "Mutlak Değer": False,
            "Üslü Sayılar": False,
            "Köklü Sayılar": False,
            "Çarpanlara Ayırma": False,
            "Denklemler": False,
            "Problemler": False,
            "Sayı Problemleri": False,
            "Kesir Problemleri": False,
            "Yaş Problemleri": False,
            "İşçi - Havuz Problemleri": False,
            "Yüzde Problemleri": False,
            "Kar - Zarar Problemleri": False,
            "Karışım Problemleri": False,
            "Hareket Problemleri": False,
            "Kümeler": False,
            "Fonksiyonlar": False,
            "Permütasyon": False,
            "Kombinasyon": False,
            "Olasılık": False,
            "Sayısal Mantık": False,
            "Geometri Temelleri": False,
            "Üçgenler": False,
            "Dörtgenler": False,
            "Çember ve Daire": False,
            "Analitik Geometri": False
        },
        "Türkçe": {
            "Sözcükte Anlam": False,
            "Cümlede Anlam": False,
            "Paragrafta Anlam": False,
            "Paragraf Yapısı": False,
            "Ana Düşünce": False,
            "Yardımcı Düşünce": False,
            "Paragraf Tamamlama": False,
            "Paragraf Sıralama": False,
            "Anlatım Biçimleri": False,
            "Düşünceyi Geliştirme Yolları": False,
            "Sözel Mantık": False,
            "Dil Bilgisi Genel Tekrar": False,
            "Ses Bilgisi": False,
            "Yazım Kuralları": False,
            "Noktalama İşaretleri": False,
            "Fiilimsi": False,
            "Cümlenin Ögeleri": False,
            "Cümle Türleri": False,
            "Anlatım Bozukluğu": False
        }
    }
}


class DataManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_data()
        self.reset_pomodoro_if_new_day()

    def load_data(self):
        if not os.path.exists(self.file_path):
            self.data = json.loads(json.dumps(DEFAULT_DATA, ensure_ascii=False))
            self.save_data()
            return self.data

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                loaded_data = json.load(file)
        except (json.JSONDecodeError, OSError):
            self.data = json.loads(json.dumps(DEFAULT_DATA, ensure_ascii=False))
            self.save_data()
            return self.data

        return self.merge_defaults(loaded_data)

    def merge_defaults(self, loaded_data):
        merged = json.loads(json.dumps(DEFAULT_DATA, ensure_ascii=False))
        merged["gunluk_kayitlar"] = loaded_data.get("gunluk_kayitlar", {})
        merged["konu_soru_kayitlari"] = loaded_data.get("konu_soru_kayitlari", {})
        merged["deneme_kayitlari"] = loaded_data.get("deneme_kayitlari", [])
        merged["hedefler"].update(loaded_data.get("hedefler", {}))
        merged["pomodoro"].update(loaded_data.get("pomodoro", {}))

        loaded_subjects = loaded_data.get("konular", {})
        for category, topics in merged["konular"].items():
            for topic in topics:
                if category in loaded_subjects and topic in loaded_subjects[category]:
                    merged["konular"][category][topic] = bool(loaded_subjects[category][topic])

        self.data = merged
        self.save_data()
        return merged

    def save_data(self, data=None):
        if data is not None:
            self.data = data
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def reset_pomodoro_if_new_day(self):
        today = date.today().isoformat()
        if self.data["pomodoro"].get("son_tarih") != today:
            self.data["pomodoro"] = {"bugun_tamamlanan": 0, "son_tarih": today}
            self.save_data()

    def save_daily_record(self, questions, minutes):
        today_key = date.today().isoformat()
        self.data["gunluk_kayitlar"][today_key] = {
            "soru": int(questions),
            "dakika": int(minutes),
            "kayit_zamani": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save_data()

    def get_today_record(self):
        return self.data["gunluk_kayitlar"].get(date.today().isoformat(), {"soru": 0, "dakika": 0})

    def get_week_totals(self):
        today = date.today()
        start = today - timedelta(days=today.weekday())
        total_q = 0
        total_m = 0
        for i in range(7):
            key = (start + timedelta(days=i)).isoformat()
            item = self.data["gunluk_kayitlar"].get(key, {})
            total_q += item.get("soru", 0)
            total_m += item.get("dakika", 0)
        return total_q, total_m

    def set_topic_status(self, category, topic, status):
        self.data["konular"][category][topic] = bool(status)
        self.save_data()

    def get_topic_stats(self):
        total = 0
        completed = 0
        for category in self.data["konular"].values():
            total += len(category)
            completed += sum(1 for value in category.values() if value)
        percent = int((completed / total) * 100) if total else 0
        return completed, total, percent

    def save_goals(self, daily_q, daily_m, weekly_q, weekly_m):
        self.data["hedefler"] = {
            "gunluk_soru": int(daily_q),
            "gunluk_dakika": int(daily_m),
            "haftalik_soru": int(weekly_q),
            "haftalik_dakika": int(weekly_m)
        }
        self.save_data()

    def add_exam_record(self, month, verbal_net, numerical_net):
        record = {
            "ay": month,
            "sozel_net": float(verbal_net),
            "sayisal_net": float(numerical_net),
            "toplam_net": float(verbal_net) + float(numerical_net),
            "kayit_zamani": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data["deneme_kayitlari"].append(record)
        self.save_data()

    def delete_exam_record(self, index):
        if 0 <= index < len(self.data["deneme_kayitlari"]):
            self.data["deneme_kayitlari"].pop(index)
            self.save_data()

    def get_last_7_days_question_data(self):
        labels = []
        values = []
        today = date.today()
        for i in range(6, -1, -1):
            current_day = today - timedelta(days=i)
            key = current_day.isoformat()
            labels.append(current_day.strftime("%d.%m"))
            values.append(self.data["gunluk_kayitlar"].get(key, {}).get("soru", 0))
        return labels, values

    def add_topic_question_record(self, category, topic, count):
        today_key = date.today().isoformat()
        if today_key not in self.data["konu_soru_kayitlari"]:
            self.data["konu_soru_kayitlari"][today_key] = []
        self.data["konu_soru_kayitlari"][today_key].append({
            "ders": category,
            "konu": topic,
            "soru": int(count),
            "kayit_zamani": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.save_data()

    def get_topic_question_totals(self):
        totals = {}
        for records in self.data.get("konu_soru_kayitlari", {}).values():
            for item in records:
                key = f"{item.get('ders')} / {item.get('konu')}"
                totals[key] = totals.get(key, 0) + item.get("soru", 0)
        return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))

    def increment_pomodoro(self):
        self.reset_pomodoro_if_new_day()
        self.data["pomodoro"]["bugun_tamamlanan"] += 1
        self.save_data()

    def get_streak(self):
        records = self.data.get("gunluk_kayitlar", {})
        streak = 0
        current = date.today()
        while True:
            key = current.isoformat()
            item = records.get(key)
            if item and (item.get("soru", 0) > 0 or item.get("dakika", 0) > 0):
                streak += 1
                current -= timedelta(days=1)
            else:
                break
        return streak


class CountdownRing(ctk.CTkCanvas):
    def __init__(self, master, size=230, thickness=18, **kwargs):
        super().__init__(master, width=size, height=size, bg="#111827", highlightthickness=0, **kwargs)
        self.size = size
        self.thickness = thickness
        self.draw_ring()

    def draw_ring(self):
        self.delete("all")
        days_left = max((EXAM_DATE - date.today()).days, 0)
        total_days_reference = 365
        progress = max(0, min(1, 1 - (days_left / total_days_reference)))
        ring_color = "#3b82f6" if days_left >= 100 else "#ef4444"
        padding = self.thickness + 8
        self.create_oval(padding, padding, self.size - padding, self.size - padding, outline="#263244", width=self.thickness)
        self.create_arc(padding, padding, self.size - padding, self.size - padding, start=90, extent=-360 * progress, style="arc", outline=ring_color, width=self.thickness)
        self.create_text(self.size / 2, self.size / 2 - 14, text=str(days_left), fill="#f9fafb", font=("Segoe UI", 42, "bold"))
        self.create_text(self.size / 2, self.size / 2 + 35, text="gün kaldı", fill="#9ca3af", font=("Segoe UI", 15, "bold"))
        if days_left < 100:
            self.create_text(self.size / 2, self.size - 28, text="Son 100 gün modu", fill="#fca5a5", font=("Segoe UI", 12, "bold"))


class SidebarButton(ctk.CTkButton):
    def __init__(self, master, icon, text, command):
        self.icon = icon
        self.full_text = text
        super().__init__(master, text=f"{icon}  {text}", command=command, anchor="w", height=42, corner_radius=12, fg_color="transparent", hover_color="#1f2937", text_color="#e5e7eb", font=("Segoe UI", 14, "bold"))

    def set_collapsed(self, collapsed):
        self.configure(text=self.icon if collapsed else f"{self.icon}  {self.full_text}", anchor="center" if collapsed else "w", width=48 if collapsed else 190)


class DGSTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1240x760")
        self.minsize(1060, 660)
        self.configure(fg_color="#0b1120")
        self.data_manager = DataManager(DATA_FILE)
        self.sidebar_collapsed = False
        self.checkbox_vars = {}
        self.pomodoro_seconds = 25 * 60
        self.pomodoro_running = False
        self.pomodoro_after_id = None
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.create_sidebar()
        self.content = ctk.CTkFrame(self, fg_color="#0b1120", corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)
        self.show_home_page()

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=240, fg_color="#111827", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self.menu_button = ctk.CTkButton(self.sidebar, text="☰  Menü", command=self.toggle_sidebar, height=44, fg_color="#2563eb", hover_color="#1d4ed8", corner_radius=14, font=("Segoe UI", 15, "bold"))
        self.menu_button.pack(padx=16, pady=(18, 18), fill="x")
        self.sidebar_title = ctk.CTkLabel(self.sidebar, text="DGS 2027", font=("Segoe UI", 22, "bold"), text_color="#f9fafb")
        self.sidebar_title.pack(pady=(0, 14))
        self.buttons = []
        items = [
            ("🏠", "Ana Sayfa", self.show_home_page),
            ("✅", "Müfredat", self.show_curriculum_page),
            ("📈", "Grafikler", self.show_graph_page),
            ("🗓", "Deneme Takvimi", self.show_exam_calendar_page),
            ("🔥", "Hedef & Streak", self.show_goals_page),
            ("🍅", "Pomodoro", self.show_pomodoro_page),
            ("📊", "Konu Analizi", self.show_topic_analysis_page),
            ("📅", "Çalışma Takvimi", self.show_calendar_page),
            ("📌", "Özet", self.show_stats_page)
        ]
        for icon, text, cmd in items:
            button = SidebarButton(self.sidebar, icon, text, cmd)
            button.pack(padx=16, pady=4, fill="x")
            self.buttons.append(button)
        self.footer_label = ctk.CTkLabel(self.sidebar, text="Hedef: 19 Temmuz 2027", text_color="#9ca3af", font=("Segoe UI", 12))
        self.footer_label.pack(side="bottom", pady=18)

    def toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed
        self.sidebar.configure(width=76 if self.sidebar_collapsed else 240)
        self.menu_button.configure(text="☰" if self.sidebar_collapsed else "☰  Menü", width=44 if self.sidebar_collapsed else 190)
        self.sidebar_title.configure(text="" if self.sidebar_collapsed else "DGS 2027")
        self.footer_label.configure(text="" if self.sidebar_collapsed else "Hedef: 19 Temmuz 2027")
        for button in self.buttons:
            button.set_collapsed(self.sidebar_collapsed)

    def clear_content(self):
        if self.pomodoro_after_id:
            try:
                self.after_cancel(self.pomodoro_after_id)
            except Exception:
                pass
            self.pomodoro_after_id = None
        for widget in self.content.winfo_children():
            widget.destroy()

    def page_header(self, title, subtitle):
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(28, 12))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text=title, font=("Segoe UI", 30, "bold"), text_color="#f9fafb", anchor="w").grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(header, text=subtitle, font=("Segoe UI", 14), text_color="#9ca3af", anchor="w").grid(row=1, column=0, sticky="ew", pady=(4, 0))

    def create_card(self, master, title=None):
        card = ctk.CTkFrame(master, fg_color="#111827", corner_radius=24)
        if title:
            ctk.CTkLabel(card, text=title, font=("Segoe UI", 18, "bold"), text_color="#f9fafb", anchor="w").pack(fill="x", padx=22, pady=(20, 8))
        return card

    def stat_card(self, master, title, value, icon, column):
        card = ctk.CTkFrame(master, fg_color="#111827", corner_radius=22)
        card.grid(row=0, column=column, sticky="ew", padx=8)
        ctk.CTkLabel(card, text=icon, font=("Segoe UI Emoji", 30), text_color="#f9fafb").pack(pady=(18, 2))
        ctk.CTkLabel(card, text=value, font=("Segoe UI", 26, "bold"), text_color="#f9fafb").pack()
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 12, "bold"), text_color="#9ca3af").pack(pady=(2, 18))
        return card

    def add_progress(self, master, label, current, target):
        percent = min(current / target, 1) if target else 0
        ctk.CTkLabel(master, text=f"{label}: {current}/{target}", text_color="#e5e7eb", font=("Segoe UI", 13, "bold"), anchor="w").pack(fill="x", padx=22, pady=(10, 4))
        bar = ctk.CTkProgressBar(master, height=14, corner_radius=20)
        bar.pack(fill="x", padx=22, pady=(0, 8))
        bar.set(percent)

    def show_home_page(self):
        self.clear_content()
        self.page_header("Ana Sayfa", "DGS hedefini her gün küçük ama net adımlarla takip et.")
        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=30, pady=16)
        body.grid_columnconfigure((0, 1), weight=1)
        body.grid_rowconfigure(0, weight=1)

        countdown_card = self.create_card(body, "Sınava Geri Sayım")
        countdown_card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        ring_container = ctk.CTkFrame(countdown_card, fg_color="#111827")
        ring_container.pack(expand=True)
        CountdownRing(ring_container).pack(pady=20)
        ctk.CTkLabel(countdown_card, text="19 Temmuz 2027 DGS", text_color="#93c5fd", font=("Segoe UI", 16, "bold")).pack(pady=(0, 16))
        ctk.CTkLabel(countdown_card, text=f"🔥 Çalışma serin: {self.data_manager.get_streak()} gün", text_color="#fbbf24", font=("Segoe UI", 16, "bold")).pack(pady=(0, 22))

        daily_card = self.create_card(body, "Bugünün Çalışması")
        daily_card.grid(row=0, column=1, sticky="nsew", padx=(14, 0))
        today_record = self.data_manager.get_today_record()
        form = ctk.CTkFrame(daily_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=26, pady=18)
        ctk.CTkLabel(form, text="Çözülen soru sayısı", text_color="#d1d5db", font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x", pady=(4, 6))
        self.question_entry = ctk.CTkEntry(form, height=46, corner_radius=14, placeholder_text="Örn: 120", font=("Segoe UI", 15))
        self.question_entry.pack(fill="x", pady=(0, 18))
        self.question_entry.insert(0, str(today_record.get("soru", 0)))
        ctk.CTkLabel(form, text="Çalışılan dakika", text_color="#d1d5db", font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x", pady=(4, 6))
        self.minute_entry = ctk.CTkEntry(form, height=46, corner_radius=14, placeholder_text="Örn: 90", font=("Segoe UI", 15))
        self.minute_entry.pack(fill="x", pady=(0, 20))
        self.minute_entry.insert(0, str(today_record.get("dakika", 0)))
        ctk.CTkButton(form, text="Bugünkü Kaydı Kaydet", height=48, corner_radius=16, fg_color="#2563eb", hover_color="#1d4ed8", font=("Segoe UI", 15, "bold"), command=self.save_daily_record).pack(fill="x", pady=(4, 18))
        goals = self.data_manager.data["hedefler"]
        self.add_progress(form, "Günlük soru hedefi", today_record.get("soru", 0), goals["gunluk_soru"])
        self.add_progress(form, "Günlük dakika hedefi", today_record.get("dakika", 0), goals["gunluk_dakika"])

    def save_daily_record(self):
        try:
            questions = int(self.question_entry.get().strip())
            minutes = int(self.minute_entry.get().strip())
            if questions < 0 or minutes < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Hatalı Giriş", "Soru ve dakika alanlarına 0 veya pozitif tam sayı girmelisin.")
            return
        self.data_manager.save_daily_record(questions, minutes)
        messagebox.showinfo("Kaydedildi", "Bugünkü çalışma kaydın kaydedildi.")
        self.show_home_page()

    def show_curriculum_page(self):
        self.clear_content()
        self.page_header("Müfredat Takibi", "Matematik ve Türkçe konularını checklist ile takip et.")
        main = ctk.CTkFrame(self.content, fg_color="transparent")
        main.grid(row=1, column=0, sticky="nsew", padx=30, pady=16)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)
        completed, total, percent = self.data_manager.get_topic_stats()
        progress_card = ctk.CTkFrame(main, fg_color="#111827", corner_radius=22)
        progress_card.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        progress_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(progress_card, text=f"Genel ilerleme: %{percent} • {completed}/{total} konu", font=("Segoe UI", 16, "bold"), text_color="#f9fafb", anchor="w").grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 8))
        bar = ctk.CTkProgressBar(progress_card, height=14, corner_radius=20)
        bar.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 20))
        bar.set(percent / 100)
        scroll = ctk.CTkScrollableFrame(main, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure((0, 1), weight=1)
        self.checkbox_vars.clear()
        for column_index, (category, topics) in enumerate(self.data_manager.data["konular"].items()):
            category_card = self.create_card(scroll, category)
            category_card.grid(row=0, column=column_index, sticky="nsew", padx=8, pady=8)
            done = sum(1 for value in topics.values() if value)
            ctk.CTkLabel(category_card, text=f"{done}/{len(topics)} konu tamamlandı", text_color="#9ca3af", font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x", padx=22, pady=(0, 10))
            for topic, is_done in topics.items():
                var = tk.BooleanVar(value=is_done)
                checkbox = ctk.CTkCheckBox(category_card, text=topic, variable=var, command=lambda c=category, t=topic, v=var: self.on_topic_toggle(c, t, v), font=("Segoe UI", 13), text_color="#e5e7eb", fg_color="#2563eb", hover_color="#1d4ed8", border_color="#64748b", corner_radius=8)
                checkbox.pack(anchor="w", padx=22, pady=7)

    def on_topic_toggle(self, category, topic, variable):
        self.data_manager.set_topic_status(category, topic, variable.get())

    def show_graph_page(self):
        self.clear_content()
        self.page_header("Grafikler", "Son 7 güne ait haftalık soru çözme trendini görüntüle.")
        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=30, pady=16)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)
        chart_card = self.create_card(body, "Haftalık Soru Çözme Trendi")
        chart_card.grid(row=0, column=0, sticky="nsew")
        chart_card.grid_columnconfigure(0, weight=1)
        chart_card.grid_rowconfigure(1, weight=1)
        labels, values = self.data_manager.get_last_7_days_question_data()
        ctk.CTkLabel(chart_card, text=f"Son 7 gün toplam: {sum(values)} soru • Günlük ortalama: {round(sum(values)/7, 1)}", text_color="#9ca3af", font=("Segoe UI", 13, "bold"), anchor="w").grid(row=0, column=0, sticky="ew", padx=22, pady=(0, 8))
        figure = Figure(figsize=(8, 4.6), dpi=100)
        figure.patch.set_facecolor("#111827")
        ax = figure.add_subplot(111)
        ax.set_facecolor("#111827")
        ax.plot(labels, values, marker="o", linewidth=2.6)
        ax.fill_between(labels, values, alpha=0.15)
        ax.set_title("Son 7 Günlük Soru Sayısı", color="#f9fafb", fontsize=14, fontweight="bold", pad=14)
        ax.set_xlabel("Tarih", color="#d1d5db")
        ax.set_ylabel("Soru", color="#d1d5db")
        ax.tick_params(axis="x", colors="#d1d5db")
        ax.tick_params(axis="y", colors="#d1d5db")
        ax.grid(True, alpha=0.22)
        for spine in ax.spines.values():
            spine.set_color("#374151")
        ax.set_ylim(0, max(values) + max(10, int(max(values) * 0.2)) if max(values) else 10)
        figure.tight_layout()
        canvas_frame = ctk.CTkFrame(chart_card, fg_color="#111827")
        canvas_frame.grid(row=1, column=0, sticky="nsew", padx=22, pady=(4, 22))
        canvas = FigureCanvasTkAgg(figure, master=canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_exam_calendar_page(self):
        self.clear_content()
        self.page_header("Deneme Takvimi", "Ayda bir çözdüğün denemelerin Sözel Net ve Sayısal Net sonuçlarını kaydet.")
        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=30, pady=16)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)
        form_card = self.create_card(body, "Yeni Deneme Kaydı")
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        form = ctk.CTkFrame(form_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=22, pady=18)
        self.exam_month_entry = self.form_entry(form, "Ay", datetime.now().strftime("%Y-%m"), "Örn: 2026-05")
        self.verbal_net_entry = self.form_entry(form, "Sözel Net", "", "Örn: 42.50")
        self.numerical_net_entry = self.form_entry(form, "Sayısal Net", "", "Örn: 28.75")
        ctk.CTkButton(form, text="Denemeyi Kaydet", height=48, corner_radius=16, fg_color="#2563eb", hover_color="#1d4ed8", font=("Segoe UI", 15, "bold"), command=self.save_exam_record).pack(fill="x", pady=(4, 14))
        table_card = self.create_card(body, "Deneme Net Tablosu")
        table_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        self.render_exam_table(table_card)

    def form_entry(self, master, label, value, placeholder):
        ctk.CTkLabel(master, text=label, text_color="#d1d5db", font=("Segoe UI", 13, "bold"), anchor="w").pack(fill="x", pady=(0, 6))
        entry = ctk.CTkEntry(master, height=44, corner_radius=14, placeholder_text=placeholder)
        entry.pack(fill="x", pady=(0, 16))
        if value:
            entry.insert(0, value)
        return entry

    def render_exam_table(self, parent):
        header = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=14)
        header.pack(fill="x", padx=22, pady=(8, 8))
        for index, text in enumerate(["Ay", "Sözel", "Sayısal", "Toplam", "Sil"]):
            header.grid_columnconfigure(index, weight=1)
            ctk.CTkLabel(header, text=text, text_color="#93c5fd", font=("Segoe UI", 12, "bold")).grid(row=0, column=index, padx=8, pady=10, sticky="ew")
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=22, pady=(0, 22))
        records = self.data_manager.data.get("deneme_kayitlari", [])
        if not records:
            ctk.CTkLabel(scroll, text="Henüz deneme kaydı yok.", text_color="#9ca3af", font=("Segoe UI", 14)).pack(pady=22)
            return
        for index, record in enumerate(records):
            row = ctk.CTkFrame(scroll, fg_color="#0f172a", corner_radius=14)
            row.pack(fill="x", pady=6)
            values = [record.get("ay", "-"), f"{record.get('sozel_net', 0):.2f}", f"{record.get('sayisal_net', 0):.2f}", f"{record.get('toplam_net', 0):.2f}"]
            for column, value in enumerate(values):
                row.grid_columnconfigure(column, weight=1)
                ctk.CTkLabel(row, text=value, text_color="#e5e7eb", font=("Segoe UI", 12, "bold")).grid(row=0, column=column, padx=8, pady=10, sticky="ew")
            row.grid_columnconfigure(4, weight=1)
            ctk.CTkButton(row, text="Sil", width=54, height=30, corner_radius=10, fg_color="#7f1d1d", hover_color="#991b1b", command=lambda i=index: self.delete_exam_record(i)).grid(row=0, column=4, padx=8, pady=8)

    def save_exam_record(self):
        month = self.exam_month_entry.get().strip()
        verbal_net = self.verbal_net_entry.get().strip().replace(",", ".")
        numerical_net = self.numerical_net_entry.get().strip().replace(",", ".")
        try:
            datetime.strptime(month, "%Y-%m")
            verbal_net = float(verbal_net)
            numerical_net = float(numerical_net)
            if verbal_net < 0 or numerical_net < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Hatalı Giriş", "Ay formatı YYYY-AA olmalı. Netler 0 veya pozitif sayı olmalı.")
            return
        self.data_manager.add_exam_record(month, verbal_net, numerical_net)
        messagebox.showinfo("Kaydedildi", "Deneme kaydın kaydedildi.")
        self.show_exam_calendar_page()

    def delete_exam_record(self, index):
        if messagebox.askyesno("Kaydı Sil", "Bu deneme kaydını silmek istediğine emin misin?"):
            self.data_manager.delete_exam_record(index)
            self.show_exam_calendar_page()

    def show_goals_page(self):
        self.clear_content()
        self.page_header("Hedef & Streak", "Günlük ve haftalık hedeflerini belirle, çalışma serini takip et.")
        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=30, pady=16)
        body.grid_columnconfigure((0, 1), weight=1)
        goals = self.data_manager.data["hedefler"]
        today_record = self.data_manager.get_today_record()
        week_q, week_m = self.data_manager.get_week_totals()
        left = self.create_card(body, "Hedefleri Düzenle")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        form = ctk.CTkFrame(left, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=22, pady=18)
        self.daily_q_goal = self.form_entry(form, "Günlük soru hedefi", str(goals["gunluk_soru"]), "120")
        self.daily_m_goal = self.form_entry(form, "Günlük dakika hedefi", str(goals["gunluk_dakika"]), "90")
        self.weekly_q_goal = self.form_entry(form, "Haftalık soru hedefi", str(goals["haftalik_soru"]), "750")
        self.weekly_m_goal = self.form_entry(form, "Haftalık dakika hedefi", str(goals["haftalik_dakika"]), "540")
        ctk.CTkButton(form, text="Hedefleri Kaydet", height=48, corner_radius=16, fg_color="#2563eb", hover_color="#1d4ed8", font=("Segoe UI", 15, "bold"), command=self.save_goals).pack(fill="x", pady=10)
        right = self.create_card(body, "İlerleme")
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        ctk.CTkLabel(right, text=f"🔥 Mevcut seri: {self.data_manager.get_streak()} gün", text_color="#fbbf24", font=("Segoe UI", 24, "bold")).pack(pady=(20, 8))
        self.add_progress(right, "Bugünkü soru", today_record.get("soru", 0), goals["gunluk_soru"])
        self.add_progress(right, "Bugünkü dakika", today_record.get("dakika", 0), goals["gunluk_dakika"])
        self.add_progress(right, "Bu hafta soru", week_q, goals["haftalik_soru"])
        self.add_progress(right, "Bu hafta dakika", week_m, goals["haftalik_dakika"])

    def save_goals(self):
        try:
            values = [int(self.daily_q_goal.get()), int(self.daily_m_goal.get()), int(self.weekly_q_goal.get()), int(self.weekly_m_goal.get())]
            if any(v <= 0 for v in values):
                raise ValueError
        except ValueError:
            messagebox.showerror("Hatalı Giriş", "Tüm hedeflere pozitif tam sayı girmelisin.")
            return
        self.data_manager.save_goals(*values)
        messagebox.showinfo("Kaydedildi", "Hedeflerin kaydedildi.")
        self.show_goals_page()

    def show_pomodoro_page(self):
        self.clear_content()
        self.page_header("Pomodoro", "25 dakika odaklan, 5 dakika mola ver. Bitince günlük pomodoro sayın artar.")
        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=30, pady=16)
        body.grid_columnconfigure(0, weight=1)
        card = self.create_card(body, "Odak Zamanlayıcı")
        card.grid(row=0, column=0, sticky="nsew")
        self.pomodoro_label = ctk.CTkLabel(card, text=self.format_time(self.pomodoro_seconds), text_color="#f9fafb", font=("Segoe UI", 64, "bold"))
        self.pomodoro_label.pack(pady=(40, 16))
        self.pomodoro_info = ctk.CTkLabel(card, text=f"Bugün tamamlanan pomodoro: {self.data_manager.data['pomodoro']['bugun_tamamlanan']}", text_color="#fbbf24", font=("Segoe UI", 17, "bold"))
        self.pomodoro_info.pack(pady=(0, 20))
        controls = ctk.CTkFrame(card, fg_color="transparent")
        controls.pack(pady=12)
        ctk.CTkButton(controls, text="Başlat", width=120, height=44, corner_radius=14, command=self.start_pomodoro).grid(row=0, column=0, padx=8)
        ctk.CTkButton(controls, text="Duraklat", width=120, height=44, corner_radius=14, fg_color="#475569", hover_color="#334155", command=self.pause_pomodoro).grid(row=0, column=1, padx=8)
        ctk.CTkButton(controls, text="Sıfırla", width=120, height=44, corner_radius=14, fg_color="#7f1d1d", hover_color="#991b1b", command=self.reset_pomodoro).grid(row=0, column=2, padx=8)

    def format_time(self, seconds):
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def start_pomodoro(self):
        if not self.pomodoro_running:
            self.pomodoro_running = True
            self.tick_pomodoro()

    def pause_pomodoro(self):
        self.pomodoro_running = False

    def reset_pomodoro(self):
        self.pomodoro_running = False
        self.pomodoro_seconds = 25 * 60
        if hasattr(self, "pomodoro_label"):
            self.pomodoro_label.configure(text=self.format_time(self.pomodoro_seconds))

    def tick_pomodoro(self):
        if not self.pomodoro_running:
            return
        if self.pomodoro_seconds <= 0:
            self.pomodoro_running = False
            self.data_manager.increment_pomodoro()
            messagebox.showinfo("Pomodoro Bitti", "Harika! 1 pomodoro tamamlandı. Şimdi 5 dakika mola iyi gider.")
            self.pomodoro_seconds = 25 * 60
            self.show_pomodoro_page()
            return
        self.pomodoro_seconds -= 1
        if hasattr(self, "pomodoro_label"):
            self.pomodoro_label.configure(text=self.format_time(self.pomodoro_seconds))
        self.pomodoro_after_id = self.after(1000, self.tick_pomodoro)

    def show_topic_analysis_page(self):
        self.clear_content()
        self.page_header("Konu Bazlı Analiz", "Hangi konudan kaç soru çözdüğünü ayrı ayrı takip et.")
        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=30, pady=16)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=2)
        form_card = self.create_card(body, "Konuya Soru Ekle")
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        form = ctk.CTkFrame(form_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=22, pady=18)
        self.topic_lesson_var = ctk.StringVar(value="Matematik")
        ctk.CTkLabel(form, text="Ders", text_color="#d1d5db", font=("Segoe UI", 13, "bold"), anchor="w").pack(fill="x", pady=(0, 6))
        lesson_menu = ctk.CTkOptionMenu(form, values=list(self.data_manager.data["konular"].keys()), variable=self.topic_lesson_var, command=lambda _: self.refresh_topic_menu())
        lesson_menu.pack(fill="x", pady=(0, 16))
        self.topic_var = ctk.StringVar(value=list(self.data_manager.data["konular"]["Matematik"].keys())[0])
        ctk.CTkLabel(form, text="Konu", text_color="#d1d5db", font=("Segoe UI", 13, "bold"), anchor="w").pack(fill="x", pady=(0, 6))
        self.topic_menu = ctk.CTkOptionMenu(form, values=list(self.data_manager.data["konular"]["Matematik"].keys()), variable=self.topic_var)
        self.topic_menu.pack(fill="x", pady=(0, 16))
        self.topic_question_entry = self.form_entry(form, "Soru sayısı", "", "Örn: 40")
        ctk.CTkButton(form, text="Konu Kaydını Ekle", height=48, corner_radius=16, command=self.save_topic_question_record).pack(fill="x", pady=10)
        table_card = self.create_card(body, "En Çok Soru Çözülen Konular")
        table_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        scroll = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=22, pady=18)
        totals = self.data_manager.get_topic_question_totals()
        if not totals:
            ctk.CTkLabel(scroll, text="Henüz konu bazlı soru kaydı yok.", text_color="#9ca3af", font=("Segoe UI", 14)).pack(pady=22)
        for topic, count in totals.items():
            row = ctk.CTkFrame(scroll, fg_color="#0f172a", corner_radius=14)
            row.pack(fill="x", pady=6)
            ctk.CTkLabel(row, text=topic, text_color="#e5e7eb", font=("Segoe UI", 12, "bold"), anchor="w").pack(side="left", padx=14, pady=10, fill="x", expand=True)
            ctk.CTkLabel(row, text=f"{count} soru", text_color="#93c5fd", font=("Segoe UI", 12, "bold")).pack(side="right", padx=14, pady=10)

    def refresh_topic_menu(self):
        lesson = self.topic_lesson_var.get()
        topics = list(self.data_manager.data["konular"][lesson].keys())
        self.topic_var.set(topics[0])
        self.topic_menu.configure(values=topics)

    def save_topic_question_record(self):
        try:
            count = int(self.topic_question_entry.get().strip())
            if count <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Hatalı Giriş", "Soru sayısına pozitif tam sayı girmelisin.")
            return
        self.data_manager.add_topic_question_record(self.topic_lesson_var.get(), self.topic_var.get(), count)
        messagebox.showinfo("Kaydedildi", "Konu bazlı soru kaydı eklendi.")
        self.show_topic_analysis_page()

    def show_calendar_page(self):
        self.clear_content()
        self.page_header("Çalışma Takvimi", "Bu ay hangi gün ne kadar çalıştığını renk yoğunluğuyla gör.")
        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=30, pady=16)
        card = self.create_card(body, datetime.now().strftime("%Y-%m Çalışma Haritası"))
        card.pack(fill="both", expand=True)
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(padx=22, pady=22, fill="both", expand=True)
        days = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
        for c, day_name in enumerate(days):
            ctk.CTkLabel(grid, text=day_name, text_color="#93c5fd", font=("Segoe UI", 13, "bold")).grid(row=0, column=c, padx=6, pady=6, sticky="ew")
        today = date.today()
        month_matrix = calendar.monthcalendar(today.year, today.month)
        for r, week in enumerate(month_matrix, start=1):
            for c, day_num in enumerate(week):
                if day_num == 0:
                    cell = ctk.CTkFrame(grid, fg_color="transparent", width=92, height=72)
                    cell.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
                    continue
                key = date(today.year, today.month, day_num).isoformat()
                item = self.data_manager.data["gunluk_kayitlar"].get(key, {})
                minutes = item.get("dakika", 0)
                questions = item.get("soru", 0)
                color = "#1f2937"
                if minutes > 0 or questions > 0:
                    color = "#1e3a8a"
                if minutes >= 60 or questions >= 80:
                    color = "#166534"
                if minutes >= 120 or questions >= 160:
                    color = "#b45309"
                cell = ctk.CTkFrame(grid, fg_color=color, corner_radius=16, width=92, height=72)
                cell.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
                cell.grid_propagate(False)
                ctk.CTkLabel(cell, text=str(day_num), text_color="#f9fafb", font=("Segoe UI", 15, "bold")).pack(pady=(10, 0))
                ctk.CTkLabel(cell, text=f"{questions}s / {minutes}dk", text_color="#d1d5db", font=("Segoe UI", 10, "bold")).pack()
        legend = ctk.CTkLabel(card, text="Gri: kayıt yok • Mavi: az • Yeşil: iyi • Turuncu: yoğun çalışma", text_color="#9ca3af", font=("Segoe UI", 12, "bold"))
        legend.pack(pady=(0, 18))

    def show_stats_page(self):
        self.clear_content()
        self.page_header("Özet", "Kaydettiğin günlük çalışmaların, denemelerin ve müfredat durumun.")
        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=30, pady=16)
        body.grid_columnconfigure((0, 1, 2, 3), weight=1)
        records = self.data_manager.data.get("gunluk_kayitlar", {})
        exam_records = self.data_manager.data.get("deneme_kayitlari", [])
        total_questions = sum(item.get("soru", 0) for item in records.values())
        total_minutes = sum(item.get("dakika", 0) for item in records.values())
        completed, total, percent = self.data_manager.get_topic_stats()
        last_exam_net = exam_records[-1].get("toplam_net", 0) if exam_records else 0
        self.stat_card(body, "Toplam Soru", str(total_questions), "🧠", 0)
        self.stat_card(body, "Toplam Dakika", str(total_minutes), "⏱", 1)
        self.stat_card(body, "Müfredat", f"%{percent}", "✅", 2)
        self.stat_card(body, "Son Deneme Neti", f"{last_exam_net:.2f}", "🗓", 3)
        history_card = self.create_card(body, "Son Çalışma Kayıtları")
        history_card.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(24, 0))
        if not records:
            ctk.CTkLabel(history_card, text="Henüz günlük kayıt yok.", text_color="#9ca3af", font=("Segoe UI", 14)).pack(padx=22, pady=24)
            return
        for day, item in sorted(records.items(), reverse=True)[:10]:
            row = ctk.CTkFrame(history_card, fg_color="#0f172a", corner_radius=14)
            row.pack(fill="x", padx=22, pady=6)
            text = f"{day} • {item.get('soru', 0)} soru • {item.get('dakika', 0)} dakika"
            ctk.CTkLabel(row, text=text, text_color="#e5e7eb", font=("Segoe UI", 13, "bold"), anchor="w").pack(fill="x", padx=16, pady=12)


if __name__ == "__main__":
    app = DGSTrackerApp()
    app.mainloop()
