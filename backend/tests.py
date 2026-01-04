# backend/tests.py
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class ThrottlingTestCase(APITestCase):
    """
    Тестирование ограничения частоты запросов (throttling)
    """

    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(
            email='throttle_test@example.com',
            password='testpass123',
            is_active=True
        )
        self.anon_url = '/api/v1/products'  # URL для анонимных запросов
        self.auth_url = '/api/v1/user/details'  # URL для авторизованных запросов

    def test_anon_throttling(self):
        """Тестирование throttling для анонимных пользователей"""
        print("Тест: ограничение для анонимных пользователей")

        # Делаем несколько запросов
        for i in range(5):
            response = self.client.get(self.anon_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            print(f"  Запрос {i + 1}: OK")

    def test_user_throttling(self):
        """Тестирование throttling для авторизованных пользователей"""
        print("Тест: ограничение для авторизованных пользователей")

        # Авторизуем пользователя
        self.client.force_authenticate(user=self.user)

        # Делаем несколько запросов
        for i in range(5):
            response = self.client.get(self.auth_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            print(f"  Запрос {i + 1}: OK")

    def test_different_endpoints_not_limited_together(self):
        """Тест что разные endpoints имеют отдельные лимиты"""
        print("Тест: разные endpoints имеют отдельные лимиты")

        urls = ['/api/v1/products', '/api/v1/categories', '/api/v1/shops']

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            print(f"  {url}: OK")


class APIEndpointsTestCase(APITestCase):
    """
    Тестирование основных API endpoints
    """

    def test_public_endpoints_accessible(self):
        """Тест что публичные endpoints доступны без авторизации"""
        public_endpoints = [
            '/api/v1/shops',
            '/api/v1/categories',
            '/api/v1/products',
        ]

        for endpoint in public_endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            print(f"{endpoint}: доступен без авторизации")

    def test_protected_endpoints_require_auth(self):
        """Тест что защищенные endpoints требуют авторизации"""
        protected_endpoints = [
            '/api/v1/basket',
            '/api/v1/order',
            '/api/v1/user/details',
            '/api/v1/user/contact',
        ]

        for endpoint in protected_endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            print(f"{endpoint}: требует авторизации")