from django.shortcuts import render
from django.views.generic import DetailView, ListView

from isegory.models import Power, Triad, Data


class PowerList(ListView):

    def get_queryset(self):
        return Power.objects.all()


class PowerDetail(DetailView):
    model = Power


class PersonList(ListView):

    def get_queryset(self):
        return Triad.objects.filter(name__exact='per')


class OrganList(ListView):

    def get_queryset(self):
        return Triad.objects.filter(name__exact='org')


class InformationList(ListView):

    def get_queryset(self):
        return Triad.objects.filter(name__exact='inf')


class DataList(ListView):

    def get_queryset(self):
        return Data.objects.all()


class DataDetail(DetailView):
    model = Data


def index(request):
    return render(request, 'isegory/index.html')


def docs(request):
    return render(request, 'isegory/documentation.html')
