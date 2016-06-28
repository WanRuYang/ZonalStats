import sys
import os 
import numpy as np
import gdal
from gdalconst import * 
import gdal, ogr, osr
import pyproj
from shapely.geometry import Polygon, Point
import subprocess
import csv 
import glob
import re
import fiona
from fiona.crs import from_epsg
import pandas as pd
gdal.PushErrorHandler('CPLQuietErrorHandler')

"""
read shapefile with fiona--as geosjon string
read tif
loop through each feature and get the overlap raster pixel value(s)
if touches one pixel, add properties['value'] = pixel value
finish loop and store the shapefile with extended attribute table

"""

class Rs(object):
	"""open gdal file and get geotranform info  
	"""
	def __init__(self, in_dataRaster, open2edit=False):
		# take single layer raster 
		if open2edit!=False:
			self.rsData = gdal.Open(in_dataRaster, GA_Update)
		else:
			self.rsData = gdal.Open(in_dataRaster, GA_ReadOnly)
		assert(self.rsData)
		# get the raster origins and pixel sizes
		self.geotransform = self.rsData.GetGeoTransform()
		self._oriX = self.geotransform[0]
		self._oriY = self.geotransform[3]
		self._resX = self.geotransform[1]
		self._resY = self.geotransform[5]
		self.b1 = self.rsData.GetRasterBand(1)
		self.nodata = self.b1.GetNoDataValue()
		self.proj = self.rsData.GetProjection()

def explode(coords):
    """Explode a GeoJSON geometry's coordinates object and yield coordinate tuples.
    As long as the input is conforming, the type of the geometry doesn't matter."""
    for e in coords:
        if isinstance(e, (float, int, long)):
            yield coords
            break
        else:
            for f in explode(e):
                yield f
def bbox(f):
    x, y = zip(*list(explode(f['geometry']['coordinates'])))
    return min(x), min(y), max(x), max(y)

def ft_raster(rsdata, geotransform, bbox):
	# get location offset on raster of each feature 
	x1 = int((bbox[0] - geotransform[0]) / geotransform[1])
	x2 = int((bbox[1] - geotransform[0]) / geotransform[1]) + 1
		
	y1 = int((bbox[3] - geotransform[3]) / geotransform[5])
	y2 = int((bbox[2] - geotransform[3]) / geotransform[5]) + 1

	xsize = x2-x1
	ysize = y2-y1

	return (x1, y1, xsize, ysize)


def labelas(vector_path, raster_path):

	v = fiona.open(vector_path) 
	r = Rs(raster_path)
		
	#write to shpafile 
	# with fiona.open('sum2005.shp', 'w',crs=from_epsg(3310),driver='ESRI Shapefile', schema=sink_schema) as output:
	# Copy the source schema and add two new properties.
	# sink_schema = v.schema.copy()
	# sink_schema['properties'][u'GDD2005'] = 'float'
    #	for i, b in enumerate(v):
	# 		# print 'feature', i,b['properties'][u'CO_MTR'], bbox(b)
	# 		offset = ft_raster(r, r.rsData.GetGeoTransform(), bbox(b))
	# 		gddVal = r.b1.ReadAsArray(offset[0], offset[1], 1, 1)
	# 		b['properties'][u'GDD2005'] = int(gddVal)
	# 		print 'feature', i, b['properties']
	# 		output.write(b)

	# write to csv

	dataout = []
	nb = [0]
	for x in range(1, 15): nb.append(x); nb.append(-x)
	for i, b in enumerate(v):

			offset = ft_raster(r, r.geotransform, bbox(b))
			gddVal = r.b1.ReadAsArray(offset[0], offset[1], 1, 1)

			if int(gddVal) > -1000:
				pass

			if int(gddVal) < -1000:
				for k in nb:
					gddVal = r.b1.ReadAsArray(offset[0]+k, offset[1]+k, 1, 1)
					if int(gddVal) > -1000:
						break
			dataout.append({ 'comtrs': str(b['properties'][u'CO_MTRS']), 'year':int(re.search('\d+',raster_path).group()), 'gdd' : int(gddVal) })

	df =  pd.DataFrame(dataout)
	df = df[['comtrs', 'year', 'gdd']]
	print df.iloc[1:5, ]
	return df 

vector_path = '/home/wryang/etdata/gdd/splm.shp'
# raster_path = '/home/wryang/etdata/gdd/g2005_alber.tif'
# labelas(vector_path, raster_path)  

dfs=[]
for f in sorted(glob.glob('/home/wryang/etdata/gdd/g*_alber.tif')):
	dfs.append(labelas(vector_path, f))
	print len(dfs)
dfs = pd.concat(dfs)
dfs.to_csv('/home/wryang/etdata/gdd/sumGdd.csv', engine='python')













