import tkinter as tk
from tkinter import messagebox, ttk
import urllib.request
import urllib.error
import json
import os

# Конфигурация
FAVORITES_FILE = "favorites.json"
GITHUB_API_URL = "https://api.github.com/users/"

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("600x500")

        # Загрузка избранных пользователей
        self.favorites = self.load_favorites()

        self.setup_ui()

    def setup_ui(self):
        # Поле ввода
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(input_frame, text="Поиск пользователя GitHub:").pack(side="left")

        self.search_entry = tk.Entry(input_frame, width=40)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda event: self.search_user())

        search_btn = tk.Button(input_frame, text="Найти", command=self.search_user)
        search_btn.pack(side="left")

        # Список результатов
        results_frame = tk.LabelFrame(self.root, text="Результаты поиска", padx=10, pady=10)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("login", "name", "location", "public_repos")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=120)

        self.tree.pack(fill="both", expand=True)

        # Кнопки управления
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        add_fave_btn = tk.Button(button_frame, text="Добавить в избранное",
                               command=self.add_to_favorites)
        add_fave_btn.pack(side="left", padx=5)

        show_fave_btn = tk.Button(button_frame, text="Показать избранное",
                                command=self.show_favorites)
        show_fave_btn.pack(side="left", padx=5)

    def search_user(self):
        username = self.search_entry.get().strip()
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым!")
            return

        try:
            url = f"{GITHUB_API_URL}{username}"
            req = urllib.request.Request(url)

            with urllib.request.urlopen(req) as response:
                data = response.read().decode('utf-8')
                user_data = json.loads(data)
                self.display_user(user_data)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                messagebox.showerror("Ошибка", f"Пользователь '{username}' не найден!")
            else:
                messagebox.showerror("Ошибка HTTP", f"HTTP {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            messagebox.showerror("Ошибка сети", f"Не удалось подключиться к GitHub API: {e.reason}")
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Не удалось обработать ответ от сервера")

    def display_user(self, user_data):
        # Очищаем предыдущие результаты
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Добавляем найденного пользователя
        self.tree.insert("", "end", values=(
            user_data.get("login", "N/A"),
            user_data.get("name", "N/A"),
            user_data.get("location", "N/A"),
            user_data.get("public_repos", 0)
        ))

    def add_to_favorites(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из списка!")
            return

        user_data = self.tree.item(selected[0])["values"]
        login = user_data[0]

        if login not in self.favorites:
            self.favorites[login] = {
                "name": user_data[1],
                "location": user_data[2],
                "public_repos": user_data[3]
            }
            self.save_favorites()
            messagebox.showinfo("Успех", f"{login} добавлен в избранное!")
        else:
            messagebox.showinfo("Информация", f"{login} уже в избранном!")

    def show_favorites(self):
        # Очищаем результаты
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Отображаем избранное
        for login, data in self.favorites.items():
            self.tree.insert("", "end", values=(
                login,
                data["name"],
                data["location"],
                data["public_repos"]
            ))

    def load_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            try:
                with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save_favorites(self):
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
