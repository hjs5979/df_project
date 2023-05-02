from django.shortcuts import render, redirect
from .models import stock_info, stock_value, stock_ts
from .forms import StockValueForm, StockTsForm 
from django.db.models import Q
import FinanceDataReader as fdr
# import pandas as pd
# import numpy as np
# import scipy.stats as stats

def index(request):
    return render(request, 'difi/upper.html')

def search(request):
    kw = request.GET.get('kw', '')
    stock_info_list = stock_info.objects.all()
    if kw:
        stock_info_list = stock_info_list.filter(
            Q(ticker__icontains=kw) |  # 제목 검색
            Q(stock_name__icontains=kw)
        ).distinct()
    context = {'stock_info_list':stock_info_list,'kw': kw}
    return render(request, 'difi/upper.html', context)
    

def stock_add(request, stock_info_ticker):
    if request.method == 'POST':
        sv_form = StockValueForm(request.POST)
        st_form = StockTsForm(request.POST)
        if form.is_valid():
            sv_form = sv_form.save(commit=False)
            st_form = st_form.save(commit=False)
            stock = fdr.DataReader(stockCode[i],startDate,endDate).filter(['Close','Change'])
            
            
            sv_form.save()
            return redirect('difi:index')
    else:
        form = UpperForm()
    context = {'form': form}
    return render(request, 'difi/upper.html', context)
    
    
