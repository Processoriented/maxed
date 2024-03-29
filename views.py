from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from .models import *


def index(request):    
    dataset_list = DataSet.objects.all()
    context = {'dataset_list': dataset_list,}
    return render(request, 'maxed/index.html', context)

def detail(request, dataset_id):
    dataset = get_object_or_404(DataSet, id=dataset_id)
    common_objs = ForceObj.objects.filter(commonly_used=True).order_by('label', 'name')
    ds_objs = dataset.datasetobj_set.all().order_by('rel_pos')
    dso_fields = {}
    for dso in ds_objs:
        dso_fields[dso] = dso.datasetfield_set.all()
    context = {
        'dataset': dataset,
        'common_objs': common_objs,
        'fops': opsList()
    }
    return render(request, 'maxed/detail.html', context)

def addobj(request, dataset_id):
    dataset = get_object_or_404(DataSet, id=dataset_id)
    postkeys = request.POST.keys()
    if 'forceobj' in postkeys:
        try:
            selected_object = get_object_or_404(ForceObj, id=request.POST['forceobj'])
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

def fields(request, datasetobj_id):
    datasetobj = get_object_or_404(DataSetObj, id=datasetobj_id)
    prevh = datasetobj.datasetfield_set.filter(hidden=True)
    prevs = datasetobj.datasetfield_set.filter(hidden=False)
    postkeys = request.POST.keys()
    am = ""
    if request.POST['showhideall'] == 0:
        prevs.update(hidden=True)
        am = "Updated all " + datasetobj.forceobj.label
        am = am + " fields to hidden"
    elif request.POST['showhideall'] == 1:
        prevh.update(hidden=False)
        am = "Updated all " + datasetobj.forceobj.label
        am = am + " fields to shown"
    else:
        if ('hidden' in postkeys): 
            sl = request.POST.getlist('hidden')
            am = "Attempted fields ("
            am = am + ", ".join(sl)
            am = am + "): "
            aml = []
            for f in prevh:
                if (str(f.id) in sl):
                    f.hidden = False
                    f.save()
                    mli = f.forcefield.label
                    mli = mli + "[" + str(f.id) + "]: "
                    mli = mli + "shown"
                    aml.append(mli)
            for f in prevs:
                if not(str(f.id) in sl):
                    f.hidden = True
                    f.save()
                    mli = f.forcefield.label
                    mli = mli + "[" + str(f.id) + "]: "
                    mli = mli + "shown"
                    aml.append(mli)
            if (len(aml) > 0):
                am = am + "; ".join(aml) + "."
            else:
                am = am + "no matches."

    return HttpResponseRedirect(reverse('maxed:detail', args=(datasetobj.dataset.id,)))

def addFilter(request, datasetobj_id):
    datasetobj = get_object_or_404(DataSetObj, id=datasetobj_id)
    return HttpResponseRedirect(reverse('maxed:detail', args=(datasetobj.dataset.id,)))
    