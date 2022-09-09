from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.generics import get_object_or_404, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsCharityOwner, IsBenefactor
from .models import Task, Benefactor
from .serializers import (
    TaskSerializer,
    CharitySerializer,
    BenefactorSerializer
)

from django.http.response import HttpResponse


def index():
    return HttpResponse('<h1>Hello world</h1>')


class BenefactorRegistration(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(data=None)

    def post(self, request, *args, **kwargs):
        serializer = BenefactorSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save(user=self.request.user)

            return Response(
                data={
                    "username": request.user.username,
                    "message": f"Benefactor with {request.user.username} created!"
                },
                status=status.HTTP_201_CREATED,
                content_type='application/json',
            )


class CharityRegistration(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(data=None)

    def post(self, request, *args, **kwargs):
        serializer = CharitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)

            return Response(
                data={
                    "username": request.user.username,
                    "message": f"Charity with username: <{request.user.username}> has been created!",
                },
                status=status.HTTP_201_CREATED,
                content_type='application/json',
            )


class Tasks(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all_related_tasks_to_user(self.request.user)

    def post(self, request, *args, **kwargs):
        data = {
            **request.data,
            "charity_id": request.user.charity.id
        }
        serializer = self.serializer_class(data = data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            self.permission_classes = [IsAuthenticated, ]
        else:
            self.permission_classes = [IsCharityOwner, ]

        return [permission() for permission in self.permission_classes]

    def filter_queryset(self, queryset):
        filter_lookups = {}
        for name, value in Task.filtering_lookups:
            param = self.request.GET.get(value)
            if param:
                filter_lookups[name] = param
        exclude_lookups = {}
        for name, value in Task.excluding_lookups:
            param = self.request.GET.get(value)
            if param:
                exclude_lookups[name] = param

        return queryset.filter(**filter_lookups).exclude(**exclude_lookups)


class TaskRequest(APIView):
    permission_classes = (IsBenefactor,)

    def get(self, request, task_id, *args, **kwargs):
        task = get_object_or_404(Task, id=task_id)

        if task.state != "P":
            return Response(
                data={
                    'detail': 'This task is not pending.'
                },
                status=status.HTTP_404_NOT_FOUND,
                content_type='application/json'
            )

        else:
            task.state = "W"
            task.assigned_benefactor = Benefactor.objects.get(id=request.user.id)
            task.save()
            return Response(
                data={
                    'detail': 'Request sent.'
                },
                status=status.HTTP_200_OK,
                content_type='application/json'
            )


class TaskResponse(APIView):
    permission_classes = [IsCharityOwner]

    def post(self, request, task_id, *args, **kwargs):
        if request.data['response'] not in ('A', 'R'):
            return Response(
                data={
                    'detail': 'Required field ("A" for accepted / "R" for rejected)'
                },
                status=status.HTTP_400_BAD_REQUEST,
                content_type='application/json'
            )

        task = get_object_or_404(Task, id=task_id)
        if task.state != 'W':
            return Response(
                data={
                    'detail': 'This task is not waiting.'
                },
                status=status.HTTP_404_NOT_FOUND,
                content_type='application/json'
            )
        else:

            if request.data['response'] == 'A':
                task.state = 'A'
                task.save()
                return Response(
                    data={'detail': 'Response sent.'},
                    status=status.HTTP_200_OK,
                    content_type='application/json'
                )

            if request.data['response'] == 'R':
                task.state = 'P'
                task.assigned_benefactor = None
                task.save()
                return Response(
                    data={'detail': 'Response sent.'},
                    status=status.HTTP_200_OK,
                    content_type='application/json'
                )


class DoneTask(APIView):
    permission_classes = [IsCharityOwner]

    def post(self, request, task_id, *args, **kwargs):
        task = get_object_or_404(Task, id=task_id)

        if task.state != "A":
            return Response(
                data={'detail': 'Task is not assigned yet.'},
                status=status.HTTP_404_NOT_FOUND,
                content_type='application/json'
            )
        task.state = 'D'
        task.save()

        return Response(
            data={'detail': 'Task has been done successfully.'},
            status=status.HTTP_200_OK,
            content_type='application/json'
        )


class Update(UpdateAPIView):
    pass
