from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages

from celery import shared_task
import json
from django.core.serializers import serialize
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy

from .models import NdbiTask, Shapefile, Geometry

from .tasks import save_data


testData = [
    {
        'id':1,
        'name': 'Jon Doe',
    },
    {
        'id': 2,
        'name': 'Clarie Anderson',

    }
]
# Create your views here.
def index(request):
    context = {
        'title': 'Home',
        'members': testData,
    }
    # return HttpResponse('<h1>Blog Home</h1>')
    return render(request, 'ds4rs_app1/home.html', context)

def about(request):
    context = {
        'title': 'About',
    }
    return render(request, 'ds4rs_app1/about.html', context)


# def ndbi(request):
#     if request.POST and 'submit' in request.POST:
#         print('NDBI Post Request')
        
#         fromDate = request.POST.get('fromDate')
#         toDate = request.POST.get('toDate')
#         cloudCover = request.POST.get('cloudCover')
#         satelliteName = request.POST.get('satelliteName')


#         files_pk = []
#         NdbiTask.objects.all().delete()
        
#         if 'aoiShapeFile' in request.FILES:
#             files = request.FILES.getlist('aoiShapeFile')
#             # print(files)
#             for f in files:
#                 uploaded = NdbiTask(fromDate = fromDate ,toDate = toDate,cloudCover = cloudCover, satelliteName = satelliteName, aoiShape=f)
#                 uploaded.save()
#                 files_pk.append(uploaded.pk)
#             # print(files_pk)
#             fig = save_data(files=json.dumps(files_pk))
#             print(fig)
            
#             # return render(request,'ds4rs_app1/ndbi.html', {'site':'a','Predictions':['SITESa','SITESb'],'chart':fig})
        
#         return HttpResponseRedirect(reverse_lazy('ds4rs-home'))

    # else:
    #     print('NDBI GET REQUEST')

    #     context = {
    #     'title': 'NDBI',
    #     'meassage': 'This is the NDBI!'
    #     }
    #     return render(request, 'ds4rs_app1/ndbi.html',context)

def ndvi(request):

    if request.method == 'POST':
        print('NDVI POST REQUEST')
        
        files_pk = []
        # UploadedFile.objects.all().delete()
        
        if 'shape' in request.FILES:
            files = request.FILES.getlist('shape')
            print(files)
            # for f in files:
            #     uploaded = UploadedFile(document=f)
            #     uploaded.save()
            #     files_pk.append(uploaded.pk)
            # save_data.delay(files=json.dumps(files_pk))
        # return HttpResponseRedirect(reverse_lazy('home'))



        
    else:
        print('NDVI GET REQUEST')
    return render(request, 'ds4rs_app1/ndvi.html')

    # print('hello')
    # context = {
    #     'title': 'NDVI',
    #     'meassage': 'This is the NDVI!'
    #     }
    # return render(request, 'ds4rs_app1/ndvi.html', context)

def lulc(request):
    print('hello')
    context = {
        'title': 'LULC',
        'meassage': 'This is the LULC!'
        }
    return render(request, 'ds4rs_app1/lulc.html', context)














class ndbi(TemplateView):
  template_name="ndbi.html"
  def index(request):
    # if request.POST and 'submit' in request.POST:
    #     print('NDBI Post Request')
            
    #     fromDate = request.POST.get('fromDate')
    #     toDate = request.POST.get('toDate')
    #     cloudCover = request.POST.get('cloudCover')
    #     satelliteName = request.POST.get('satelliteName')


    #     files_pk = []
    #     NdbiTask.objects.all().delete()
        
    #     if 'aoiShapeFile' in request.FILES:
    #         files = request.FILES.getlist('aoiShapeFile')
    #         # print(files)
    #         for f in files:
    #             uploaded = NdbiTask(fromDate = fromDate ,toDate = toDate,cloudCover = cloudCover, satelliteName = satelliteName, aoiShape=f)
    #             uploaded.save()
    #             files_pk.append(uploaded.pk)
    #         # print(files_pk)
    #         fig = save_data(files=json.dumps(files_pk))
    #         print(fig)
            
    #         # return render(request,'ds4rs_app1/ndbi.html', {'site':'a','Predictions':['SITESa','SITESb'],'chart':fig})
        
    #     return HttpResponseRedirect(reverse_lazy('ds4rs-home'))

    # else:
    print('NDBI GET REQUEST')

    context = {
       'title': 'NDBI',
       'meassage': 'This is the NDBI!'
        }
    return render(request, 'ds4rs_app1/ndbi.html',context)





  def getNdbiChart(request):
    print('hello')
    context = locals()
    chartArray=[]
    myChart=()
    if request.POST and 'submit' in request.POST:
        print('NDBI Post Request')
            
        fromDate = request.POST.get('fromDate')
        toDate = request.POST.get('toDate')
        cloudCover = request.POST.get('cloudCover')
        satelliteName = request.POST.get('satelliteName')




        files_pk = []
        NdbiTask.objects.all().delete()
        
        if 'aoiShapeFile' in request.FILES:
            files = request.FILES.getlist('aoiShapeFile')
            # print(files)
            for f in files:
                uploaded = NdbiTask(fromDate = fromDate ,toDate = toDate,cloudCover = cloudCover, satelliteName = satelliteName, aoiShape=f)
                uploaded.save()
                files_pk.append(uploaded.pk)
            # print(files_pk)
            chartInfo  = save_data( fromDate, toDate,cloudCover, satelliteName, files=json.dumps(files_pk))
            # print(fig)
            myChart = chartInfo['fig']
            totalNumofImages = chartInfo['totalNumofImages']

        chartTitle="NDBI Time Series"
        description="The line graph below shows the changes in the Max, Min, and Mean NDBI values over the time period from "+fromDate+" to "+toDate+"."
        postscript="""<ul>
        <li>The line graph uses the """ +str.upper(satelliteName) +""" data from Google Earth Engine(GEE) Archive and Uses <i>Altair</i> python Library to generate the graph</li>
        <li>The Maximum Cloud cover considered in this analysis is """+cloudCover+"""%</li>
        <li>The total number of images analyzed is """+str(totalNumofImages)+""" </li>
        </ul>"""
        p={}
        p['name']=chartTitle
        p['chart']=myChart
        myChart.save('chart.html')
        p['description']=description
        p['postscript']=postscript
        chartArray.append(p)

        context['chartArray']=chartArray
        print(context)
        return render(request, 'ds4rs_app1/ndbi_chart.html', context)
