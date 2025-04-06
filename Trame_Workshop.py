import numpy as np
import matplotlib.pyplot as plt
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, trame, matplotlib

# ----------------------------------------------------------------------------- 
# Trame setup 
# ----------------------------------------------------------------------------- 

server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller
state.table_items = []

# ----------------------------------------------------------------------------- 
# Table Headers 
# ----------------------------------------------------------------------------- 

state.table_headers = [
{"text": "Index", "value": "index"},
{"text": "X Value", "value": "values1"},
{"text": "Y Value", "value": "values2"},
{"text": "Actions", "value": "actions"},
]

# ----------------------------------------------------------------------------- 
# Table Structure
# ----------------------------------------------------------------------------- 
state.table = {
"headers": ("table_headers", state.table_headers),
"items": ("table_items", []),
"classes": "elevation-1 ma-4",
"multi_sort": True,
"dense": True,
"items_per_page": 5,
"dark": True,
}

# ----------------------------------------------------------------------------- 
# Table Items
# ----------------------------------------------------------------------------- 
def table_values():
    
    # hardcoding values
    new_value1 = float(state.table_items[-1]["values1"]) + 1 if state.table_items else 1
    new_value2 = float(state.table_items[-1]["values2"]) * -1.5 if state.table_items else 1

    # Append new values to the table items
    state.table_items.append(
        {   "index": len(state.table_items) + 1,
            "values1": new_value1,
            "values2": new_value2,
            "actions": "Remove",
        }
    )
    
    server.state.dirty("table_items")  #Refresh the table items

# ----------------------------------------------------------------------------- 
# Define Figure Size 
# ----------------------------------------------------------------------------- 
def figure_size():
        return {"figsize": (10, 6), "dpi": 80}

# ----------------------------------------------------------------------------- 
# Scatter Plot View 
# ----------------------------------------------------------------------------- 
def ScatterPlot():
    plt.close("all")
    fig, ax = plt.subplots(**figure_size())

    if state.table_items:
        # Extract all X and Y values from table_items
        x_values = [item["values1"] for item in state.table_items]
        y_values = [item["values2"] for item in state.table_items]
    
        ax.plot(x_values, y_values, "or", ms=20, alpha=0.3)
        
        ax.plot(np.random.normal(size=50), np.random.normal(size=50), "ob", ms=20, alpha=0.1)

    ax.set_xlabel("X axis", size=14)
    ax.set_ylabel("Y axis", size=14)
    ax.set_title("Matplotlib ScatterPlot", size=18)
    ax.grid(color="lightgray", alpha=0.7)
    return fig

# ----------------------------------------------------------------------------- 
# Line Plot View 
# ----------------------------------------------------------------------------- 
def LinePlot():
    plt.close("all")
    fig, ax = plt.subplots(**figure_size())
    
    if state.table_items:
        # Extract all X and Y values from table_items
        x_values = [item["values1"] for item in state.table_items]
        y_values = [item["values2"] for item in state.table_items]
        
        ax.plot(x_values, y_values, "-o", 
                linewidth=4, 
                markerfacecolor="red",
                markersize=10,)
    
    ax.set_xlabel("X axis", size=14)
    ax.set_ylabel("Y axis", size=14)
    ax.set_title("Matplotlib LinePlot", size=18)
    ax.grid(True, color="lightgray", linestyle="solid")
    return fig


# -----------------------------------------------------------------------------
# Change Charts 
# -----------------------------------------------------------------------------
@state.change("active_figure", "figure_size", "table_items")
def update_chart(active_figure, **kwargs):
    ctrl.update_figure(globals()[active_figure]()) #creates a function with the name of the active figure and calls it

# -----------------------------------------------------------------------------
# Remove Item
# -----------------------------------------------------------------------------
def remove_item(value1, value2):
    for i in state.table_items:
        if i["values1"] == value1:
            if i["values2"] == value2:
                state.table_items.remove(i)
                server.state.dirty("table_items")

# -----------------------------------------------------------------------------
# Update Values with New Values
# -----------------------------------------------------------------------------
def update_values(value, index, field):
    value = float(value) 

    #Indexing starts from 0
    if index - 1 < len(state.table_items):
        state.table_items[index - 1][field] = value
        server.state.dirty("table_items")

# ----------------------------------------------------------------------------- 
# UI Layout
# ----------------------------------------------------------------------------- 

state.trame__title = "Trame Workshop"

with SinglePageLayout(server) as layout:
    layout.title.set_text("Trame Application with Matplotlib Figures")

    with layout.toolbar:
        vuetify.VSpacer(style="margin-right: 20px")
        vuetify.VSelect(
            v_model=("active_figure", "ScatterPlot"),
            items=(
                "figures",
                [
                    {"text": "Scatter Plot", "value": "ScatterPlot"},
                    {"text": "Line Plot", "value": "LinePlot"},
                    
                ],
            ),
            label="Select Chart",
            dense=True,
            style="margin-top: 15px",
        )

    with layout.content:

        with vuetify.VContainer(fluid=True, style="background-color: #aaa7cc; max-width: 100%; max-height: 100%;"):    
            with vuetify.VRow(classes="justify-center"):
                vuetify.VSubheader("Welcome to the Trame Dashboard",
                            style="font-size: 30px;font-weight: bold;color: #33007b; padding-top: 20px; padding-bottom: 20px;")
            
            with vuetify.VRow(classes="justify-center"):
                with vuetify.VCol(cols=5):
                    
                    with vuetify.VRow(classes="justify-center"):    
                        vuetify.VBtn("Update Table", 
                            style="margin-top: 40px", 
                            color="#f96161", 
                            click=table_values, 
                            classes="d-flex align-center justify-center",)

                    with vuetify.VRow(classes="justify-center"):
                        
                            with vuetify.VDataTable(**state.table, style="margin-top: 40px"): #  ** for unpacking the dictionary values
                                    
                                    with vuetify.Template(actions="{ item }",__properties=[("actions", "v-slot:item.actions")],):
                                        vuetify.VIcon("mdi-close-thick", color="red" ,click=(remove_item, "[item.values1, item.values2]"),)

                                    with vuetify.Template(                                                                                                                                
                                        values1="{ item }",                                                                                                                          
                                        __properties=[("values1", "v-slot:item.values1"),],):                                                                                                                                                                                                                                                                                              
                                                                                                                                                                                            
                                            vuetify.VTextField(                                                                                                                               
                                            v_model=("item.values1",),                                                                                                                      
                                            type="number",                                                                                                                                    
                                            dense=True,                                                                                                                                       
                                            hide_details=True,                                                                                                                                
                                            change=(update_values, "[item.values1, item.index, 'values1']"),                                                                                                                                                                                                                                 
                                            classes="d-flex align-center",                                                                                                                    
                                            step=0.1,
                                        )  

                                    with vuetify.Template(                                                                                                                                
                                        values2="{ item }",                                                                                                                          
                                        __properties=[("values2", "v-slot:item.values2"),],):                                                                                                                                                                                                                                                                                              
                                                                                                                                                                                            
                                            vuetify.VTextField(                                                                                                                               
                                            v_model=("item.values2",),                                                                                                                      
                                            type="number",                                                                                                                                    
                                            dense=True,                                                                                                                                       
                                            hide_details=True,                                                                                                                                
                                            change=(update_values, "[item.values2, item.index, 'values2']"),                                                                                                                                                                                                                                  
                                            classes="d-flex align-center",                                                                                                                    
                                            step=0.1,
                                        )  
                    
                with vuetify.VCol(cols=7):
                    html_figure = matplotlib.Figure(style="position: absolute,padding-top: 30px",) # create the matplotlib figure
                    ctrl.update_figure = html_figure.update   # whenever the figure is updated, the update function is called
                
                                                    
# ----------------------------------------------------------------------------- 
# Start the Application 
# ----------------------------------------------------------------------------- 

if __name__ == "__main__":
    server.start()  #makes sure to run only on execution, launches the trame server
    
