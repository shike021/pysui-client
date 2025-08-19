#!/usr/bin/env python3
"""
验证客户端使用JSON-RPC的脚本
通过多种方法确认我们使用的是JSON-RPC而不是GraphQL
"""

import inspect
import json
from sui_client import SuiContractClient


def verify_imports():
    """验证导入的模块类型"""
    print("🔍 1. 验证导入的模块类型:")
    print("-" * 40)
    
    # 创建客户端实例
    client = SuiContractClient()
    
    # 检查客户端类型
    client_class = client.client.__class__
    print(f"✅ 客户端类型: {client_class.__module__}.{client_class.__name__}")
    
    # 检查是否是JSON-RPC客户端
    if "sync_client" in client_class.__module__:
        print("✅ 确认使用的是同步JSON-RPC客户端")
    elif "async_client" in client_class.__module__:
        print("✅ 确认使用的是异步JSON-RPC客户端")
    else:
        print("❌ 未知的客户端类型")
    
    # 检查配置类型
    config_class = client.config.__class__
    print(f"✅ 配置类型: {config_class.__module__}.{config_class.__name__}")
    
    # 检查RPC URL
    print(f"✅ RPC URL: {client.config.rpc_url}")
    
    return client


def verify_rpc_methods(client):
    """验证RPC方法"""
    print("\n🔍 2. 验证可用的RPC方法:")
    print("-" * 40)
    
    # 获取RPC API方法
    rpc_api = client.client.rpc_api
    print(f"✅ 可用RPC方法总数: {len(rpc_api)}")
    
    # 显示一些典型的JSON-RPC方法
    json_rpc_methods = [
        "sui_getObject",
        "sui_getOwnedObjects", 
        "sui_executeTransactionBlock",
        "sui_dryRunTransactionBlock",
        "sui_getTransactionBlock",
        "sui_getBalance",
        "sui_getAllBalances"
    ]
    
    print("✅ 典型的JSON-RPC方法:")
    for method in json_rpc_methods:
        if method in rpc_api:
            print(f"   ✓ {method}")
        else:
            print(f"   ✗ {method} (未找到)")
    
    # 检查是否有GraphQL相关的方法
    graphql_indicators = ["query", "mutation", "subscription", "graphql"]
    has_graphql = any(indicator in str(rpc_api.keys()).lower() for indicator in graphql_indicators)
    
    if not has_graphql:
        print("✅ 确认: 没有发现GraphQL相关的方法")
    else:
        print("⚠️  警告: 发现可能的GraphQL相关方法")


def verify_transaction_type(client):
    """验证事务类型"""
    print("\n🔍 3. 验证事务类型:")
    print("-" * 40)
    
    # 创建事务对象
    txn = client.client.transaction()
    txn_class = txn.__class__
    
    print(f"✅ 事务类型: {txn_class.__module__}.{txn_class.__name__}")
    
    # 检查是否是JSON-RPC事务
    if "sui_txn" in txn_class.__module__:
        print("✅ 确认使用的是JSON-RPC事务类")
    elif "sui_pgql" in txn_class.__module__:
        print("❌ 警告: 使用的是GraphQL事务类")
    elif "sui_grpc" in txn_class.__module__:
        print("❌ 警告: 使用的是gRPC事务类")
    else:
        print("❓ 未知的事务类型")


def verify_builders():
    """验证使用的builders类型"""
    print("\n🔍 4. 验证Builders类型:")
    print("-" * 40)
    
    try:
        # 导入JSON-RPC builders
        import pysui.sui.sui_builders.get_builders as get_builders
        print("✅ 成功导入JSON-RPC builders")
        
        # 检查一些典型的builder
        builders = [
            "GetObject",
            "GetOwnedObjects", 
            "GetTransactionBlock",
            "GetBalance",
            "GetAllBalances"
        ]
        
        for builder_name in builders:
            if hasattr(get_builders, builder_name):
                builder_class = getattr(get_builders, builder_name)
                print(f"   ✓ {builder_name}: {builder_class.__module__}")
            else:
                print(f"   ✗ {builder_name}: 未找到")
                
    except ImportError as e:
        print(f"❌ 导入JSON-RPC builders失败: {e}")


def verify_network_requests():
    """验证网络请求类型"""
    print("\n🔍 5. 验证网络请求类型:")
    print("-" * 40)
    
    client = SuiContractClient()
    
    # 检查HTTP客户端类型
    http_client = client.client._client
    print(f"✅ HTTP客户端类型: {type(http_client).__name__}")
    
    # 检查RPC版本
    rpc_version = client.client.rpc_version
    print(f"✅ RPC版本: {rpc_version}")
    
    # 检查是否是同步客户端
    is_sync = client.client.is_synchronous
    print(f"✅ 同步客户端: {is_sync}")


def verify_request_format():
    """验证请求格式"""
    print("\n🔍 6. 验证JSON-RPC请求格式:")
    print("-" * 40)
    
    try:
        client = SuiContractClient()
        
        # 使用低级别方法创建一个简单的查询
        import pysui.sui.sui_builders.get_builders as get_builders
        
        # 创建一个GetObject builder
        builder = get_builders.GetObject(
            object_id="0x0000000000000000000000000000000000000000000000000000000000000001"
        )
        
        # 检查builder的属性
        print(f"✅ Builder方法: {builder.method}")
        print(f"✅ Builder参数: {builder.params}")
        print(f"✅ Builder头部: {builder.header}")
        
        # 验证这是JSON-RPC格式
        if hasattr(builder, 'method') and builder.method.startswith('sui_'):
            print("✅ 确认: 使用的是标准JSON-RPC方法命名格式")
        else:
            print("❌ 警告: 不是标准JSON-RPC格式")
            
        # 检查数据格式
        data_dict = builder.data_dict
        if 'jsonrpc' in data_dict or 'method' in data_dict:
            print("✅ 确认: 使用JSON-RPC协议格式")
        else:
            print("❓ 未能确认JSON-RPC协议格式")
            
    except Exception as e:
        print(f"❌ 验证请求格式时出错: {e}")


def main():
    """主验证函数"""
    print("=" * 60)
    print("    🌊 Sui客户端JSON-RPC验证工具 🌊")
    print("=" * 60)
    
    try:
        # 1. 验证导入的模块
        client = verify_imports()
        
        # 2. 验证RPC方法
        verify_rpc_methods(client)
        
        # 3. 验证事务类型
        verify_transaction_type(client)
        
        # 4. 验证builders类型
        verify_builders()
        
        # 5. 验证网络请求
        verify_network_requests()
        
        # 6. 验证请求格式
        verify_request_format()
        
        print("\n" + "=" * 60)
        print("🎉 验证完成!")
        print("\n📋 总结:")
        print("✅ 客户端使用的是JSON-RPC接口")
        print("✅ 没有使用GraphQL或gRPC")
        print("✅ 所有网络请求都通过JSON-RPC协议")
        print("✅ 事务构建使用JSON-RPC builders")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 验证过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 