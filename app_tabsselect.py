#from flask import Flask, render_template, request, redirect, url_for, session
#from flask_socketio import SocketIO, join_room, leave_room, emit
#from flask_session import Session
import requests
import json
from engineio.payload import Payload

import string
import random

from werkzeug.middleware.dispatcher import DispatcherMiddleware

#from dash import Dash
#import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
#from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto
#import flask

import plotly.express as px
import pandas as pd

from quart import Quart, g, request
from quart.helpers import make_response

import dash_devices
from dash_devices.dependencies import Input, Output, State

import socketio

def sendUE4(adress, data):
    # The POST request to our node server
    res = requests.post('http://127.0.0.1:3000/in', json=data)
    #return
    # Convert response data to json
    #returned_data = res.json() 
    #print(returned_data)


dash_app = dash_devices.Dash(__name__)
dash_app.config.suppress_callback_exceptions = True



start_table_df = pd.DataFrame(columns=[''])

import json

import base64
import datetime
import io

#import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
import dash_table as dt

import plotly.express as px


import pandas as pd

from additionalfunctions import *



scorethreshold = 0.6

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

colors = {
    'background': '#F0F8FF',
    'text': '#00008B'
}



dfnodestype1 = []
dfnodestype2 = []

pickednode = []
diseaseselected = False

diseasedegrees = []
disdisdegrees= []
genegenedegrees= []



df = pd.read_csv( 'flask_websockets_Node\input\curated_gene_disease_associations2.csv')

dfnew = df

print(df.columns)

#disease filter
df = df.query('source == "CTD_human" & diseaseType == "disease"' )
df = df.query('score > ' + str(scorethreshold))

#all to string
df=df. applymap(str)


dfnodes, dfedges, dfnodesgenes, dfedgesgenes, diseasedegrees, disdisdegrees, genegenedegrees = alldiseasegenegraphs(df)


edges = [{'data': {'source': x, 'target': y}} for x,y in zip(dfedges.source,dfedges.target)]


nodes = [{'data': {'id': x, 'label': y, 'size': 1}} for x,y in zip(dfnodes.number,dfnodes.abbr)]



#from set elements function
disses = [x[1] for x in genegenedegrees]


colors = []
for colorelem in dfnodes.dpi:
    if (float(colorelem) < float(400)):
        col = "yellow"
        colors.append(col)
    elif (float(colorelem) < float(600)):
        col = "green"
        colors.append(col)
    elif (float(colorelem) < float(800)):
        col = "red"
        colors.append(col)
    else:
        col = "blue"
        colors.append(col)

#coloring according to dpi
nodes = [{'data': {'id': x, 'label': y, 'size': z*5+5, 'color': a, 'oldcolor': a}} for x,y,z,a in zip(dfnodes.number,dfnodes.abbr, disses, colors)]    

edges = [{'data': {'source': x, 'target': y}} for x,y in zip(dfedges.source,dfedges.target)]


elements = nodes + edges

#nodessets
dfnodestype1 = df['geneId']
dfnodestype2 = df['diseaseId']


# create bipartite graph in networkx 
nxgraph1 = convertnx(df)


#create gene network / networkx
nxgraphdisease = convertnx_part(dfedges)

#create disease network / networkx
nxgraphgenes = convertnx_part(dfedgesgenes)


tab1 = html.Div(children=[
    html.H1(children='Dash Graph app'),
  


    html.Div(className="app-header",
    children='''


    '''),
    

    html.P("Just a shared element (without function at the moment):"),

    dcc.RadioItems(
    id='sortnetwork',
    options=[
        {'label': '1', 'value': 'D'},
        {'label': '2', 'value': 'G'},
   
    ],
    value='D'
    ),
        html.P("Do you want to share tabs:"),

     dcc.RadioItems(
    id='sharetabs',
    options=[
        {'label': 'yes', 'value': 'Y'},
        {'label': 'no', 'value': 'N'},
   
    ],
    value='Y'
    ),

    html.P(id='placeholder1'),

    html.P("Exclude gene-disease-edges with a score below (this slider is SHARED):"),
    dcc.Slider(id="scorethresholdslider", min=0, max=1, step = 0.05, value=scorethreshold, 
               marks={0: '0', 1: '1'}),

    html.Div(id='thresh'),
    html.Div(id='dfelement'),
  
 
   # dash_table.DataTable(
   # id='table1',
   # columns=[{"name": i, "id": i} for i in df.columns],
   # columns=df.columns,
  
  #  data=df.to_dict('records'),
    
#)
])


default_stylesheet = [
    {
        "selector": "node",
        "style": {
           "height": "data(size)",
           "width": "data(size)",
           'background-color': "data(color)",
           "border-color": "data(color)",
            "content": "data(label)",
            "font-size": "12px",
            "text-valign": "center",
            "text-halign": "center",
        }
    }
]

tab2 = html.Div([
    html.H3('Gene network'),

   

    dcc.RadioItems(
    id='cytographlayout',
    options=[
        {'label': 'circle', 'value': 'circle'},
        {'label': 'cose', 'value': 'cose'},
      
        
    ],
    value='cose'
    ),

     html.Button('Update Graph', id='updatecyto', n_clicks_timestamp=0),
     html.H3('Coloring according to DPI value (disease pleiotropy index, indicates the number of different disease classes a gene is associated with) '),
#cytoscape element
    cyto.Cytoscape(
        id='cytoscapenetw',

        style={'width': '90vh', 'height': '90vh'},

        elements=elements,

        layout={
            'name': 'circle'
        },
         stylesheet=default_stylesheet
    ),
    html.Pre(id='cytoscape-tapNodeData-json', style=styles['pre']),

   

  
])

#callback for choosing score-threshold (for disgenenet-file)
@dash_app.callback_shared(Output('thresh', 'children'),
             [Input('scorethresholdslider', 'value')])
def change_scorethreshold(val):
    global scorethreshold
    scorethreshold = val
    return val



@dash_app.callback_shared(Output('cytoscape-tapNodeData-json', 'children'),
              [Input('cytoscapenetw', 'tapNodeData')])
def displayTapNodeData(data):
    global pickednode
    global diseaseselected
    pickednode = data
    diseaseselected = False
    print(str(pickednode))
    return json.dumps(data, indent=2)


@dash_app.callback_shared(Output('sortnetworkstore', 'data'),
              [Input('sortnetwork', 'value')])
def sortnetworkstore(data):
    print("sortnetworkstore")
    return data

@dash_app.callback_shared(Output('threshstore', 'data'),
              [Input('thresh', 'children')])
def threshstore(data):
    print("threshstore")
    return data

@dash_app.callback_shared(Output('sharetabsstore', 'data'),
              [Input('sharetabs', 'value')])
def threshstore(data):
    print("sharetabsstore")
    return data



#callback for creating gene network graph (cytoscape)
@dash_app.callback_shared(
    [Output('cytoscapenetw', 'elements'),

    Output('cytoscapenetw', 'layout')],
    
    [Input('cytographlayout', 'value'),

    Input('updatecyto', 'n_clicks_timestamp'),
    
     Input('sortnetworkstore', 'data'), 

    Input('threshstore', 'data')] )
def set_elements( llayout, updatebutton, sortof, val):
    global dfnew
    global df, dfnodes, dfedges, dfnodesgenes, dfedgesgenes, diseasedegrees, disdisdegrees, genegenedegrees, elements, dfnodestype1, dfnodestype2
    global nxgraph1, nxgraphdisease, nxgraphgenes
    

    layout={ 'name': llayout}

    
    df = dfnew

    
    df = df.query('source == "CTD_human" & diseaseType == "disease"' )

    print("scorethresho")
    print(scorethreshold)
    print("thresval")
    print(val)
    df = df.query('score > ' + str(val))

    df=df.applymap(str)


    dfnodes, dfedges, dfnodesgenes, dfedgesgenes, diseasedegrees, disdisdegrees, genegenedegrees = alldiseasegenegraphs(df)


    #from set elements function
    disses = [x[1] for x in genegenedegrees]

 
    colors = []
    for colorelem in dfnodes.dpi:
        if (float(colorelem) < float(400)):
            col = "yellow"
            colors.append(col)
        elif (float(colorelem) < float(600)):
            col = "green"
            colors.append(col)
        elif (float(colorelem) < float(800)):
            col = "red"
            colors.append(col)
        else:
            col = "blue"
            colors.append(col)

    #coloring according to dpi
    nodes = [{'data': {'id': x, 'label': y, 'size': z*5+5, 'color': a}} for x,y,z,a in zip(dfnodes.number,dfnodes.abbr, disses, colors)]    

    edges = [{'data': {'source': x, 'target': y}} for x,y in zip(dfedges.source,dfedges.target)]


    elements = nodes + edges

    #nodessets
    dfnodestype1 = df['geneId']
    dfnodestype2 = df['diseaseId']


    return elements, layout



tab3 = html.Div([
    html.H3('Bipartite gene-disease network / networkx'),

    html.Button('Update NXGraph', id='updatenx', n_clicks_timestamp=0),

    dcc.Graph(id="nxgr")

])

#callback for creating networkx bipartite graph
@dash_app.callback(
    Output('nxgr', 'figure'),
    [Input('updatenx',  'n_clicks_timestamp')]

)
def update_output2(ns):

    graph1 = createnxgraph(nxgraph1, dfnodestype1)
    return graph1



tab4 = html.Div([
    html.H3('disease network'),
    dcc.RadioItems(
    id='cytographlayout2',
    options=[
        {'label': 'circle', 'value': 'circle'},
        {'label': 'cose', 'value': 'cose'},
      
        
    ],
    value='cose'
    ),

     html.Button('Update Graph', id='updatecyto2', n_clicks_timestamp=0),

    cyto.Cytoscape(
        id='cytoscapenetw2',
        style={'width': '100%', 'height': '1200px'},
        elements=elements,
        layout={
            'name': 'circle'
        }
    ),
    html.Pre(id='cytoscape-tapNodeData-jsonb', style=styles['pre']),

])


@dash_app.callback_shared(Output('cytoscape-tapNodeData-jsonb', 'children'),
              [Input('cytoscapenetw2', 'tapNodeData')])
def displayTapNodeData(data):
    global pickednode
    global diseaseselected
    pickednode = data
    diseaseselected = True
    print(str(pickednode))
    return json.dumps(data, indent=2)
    

@dash_app.callback_shared(
    [Output('cytoscapenetw2', 'elements'),

    Output('cytoscapenetw2', 'layout')],
    
    [Input('cytographlayout2', 'value'),

    Input('updatecyto2', 'n_clicks_timestamp')])
def set_elements( llayout, graphelement):
   
    genenodes = [{'data': {'id': x, 'label': y}} for x,y in zip(dfnodesgenes.number,dfnodesgenes.abbr)]
    geneedges = [{'data': {'source': x, 'target': y}} for x,y in zip(dfedgesgenes.source,dfedgesgenes.target)]

    layoutgene={ 'name': llayout}

    elementsgene = genenodes + geneedges

    return elementsgene, layoutgene





tab5 = html.Div([
    html.H3('Individual node statistics / degree histograms'),
    dcc.Textarea(
        id='textarea-example',
        value=str(pickednode),
        style={'width': '100%', 'height': 100},
    ),
    #show picked node
    html.Div(id='textarea-example-output', style={'whiteSpace': 'pre-line'}),

    #indiv p node
    html.Div(id='textarea-example-output2', style={'whiteSpace': 'pre-line'}),

    html.Button('Show Node Statistics', id='showstat', n_clicks_timestamp=0),

#datatable doesn't work with dash_devices...
 #    dt.DataTable(
 #       id='tbl', 
  #      data = [],
   #     columns = []
    
   # ),

    html.Div(id="tablesubstitute"),

    html.Table(id="htmltable"),

    html.H4("Histograms for the degree distribution of the networks:"),
    dcc.Graph(id="histo1"),

    html.P("Number of bins:"),
    dcc.Slider(id="binnumber", min=1, max=100, value=1, 
               marks={1: '1', 100: '100'}),

    dcc.RadioItems(
    id='histoselectgraph',
    options=[
        {'label': 'DiseaseGraph Degree Distribution', 'value': 'D'},
        {'label': 'GeneGraph Degree Distribution', 'value': 'G'},
        
        
    ],
    value='N'
    ),
   


])

@dash_app.callback_shared(

    Output('htmltable', 'children'),
    [Input('htmltable', 'n_clicks_timestamp')])
def update_stat_table(click):
    if diseaseselected == True:
        statgraph = nxgraphgenes
    else:
        statgraph = nxgraphdisease
  
    data1, columns1 = allcentralities(statgraph, pickednode)


    data2, columns2 = allcentralities(nxgraph1, pickednode)

    data = [data1, data2]
    data = pd.concat(data)
    
    data.index = ['Projection', 'Bipartite Graph']
    data['Graph Type'] = data.index
    data = data.reset_index()
  

    columns = [{"name": i, "id": i} for i in data.columns]
   
    #return data, columns
    return html.Table(
        # Header
        [html.Tr([html.Th(col, style={'border': 'solid', 'font-size':'1.2rem', 'border-color': 'black', 'border-width': '2px',
         'background-color': 'blue', 'rules': 'all'}) for col in data.columns], style={'border': 'solid', 'font-size':'1.3rem', 'border-color': 'black', 'border-width': '2px',
         'background-color': 'blue', 'rules': 'all'}) ] +
        # Body
        [html.Tr([
            html.Td(data.iloc[i][col], style={'border': 'solid', 'font-size':'1.3rem', 'border-color': 'black', 'border-width': '2px',
         'background-color': 'blue', 'rules': 'all'}) for col in data.columns
        ]) for i in range((len(data)))], style={'border': 'solid', 'font-size':'1.3rem', 'border-color': 'black', 'border-width': '2px',
         'background-color': 'blue', 'rules': 'all'}
    )


#callback for creating the data table for statistics of selected node
@dash_app.callback_shared(

    Output('tablesubstitute', 'children'),
    [Input('showstat', 'n_clicks_timestamp')])
def update_stat_table(click):
    if diseaseselected == True:
        statgraph = nxgraphgenes
    else:
        statgraph = nxgraphdisease
  
    data1, columns1 = allcentralities(statgraph, pickednode)


    data2, columns2 = allcentralities(nxgraph1, pickednode)

    data = [data1, data2]
    data = pd.concat(data)
    
    data.index = ['Projection', 'Bipartite Graph']
    data['Graph Type'] = data.index
    data = data.reset_index()
  

    columns = [{"name": i, "id": i} for i in data.columns]
    data = data.to_dict('records')

    return str(data)


#callback for creating a degree distribution histogram
@dash_app.callback_shared(
    Output("histo1", "figure"), 
    [Input("binnumber", "value"), 
     Input("histoselectgraph", "value")])
def display_color(binnumber, histoselectgraph):
    global disdisdegrees
    global genegenedegrees
  
    if histoselectgraph == 'D':
        disdisdegreedata = []
        for elem in disdisdegrees:
            disdisdegreedata.append(elem[1])
  
        fig = px.histogram(disdisdegreedata, nbins = binnumber)
    else: 
        genegenedegreedata = []
        for elem in genegenedegrees:
            genegenedegreedata.append(elem[1])
   
        fig = px.histogram(genegenedegreedata, nbins = binnumber)

        
  
    return fig

@dash_app.callback_shared(
    Output('textarea-example-output', 'children'),
    [Input('textarea-example', 'value')]

)
def update_output(value):
    global pickednode
    print(str(pickednode))
    return 'You have selected: \n{}'.format(pickednode)


tab6 = html.Div([
    html.H3('Diversity-ubiquity plot for genes'),
    html.Button('Compute diversity-ubiquity plot for disease network', id='showubiqu', n_clicks_timestamp=0),
     dcc.Graph(id="ubiqugraph", style={'width': '90vh', 'height': '90vh'})

])

#create diversity-ubiquity plot
@dash_app.callback_shared(
    Output('ubiqugraph', 'figure'), 
    [Input('showubiqu', 'n_clicks_timestamp')])
def update_stat_table(click):
    
    bipartdegrees = nx.degree(nxgraph1)

    #for diselem in nxgraphgenes.nodes:
     #   del bipartdegrees[diselem]

    #number of diseases each gene causes
    bipartdegreesgene = { genekey: bipartdegrees[genekey] for genekey in nxgraphdisease.nodes }

    bipartdegreesgdis = { diskey: bipartdegrees[diskey] for diskey in nxgraphdisease.nodes }


 
    plotxy = []

    #calculate ubiquity for genes (i.e. average number of genes that also cause the disease)
    for elem in nxgraphdisease.nodes:
        disnumbers = []
        for dis in nxgraph1[elem]:
            disnumber = len(nxgraph1[dis])

            disnumbers.append(disnumber)
        avrgdis = np.mean(disnumbers)

        plotxy.append([elem, bipartdegreesgene[elem], avrgdis])
    
    plotxydf = pd.DataFrame(plotxy, columns=['elem', 'diversity', 'ubiquity'])

    #for elem in nxgraphdisease.nodes:
    #    print(len(nxgraphdisease[elem]))
    #    plotxy.append([elem, bipartdegreesgene[elem], len(nxgraphdisease[elem])])
    #number of genes for each disease

    fig = px.scatter(plotxydf, x="diversity", y="ubiquity", hover_data=['elem'], title="diversity-ubiquity plot", labels = {"diversity": "diversity: number of diseases the gene causes", "ubiquity": "ubiquity: average number of genes which also cause the disease"})

    return fig




dash_app.layout = html.Div([
    html.H1('Dash Graph multiple tabs', className="app-headerf" ),
     dcc.Store(id='threshstore'),
     dcc.Store(id='sortnetworkstore'),
     dcc.Store(id='sharetabsstore'),
    dcc.Tabs(className="app-header", id="tabs-example", value='tab-1-example', children=[
        dcc.Tab(id="tab-1", label='Data upload', value='tab-1-example'),
        dcc.Tab(id="tab-2", label='Gene Network', value='tab-2-example'),
        dcc.Tab(id="tab-3", label='Bipartite network', value='tab-3-example'),
        dcc.Tab(id="tab-4", label='Disease network', value='tab-4-example'),
        dcc.Tab(id="tab-5", label='Statistics / pick node before', value='tab-5-example'),
        dcc.Tab(id="tab-6", label='Diversity-ubiquity plot', value='tab-6-example'),
    ]),
    html.Div( 
    id='tabs-content-example',
             children = tab1,className="app-headerf2")
             
],className="app-headerf",)

#callback for showing selected data
@dash_app.callback_shared( 
    [Output('table1', 'columns'),
    Output('table1', 'data')],
    [Input('graphelement', 'value')])
def set_table(graphelement):
    global dfnodes
    global dfedges
    global df
 

    if (graphelement == 'N'):
        dataview = dfnodes
      #  return [{"number": i, "abbr": i, "dpi": i} for i in dataview.columns], dataview.to_dict('records')

    elif (graphelement == 'E'):
        dataview = dfedges
       # return [{"source": i, "target": i} for i in dataview.columns], dataview.to_dict('records')

    elif (graphelement == 'D'):
        dataview = df
 

    return [{"name": i, "id": i} for i in dataview.columns], dataview.to_dict('records')
 #   return dataview.columns, dataview.to_dict('records')


#callback for switching tabs
@dash_app.callback(Output('tabs-content-example', 'children'),
             [Input('tabs-example', 'value')],
             [State('sharetabsstore', 'data')]
           #  State('tabs-content-example', 'children')],
             )           
def render_content(tab, sharetabs):
    print("sharetabsstore")
    print(sharetabs)
    if (sharetabs == "Y"):
        if tab == 'tab-1-example':
            dash_app.push_mods({'tabs-content-example': {'children': tab1}})
            return tab1
        elif tab == 'tab-2-example':
            print("return tab2")
            dash_app.push_mods({'tabs-content-example': {'children': tab2}})
            return tab2
        elif tab == 'tab-3-example':
            dash_app.push_mods({'tabs-content-example': {'children': tab3}})
            return tab3

        elif tab == 'tab-4-example':
            dash_app.push_mods({'tabs-content-example': {'children': tab4}})
            return tab4

        elif tab == 'tab-5-example':
            dash_app.push_mods({'tabs-content-example': {'children': tab5}})
            print("return tab5")
            return tab5

        elif tab == 'tab-6-example':
            dash_app.push_mods({'tabs-content-example': {'children': tab6}})
            return tab6

    if (sharetabs == "Y" or sharetabs == "N"):
        if tab == 'tab-1-example':

            return tab1
        elif tab == 'tab-2-example':

            return tab2
        elif tab == 'tab-3-example':
    
            return tab3

        elif tab == 'tab-4-example':
    
            return tab4

        elif tab == 'tab-5-example':

            return tab5

        elif tab == 'tab-6-example':
            
            return tab6
    else:
        return dash_devices.no_update








if __name__ == '__main__':
   # socketio.run(app, host="127.0.0.1", port=5000)
    #socketio.run(app)
   # dash_app.run_server(debug=True, host='0.0.0.0', port=5000, dev_tools_hot_reload=True, dev_tools_client_reload=True)
    dash_app.run_server(debug=True, host='0.0.0.0', port=5000)
