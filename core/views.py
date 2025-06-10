# core/views.py
from django.shortcuts import render
from django.views.generic import TemplateView

class HomePageView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # You can add some data here, e.g., featured courses
        # from courses.models import Course
        # context['featured_courses'] = Course.objects.filter(is_published=True).order_by('?')[:3]
        return context