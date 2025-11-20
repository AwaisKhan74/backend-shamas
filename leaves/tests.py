from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from leaves.models import LeaveRequest


class LeaveRequestAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.employee = User.objects.create_user(
            work_id="EMP001",
            username="employee",
            email="employee@example.com",
            password="Employee@123",
            role="FIELD_AGENT",
        )
        self.manager = User.objects.create_user(
            work_id="MAN001",
            username="manager",
            email="manager@example.com",
            password="Manager@123",
            role="MANAGER",
        )
        response = self.client.post(
            "/api/auth/login/",
            {"email": "employee@example.com", "password": "Employee@123"},
            format="json",
        )
        self.access_token = response.data["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_employee_create_leave_request(self):
        url = reverse("leaves-list")
        payload = {
            "leave_type": "SICK",
            "start_date": "2025-07-30",
            "end_date": "2025-08-08",
            "description": "Feeling unwell.",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LeaveRequest.objects.count(), 1)

    def test_manager_can_approve_leave(self):
        leave = LeaveRequest.objects.create(
            requested_by=self.employee,
            leave_type="SICK",
            start_date="2025-07-30",
            end_date="2025-07-31",
            description="Need rest",
        )
        response = self.client.post(
            "/api/auth/login/",
            {"email": "manager@example.com", "password": "Manager@123"},
            format="json",
        )
        token = response.data["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        status_url = reverse("leaves-set-status", args=[leave.id])
        response = self.client.patch(status_url, {"status": "APPROVED"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        leave.refresh_from_db()
        self.assertEqual(leave.status, "APPROVED")

