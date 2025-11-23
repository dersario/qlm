#!/usr/bin/env python3
"""
Простой скрипт для тестирования API QuickLead Manager
"""

import requests

BASE_URL = "http://localhost:8000"


def test_api():
    """Тестирование основных функций API"""

    print("🧪 Тестирование QuickLead Manager API")
    print("=" * 50)

    # 1. Проверка работоспособности
    print("\n1. Проверка работоспособности...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API работает")
            print(f"   Ответ: {response.json()}")
        else:
            print(f"❌ API недоступен: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return

    # 2. Аутентификация
    print("\n2. Аутентификация...")
    auth_data = {"username": "admin", "password": "admin123"}

    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", data=auth_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data["access_token"]
            print("✅ Успешная аутентификация")
            print(f"   Токен получен: {token[:20]}...")
        else:
            print(f"❌ Ошибка аутентификации: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return
    except Exception as e:
        print(f"❌ Ошибка при аутентификации: {e}")
        return

    # Заголовки для авторизованных запросов
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 3. Получение информации о пользователе
    print("\n3. Получение информации о пользователе...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Информация о пользователе получена")
            print(f"   Пользователь: {user_data['username']} ({user_data['role']})")
        else:
            print(f"❌ Ошибка получения информации: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    # 4. Создание проекта
    print("\n4. Создание проекта...")
    project_data = {
        "name": "Тестовый проект",
        "description": "Проект для тестирования API",
        "webhook_url": "https://httpbin.org/post",
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/projects", headers=headers, json=project_data
        )
        if response.status_code == 200:
            project = response.json()
            project_id = project["id"]
            api_key = project["api_key"]
            print("✅ Проект создан")
            print(f"   ID: {project_id}")
            print(f"   API ключ: {api_key[:20]}...")
        else:
            print(f"❌ Ошибка создания проекта: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # 5. Создание заявки через внешний API
    print("\n5. Создание заявки через внешний API...")
    lead_data = {
        "name": "Иван Тестовый",
        "phone": "+7 (999) 123-45-67",
        "email": "ivan.test@example.com",
        "message": "Тестовая заявка из скрипта",
        "utm_source": "test",
        "utm_campaign": "api_test",
        "custom_fields": {"budget": "100000", "source": "api_test"},
    }

    external_headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/lead", headers=external_headers, json=lead_data
        )
        if response.status_code == 200:
            lead = response.json()
            lead_id = lead["id"]
            print("✅ Заявка создана через внешний API")
            print(f"   ID заявки: {lead_id}")
            print(f"   Статус: {lead['status']}")
        else:
            print(f"❌ Ошибка создания заявки: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # 6. Получение заявок
    print("\n6. Получение заявок...")
    try:
        response = requests.get(f"{BASE_URL}/api/leads", headers=headers)
        if response.status_code == 200:
            leads = response.json()
            print(f"✅ Получено заявок: {len(leads)}")
            if leads:
                print(f"   Последняя заявка: ID {leads[0]['id']}, {leads[0]['name']}")
        else:
            print(f"❌ Ошибка получения заявок: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    # 7. Получение статистики
    print("\n7. Получение статистики...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/leads/stats/dashboard", headers=headers
        )
        if response.status_code == 200:
            stats = response.json()
            print("✅ Статистика получена")
            print(f"   Всего заявок: {stats['total_leads']}")
            print(f"   Конверсия: {stats['conversion_rate']}%")
        else:
            print(f"❌ Ошибка получения статистики: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    print("\n" + "=" * 50)
    print("🎉 Тестирование завершено!")


if __name__ == "__main__":
    test_api()
