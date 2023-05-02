from django.shortcuts import render, redirect
from .models import stock_info, stock_value, stock_ts
from .forms import StockValueForm, StockTsForm 
from django.db.models import Q
import FinanceDataReader as fdr
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers

def search(request, search_param):
    if request.method == 'GET':
        stock_info_list = stock_info.objects.filter(
            Q(ticker__icontains=search_param) |  # 제목 검색
            Q(stock_name__icontains=search_param)
        ).distinct()

        rl = serializers.serialize('json',stock_info_list)

        return HttpResponse(rl,content_type="application/json")

def insert_ts(request):
        #ticker
        #id
        #date
        #close
        #change

def get_one(request):
    stocks = fdr.DataReader().filter(['Close','Change'])

    return
    #ts
    #startDate_close
    #endDate_close


def add_one(request):
    if request.method == 'POST':
        #ticker
        #stock_name
        
        #startDate
        #endDate

        #quantity

    return
        




        #start_value
        #end_value
        #ugl
        #return_rate



# import pandas as pd
# import numpy as np
# import scipy.stats as stats

# def index(request):
#     return render(request, 'difi/upper.html')

# def search(request):
#     kw = request.GET.get('kw', '')
#     stock_info_list = stock_info.objects.all()
#     if kw:
#         stock_info_list = stock_info_list.filter(
#             Q(ticker__icontains=kw) |  # 제목 검색
#             Q(stock_name__icontains=kw)
#         ).distinct()
#     context = {'stock_info_list':stock_info_list,'kw': kw}
#     return render(request, 'difi/upper.html', context)
    

# def stock_add(request, stock_info_ticker):
#     if request.method == 'POST':
#         sv_form = StockValueForm(request.POST)
#         if form.is_valid():
#             sv_form = sv_form.save(commit=False)
#             stocks = fdr.DataReader(sv_form.ticker,sv_form.startDate,sv_form.endDate).filter(['Close','Change'])
#             for stock in range(len(stocks)):
#                 a = stock_ts(Close=stock["Close"],Change=stock["Change"])
                
            
#             sv_form.save()
#             return redirect('difi:index')
#     else:
#         form = UpperForm()
#     context = {'form': form}
#     return render(request, 'difi/upper.html', context)
    
    
