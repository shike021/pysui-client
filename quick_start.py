#!/usr/bin/env python3
"""
Sui客户端快速开始脚本
提供菜单式界面，方便用户选择不同功能进行测试
"""

import sys
import os
from sui_client import SuiContractClient


def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("          🌊 Sui区块链客户端程序 🌊")
    print("     使用pysui库和JSON-RPC接口开发")
    print("=" * 60)
    print()


def print_menu():
    """打印主菜单"""
    print("📋 请选择要执行的操作:")
    print("1. 🧪 测试基本功能（推荐首次运行）")
    print("2. 💰 查询账户余额")
    print("3. 🚀 部署示例合约")
    print("4. 📞 调用合约函数")
    print("5. 🔍 查询对象信息")
    print("6. 📊 查询交易信息")
    print("7. 🎯 运行完整示例")
    print("8. ❓ 显示帮助信息")
    print("0. 👋 退出程序")
    print("-" * 40)


def test_basic_functionality():
    """运行基本功能测试"""
    print("\n🧪 运行基本功能测试...")
    os.system("python test_client.py")


def check_balance():
    """查询账户余额"""
    try:
        print("\n💰 查询账户余额...")
        client = SuiContractClient()
        balance_info = client.get_account_balance()
        
        print(f"✅ 余额查询成功:")
        print(f"   活跃地址: {balance_info['active_address']}")
        print(f"   总余额: {balance_info['total_balance_sui']:.6f} SUI")
        print(f"   总余额(mists): {balance_info['total_balance_mists']:,}")
        print(f"   SUI对象数量: {len(balance_info['sui_objects'])}")
        
        if balance_info['total_balance_sui'] < 1.0:
            print("   ⚠️  建议从水龙头获取更多测试币: sui client faucet")
        
    except Exception as e:
        print(f"❌ 余额查询失败: {e}")


def deploy_contract():
    """部署合约"""
    try:
        print("\n🚀 开始部署示例合约...")
        
        # 检查合约目录是否存在
        if not os.path.exists("./example_contract"):
            print("❌ 未找到example_contract目录")
            print("   请确保example_contract目录存在并包含有效的Move项目")
            return
        
        client = SuiContractClient()
        
        # 检查余额
        balance_info = client.get_account_balance()
        if balance_info['total_balance_sui'] < 0.2:
            print("❌ 余额不足，建议至少有0.2 SUI进行部署")
            print("   运行命令获取测试币: sui client faucet")
            return
        
        print("   编译和部署合约中...")
        deploy_result = client.deploy_contract(
            package_path="./example_contract",
            gas_budget=100_000_000  # 100M mists
        )
        
        print("✅ 合约部署成功!")
        print(f"   包ID: {deploy_result['package_id']}")
        print(f"   UpgradeCap ID: {deploy_result['upgrade_cap_id']}")
        print(f"   事务哈希: {deploy_result['transaction_hash']}")
        print(f"   Gas使用: {deploy_result['gas_used']}")
        
        # 保存包ID到文件，供后续调用使用
        with open("deployed_package_id.txt", "w") as f:
            f.write(deploy_result['package_id'])
        print(f"   📝 包ID已保存到 deployed_package_id.txt")
        
    except Exception as e:
        print(f"❌ 合约部署失败: {e}")


def call_contract():
    """调用合约函数"""
    try:
        print("\n📞 调用合约函数...")
        
        # 尝试从文件读取包ID
        package_id = None
        if os.path.exists("deployed_package_id.txt"):
            with open("deployed_package_id.txt", "r") as f:
                package_id = f.read().strip()
        
        if not package_id:
            package_id = input("请输入合约包ID: ").strip()
            if not package_id:
                print("❌ 未提供包ID")
                return
        
        print(f"   使用包ID: {package_id}")
        
        client = SuiContractClient()
        
        # 调用create_greeting函数
        print("   调用create_greeting函数...")
        call_result = client.call_contract_function(
            package_id=package_id,
            module_name="hello_world",
            function_name="create_greeting",
            arguments=[b"Hello from quick_start!"],
            gas_budget=20_000_000
        )
        
        print("✅ 函数调用成功!")
        print(f"   事务哈希: {call_result['transaction_hash']}")
        print(f"   Gas使用: {call_result['gas_used']}")
        
        if call_result['object_changes']:
            for change in call_result['object_changes']:
                if change.get('type') == 'created':
                    print(f"   创建的对象ID: {change['objectId']}")
        
    except Exception as e:
        print(f"❌ 合约函数调用失败: {e}")


def query_object():
    """查询对象信息"""
    try:
        object_id = input("请输入对象ID: ").strip()
        if not object_id:
            print("❌ 未提供对象ID")
            return
        
        print(f"\n🔍 查询对象信息: {object_id}")
        
        client = SuiContractClient()
        object_info = client.get_object_info(object_id)
        
        print("✅ 对象信息查询成功:")
        print(f"   对象ID: {object_id}")
        print(f"   对象类型: {object_info.get('data', {}).get('type', 'Unknown')}")
        print(f"   拥有者: {object_info.get('data', {}).get('owner', 'Unknown')}")
        print(f"   版本: {object_info.get('data', {}).get('version', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ 对象信息查询失败: {e}")


def query_transaction():
    """查询交易信息"""
    try:
        tx_hash = input("请输入交易哈希: ").strip()
        if not tx_hash:
            print("❌ 未提供交易哈希")
            return
        
        print(f"\n📊 查询交易信息: {tx_hash}")
        
        client = SuiContractClient()
        tx_info = client.get_transaction_info(tx_hash)
        
        print("✅ 交易信息查询成功:")
        print(f"   交易哈希: {tx_hash}")
        print(f"   状态: {tx_info.get('effects', {}).get('status', {}).get('status', 'Unknown')}")
        print(f"   Gas费用: {tx_info.get('effects', {}).get('gasUsed', 'Unknown')}")
        print(f"   发送者: {tx_info.get('transaction', {}).get('data', {}).get('sender', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ 交易信息查询失败: {e}")


def run_full_example():
    """运行完整示例"""
    print("\n🎯 运行完整示例...")
    os.system("python usage_example.py")


def show_help():
    """显示帮助信息"""
    print("\n❓ 帮助信息:")
    print("=" * 50)
    print("1. 首次使用建议先运行'测试基本功能'")
    print("2. 确保已安装Sui CLI并正确配置")
    print("3. 确保账户有足够的SUI余额进行测试")
    print("4. 获取测试币命令: sui client faucet")
    print("5. 查看Sui配置: sui client envs")
    print("6. 切换网络: sui client switch --env <network>")
    print("=" * 50)
    print("\n📁 项目文件说明:")
    print("- sui_client.py: 主要的客户端类")
    print("- usage_example.py: 完整使用示例")
    print("- test_client.py: 基本功能测试")
    print("- example_contract/: 示例Move合约")
    print("- README.md: 详细文档")
    print("=" * 50)


def main():
    """主函数"""
    print_banner()
    
    while True:
        print_menu()
        choice = input("请输入选项 (0-8): ").strip()
        
        if choice == "0":
            print("\n👋 感谢使用Sui客户端程序！")
            break
        elif choice == "1":
            test_basic_functionality()
        elif choice == "2":
            check_balance()
        elif choice == "3":
            deploy_contract()
        elif choice == "4":
            call_contract()
        elif choice == "5":
            query_object()
        elif choice == "6":
            query_transaction()
        elif choice == "7":
            run_full_example()
        elif choice == "8":
            show_help()
        else:
            print("❌ 无效选项，请重新选择")
        
        if choice != "0":
            input("\n按回车键继续...")
            print()


if __name__ == "__main__":
    main() 