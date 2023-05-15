from django.shortcuts import render, redirect
from .models import stock_info, stock_value, stock_ts
from .forms import StockValueForm, StockTsForm 
from django.db.models import Q
import FinanceDataReader as fdr
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers
import json
from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator

@csrf_exempt
def index(request):
    return HttpResponse("avc")

@csrf_exempt
def search(request, search_param):
    if request.method == 'GET':
        stock_info_list = stock_info.objects.filter(
            Q(ticker__icontains=search_param) |  # 제목 검색
            Q(stock_name__icontains=search_param)
        ).distinct()

        rl = serializers.serialize('json',stock_info_list)

        return HttpResponse(rl,content_type="application/json")
    
# @csrf_exempt
# def insert_ts(request, ):
#     return 1
#     #ticker
#     #id
#     #date
#     #close
    #change
@csrf_exempt
def get_one(request):
    
    if request.method=='GET':
        get_ticker = request.GET['ticker']
        # get_startDate = request.GET['startDate']
        # get_endDate = request.GET['endDate']
        # get_quantity = request.GET['quantity']
        stock = stock_info.objects.get(ticker=get_ticker)
        # ret = serializers.serialize('json', stock)
        # ts = fdr.DataReader(stockCode[0],startDate,endDate).filter(['Close','Change'])
        


        # instance = stock_ts.objects.create()

    return JsonResponse({'ticker':stock.ticker, 
                         'stock_name':stock.stock_name})
    #ts
    #startDate_close
    #endDate_close

@csrf_exempt
def add_one(request):
    if request.method=='POST':
        bod = json.loads(request.body)
        
        posted_ticker =  bod['ticker']
        posted_startDate = bod['startDate']
        posted_endDate = bod['endDate']
        
        posted_info = stock_info.objects.get(ticker=posted_ticker)
        
        ts = fdr.DataReader(posted_ticker,posted_startDate,posted_endDate).filter(['Close','Change'])
        
        ts = ts.reset_index()
        # print(posted_ticker, posted_startDate, posted_endDate)
        # print(ts)
        
        # a = ts.iloc[0]['Close']
        # b = ts.iloc[-1]['Close']
        
        # print(a,b)
        
        for i in range(len(ts)):
            ts_tuple = ts.iloc[i]
            # print(ts_tuple)
            stock_ts.objects.create(date=ts_tuple['Date'], close=ts_tuple['Close'], change=ts_tuple['Change'], ticker=posted_ticker)

        start_price = ts.iloc[0]['Close']
        end_price = ts.iloc[-1]['Close']
        
        stock_value.objects.create(ticker=posted_ticker, 
                                   stock_name=posted_info.stock_name,
                                   startDate_close=start_price,
                                   endDate_close=end_price
                                   )
        
        stock_value_list = stock_value.objects.all()
        ret = serializers.serialize('json', stock_value_list)
        
        return HttpResponse(ret, content_type="application/json")
    
    elif request.method=='GET':
        stock_value_list = stock_value.objects.all()
        ret = serializers.serialize('json', stock_value_list)
        
        return HttpResponse(ret, content_type="application/json")
    
    else:
        print(request.body)
        bod = json.loads(request.body)
        print(bod)
        # deleting_ticker = bod['ticker']
        
        # filter_stock_ts_list = stock_ts.objects.filter(ticker=deleting_ticker)
        
        # filter_stock_ts_list.delete()
        
        # filter_stock_value_list = stock_value.objects.filter(ticker=deleting_ticker)
        
        # filter_stock_value_list.delete()
        
        # stock_value_list = stock_value.objects.all()
        # ret = serializers.serialize('json', stock_value_list)
        
        
        
        # return HttpResponse(ret, content_type="application/json")
        
        
        
        
        
        
        
        
        



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
    
    
