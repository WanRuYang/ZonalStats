import numpy as np
from scipy import ndimage
import gdal
import glob
import pandas as pd
import re
import cPickle as pkl


class ZonalStats(object):
        def __init__(self, inDataFile, inLabelFile, maskNoData=False):
                self._inDs = inDataFile
                self._inLb = inLabelFile
                self.dataDs = gdal.Open(self._inDs)
                self.labelDs=  gdal.Open(self._inLb)

                if maskNoData==False:
                    self.data = self.dataDs.GetRasterBand(1).ReadAsArray()
                else:
                    nd = self.dataDs.GetRasterBand(1).GetNoDataValue()
                    self.data = np.ma.masked_less_equal(self.dataDs.GetRasterBand(1).ReadAsArray(), nd)
                
                self.lb = self.labelDs.GetRasterBand(1).ReadAsArray()
                self.labSet = np.unique( self.lb )
                self.result = {}
                print self.data.shape
                print self.lb.shape                #self.df

                return None

        def anz(self):
                self.result = {'id':list(self.labSet),
                         'mean':[ round(x, 4) for x in list(ndimage.mean(self.data, labels=self.lb, index=self.labSet))]
                         # ,
                         # 'min':list(ndimage.minimum(self.data, labels=self.lb, index=self.labSet)),
                         # 'max':list(ndimage.maximum(self.data, labels=self.lb, index=self.labSet)),
                         # 'std':list(ndimage.variance(self.data, labels=self.lb, index=self.labSet))
                         }
                #print self.result['id']
                #print self.result['min']
                #print len(self.result['min'])
                self.df = pd.DataFrame(self.result)
                self.df.set_index(self.df['id'])
                #print self.df

                # self.outname = self._inDs[:-4]+'.csv'
                # f = open(self.outname, 'w')
                # self.df.to_csv( f, index=False )
                # f.close()


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

        #todo add properties....
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

for yr in range(2006, 2015):

    """
    summary ndvi rasters; take mean value only 
    """
    print 'data year %d' %yr
    datafiles = sorted(glob.glob('/home/wryang/etdata/modisTemp/vi*'+str(yr)+'*sg134.tif'))
    print datafiles[0]
    zonefile = '/home/wryang/etdata/ndviGrid.tif'
    dfs=[]

    dfout = ZonalStats( datafiles[0], zonefile, True ).anz()
    dfout.columns = ['id', re.search('\d{7}', datafiles[0] ).group()]
    print 'date column name %s of file %s' %(re.search('\d{7}', datafiles[0] ).group(), datafiles[0])

    for f in datafiles[1:]:
        print f
        result = ZonalStats( f, zonefile, True ).anz()
        dataCol = re.search('\d{7}', f ).group()
        print 'date column name %s of file %s' %(dataCol,f)
        result.columns = ['id', dataCol ]
        result = result[[dataCol]]
        dfout = dfout.join(result)

    # export to csv 
    # dfout.to_csv('/home/wryang/etdata/cimis/vi'+str(yr)+'.csv')
    # exprot to pkl, the file is big and the following analysis will be done in python 
    with open('/home/wryang/etdata/cimis/vi'+str(yr)+'.pkl', 'a') as f:
        pkl.dump(df, f)


# datafiles = sorted(glob.glob('kc201*tif'))
# modis = sorted(glob.glob('modisTemp/vi*A201*crop.tif'))



#for i in range(len(datafiles)):
#       print 'data image %s' % datafiles[i]
#       ZonalStats( datafiles[i], 'kc30.tif' ).anz()

#       print 'temp file %s' % datafiles[i][:-4]+'.csv' 

# ds = [re.search('\d+', f).group() for f in datafiles]
# modis = [f for f in modis if re.search('\d+', f).group(0) in ds]
# for i in range(len(ds)):
#         print 'data files and vi files pari %s %s' %(ds[i], modis[i])
#         df_kc = pd.read_csv( datafiles[i][:-4]+'.csv' )
#         print df_kc.iloc[8000:8005, ]

#         #print 'vi image:%s' %modis[i]
#         df_vi = pd.DataFrame({ 'ndvi':list(ZonalStats(modis[i], 'vi250crop.tif').cal('mean')) })
#         df = pd.concat([df_vi, df_kc], axis=1)
#         df.to_csv( datafiles[i][:-4]+'_vikc.csv', index=False )