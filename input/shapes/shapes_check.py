""" Fixing of a new error that started on Sao Paulo state.
    INFO:shapely.geos:Self-intersection at or near point -46.752428277068574 -23.326725567347236
    INFO:generator:Generating region 3509007001001
    We are guessing due to new library precisions.
"""


import geopandas as gdp

aps = gdp.read_file('APS.shp')
aps[aps.AP == '3509007001001']['geometry'] = aps[aps.AP == '3509007001001'].geometry.buffer(0)
aps.to_file('APs.shp')

# fr = 'mun_ACPS_ibge_2014_latlong_wgs1984_fixed.shp'
# ur = 'URBAN_IBGE_ACPs.shp'
#
# full_region = gdp.read_file(fr)
# urban_region = gdp.read_file(ur)

# full_region['geometry'] = full_region.geometry.buffer(0)
# urban_region['geometry'] = urban_region.geometry.buffer(0)
#
# full_region.to_file(fr)
# urban_region.to_file(ur)

