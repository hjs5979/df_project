from django.shortcuts import render, redirect
from .models import stock, stock_value, stock_timestamp, user
# from .forms import StockValueForm, StockTsForm 
from django.db.models import Q
import FinanceDataReader as fdr
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers
import json
from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.db.models import F
import numpy as np
from django.db.models import StdDev, Avg
import pandas as pd
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from django.contrib.auth.hashers import make_password, check_password

@csrf_exempt
def index(request):
    return HttpResponse("avc")

@csrf_exempt
def select_stock_list(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        inq_content = request_body.get('inq_content')
        print(inq_content)
        # print(stock_list.wordId)
        stock_list = stock.objects.filter(
            Q(stock_ticker__icontains=inq_content) | 
            Q(stock_name__icontains=inq_content)
        ).distinct()

        result = serializers.serialize('json',stock_list)

        return HttpResponse(result,content_type="application/json")
    else:
        return HttpResponse("잘못된 방식입니다.")

@transaction.atomic
@csrf_exempt
def insert_stock(request):
    if request.method=='POST':
        request_body = json.loads(request.body)
        stock_ticker_in = request_body.get('stock_ticker')
        start_date_in  = request_body.get('start_date')
        end_date_in  = request_body.get('end_date')
        # stock_out = stock.objects.get(stock_ticker=stock_ticker_in)
        
        print(start_date_in)
        print(end_date_in)

        stock_ts = fdr.DataReader(stock_ticker_in,start_date_in,end_date_in).filter(['Close','Change'])
        
        # print(stock_timestamp)
        stock_ts = stock_ts.reset_index()
        
        
        # a = stock_timestamp.iloc[0]['Close']
        # b = stock_timestamp.iloc[-1]['Close']
        
        # print(a,b)
        
        for i in range(len(stock_ts)):
            stock_ts_tuple = stock_ts.iloc[i]
            # print(ts_tuple)
            stock_timestamp.objects.create(date=stock_ts_tuple['Date'], close=stock_ts_tuple['Close'], change=stock_ts_tuple['Change'], stock_ticker=stock_ticker_in, user_id_id='s6s6111')

        # start_date_close = stock_ts.loc[stock_ts['Date'] == start_date_in, 'Close'].values[0]
        start_date_close = stock_ts.iloc[0, 1]
        # end_date_close = stock_ts.loc[stock_ts['Date'] == start_date_in, 'Close'].values[0]
        end_date_close = stock_ts.iloc[-1, 1]
        
        # end_price = ts.iloc[-1]['Close']
        
        stock_value.objects.create(stock_ticker_id=stock_ticker_in,
                                   user_id_id='s6s6111',
                                   start_date=start_date_in,
                                   end_date=end_date_in,
                                   start_date_close=start_date_close,
                                   end_date_close=end_date_close
                                   )
        
        stock_value_list = stock_value.objects.all()
        result = serializers.serialize('json', stock_value_list)
        
        return HttpResponse(result, content_type="application/json")
    
    else :
        
        return HttpResponse('잘못된 요청입니다.')

@csrf_exempt
def select_stock_value_list(request):
    if request.method == 'POST':
        # request_body = json.loads(request.body)
        # user_id = request_body.get('')
        
        # stock_value_list = stock_value.objects.filter(user_id='s6s6111')

        # stock_value_list = stock_value.objects.prefetch_related('stock_ticker')
        # .filter(user_id='s6s6111')
        stock_value_list = stock_value.objects.select_related('stock_ticker').filter(user_id='s6s6111')
        
        result = json.dumps(list(stock_value_list.values('stock_ticker','start_date','end_date','start_date_close','end_date_close','quantity','start_date_close_total','end_date_close_total','profit_loss','return_rate','weight','stock_ticker__stock_name')), default=str)

        return HttpResponse(result, content_type="application/json")
    else:
        return HttpResponse("잘못된 요청 방식입니다.")

@transaction.atomic
@csrf_exempt
def delete_stock(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        stock_ticker_in = request_body.get('stock_ticker')
        user_id = 's6s6111'

        stock_timestamp_out = stock_timestamp.objects.filter(stock_ticker=stock_ticker_in, user_id=user_id)
        stock_timestamp_out.delete()

        stock_value_out = stock_value.objects.get(stock_ticker=stock_ticker_in, user_id=user_id)
        stock_value_out.delete()

        return HttpResponse('1', content_type="application/json")
    else:
        return HttpResponse("잘못된 요청 방식입니다.")

@transaction.atomic
@csrf_exempt
def update_stock(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        stock_list = request_body.get('stock_list')
        # print(stock_list)
        for i in stock_list:
            if stock_value.objects.filter(stock_ticker=i['stock_ticker'], user_id='s6s6111').exists():
                # print(i)
                stock_value.objects.filter(stock_ticker=i['stock_ticker'], user_id='s6s6111').update(quantity=int(i["quantity"]))
                # stock_value.objects.filter(stock_ticker=i['stock_ticker'], user_id='s6s6111').update(weight=float(i["weight"]))
                stock_value.objects.filter(stock_ticker=i['stock_ticker'], user_id='s6s6111').update(start_date_close_total=i["start_date_close_total"])
                stock_value.objects.filter(stock_ticker=i['stock_ticker'], user_id='s6s6111').update(end_date_close_total=i["end_date_close_total"])
                stock_value.objects.filter(stock_ticker=i['stock_ticker'], user_id='s6s6111').update(profit_loss=i["profit_loss"])
                stock_value.objects.filter(stock_ticker=i['stock_ticker'], user_id='s6s6111').update(return_rate=i["return_rate"])

            else:
                print('error')
            

        return HttpResponse('1', content_type="application/json")
    else:
        return HttpResponse("잘못된 요청 방식입니다.")
    
@transaction.atomic
@csrf_exempt
def calc_stock(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        stock_list = request_body.get('stock_list')
        
        if len(stock_list) > 0:

            kospi_index = fdr.DataReader("KS11",stock_list[0].get("start_date"),stock_list[0].get("end_date")).filter(['Change'])

            kospi_std = np.std(kospi_index["Change"])

            kospi_avg = np.average(kospi_index["Change"])

            kospi_coef = (kospi_std / kospi_avg)

            
            # print(kospi_std, kospi_avg, kospi_coef)
        else:
            print("error")

        grand_start_total= 0
        grand_end_total = 0

        stock_std_sum = 0
        stock_coef_sum = 0

        stock_ts_obj = {}

        stock_df_all = pd.DataFrame([])

        weights = np.array([])

        for i in stock_list:

            grand_start_total += i["start_date_close_total"]
            grand_end_total += i["end_date_close_total"]

            stock_ts = stock_timestamp.objects.filter(stock_ticker=i["stock_ticker"], user_id="s6s6111")

            stock_ts_list = []
            
            stock_name = stock.objects.get(stock_ticker=i["stock_ticker"]).stock_name
            
            weights = np.append(weights, i["start_date_close_total"])

            for obj in stock_ts:
                data = { 'date' : str(obj.date), 'close' : obj.close}  # 필드의 값을 리스트에 추가 (field_name은 필드명)
                stock_ts_list.append(data)
                
            stock_ts_obj[stock_name] = stock_ts_list
            
            stock_list = list(stock_timestamp.objects.filter(stock_ticker=i["stock_ticker"], user_id="s6s6111").values("date", "close"))

            stock_df = pd.DataFrame.from_records(stock_list)

            stock_df = stock_df.set_index(keys=['date'], inplace=False, drop=True).rename(columns={"close":stock_name})

            if stock_df_all.empty:
                stock_df_all = stock_df
            
            else:
                stock_df_all = pd.merge(stock_df_all, stock_df, left_index=True, right_index=True)
            
            print("stock_df_all => ", stock_df_all)
            
            # stock_std = stock_timestamp.objects.filter(stock_ticker=i["stock_ticker"], user_id="s6s6111").aggregate(std_dev=StdDev('change'))['std_dev']
            # stock_avg = stock_timestamp.objects.filter(stock_ticker=i["stock_ticker"], user_id="s6s6111").aggregate(avg_value=Avg('change'))['avg_value']
            # stock_coef = (stock_std / stock_avg)
            # print(stock_avg)
            # stock_std_sum += stock_std
            # stock_coef_sum += stock_coef

        #투자비율
        weights /= grand_start_total

        # print(stock_df_all)

        # 연환산수익률
        mu = expected_returns.mean_historical_return(stock_df_all, frequency=len(stock_df_all))

        #공분산 행렬
        s = risk_models.sample_cov(stock_df_all, frequency=len(stock_df_all))

        stock_var = np.dot(weights.T, np.dot(s, weights))

        stock_std = np.sqrt(stock_var)

        ef = EfficientFrontier(mu, s)
        
        risk_free_rate = 0.04

        try:
            weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
            print("case1")
            
        except:
            weights = ef.max_sharpe(risk_free_rate=-1)
            print("case2")
            risk_free_rate=-1
            
        cleaned_weights = ef.clean_weights()
        
        ef.portfolio_performance(verbose=True)

        latest_prices = get_latest_prices(stock_df_all).astype(float)
        
        weights = cleaned_weights
        
        da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=grand_start_total)

        # allocation, leftover = da.lp_portfolio(verbose=True)

        allocation, leftover = da.greedy_portfolio(verbose=True)
        
        total_profit_loss = grand_end_total - grand_start_total
        total_return_rate = total_profit_loss/grand_start_total

        # stock_std_avg = stock_std_sum/len(stock_list)
        # stock_coef_avg = stock_coef_sum/len(stock_list)
        
        print(mu.to_dict())
        # json_data = json.dumps(stock_ts_obj)

        # print(stock_std_avg, stock_coef_avg)

        # stock_ts_list = serializers.serialize('json', stock_ts_list)

        # data = {"grand_start_total": grand_start_total,"grand_end_total":grand_end_total, "total_profit_loss":total_profit_loss,"total_return_rate":total_return_rate, "kospi_std": float(kospi_std), "kospi_coef":float(kospi_coef), "stock_std_avg":float(stock_std_avg), "stock_coef_avg":float(stock_coef_avg), "stock_ts_list":stock_ts_obj}
        data = {"grand_start_total": grand_start_total,"grand_end_total":grand_end_total, "total_profit_loss":total_profit_loss,"total_return_rate":total_return_rate, "kospi_std": float(kospi_std), "kospi_coef":float(kospi_coef), "AHPR":mu.to_dict(), "stock_var":stock_var, "stock_std":stock_std, "risk_free_rate":risk_free_rate, "allocation":allocation, "leftover":leftover ,"stock_ts_list":stock_ts_obj}
        
        json_data = json.dumps(data)

        return HttpResponse(json_data, content_type="application/json")
        # return JsonResponse(json_data, safe=False)
    else:
        return HttpResponse("잘못된 요청 방식입니다.")

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # 로그인 후 리다이렉트할 URL
        else:
            return render(request, 'login.html', {'error': '유효하지 않은 사용자입니다.'})
    else:
        return render(request, 'login.html')

@csrf_exempt
def id_check(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        user_id_in = request_body.get('id')
        cnt = user.objects.filter(user_id = user_id_in).count()
        print(cnt)
        value = 1
        if cnt == 0:
            value = 0
            return HttpResponse(value, content_type="application/json")
        else:
            
            return HttpResponse(value, content_type="application/json")
    else:
        return HttpResponse("잘못된 요청 방식입니다.")

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        user_id_in = request_body.get('userId')
        user_password_in = request_body.get('userPassword')
        user_name_in = request_body.get('userName')
        user_email_in = request_body.get('userEmail')

        encoded_password = make_password(user_password_in)

        yn = check_password(encoded_password, user_password_in)

        print(yn)

    return HttpResponse("잘못된 요청 방식입니다.")

        # user.objects.create(user_name=user_name_in,
        #                     user_password=encoded_password,
        #                     user_id=user_id_in,
        #                     user_emial=user_email_in,
        #                     )
# @csrf_exempt:
# def select_stock_list(request, search_param):
#     # if request.method == 'GET':
#     #     stock_info_list = stock_info.objects.filter(
#     #         Q(ticker__icontains=search_param) |  # 제목 검색
#     #         Q(stock_name__icontains=search_param)
#     #     ).distinct()

#     #     rl = serializers.serialize('json',stock_info_list)

#         return HttpResponse("",content_type="application/json")
    
# @csrf_exempt
# def insert_ts(request, ):
#     return 1
#     #ticker
#     #id
#     #date
#     #close
    #change
# @csrf_exempt
# def get_one(request):
    
    # if request.method=='GET':
    #     get_ticker = request.GET['ticker']
        # get_startDate = request.GET['startDate']
        # get_endDate = request.GET['endDate']
        # get_quantity = request.GET['quantity']
        # stock = stock_info.objects.get(ticker=get_ticker)
        # ret = serializers.serialize('json', stock)
        # ts = fdr.DataReader(stockCode[0],startDate,endDate).filter(['Close','Change'])
        


        # instance = stock_ts.objects.create()

    # return JsonResponse({'ticker':stock.ticker, 
    #                      'stock_name':stock.stock_name})
     
    #  return JsonResponse({'ticker':'', 
    #                      'stock_name':''})
    #ts
    #startDate_close
    #endDate_close

# @csrf_exempt
# def add_one(request):
    # if request.method=='POST':
    #     bod = json.loads(request.body)
        
    #     posted_ticker =  bod['ticker']
    #     posted_startDate = bod['startDate']
    #     posted_endDate = bod['endDate']
        
    #     posted_info = stock_info.objects.get(ticker=posted_ticker)
        
    #     ts = fdr.DataReader(posted_ticker,posted_startDate,posted_endDate).filter(['Close','Change'])
        
    #     ts = ts.reset_index()
        # print(posted_ticker, posted_startDate, posted_endDate)
        # print(ts)
        
        # a = ts.iloc[0]['Close']
        # b = ts.iloc[-1]['Close']
        
        # print(a,b)
        
    #     for i in range(len(ts)):
    #         ts_tuple = ts.iloc[i]
    #         # print(ts_tuple)
    #         stock_ts.objects.create(date=ts_tuple['Date'], close=ts_tuple['Close'], change=ts_tuple['Change'], ticker=posted_ticker)

    #     start_price = ts.iloc[0]['Close']
    #     end_price = ts.iloc[-1]['Close']
        
    #     stock_value.objects.create(ticker=posted_ticker, 
    #                                stock_name=posted_info.stock_name,
    #                                startDate_close=start_price,
    #                                endDate_close=end_price
    #                                )
        
    #     stock_value_list = stock_value.objects.all()
    #     ret = serializers.serialize('json', stock_value_list)
        
    #     return HttpResponse(ret, content_type="application/json")
    
    # elif request.method=='GET':
    #     stock_value_list = stock_value.objects.all()
    #     ret = serializers.serialize('json', stock_value_list)
        
        # return HttpResponse('', content_type="application/json")
    
# @csrf_exempt
# def delete_one(request, delete_param):
    # if request.method == 'DELETE':
    #     delete_ts_list = stock_ts.objects.filter(ticker=delete_param)

    #     delete_ts_list.delete()

    #     delete_value_list = stock_value.objects.get(ticker=delete_param)

    #     delete_value_list.delete()

    #     stock_value_list = stock_value.objects.all()
    #     ret = serializers.serialize('json', stock_value_list)

        # return HttpResponse('', content_type="application/json")
        
        
        
        
        
        
        
        



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