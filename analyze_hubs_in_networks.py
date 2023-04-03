"""
Created on Mon, 2023 Mar 27 
"""

#%%

import os
import sys
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings(action='ignore', category=FutureWarning) # setting ignore as a parameter and further adding category
from itertools import chain


tasks = ['listening', 'imagined']
path_analysis = 'X:\\EEG_BCI\\2. Word decoding\\1. Temporal dynamic decoding\\analysis\\'
IC_chosen_scheme = 'brain_ICs_with_rv'

#% Load layout's information for graph
path_atlas = 'X:\\EEG_BCI\\2. Word decoding\\1. Temporal dynamic decoding\\code\\python\\semantic_processing\\graph_visualization\\'
fname_atlas = 'groupSIFT_atlas.xlsx'
layout_xls = pd.ExcelFile(path_atlas+ fname_atlas)
layout_df = pd.read_excel(layout_xls, "for_circular_layout")
layout_df.rename(columns={'Name': 'from'}, inplace=True) # change name of columns
layout_xls.close()
layout_df['from_int'] = list(range(len(layout_df))) # add interger index for each regions
layout_df.dropna(inplace=True)


#%%
# CHECK THE MEAN AND STD COMPUTATION AGAIN
semantic_groups = ['face', 'number', 'animal']
degree_listening = pd.read_excel(path_analysis + 'semantic_processing\\listening\\groupSIFT\\' + IC_chosen_scheme + '\\all_time_nodes_degree_listening.xlsx')
degree_imagined = pd.read_excel(path_analysis + 'semantic_processing\\imagined\\groupSIFT\\' + IC_chosen_scheme + '\\all_time_nodes_degree_imagined.xlsx')

path_save = path_analysis + 'semantic_processing\\' 
fname_hub_excel = 'groupSIFT_connectivity_hub.xlsx'
hemisphere_order = [np.arange(19,57,1), np.arange(0,19,1)[::-1], np.arange(57,76,1)[::-1]]
hemisphere_order = list(chain(*hemisphere_order))
hemisphere_order = hemisphere_order[::-1]


with pd.ExcelWriter(path_save + fname_hub_excel) as writer:           
    for semi in range(len(semantic_groups)): 

        # dataframe with indexes are 'mean', 'std' for deciding hub for each semantic group in each task
        hub_description_df = pd.DataFrame( list(zip(degree_listening[semantic_groups[semi]].describe(), degree_imagined[semantic_groups[semi]].describe())),
                                                    columns=tasks, index=list(degree_listening[semantic_groups[semi]].describe().index))
        
        hub_index = []
        hub_index.extend( degree_listening[semantic_groups[semi]].index[[ 
            degree_listening[semantic_groups[semi]]>=degree_listening[semantic_groups[semi]].values.mean() + 
            degree_listening[semantic_groups[semi]].values.std() ]])
        
        hub_index.extend( degree_imagined[semantic_groups[semi]].index[[ 
            degree_imagined[semantic_groups[semi]]>=degree_imagined[semantic_groups[semi]].values.mean() + 
            degree_imagined[semantic_groups[semi]].values.std() ]])

        hub_index = list(set(hub_index))
        temp = [hemisphere_order.index(hubi) for hubi in list(set(hub_index))] # sort hub according to hemispere and from frontal to occipital
        temp.sort() # sort hub index according to hemispere and from frontal to occipital
        hub_index = [hemisphere_order[i] for i in temp]
        hub_degree_listening = [ degree_listening[semantic_groups[semi]][i] for i in hub_index ]
        hub_degree_imagined = [ degree_imagined[semantic_groups[semi]][i] for i in hub_index ]    

        # dataframe with index are hubs' name, 2 columns (listening and imagined) of degree values corresponding to each hub in task 
        hub_df = pd.DataFrame( list(zip(hub_degree_listening, hub_degree_imagined)), columns=tasks, index=layout_df['abb'][hub_index])
        hub_df.to_excel(writer, sheet_name = semantic_groups[semi])


        hub_description_df.to_excel(writer, sheet_name = semantic_groups[semi] + '_description')
        del temp
        del hub_df
        del hub_description_df






# %%
