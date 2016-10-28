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
gdal.PushErrorHandler('CPLQuietErrorHandler')

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
		self._resX = abs(self.geotransform[1])
		self._resY = abs(self.geotransform[5])
		self.b1 = self.rsData.GetRasterBand(1)
		self.nodata = self.b1.GetNoDataValue()
		self.proj = self.rsData.GetProjection()
 		#p = osr.SpatialReference()
		#p.ImportFromEPSG(3310)
		#self.rsData.SetProjection(p.ExportToWkt)		
	
	#TODO: setting geotransform

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

	vds = ogr.Open(vector_path, GA_ReadOnly)  # TODO maybe open update if we want to write stats
	assert(vds)
	vlyr = vds.GetLayer(0)
	rds = Rs(raster_path, True)
	b=rds.b1.ReadAsArray()
	nr, nc = b.shape				
	print nr, nc
	#sourceSR = vlyr.GetSpatialRef()
	#targetSR = osr.SpatialReference()
	#targetSR.ImportFromEPSG(3310)
	#coordTrans = osr.CreateCoordinateTransformation(sourceSR,targetSR)
	
	print len(vlyr)
	for i,ft in enumerate(vlyr):
		off = ft_raster(rds, rds.geotransform, ft.geometry().GetEnvelope())
		print 'feature # %d %s' %(i, str(off))

		if off[0] < 0 and off[1] <0:
			src_array = rds.b1.ReadAsArray(0, 0, off[2]+off[0], off[3]+off[1])
			rows, cols =  src_array.shape
                        outData = np.array( [i]*(rows*cols) ).reshape(rows, cols)
                        print 'offset', off[0], off[1]
                        rds.b1.WriteArray( outData, 0, 0)

		if off[0] <0 and off[1] >=0:
			if off[0]+off[2] > nr:
                                nY = nr - off[1]
                                src_array = rds.b1.ReadAsArray( off[0], 0, off[2]+off[0], nY )
                                rows, cols =  src_array.shape
                                outData = np.array( [i]*(rows*cols) ).reshape(rows, cols)
                                print  'y offset <0 and x offset > image'
                                rds.b1.WriteArray( outData, 0, off[1])
				
			if off[1]+off[3] <= nr:
	                        src_array = rds.b1.ReadAsArray(0, off[1], off[2]+off[0], off[3] )
        	                rows, cols =  src_array.shape
                	        outData = np.array( [i]*(rows*cols) ).reshape(rows, cols)
                        	print 'offset', off[0], off[1]
	                        rds.b1.WriteArray( outData, 0, off[1])


                if off[0] >= 0 and off[1] <0:
			if off[0]+off[2] > nc:
				nX = nc - off[0]
                                src_array = rds.b1.ReadAsArray( off[0], 0, nX, off[3]+off[1] )
                                rows, cols =  src_array.shape
                                outData = np.array( [i]*(rows*cols) ).reshape(rows, cols)
                                print  'y offset <0 and x offset > image'
                                rds.b1.WriteArray( outData, off[0], 0)

			if off[0]+off[2] <= nc:
	                        src_array = rds.b1.ReadAsArray( off[0], 0, off[2], off[3]+off[1] )
        	                rows, cols =  src_array.shape
                	        outData = np.array( [i]*(rows*cols) ).reshape(rows, cols)
           			print  'y oofset <0'
	                        rds.b1.WriteArray( outData, off[0], 0)
			

		if off[1] >=0 and off[0] >=0:
			
			if off[0]+off[2] > nc and off[1]+off[3] > nr:
				print 'polygon exceed image width and legth'
				nX = nc-off[0]
				nY = nr-off[1]
				src_array = rds.b1.ReadAsArray( off[0],off[1],nX,nY )
				rows, cols =  src_array.shape
				outData = np.array( [i]*(rows*cols) ).reshape(rows, cols)
				rds.b1.WriteArray( outData, off[0], off[1])
 
                        if off[0]+off[2] > nc and off[1]+off[3] < nr:
                                print 'polygon exceed image width and legth'
                                nX = nc-off[0]
                     
                                src_array = rds.b1.ReadAsArray( off[0],off[1],nX,off[3] )
                                rows, cols =  src_array.shape
                                outData = np.array( [i]*(rows*cols) ).reshape(rows, cols)
                                rds.b1.WriteArray( outData, off[0], off[1])

                        if off[0]+off[2] < nc and off[1]+off[3] > nr:
                                print 'polygon exceed image width and legth'
                                nY = nr-off[1]

                                src_array = rds.b1.ReadAsArray(off[0],off[1],off[2], nY )
                                rows, cols =  src_array.shape
                                outData = np.array( [i]*(rows*cols) ).reshape(rows, cols)
                                rds.b1.WriteArray( outData, off[0], off[1])

	
			if  off[0]+off[2] <= nc and off[1]+off[3] <= nr:
				src_array = rds.b1.ReadAsArray(*off)
				rows, cols =  src_array.shape
				outData = np.array( [i]*(rows*cols) ).reshape(rows, cols)
				rds.b1.WriteArray( outData, off[0], off[1])
		 

if __name__ == "__main__": 
	#gdaltindex
	#poly
	
	#vs = ['ca_north250.shp', 'ca_south250.shp', 'ca_center250.shp']
	#rs = ['ca_north30.tif', 'ca_south30.tif', 'ca_center30.tif']

	#for i in range(len(rs)):
	#	labelas(vs[i], rs[i])	
	# convert vi250.tif to vi250.shp
	# labelas('vi250crop.shp', 'kc30.tif')

	# use target region shapfile to create splmLabel each comtrs has a number 
	labelas('/home/wryang/etdata//gdd/splm.shp', '/home/wryang/etdata/ndviGrid.tif')

