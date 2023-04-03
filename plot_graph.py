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
color_palette_edge = Inferno256

tasks = ['listening', 'imagined']
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
layout_df.rename(columns={'Name': 'from'}, inplace=True) # change name of columns

# language_df = pd.read_excel(layout_xls, "language_network") # plot only regions in language network
language_df = pd.read_excel(layout_xls, "for_circular_layout") # plot all connections
language_df.rename(columns={'Name': 'name'}, inplace=True) # change name of columns
language_df['from_int'] = list(range(len(language_df))) # add interger index for each regions
language_df.dropna(inplace=True)

layout_xls.close()
layout_df['from_int'] = list(range(len(layout_df))) # add interger index for each regions
layout_df.dropna(inplace=True)


#%% define functions here
def main_sem(option, IC_chosen_scheme, labels_option):

    # Plot network graph for each time window of interested resulted from cluster t-test on scalp data for temporal dynamic decoding
  if option == 1:
    for taski in range(len(tasks)):
      
      # path to save figures
      path_save_fifgure = path_analysis + '\\semantic_processing\\'  + tasks[taski] +  '\\figure\\connectivity\\' + IC_chosen_scheme + '\\'
      path_save_degree = path_analysis + 'semantic_processing\\'  + tasks[taski] +  '\\groupSIFT\\' + IC_chosen_scheme + '\\' 
      # Time window to check depends on task
      if taski==0:
        time_wins = [ [106, 133], [196, 231], [352, 407], [458, 485] ]
      elif taski == 1:
        time_wins = [ [63, 134], [173, 243], [274, 325], [446, 477], [580, 657] ]
      else:  
        time_wins = [ [137, 177], [189, 216], [240, 302], [384, 497], [560, 689] ]
    
      for semi in range(len(word_sems)):
        # Load connectivity file
        path_conn = path_analysis + 'semantic_processing\\'  + tasks[taski] +  '\\groupSIFT\\' +IC_chosen_scheme + '\\' + word_sems[semi] + '\\' + fwhm + '\\'
        fname_conn = 'Conn_for_graph.xlsx'
        conn_file = pd.ExcelFile(path_conn + fname_conn)

        fname_degree = 'time_win_nodes_degree_' + word_sems[semi] + '.xlsx'
        with pd.ExcelWriter(path_conn + fname_degree) as writer:
          
          for timei in range(len(time_wins)):
            # title for graph and file to be saved
            plot_title = tasks[taski] + ': ' + IC_chosen_scheme + word_sems[semi] + ', ' + str(time_wins[timei][0]) + '-' + str(time_wins[timei][1]) + ' ms' 

            if labels_option == 0:
              plot_fname =   tasks[taski] + '_' + IC_chosen_scheme +  word_sems[semi] + '_' + str(time_wins[timei][0]) + '_' + str(time_wins[timei][1]) +  '_ms_turn_off_labels.html' 
            else:
              plot_fname = tasks[taski] + '_' + IC_chosen_scheme +  word_sems[semi] + '_' + str(time_wins[timei][0]) + '_' + str(time_wins[timei][1]) + '_ms.html' 
  
            conn_df = pd.read_excel(conn_file, "time_win_" + str(timei+1))
            conn_df.dropna(inplace=True)
            _, nodes_degree = plot_conn_graph(layout_df, conn_df, language_df, labels_option, path_save_fifgure, plot_fname, plot_title, color_palette)

            # save the degree for each time window
            nodes_degree = dict(zip(layout_df['from'], nodes_degree.values()))
            saved_df = pd.DataFrame.from_dict(nodes_degree, orient = 'index', columns=['weight'])
            saved_df.to_excel(writer, sheet_name = 'timewin_' + str(timei))
            del saved_df

        # close the connectivity file for the current semantic group
        conn_file.close()

        del path_conn

  else: 
    #% Plot network graph all time data generated from groupSIFT as individual*.xlsx file 
    for taski in range(len(tasks)):
      # path to save figures
      path_save = path_analysis + '\\semantic_processing\\'  + tasks[taski] +  '\\figure\\connectivity\\' + IC_chosen_scheme + '\\'
      path_save_degree = path_analysis + 'semantic_processing\\'  + tasks[taski] +  '\\groupSIFT\\' + IC_chosen_scheme + '\\'       
      fname_degree = 'all_time_nodes_degree_' + tasks[taski] + '.xlsx'
      
      with pd.ExcelWriter(path_save_degree + fname_degree) as writer:
        for semi in range(len(word_sems)):       
          path_conn = path_analysis + 'semantic_processing\\'  + tasks[taski] +  '\\groupSIFT\\' + IC_chosen_scheme+'\\' + word_sems[semi] + '\\' + fwhm + '\\'
          fname_conn = 'individualSubjectConnectivity.xlsx'
          conn_file = pd.ExcelFile(path_conn + fname_conn)
          plot_title =  tasks[taski] + ': '+ IC_chosen_scheme + word_sems[semi] + ' all time' 
          if labels_option == 0:
            plot_fname =  tasks[taski] + '_' + IC_chosen_scheme + '_' + word_sems[semi] + '_all_time_turn_off_labels.html' 
          else:
            plot_fname =  tasks[taski] + '_' +  IC_chosen_scheme + '_' + word_sems[semi] + '_all_time.html' 

          conn_df = pd.read_excel(conn_file, "connectivity")
          conn_df.dropna(inplace=True)
          _, nodes_degree = plot_conn_graph(layout_df, conn_df, language_df, labels_option, path_save, plot_fname, plot_title, color_palette)
          # plot_conn_graph_language_net(layout_df, conn_df, path_save, plot_fname, plot_title, color_palette)
          conn_file.close()
          # save the degree 
          nodes_degree = dict(zip(layout_df['from'], nodes_degree.values()))
          saved_df = pd.DataFrame.from_dict(nodes_degree, orient = 'index', columns=['weight'])
          # saved_df = saved_df.transpose()
          saved_df.to_excel(writer, sheet_name = word_sems[semi])
          del saved_df
          
          del path_conn

    

def main_task(option, IC_chosen_scheme, labels_option):

  # Plot network graph for each time window of interested resulted from cluster t-test on scalp data for temporal dynamic decoding
  if option == 1:
    for taski in range(len(tasks)):
      # Time window to check depends on task
      if taski==0:
        time_wins = [ [106, 133], [196, 231], [352, 407], [458, 485] ]
      elif taski == 1:
        time_wins = [ [63, 134], [173, 243], [274, 325], [446, 477]]
      else:  
        time_wins = [ [137, 177], [189, 216], [240, 302], [384, 497]]
  

      # path to save figures
      path_save_figure = path_analysis + 'task_processing\\' + '\\figure\\' + tasks[taski]  + '\\connectivity\\' 

      # Load connectivity file
      # path_conn = path_analysis + 'semantic_processing\\'  + tasks[taski] +  '\\groupSIFT\\onlySingleDipole\\' + word_sems[semi] + '\\' + fwhm + '\\p_' + str(p_value) + '\\'
      path_conn = path_analysis + 'task_processing\\groupSIFT\\' + tasks[taski] +  '\\' + IC_chosen_scheme +'\\' 
      fname_conn = 'Conn_for_graph.xlsx'
      conn_file = pd.ExcelFile(path_conn + fname_conn)    

      path_save_degree = path_analysis + 'task_processing\\groupSIFT\\' + tasks[taski] + '\\'  
      fname_degree = 'time_win_nodes_degree_' + IC_chosen_scheme + '.xlsx'
      with pd.ExcelWriter(path_save_degree + fname_degree) as writer:
        for timei in range(len(time_wins)):
          # title for graph and file to be saved
          plot_title = tasks[taski] + IC_chosen_scheme + ': ' +  str(time_wins[timei][0]) + '-' + str(time_wins[timei][1]) + ' ms' 
          if labels_option == 0:
            plot_fname = tasks[taski] + IC_chosen_scheme + str(time_wins[timei][0]) + '_' + str(time_wins[timei][1]) + '_ms_turn_off_labels.html' 
          else:
            plot_fname = tasks[taski] + IC_chosen_scheme + str(time_wins[timei][0]) + '_' + str(time_wins[timei][1]) + '_ms.html' 
          conn_df = pd.read_excel(conn_file, "time_win_" + str(timei+1))
          conn_df.dropna(inplace=True)
          _, nodes_degree = plot_conn_graph(layout_df, conn_df, language_df, labels_option, path_save_figure, plot_fname, plot_title, color_palette)

          # save the degree 
          nodes_degree = dict(zip(layout_df['from'], nodes_degree.values()))
          saved_df = pd.DataFrame.from_dict(nodes_degree, orient = 'index', columns=['weight'])
          # saved_df = saved_df.transpose()
          saved_df.to_excel(writer, sheet_name = 'timewin_' + str(timei))
          del saved_df
          del nodes_degree

      # close the connectivity file for the current semantic group
      conn_file.close()

      
      del path_conn
#%%
  else: 
    #% Plot network graph all time data generated from groupSIFT as individual*.xlsx file 
    path_save_degree = path_analysis + 'task_processing\\groupSIFT\\' 
    fname_degree = 'all_time_nodes_degree_' + IC_chosen_scheme + '.xlsx'
    with pd.ExcelWriter(path_save_degree + fname_degree) as writer:
      for taski in range(len(tasks)):
        #% path to save figures
        path_save_figure = path_analysis + 'task_processing\\' + '\\figure\\' + tasks[taski]  + '\\connectivity\\' 

        path_conn = path_analysis + 'task_processing\\groupSIFT\\' + tasks[taski] +  '\\' + IC_chosen_scheme + '\\' 
        fname_conn = 'individualSubjectConnectivity.xlsx'
        conn_file = pd.ExcelFile(path_conn + fname_conn)
        plot_title = tasks[taski] + IC_chosen_scheme
        if labels_option == 0:
          plot_fname = tasks[taski] + IC_chosen_scheme + '_all_time_turn_off_labels.html' 
        else:
          plot_fname = tasks[taski] + IC_chosen_scheme + '_all_time.html' 
        conn_df = pd.read_excel(conn_file, "connectivity")
        conn_df.dropna(inplace=True)
        _, nodes_degree = plot_conn_graph(layout_df, conn_df, language_df, labels_option,  path_save_figure, plot_fname, plot_title, color_palette)

        conn_file.close()
        # save the degree        
        nodes_degree = dict(zip(layout_df['from'], nodes_degree.values()))
        saved_df = pd.DataFrame.from_dict(nodes_degree, orient = 'index', columns=['weight'])
        saved_df.to_excel(writer, sheet_name = tasks[taski])
        del saved_df
        del nodes_degree

        del path_conn




#%% Run funtion
if __name__ == "__main__":
    IC_chosen_scheme = 'brain_ICs_with_rv'
    main_task(2, IC_chosen_scheme, 1)
    main_sem(2, IC_chosen_scheme, 1)
