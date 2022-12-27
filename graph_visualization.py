"""

Created on Tue, 2022 Dec 17 



  - Visualize effective connectivity using Bokeh and Networkx in circular layout
  - Node size was adjusted using degree value computed using Networkx
  - Regions in same lobe were coded in same color using Turbo256 color palette 
  - Edges width changes corresponding to weight of connection between 2 nodes
  - Only nodes which have connection to other nodes have label accompanied.
  - Make arc edges instead of line edges with color indicates the direction of connection


  Requirements: 
    - Data for connectivity were generated from the file code 'g_extract_conn_information_for_custom_visualization.mat'

    - Connectivity information saved in excel file with 3 columns: 
            1. from      (node's name, string)
            2. to        (node's name, string)
            3. weights   (edges' weight, float)


@author: TrangLT, CNE, UoU
         
"""


#%% Import all required packages
import os
# output_notebook()
import pandas as pd
import networkx
import numpy as np

from bokeh.io import output_notebook, show, save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, LinearColorMapper, Label, ColorBar
from bokeh.plotting import figure, from_networkx, output_file, save
from bokeh.palettes import  Turbo256, Greys256, Inferno256, Viridis256
from bokeh.transform import linear_cmap


color_palette = Turbo256

#%%
# Load layout's information for graph
path_analysis = 'X:\\EEG_BCI\\2. Word decoding\\1. Temporal dynamic decoding\\analysis\\'
path_atlas = 'X:\\EEG_BCI\\2. Word decoding\\1. Temporal dynamic decoding\\analysis\\'
fname_atlas = 'groupSIFT_atlas.xlsx'

tasks = ['listening', 'imagined', 'overt']
word_sems = ['face', 'number', 'animal']
fwhm = 'fwhm20' # gaussian's fwhm 

# Load customized layout for circular graph
layout_xls = pd.ExcelFile(path_atlas + fname_atlas)
layout_df = pd.read_excel(layout_xls, "for_circular_layout")
layout_xls.close()
layout_df['from_int'] = list(range(len(layout_df))) # add interger index for each regions
layout_df.rename(columns={'Regions': 'from'}, inplace=True) # change name of columns

#%%
for taski in range(len(tasks)):

  # Time window to check depends on task
  if taski==0:
    time_wins = [ [106, 133], [196, 231], [352, 407], [458, 485] ]
  elif taski == 1:
    time_wins = [ [63, 134], [173, 243], [274, 325], [446, 477], [580, 657] ]
  else:  
    time_wins = [ [137, 177], [189, 216], [240, 302], [384, 497], [560, 689] ]
  
  path_save = path_analysis + '\\semantic_processing\\'  + tasks[taski] +  '\\figure\\connectivity\\' + fwhm + '\\'

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

      #%% Morph connectivity information into atlas dataframe and create graph
      graph_df = layout_df.join(conn_df.set_index('from'), on='from')

      # add integer index for compatible with Bokeh
      # which regions do not have connection to other regions will have the value of field 'to' equals to its value of 'from_int'
      # in other words, regions which do not have connection to other regions then it has connection to itself
      to_int = graph_df['to'].values.copy()
      for i in range(len(to_int)):
          if pd.isna(to_int[i]) == False:
              to_int[i] = layout_df.set_index('from').loc[to_int[i]]['from_int']
          else:
              to_int[i] = graph_df.set_index('from').iloc[i]['from_int']
      graph_df['to'] = to_int

      G = networkx.OrderedDiGraph()
      G.add_nodes_from(np.arange(len(layout_df)))
      G.add_edges_from((u,v) for (u,v) in zip(graph_df['from_int'].values, graph_df['to'].values))
      for edge_i in range(len(graph_df)):
        edge_info = graph_df[['from_int', 'to', 'weights']].iloc[edge_i]
        G.add_weighted_edges_from( [( edge_info[0],edge_info[1],edge_info[2] )])

      plot = figure(tools="pan,reset, wheel_zoom", active_scroll='wheel_zoom',
            x_range=Range1d(-15.1, 15.1), y_range=Range1d(-15.1, 15.1), title=plot_title)

      # turn off grid
      plot.xgrid.grid_line_color = None
      plot.ygrid.grid_line_color = None

      #%% Adjust appearance of node and edges
      degrees_ori = dict(networkx.degree(G))
      degrees = dict([ (key, value*20) for key, value in degrees_ori.items()])
      networkx.set_node_attributes(G, name='degree', values=degrees)

      number_to_adjust_by = 10
      adjusted_node_size = dict([(node, degree+number_to_adjust_by) for node, degree in networkx.degree(G)])
      networkx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)

      # Adjust color according to regions
      adjusted_node_color = dict(zip(layout_df['from_int'], layout_df['color_index']*10))
      networkx.set_node_attributes(G, name='adjusted_node_color', values=adjusted_node_color)

      color_by_this_attribute = 'adjusted_node_color'
      size_by_this_attribute = 'adjusted_node_size'

      network_graph = from_networkx(G, networkx.circular_layout, scale=10, center=(0, 0))
      minimum_value_color = min(network_graph.node_renderer.data_source.data[color_by_this_attribute])
      maximum_value_color = max(network_graph.node_renderer.data_source.data[color_by_this_attribute])
      network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute,
      fill_color = linear_cmap(color_by_this_attribute, color_palette, minimum_value_color, maximum_value_color))


      plot.renderers.append(network_graph)

      #%% Adjust edge appearance with width and color corresponding to weight and direction of connection respectively

      # Assign emtpy edge_with for edge to shut down the default straight edges
      edge_width = []
      network_graph.edge_renderer.data_source.data['edge_width'] = edge_width 

      # make a curved plot between 2 nodes
      def bezier(start, end, control, steps):
        return [(1-s)**2*start + 2*(1-s)*s*control + s**2*end for s in steps]

      # get coordinate for each node to generate curve between 2 nodes
      x,y = zip(*network_graph.layout_provider.graph_layout.values()) 
      steps = [i/100. for i in range(100)]
      color_mapper = list(color_palette)[::2][:99]
      color_bar = ColorBar(color_mapper=LinearColorMapper(palette=tuple(color_mapper)))

      def create_renderers(x, y, start_node, end_node, weight, color_mapper):
          # generate data for bezier curve from start_node to end_node
          xs1 = np.array(bezier(x[start_node], x[end_node], 0, steps))   
          ys1 = np.array(bezier(y[start_node], y[end_node], 0, steps))

          # make multiple segments for the bezier curve to faciliate multiple color for the MultiLine
          xs = [xs1[i-1:i+1] for i in range(1, len(xs1))] 
          ys = [ys1[i-1:i+1] for i in range(1, len(ys1))]
        
          data_source = ColumnDataSource(dict(
              xs = xs,
              ys = ys,
              color_mapper = color_mapper))

          glyph = MultiLine(xs="xs", ys="ys", 
                            line_color='color_mapper', 
                            line_width=weight)

          return data_source, glyph, color_mapper

      # for normalizing edge weight to z-score for visualization
      conn_weight_mean = conn_df['weights'].mean()
      conn_weight_std = conn_df['weights'].std()
      for start_node, end_node,_ in G.edges(data=True):  
        if start_node == end_node:
          continue
        conn_weigth = G[start_node][end_node]['weight']
        edge_width = ( (conn_weigth-conn_weight_mean)/conn_weight_std + 2 if np.isnan(conn_weigth)==False else conn_weigth ) 
        ds1, line1, cmap = create_renderers(x, y, start_node, end_node, edge_width, color_mapper)
        plot.add_glyph(ds1, line1)

      # plot.add_layout(color_bar, 'right')

      #%% Add labels and adjust x_offset and y_offset for label according to each node's position
      centroid_df = pd.DataFrame(pd.concat([conn_df['from'], conn_df['to']]).drop_duplicates(inplace=False), columns=["centroids"])
      nodes_index = network_graph.node_renderer.data_source.data['index']

      x,y = zip(*network_graph.layout_provider.graph_layout.values()) # get coordinate for each node as anchor for node's label
      angle_step = 4.5 # distance in angle (degree) between 2 labels
      labels_angles = np.linspace(0,360-angle_step, len(layout_df))
      inter_index = [np.where(labels_angles>90)[0][0],np.where(labels_angles<=270)[0][-1]]
      labels_angles[inter_index[0]:inter_index[1]] = labels_angles[inter_index[0]:inter_index[1]] +180

      # only show labels for nodes that have connection to other nodes
      node_labels=[]
      for i in nodes_index:
        if layout_df.loc[i]['from'] in centroid_df['centroids'].values:
          node_labels.append(layout_df.loc[i]['from'])
        else:
          node_labels.append('')

      # node_labels = layout_df['from']
      for i in range(len(x)):
        label = Label(x=x[i], y=y[i], text=node_labels[i], 
        x_offset=layout_df['x_offset'].values[i], 
        y_offset=layout_df['y_offset'].values[i], 
        angle=labels_angles[i], angle_units='deg',
        background_fill_color=None, 
        text_font_size='10px', text_font_style='bold') 
        plot.renderers.append(label)


      # #%%
      # # for checking label position for each node
      # node_labels = layout_df['from']
      # for i in [20]:
      #   label = Label(x=x[i], y=y[i], text=node_labels[i], 
      #   x_offset=-15,
      #   y_offset=135,
      #   angle=labels_angles[i], angle_units='deg',
      #   background_fill_color='white', background_fill_alpha=.7,
      #   text_font_size='10px',text_font_style='bold') 
      #   plot.renderers.append(label)

      # show(plot)
      output_file(filename=path_save +plot_fname, title=plot_title)
      save(plot)

    # close the connectivity file for the current semantic group
    conn_file.close()
  del path_conn
      # %%