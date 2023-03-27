"""
Created on Tue, 2022 Dec 28 

  - Visualize nodes and labels using Bokeh and Networkx in circular layout for adjust x_offset and y_offset
for each node's label manually

  Requirements: 
    - layout_df for circular layout

@author: TrangLT, CNE, UoU
          2022.12.28: Make functions more readable
       
"""
#%% Import all required packages
import pandas as pd
from bokeh.io import output_notebook, show, save
output_notebook()
import networkx
import numpy as np
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, LinearColorMapper, LabelSet, Label
from bokeh.plotting import figure
from bokeh.plotting import from_networkx
from bokeh.palettes import Blues8, RdYlBu, Turbo256
color_palette = Turbo256
# Load layout's information for graph
path_atlas = 'X:\\EEG_BCI\\2. Word decoding\\1. Temporal dynamic decoding\\code\\python\\semantic_processing\\graph_visualization\\'
fname = 'groupSIFT_atlas.xlsx'
xls = pd.ExcelFile(path_atlas + fname)
layout_df = pd.read_excel(xls, "for_circular_layout")
# layout_df = pd.read_excel(xls, "language_network")
xls.close()
layout_df['from_int'] = list(range(len(layout_df))) # add interger index for each regions
layout_df.rename(columns={'Name': 'from'}, inplace=True) # change name of columns
G = networkx.OrderedDiGraph()
G.add_nodes_from(np.arange(len(layout_df)))
network_graph = from_networkx(G, networkx.circular_layout, scale=10, center=(0, 0))

nodes_index = network_graph.node_renderer.data_source.data['index']
x,y = zip(*network_graph.layout_provider.graph_layout.values()) # get coordinate for each node as anchor for node's label
angle_step = 4.5 # distance in angle (degree) between 2 labels
labels_angles = np.linspace(0,360-angle_step, len(layout_df))
inter_index = [np.where(labels_angles>90)[0][0],np.where(labels_angles<=270)[0][-1]]
labels_angles[inter_index[0]:inter_index[1]] = labels_angles[inter_index[0]:inter_index[1]] +180
# for checking label position for each node
plot = figure(tools="pan,save,reset, wheel_zoom", active_scroll='wheel_zoom',
            x_range=Range1d(-15.1, 15.1), y_range=Range1d(-15.1, 15.1))
plot.renderers.append(network_graph)
node_labels = layout_df['from']
for i in list(range(76)):
  label = Label(x=x[i], y=y[i], text=node_labels[i], 
  x_offset=layout_df['x_offset'].values[i],
  y_offset=layout_df['y_offset'].values[i],
  angle=labels_angles[i], angle_units='deg',
  text_font_size='10px', text_font_style='bold', 
  background_fill_color='white', background_fill_alpha=.7) 
  plot.renderers.append(label)

show(plot)
# %%