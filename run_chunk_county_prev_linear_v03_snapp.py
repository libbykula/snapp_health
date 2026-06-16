import sys
import pandas as pd
import geopandas as gpd
import gep_hypertension_linear_county_prev_v05_snapp
import os
import snapp_public_ndvi_v02

base_dir = '/users/3/kula0049/Files/base_data'
country_label = 'usa'
county_geoids = sys.argv[1].split(",")

prev_data = pd.read_csv(os.path.join(base_dir, 'Price_Prevalence/ht prevalence who 2021.csv'))
age_data = pd.read_csv(os.path.join(base_dir, 'Age/IDB_02-18-2026.csv'))

# Prepping age -- do I need to merge in iso3 labels?
age_data = age_data[age_data['GROUP'].notna()]

ee_r264 = gpd.read_file(os.path.join(base_dir, 'cartographic/ee/ee_r264_correspondence.gpkg'))

age_data = pd.merge(age_data, ee_r264,
                    how = 'left', left_on='Country/Area Name', 
                    right_on='iso3_r250_name')

# print(age_data['iso3_r250_name'].unique())
age_data = age_data[age_data['GROUP'] != '']
age_data = age_data[age_data['iso3_r250_label'].str.lower()==country_label]

age_data['GROUP_NUM'] = (
    age_data['GROUP']
    .replace({'100+': 100})
)
age_data['GROUP_NUM'] = pd.to_numeric(age_data['GROUP_NUM'], errors='coerce')
age_data['Population'] = pd.to_numeric(
    age_data['Population'].astype(str).str.replace(',', '', regex=False).str.strip(),
    errors='coerce'
)

total_pop = age_data['Population'].sum()

pop_30_79 = age_data.loc[age_data['GROUP_NUM'].between(30, 79),
    'Population'
].sum()

perc_adults = pop_30_79 / total_pop

scenarios = ['public', 'private']

for county_geoid in county_geoids:

    try:
        snapp_public_ndvi_v02.reclassify_raster(county_geoid)
    except Exception as e:
        print('FAILED', county_geoid, e)

    for scen in scenarios:
        try:
            gep_hypertension_linear_county_prev_v05_snapp.get_hypertension_gep(county_geoid, perc_adults, scen)
        except Exception as e:
            print("FAILED", county_geoid, e)
                
        del_path = os.path.join(base_dir, 'NDVI/ndvi_2019_ave_scaled_' + scen + '_' + county_geoid + '.tiff')
        if os.path.exists(del_path):
            os.remove(del_path)
            
    print('Done with ', county_geoid)

        