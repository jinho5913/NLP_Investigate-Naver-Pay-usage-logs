# NLP_Investigate-Naver-Pay-usage-logs

### < 네이버페이 사용 로그 분석 >  
네이버페이에서 결제 한 사람(`orderDone`)/결제 전 단계(`orderSheet`) 까지만 간 사람의 행동 분석


### 진행사항
#### 0423
* Naver Pay '구매 결정' or '장바구니' 까지 도달한 sequence 구분
```
# split sequence (4가지 샘플 중 하나)
python n_orderDone0.py
```
