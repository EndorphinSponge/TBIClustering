#%% Installs for colab
# !pip install kneed
# !pip install adjustText


#%% Imports 
# General
from collections import Counter
from math import log
import os

# Data science
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Other
from adjustText import adjust_text


#%%

def roundNum(num, base):
    """
    Rounds a number to a base, will return 1/5 of the base if the number
    is less than half the base (i.e., rounding with min being half of base)
    """
    if num > base/2:
        return base * round(num/base)
    elif num <= base/2 and num > base/5: # Catch cases in between and round up (normally it would round down)
        return base
    else:
        return int(base/5)

class Grapher:

    def __init__(self,):
        self.graph = None
        self.df = None

    def importDF(self, df):
        """
        Takes df with rows representing observations and columns representing factors with 
        each cell having 0 or 1 indicator presence of factor
        """

    def buildGraphFromDF(self, df,):
        """
        Takes df with rows representing observations and columns representing factors with 
        each cell having 0 or 1 indicator presence of factor
        ---
        thresh: lower threshold for number of counts needed for each node (exclusive)
        """
        # Reminder that nx nodes can have abitrary attributes that don't contribute to rendering, need to manually adjust visual parameters with drawing methods
        # nx.Graph is just a way to store data, data can be stored in node attributes         
        self.graph = nx.Graph() # Reset graph
        columns = list(df.columns)
        nodes = {column: df[column].sum() for column in columns if df[column].sum() > 0} # Dict comprehension to get sums of each column
        edges = Counter()
        for index, row in df.iterrows(): # Count edges 
            nodes_row = [] # Store list of nodes in this row # Shouldn't  have any duplicates
            for column in columns:
                if row[column] == 1:
                    nodes_row.append(column)
            for i, node_start in enumerate(nodes_row): # Enumerate used to simulatenously return index for loop
                for j, node_end in enumerate(nodes_row[i+1:]): # To prevent repeating already enumarated nodes
                    edges[(node_start, node_end)] += 1 # Bidirectional connection
                    edges[(node_end, node_start)] += 1
            
        for node in nodes:
            count = nodes[node]
            self.graph.add_node(node, color = "#8338ec", size = count)
        for node1, node2 in edges:
            count = edges[(node1, node2)]
            self.graph.add_edge(node1, node2, width = count)
        print(nx.algorithms.bipartite.spectral_bipartivity(self.graph))
        return None
    def buildGraphFromDFBi(self, df,):
        """
        Takes df with rows representing observations and columns representing factors with 
        each cell having 0 or 1 indicator presence of factor
        ---
        thresh: lower threshold for number of counts needed for each node (exclusive)
        """
        # Reminder that nx nodes can have abitrary attributes that don't contribute to rendering, need to manually adjust visual parameters with drawing methods
        # nx.Graph is just a way to store data, data can be stored in node attributes         
        self.graph = nx.DiGraph() # Reset graph
        columns = list(df.columns)
        nodes = {column: df[column].sum() for column in columns if df[column].sum() > 0} # Dict comprehension to get sums of each column
        edges = Counter()
        for index, row in df.iterrows(): # Count edges 
            nodes_row = [] # Store list of nodes in this row # Shouldn't  have any duplicates
            for column in columns:
                if row[column] == 1:
                    nodes_row.append(column)
            for i, node_start in enumerate(nodes_row): # Enumerate used to simulatenously return index for loop
                for j, node_end in enumerate(nodes_row[i+1:]): # To prevent repeating already enumarated nodes
                    edges[(node_start, node_end)] += 1 # Bidirectional connection
                    edges[(node_end, node_start)] += 1
            
        for node in nodes:
            count = nodes[node]
            self.graph.add_node(node, color = "#8338ec", size = count)
        for node1, node2 in edges:
            count = edges[(node1, node2)]
            self.graph.add_edge(node1, node2, width = count)
        print(nx.algorithms.bipartite.spectral_bipartivity(self.graph))
        return None

    def resetGraph(self,):
        self.graph = nx.Graph()

    def renderGraphNX2(self, 
        width_log = 2, width_min = 0.2, 
        alpha_max = 0.95, alpha_min = 0.01, alpha_root = 1, 
        save_prefix = False, cmap= True, fig_size = 10,
        ):
        """
        Renders the graph contained within the object using NX
        ----
        save_prefix: prefix for saving figures
        cmap: use color mapping in the stead of transparency 
        """
        dict_sizes = dict(self.graph.nodes(data="size")) # Convert node data to dict
        scaling = fig_size*40/max(list(dict_sizes.values())) # Use max node value 
        print("Scaling = " + str(scaling))
        node_sizes = [scaling*size for (node, size) in self.graph.nodes(data="size")]
        node_colors = [color for (node, color) in self.graph.nodes(data="color")]
        edge_width_true = [width for (node1, node2, width) in self.graph.edges(data="width")]
        edge_widths = [log(scaling*width, width_log) for width in edge_width_true]
        edge_widths = np.clip(edge_widths, width_min, None) # Set lower bound of width to 1
        edge_transparency = [alpha_max*(width/max(edge_width_true))**(1/alpha_root) for width in edge_width_true] # Scaled to max width times 0.7 to avoid solid lines, cube root if you want to reduce right skewness 
        edge_transparency = np.clip(edge_transparency, alpha_min, None) # Use np to set lower bound for edges
        edge_zeroes = [0 for i in edge_width_true]

        #%% Networkx visualization (multiple elements)
        # nx uses matplotlib.pyplot for figures, can use plt manipulation to modify size
        fig = plt.figure(1, figsize = (fig_size * 1.1, fig_size), dpi = 800)
        plt.clf() # Clear figure, has to be done AFTER setting figure size/DPI, otherwise this information is no assigned properly
        layout = nx.kamada_kawai_layout(self.graph) # Different position solvers available: https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_kamada_kawai.html
        nx.draw_networkx_nodes(self.graph, 
            pos = layout,
            alpha = 0.8,
            node_size = node_sizes,
            node_color = node_colors,
            )
        # Manually draw labels with different sizes: https://stackoverflow.com/questions/62649745/is-it-possible-to-change-font-sizes-according-to-node-sizes
        # Non-overlapping text: https://stackoverflow.com/questions/19073683/how-to-fix-overlapping-annotations-text
        texts = []
        for node, (x, y) in layout.items():
            label_size = log(scaling*self.graph.nodes[node]["size"], 2) # Retrieve size information via node identity in graph
            texts.append(plt.text(x, y, node, fontsize = label_size, ha = "center", va = "center", alpha = 0.7)) # Manually draw text
        adjust_text(texts)

        # Draw legend: https://stackoverflow.com/questions/29973952/how-to-draw-legend-for-scatter-plot-indicating-size
        # Same scaling factor but different rounding thresholds
        d1 = roundNum(0.02*max(node_sizes)/scaling, 5) # Reference of 5 for max of 250
        d2 = roundNum(0.08*max(node_sizes)/scaling, 10) # Reference of 20 for max of 250 
        d3 = roundNum(0.4*max(node_sizes)/scaling, 20) # Reference of 100 for max of 250
        d4 = roundNum(max(node_sizes)/scaling, 50) # Reference of 250 for max of 250
        p1 = plt.scatter([],[], s=d1*scaling, marker='o', color='#8338ec', alpha = 0.8)
        p2 = plt.scatter([],[], s=d2*scaling, marker='o', color='#8338ec', alpha = 0.8)
        p3 = plt.scatter([],[], s=d3*scaling, marker='o', color='#8338ec', alpha = 0.8)
        p4 = plt.scatter([],[], s=d4*scaling, marker='o', color='#8338ec', alpha = 0.8)

        plt.legend((p1, p2, p3, p4), 
            (d1, d2, d3, d4), # Divide by scaling to convert back to normal size
            scatterpoints=1,loc='lower left', title = "Number of patient with condition", 
            ncol=4, prop={'size': fig_size}, title_fontsize = fig_size, borderpad = 0.8,
            )
        # scatterpoints = number of points in each size demo
        # ncol = number of columns that each size demo will be split into
        # prop = container deciding properties of text relating to the size demos
        # 10 is default font size
        
        if cmap: # Will map values (in proportion to min/max) to a color spectrum
            edges = nx.draw_networkx_edges(self.graph,
                pos = layout,
                alpha = edge_transparency, # Can add transparency on top to accentuate
                edge_color = edge_transparency,
                width = edge_widths,
                edge_cmap = plt.cm.summer, 
                )
            edges = nx.draw_networkx_edges(self.graph, # Dummy variable for if color assignment is cube rooted, (transparency set to zero)
                pos = layout,
                alpha = edge_zeroes, # Array of zeroes
                edge_color = edge_width_true, # NOTE THAT THIS IS NOT EXACTLY THE SAME SCALE (due to cube root)
                edge_cmap = plt.cm.summer, 
                )
            # Colorbar legend solution: https://groups.google.com/g/networkx-discuss/c/gZmr-YgvIQs
            # Alternative solution using FuncFormatter here: https://stackoverflow.com/questions/38309171/colorbar-change-text-value-matplotlib
            plt.sci(edges)
            plt.colorbar().set_label("Number of patients with comorbidity relationship")
            # Available colormaps: https://matplotlib.org/3.5.0/tutorials/colors/colormaps.html
            # Tested colormaps: GnBu is too similar to node color scheme, [YlOrRd, PuRd, Wistia] makes small edges too light, 
        else:
            edges = nx.draw_networkx_edges(self.graph,
                pos = layout,
                alpha = edge_transparency,
                width = edge_widths,
                )
        if save_prefix:
            plt.savefig(f"figures/net_{save_prefix}_(width[log{str(width_log)}_min{str(width_min)}]alpha[max{str(alpha_max)}min{str(alpha_min)}root{str(alpha_root)}]).png")
        else:
            plt.show()
        return None


#%%

if __name__ == "__main__":
    df = pd.read_excel("data/merged_elix_formatted_betterlabels_annotated.xlsx")
    temp = Grapher()
    for i in range(8):
        df_subset = df[df["LCA class"] == i].drop("LCA class", 1)
        temp.buildGraphFromDF(df_subset)
        temp.renderGraphNX2(alpha_root=0.5, save_prefix=f"comorb_clu{i}")
# %%
if __name__ == "__main__":
    df = pd.read_excel("data/merged_elix_formatted_betterlabels.xlsx")
    temp = Grapher()
    temp.buildGraphFromDF(df)
    temp.renderGraphNX2(alpha_root=0.5, save_prefix=f"comorb")

#%%
    graph = temp.graph
    sorted_sizes = sorted(list(graph.nodes(data = "size")), key = lambda x: x[1])
    sorted_edges = sorted(list(graph.edges(data = "width")), key = lambda x: x[2])
    print(sorted_sizes)
    print(sorted_edges)