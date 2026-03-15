"""
数据字段管理
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path


class DataFieldsManager:
    """数据字段管理"""
    
    def __init__(self, fields_file: str = None):
        """
        初始化数据字段管理器
        
        Args:
            fields_file: 字段JSON文件路径
        """
        self.fields = {}  # id -> field_info
        self.fields_by_category = {}  # category -> [field_ids]
        self.logger = logging.getLogger(__name__)
        
        if fields_file:
            self.load_from_file(fields_file)
    
    def load_from_file(self, filepath: str):
        """从文件加载字段"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                fields_list = data
            elif isinstance(data, dict) and 'fields' in data:
                fields_list = data['fields']
            else:
                fields_list = []
            
            for field in fields_list:
                if isinstance(field, dict) and 'id' in field:
                    field_id = field['id']
                    self.fields[field_id] = field
                    
                    # 按类别分组
                    category = field.get('category', 'Unknown')
                    if category not in self.fields_by_category:
                        self.fields_by_category[category] = []
                    self.fields_by_category[category].append(field_id)
            
            self.logger.info(f"加载了 {len(self.fields)} 个数据字段")
            
        except Exception as e:
            self.logger.error(f"加载字段文件失败: {e}")
    
    def load_from_wq_client(self, wq_client, region: str = "USA", 
                           universe: str = "TOP3000"):
        """从WorldQuant客户端加载字段"""
        try:
            fields_list = wq_client.get_data_fields(
                region=region,
                universe=universe
            )
            
            for field in fields_list:
                field_id = field.get('id')
                if field_id:
                    self.fields[field_id] = field
                    
                    category = field.get('category', 'Unknown')
                    if category not in self.fields_by_category:
                        self.fields_by_category[category] = []
                    self.fields_by_category[category].append(field_id)
            
            self.logger.info(f"从WorldQuant加载了 {len(self.fields)} 个数据字段")
            
        except Exception as e:
            self.logger.error(f"从WorldQuant加载字段失败: {e}")
    
    def get_field(self, field_id: str) -> Optional[Dict]:
        """获取字段信息"""
        return self.fields.get(field_id)
    
    def get_fields_by_category(self, category: str) -> List[str]:
        """获取某类别的所有字段"""
        return self.fields_by_category.get(category, [])
    
    def list_all_fields(self) -> List[str]:
        """列出所有字段"""
        return list(self.fields.keys())
    
    def validate_field(self, field_id: str) -> bool:
        """验证字段是否存在"""
        return field_id in self.fields
    
    def search_fields(self, keyword: str) -> List[str]:
        """搜索字段"""
        keyword = keyword.lower()
        results = []
        
        for field_id, field_info in self.fields.items():
            if keyword in field_id.lower():
                results.append(field_id)
            elif keyword in field_info.get('name', '').lower():
                results.append(field_id)
            elif keyword in field_info.get('description', '').lower():
                results.append(field_id)
        
        return results
    
    def get_field_type(self, field_id: str) -> Optional[str]:
        """获取字段类型"""
        field = self.fields.get(field_id)
        return field.get('type') if field else None
    
    def get_field_description(self, field_id: str) -> Optional[str]:
        """获取字段描述"""
        field = self.fields.get(field_id)
        return field.get('description') if field else None
    
    def filter_fields_by_type(self, field_type: str) -> List[str]:
        """按类型过滤字段"""
        results = []
        for field_id, field_info in self.fields.items():
            if field_info.get('type') == field_type:
                results.append(field_id)
        return results
    
    def get_common_fields(self) -> List[str]:
        """获取常用字段"""
        common_fields = [
            # 价格相关
            'open', 'high', 'low', 'close', 'volume', 'vwap',
            # 收益相关
            'returns', 'cap', 'sharesout',
            # 基本面
            'earnings', 'book_value', 'sales', 'ebitda',
            'enterprise_value', 'operating_cash_flow',
            # 估值指标
            'pe_ratio', 'pb_ratio', 'ps_ratio',
            # 其他
            'dividend_yield', 'beta', 'momentum'
        ]
        
        # 只返回存在的字段
        return [f for f in common_fields if f in self.fields]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "fields": list(self.fields.values()),
            "categories": self.fields_by_category,
            "total_count": len(self.fields)
        }
    
    def save_to_file(self, filepath: str):
        """保存到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


# 预定义的常用字段
COMMON_FIELDS = {
    "price": {
        "open": "开盘价",
        "high": "最高价",
        "low": "最低价",
        "close": "收盘价",
        "volume": "成交量",
        "vwap": "成交量加权均价",
    },
    "fundamental": {
        "cap": "市值",
        "earnings": "净利润",
        "book_value": "账面价值",
        "sales": "销售收入",
        "ebitda": "息税折旧摊销前利润",
        "enterprise_value": "企业价值",
        "operating_cash_flow": "经营现金流",
    },
    "returns": {
        "returns": "收益率",
        "sharesout": "流通股本",
    },
    "valuation": {
        "pe_ratio": "市盈率",
        "pb_ratio": "市净率",
        "ps_ratio": "市销率",
        "dividend_yield": "股息率",
    }
}
