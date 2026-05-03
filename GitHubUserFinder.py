import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import requests
from datetime import datetime
from PIL import Image, ImageTk
import io
import sys

# Определяем правильный путь для сохранения файлов
def get_data_file_path(filename):
    """Возвращает путь к файлу в папке пользователя или рядом с программой"""
    # Вариант 1: Папка документов пользователя (рекомендуется)
    docs_path = os.path.expanduser("~/Documents/GitHubUserFinder")
    
    # Вариант 2: Папка AppData (Windows)
    appdata_path = os.path.expanduser("~/AppData/Local/GitHubUserFinder")
    
    # Вариант 3: Папка с программой (если доступна для записи)
    program_path = os.path.dirname(os.path.abspath(__file__))
    
    # Проверяем, можно ли писать в папку с программой
    try:
        test_file = os.path.join(program_path, "test_write.tmp")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        # Если получилось - используем папку с программой
        save_dir = program_path
    except:
        # Если нет - используем папку Documents
        save_dir = docs_path
        # Создаём папку, если её нет
        os.makedirs(save_dir, exist_ok=True)
    
    return os.path.join(save_dir, filename)

DATA_FILE = get_data_file_path("favorites.json")

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("900x700")
        
        # Показываем, где сохраняются данные
        info_label = tk.Label(root, text=f"📁 Данные сохраняются в: {os.path.dirname(DATA_FILE)}", 
                              font=("Arial", 8), fg="gray")
        info_label.pack(pady=2)
        
        self.favorites = []
        self.load_favorites()
        
        # Поле поиска
        search_frame = tk.Frame(root)
        search_frame.pack(pady=10)
        
        tk.Label(search_frame, text="Введите имя пользователя GitHub:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_user())
        
        self.search_btn = tk.Button(search_frame, text="Поиск", command=self.search_user)
        self.search_btn.pack(side=tk.LEFT, padx=5)
        
        # Результаты поиска
        result_frame = tk.LabelFrame(root, text="Результаты поиска", padx=5, pady=5)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Таблица результатов
        columns = ("Аватар", "Логин", "Имя", "Репозитории", "Подписчики")
        self.result_tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=10)
        
        self.result_tree.heading("Аватар", text="Аватар")
        self.result_tree.heading("Логин", text="Логин")
        self.result_tree.heading("Имя", text="Имя")
        self.result_tree.heading("Репозитории", text="Репозитории")
        self.result_tree.heading("Подписчики", text="Подписчики")
        
        self.result_tree.column("Аватар", width=80)
        self.result_tree.column("Логин", width=150)
        self.result_tree.column("Имя", width=200)
        self.result_tree.column("Репозитории", width=100)
        self.result_tree.column("Подписчики", width=100)
        
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка добавления в избранное
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        
        self.add_fav_btn = tk.Button(btn_frame, text="★ Добавить в избранное", command=self.add_to_favorites)
        self.add_fav_btn.pack(side=tk.LEFT, padx=5)
        
        # Список избранного
        fav_frame = tk.LabelFrame(root, text="Избранные пользователи", padx=5, pady=5)
        fav_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns_fav = ("Логин", "Имя", "Репозитории", "Дата добавления")
        self.fav_tree = ttk.Treeview(fav_frame, columns=columns_fav, show="headings", height=6)
        
        for col in columns_fav:
            self.fav_tree.heading(col, text=col)
            self.fav_tree.column(col, width=150)
        
        scrollbar_fav = ttk.Scrollbar(fav_frame, orient=tk.VERTICAL, command=self.fav_tree.yview)
        self.fav_tree.configure(yscrollcommand=scrollbar_fav.set)
        
        self.fav_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_fav.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка удаления из избранного
        remove_btn = tk.Button(fav_frame, text="🗑 Удалить из избранного", command=self.remove_from_favorites)
        remove_btn.pack(pady=5)
        
        self.refresh_favorites()
        
        # Кэш для аватаров
        self.avatar_cache = {}
        self.current_user = None
    
    def load_favorites(self):
        """Загрузка избранных пользователей из JSON"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.favorites = json.load(f)
                    print(f"Загружено {len(self.favorites)} избранных пользователей")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка загрузки: {e}")
                self.favorites = []
        else:
            print(f"Файл {DATA_FILE} не найден, создаём новый")
            self.favorites = []
    
    def save_favorites(self):
        """Сохранение избранных пользователей в JSON"""
        try:
            # Убеждаемся, что директория существует
            os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
            
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=4)
            print(f"Сохранено {len(self.favorites)} пользователей в {DATA_FILE}")
            return True
        except PermissionError:
            messagebox.showerror("Ошибка", 
                               f"Нет прав на запись в файл:\n{DATA_FILE}\n\n"
                               f"Попробуйте:\n"
                               f"1. Закрыть файл favorites.json, если он открыт\n"
                               f"2. Запустить программу от имени администратора\n"
                               f"3. Проверить права на папку:\n{os.path.dirname(DATA_FILE)}")
            return False
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
            return False
    
    def search_user(self):
        """Поиск пользователя на GitHub"""
        username = self.search_entry.get().strip()
        
        if not username:
            messagebox.showerror("Ошибка", "Введите имя пользователя для поиска")
            return
        
        # Очистка таблицы результатов
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        try:
            # Запрос к GitHub API
            print(f"Поиск пользователя: {username}")
            response = requests.get(f"https://api.github.com/users/{username}", timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                self.display_user(user_data)
            elif response.status_code == 404:
                messagebox.showerror("Ошибка", f"Пользователь '{username}' не найден")
            else:
                messagebox.showerror("Ошибка", f"Ошибка API: {response.status_code}")
                
        except requests.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка соединения:\n{str(e)}\n\nПроверьте интернет-соединение")
    
    def display_user(self, user_data):
        """Отображение информации о пользователе"""
        login = user_data.get("login", "N/A")
        name = user_data.get("name", "N/A")
        if name == "None" or not name:
            name = "—"
        repos = user_data.get("public_repos", 0)
        followers = user_data.get("followers", 0)
        avatar_url = user_data.get("avatar_url", "")
        
        # Сохранение данных пользователя для последующего использования
        self.current_user = {
            "login": login,
            "name": name,
            "public_repos": repos,
            "followers": followers,
            "avatar_url": avatar_url
        }
        
        # Добавление в таблицу
        self.result_tree.insert("", tk.END, values=("🖼", login, name, repos, followers))
        
        # Асинхронная загрузка аватара (опционально)
        if avatar_url:
            self.root.after(100, lambda: self.load_avatar_async(login, avatar_url))
    
    def load_avatar_async(self, login, url):
        """Асинхронная загрузка аватара"""
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                img_data = response.content
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((30, 30), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.avatar_cache[login] = photo
                
                # Обновляем аватар в таблице
                for item in self.result_tree.get_children():
                    if self.result_tree.item(item)['values'][1] == login:
                        self.result_tree.set(item, "Аватар", "●")
                        # Сохраняем фото для отображения (сложно в treeview, поэтому просто ставим символ)
                        break
        except:
            pass
    
    def add_to_favorites(self):
        """Добавление пользователя в избранное"""
        if not self.current_user:
            messagebox.showwarning("Предупреждение", "Сначала найдите пользователя")
            return
        
        # Проверка, не добавлен ли уже пользователь
        if any(fav["login"] == self.current_user["login"] for fav in self.favorites):
            messagebox.showinfo("Информация", f"Пользователь {self.current_user['login']} уже в избранном")
            return
        
        # Добавление в избранное
        fav_entry = {
            "login": self.current_user["login"],
            "name": self.current_user["name"],
            "public_repos": self.current_user["public_repos"],
            "followers": self.current_user["followers"],
            "avatar_url": self.current_user["avatar_url"],
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.favorites.append(fav_entry)
        if self.save_favorites():
            self.refresh_favorites()
            messagebox.showinfo("Успех", f"Пользователь {self.current_user['login']} добавлен в избранное")
    
    def remove_from_favorites(self):
        """Удаление пользователя из избранного"""
        selection = self.fav_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления")
            return
        
        # Получение логина выбранного пользователя
        item = self.fav_tree.item(selection[0])
        login = item['values'][0]
        
        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", f"Удалить пользователя {login} из избранного?"):
            # Удаление из списка
            self.favorites = [fav for fav in self.favorites if fav["login"] != login]
            if self.save_favorites():
                self.refresh_favorites()
                messagebox.showinfo("Успех", f"Пользователь {login} удалён из избранного")
    
    def refresh_favorites(self):
        """Обновление списка избранного"""
        # Очистка таблицы
        for item in self.fav_tree.get_children():
            self.fav_tree.delete(item)
        
        # Добавление пользователей
        for fav in self.favorites:
            self.fav_tree.insert("", tk.END, values=(
                fav["login"],
                fav["name"] if fav["name"] != "None" else "—",
                fav["public_repos"],
                fav.get("date_added", "N/A")
            ))


if __name__ == "__main__":
    # Проверка установки необходимых библиотек
    try:
        import requests
        from PIL import Image, ImageTk
        print("Библиотеки успешно загружены")
    except ImportError as e:
        print(f"Ошибка: Установите необходимые библиотеки:")
        print("pip install requests pillow")
        print(f"Детали: {e}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    
    # Создание и запуск приложения
    root = tk.Tk()
    app = GitHubUserFinder(root)
    
    # Вывод информации о файле данных
    print(f"\n✅ Программа запущена")
    print(f"📁 Файл избранного: {DATA_FILE}")
    print(f"📁 Папка: {os.path.dirname(DATA_FILE)}")
    
    root.mainloop()