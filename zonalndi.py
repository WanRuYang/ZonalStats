import numpy as np
from scipy import ndimage
import gdal
import glob
import pandas as pd
import re
import cPickle as pkl
import os

class ZonalStats(object):
        def __init__(self, inDataFile, inLabelFile):
                self._inDs = inDataFile
                self._inLb = inLabelFile
                self.dataDs = gdal.Open(self._inDs)
                self.labelDs=  gdal.Open(self._inLb, gdal.GA_Update)
                self.data = self.dataDs.GetRasterBand(1).ReadAsArray()
		self.lb = self.labelDs.GetRasterBand(1).ReadAsArray()
		self.labSet = np.unique( self.lb )
                self.result = {}
                print self.data.shape
                print self.lb.shape               

                return None

        def anz(self):
                self.result = {'id':list(self.labSet),
                         'mean':[ round(x, 4) for x in list(ndimage.mean(self.data, labels=self.lb, index=self.labSet))],
                         'min':list(ndimage.minimum(self.data, labels=self.lb, index=self.labSet)),
                         'max':list(ndimage.maximum(self.data, labels=self.lb, index=self.labSet)),
                         'std':list(ndimage.variance(self.data, labels=self.lb, index=self.labSet))
                         }
                #print self.result['id']
                #print self.result['min']
                #print len(self.result['min'])
                self.df = pd.DataFrame(self.result)
		self.df = self.df[self.df['id']>0 ]
                self.df.set_index(self.df['id'])
               	
		# save each zonal ouput ...TODO
                # self.outname = self._inDs[:-4]+'.csv'
                # f = open(self.outname, 'w')
                # self.df.to_csv( f, index=False )
                # f.close()
		print self.df.iloc[0:5, ]

                return self.df

        def cal(self, stat = 'mean'):
                if stat=='mean':
                        zonalstats = ndimage.mean(self.data, labels=self.lb, index=self.labSet)
                if stat=='minimum':
                        zonalstats = ndimage.minimum(self.data, labels=self.lb, index=self.labSet)
                if stat=='maximum':
                        zonalstats = ndimage.maximum(self.data, labels=self.lb, index=self.labSet)
                if stat=='sum':
                        zonalstats = ndimage.sum(self.data, labels=self.lb, index=self.labSet)
                if stat=='std':
                        zonalstats = ndimage.standard_deviation(self.data, labels=self.lb, index=self.labSet)
                if stat=='variance':
                        zonalstats = ndimage.variance(self.data, labels=self.lb, index=self.labSet)
                return zonalstats

        #TODO add properties....
        #staticmethod
        # def sumlabel(self):
        #         hist = []
        #         def analyze(x):
        #                 xmin = x.min()
        #                 xmax = x.max()
        #                 xmean = x.mean()
        #                 xhist = np.histogram(x, range=(xmin, xmax))
        #                 hist.append({'min': xmin,
        #                          'max': xmax,
        #                          'mean': xmean,
        #                          'hist': xhist})
        #                 return 1


        #         ndimage.labeled_comprehension(self.data, self.lb, self.labSet, analyze, float, -1)
        #         print hist


def fixlabel(inData, inLabel):
	"""
	dobule check if the zonal label image correctly label each no data value "0"
	"""
	lds = gdal.Open(inLabel, gdal.GA_Update)
	dds = gdal.Open(inData)
	
	lb = (lds.GetRasterBand(1).ReadAsArray())
	db = (dds.GetRasterBand(1).ReadAsArray())
	
	r, c = lb.shape	

	for i in range(r*c):
		if (db.flatten())[i] == -99:
			(lb.flatten())[i]=0

	lds.GetRasterBand(1).WriteArray(lb.reshape(r, c), 0, 0)
	lds = None
	dds = None


if __name__ == "__main__": 
	for yr in range(2005, 2015):

	"""
    	summary ndvi rasters; take mean value only 
    	"""
    	print 'data year %d' %yr
	datafiles = sorted(glob.glob('/home/wryang/etdata/modisTemp/vi*'+str(yr)+'*sg134.tif'))
    	print datafiles[0]
    	zonefile = '/home/wryang/etdata/ndviGrid.tif'
        dfout = ZonalStats( datafiles[0], zonefile ).anz()
	dfout.columns = ['id', re.search('\d{7}', datafiles[0] ).group()]
        print 'date column name %s of file %s' %(re.search('\d{7}', datafiles[0] ).group(), datafiles[0])

        for f in datafiles[1:]:
		print f
		result = ZonalStats( f, zonefile ).anz()
        	dataCol = re.search('\d{7}', f ).group()
	        print 'date column name %s of file %s' %(dataCol,f)
        	result.columns = ['id', dataCol ]
	        result = result[[dataCol]]
	        dfout = dfout.join(result)

	# export to csv 
	dfout.to_csv('/home/wryang/etdata/cimis/vi'+str(yr)+'.csv')

	# exprot to pkl, the file is big and the following analysis will be done in python 
	# with open('/home/wryang/etdata/cimis/vi'+str(yr)+'.pkl', 'a') as f:
	#     pkl.dump(dfout, f)

