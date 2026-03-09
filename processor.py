from kafka import KafkaConsumer
from clickhouse_driver import Client
import json
from datetime import datetime

# ClickHouse 및 Kafka 설정 (비밀번호 1234 확인)
client = Client(host='localhost', port=9000, password='1234')
consumer = KafkaConsumer(
    'whale_topic',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

print("📥 Consumer 대기 중... Kafka에서 데이터를 가져와 DB로 저장합니다.")

try:
    for message in consumer:
        data = message.value
        
        # ClickHouse에 데이터 삽입
        client.execute(
            'INSERT INTO whale_trades (event_time, symbol, price, quantity, amount_usd, side) VALUES',
            [(datetime.now(), data['symbol'], data['price'], data['quantity'], data['amount_usd'], data['side'])]
        )
        print(f"💾 [DB 저장 성공] {data['amount_usd']:,.0f} USD ({data['symbol']})")
except Exception as e:
    print(f"❌ DB 저장 중 에러 발생: {e}")