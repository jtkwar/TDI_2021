# -*- coding: utf-8 -*-
"""
Created on Sun May 16 16:50:07 2021

@author: stark
"""
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import plotly.express as px


def homepage_app():
    st.title("Washington State Cannabis Analytics")
    st.header("TDI Spring Cohort 2021")
    st.subheader("Jeffrey Kwarsick, PhD")
    
def single_company_stats():
    # open the licensees .csv file
    license_info = "Licensees_0.csv"
    # load saved list of dispersaries ids, sorted by number of sales
    with open("sorted_dispo_sale_counts.pkl", 'rb') as f:
        dispos_list = pickle.load(f)
    
    # current number of processed companies
    n = 11
    # grab only the mme_id for each dispenary that has been processed
    current_dispos = [dispos_list[i][0] for i in range(n)]
    
    license_df = pd.read_csv(license_info)
    # keep only some information for now
    license_df = license_df[['global_id', 'name', 'address1', 'address2', 'city']]
    # keep only processed companies in the list
    license_df = license_df[license_df["global_id"].isin(current_dispos)]
    ######################################################################################
    ######################################################################################
    st.title("Company Stats")
    city = st.selectbox("Select City", list(license_df["city"].unique()))
    company = st.selectbox("Select Company", list(license_df[license_df['city'] == city]["name"]))
    # return selected company information
    st.table(license_df.loc[license_df['name'] == str(company)])
    ######################################################################################
    # contruct everything we need to build open the files
    mme_id_string = str(license_df[license_df["name"] == str(company)]["global_id"].item())
    dispo_sales_load_string = "dispo_sales_data_repo"
    final_string = os.path.join(os.getcwd(), dispo_sales_load_string)
    # loads the cleaned .csv file for sales for each company
    company_df = pd.read_csv(final_string + "/sales_" + mme_id_string + ".csv", error_bad_lines=False)
    # convert date column to a datetime
    company_df['sold_at'] = company_df['sold_at'].astype('datetime64[ns]')
    
    # compute number of sales: recreational vs medical
    sale_type_breakdown = company_df["type"].value_counts()
    st.header("Sales Type Breakdown")
    st.table(sale_type_breakdown)
    
    # resample dictionary
    resample_dict = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M', 'Quarterly': 'Q',
                     'Yearly': 'Y'}
    st.header("Sales Data Visualization")
    tp_selection = st.selectbox("Select Time Period Sampling", list(resample_dict.keys()))
    
    medical_df = company_df[company_df['type'] == 'retail_medical'].set_index('sold_at').resample(resample_dict[tp_selection]).sum()
    rec_df = company_df[company_df['type'] == 'retail_recreational'].set_index('sold_at').resample(resample_dict[tp_selection]).sum()
    total_sales = company_df.set_index('sold_at').resample(resample_dict[tp_selection]).sum()
    if tp_selection == 'Daily' or tp_selection == 'Weekly' or tp_selection == 'Monthly':
        f = px.line(total_sales,
                    x=total_sales.index,
                    y=total_sales.iloc[:,0],
                    title="{0} {1} Sales (Recreational and Medical)".format(company, tp_selection))
        f.update_traces(mode="markers+lines")
        g = px.line(medical_df,
                    x=medical_df.index,
                    y=medical_df.iloc[:,0],
                    title="{0} {1} Medical Retail Sales".format(company, tp_selection))        
        g.update_traces(mode="markers+lines")
    else:
        f = px.bar(total_sales, x=total_sales.index, y=total_sales.iloc[:,0])
        g = px.bar(medical_df, x=medical_df.index, y=medical_df.iloc[:,0])
        #f.add_bar(rec_df, x=rec_df.index, y=rec_df.iloc[:,0])
    f.update_xaxes(title="Date")
    f.update_yaxes(title="Total Sales, USD")
    g.update_xaxes(title="Date")
    g.update_yaxes(title="Total Sales, USD")
    st.plotly_chart(f)
    st.plotly_chart(g)
    
def company_comparison():
    st.title("Company Comparison")
    
    
    