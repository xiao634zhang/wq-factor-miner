"""
WorldQuant Brain API客户端
"""

import requests
import time
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path


class WQClient:
    """WorldQuant Brain API客户端"""
    
    def __init__(self, username: str, password: str, 
                 api_base: str = "https://api.worldquantbrain.com"):
        """
        初始化客户端
        
        Args:
            username: WorldQuant Brain用户名
            password: WorldQuant Brain密码
            api_base: API基础URL
        """
        self.username = username
        self.password = password
        self.api_base = api_base
        self.session = None
        self.logger = logging.getLogger(__name__)
        
        # 登录
        self._login()
    
    @classmethod
    def from_config(cls, config_path: str = "config.yaml"):
        """从配置文件创建客户端"""
        import yaml
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return cls(
            username=config['worldquant']['username'],
            password=config['worldquant']['password'],
            api_base=config['worldquant'].get('api_base', 'https://api.worldquantbrain.com')
        )
    
    def _login(self):
        """登录WorldQuant Brain"""
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = self.session.post(f"{self.api_base}/authentication")
                response.raise_for_status()
                self.logger.info("登录WorldQuant Brain成功")
                return
            except Exception as e:
                self.logger.warning(f"登录失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(15)
                else:
                    raise Exception("登录失败，请检查用户名和密码")
    
    def _reconnect(self):
        """重新连接"""
        self.logger.info("重新连接...")
        self._login()
    
    def get_data_fields(self, region: str = "USA", universe: str = "TOP3000",
                       instrument_type: str = "EQUITY", delay: int = 1) -> List[Dict]:
        """
        获取数据字段列表
        
        Args:
            region: 区域 (USA, CHN, etc.)
            universe: 股票池 (TOP3000, TOP1000, etc.)
            instrument_type: 证券类型 (EQUITY)
            delay: 延迟 (0 or 1)
        
        Returns:
            数据字段列表
        """
        url = f"{self.api_base}/data-fields"
        params = {
            "instrumentType": instrument_type,
            "region": region,
            "universe": universe,
            "delay": delay,
            "limit": 50
        }
        
        all_fields = []
        offset = 0
        
        while True:
            params["offset"] = offset
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            all_fields.extend(results)
            
            # 检查是否还有更多
            if len(results) < 50:
                break
            
            offset += 50
        
        self.logger.info(f"获取到 {len(all_fields)} 个数据字段")
        return all_fields
    
    def simulate_alpha(self, formula: str, settings: Dict) -> str:
        """
        提交因子回测
        
        Args:
            formula: Alpha因子公式
            settings: 回测设置
        
        Returns:
            任务URL
        """
        data = {
            "type": "REGULAR",
            "settings": settings,
            "regular": formula
        }
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    f"{self.api_base}/simulations",
                    json=data
                )
                response.raise_for_status()
                
                location = response.headers.get("Location")
                if location:
                    self.logger.info(f"提交成功: {formula[:50]}...")
                    return location
                
            except Exception as e:
                self.logger.warning(f"提交失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(30)  # 增加延迟到30秒
                    self._reconnect()
                else:
                    raise
        
        return None
    
    def get_simulation_result(self, task_url: str) -> Dict:
        """
        获取回测结果
        
        Args:
            task_url: 任务URL
        
        Returns:
            回测结果
        """
        response = self.session.get(task_url)
        response.raise_for_status()
        
        result = response.json()
        
        # 检查是否完成
        if "alpha" in result:
            # 获取详细结果
            alpha_id = result["alpha"]
            alpha_response = self.session.get(f"{self.api_base}/alphas/{alpha_id}")
            alpha_response.raise_for_status()
            return alpha_response.json()
        
        return result
    
    def batch_simulate(self, formulas: List[str], settings: Dict,
                      max_concurrent: int = 3, callback=None) -> List[Dict]:
        """
        批量回测
        
        Args:
            formulas: 公式列表
            settings: 回测设置
            max_concurrent: 最大并发数
            callback: 回调函数
        
        Returns:
            回测结果列表
        """
        results = []
        active_tasks = {}  # task_url -> formula
        
        for i, formula in enumerate(formulas):
            # 检查并发数
            while len(active_tasks) >= max_concurrent:
                # 检查已完成的任务
                completed = []
                for task_url in active_tasks:
                    result = self.get_simulation_result(task_url)
                    if "is" not in result or result.get("is") != "SIMULATING":
                        completed.append(task_url)
                        results.append({
                            "formula": active_tasks[task_url],
                            "result": result
                        })
                        if callback:
                            callback(result)
                
                # 移除已完成的任务
                for task_url in completed:
                    del active_tasks[task_url]
                
                time.sleep(5)
            
            # 提交新任务
            task_url = self.simulate_alpha(formula, settings)
            if task_url:
                active_tasks[task_url] = formula
            
            # 避免请求过快
            time.sleep(2)
        
        # 等待所有任务完成
        while active_tasks:
            completed = []
            for task_url in active_tasks:
                result = self.get_simulation_result(task_url)
                if "is" not in result or result.get("is") != "SIMULATING":
                    completed.append(task_url)
                    results.append({
                        "formula": active_tasks[task_url],
                        "result": result
                    })
                    if callback:
                        callback(result)
            
            for task_url in completed:
                del active_tasks[task_url]
            
            if active_tasks:
                time.sleep(5)
        
        return results
