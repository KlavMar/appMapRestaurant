#import libraries
from os import name
from dash import Dash,html,dcc,Input,Output,dash_table,State
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pandas as pd
import re 
from pathlib import Path
import plotly.express as px
from math import *
from dotenv import load_dotenv
from dotenv import dotenv_values
import os
load_dotenv()
config = dotenv_values(".env")


dir_csv="csv/"
dir_app=Path(__file__).resolve().parent
path=f'{dir_app}/{dir_csv}/'
style_graph={
    "margin":"3em auto","width":"95vw","border-radius":"1em","background":"#ffffff","height":"30vh"
}
df=pd.read_csv(f"{path}df.csv",sep=";",index_col=0,encoding='utf8').loc[1:,]

price_list = list(set(df.dropna().fourchette_prix))
price_list.append(" ")


pattern = "[a-zéèà&A-Zç()ïî]*"
liste_final =[]
for i in df.type_cuisine_1.unique():
    try:
        if i not in ["Fermé aujourd'hui",'Ferme dans 1 min']:
            string= " ".join(re.findall(pattern,i))
            liste_final.append(string.strip())
    except:
        pass


external_stylesheets=["https://storage.googleapis.com/portfolio_django_web_perso/css/dash/F12.css",
                      "https://cdn.jsdelivr.net/npm/tailwindcss@2.2.4/dist/tailwind.min.css"]
app = DjangoDash(name ='restaurant_map',external_stylesheets=external_stylesheets)
def recup_df_mask(note,type_cuisine,price):
  
   
    #df["link"]=df.link.apply(lambda x:f"[lien]({x})")

    if (note == None  and type_cuisine == None) or len(type_cuisine) == 0:
        return df
    else: 
        if type_cuisine == None : 
            mask = (df.note ==note) 
        elif note == None:
            mask= (df.type_cuisine.isin(type_cuisine))
        else:
            mask = ((df.note ==note) & (df.type_cuisine.isin(type_cuisine)))
    
    data = df.loc[mask,:]

    if price  !=  None:
        data = data[data.fourchette_prix==price]
    else:
        data  
    


    return data 



@app.callback(
        Output('map_restaurant','figure'),
        [Input('note','value'),Input("type_cuisine","value"),Input("price","value")]
)
def create_fig(note,type_cuisine,price):
    df = recup_df_mask(note,type_cuisine,price)
  
    jt =os.getenv("jt")
    px.set_mapbox_access_token(jt)
    fig = px.scatter_mapbox(df, lat="lat", lon="lon",color="fourchette_prix", size="note", size_max=15, zoom=14,hover_name="Restaurant",hover_data= {

                        "type_cuisine": False,             
                        "Avis":True,
                        "note":True,
                        "lat":False,"lon":False,
                            },
                           
                        )
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Arial"
        ),
        font=dict( family="Arial Black",size=18,color="#6b7280")
        
        )
    fig.update_layout(legend=dict(orientation="h",yanchor="top",y=1,xanchor="left",x=0.00,title="Prix"),font=dict(size=20,family="Arial"))      
    fig.update_layout(margin=dict(b=10,r=0,t=10,l=0),dragmode=False)

    return fig 


@app.callback(Output("cards","children"),[Input('note','value'),Input("type_cuisine","value"),Input("price","value")])

def update_table(note,type_cuisine,price):
    df_f = df.loc[:,["restaurants","type_cuisine","note","Avis","fourchette_prix","link"]]
    df_f.Avis=df_f.Avis.apply(lambda x:re.findall("[\d]*",x)[0])
    df_f.Avis=df_f.Avis.astype("float64")
    if (note == None  and type_cuisine == None) or type_cuisine == []:
        mask = ((df_f.note>=4.5) )
            
    else: 
        if type_cuisine == None : 
            mask = (df_f.note ==note) 
        elif note == None:
            mask= (df_f.type_cuisine.isin(type_cuisine))
        else:
            mask = ((df_f.note ==note) & (df_f.type_cuisine.isin(type_cuisine)))

    data = df_f.loc[mask,:]
    if price  !=  None:
        data = data[data.fourchette_prix == price]
    else:
        pass 
    

  
    cards = []
    for index,row in data.iterrows():
        card = html.Div(
        children=[
                    html.H4(row['restaurants'], className="text-2xl font-semibold p-3 m-3"),
                    html.P(f"{row['type_cuisine']}",className="text-xl font-semibold "),
                    html.Div(
                        children=[
                                html.P(f"note: {row['note']}",className="font-semibold m-2 "),
                                html.P(f"Avis: {int(row['Avis'])}",className="font-semibold m-2 "),
                                html.P(f"Prix: {row['fourchette_prix']}",className="font-semibold m-2 "),
                               
                        ],style={"display":"flex","flex-flow":"row wrap","justify-content":"center"}
                                ),
                     html.A("Réserver",href=f"{row['link']}",className='rounded-2xl px-10 py-3 m-2 bg-yellow-500 text-grey-300 text-semibold')
                   
                ],className="border-2 rounded-2xl m-2 p-5",style={"max-width":"97vw"}
            )
        cards.append(card)


    return cards





app.layout=html.Div([
        html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(
                        children = [
                            html.H3(children="Note",className="font-semibold"),
                            dcc.Dropdown(id="note",options=[{"label":i,"value":i} for i in sorted(df.note.unique())],className="dropdown-item"),
                        ]
                    ),
                    html.Div(
                        children=[
                            html.H3(children="Type de cuisine",className="font-semibold"),
                            dcc.Dropdown(id="type_cuisine",
                                         options=[{"label":i,"value":i} for i in sorted(liste_final)],
                                         multi=True,
                                         className="dropdown-item",),
                        ]
                    ),
                     html.Div(
                        children=[
                            html.H3(children="Price",className="font-semibold"),
                            dcc.Dropdown(id="price",options=[{"label":i,"value":i} for i in sorted(price_list)],className="dropdown-item"),
                        ]
                    ),
                ],className="container-dropdown-filter"
            )
        ],className="container-nav-dash-filter"
    ),
    html.Div(
        children=[
            html.Div(id="cards",children=[],className="lg:col-span-3 md:col-span-3 overflow-auto h-screen"),
            html.Div(dcc.Graph(id="map_restaurant",className="lg:col-span-8 md:col-span-12 p-1  my-2 h-screen",style={"min-width":"90vw","max-width":"98vw"}))
           ],className="grid lg:grid-flow-row sm:grid-flow-col lg:grid-cols-12 sm:grid-cols-12 gap-4",
           )
])
