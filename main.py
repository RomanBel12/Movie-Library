import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

DATA_FILE = "movies.json"

# ---------- Работа с JSON (с обработкой ошибок) ----------
def load_movies():
    """Загружает список фильмов из JSON-файла. В случае ошибки возвращает пустой список."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                else:
                    return []
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_movies(movies):
    """Сохраняет список фильмов в JSON-файл. При ошибке выводит сообщение."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(movies, f, ensure_ascii=False, indent=4)
    except IOError:
        messagebox.showerror("Ошибка", "Не удалось сохранить данные.")

# ---------- Основной класс приложения ----------
class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        self.movies = load_movies()          # все фильмы
        self.filtered_movies = self.movies.copy()  # отображаемые с учётом фильтра

        self.build_ui()
        self.refresh_table()

    def build_ui(self):
        # ----- Панель добавления -----
        input_frame = tk.LabelFrame(self.root, text="Добавить фильм", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_title = tk.Entry(input_frame, width=25)
        self.entry_title.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Жанр:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.entry_genre = tk.Entry(input_frame, width=15)
        self.entry_genre.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="Год:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_year = tk.Entry(input_frame, width=10)
        self.entry_year.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Рейтинг (0–10):").grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.entry_rating = tk.Entry(input_frame, width=10)
        self.entry_rating.grid(row=1, column=3, padx=5, pady=5)

        btn_add = tk.Button(input_frame, text="Добавить фильм", command=self.add_movie,
                            bg="#4CAF50", fg="white")
        btn_add.grid(row=2, column=0, columnspan=4, pady=10)

        # ----- Панель фильтрации -----
        filter_frame = tk.LabelFrame(self.root, text="Фильтр", padx=10, pady=10)
        filter_frame.pack(pady=5, padx=10, fill="x")

        tk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, sticky="e", padx=5)
        self.filter_genre = tk.Entry(filter_frame, width=15)
        self.filter_genre.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Год:").grid(row=0, column=2, sticky="e", padx=5)
        self.filter_year = tk.Entry(filter_frame, width=10)
        self.filter_year.grid(row=0, column=3, padx=5)

        btn_filter = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        btn_filter.grid(row=0, column=4, padx=5)

        btn_reset = tk.Button(filter_frame, text="Сбросить", command=self.reset_filter)
        btn_reset.grid(row=0, column=5, padx=5)

        # ----- Таблица -----
        table_frame = tk.Frame(self.root)
        table_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        columns = ("Название", "Жанр", "Год", "Рейтинг")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ----- Кнопка удаления -----
        btn_delete = tk.Button(self.root, text="Удалить выбранный", command=self.delete_movie,
                               bg="#f44336", fg="white")
        btn_delete.pack(pady=5)

    # ---------- Добавление фильма ----------
    def add_movie(self):
        title = self.entry_title.get().strip()
        genre = self.entry_genre.get().strip()
        year_str = self.entry_year.get().strip()
        rating_str = self.entry_rating.get().strip()

        if not title:
            messagebox.showerror("Ошибка", "Название не может быть пустым.")
            return

        if not genre:
            genre = "Не указан"

        # Валидация года
        try:
            year = int(year_str) if year_str else None
            if year is not None and year < 1800:
                messagebox.showerror("Ошибка", "Год должен быть не менее 1800.")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть целым числом.")
            return

        # Валидация рейтинга
        try:
            rating = float(rating_str) if rating_str else None
            if rating is not None and (rating < 0 or rating > 10):
                messagebox.showerror("Ошибка", "Рейтинг должен быть от 0 до 10.")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом.")
            return

        movie = {"title": title, "genre": genre, "year": year, "rating": rating}
        self.movies.append(movie)
        save_movies(self.movies)
        self.clear_inputs()
        self.refresh_table()

    def clear_inputs(self):
        self.entry_title.delete(0, tk.END)
        self.entry_genre.delete(0, tk.END)
        self.entry_year.delete(0, tk.END)
        self.entry_rating.delete(0, tk.END)

    # ---------- Удаление ----------
    def delete_movie(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите фильм для удаления.")
            return

        item = selected[0]
        values = self.tree.item(item, "values")
        title, genre, year_str, rating_str = values
        year = int(year_str) if year_str else None
        rating = float(rating_str) if rating_str else None

        for idx, mov in enumerate(self.movies):
            if (mov["title"] == title and mov["genre"] == genre and
                mov["year"] == year and mov["rating"] == rating):
                del self.movies[idx]
                break
        save_movies(self.movies)
        self.refresh_table()

    # ---------- Фильтрация ----------
    def apply_filter(self):
        genre_filter = self.filter_genre.get().strip().lower()
        year_filter_str = self.filter_year.get().strip()
        year_filter = int(year_filter_str) if year_filter_str else None

        self.filtered_movies = []
        for movie in self.movies:
            match_genre = True
            match_year = True
            if genre_filter:
                match_genre = genre_filter in movie["genre"].lower()
            if year_filter is not None:
                match_year = (movie["year"] == year_filter)
            if match_genre and match_year:
                self.filtered_movies.append(movie)

        self.display_table(self.filtered_movies)

    def reset_filter(self):
        self.filter_genre.delete(0, tk.END)
        self.filter_year.delete(0, tk.END)
        self.filtered_movies = self.movies.copy()
        self.display_table(self.filtered_movies)

    # ---------- Обновление таблицы ----------
    def refresh_table(self):
        self.filtered_movies = self.movies.copy()
        self.display_table(self.filtered_movies)

    def display_table(self, movies_list):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for movie in movies_list:
            year_str = str(movie["year"]) if movie["year"] is not None else ""
            rating_str = str(movie["rating"]) if movie["rating"] is not None else ""
            self.tree.insert("", tk.END, values=(movie["title"], movie["genre"], year_str, rating_str))

# ---------- Запуск ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()
