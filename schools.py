import pandas as pd
from sodapy import Socrata
import matplotlib.pyplot as plt

client = Socrata("data.cityofnewyork.us", "ghD7sxmh9I7Ud8yq8Au5YKort", timeout=1000)
map_results = client.get("755u-8jsi", where="borough='Manhattan'", select='borough, zone, location_id', limit=1000)
manhattan_zones = pd.DataFrame.from_records(map_results)
print(manhattan_zones)

school_locations = pd.read_csv(
    filepath_or_buffer="C:\\Users\\lahat\\Documents\\Uni\\Year3\\IntrotoDS\\final_project\\2017_"
                       "-_2018_School_Locations.csv",
    index_col=False, header=0, usecols=[1, 3, 7, 22, 38])
school_locations['ATS SYSTEM CODE'] = school_locations['ATS SYSTEM CODE'].str.strip()
school_locations['NTA_NAME'] = school_locations['NTA_NAME'].str.strip()
print(school_locations['NTA_NAME'].array.unique())

quality_report = pd.read_csv(
    filepath_or_buffer="C:\\Users\\lahat\\Documents\\Uni\\Year3\\IntrotoDS\\final_project\\2017"
                       "-2018_School_Quality_Reports_-_Elem__Middle___K-8.csv",
    index_col=False, header=0, usecols=[0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])

school_loc_qual = quality_report.merge(right=school_locations, left_on='DBN', right_on='ATS SYSTEM CODE', how='inner')
print(school_loc_qual.columns)

# TODO some names appear but sort of differently!
manhattan_schools = school_loc_qual[school_loc_qual['NTA_NAME'].isin(manhattan_zones['zone'].array)]

# Choose quality column to check by
schools_by_zone = manhattan_schools.groupby(by=['NTA_NAME'], as_index=False)[
    ['Rigorous Instruction - Percent Positive', 'Collaborative Teachers - Percent Positive',
     'Supportive Environment - Percent Positive', 'Effective School Leadership - Percent Positive',
     'Strong Family-Community Ties - Percent Positive', 'Trust - Percent Positive']].mean()
print(schools_by_zone)

ax = schools_by_zone.plot.bar(x=0, stacked=True)
#plt.show()

