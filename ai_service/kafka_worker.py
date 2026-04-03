# ai_service/kafka_worker.py
from kafka import KafkaConsumer
import json
import redis
import os


# 导入你现有的 AI 处理逻辑，假设在 api.py 或 matcher.py 里有一个处理文件的函数
# from matcher import process_resume_and_match_jobs

def run_worker():
    # 1. 连接 Redis 和 Kafka
    r = redis.Redis(host='localhost', port=6379, db=0)
    consumer = KafkaConsumer(
        'resume-tasks',
        bootstrap_servers=['localhost:9092'],
        group_id='ai-recommendation-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print("Kafka Worker is listening for tasks...")

    for message in consumer:
        task_data = message.value
        task_id = task_data['taskId']
        file_path = task_data['filePath']

        print(f"Received Task: {task_id}, processing file: {file_path}")

        try:
            # 2. 调用你现有的深度学习模型逻辑
            # 由于你原本是接收 HTTP UploadFile，现在改成了读取本地 file_path
            # recommendations = process_resume_and_match_jobs(file_path)

            # 这里我 mock 一个结果，实际中替换成你上面调用的返回结果
            recommendations = [
                {"job_id": 1, "title": "Software Engineer", "score": 0.95},
                {"job_id": 2, "title": "Backend Developer", "score": 0.88}
            ]

            # 3. 将计算结果序列化为 JSON，存入 Redis，并设置过期时间（比如1小时）
            redis_key = f"recommend_result:{task_id}"
            r.setex(redis_key, 3600, json.dumps(recommendations))

            print(f"Task {task_id} completed and saved to Redis.")

            # (可选) 删掉暂存的文件释放磁盘空间
            if os.path.exists(file_path):
                os.remove(file_path)

        except Exception as e:
            print(f"Error processing task {task_id}: {e}")
            r.setex(f"recommend_result:{task_id}", 3600, json.dumps({"error": str(e)}))


if __name__ == "__main__":
    run_worker()