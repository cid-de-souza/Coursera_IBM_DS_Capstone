# Import required libraries
import pandas as pd
import dash
# ----------------------------------------------------------------------
# NEXT LINE CHANGED TO AVOID THIS WARNING
#      The dash_html_components package is deprecated. Please replace
#      `import dash_html_components as html` with `from dash import html`
# import dash_html_components as html # ORIGINAL
from dash import html                 # REPLACEMENT 
# ----------------------------------------------------------------------
# NEXT LINE CHANGED TO AVOID THIS WARNING
#      The dash_html_components package is deprecated. Please replace
#      `import dash_core_components as dcc` with `from dash import dcc`
# import dash_core_components as dcc # ORIGINAL
from dash import dcc                 # REPLACEMENT
# ----------------------------------------------------------------------
from dash.dependencies import Input, Output, State
import plotly.express as px
import numpy as np

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# ----------------------------------------------------------------------
# TASK 1 preprocessing: generate options for dropdown menu
# ......................................................................
site_lst = spacex_df['Launch Site'].unique().tolist()
options_ddm1 = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': i, 'value': i} for i in site_lst]
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# TASK 2a  preprocessing: preparing dataframe  with data to  build the
# pie   chart   with   percentage   of  success   for   launch   sites
# ......................................................................

# - compute total number of successes
tot_success = spacex_df['class'].sum(); 

# -  create pandas  series  (ps) `perc_succ`  with  the percentage  of
# success represented by each launch site (with one decimal position)
perc_succ = np.round(spacex_df.groupby(['Launch Site'])['class'].sum() * 100 / tot_success,1)

# - build lists from the previous  pandas series to create the desired
# - dataframe
lst_sites = (list)(perc_succ.index)
lst_rates = perc_succ.values.tolist()

# - create dataframe of percentage of  success rates grouped by launch
# - sites
df_succ_per_site = pd.DataFrame(list(zip(lst_sites, lst_rates)),
                                columns =['Launch Site', 'Success Rate'])

# ----------------------------------------------------------------------
# TASK 2b preprocessing: procedure to compute the dataset to build the
# pie  chart with  the success  and failure  percentages for  the site
# `entered_site`
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def compute_data_for_site_succ_rate(in_site):

    # filter the rows for entered_site
    df_aux = spacex_df[spacex_df['Launch Site'] == in_site][['Launch Site', 'class']]; #print(df_aux)

    # - pandas series (ps) `aux` with computed percentages for class
    aux = df_aux['class'].value_counts(normalize=True) * 100;

    # - build lists from where the df is built
    lst_class = (list)(aux.index)
    lst_perc = aux.values.tolist()

    # - create dataframe of percentage of success rates grouped by launch sites
    df_site = pd.DataFrame(list(zip(lst_class, lst_perc)),
                           columns =['Class', 'Percentage'])

    return df_site

# ----------------------------------------------------------------------
# TASK 3 preprocessing: getting min and max payloads
# ----------------------------------------------------------------------

# - computing the maxximum and minimum paylods
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# - computing 10 equally spaced values in the payload range
payload_ticks = np.round(np.linspace(0.0, 10000.0, num=11),0)

# - build dictionary of payload marks from the 10 values computed above
payload_marks={}
for i in range(len(payload_ticks)):
    payload_marks[(int)(payload_ticks[i])]=str((int)(payload_ticks[i]))

# ----------------------------------------------------------------------
# TASK 4 preprocessing: 
# ----------------------------------------------------------------------

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# - procedure to  compute the dataset to build the  pie chart with the
# - success rate     for     the      site     `entered_site`
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def compute_data_for_scatter_plot(in_site, payload_range):
    if in_site == 'ALL':
        df_aux = spacex_df[['Launch Site', 'Booster Version Category','Payload Mass (kg)','class']]
    else:
        df_aux = spacex_df[spacex_df['Launch Site'] == in_site]
        df_aux = df_aux[['Launch Site', 'Booster Version Category','Payload Mass (kg)','class']]

    df_aux = df_aux[(df_aux['Payload Mass (kg)'] >= payload_range[0]) & (df_aux['Payload Mass (kg)'] <= payload_range[1])]
    return df_aux

# ======================================================================

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                # ----------------------------------------------------------------------
                                dcc.Dropdown(id='site-dropdown',
                                             options=options_ddm1,
                                             value='ALL',
                                             placeholder="Select a Launch Site here",
                                             searchable=True                                           
                                ),
                                # ----------------------------------------------------------------------
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000,                # endpoints of the slide bar
                                                step=100,                        # limits the mouse positions to multiples of 100 in the slide bar
                                                marks=payload_marks,             # dictionary of marks indicated in the slide bar
                                                value=[min_payload,max_payload], # initializes the selected range
                                ),
                                html.Br(),

                                # MY TEST: TO KNOW THE TYPE AND VALUE RETURNED BY the RangeSlider component above
                                # Answer:  Type of slider_value "<class 'list'>"
                                #          Type of slider_value[0] "<class 'int'>" 
                                # html.Div(id='test'),
 
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                html.Br()])

# ----------------------------------------------------------------------
# MY TEST:  the test callback: used  to get the types  returned by the
# `dcc component` RangeSlider
# ----------------------------------------------------------------------
# @app.callback(
#     Output('test', 'children'),
#     [Input('payload-slider', 'value'), Input('site-dropdown', 'value')])
# def update_output(slider_value, ddwn_value):
#     my_string = 'Selected Range "{}"\n'.format(slider_value)
#     my_string += 'Type of slider_value "{}"\n'.format(type(slider_value))
#     my_string += 'Type of slider_value[0] "{}"\n'.format(type(slider_value[0]))
#     my_string2 = 'Site dropdown selection: "{}" '.format(ddwn_value)
#     return my_string, my_string2

# ----------------------------------------------------------------------
# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# ......................................................................
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    #filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(df_succ_per_site, values='Success Rate', 
                     names='Launch Site', 
                     title='Total successful launches by site')
        return fig
    else:
        # return the outcomes piechart for the entered site
        df_site_class_perc = compute_data_for_site_succ_rate(entered_site)
        
        fig = px.pie(df_site_class_perc, values='Percentage', 
                     names='Class', 
                     title='Total success launches for site '+' '+entered_site)
        return fig

# ----------------------------------------------------------------------
# TASK 4:
# Add a callback function  for `site-dropdown` and `payload-slider` as
# inputs, `success-payload-scatter-chart` as output
# ......................................................................
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input('payload-slider', 'value'), Input('site-dropdown', 'value')])
def get_scatter_plot(slider_value,entered_site):
    
    # - build the dataset according to the `entered_site`
    df=compute_data_for_scatter_plot(entered_site,slider_value)

    # title string
    title_str = 'Correlation between Payload and Success for '
    if entered_site == 'ALL':
        title_str += 'all sites'
    else:
        title_str += 'site '+entered_site
    title_str += ' and payload range '+(str)(slider_value)
        
    fig = px.scatter(df, x="Payload Mass (kg)", y="class", 
                     hover_name="Payload Mass (kg)", color="Booster Version Category",
                     title=title_str, size_max=20)
    fig.update_traces(marker_size=10) # minimum size for a marker: 10 seems appropriate

    return fig

# ----------------------------------------------------------------------


# Run the app
if __name__ == '__main__':
    app.run_server()
