from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'
    # title = "Об авторе проекта"


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'
