from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Q
from .models import WebcamModel, Favourite
from core.models import Config


class ModelDetailView(DetailView):
    """
    Display detail page for a specific webcam model.
    Converted from HomeController@detail in Laravel.
    """
    model = WebcamModel
    template_name = 'models_app/detail.html'
    context_object_name = 'model'

    def get_object(self):
        unique_username = self.kwargs.get('unique_username')
        return get_object_or_404(WebcamModel, user_name=unique_username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add related models
        model = self.get_object()
        context['related_models'] = WebcamModel.objects.filter(
            gender=model.gender,
            is_online=True
        ).exclude(id=model.id)[:8]
        return context


class RelatedModelsView(View):
    """
    AJAX endpoint for fetching related models.
    Converted from HomeController@ajaxRelated in Laravel.
    """
    def get(self, request, id):
        model = get_object_or_404(WebcamModel, id=id)
        related = WebcamModel.objects.filter(
            gender=model.gender,
            is_online=True
        ).exclude(id=id)[:8]

        data = [
            {
                'id': m.id,
                'display_name': m.display_name,
                'image': m.image,
                'user_name': m.user_name,
                'is_online': m.is_online,
            }
            for m in related
        ]
        return JsonResponse({'models': data})


class GenderFilterView(ListView):
    """
    Filter models by gender.
    Converted from HomeController@sex in Laravel.
    """
    model = WebcamModel
    template_name = 'models_app/sex.html'
    context_object_name = 'models'
    paginate_by = 20

    def get_queryset(self):
        sex = self.kwargs.get('sex')
        # Get gender mapping from Config model
        gender_map = Config.GENDER_MAPPING.get(sex, [])

        queryset = WebcamModel.objects.filter(
            is_online=True,
            gender__in=gender_map
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sex'] = self.kwargs.get('sex')
        return context


class FavouritesView(LoginRequiredMixin, ListView):
    """
    Display user's favourite models.
    Converted from HomeController@favorites in Laravel.
    """
    model = WebcamModel
    template_name = 'models_app/favorited.html'
    context_object_name = 'models'
    paginate_by = 20

    def get_queryset(self):
        return self.request.user.favourited_models.all()


class ToggleFavouriteView(LoginRequiredMixin, View):
    """
    Toggle favourite status for a model.
    Converted from HomeController@attachFavourite in Laravel.
    """
    def post(self, request, id):
        model = get_object_or_404(WebcamModel, id=id)
        favourite, created = Favourite.objects.get_or_create(
            user=request.user,
            model=model
        )

        if not created:
            favourite.delete()
            action = 'removed'
        else:
            action = 'added'

        return JsonResponse({
            'success': True,
            'action': action,
            'message': f'Model {action} to favourites'
        })
