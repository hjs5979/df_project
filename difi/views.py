from django.shortcuts import render, redirect
from .models import stock_info, stock_value
from .forms import UpperForm
# import FinanceDataReader as fdr
# import pandas as pd
# import numpy as np
# import scipy.stats as stats

def index(request):
    
    return render(request, 'difi/upper.html')

def search(request):
    return render(request, 'difi/search.html')
    

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
    
    
