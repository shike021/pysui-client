#!/usr/bin/env python3
"""
Sui客户端完整功能演示
展示部署合约、调用合约、发送交易的完整流程
"""

from sui_client import SuiContractClient
import json
import time


def 演示_完整流程():
    """演示完整的合约部署和调用流程"""
    
    print("🌊 Sui区块链客户端功能演示")
    print("=" * 50)
    
    try:
        # 1. 创建客户端
        print("\n📱 1. 创建Sui客户端...")
        client = SuiContractClient()
        print(f"   ✅ 客户端创建成功")
        print(f"   📍 连接到: {client.config.rpc_url}")
        print(f"   👤 活跃地址: {client.active_address}")
        
        # 2. 查询余额
        print("\n💰 2. 查询账户余额...")
        balance_info = client.get_account_balance()
        print(f"   💎 总余额: {balance_info['total_balance_sui']:.6f} SUI")
        print(f"   📦 SUI对象: {len(balance_info['sui_objects'])} 个")
        
        if balance_info['total_balance_sui'] < 1.0:
            print("   ⚠️  余额不足，请先获取测试币: sui client faucet")
            return
        
        # 3. 部署合约
        print("\n🚀 3. 部署智能合约...")
        print("   📝 编译Move包...")
        print("   🔨 生成字节码...")
        print("   📡 发送部署交易...")
        
        deploy_result = client.deploy_contract(
            package_path="./example_contract",
            gas_budget=100_000_000  # 100M mists
        )
        
        package_id = deploy_result['package_id']
        upgrade_cap_id = deploy_result['upgrade_cap_id']
        tx_hash = deploy_result['transaction_hash']
        
        print(f"   ✅ 合约部署成功!")
        print(f"   📦 包ID: {package_id}")
        print(f"   🔑 UpgradeCap: {upgrade_cap_id}")
        print(f"   🔗 交易哈希: {tx_hash}")
        print(f"   ⛽ Gas使用: {deploy_result['gas_used']}")
        
        # 等待交易确认
        print("\n⏱️  等待交易确认...")
        time.sleep(3)
        
        # 4. 调用合约函数 - 创建问候消息
        print("\n📞 4. 调用合约函数 - 创建问候消息...")
        call_result1 = client.call_contract_function(
            package_id=package_id,
            module_name="hello_world",
            function_name="create_greeting",
            arguments=[b"Hello from Sui JSON-RPC!"],
            gas_budget=20_000_000
        )
        
        print(f"   ✅ 函数调用成功!")
        print(f"   🔗 交易哈希: {call_result1['transaction_hash']}")
        print(f"   ⛽ Gas使用: {call_result1['gas_used']}")
        
        # 查看创建的对象
        greeting_object_id = None
        if call_result1['object_changes']:
            for change in call_result1['object_changes']:
                if change.get('type') == 'created' and 'GreetingMessage' in change.get('objectType', ''):
                    greeting_object_id = change['objectId']
                    print(f"   📝 创建的问候对象: {greeting_object_id}")
                    break
        
        time.sleep(2)
        
        # 5. 调用合约函数 - 创建计数器
        print("\n📞 5. 调用合约函数 - 创建共享计数器...")
        call_result2 = client.call_contract_function(
            package_id=package_id,
            module_name="hello_world",
            function_name="create_counter",
            arguments=[],
            gas_budget=20_000_000
        )
        
        print(f"   ✅ 计数器创建成功!")
        print(f"   🔗 交易哈希: {call_result2['transaction_hash']}")
        
        # 查找计数器对象ID
        counter_id = None
        if call_result2['object_changes']:
            for change in call_result2['object_changes']:
                if change.get('type') == 'created' and 'Counter' in change.get('objectType', ''):
                    counter_id = change['objectId']
                    print(f"   🔢 创建的计数器: {counter_id}")
                    break
        
        if counter_id:
            time.sleep(2)
            
            # 6. 调用合约函数 - 增加计数器
            print("\n📞 6. 调用合约函数 - 增加计数器...")
            call_result3 = client.call_contract_function(
                package_id=package_id,
                module_name="hello_world",
                function_name="increment_counter",
                arguments=[counter_id],
                gas_budget=20_000_000
            )
            
            print(f"   ✅ 计数器递增成功!")
            print(f"   🔗 交易哈希: {call_result3['transaction_hash']}")
            
            # 查看事件
            if call_result3['events']:
                for event in call_result3['events']:
                    if 'parsedJson' in event:
                        event_data = event['parsedJson']
                        if 'old_value' in event_data and 'new_value' in event_data:
                            print(f"   📊 计数变化: {event_data['old_value']} → {event_data['new_value']}")
        
        # 7. 查询对象信息
        if greeting_object_id:
            print(f"\n🔍 7. 查询对象信息...")
            object_info = client.get_object_info(greeting_object_id)
            print(f"   ✅ 对象查询成功!")
            print(f"   🆔 对象ID: {greeting_object_id}")
            print(f"   📋 对象类型: {object_info.get('data', {}).get('type', 'Unknown')}")
            print(f"   👤 拥有者: {object_info.get('data', {}).get('owner', 'Unknown')}")
        
        # 8. 查询交易信息
        print(f"\n📊 8. 查询交易详情...")
        tx_info = client.get_transaction_info(deploy_result['transaction_hash'])
        print(f"   ✅ 交易查询成功!")
        print(f"   📈 状态: {tx_info.get('effects', {}).get('status', {}).get('status')}")
        print(f"   ⛽ Gas费用: {tx_info.get('effects', {}).get('gasUsed')}")
        print(f"   👤 发送者: {tx_info.get('transaction', {}).get('data', {}).get('sender')}")
        
        print("\n🎉 完整功能演示成功完成!")
        print("\n📋 演示的功能:")
        print("   ✅ 部署Move智能合约")
        print("   ✅ 调用合约函数")
        print("   ✅ 发送和确认交易")
        print("   ✅ 查询对象信息")
        print("   ✅ 查询交易详情")
        print("   ✅ 处理事件和状态变化")
        
        return {
            'package_id': package_id,
            'upgrade_cap_id': upgrade_cap_id,
            'greeting_object_id': greeting_object_id,
            'counter_id': counter_id,
            'transactions': [
                deploy_result['transaction_hash'],
                call_result1['transaction_hash'],
                call_result2['transaction_hash'],
                call_result3['transaction_hash'] if counter_id else None
            ]
        }
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        print("💡 请确保:")
        print("   1. Sui CLI已正确安装和配置")
        print("   2. 账户有足够的SUI余额")
        print("   3. 网络连接正常")
        print("   4. example_contract目录存在且有效")
        return None


def 演示_单独功能():
    """演示每个功能的独立使用"""
    
    print("\n🔧 单独功能演示")
    print("=" * 30)
    
    client = SuiContractClient()
    
    print("\n1️⃣ 只部署合约:")
    print("```python")
    print("deploy_result = client.deploy_contract('./example_contract')")
    print("package_id = deploy_result['package_id']")
    print("```")
    
    print("\n2️⃣ 只调用函数:")
    print("```python")
    print("call_result = client.call_contract_function(")
    print("    package_id='0x123...',")
    print("    module_name='hello_world',")
    print("    function_name='create_greeting',")
    print("    arguments=[b'Hello!']")
    print(")")
    print("```")
    
    print("\n3️⃣ 查询余额:")
    print("```python")
    print("balance = client.get_account_balance()")
    print("print(f'余额: {balance[\"total_balance_sui\"]} SUI')")
    print("```")


if __name__ == "__main__":
    print("选择演示模式:")
    print("1. 完整流程演示（需要网络和余额）")
    print("2. 代码示例演示（无需网络）")
    
    try:
        choice = input("\n请选择 (1/2): ").strip()
        
        if choice == "1":
            result = 演示_完整流程()
            if result:
                print(f"\n💾 演示结果已保存，可用于后续测试")
                
        elif choice == "2":
            演示_单独功能()
            
        else:
            print("🎯 快速开始:")
            print("python quick_start.py  # 交互式菜单")
            print("python 功能演示.py     # 完整演示")
            
    except KeyboardInterrupt:
        print("\n\n👋 演示已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}") 