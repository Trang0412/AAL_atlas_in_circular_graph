from functions import *
from bokeh.palettes import Turbo256
import pandas as pd



color_palette = Turbo256
# Load layout's information for graph
path_analysis = 'X:\\EEG_BCI\\2. Word decoding\\1. Temporal dynamic decoding\\analysis\\'
path_atlas = 'X:\\EEG_BCI\\2. Word decoding\\1. Temporal dynamic decoding\\code\\python\\semantic_processing\\graph_visualization\\'
fname_atlas = 'groupSIFT_atlas.xlsx'

tasks = ['listening', 'imagined', 'overt']
word_sems = ['face', 'number', 'animal']
fwhm = 'fwhm25' # gaussian's fwhm 

# Load customized layout for circular graph
layout_xls = pd.ExcelFile(path_atlas + fname_atlas)
layout_df = pd.read_excel(layout_xls, "for_circular_layout")
layout_xls.close()
layout_df['from_int'] = list(range(len(layout_df))) # add interger index for each regions
layout_df.rename(columns={'Regions': 'from'}, inplace=True) # change name of columns

def main(option=2):

    # Plot network graph for each time window of interested resulted from cluster t-test on scalp data for temporal dynamic decoding
  if option == 1:
    for taski in range(len(tasks)):
      
      path_save = path_analysis + '\\semantic_processing\\'  + tasks[taski] +  '\\figure\\connectivity\\' + fwhm + '\\'

      # Time window to check depends on task
      if taski==0:
        time_wins = [ [106, 133], [196, 231], [352, 407], [458, 485] ]
      elif taski == 1:
        time_wins = [ [63, 134], [173, 243], [274, 325], [446, 477], [580, 657] ]
      else:  
        time_wins = [ [137, 177], [189, 216], [240, 302], [384, 497], [560, 689] ]
    
      for semi in range(len(word_sems)):
        # Load connectivity file
        path_conn = path_analysis + 'semantic_processing\\'  + tasks[taski] +  '\\groupSIFT\\onlySingleDipole\\' + word_sems[semi] + '\\' + fwhm +'\\'
        fname_conn = 'Conn_for_graph.xlsx'
        conn_file = pd.ExcelFile(path_conn + fname_conn)

        for timei in range(len(time_wins)):
          # title for graph and file to be saved
          plot_title = tasks[taski] + ': ' + word_sems[semi] + ', ' + str(time_wins[timei][0]) + '-' + str(time_wins[timei][1]) + ' ms' 
          plot_fname = tasks[taski] + '_' + word_sems[semi] + '_' + str(time_wins[timei][0]) + '_' + str(time_wins[timei][1]) + '_ms.html' 
          conn_df = pd.read_excel(conn_file, "time_win_" + str(timei+1))
          conn_df.dropna(inplace=True)
          plot_conn_graph(layout_df, conn_df, path_save, plot_fname, plot_title, color_palette)

        # close the connectivity file for the current semantic group
        conn_file.close()
        del path_conn

  else: 
    #% Plot network graph all time data generated from groupSIFT as individual*.xlsx file 
    for taski in range(len(tasks)):
      path_save = path_analysis + '\\semantic_processing\\'  + tasks[taski] +  '\\figure\\connectivity\\' + fwhm + '\\'

      for semi in range(len(word_sems)):       
        path_conn = path_analysis + 'semantic_processing\\'  + tasks[taski] +  '\\groupSIFT\\onlySingleDipole\\' + word_sems[semi] + '\\' + fwhm + '\\'
        fname_conn = 'individualSubjectConnectivity_useGFWER.xlsx'
        conn_file = pd.ExcelFile(path_conn + fname_conn)
        plot_title = tasks[taski] + ': ' + word_sems[semi] + 'all time' 
        plot_fname = tasks[taski] + '_' + word_sems[semi] + '_all_time.html' 
        conn_df = pd.read_excel(conn_file, "connectivity")
        conn_df.dropna(inplace=True)
        plot_conn_graph(layout_df, conn_df, path_save, plot_fname, plot_title, color_palette)
        conn_file.close()
        del path_conn

    
if __name__ == "__main__":
    main(option=2)
