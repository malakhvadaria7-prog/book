import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import json
import os

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("600x500")

        # Загрузка данных
        self.tasks_data = self.load_data()
        self.history = self.tasks_data.get("history", [])

        self.setup_ui()

    def setup_ui(self):
        # Заголовок
        ttk.Label(self.root, text="Генератор случайных задач", font=("Arial", 16)).pack(pady=10)

        # Кнопка генерации задачи
        self.generate_btn = ttk.Button(self.root, text="Сгенерировать задачу", command=self.generate_task)
        self.generate_btn.pack(pady=5)

        # Поле отображения текущей задачи
        ttk.Label(self.root, text="Текущая задача:").pack(pady=(10, 5))
        self.current_task_label = ttk.Label(self.root, text="Нажмите кнопку для генерации", wraplength=500)
        self.current_task_label.pack(pady=5)

        # Фильтр по типу
        ttk.Label(self.root, text="Фильтр по типу:").pack(pady=(15, 5))
        self.filter_var = tk.StringVar(value="Все")
        filter_options = ["Все", "Учёба", "Спорт", "Работа"]
        self.filter_combo = ttk.Combobox(self.root, textvariable=self.filter_var, values=filter_options, state="readonly")
        self.filter_combo.pack(pady=5)
        self.filter_combo.bind("<<ComboboxSelected>>", self.apply_filter)

        # Список истории
        ttk.Label(self.root, text="История задач:").pack(pady=(15, 5))

        # Фрейм для списка и скроллбара
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.history_listbox = tk.Listbox(list_frame, height=10, width=60)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=scrollbar.set)

        self.history_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
 # Чекбоксы типов символов
        ttk.Label(self.root, text="Типы символов:").pack(pady=(15, 5))

        checkbox_frame = ttk.Frame(self.root)
        checkbox_frame.pack(pady=5)

        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.special_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(checkbox_frame, text="Заглавные буквы (A‑Z)", variable=self.uppercase_var).pack(anchor=tk.W)
        ttk.Checkbutton(checkbox_frame, text="Строчные буквы (a‑z)", variable=self.lowercase_var).pack(anchor=tk.W)
        ttk.Checkbutton(checkbox_frame, text="Цифры (0‑9)", variable=self.digits_var).pack(anchor=tk.W)
        ttk.Checkbutton(checkbox_frame, text="Специальные символы (!@#$%)", variable=self.special_var).pack(anchor=tk.W)
        # Кнопки управления
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Добавить задачу", command=self.add_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить историю", command=self.clear_history).pack(side=tk.LEFT, padx=5)

        # Обновление списка истории
        self.update_history_list()
 # Таблица истории
        ttk.Label(self.root, text="История паролей:").pack(pady=(15, 5))

        history_frame = ttk.Frame(self.root)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("Length", "Characters", "Password")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=8)

        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Копировать пароль", command=self.copy_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить историю", command=self.clear_history).pack(side=tk.LEFT, padx=5)

        self.update_history_table()

    def update_length_label(self, event=None):
        """Обновляет отображение длины пароля"""
        self.length_label.config(text=str(self.length_var.get()))

    def generate_password(self):
        """Генерирует пароль с валидацией"""
        try:
            # Проверка длины
            length = self.length_var.get()
            if length < 8 or length > 32:
                messagebox.showerror("Ошибка", "Длина пароля должна быть от 8 до 32 символов")
                return

            # Проверка выбора типов символов
            char_types = [
                self.uppercase_var.get(),
                self.lowercase_var.get(),
                self.digits_var.get(),
                self.special_var.get()
            ]
            if not any(char_types):
                messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов")
                return

            # Формирование набора символов
            chars = ""
            if self.uppercase_var.get():
                chars += string.ascii_uppercase
            if self.lowercase_var.get():
                chars += string.ascii_lowercase
            if self.digits_var.get():
                chars += string.digits
            if self.special_var.get():
                chars += "!@#$%^&*"

            if not chars:
                messagebox.showerror("Ошибка", "Не выбран ни один тип символов для генерации")
                return

            # Генерация пароля
            password = ''.join(secrets.choice(chars) for _ in range(length))

            # Отображение пароля
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, password)

            # Добавление в историю
            history_entry = {
                "length": length,
                "characters": self.get_char_types_description(),
                "password": password
            }
            self.history.append(history_entry)
            self.save_history()
            self.update_history_table()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при генерации пароля: {str(e)}")
    def get_char_types_description(self):
        """Возвращает описание выбранных типов символов"""
        types = []
        if self.uppercase_var.get():
            types.append("A‑Z")
        if self.lowercase_var.get():
            types.append("a‑z")
        if self.digits_var.get():
            types.append("0‑9")
        if self.special_var.get():
            types.append("!@#$%")
        return ", ".join(types)
    def copy_password(self):
        """Копирует текущий пароль в буфер обмена"""
        password = self.password_entry.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена")
        else:
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте пароль")
    def clear_history(self)
    def load_data(self):
        """Загружает данные из JSON-файла"""
        if os.path.exists("tasks.json"):
            try:
                with open("tasks.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except (IOError, json.JSONDecodeError):
                pass
        # Данные по умолчанию
        return {
            "tasks": {
                "Учёба": ["Прочитать статью", "Изучить главу книги", "Решить 5 задач по математике", "Подготовиться к экзамену"],
                "Спорт": ["Сделать зарядку", "Пробежать 3 км", "Позаниматься йогой 30 минут", "Отжаться 50 раз"],
                "Работа": ["Проверить почту", "Составить отчёт", "Провести совещание", "Ответить на запросы клиентов"]
            },
            "history": []
        }

    def save_data(self):
        """Сохраняет данные в JSON-файл"""
        with open("tasks.json", "w", encoding="utf-8") as f:
            json.dump(self.tasks_data, f, ensure_ascii=False, indent=2)

    def generate_task(self):
        """Генерирует случайную задачу"""
        filter_type = self.filter_var.get()
        available_tasks = []

        if filter_type == "Все":
            for task_list in self.tasks_data["tasks"].values():
                available_tasks.extend(task_list)
        else:
            available_tasks = self.tasks_data["tasks"].get(filter_type, [])

        if not available_tasks:
            messagebox.showwarning("Предупреждение", "Нет задач для выбранного типа")
            return

        selected_task = random.choice(available_tasks)
        task_type = self.get_task_type(selected_task)

        # Отображение задачи
        self.current_task_label.config(text=f"{selected_task} ({task_type})")

        # Добавление в историю
        self.history.append({
            "task": selected_task,
            "type": task_type
        })
        self.tasks_data["history"] = self.history
        self.save_data()
        self.update_history_list()

    def get_task_type(self, task):
        """Определяет тип задачи по её тексту"""
        for task_type, tasks in self.tasks_data["tasks"].items():
            if task in tasks:
                return task_type
        return "Другое"

    def add_task(self):
        """Добавляет новую задачу"""
        task_text = simpledialog.askstring("Новая задача", "Введите текст задачи:")
        if not task_text or not task_text.strip():
            messagebox.showerror("Ошибка", "Задача не может быть пустой")
            return

        task_type = simpledialog.askstring(
            "Тип задачи",
            "Выберите тип задачи (Учёба, Спорт, Работа):",
            initialvalue="Учёба"
        )
        if task_type not in ["Учёба", "Спорт", "Работа"]:
            messagebox.showerror("Ошибка", "Неверный тип задачи. Допустимые значения: Учёба, Спорт, Работа")
            return

        # Добавляем задачу в список
        if task_type not in self.tasks_data["tasks"]:
            self.tasks_data["tasks"][task_type] = []
        self.tasks_data["tasks"][task_type].append(task_text.strip())
        self.save_data()
        messagebox.showinfo("Успех", f"Задача '{task_text}' добавлена в категорию '{task_type}'!")

    def clear_history(self):
        """Очищает историю задач"""
        self.history = []
        self.tasks_data["history"] = []
        self.save_data()
        self.update_history_list()
        messagebox.showinfo("Успех", "История очищена!")

    def apply_filter(self, event=None):
        """Применяет фильтр к истории"""
        self.update_history_list()

    def update_history_list(self):
        """Обновляет отображение истории"""
        self.history_listbox.delete(0, tk.END)
        filter_type = self.filter_var.get()

        for record in reversed(self.history):
            if filter_type == "Все" or record["type"] == filter_type:
                self.history_listbox.insert(tk.END, f"{record['task']} ({record['type']})")

if __name__ == "__main__":
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()


---

## Обновления в коде (`main.py`)

В метод `add_task` добавлены проверки корректности типа задачи:

```python
def add_task(self):
    """Добавляет новую задачу"""
    task_text = simpledialog.askstring("Новая задача", "Введите текст задачи:")
    if not task_text or not task_text.strip():
        messagebox.showerror("Ошибка", "Задача не может быть пустой")
        return

    task_type = simpledialog.askstring(
        "Тип задачи",
        "Выберите тип задачи (Учёба, Спорт, Работа):",
        initialvalue="Учёба"
    )
    if task_type not in ["Учёба", "Спорт", "Работа"]:
        messagebox.showerror("Ошибка", "Неверный тип задачи. Допустимые значения: Учёба, Спорт, Работа")
        return

    # Добавляем задачу в список
    if task_type not in self.tasks_data["tasks"]:
        self.tasks_data["tasks"][task_type] = []
    self.tasks_data["tasks"][task_type].append(task_text.strip())
    self.save_data()
    messagebox.showinfo("Успех", f"Задача '{task_text}' добавлена в категорию '{task_type}'!")

# Стандартные библиотеки Python — не требуют установки
# tk
