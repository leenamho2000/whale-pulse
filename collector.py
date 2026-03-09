import asyncio
import websockets
import json
from kafka import KafkaProducer

# Kafka 설정
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

async def binance_producer():
    uri = "wss://stream.binance.com:9443/ws/btcusdt@aggTrade"
    async with websockets.connect(uri) as websocket:
        print("✅ Kafka Producer 연결 성공! 데이터를 쏘아 올립니다...")
        while True:
            try:
                data = await websocket.recv()
                msg = json.loads(data)
                
                price = float(msg['p'])
                quantity = float(msg['q'])
                amount_usd = price * quantity
                
                # 고래 데이터만 Kafka의 'whale_topic'으로 전송
                if amount_usd >= 100000:
                    payload = {
                        'symbol': 'BTCUSDT',
                        'price': price,
                        'quantity': quantity,
                        'amount_usd': amount_usd,
                        'side': 'BUY' if msg['m'] == False else 'SELL' # m이 False면 매수
                    }
                    producer.send('whale_topic', payload)
                    print(f"🚀 Kafka 전송 완료: {amount_usd:,.0f} USD")
                    
            except Exception as e:
                print(f"❌ 에러: {e}")
                break

if __name__ == "__main__":
    asyncio.run(binance_producer())