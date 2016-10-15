from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from .models import *


def index(request):    
    dataset_list = DataSet.objects.all()
    context = {'dataset_list': dataset_list,}
    return render(request, 'maxed/index.html', context)

def detail(request, dataset_id):
    dataset = get_object_or_404(DataSet, pk=dataset_id)
    common_objs = ForceObj.objects.filter(commonly_used=True).order_by('label', 'name')
    ds_objs = dataset.datasetobj_set.all().order_by('rel_pos')
    dso_fields = {}
    for dso in ds_objs:
        dso_fields[dso] = dso.datasetfield_set.all()
    context = {
        'dataset': dataset,
        'common_objs': common_objs
    }
    return render(request, 'maxed/detail.html', context)

def addobj(request, dataset_id):
    dataset = get_object_or_404(DataSet, pk=dataset_id)
    postkeys = request.POST.keys()
    if 'forceobj' in postkeys:
        try:
            selected_object = get_object_or_404(ForceObj, pk=request.POST['forceobj'])
        except (KeyError, ForceObj.DoesNotExist):
            #redisplay the form
            return render(request, 'maxed/detail.html', {
                'dataset': dataset,
                'error_message': "You didn't select a SalesForce Object.",
                })
        else:
            dataset.datasetobj_set.get_or_create(forceobj=selected_object)
            return HttpResponseRedirect(reverse('maxed:detail', args=(dataset.id,)))
    else:
        dataset.datasetobj_set.all().delete()
        return HttpResponseRedirect(reverse('maxed:detail', args=(dataset.id,)))

