import streamlit as st
import pandas as pd
import numpy as np
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.charts import Map
from pyecharts.faker import Faker
from streamlit_echarts import st_pyecharts
import matplotlib.pyplot as plt
import plotly.express as px





#set up page
st.set_page_config(page_title = "mgmt 225 dashboard", layout = 'wide')
month_order = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov','Dec']

# import pandas dataset
@st.cache
def read_file():
    orders = pd.read_csv("orders.csv", encoding="ISO-8859-1")

    orders["Order_Date"] = pd.to_datetime(orders["Order_Date"]).dt.month
    orders["Order_Date"].replace([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 
                        month_order, inplace=True)
    
    return orders
@st.cache(suppress_st_warning = True)
def bar_plot(x, y, y_label = None, title = None, subtitle = None):
    b = (
        Bar()
        .add_xaxis(list(x))
        .add_yaxis(
            y_label, list(round(y,0)), color = '#00c04b'
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title, subtitle=subtitle
            )
            #toolbox_opts=opts.ToolboxOpts(),
        )
    )
    st_pyecharts(b)


orders = read_file()


st.markdown("""
<style>
.big-font {
    font-size:30px !important;
}
</style>
""", unsafe_allow_html=True)


# --- SIDE BAR -----------------------------#

st.sidebar.header("Please slice the data here:")

state = st.sidebar.multiselect(
    "Select the state",
    options = orders["State"].unique(),
    default = None
    )
st.markdown('###')

month = st.sidebar.multiselect(
    "Select the Month",
    options = orders["Order_Date"].unique(),
    default = None
    )


order_selection = orders.query(
    "State == @state & Order_Date == @month"
)


monthly_sales = pd.pivot_table(order_selection, values = "Revenue", index = "Order_Date", 
                                   aggfunc=np.sum, margins = False, margins_name = "Grand Total")

region_sales  = pd.pivot_table(order_selection, values = "Revenue", index = "State", 
                                   aggfunc=np.sum, margins = False, margins_name = "Grand Total")

cat_sales     = pd.pivot_table(order_selection, values = "Revenue", index = "Category", 
                                   aggfunc=np.sum, margins = False, margins_name = "Grand Total")

properties = {"font-size": "2px", 
                "font-family":'Arial'}

st.header("MGMT 225 Revenue Dashboard Example")
tab1, tab2 = st.tabs(['🚦Dashboard', '🎯Report'])



with tab1:
    try:
        col1, col2 = st.columns([8,16])
        
        with col1:
            col1.subheader('Total Revenue')
            grand_total = round(monthly_sales["Revenue"].sum(),2)
            delta_grand_total = round((grand_total-50000)/50000,2)
            col1.metric(label = "", value=f'${grand_total:,.2f}', delta=f'{delta_grand_total}% (Industry Benchmark)')
        
        with col2:
            col2.subheader('Monthly Revenue')
            monthly_sales = monthly_sales.reindex(month_order, axis=0)
            bar_plot(monthly_sales["Revenue"].index, monthly_sales["Revenue"], title = None, 
            subtitle = None)

        
        col3, col4 = st.columns([10, 10])
        with col3:
            col3.subheader('Revenue by State')
            fig = px.choropleth(locations=region_sales["Revenue"].index, 
                locationmode="USA-states", color=region_sales["Revenue"], 
                scope="usa", color_continuous_scale = 'emrld')
            fig.layout.coloraxis.colorbar.title = "Revenue"
            fig.update_layout(coloraxis_colorbar_x=-0.15)
            st.plotly_chart(fig)
            #bar_plot(region_sales["Revenue"].index, region_sales["Revenue"], title = None, 
            #subtitle="Revenue")

        with col4:
            col4.subheader('Revenue by Product Category')
            bar_plot(cat_sales["Revenue"].index, cat_sales["Revenue"], title="", 
            subtitle="Revenue")
            
    except Exception as e:
        st.markdown('<p class="big-font">  ⚠️ Please select the state and/or month </p>', unsafe_allow_html=True)  
        

with tab2:
        try:
                col1, col2 = st.columns([2,2])

                if monthly_sales.size or region_sales.size or cat_sales.size:

                    with col1:
                            col1.subheader("Monthly Sales")
                            monthly_sales["Revenue"] = monthly_sales["Revenue"].replace(np.nan, 0, regex = False)
                            st.table(monthly_sales.style.format(precision=2)) 

                    with col2:
                            col2.subheader("Sales by State")
                            st.table(region_sales.style.format(precision=2)) 
                    
                    col3, col4 = st.columns([2,2])
                    with col3:
                            col3.subheader("Sales by Product Category")
                            st.table(cat_sales.style.format(precision=2))
                      
                else:
                    st.markdown('<p class="big-font">  ⚠️ Please select the state and/or month </p>', unsafe_allow_html=True) 

        except Exception as e:
                st.write(e)
                #st.markdown('<p class="big-font">  ⚠️ Please select the state and/or month </p>', unsafe_allow_html=True)  



