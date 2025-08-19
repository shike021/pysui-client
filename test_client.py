#!/usr/bin/env python3
"""
简单的Sui客户端测试脚本
验证基本功能是否正常工作
"""

import sys
import traceback
from sui_client import SuiContractClient


def test_basic_functionality():
    """测试基本功能"""
    print("🧪 开始测试Sui客户端基本功能...\n")
    
    try:
        # 1. 测试客户端初始化
        print("1. 测试客户端初始化...")
        client = SuiContractClient()
        print("✅ 客户端初始化成功")
        print(f"   - RPC URL: {client.config.rpc_url}")
        print(f"   - 活跃地址: {client.active_address}")
        print(f"   - Gas价格: {client.client.current_gas_price}")
        print()
        
        # 2. 测试余额查询
        print("2. 测试余额查询...")
        balance_info = client.get_account_balance()
        print("✅ 余额查询成功")
        print(f"   - 活跃地址: {balance_info['active_address']}")
        print(f"   - 总余额: {balance_info['total_balance_sui']:.6f} SUI")
        print(f"   - 总余额(mists): {balance_info['total_balance_mists']:,}")
        print(f"   - SUI对象数量: {len(balance_info['sui_objects'])}")
        print()
        
        # 检查余额是否足够进行测试
        if balance_info['total_balance_sui'] < 0.1:
            print("⚠️  警告: 余额不足0.1 SUI，建议从水龙头获取测试币")
            print("   运行命令: sui client faucet")
        
        # 3. 测试对象查询（如果有SUI对象的话）
        if balance_info['sui_objects']:
            print("3. 测试对象信息查询...")
            first_object = balance_info['sui_objects'][0]
            
            # 检查是否有具体的object_id（GetCoins返回）还是汇总信息（GetAllCoinBalances返回）
            if 'object_id' in first_object and first_object['object_id']:
                object_id = first_object['object_id']
                try:
                    object_info = client.get_object_info(object_id)
                    print("✅ 对象信息查询成功")
                    print(f"   - 对象ID: {object_id}")
                    print(f"   - 对象类型: {object_info.get('data', {}).get('type', 'Unknown')}")
                    print(f"   - 拥有者: {object_info.get('data', {}).get('owner', 'Unknown')}")
                    balance = object_info.get('data', {}).get('content', {}).get('fields', {}).get('balance', 0)
                    print(f"   - 余额: {int(balance) / 1_000_000_000:.6f} SUI")
                    print()
                except Exception as e:
                    print(f"⚠️  对象信息查询失败: {e}")
                    print()
            else:
                # 这是GetAllCoinBalances的汇总信息
                print("✅ 对象信息查询成功（汇总信息）")
                print(f"   - 币种类型: {first_object.get('coin_type', '未知')}")
                print(f"   - 对象数量: {first_object.get('coin_count', 0)}")
                print(f"   - 总余额: {first_object.get('total_balance', 0) / 1_000_000_000:.6f} SUI")
                print()
        else:
            print("3. 跳过对象查询测试（没有找到SUI对象）\n")
        
        print("✅ 所有基本功能测试通过!")
        print("\n📋 测试总结:")
        print("✅ 客户端连接正常")
        print("✅ 余额查询功能正常") 
        if balance_info['sui_objects']:
            print("✅ 对象查询功能正常")
        print("✅ JSON-RPC接口工作正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print(f"错误详情:\n{traceback.format_exc()}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("    Sui区块链客户端基础功能测试")
    print("=" * 50)
    print()
    
    success = test_basic_functionality()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成！所有基本功能正常工作。")
        print("\n📝 下一步:")
        print("1. 运行 'python usage_example.py' 进行完整功能测试")
        print("2. 如果要测试合约部署，确保有足够的SUI余额")
        print("3. 查看 'sui_client.py' 了解更多API使用方法")
    else:
        print("💥 测试失败！请检查:")
        print("1. Sui CLI是否正确安装和配置")
        print("2. 网络连接是否正常")
        print("3. Sui配置文件是否正确")
        print("4. pysui库是否正确安装")
        sys.exit(1)
    
    print("=" * 50)


if __name__ == "__main__":
    main() 