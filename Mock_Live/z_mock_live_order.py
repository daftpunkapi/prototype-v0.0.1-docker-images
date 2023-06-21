import json
import random
import time
import pandas as pd
from kafka import KafkaProducer

data = pd.read_csv('Rest_Info.csv')

# Define Kafka producer
producer = KafkaProducer(bootstrap_servers=['broker:29092'])

# Making first 5 orders as NEW for each restuarant
for row in data['rest_id']:
    rest_live = {'rest_id': row, 'status': 'NEW'}
    rest_live_str = json.dumps(rest_live)
    print(rest_live_str)
    producer.send('live_order_status', rest_live_str.encode('utf-8'))
    producer.send('live_order_status', rest_live_str.encode('utf-8'))
    producer.send('live_order_status', rest_live_str.encode('utf-8'))
    producer.send('live_order_status', rest_live_str.encode('utf-8'))
    producer.send('live_order_status', rest_live_str.encode('utf-8'))
    
#  Generate and send random restuarant status
while True:
    # Generate random rest_id and rest_status
    random_rest_id = data['rest_id'].sample(n=1).iloc[0]
    random_status = random.choice(["NEW", "PROCESSED"])
    # Create JSON object with ID and status
    rest_live = {'rest_id': random_rest_id, 'status': random_status}
    
    # Serialize JSON object to string
    rest_live_str = json.dumps(rest_live)

    print(rest_live_str)
    
    # Send JSON object to Kafka
    producer.send('live_order_status', rest_live_str.encode('utf-8'))
    
    # Wait for 2 seconds
    time.sleep(random.uniform(1,5))