# 🐳 WhalePulse: 초저지연 실시간 고래 체결 및 시장 심리 분석 시스템
> **Real-time Data Engineering Pipeline + Market Surveillance Analytics**

---

## 1. 프로젝트 동기 (Motivation)
암호화폐 시장의 유동성은 소수의 '고래(Whale)'들에 의해 주도됩니다. 하지만 초당 수만 건씩 쏟아지는 체결 데이터 속에서 유의미한 거대 자본의 흐름을 파악하는 것은 불가능에 가깝습니다. 본 프로젝트는 **Apache Kafka를 활용한 데이터 버퍼링**과 **ClickHouse의 고성능 시계열 처리**를 결합하여, 거대 자본의 움직임을 실시간으로 감시하고 이를 투자 지표로 변환하는 엔드 투 엔드 파이프라인을 구축했습니다.

---

## 2. 시스템 아키텍처 (Architecture)

![Architecture](./images/architecture.png)


### 실시간 데이터 처리 전략
1. **Ingestion Layer:** Python Asyncio 기반 비동기 수집기를 통해 바이낸스(Binance)의 실시간 체결 데이터를 수집합니다.
2. **Messaging Layer:** 트래픽 폭주 시 데이터 유실을 방지하고 시스템 결합도를 낮추기 위해 **Kafka**를 완충 지대로 활용합니다.
3. **Storage Layer:** 초당 수만 건의 쓰기 성능과 복잡한 분석 쿼리에 최적화된 **ClickHouse**를 채택했습니다.
4. **Presentation Layer:** **Streamlit**을 통해 시장 심리 지수(WSI) 및 누적 거래 흐름(CVD)을 시각화합니다.

---

## 3. 단계별 구현 및 기술적 가치 (Implementation)

### ① 분산 메시징 시스템을 통한 데이터 안정성 확보
갑작스러운 변동성 확대로 거래량이 폭증할 때 DB 부하를 관리하기 위해 Kafka를 도입했습니다.
* **Action:** Docker 기반의 Kafka 및 Zookeeper 클러스터를 구축하여 메시지 큐 시스템 완성.
* **Result:** 수집기와 처리기의 속도 차이를 조절(Backpressure Control)하여 무중단 파이프라인을 구축했습니다.

### ② 고성능 시계열 데이터베이스 구축 (OLAP)
데이터 분석가(DA)로서 대규모 데이터 조회 속도를 확보하기 위해 Columnar DB인 ClickHouse를 설계했습니다.
* **Action:** DBeaver를 연동하여 실시간으로 유입되는 고래 데이터를 SQL 기반으로 검증하고 스키마를 최적화했습니다.

### ③ 도메인 중심의 시장 진단 지표 산출
단순 거래 내역 나열을 넘어, 투자 의사결정을 돕는 분석 로직을 직접 설계했습니다.
* **Whale Sentiment Index (WSI):** 매수/매도 고래 거래량 비중을 통해 시장 심리를 실시간으로 수치화합니다.
* **Market Status Diagnosis:** 고래의 활동 강도에 따라 '강력 매수', '강력 매도', '관망' 등의 AI 진단 메시지를 제공합니다.

---

## 4. 엔지니어링 트러블슈팅 (Troubleshooting)
구축 과정에서 발생한 실제 에러들을 해결하며 실시간 데이터 파이프라인의 핵심 원리를 깊이 이해했습니다.

#### ① Python 3.13 호환성 및 라이브러리 충돌
* **Issue:** `kafka-python` 라이브러리가 최신 파이썬 버전에서 `NoBrokersAvailable` 에러를 발생시켰습니다.
* **Solution:** 커뮤니티에서 최신 파이썬 환경을 지원하는 `kafka-python-ng` 라이브러리로 교체하여 클러스터 연결 안정성을 확보했습니다.

#### ② 인프라 리소스 충돌 및 컨테이너 관리
* **Issue:** 이미 생성된 컨테이너 이름(Conflict)으로 인해 ClickHouse 서버 실행이 실패했습니다.
* **Solution:** `docker rm -f`를 통한 리소스 초기화 및 `docker-compose`를 이용한 환경 변수 통합 관리 체계를 구축하여 문제를 해결했습니다.

#### ③ Streamlit UI 렌더링 및 ID 충돌 (DuplicateElementId)
* **Issue:** 실시간 갱신 루프 내에서 동일한 `key`를 가진 차트 엘리먼트가 중복 생성되어 대시보드가 중단되었습니다.
* **Solution:** `while True` 방식 대신 Streamlit의 표준 실행 모델인 `st.rerun()` 시스템을 도입하여 UI 업데이트 안정성을 확보했습니다.

---

## 5. 프로젝트 성과 및 회고
* **실시간성 확보:** 바이낸스 체결 발생 시점부터 대시보드 표출까지의 지연 시간을 0.5초 미만으로 유지하는 성과를 거두었습니다.
* **통합 인프라 구축:** Docker 기반의 컨테이너화를 통해 Kafka, ClickHouse, Streamlit이 유기적으로 작동하는 독립된 분석 환경을 완성했습니다.
* **분석가적 역량 입증:** 가공되지 않은 텍스트 데이터를 시장의 '심리 지표'로 정제함으로써 데이터의 비즈니스 가치를 극대화했습니다.