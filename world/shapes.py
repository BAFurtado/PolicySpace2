import json
from collections import defaultdict

import geopandas as gpd
import pandas as pd
from osgeo import ogr
from shapely.geometry import shape


def prepare_shapes_2010(geo):
    urban = pd.DataFrame()
    temp = gpd.read_file('input/shapes/2010/urban_mun_2010.shp')
    for mun in geo.mun_codes:
        temp1 = temp[temp.CD_MUN == str(mun)]
        urban = pd.concat([temp1, urban])

    urban = {
        mun: urban[urban.CD_MUN == mun]['geometry'].item()
        for mun in urban.CD_MUN
    }

    codes = [str(code) for code in geo.mun_codes]

    my_shapes = list()
    states = list()
    for uf in geo.states_on_process:
        states.append(ogr.Open(f'input/shapes/2010/areas/{uf}.shp'))
    for mun_id in codes:
        for state in states:
            for mun_reg in range(state.GetLayer(0).GetFeatureCount()):
                if state.GetLayer(0).GetFeature(mun_reg).GetField(1) == mun_id:
                    shap = state.GetLayer(0).GetFeature(mun_reg)
                    shap.id = str(shap.GetField(0))
                    my_shapes.append(shap)

    return urban, my_shapes


def prepare_shapes(geo):
    """Loads shape data for municipalities"""

    # list of States codes in Brazil
    states_codes = pd.read_csv('input/STATES_ID_NUM.csv', sep=';', header=0, decimal=',')

    # creating a list of code number for each state to use in municipalities selection
    processing_states_code_list = []
    for item in geo.states_on_process:
        processing_states_code_list.append((states_codes['nummun'].loc[states_codes['codmun'] == item]).values[0])

    # load the shapefiles
    if geo.year == 2010:
        return prepare_shapes_2010(geo)
    full_region = ogr.Open('input/shapes/mun_ACPS_ibge_2014_latlong_wgs1984_fixed.shp')
    urban_region = ogr.Open('input/shapes/URBAN_IBGE_ACPs.shp')
    aps_region = ogr.Open('input/shapes/APs.shp')

    urban = []
    urban_mun_codes = []
    # selecting the urban areas for each municipality
    for state in processing_states_code_list:
        for acp in geo.processing_acps:
            # for all states different from Federal district (53 code)
            for mun_reg in range(urban_region.GetLayer(0).GetFeatureCount()):
                if urban_region.GetLayer(0).GetFeature(mun_reg).GetField(5) == str(acp) and \
                                urban_region.GetLayer(0).GetFeature(mun_reg).GetField(3) == str(state):
                    urban.append(urban_region.GetLayer(0).GetFeature(mun_reg))
                    urban_mun_codes.append(urban_region.GetLayer(0).GetFeature(mun_reg).GetField(1))

    urban = {
        item.GetField(1): shape(json.loads(item.geometry().ExportToJson()))
        for item in urban
    }

    # map municipal codes to constituent AP shapes
    mun_codes_to_ap_shapes = defaultdict(list)
    for reg in range(aps_region.GetLayer(0).GetFeatureCount()):
        shap = aps_region.GetLayer(0).GetFeature(reg)
        code = shap.GetField(0)
        mun_code = code[:7]
        shap.id = code
        shap.mun_code = mun_code
        mun_codes_to_ap_shapes[mun_code].append(shap)

    my_shapes = []
    # selection of municipalities boundaries
    # running over the states in the list
    for mun_id in urban_mun_codes:
        # for all states different from Federal district (53 code)
        # if we have AP shapes for this municipality, use those
        if mun_id in mun_codes_to_ap_shapes:
            my_shapes.extend(mun_codes_to_ap_shapes[mun_id])
        else:
            for mun_reg in range(full_region.GetLayer(0).GetFeatureCount()):
                if full_region.GetLayer(0).GetFeature(mun_reg).GetField(1) == mun_id:
                    shap = full_region.GetLayer(0).GetFeature(mun_reg)
                    # Make sure FIELD 1 is IBGE CODE
                    shap.id = shap.GetField(1)
                    my_shapes.append(shap)

    return urban, my_shapes
