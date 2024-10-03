import subprocess
import toml
import os


def get_commits_before_date(repo_path, before_date):
    """
    Получает коммиты из указанного репозитория до заданной даты.
    Возвращает список словарей, содержащих хэш коммита, родителей и сообщение.
    """
    git_command = [
        "git", "-C", repo_path, "log", "--pretty=format:%H|%P|%s", f"--before={before_date}"
    ]
    result = subprocess.run(git_command, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Не удалось получить git log: {result.stderr}")

    commits = result.stdout.strip().split("\n")
    commit_data = []
    for commit in commits:
        if not commit:  # Пропустить пустые строки
            continue
        parts = commit.split("|", 2)
        hash = parts[0]
        parents = parts[1].split() if parts[1] else []
        message = parts[2]
        commit_data.append({"hash": hash, "parents": parents, "message": message})

    return commit_data


def generate_plantuml(commit_data):
    """
    Генерирует текстовое представление графа в формате PlantUML
    для визуализации коммитов и их зависимостей.
    """
    uml = "@startuml\n"
    for commit in commit_data:
        # Создаем узел для каждого коммита с его сообщением
        uml += f"({commit['hash']}) : {commit['message']}\n"
        # Добавляем зависимости от родительских коммитов
        for parent in commit['parents']:
            uml += f"({commit['hash']}) --> ({parent})\n"
    uml += "@enduml"
    return uml


def save_uml_to_file(uml_content, filename="graph.puml"):
    """
    Сохраняет сгенерированный текст PlantUML в файл.
    """
    with open(filename, "w") as f:
        f.write(uml_content)


def visualize_uml(plantuml_jar_path, uml_file="graph.puml"):
    """
    Запускает визуализацию PlantUML с использованием программы,
    путь к которой передается через параметр plantuml_jar_path.
    """
    if not os.path.exists(plantuml_jar_path):
        raise FileNotFoundError(f"PlantUML не найден по пути: {plantuml_jar_path}")

    subprocess.run(["java", "-jar", plantuml_jar_path, uml_file], check=True)


def load_config(config_file="config.toml"):
    """
    Загружает конфигурационный файл в формате TOML и возвращает его содержимое.
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Конфигурационный файл {config_file} не найден.")

    return toml.load(config_file)


def main():
    # Загрузка конфигурации из файла
    config = load_config("config.toml")

    # Получение параметров из конфигурации
    repo_path = config["settings"]["repository_path"]
    before_date = config["settings"]["before_date"]
    visualization_tool_path = config["settings"]["visualization_tool_path"]

    # Проверка наличия репозитория
    if not os.path.exists(repo_path):
        raise FileNotFoundError(f"Репозиторий не найден по пути: {repo_path}")

    # Получение данных о коммитах до заданной даты
    print(f"Получение коммитов до {before_date} из репозитория {repo_path}...")
    commit_data = get_commits_before_date(repo_path, before_date)

    if not commit_data:
        print(f"Коммитов до {before_date} не найдено.")
        return

    # Генерация PlantUML диаграммы
    print("Генерация PlantUML диаграммы...")
    uml_content = generate_plantuml(commit_data)

    # Сохранение диаграммы в файл
    print("Сохранение диаграммы в файл...")
    save_uml_to_file(uml_content)

    # Визуализация графа
    print("Визуализация графа...")
    visualize_uml(visualization_tool_path)

    print("Готово! Граф визуализирован.")


if __name__ == "__main__":
    main()
