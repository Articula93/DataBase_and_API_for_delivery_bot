import schedule
import time

def hello_world():
    print("Hello, World!")
 
schedule.every(10).seconds.do(hello_world)
 
while True:
    schedule.run_pending()
    time.sleep(1)