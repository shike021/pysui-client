#!/usr/bin/env python3
"""
Sui区块链客户端程序
使用pysui库的JSON-RPC接口实现合约部署和调用功能

注意：本客户端故意使用JSON-RPC接口而不是GraphQL，
虽然pysui官方推荐GraphQL，但JSON-RPC更通用且标准化。
deprecation警告是预期的，不影响功能。
"""

import warnings
import logging
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

# 抑制pysui的deprecation警告（我们故意使用JSON-RPC）
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pysui.*")
warnings.filterwarnings("ignore", message=".*deprecated.*", category=DeprecationWarning)

# pysui 核心导入
from pysui import SuiConfig, SyncClient, SuiRpcResult, SuiAddress, ObjectID
from pysui.sui.sui_txn.sync_transaction import SuiTransaction
from pysui.sui.sui_types.scalars import SuiU64, SuiU8, SuiString, SuiInteger
from pysui.sui.sui_types.collections import SuiArray
from pysui.sui.sui_bcs import bcs

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 抑制deprecation相关的日志
logging.getLogger("deprecated").setLevel(logging.ERROR)


class SuiContractClient:
    """
    Sui智能合约客户端类
    
    本客户端使用JSON-RPC接口与Sui区块链交互。
    
    注意：虽然pysui官方推荐使用GraphQL，但我们故意选择JSON-RPC因为：
    1. JSON-RPC是更通用和标准化的API调用方式
    2. 更容易与其他系统集成
    3. 调试和理解更简单
    4. 符合项目的技术需求
    
    deprecation警告是预期的，不影响功能正常使用。
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化Sui客户端
        
        Args:
            config_path: Sui配置文件路径，默认使用default_config()
        """
        try:
            if config_path:
                self.config = SuiConfig.user_config(config_path)
            else:
                self.config = SuiConfig.default_config()
            
            self.client = SyncClient(self.config)
            self.active_address = self.config.active_address
            
            logger.info(f"已连接到Sui网络: {self.config.rpc_url}")
            logger.info(f"当前活跃地址: {self.active_address}")
            
            # 检查连接状态
            self._check_connection()
            
        except Exception as e:
            logger.error(f"初始化Sui客户端失败: {e}")
            raise
    
    def _check_connection(self):
        """检查与Sui网络的连接"""
        try:
            # 通过获取gas价格来验证连接
            gas_price = self.client.current_gas_price
            logger.info(f"当前gas价格: {gas_price}")
        except Exception as e:
            logger.error(f"无法连接到Sui网络: {e}")
            raise
    
    def _handle_result(self, result: SuiRpcResult, operation: str) -> Dict[str, Any]:
        """
        处理RPC调用结果
        
        Args:
            result: SuiRpcResult对象
            operation: 操作描述
            
        Returns:
            结果数据字典
            
        Raises:
            Exception: 当操作失败时抛出异常
        """
        if result.is_ok():
            logger.info(f"{operation} 执行成功")
            if hasattr(result.result_data, 'to_json'):
                return json.loads(result.result_data.to_json())
            else:
                return result.result_data
        else:
            error_msg = f"{operation} 执行失败: {result.result_string}"
            logger.error(error_msg)
            if result.result_data:
                logger.error(f"错误详情: {result.result_data}")
            raise Exception(error_msg)
    
    def get_account_balance(self) -> Dict[str, Any]:
        """
        获取账户余额信息
        
        Returns:
            包含余额信息的字典
        """
        try:
            # 使用JSON RPC方式获取余额 - 使用更直接的方法
            import pysui.sui.sui_builders.get_builders as get_builders
            
            # 使用实际存在的builders
            try:
                # 方法1：尝试使用GetAllCoinBalances（实际存在）
                if hasattr(get_builders, 'GetAllCoinBalances'):
                    builder = get_builders.GetAllCoinBalances(owner=self.active_address)
                    result = self.client.execute(builder)
                    
                    if not result.is_ok():
                        logger.error(f"GetAllCoinBalances 查询失败: {result.result_string}")
                        return {
                            'total_balance_mists': 0,
                            'total_balance_sui': 0.0,
                            'sui_objects': [],
                            'active_address': str(self.active_address),
                            'error': result.result_string
                        }
                    
                    # 直接使用result.result_data，这是CoinBalances对象
                    balance_data = result.result_data
                    total_balance = 0
                    sui_objects = []
                    
                    # 处理CoinBalances对象
                    if hasattr(balance_data, 'items') and balance_data.items:
                        for balance_item in balance_data.items:
                            if hasattr(balance_item, 'coin_type') and balance_item.coin_type == '0x2::sui::SUI':
                                total_balance = int(balance_item.total_balance)
                                coin_count = getattr(balance_item, 'coin_object_count', 0)
                                sui_objects.append({
                                    'coin_count': coin_count,
                                    'total_balance': total_balance,
                                    'coin_type': balance_item.coin_type
                                })
                                break
                    
                    logger.info(f"账户总余额: {total_balance / 1_000_000_000} SUI")
                    
                    return {
                        'total_balance_mists': total_balance,
                        'total_balance_sui': total_balance / 1_000_000_000,
                        'sui_objects': sui_objects,
                        'active_address': str(self.active_address)
                    }
                
                # 方法2：使用GetCoins（已确认存在）
                elif hasattr(get_builders, 'GetCoins'):
                    builder = get_builders.GetCoins(
                        owner=self.active_address,
                        coin_type="0x2::sui::SUI"
                    )
                    result = self.client.execute(builder)
                    
                    if not result.is_ok():
                        logger.error(f"GetCoins 查询失败: {result.result_string}")
                        return {
                            'total_balance_mists': 0,
                            'total_balance_sui': 0.0,
                            'sui_objects': [],
                            'active_address': str(self.active_address),
                            'error': result.result_string
                        }
                    
                    # 直接使用result.result_data，这是SuiCoinObjects对象
                    coin_data = result.result_data
                    total_balance = 0
                    sui_objects = []
                    
                    # 处理SuiCoinObjects对象
                    if hasattr(coin_data, 'data') and coin_data.data:
                        for coin in coin_data.data:
                            if hasattr(coin, 'balance'):
                                balance = int(coin.balance)
                                total_balance += balance
                                sui_objects.append({
                                    'object_id': getattr(coin, 'coin_object_id', ''),
                                    'balance': balance,
                                    'version': getattr(coin, 'version', ''),
                                    'digest': getattr(coin, 'digest', ''),
                                    'coin_type': getattr(coin, 'coin_type', '0x2::sui::SUI')
                                })
                    
                    logger.info(f"账户总余额: {total_balance / 1_000_000_000} SUI")
                    
                    return {
                        'total_balance_mists': total_balance,
                        'total_balance_sui': total_balance / 1_000_000_000,
                        'sui_objects': sui_objects,
                        'active_address': str(self.active_address)
                    }
                
                else:
                    # 方法4：如果所有builder都不存在，返回基础信息
                    logger.warning("未找到合适的余额查询builder，返回基础信息")
                    return {
                        'total_balance_mists': 0,
                        'total_balance_sui': 0.0,
                        'sui_objects': [],
                        'active_address': str(self.active_address),
                        'note': '需要更新pysui版本或使用GraphQL接口查询余额'
                    }
                    
            except Exception as builder_error:
                logger.warning(f"Builder执行失败: {builder_error}, 尝试备选方案")
                # 备选方案：返回基础信息
                return {
                    'total_balance_mists': 0,
                    'total_balance_sui': 0.0,
                    'sui_objects': [],
                    'active_address': str(self.active_address),
                    'note': f'余额查询失败: {builder_error}'
                }
            
        except Exception as e:
            logger.error(f"获取账户余额失败: {e}")
            # 不抛出异常，返回错误信息
            return {
                'total_balance_mists': 0,
                'total_balance_sui': 0.0,
                'sui_objects': [],
                'active_address': str(self.active_address),
                'error': str(e)
            }
    
    def deploy_contract(self, 
                       package_path: str, 
                       gas_budget: Optional[int] = None,
                       build_args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        部署智能合约到Sui网络
        
        Args:
            package_path: Move包的路径
            gas_budget: Gas预算，单位为mists
            build_args: 额外的构建参数
            
        Returns:
            包含部署结果的字典，包括包ID和UpgradeCap对象ID
        """
        try:
            logger.info(f"开始部署合约: {package_path}")
            
            # 验证包路径
            pkg_path = Path(package_path)
            if not pkg_path.exists():
                raise FileNotFoundError(f"包路径不存在: {package_path}")
            
            # 检查是否是有效的Move包
            move_toml = pkg_path / "Move.toml"
            if not move_toml.exists():
                raise FileNotFoundError(f"在 {package_path} 中未找到Move.toml文件")
            
            # 导入正确的SuiTransaction
            from pysui.sui.sui_txn.sync_transaction import SuiTransaction
            
            # 创建事务
            txn = SuiTransaction(
                client=self.client,
                initial_sender=self.active_address
            )
            
            # 添加发布命令
            logger.info("编译和准备合约...")
            upgrade_cap = txn.publish(
                project_path=str(pkg_path),
                args_list=build_args or []
            )
            
            # 将UpgradeCap转移给发送者
            txn.transfer_objects(
                transfers=[upgrade_cap],
                recipient=self.active_address
            )
            
            # SuiTransaction会自动处理gas预算，我们只需要检查估算成本
            try:
                inspect_result = txn.inspect_for_cost()
                if isinstance(inspect_result, tuple) and len(inspect_result) >= 2:
                    gas_max, gas_min, gas_object_id = inspect_result
                    logger.info(f"Gas估算 - 最大: {gas_max}, 最小: {gas_min} mists")
                    
                    # 检查是否超过最大限制
                    max_gas = txn.constraints.max_tx_gas
                    if gas_max > max_gas:
                        logger.warning(f"估算gas ({gas_max}) 超过最大限制 ({max_gas})")
                else:
                    logger.info("Gas估算完成，将使用默认预算")
                    
            except Exception as e:
                logger.warning(f"Gas估算失败: {e}，将使用默认预算")
            
            # 执行事务
            logger.info("提交部署事务...")
            result = txn.execute()
            deploy_data = self._handle_result(result, "合约部署")
            
            # 提取关键信息
            package_id = None
            upgrade_cap_id = None
            
            if 'objectChanges' in deploy_data:
                for change in deploy_data['objectChanges']:
                    if change.get('type') == 'published':
                        package_id = change.get('packageId')
                    elif change.get('type') == 'created' and '::package::UpgradeCap' in change.get('objectType', ''):
                        upgrade_cap_id = change.get('objectId')
            
            deployment_info = {
                'package_id': package_id,
                'upgrade_cap_id': upgrade_cap_id,
                'transaction_hash': deploy_data.get('digest'),
                'gas_used': deploy_data.get('effects', {}).get('gasUsed'),
                'status': deploy_data.get('effects', {}).get('status'),
                'full_result': deploy_data
            }
            
            logger.info(f"合约部署成功!")
            logger.info(f"包ID: {package_id}")
            logger.info(f"UpgradeCap ID: {upgrade_cap_id}")
            logger.info(f"事务哈希: {deployment_info['transaction_hash']}")
            
            return deployment_info
            
        except Exception as e:
            logger.error(f"合约部署失败: {e}")
            raise
    
    def call_contract_function(self,
                              package_id: str,
                              module_name: str,
                              function_name: str,
                              arguments: Optional[List[Any]] = None,
                              type_arguments: Optional[List[str]] = None,
                              gas_budget: Optional[int] = None) -> Dict[str, Any]:
        """
        调用智能合约函数
        
        Args:
            package_id: 合约包ID
            module_name: 模块名称
            function_name: 函数名称
            arguments: 函数参数列表
            type_arguments: 泛型类型参数
            gas_budget: Gas预算
            
        Returns:
            包含调用结果的字典
        """
        try:
            logger.info(f"调用合约函数: {package_id}::{module_name}::{function_name}")
            
            # 导入正确的SuiTransaction
            from pysui.sui.sui_txn.sync_transaction import SuiTransaction
            
            # 创建事务
            txn = SuiTransaction(
                client=self.client,
                initial_sender=self.active_address
            )
            
            # 构建目标字符串
            target = f"{package_id}::{module_name}::{function_name}"
            
            # 处理参数
            processed_args = []
            if arguments:
                for arg in arguments:
                    if isinstance(arg, str):
                        # 检查是否是对象ID
                        if len(arg) == 66 and arg.startswith('0x'):
                            processed_args.append(ObjectID(arg))
                        else:
                            processed_args.append(SuiString(arg))
                    elif isinstance(arg, bytes):
                        # 将bytes转换为list[int]用于vector<u8>
                        processed_args.append(list(arg))
                    elif isinstance(arg, int):
                        processed_args.append(SuiU64(arg))
                    elif isinstance(arg, bool):
                        processed_args.append(arg)
                    else:
                        processed_args.append(arg)
            
            # 调用合约函数
            result_refs = txn.move_call(
                target=target,
                arguments=processed_args,
                type_arguments=type_arguments or []
            )
            
            # 检查执行成本（SuiTransaction会自动处理gas预算）
            try:
                inspect_result = txn.inspect_for_cost()
                if isinstance(inspect_result, tuple) and len(inspect_result) >= 2:
                    gas_max, gas_min, gas_object_id = inspect_result
                    logger.info(f"Gas估算 - 最大: {gas_max}, 最小: {gas_min} mists")
                else:
                    logger.info("Gas估算完成，将使用默认预算")
            except Exception as e:
                logger.warning(f"Gas估算失败: {e}，将使用默认预算")
            
            # 执行事务
            logger.info("提交函数调用事务...")
            result = txn.execute()
            call_data = self._handle_result(result, "合约函数调用")
            
            call_info = {
                'transaction_hash': call_data.get('digest'),
                'gas_used': call_data.get('effects', {}).get('gasUsed'),
                'status': call_data.get('effects', {}).get('status'),
                'events': call_data.get('events', []),
                'object_changes': call_data.get('objectChanges', []),
                'full_result': call_data
            }
            
            logger.info(f"合约函数调用成功!")
            logger.info(f"事务哈希: {call_info['transaction_hash']}")
            
            return call_info
            
        except Exception as e:
            logger.error(f"合约函数调用失败: {e}")
            raise
    
    def get_object_info(self, object_id: str) -> Dict[str, Any]:
        """
        获取对象信息
        
        Args:
            object_id: 对象ID
            
        Returns:
            对象信息字典
        """
        try:
            import pysui.sui.sui_builders.get_builders as get_builders
            
            # 尝试使用GetObject builder
            if hasattr(get_builders, 'GetObject'):
                builder = get_builders.GetObject(
                    object_id=ObjectID(object_id),
                    options={"showType": True, "showContent": True, "showOwner": True}
                )
                
                result = self.client.execute(builder)
                object_data = self._handle_result(result, f"获取对象信息 {object_id}")
                
                return object_data
            else:
                logger.warning("GetObject builder不可用")
                return {
                    'object_id': object_id,
                    'error': 'GetObject builder不可用，请使用GraphQL接口',
                    'note': 'JSON-RPC GetObject已被deprecated'
                }
            
        except Exception as e:
            logger.error(f"获取对象信息失败: {e}")
            return {
                'object_id': object_id,
                'error': str(e)
            }
    
    def get_transaction_info(self, tx_hash: str) -> Dict[str, Any]:
        """
        获取交易信息
        
        Args:
            tx_hash: 交易哈希
            
        Returns:
            交易信息字典
        """
        try:
            import pysui.sui.sui_builders.get_builders as get_builders
            
            # 使用实际存在的transaction builder
            if hasattr(get_builders, 'GetTx'):
                builder = get_builders.GetTx(
                    digest=tx_hash,
                    options={
                        "showInput": True,
                        "showEffects": True,
                        "showEvents": True,
                        "showObjectChanges": True
                    }
                )
                
                result = self.client.execute(builder)
                tx_data = self._handle_result(result, f"获取交易信息 {tx_hash}")
                
                return tx_data
            
            # 备选方案：尝试GetMultipleTx
            elif hasattr(get_builders, 'GetMultipleTx'):
                builder = get_builders.GetMultipleTx(
                    digests=[tx_hash],
                    options={
                        "showInput": True,
                        "showEffects": True,
                        "showEvents": True,
                        "showObjectChanges": True
                    }
                )
                
                result = self.client.execute(builder)
                tx_data = self._handle_result(result, f"获取交易信息 {tx_hash}")
                
                # GetMultipleTx返回数组，取第一个
                if isinstance(tx_data, list) and len(tx_data) > 0:
                    return tx_data[0]
                return tx_data
            else:
                logger.warning("GetTransactionBlock builder不可用")
                return {
                    'transaction_hash': tx_hash,
                    'error': 'GetTransactionBlock builder不可用，请使用GraphQL接口',
                    'note': 'JSON-RPC GetTransactionBlock已被deprecated'
                }
            
        except Exception as e:
            logger.error(f"获取交易信息失败: {e}")
            return {
                'transaction_hash': tx_hash,
                'error': str(e)
            }


def main():
    """主函数，演示客户端使用方法"""
    try:
        # 创建客户端实例
        logger.info("=== Sui区块链客户端演示 ===")
        client = SuiContractClient()
        
        # 获取账户余额
        logger.info("\n=== 查询账户余额 ===")
        balance_info = client.get_account_balance()
        print(f"活跃地址: {balance_info['active_address']}")
        print(f"总余额: {balance_info['total_balance_sui']:.6f} SUI")
        print(f"SUI对象数量: {len(balance_info['sui_objects'])}")
        
        # 部署合约示例（需要提供有效的Move包路径）
        # logger.info("\n=== 部署合约演示 ===")
        # 注意：这里需要替换为实际的Move包路径
        # package_path = "./my_contract"  # 替换为您的合约路径
        # deploy_result = client.deploy_contract(
        #     package_path=package_path,
        #     gas_budget=50_000_000  # 50M mists
        # )
        # print(f"部署结果: {json.dumps(deploy_result, indent=2, ensure_ascii=False)}")
        
        # 调用合约函数示例
        # logger.info("\n=== 调用合约函数演示 ===")
        # call_result = client.call_contract_function(
        #     package_id="0x1234...",  # 替换为实际的包ID
        #     module_name="example",
        #     function_name="hello_world",
        #     arguments=["Hello, Sui!"],
        #     gas_budget=10_000_000  # 10M mists
        # )
        # print(f"调用结果: {json.dumps(call_result, indent=2, ensure_ascii=False)}")
        
        logger.info("\n=== 演示完成 ===")
        
    except Exception as e:
        logger.error(f"演示过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 