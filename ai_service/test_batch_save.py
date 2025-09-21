#!/usr/bin/env python3
"""
测试批量保存职位功能的脚本
"""

import requests
import json

# 配置
BACKEND_INTAKE_URL = "http://localhost:8080/api/internal/jobs/batch-intake"
INTERNAL_API_KEY = "thisisaramdomandVeryLongStringtoMakeItASecretKey155423asc5assajci,w,YAJCB"

def test_batch_save():
    """测试批量保存功能"""
    
    # 准备测试数据
    test_jobs = [
        {
            "title": "测试职位1 - 前端开发工程师",
            "company": "测试公司A",
            "location": "北京",
            "description": "这是一个测试职位描述，用于验证批量保存功能。",
            "url": "https://example.com/test-job-1",
            "source": "测试来源"
        },
        {
            "title": "测试职位2 - 后端开发工程师", 
            "company": "测试公司B",
            "location": "上海",
            "description": "这是另一个测试职位描述，用于验证批量保存功能。",
            "url": "https://example.com/test-job-2",
            "source": "测试来源"
        },
        {
            "title": "测试职位3 - 全栈开发工程师",
            "company": "测试公司C", 
            "location": "深圳",
            "description": "这是第三个测试职位描述，用于验证批量保存功能。",
            "url": "https://example.com/test-job-2",
            "source": "测试来源"
        }
    ]
    
    print(f"准备测试批量保存 {len(test_jobs)} 个职位...")
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-Internal-API-Key': INTERNAL_API_KEY
        }
        
        response = requests.post(BACKEND_INTAKE_URL, json=test_jobs, headers=headers)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 批量保存完成！")
            print(f"   总职位数量: {result.get('total', '未知')}")
            print(f"   成功保存: {result.get('saved', '未知')}")
            print(f"   跳过重复: {result.get('skipped', '未知')}")
            print(f"   消息: {result.get('message', '无消息')}")
        else:
            print(f"❌ 批量保存失败！")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    test_batch_save()
