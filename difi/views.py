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
import jwt
from django.conf import settings
from datetime import datetime, timedelta
import bcrypt
from django.utils.crypto import get_random_string
from django.core.cache import cache

@csrf_exempt
def index(request):
    return HttpResponse("avc")

@csrf_exempt
def select_stock_list(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        inq_content = request_body.get('inq_content')

        if inq_content is None:
            return HttpResponse(error_message(data="inq_content", code="001"), status=500)

        stock_list = stock.objects.filter(
            Q(stock_ticker__icontains=inq_content) | 
            Q(stock_name__icontains=inq_content)
        ).distinct()

        result = serializers.serialize('json',stock_list)

        return HttpResponse(result,content_type="application/json")
    else:
        return HttpResponse(error_message(code=100), status=500)

@transaction.atomic
@csrf_exempt
def insert_stock(request):
    if request.method=='POST':
        request_body = json.loads(request.body)
        stock_ticker_in = request_body.get('stock_ticker')
        start_date_in  = request_body.get('start_date')
        end_date_in  = request_body.get('end_date')
        user_id_in = request_body.get('user_id')

        if stock_ticker_in is None or stock_ticker_in == "":
            return HttpResponse(error_message(data="stock_ticker", code="001"), status=500)
        if start_date_in is None or start_date_in == "":
            return HttpResponse(error_message(data="start_date", code="001"), status=500)
        if end_date_in is None or end_date_in == "":
            return HttpResponse(error_message(data="end_date", code="001"), status=500)
        if user_id_in is None or user_id_in == "":
            return HttpResponse(error_message(data="user_id", code="001"), status=500)
        
        stock_ts = fdr.DataReader(stock_ticker_in,start_date_in,end_date_in).filter(['Close','Change'])

        if stock_ts is None or len(stock_ts) == 0:
            return HttpResponse(error_message(code="002", content="stock_ts is empty"), status=500)

        stock_ts = stock_ts.reset_index()
        
        for i in range(len(stock_ts)):
            stock_ts_tuple = stock_ts.iloc[i]
            stock_timestamp.objects.create(date=stock_ts_tuple['Date'], close=stock_ts_tuple['Close'], change=stock_ts_tuple['Change'], stock_ticker=stock_ticker_in, user_id_id=user_id_in)
        
        start_date_close = stock_ts.iloc[0, 1]
        end_date_close = stock_ts.iloc[-1, 1]
        
        stock_value.objects.create(stock_ticker_id=stock_ticker_in,
                                   user_id_id=user_id_in,
                                   start_date=start_date_in,
                                   end_date=end_date_in,
                                   start_date_close=start_date_close,
                                   end_date_close=end_date_close
                                   )
        
        stock_value_list = stock_value.objects.all()
        result = serializers.serialize('json', stock_value_list)
        
        return HttpResponse(result, content_type="application/json")
    
    else :
        
        return HttpResponse(error_message(code=100), status=500)

@csrf_exempt
def select_stock_value_list(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        user_id_in = request_body.get('user_id')

        if user_id_in is None or user_id_in == "":
            return HttpResponse(error_message(data="user_id", code="001"), status=500)

        stock_value_list = stock_value.objects.select_related('stock_ticker').filter(user_id=user_id_in)
        
        result = json.dumps(list(stock_value_list.values('stock_ticker','start_date','end_date','start_date_close','end_date_close','quantity','start_date_close_total','end_date_close_total','profit_loss','return_rate','weight','stock_ticker__stock_name')), default=str)

        return HttpResponse(result, content_type="application/json")
    else:
        return HttpResponse(error_message(code=100), status=500)

@transaction.atomic
@csrf_exempt
def delete_stock(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        stock_ticker_in = request_body.get('stock_ticker')
        user_id_in = request_body.get('user_id')

        if stock_ticker_in is None or stock_ticker_in == "":
            return HttpResponse(error_message(data="stock_ticker", code="001"), status=500)
        if user_id_in is None or user_id_in == "":
            return HttpResponse(error_message(data="user_id", code="001"), status=500)

        stock_timestamp_out = stock_timestamp.objects.filter(stock_ticker=stock_ticker_in, user_id=user_id_in)
        
        if not stock_timestamp_out.exists():
            return HttpResponse(error_message(code="003", content="stock_timestamp is no data"), status=500)
        
        stock_timestamp_out.delete()

        stock_value_out = stock_value.objects.get(stock_ticker=stock_ticker_in, user_id=user_id_in)
        
        if not stock_value_out.exists():
            return HttpResponse(error_message(code="003", content="stock_value is no data"), status=500)

        stock_value_out.delete()

        return HttpResponse('success', content_type="application/json")
    else:
        return HttpResponse(error_message(code=100), status=500)

@transaction.atomic
@csrf_exempt
def update_stock(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        stock_value_list = request_body.get('stock_value_list')
        user_id_in = request_body.get('user_id')

        if stock_value_list is None or len(stock_value_list) < 1:
            return HttpResponse(error_message(data="stock_value_list", code="001"), status=500)
        if user_id_in is None or user_id_in == "":
            return HttpResponse(error_message(data="user_id", code="001"), status=500)

        for i in stock_value_list:
            if stock_value.objects.filter(stock_ticker=i['stock_ticker'], user_id=user_id_in).exists():
                stock_value.objects.filter(stock_ticker=i['stock_ticker'], user_id=user_id_in).update(quantity=int(i["quantity"]))
                stock_value.objects.filter(stock_ticker=i['stock_ticker'], user_id=user_id_in).update(start_date_close_total=i["start_date_close_total"])
                stock_value.objects.filter(stock_ticker=i['stock_ticker'], user_id=user_id_in).update(end_date_close_total=i["end_date_close_total"])
                stock_value.objects.filter(stock_ticker=i['stock_ticker'], user_id=user_id_in).update(profit_loss=i["profit_loss"])
                stock_value.objects.filter(stock_ticker=i['stock_ticker'], user_id=user_id_in).update(return_rate=i["return_rate"])

            else:
                return HttpResponse(error_message(code="003", content="stock_value is no data"), status=500)
            

        return HttpResponse('success', content_type="application/json")
    else:
        return HttpResponse(error_message(code=100), status=500)
    
@transaction.atomic
@csrf_exempt
def calc_stock(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        stock_value_list = request_body.get('stock_value_list')
        user_id_in = request_body.get('user_id')

        if stock_value_list is None or len(stock_value_list) < 1:
            return HttpResponse(error_message(data="stock_value_list", code="001"), status=500)
        if user_id_in is None or user_id_in == "":
            return HttpResponse(error_message(data="user_id", code="001"), status=500)

        kospi_index = fdr.DataReader("KS11",stock_value_list[0].get("start_date"),stock_value_list[0].get("end_date")).filter(['Change'])

        if kospi_index is None or len(kospi_index) < 1:
            return HttpResponse(error_message(code="003", content="kospi_index is no data"), status=500)

        kospi_std = np.std(kospi_index["Change"])
        kospi_avg = np.average(kospi_index["Change"])
        kospi_coef = (kospi_std / kospi_avg)

        grand_start_total= 0
        grand_end_total = 0

        stock_std_sum = 0
        stock_coef_sum = 0

        stock_ts_obj = {}

        stock_df_all = pd.DataFrame([])

        weights = np.array([])

        for i in stock_value_list:

            grand_start_total += i["start_date_close_total"]
            grand_end_total += i["end_date_close_total"]

            stock_ts = stock_timestamp.objects.filter(stock_ticker=i["stock_ticker"], user_id=user_id_in)

            if not stock_ts.exists():
                return HttpResponse(error_message(code="003", content="stock_ts is no data"), status=500)

            stock_ts_list = []
            
            stock_name = stock.objects.get(stock_ticker=i["stock_ticker"]).stock_name
            
            if stock_name is None or stock_name == "":
                return HttpResponse(error_message(data="stock_name", code="001"), status=500)

            weights = np.append(weights, i["start_date_close_total"])

            for obj in stock_ts:
                data = { 'date' : str(obj.date), 'close' : obj.close}  # 필드의 값을 리스트에 추가 (field_name은 필드명)
                stock_ts_list.append(data)
                
            stock_ts_obj[stock_name] = stock_ts_list
            
            stock_timestamp_list = stock_timestamp.objects.filter(stock_ticker=i["stock_ticker"], user_id=user_id_in)

            if not stock_timestamp_list.exists():
                return HttpResponse(error_message(code="003", content="stock_timestamp is no data"), status=500)

            stock_list = list(stock_timestamp_list.values("date", "close"))

            stock_df = pd.DataFrame.from_records(stock_list)
            
            stock_df = stock_df.set_index(keys=['date'], inplace=False, drop=True).rename(columns={"close":stock_name})

            if stock_df_all.empty:
                stock_df_all = stock_df
            
            else:
                stock_df_all = pd.merge(stock_df_all, stock_df, left_index=True, right_index=True)

        weights /= grand_start_total

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
            
        except:
            weights = ef.max_sharpe(risk_free_rate=-1)
            risk_free_rate=-1
            
        cleaned_weights = ef.clean_weights()
        
        ef.portfolio_performance(verbose=True)

        latest_prices = get_latest_prices(stock_df_all).astype(float)
        
        weights = cleaned_weights
        
        da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=grand_start_total)

        allocation, leftover = da.greedy_portfolio(verbose=True)
        
        total_profit_loss = grand_end_total - grand_start_total
        total_return_rate = total_profit_loss/grand_start_total

        data = {"grand_start_total": grand_start_total,"grand_end_total":grand_end_total, "total_profit_loss":total_profit_loss,"total_return_rate":total_return_rate, "kospi_std": float(kospi_std), "kospi_coef":float(kospi_coef), "AHPR":mu.to_dict(), "stock_var":stock_var, "stock_std":stock_std, "risk_free_rate":risk_free_rate, "allocation":allocation, "leftover":leftover ,"stock_ts_list":stock_ts_obj}
        
        json_data = json.dumps(data)

        return HttpResponse(json_data, content_type="application/json")
        
    else:
        return HttpResponse(error_message(code=100), status=500)

@transaction.atomic
@csrf_exempt
def login(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        
        user_id_in = request_body.get('user_id')
        user_password_in = request_body.get('user_password')
        
        if user_id_in is None or user_id_in == "":
            return HttpResponse(error_message(data="user_id", code="001"), status=500)
        if user_password_in is None or user_password_in == "":
            return HttpResponse(error_message(data="user_password", code="001"), status=500)

        userObj = user.objects.filter(user_id = user_id_in)

        chk = False

        if userObj.count() == 1:
            chk = check_password(user_password_in, userObj.first().user_password)
        else:
            return HttpResponse(error_message(code="200", content="user is not valid"), status=500)
        
        if chk == False:
            return HttpResponse(error_message(code="201", content="password is not correct"), status=500)
        else:
            access_token = create_jwt_token(user_id_in)
            refresh_token = get_random_string(length=32)
            
            redis_data = {
                'access_token': access_token,
                'user_id': user_id_in,
            }

            cache.set(refresh_token, redis_data)
            
            token_data = {"refresh_token" : refresh_token, "access_token" : access_token}

            json_data = json.dumps(token_data)

            return HttpResponse(json_data, content_type="application/json") 

    else:
        return HttpResponse(error_message(code=100), status=500)

@transaction.atomic
@csrf_exempt
def id_check(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        user_id_in = request_body.get('id')

        if user_id_in is None or user_id_in == "":
            return HttpResponse(error_message(data="user_id", code="001"), status=500)

        cnt = user.objects.filter(user_id = user_id_in).count()
        
        value = 1

        if cnt == 0:
            value = 0

            return HttpResponse(value, content_type="application/json")
        else:
            
            return HttpResponse(value, content_type="application/json")
    else:
        return HttpResponse(error_message(code=100), status=500)

@transaction.atomic
@csrf_exempt
def signup(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        user_id_in = request_body.get('userId')
        user_password_in = request_body.get('userPassword')
        user_name_in = request_body.get('userName')
        user_email_in = request_body.get('userEmail')

        if user_id_in is None or user_id_in == "":
            return HttpResponse(error_message(data="user_id", code="001"), status=500)
        if user_password_in is None or user_password_in == "":
            return HttpResponse(error_message(data="user_password", code="001"), status=500)
        if user_name_in is None or user_name_in == "":
            return HttpResponse(error_message(data="user_name", code="001"), status=500)
        if user_email_in is None or user_email_in == "":
            return HttpResponse(error_message(data="user_email", code="001"), status=500)

        encoded_password = make_password(user_password_in)

        user.objects.create(user_name=user_name_in,
                            user_password=encoded_password,
                            user_id=user_id_in,
                            user_email=user_email_in,
                            )

        return HttpResponse("success", content_type="application/json")

    else:
        return HttpResponse(error_message(code=100), status=500)
    
def create_jwt_token(user_id):
    # 현재 시간과 유효 기간 설정
    now = datetime.utcnow()
    expire = now + timedelta(days=1)

    # 토큰 페이로드 생성
    payload = {
        'user_id': user_id,
        'exp': expire,
        'iat': now
    }

    # JWT 토큰 생성
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return token

@transaction.atomic
@csrf_exempt
def select_user(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        user_id_in = request_body.get('user_id')

        if user_id_in is None or user_id_in == "":
            return HttpResponse(error_message(data="user_id", code="001"), status=500)

        userObj = user.objects.filter(user_id = user_id_in)

        if userObj.count() == 1:
            
            userObj = userObj.first()

            user_data = {"user_id" : userObj.user_id, "user_name" : userObj.user_name, "user_email": userObj.user_email}

            json_data = json.dumps(user_data)

            return HttpResponse(json_data, content_type="application/json")
        else:
            return HttpResponse(error_message(code="200", content="user is not valid"), status=500)
        
    else:
            return HttpResponse(error_message(code=100), status=500)

@transaction.atomic
@csrf_exempt
def check_user(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        user_id_in = request_body.get('user_id')
        refresh_token_in = request_body.get('refresh_token')
        access_token_in = request_body.get('access_token')
        
        if user_id_in is None or user_id_in == "":
            return HttpResponse(error_message(data="user_id", code="001"), status=500)
        if refresh_token_in is None or refresh_token_in == "":
            return HttpResponse(error_message(data="refresh_token", code="001"), status=500)
        if access_token_in is None or access_token_in == "":
            return HttpResponse(error_message(data="access_token", code="001"), status=500)

        token_data = cache.get(refresh_token_in)

        token_data = {"access_token":access_token_in, "refresh_token" : refresh_token_in}

        try:
            decoded_token = jwt.decode(access_token_in, settings.SECRET_KEY, algorithms='HS256')
            # JWT 유효성 검사 성공 시 처리할 로직
            
        except jwt.ExpiredSignatureError:
            # 만료된 JWT 처리

            if token_data.user_id == user_id_in:
                access_token_new = create_jwt_token(user_id_in)
                
                token_data.access_token = access_token_new

                redis_data = {
                'access_token': access_token_new,
                'user_id': user_id_in,
                }
                
                cache.set(refresh_token_in, access_token_new)

            else:
                return HttpResponse(error_message(code=202, content="user_id is not correct"), status="500")

        except jwt.InvalidTokenError:
            # 유효하지 않은 JWT 처리
            
            return HttpResponse(error_message(code=203, content="token is not valid"), status="500")
        
        json_data = json.dumps(token_data)

        return HttpResponse(json_data, content_type="application/json")

    else:
        return HttpResponse(error_message(code=100), status=500)

def error_message(code,data=None, content=None):
    
    if code == "001":
        error_obj = {"message": data + " is null", "code":code}
    elif code == "100":
        error_obj = {"message": "잘못된 API 요청입니다.", "code":code}
    else:
        error_obj = {"message":content, "code": code}
    
    json_error_obj = json.dumps(error_obj)

    return json_error_obj


        # try:
        #     decoded_token = jwt.decode(access_token, settings.SECRET_KEY, algorithms='HS256')
        #     # JWT 유효성 검사 성공 시 처리할 로직
            
        #     return True
        # except jwt.ExpiredSignatureError:
        #     # 만료된 JWT 처리
            
        #     return False
        # except jwt.InvalidTokenError:
        #     # 유효하지 않은 JWT 처리
            
        #     return False
        
        # userObj = user.objects.filter(user_id = user_id_in)

        # if userObj.count() == 1:
            
        #     userObj = userObj.first()

        #     user_data = {"user_id" : userObj.user_id, "user_name" : userObj.user_name, "user_email": userObj.user_email}

        #     json_data = json.dumps(user_data)

    #         return HttpResponse(json_data, content_type="application/json")
    #     else:
    #         return HttpResponse("없는 아이디")
        
    # else:
    #         return HttpResponse("잘못된 요청입니다.")
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