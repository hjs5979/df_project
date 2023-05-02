from django.shortcuts import render, redirect
from .models import stock_info, stock_value
from .forms import UpperForm
from django.db.models import Q
# import FinanceDataReader as fdr
# import pandas as pd
# import numpy as np
# import scipy.stats as stats

def index(request):
    
    return render(request, 'difi/upper.html')

def search(request):
    # kw = request.GET.get('kw', '')
    kw = '삼성전자'
    stock_info_list = stock_info.objects
    if kw:
        stock_info_list = stock_info_list.filter(
            Q(ticker__icontains=kw) |  # 제목 검색
            Q(stock_name__icontains=kw)
        ).distinct()
    context = {'stock_info_list':stock_info_list,'kw': kw}
    return render(request, 'difi/upper.html', context)
    

# def stock_add(request, stock_info_id):
#     if request.method == 'POST':
#         form = UpperForm(request.POST)
#         if form.is_valid():
#             sv = form.save(commit=False)
#             sv.save()
#             return redirect('difi:index')
#     else:
#         form = UpperForm()
#     context = {'form': form}
#     return render(request, 'difi/upper.html', context)
    
    
