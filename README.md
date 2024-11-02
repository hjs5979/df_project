# DIFI

분산투자 관리 웹 서비스  
https://

# 사용 기술

## 1. Back-end

> java  
> Django  
> Postgresql
> Redis

## 2. Front-end

> React.js

<br />

## ERD

<div markdown="1" style="padding-left: 15px;">
  <img src="https://github.com/user-attachments/assets/4a6e2dfa-6250-4e27-b7ad-25e7fb5b2c25" />

</div>


## Structure

<div markdown="1" style="padding-left: 15px;">
<img src="https://github.com/user-attachments/assets/73ee2d94-6fc6-4672-add8-7dcc3884cb31" />
</div>

## 서비스 설명

### 1. 구매한 주식 내역 기록
> 1. 파이썬 라이브러리를 통해 해당일의 주식 데이터 가져옴.
> 2. 구매가격, 수량, 비중을 입력 및 저장

### 2. 주식 관련 통계값 제공
> 입력한 주식 데이터에 대한 통계값 제공

### 3. 투자 비중 추천
> 1. 파이썬 라이브러리를 통해 각 주식의 비중 추천.
> 2. 샤프비율을 통해 최적 비중 계산

### 3. 로그인 / 로그아웃 기능
> Redis를 통해 토큰 기반 인증 구현. Access Token과 Refresh Token을 통해 로그인/로그아웃 구현.

<br />

