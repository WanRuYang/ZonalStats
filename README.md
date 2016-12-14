## ZonalStats : use scipy.ndimage for zonal stats of raster images 
Zonal Statistics is a common function in summarizing data for subregions in a area of interest. 
The procedure ususally involves two dataset: 
- a raster layer (single band) with the data value to aggreate, and 
- a shapfile with sub-region information as polygons. 

One straight forward idea is to loop through each polygon features to get 
the summary statistics , and this process can be extremely slow when the 
data size getting big（`･⊝･´ ）.
Here I utilize scipy function [ndimage](http://docs.scipy.org/doc/scipy-0.17.1/reference/ndimage.html) to speed up the process.

First, you have to convert the shapefile to image of the same size and resolution as the raster. 
This step is super easy since we have the awesome [gdal_rasterize](http://www.gdal.org/gdal_rasterize.html) function. 
Here comes an simgple way using gdal_rasterize to generate a shapefile for you:
```bash
gdal_rasterize -tr 30 30 -te -379800.000 -603780.000 538230.000 450450.000 -a id -of  GTiff -a_srs EPSG:3310 training.shp training.tif
```
where 
-tr spefify the x and y resolution 
-te specify the xmin ymin xmax ymax
-a the field the raster pixel value be based on 
-of data format, GTiff is actually the default 
-a_srs overwirte the original projection, DO NOT USE if you're not sure it correct



