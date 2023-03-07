"""

Created on Tue, 2022 Dec 27 


  - Visualize effective connectivity using Bokeh and Networkx in circular layout
  - Node size was adjusted using degree value computed using Networkx
  - Regions in same lobe were coded in same color using Turbo256 color palette 
  - Edges width changes corresponding to weight of connection between 2 nodes
  - Only nodes which have connection to other nodes have label accompanied.
  - Make arc edges instead of line edges with color indicates the direction of connection


  REQUIREMENTS: 
    - Data for connectivity were generated from the file code 'g_extract_conn_information_for_custom_visualization.mat'

    - Connectivity information saved in excel file with 3 columns: 
            1. from      (node's name, string)
            2. to        (node's name, string)
            3. weights   (edges' weight, float)

  HOW TO USE THIS FUNCTION
    - Chnange parameters 'option' depends on whether connectivity information for each time window (1) or for all time (2) is generated.


@author: TrangLT, CNE, UoU
          2022.12.27: Make functions more readable

         
"""
#%%
from functions import *
from bokeh.palettes import Turbo256
import pandas as pd

color_palette = Turbo256

tasks = ['listening', 'imagined', 'overt']
# tasks = [ 'overt']
word_sems = ['face', 'number', 'animal']
fwhm = 'fwhm25' # gaussian's fwhm 
p_value = 0.05

# Load layout's information for graph
path_analysis = 'X:\\EEG_BCI\\2. Word decoding\\1. Temporal dynamic decoding\\analysis\\'
path_atlas = 'X:\\EEG_BCI\\2. Word decoding\\1. Temporal dynamic decoding\\code\\python\\semantic_processing\\graph_visualization\\'
fname_atlas = 'groupSIFT_atlas.xlsx'

layout_xls = pd.ExcelFile(path_atlas + fname_atlas)

layout_df = pd.read_excel(layout_xls, "for_circular_layout")
layout_df.rename(columns={'Regions': 'from'}, inplace=True) # change name of columns

language_df = pd.read_excel(layout_xls, "language_network") # plot only regions in language network
language_df.rename(columns={'Name': 'name'}, inplace=True) # change name of columns
language_df['from_int'] = list(range(len(language_df))) # add interger index for each regions
language_df.dropna(inplace=True)

layout_xls.close()
layout_df['from_int'] = list(range(len(layout_df))) # add interger index for each regions
layout_df.dropna(inplace=True)


#%% define functions here
def main_sem(option=2):

    # Plot network graph for each time window of interested resulted from cluster t-test on scalp data for temporal dynamic decoding
  if option == 1:
    for taski in range(len(tasks)):
      
      # path to save figures
      path_save = path_analysis + '\\semantic_processing\\'  + tasks[taski] +  '\\figure\\connectivity\\all_ICs\\' + fwhm + '\\p_' + str(p_value) + '\\'
      # path_save = path_analysis + '\\semantic_processing\\'  + tasks[taski] +  '\\figure\\connectivity\\' + 'rv_lessthan_0.15' + '\\'

      # Time window to check depends on task
      if taski==0:
        time_wins = [ [106, 133], [196, 231], [352, 407], [458, 485] ]
      elif taski == 1:
        time_wins = [ [63, 134], [173, 243], [274, 325], [446, 477], [580, 657] ]
      else:  
        time_wins = [ [137, 177], [189, 216], [240, 302], [384, 497], [560, 689] ]
    
      for semi in range(len(word_sems)):
        # Load connectivity file
        path_conn = path_analysis + 'semantic_processing\\'  + tasks[taski] +  '\\groupSIFT\\onlySingleDipole_all_ICs\\' + word_sems[semi] + '\\' + fwhm + '\\p_' + str(p_value) + '\\'
        # path_conn = path_analysis + 'semantic_processing\\'  + tasks[taski] +  '\\groupSIFT\\onlySingleDipole_all_ICs\\' + word_sems[semi] + '\\' + fwhm + '\\'
        fname_conn = 'Conn_for_graph.xlsx'
        conn_file = pd.ExcelFile(path_conn + fname_conn)

        for timei in range(len(time_wins)):
          # title for graph and file to be saved
          plot_title = tasks[taski] + ': ' + word_sems[semi] + ', ' + str(time_wins[timei][0]) + '-' + str(time_wins[timei][1]) + ' ms_language_network_' 
          plot_fname = tasks[taski] + '_' + word_sems[semi] + '_' + str(time_wins[timei][0]) + '_' + str(time_wins[timei][1]) + '_ms_language_network_.html' 
          conn_df = pd.read_excel(conn_file, "time_win_" + str(timei+1))
          conn_df.dropna(inplace=True)
          plot_conn_graph(layout_df, conn_df, language_df, path_save, plot_fname, plot_title, color_palette)

        # close the connectivity file for the current semantic group
        conn_file.close()
        del path_conn

  else: 
    #% Plot network graph all time data generated from groupSIFT as individual*.xlsx file 
    for taski in range(len(tasks)):
      # path to save figures
      # path_save = path_analysis + 'semantic_processing\\'  + tasks[taski] +  '\\figure\\connectivity\\' + fwhm + '\\p_' + str(p_value) + '\\'
      path_save = path_analysis + 'semantic_processing\\'  + tasks[taski] +  '\\figure\\connectivity\\all_ICs\\' + fwhm + '\\p_' + str(p_value) + '\\'
      
      for semi in range(len(word_sems)):       
        path_conn = path_analysis + 'semantic_processing\\'  + tasks[taski] +  '\\groupSIFT\\onlySingleDipole_all_ICs\\' + word_sems[semi] + '\\' + fwhm + '\\p_' + str(p_value) + '\\'
        fname_conn = 'individualSubjectConnectivity_useGFWER.xlsx'
        conn_file = pd.ExcelFile(path_conn + fname_conn)
        plot_title = tasks[taski] + ': ' + word_sems[semi] + ' all time language network' 
        plot_fname = tasks[taski] + '_' + word_sems[semi] + '_all_time_language_network.html' 
        conn_df = pd.read_excel(conn_file, "connectivity")
        conn_df.dropna(inplace=True)
        plot_conn_graph(layout_df, conn_df, language_df, path_save, plot_fname, plot_title, color_palette)
        # plot_conn_graph_language_net(layout_df, conn_df, path_save, plot_fname, plot_title, color_palette)
        conn_file.close()
        del path_conn

    

def main_task(option=1):

  # Plot network graph for each time window of interested resulted from cluster t-test on scalp data for temporal dynamic decoding
  if option == 1:
    for taski in range(len(tasks)):
      #%%
      # path to save figures
      path_save = path_analysis + 'task_processing\\' + '\\figure\\' + tasks[taski]  + '\\connectivity\\' 

      # Time window to check depends on task
      if taski==0:
        time_wins = [ [106, 133], [196, 231], [352, 407], [458, 485] ]
      elif taski == 1:
        time_wins = [ [63, 134], [173, 243], [274, 325], [446, 477], [580, 657] ]
      else:  
        time_wins = [ [137, 177], [189, 216], [240, 302], [384, 497], [560, 689] ]
    

      # Load connectivity file
      # path_conn = path_analysis + 'semantic_processing\\'  + tasks[taski] +  '\\groupSIFT\\onlySingleDipole\\' + word_sems[semi] + '\\' + fwhm + '\\p_' + str(p_value) + '\\'
      path_conn = path_analysis + 'task_processing\\groupSIFT\\' + tasks[taski] +  '\\onlySingleDipole_all_ICs\\' 
      fname_conn = 'Conn_for_graph.xlsx'
      conn_file = pd.ExcelFile(path_conn + fname_conn)

      for timei in range(len(time_wins)):
        # title for graph and file to be saved
        plot_title = tasks[taski] + ' all ICs: ' +  str(time_wins[timei][0]) + '-' + str(time_wins[timei][1]) + ' ms' 
        plot_fname = tasks[taski] + '_all_ICs' + str(time_wins[timei][0]) + '_' + str(time_wins[timei][1]) + '_ms.html' 
        conn_df = pd.read_excel(conn_file, "time_win_" + str(timei+1))
        conn_df.dropna(inplace=True)
        plot_conn_graph(layout_df, conn_df, language_df, path_save, plot_fname, plot_title, color_palette)

      # close the connectivity file for the current semantic group
      conn_file.close()
      del path_conn
#%%
  else: 
    #% Plot network graph all time data generated from groupSIFT as individual*.xlsx file 
    for taski in range(len(tasks)):
      #%% path to save figures
      path_save = path_analysis + 'task_processing\\' + '\\figure\\' + tasks[taski]  + '\\connectivity\\' 
        
      path_conn = path_analysis + 'task_processing\\groupSIFT\\' + tasks[taski] +  '\\onlySingleDipole_all_brain_ICs\\' 
      fname_conn = 'individualSubjectConnectivity_0.05.xlsx'
      conn_file = pd.ExcelFile(path_conn + fname_conn)
      plot_title = tasks[taski] + ' all brain ICs' 
      plot_fname = tasks[taski] + '_all_brain_ICs_all_time_language_network.html' 
      conn_df = pd.read_excel(conn_file, "connectivity")
      conn_df.dropna(inplace=True)
      plot_conn_graph(layout_df, conn_df, language_df, path_save, plot_fname, plot_title, color_palette)
      # plot_conn_graph_language_net(layout_df, conn_df, path_save, plot_fname, plot_title, color_palette)
      conn_file.close()
      del path_conn




#%% Run funtion
if __name__ == "__main__":
    # main_task(option=2)
    main_sem(option=1)
