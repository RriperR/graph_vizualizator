import unittest
from unittest.mock import patch, MagicMock
from main import get_commits_before_date, generate_plantuml, sanitize_message


class TestGitParser(unittest.TestCase):
    @patch('subprocess.run')
    def test_get_commits_before_date(self, mock_run):
        #Тест для функции get_commits_before_date, проверяющий корректность парсинга коммитов.
        # Имитация успешного вывода команды git log
        mock_run.return_value = MagicMock(stdout="123abc|456def|Initial commit\n789ghi||Second commit", returncode=0)

        # Проверка, что функция возвращает правильные данные
        repo_path = "/mock/repo"
        before_date = "2023-12-31"
        commits = get_commits_before_date(repo_path, before_date)

        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0]['hash'], "123abc")
        self.assertEqual(commits[0]['parents'], ["456def"])
        self.assertEqual(commits[0]['message'], "Initial commit")
        self.assertEqual(commits[1]['hash'], "789ghi")
        self.assertEqual(commits[1]['parents'], [])
        self.assertEqual(commits[1]['message'], "Second commit")


class TestGraphGenerator(unittest.TestCase):
    def test_sanitize_message(self):
        #Тест для функции sanitize_message, проверяющий корректную обработку спецсимволов.
        message = "send every hour with 502 and read-timeout"
        sanitized = sanitize_message(message)
        expected = "send every hour with 502 and read timeout"
        self.assertEqual(sanitized, expected)

    def test_generate_plantuml(self):
        #Тест для функции generate_plantuml, проверяющий корректную генерацию PlantUML.

        commit_data = [
            {
                'hash': '123abc',
                'parents': ['456def'],
                'message': 'Initial commit'
            },
            {
                'hash': '789ghi',
                'parents': [],
                'message': 'Second commit'
            }
        ]
        uml = generate_plantuml(commit_data)
        expected_uml = (
            "@startuml\n"
            "\"123abc\" : \"Initial commit\"\n"
            "\"123abc\" --> \"456def\"\n"
            "\"789ghi\" : \"Second commit\"\n"
            "@enduml"
        )
        self.assertEqual(uml, expected_uml)


if __name__ == "__main__":
    unittest.main()