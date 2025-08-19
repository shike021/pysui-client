#!/usr/bin/env python3
"""
Sui客户端使用示例
演示如何使用SuiContractClient进行合约部署和调用
"""

import json
import time
from sui_client import SuiContractClient


def main():
    """完整的使用示例"""
    try:
        print("=== Sui智能合约客户端使用示例 ===\n")
        
        # 1. 初始化客户端
        print("1. 初始化客户端...")
        client = SuiContractClient()
        print("✓ 客户端初始化成功\n")
        
        # 2. 查询账户余额
        print("2. 查询账户余额...")
        balance_info = client.get_account_balance()
        print(f"   活跃地址: {balance_info['active_address']}")
        print(f"   总余额: {balance_info['total_balance_sui']:.6f} SUI")
        print(f"   SUI对象数量: {len(balance_info['sui_objects'])}")
        
        # 检查是否有足够的余额
        if balance_info['total_balance_sui'] < 1.0:
            print("   ⚠️  警告: 余额不足1 SUI，可能无法完成合约部署")
        print("✓ 余额查询完成\n")
        
        # 3. 部署合约
        print("3. 部署示例合约...")
        try:
            deploy_result = client.deploy_contract(
                package_path="./example_contract",
                gas_budget=100_000_000  # 100M mists
            )
            
            package_id = deploy_result['package_id']
            upgrade_cap_id = deploy_result['upgrade_cap_id']
            
            print(f"✓ 合约部署成功!")
            print(f"   包ID: {package_id}")
            print(f"   UpgradeCap ID: {upgrade_cap_id}")
            print(f"   事务哈希: {deploy_result['transaction_hash']}")
            print(f"   Gas使用: {deploy_result['gas_used']}")
            print()
            
            # 等待一秒确保事务被处理
            time.sleep(2)
            
            # 4. 调用合约函数 - 创建问候消息
            print("4. 调用合约函数 - 创建问候消息...")
            call_result = client.call_contract_function(
                package_id=package_id,
                module_name="hello_world",
                function_name="create_greeting",
                arguments=[b"Hello, Sui Blockchain!"],  # 传入字节数组
                gas_budget=20_000_000  # 20M mists
            )
            
            print(f"✓ 函数调用成功!")
            print(f"   事务哈希: {call_result['transaction_hash']}")
            print(f"   Gas使用: {call_result['gas_used']}")
            
            # 查看创建的对象
            if call_result['object_changes']:
                for change in call_result['object_changes']:
                    if change.get('type') == 'created':
                        print(f"   创建的对象ID: {change['objectId']}")
                        print(f"   对象类型: {change['objectType']}")
            print()
            
            # 等待一秒
            time.sleep(2)
            
            # 5. 调用合约函数 - 创建共享计数器
            print("5. 调用合约函数 - 创建共享计数器...")
            counter_result = client.call_contract_function(
                package_id=package_id,
                module_name="hello_world",
                function_name="create_counter",
                arguments=[],
                gas_budget=20_000_000
            )
            
            print(f"✓ 计数器创建成功!")
            print(f"   事务哈希: {counter_result['transaction_hash']}")
            
            # 找到创建的计数器对象ID
            counter_id = None
            if counter_result['object_changes']:
                for change in counter_result['object_changes']:
                    if (change.get('type') == 'created' and 
                        'Counter' in change.get('objectType', '')):
                        counter_id = change['objectId']
                        print(f"   计数器对象ID: {counter_id}")
                        break
            print()
            
            if counter_id:
                # 等待一秒
                time.sleep(2)
                
                # 6. 调用合约函数 - 增加计数器
                print("6. 调用合约函数 - 增加计数器...")
                increment_result = client.call_contract_function(
                    package_id=package_id,
                    module_name="hello_world",
                    function_name="increment_counter",
                    arguments=[counter_id],  # 传入计数器对象ID
                    gas_budget=20_000_000
                )
                
                print(f"✓ 计数器递增成功!")
                print(f"   事务哈希: {increment_result['transaction_hash']}")
                
                # 查看事件
                if increment_result['events']:
                    for event in increment_result['events']:
                        if 'parsedJson' in event:
                            event_data = event['parsedJson']
                            if 'old_value' in event_data and 'new_value' in event_data:
                                print(f"   计数器值变化: {event_data['old_value']} -> {event_data['new_value']}")
                print()
            
            # 7. 获取事务详情
            print("7. 获取部署事务的详细信息...")
            tx_info = client.get_transaction_info(deploy_result['transaction_hash'])
            print(f"✓ 事务信息获取成功!")
            print(f"   状态: {tx_info.get('effects', {}).get('status', {}).get('status')}")
            print(f"   Gas费用: {tx_info.get('effects', {}).get('gasUsed')}")
            print(f"   执行的命令数量: {len(tx_info.get('transaction', {}).get('data', {}).get('transaction', {}).get('commands', []))}")
            print()
            
        except FileNotFoundError:
            print("❌ 未找到示例合约目录 './example_contract'")
            print("   请确保example_contract目录存在并包含有效的Move项目")
            print("   或者修改package_path参数指向您的合约目录")
            return
        except Exception as e:
            print(f"❌ 合约操作失败: {e}")
            return
        
        print("=== 示例执行完成 ===")
        print("\n📖 使用说明:")
        print("1. 确保您的Sui配置正确且账户有足够的SUI余额")
        print("2. 可以修改example_contract中的Move代码来测试其他功能")
        print("3. 可以在usage_example.py中添加更多的合约调用示例")
        print("4. 查看sui_client.py了解更多可用的方法")
        
    except Exception as e:
        print(f"❌ 示例执行过程中发生错误: {e}")


if __name__ == "__main__":
    main() 