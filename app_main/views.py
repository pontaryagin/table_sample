from django.http.response import Http404
from django_tables2 import tables, Column, TemplateColumn, SingleTableView, LazyPaginator, RequestConfig
import pandas as pd
from django.http import HttpResponse, Http404
import django_filters
from django_tables2.views import SingleTableMixin
from django.shortcuts import render
from django.views.generic import View
from django import forms
import re

class MyTable(tables.Table):
    name = Column(
        verbose_name="Col1",
    )

    value = Column(
        verbose_name="Col2",
        order_by='-value'
    )
    
    type = Column(
        verbose_name="Col3",
    )

    def render_value(self, value):
        return "{:,.2f}".format(value)
    class Meta:
        attrs = {
            'class': 'table  table-striped table-bordered  table-sm'
            }
        fields = ()

def csv_to_table(df_csv):
    list_table : list[dict] = []
    for index, row in df_csv.iterrows():
        list_temp : list[tuple] = []
        for i, v in row.iteritems():
            list_temp.append(tuple([i,v]))
        dict_temp = dict(list_temp)
        list_table.append(dict_temp)
    return list_table

def get_table(order, type):
    df = pd.read_csv('data/tmp.csv')
    print("type" , type)
    if type:
        df = df.query(f"type.str.match('{type}')")
    table = MyTable(csv_to_table(df), order_by=order)
    return table

class FilterForm(forms.Form):
    name = forms.CharField(label='Name', required=False)
    type = forms.CharField(label='Type', required=False)
    class Meta:
        fields = ('name', 'type',)
        

class TableRenderView(View):
    def get(self, request, *args, **kwargs):
        type = request.GET.get("type")
        order = request.GET.get("sort")
        try:
            type_pat = re.compile(type) if type else None
        except:
            form = FilterForm(request.GET)
            type = None
            form.add_error("type", "正規表現である必要があります。")
        else:
            form = FilterForm(initial=request.GET)

        table = get_table(order, type)
        return render(request, "page1.html", context={'form': form, 'table': table })

