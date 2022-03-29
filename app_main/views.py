from typing import *
from django.http.response import FileResponse, Http404
from django_tables2 import tables, Column, TemplateColumn, SingleTableView, LazyPaginator, RequestConfig
import pandas as pd
from django.http import HttpResponse, Http404
import django_filters
from django_tables2.views import SingleTableMixin
from django.shortcuts import render
from django.views.generic import View
from django import forms
import re
import io
import os
from app_main.settings import BASE_DIR
from pathlib import Path
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import time

class MyTable(tables.Table):
    count = 0
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
        # time.sleep(10/100)
        self.count += 1
        print(self.count)
        return f"count={self.count};"+"{:,.2f}".format(value)
    class Meta:
        attrs = {
            'class': 'table  table-striped table-bordered  table-sm'
            }
        fields = ()

def get_df(type, name):
    df = pd.read_csv(f'data/{name}.csv')
    print("type" , type)
    dfs = []
    for i in range(1000):
        dfs.append(df)
    df = pd.concat(dfs)
    if type:
        df = df.query(f"type.str.match('{type}')")
    return df


def get_table(order, type,name):
    df = get_df(type,name)
    print("df obtained")
    # mod below
    # table = MyTable(df.to_dict('records'), order_by=order)
    # return table
    if order is not None:
        df.sort_values(order, inplace=True)
    return df.to_dict('records')

class FilterForm(forms.Form):
    name = forms.CharField(label='Name', required=False)
    type = forms.CharField(label='Type', required=False)
    class Meta:
        fields = ('name', 'type',)


T = TypeVar('T') 
def get_page_object(objs: List[T], each_page_num: int, page_num: int):
    # get pagination
    paginator = Paginator(objs, each_page_num)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj

class TableRenderView(View):
    def get(self, request, *args, **kwargs):
        name = request.GET.get("name")
        type = request.GET.get("type")
        order = request.GET.get("sort")
        page_num = request.GET.get("page")
        try:
            type_pat = re.compile(type) if type else None
        except:
            form = FilterForm(request.GET)
            type = None
            form.add_error("type", "正規表現である必要があります。")
        else:
            form = FilterForm(initial=request.GET)

        # mod here
        # table = get_table(order, type, name)
        # print("get_table end")
        # table = RequestConfig(request, paginate={"per_page": 10}).configure(table)
        # print("RequestConfig end")
        # o = render(request, "page1.html", context={'form': form, 'table': table })
        # print("render end")
        # return o

        table_records = get_table(order, type, name)
        print("get_table end")
        page_obj = get_page_object(table_records, 10, page_num)
        print("get_page_object end")
        table = MyTable(page_obj, order)
        print("MyTable end")
        # table = RequestConfig(request, paginate={"per_page": 100}).configure(table)
        return render(request, "page1.html", 
            context={'form': form, 'table': table, 'items': page_obj.object_list, 'page_obj': page_obj  })

class DowloadView(View):
    def get(self, request, *args, **kwargs):
        path = kwargs.get("path")
        buf = io.BytesIO()
        df = get_df(None)
        df.to_csv(buf)
        buf.seek(0)
        response = FileResponse(buf)
        return response

class CategoryRenderView(View):
    def get(self, request, *args, **kwargs):
        items:list = []
        page_num = request.GET.get('page')
        for file in (BASE_DIR / "data").iterdir():
            name = file.stem
            items.append({"name": name, "url": f"/page1/?name={name}"})
        page_obj = get_page_object(items, 3, page_num)
        return render(request, "category.html", context={'items': page_obj.object_list, 'page_obj': page_obj })

