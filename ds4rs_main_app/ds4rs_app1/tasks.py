import json
import os
import folium
from osgeo import ogr
from osgeo import osr
from django.contrib.gis.geos import GEOSGeometry
from django.conf import settings
from celery import shared_task

from .models import NdbiTask, Shapefile, Geometry
from django.contrib.gis.gdal import DataSource

import pathlib
import geemap
import ee
import numpy as np
import ee
from google.auth import compute_engine
import pandas as pd
import warnings
import altair as alt
import pandas as pd

#folium
import folium
from folium import plugins







def get_ndbi(img, aoi):
    
    img_date = img.date().getInfo()['value']
    img_sytemindex = img.get('system:index').getInfo()
  
    nir  = img.select('B4') #picking the near infrared band from the img
    swir = img.select('B5') #picking short wave infrared
    
    ndbi = swir.subtract(nir).divide(swir.add(nir)).rename('NDBI')
    
    return ndbi


def get_ndbi_info(img, aoi):
    
    img_date = img.date().getInfo()['value']
    img_sytemindex = img.get('system:index').getInfo()
  
    nir  = img.select('B4') #picking the near infrared band from the img
    swir = img.select('B5') #picking short wave infrared
    
    ndbi = swir.subtract(nir).divide(swir.add(nir)).rename('NDBI')
    
    min_ndbi_val = ndbi.reduceRegion(ee.Reducer.min(), aoi, 30,  crs = 'EPSG:32648', bestEffort = True, maxPixels = 1e9).getInfo()['NDBI']
    max_ndbi_val = ndbi.reduceRegion(ee.Reducer.max(), aoi, 30,  crs = 'EPSG:32648', bestEffort = True, maxPixels = 1e9).getInfo()['NDBI']
    mean_ndbi_val = ndbi.reduceRegion(ee.Reducer.mean(), aoi, 30,  crs = 'EPSG:32648', bestEffort = True, maxPixels = 1e9).getInfo()['NDBI']
    
    img_all_info = {
      'system:index': img_sytemindex,
      'date': img_date,
      'min_ndbi' : min_ndbi_val,
      'max_ndbi' : max_ndbi_val,
      'mean_ndbi' : mean_ndbi_val      
      }

    return img_all_info

def add_date_info(df):
  df['Timestamp'] = pd.to_datetime(df['Millis'], unit='ms')
  df['Year'] = pd.DatetimeIndex(df['Timestamp']).year
  df['Month'] = pd.DatetimeIndex(df['Timestamp']).month
  df['Day'] = pd.DatetimeIndex(df['Timestamp']).day
  df['DOY'] = pd.DatetimeIndex(df['Timestamp']).dayofyear
  return df

#clipping
def fctn_clip(img,aoi):
  clip_img = img.clip(aoi)
  return clip_img



service_account = settings.GEE_SERVICE_ACC
credentials = ee.ServiceAccountCredentials(service_account, settings.GEE_CREDS)
ee.Initialize(credentials)


figure = folium.Figure()
        
#create Folium Object
map  = folium.Map(
    location=[28.5973518, 83.54495724],
    zoom_start=8
)

# visual parameters for the satellite imagery natural colors display
image_vis_params = {
  'min': 0,
  'max': 0.3,
  'gamma': 1,
#   'palette': [ 'FE8374', 'C0E5DE', '3A837C','034B48'],
}


#add map to figure
map.add_to(figure)


# ##### earth-engine drawing method setup
def add_ee_layer(self, ee_image_object, vis_params, name):
  map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
  folium.raster_layers.TileLayer(
      tiles = map_id_dict['tile_fetcher'].url_format,
      attr = 'Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
      name = name,
      overlay = True,
      control = True
  ).add_to(self)

# configuring earth engine display rendering method in folium
folium.Map.add_ee_layer = add_ee_layer


@shared_task
def save_data(fromDate,toDate,cloudCover, satelliteName, files):
    pks = json.loads(files)


    cloudCover_ee = ee.Number(int(cloudCover))
    from_year_ee = ee.Number(int(fromDate.split('-')[0]))
    from_month_ee = ee.Number(int(fromDate.split('-')[1]))
    from_day_ee = ee.Number(int(fromDate.split('-')[2]))

    
    to_year_ee = ee.Number(int(toDate.split('-')[0]))
    to_month_ee = ee.Number(int(toDate.split('-')[1]))
    to_day_ee = ee.Number(int(toDate.split('-')[2]))


    if satelliteName == 'landsat7':
        satelliteName = str.upper(satelliteName)
    elif satelliteName == 'landsat8':
        satelliteName = str.upper(satelliteName)
    elif satelliteName == 'sentinel2':
        satelliteName == str.upper(satelliteName)
    else:
        print('Satellite Not Added Yet!')

    print(satelliteName)


    files = NdbiTask.objects.filter(pk__in=pks)
    for file in files:
        ext = file.filename().split('.')[1]
        if ext == 'shp':
            file_path = os.path.join(str(settings.BASE_DIR).replace('\\', '/')+ file.aoiShape.url)

            aoi = geemap.shp_to_ee(file_path)
            print('Loading aoi shape path to ee done')

            # import numpy as np
            # aoi_geometry = aoi.geometry()
            # coords = aoi_geometry.getInfo()['coordinates']
            # mapBoundary = coords[0][1]

            # coords = np.array(coords[0])

            # today = ee.Date(pd.to_datetime('today'))
            # date_range = ee.DateRange(today.advance(-5, 'years'), today)
            
            landsat =  ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA').filterBounds(aoi)\
                        .filter(ee.Filter.lt('CLOUD_COVER', cloudCover_ee)).filter(ee.Filter.calendarRange(from_year_ee,to_year_ee,'year'))\
                            .filter(ee.Filter.calendarRange(from_month_ee,to_month_ee,'month'))
            
                        
            print("Total Image Downloaded: ",landsat.size().getInfo()) #gets the total number of images

            if landsat.size().getInfo() < 1:
               print('Insufficient Image Downloaded for a time series analysis')

            landsat_list = landsat.toList(landsat.size()) # the landsat image collection is an imagecollection object which is 
                                                            #an earthengine native datatype. this collections can not be iterated by loop. 
                                                            #So we have to convert it to a list or array to iteratively process it. 
            
            
            landsat_list_size = landsat_list.size().getInfo()
  
            warnings.filterwarnings('ignore')

  
            df = pd.DataFrame(columns=['SystemIndex', 'Millis', 'MinNDBI', 'MaxNDBI', 'MeanNDBI'])

            for i in range(landsat_list_size):
                print(i)
                image = ee.Image(landsat_list.get(i))
                image = fctn_clip(image, aoi)

                # image_ndbi = get_ndbi(image, aoi)



                # map.add_ee_layer(image_ndbi, image_vis_params, 'LandsatFirst')
                # map.add_child(folium.LayerControl())




                image_info = get_ndbi_info(image, aoi)
                df = df.append({'SystemIndex': image_info['system:index'], 
                                'Millis':  image_info['date'], 
                                'MinNDBI': image_info['min_ndbi'], 
                                'MaxNDBI': image_info['max_ndbi'], 
                                'MeanNDBI': image_info['mean_ndbi']}, 
                                ignore_index=True)

            df = add_date_info(df).drop(columns=['Millis'])


            fig = alt.Chart(df).transform_fold(['MinNDBI', 'MaxNDBI', 'MeanNDBI'],as_=['NDBI_Type', 'Value']
                                               ).mark_line().encode(x='Timestamp:T',y='Value:Q',color='NDBI_Type:N')
            
            # fig.save('chart.html')

            # print(fig)

            chartInfo = {
                'fig': fig,
                'totalNumofImages': landsat_list_size
            }

            # Clean up uploaded files
            for pk in pks:
                try:
                    db_file = NdbiTask.objects.get(pk=pk)
                    # Delete the uploaded files or perform necessary cleanup
                    db_file.delete()  # This deletes the database record and the associated file
                except NdbiTask.DoesNotExist:
                    pass  # Handle if the record does not exist


            return chartInfo        
        else:    # if file format is not shp we do not process. Just continue to next iteration
            continue 
        
        for pk in pks: # Clean up uploaded files
            try:
                db_file = NdbiTask.objects.get(pk=pk)
                # Delete the uploaded files or perform necessary cleanup
                db_file.delete()  # This deletes the database record and the associated file
            except NdbiTask.DoesNotExist:
                pass  # Handle if the record does not exist

        return