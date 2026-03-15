"""
回测引擎
"""

import time
import json
import logging
from typing import List, Dict
from pathlib import Path


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, wq_client, config: Dict = None):
        """
        初始化回测引擎
        
        Args:
            wq_client: WorldQuant客户端
            config: 配置字典
        """
        self.client = wq_client
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 默认设置
        self.default_settings = {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": 20,
            "neutralization": "SECTOR",
            "truncation": 0.08,
            "pasteurization": "ON",
            "unitHandling": "VERIFY",
            "nanHandling": "OFF",
            "language": "FASTEXPR",
            "visualization": False
        }
    
    def run_backtest(self, formula: str, settings: Dict = None) -> Dict:
        """
        执行单次回测
        
        Args:
            formula: 因子公式
            settings: 回测设置
        
        Returns:
            回测结果
        """
        settings = settings or self.default_settings
        
        self.logger.info(f"提交回测: {formula}")
        
        # 提交回测
        task_url = self.client.simulate_alpha(formula, settings)
        
        if not task_url:
            return {"success": False, "error": "提交失败"}
        
        # 等待结果
        while True:
            result = self.client.get_simulation_result(task_url)
            
            if "is" in result and result["is"] == "SIMULATING":
                self.logger.info("回测进行中...")
                time.sleep(5)
            else:
                break
        
        # 解析结果
        return self._parse_result(formula, result)
    
    def batch_backtest(self, formulas: List[str], settings: Dict = None,
                      max_concurrent: int = 3, save_progress: bool = True) -> List[Dict]:
        """
        批量回测
        
        Args:
            formulas: 公式列表
            settings: 回测设置
            max_concurrent: 最大并发数
            save_progress: 是否保存进度
        
        Returns:
            回测结果列表
        """
        settings = settings or self.default_settings
        results = []
        
        self.logger.info(f"开始批量回测，共 {len(formulas)} 个因子")
        
        for i, formula in enumerate(formulas):
            self.logger.info(f"进度: {i+1}/{len(formulas)}")
            
            result = self.run_backtest(formula, settings)
            results.append(result)
            
            # 保存进度
            if save_progress:
                self._save_progress(results, "backtest_progress.json")
            
            # 避免请求过快
            time.sleep(2)
        
        self.logger.info(f"批量回测完成，成功 {sum(1 for r in results if r.get('success'))} 个")
        
        return results
    
    def _parse_result(self, formula: str, result: Dict) -> Dict:
        """解析回测结果"""
        try:
            # 提取关键指标
            is_data = result.get("is", {})
            
            parsed = {
                "success": True,
                "formula": formula,
                "sharpe_ratio": is_data.get("sharpe", 0),
                "fitness": is_data.get("fitness", 0),
                "turnover": is_data.get("turnover", 0),
                "returns": is_data.get("returns", 0),
                "drawdown": is_data.get("drawdown", 0),
                "margin": is_data.get("margin", 0),
                "full_result": result
            }
            
            # 判断是否满足提交标准
            parsed["meets_criteria"] = self._check_criteria(parsed)
            
            return parsed
            
        except Exception as e:
            self.logger.error(f"解析结果失败: {e}")
            return {"success": False, "formula": formula, "error": str(e)}
    
    def _check_criteria(self, result: Dict) -> bool:
        """检查是否满足提交标准"""
        criteria = self.config.get("submission_criteria", {})
        
        fitness = result.get("fitness", 0)
        sharpe = result.get("sharpe_ratio", 0)
        turnover = result.get("turnover", 0)
        
        # 检查各项指标
        if fitness < criteria.get("fitness", 1.0):
            return False
        if sharpe < criteria.get("sharpe_ratio", 1.25):
            return False
        if turnover < criteria.get("turnover_min", 0.01):
            return False
        if turnover > criteria.get("turnover_max", 0.70):
            return False
        
        return True
    
    def _save_progress(self, results: List[Dict], filepath: str):
        """保存进度"""
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
