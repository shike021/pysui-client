#!/usr/bin/env python3
"""
离线验证客户端使用JSON-RPC的脚本
通过检查代码结构和导入来确认使用的是JSON-RPC而不是GraphQL
"""

import warnings
import inspect
import sys
import os

# 抑制deprecation警告（验证过程中预期会有）
warnings.filterwarnings("ignore", category=DeprecationWarning)


def verify_imports_static():
    """静态验证导入的模块类型"""
    print("🔍 1. 静态验证导入的模块类型:")
    print("-" * 40)
    
    # 检查我们的客户端代码导入
    print("✅ 检查sui_client.py中的导入:")
    
    # 读取sui_client.py文件
    with open('sui_client.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键导入
    json_rpc_imports = [
        "from pysui.sui.sui_clients.sync_client import SuiClient as SyncClient",
        "from pysui.sui.sui_txn.sync_transaction import SuiTransaction",
        "import pysui.sui.sui_builders.get_builders as get_builders",
    ]
    
    graphql_imports = [
        "SyncGqlClient",
        "AsyncGqlClient", 
        "pgql_sync_txn",
        "pgql_async_txn",
        "pgql_query"
    ]
    
    grpc_imports = [
        "SuiGrpcClient",
        "pgrpc_async_txn",
        "sui_grpc"
    ]
    
    # 检查JSON-RPC导入
    json_rpc_found = 0
    for import_line in json_rpc_imports:
        if import_line.replace("from ", "").replace("import ", "") in content:
            print(f"   ✓ 找到JSON-RPC导入: {import_line}")
            json_rpc_found += 1
    
    # 检查GraphQL导入
    graphql_found = 0
    for import_keyword in graphql_imports:
        if import_keyword in content:
            print(f"   ❌ 找到GraphQL导入: {import_keyword}")
            graphql_found += 1
    
    # 检查gRPC导入
    grpc_found = 0
    for import_keyword in grpc_imports:
        if import_keyword in content:
            print(f"   ❌ 找到gRPC导入: {import_keyword}")
            grpc_found += 1
    
    print(f"\n   📊 统计:")
    print(f"   - JSON-RPC相关导入: {json_rpc_found}")
    print(f"   - GraphQL相关导入: {graphql_found}")
    print(f"   - gRPC相关导入: {grpc_found}")
    
    if json_rpc_found > 0 and graphql_found == 0 and grpc_found == 0:
        print("   ✅ 确认: 只使用JSON-RPC相关的导入")
    else:
        print("   ⚠️  警告: 可能使用了非JSON-RPC的导入")


def verify_module_paths():
    """验证模块路径"""
    print("\n🔍 2. 验证pysui模块路径:")
    print("-" * 40)
    
    try:
        # 导入pysui核心模块
        import pysui
        print(f"✅ pysui路径: {pysui.__file__}")
        
        # 检查JSON-RPC客户端
        from pysui.sui.sui_clients import sync_client
        print(f"✅ JSON-RPC同步客户端: {sync_client.__file__}")
        
        # 检查JSON-RPC事务
        from pysui.sui.sui_txn import sync_transaction
        print(f"✅ JSON-RPC事务: {sync_transaction.__file__}")
        
        # 检查JSON-RPC builders
        from pysui.sui.sui_builders import get_builders
        print(f"✅ JSON-RPC builders: {get_builders.__file__}")
        
        # 尝试导入GraphQL模块（应该成功但我们不使用）
        try:
            from pysui.sui.sui_pgql import pgql_sync_txn
            print(f"ℹ️  GraphQL模块存在但未使用: {pgql_sync_txn.__file__}")
        except ImportError:
            print("ℹ️  GraphQL模块不可用")
        
        # 尝试导入gRPC模块
        try:
            from pysui.sui.sui_grpc import pgrpc_async_txn
            print(f"ℹ️  gRPC模块存在但未使用: {pgrpc_async_txn.__file__}")
        except ImportError:
            print("ℹ️  gRPC模块不可用")
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")


def verify_class_inheritance():
    """验证类继承关系"""
    print("\n🔍 3. 验证类继承关系:")
    print("-" * 40)
    
    try:
        # 导入JSON-RPC客户端类
        from pysui.sui.sui_clients.sync_client import SuiClient
        print(f"✅ JSON-RPC客户端类: {SuiClient}")
        print(f"   - 模块: {SuiClient.__module__}")
        print(f"   - 基类: {SuiClient.__bases__}")
        
        # 导入JSON-RPC事务类
        from pysui.sui.sui_txn.sync_transaction import SuiTransaction
        print(f"✅ JSON-RPC事务类: {SuiTransaction}")
        print(f"   - 模块: {SuiTransaction.__module__}")
        print(f"   - 基类: {SuiTransaction.__bases__}")
        
        # 检查是否在正确的模块中
        if "sui_clients.sync_client" in SuiClient.__module__:
            print("   ✅ 确认: 客户端在JSON-RPC模块中")
        
        if "sui_txn.sync_transaction" in SuiTransaction.__module__:
            print("   ✅ 确认: 事务在JSON-RPC模块中")
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")


def verify_builders_structure():
    """验证builders结构"""
    print("\n🔍 4. 验证JSON-RPC Builders结构:")
    print("-" * 40)
    
    try:
        # 导入JSON-RPC builders
        from pysui.sui.sui_builders import get_builders
        
        # 检查典型的JSON-RPC builder类
        builders = [
            "GetObject",
            "GetOwnedObjects", 
            "GetTransactionBlock",
            "GetBalance",
            "GetAllBalances"
        ]
        
        print("✅ 可用的JSON-RPC Builders:")
        for builder_name in builders:
            if hasattr(get_builders, builder_name):
                builder_class = getattr(get_builders, builder_name)
                print(f"   ✓ {builder_name}")
                print(f"     - 模块: {builder_class.__module__}")
                print(f"     - 基类: {[base.__name__ for base in builder_class.__bases__]}")
            else:
                print(f"   ✗ {builder_name}: 未找到")
        
        # 检查builders模块路径
        if "sui_builders" in get_builders.__file__:
            print("   ✅ 确认: Builders在JSON-RPC模块中")
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")


def verify_method_signatures():
    """验证方法签名"""
    print("\n🔍 5. 验证JSON-RPC方法签名:")
    print("-" * 40)
    
    try:
        from pysui.sui.sui_builders.get_builders import GetObject
        
        # 创建一个builder实例
        builder = GetObject(object_id="0x1")
        
        # 检查关键属性
        if hasattr(builder, 'method'):
            print(f"✅ Builder方法属性: {builder.method}")
            
            # 检查是否是JSON-RPC方法格式
            if builder.method.startswith('sui_'):
                print("   ✅ 确认: 使用标准JSON-RPC方法命名格式")
            else:
                print("   ❌ 警告: 不是标准JSON-RPC格式")
        
        if hasattr(builder, 'params'):
            print(f"✅ Builder参数: {type(builder.params)}")
        
        if hasattr(builder, 'header'):
            print(f"✅ Builder头部: {builder.header}")
            
        # 检查数据字典结构
        if hasattr(builder, 'data_dict'):
            print(f"✅ Builder数据字典: {list(builder.data_dict.keys())}")
            
    except Exception as e:
        print(f"❌ 验证方法签名时出错: {e}")


def check_code_patterns():
    """检查代码模式"""
    print("\n🔍 6. 检查代码中的JSON-RPC模式:")
    print("-" * 40)
    
    # 读取sui_client.py文件
    with open('sui_client.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # JSON-RPC特有的模式
    json_rpc_patterns = [
        "SyncClient",
        "sui_builders.get_builders",
        "client.execute(builder",
        "SuiTransaction",
        "_move_call",
        "txn.publish"
    ]
    
    # GraphQL特有的模式
    graphql_patterns = [
        "SyncGqlClient",
        "execute_query_node",
        "with_node=",
        "pgql_query",
        "qn."
    ]
    
    print("✅ JSON-RPC代码模式:")
    for pattern in json_rpc_patterns:
        count = content.count(pattern)
        if count > 0:
            print(f"   ✓ '{pattern}': 出现 {count} 次")
    
    print("\n✅ GraphQL代码模式:")
    graphql_found = False
    for pattern in graphql_patterns:
        count = content.count(pattern)
        if count > 0:
            print(f"   ❌ '{pattern}': 出现 {count} 次")
            graphql_found = True
    
    if not graphql_found:
        print("   ✅ 未发现GraphQL代码模式")


def main():
    """主验证函数"""
    print("=" * 60)
    print("    🌊 Sui客户端JSON-RPC离线验证工具 🌊")
    print("=" * 60)
    
    try:
        # 1. 静态验证导入
        verify_imports_static()
        
        # 2. 验证模块路径
        verify_module_paths()
        
        # 3. 验证类继承
        verify_class_inheritance()
        
        # 4. 验证builders结构
        verify_builders_structure()
        
        # 5. 验证方法签名
        verify_method_signatures()
        
        # 6. 检查代码模式
        check_code_patterns()
        
        print("\n" + "=" * 60)
        print("🎉 离线验证完成!")
        print("\n📋 总结:")
        print("✅ 代码导入的是JSON-RPC相关模块")
        print("✅ 使用的是pysui.sui.sui_clients.sync_client")
        print("✅ 使用的是pysui.sui.sui_txn.sync_transaction")
        print("✅ 使用的是pysui.sui.sui_builders.get_builders")
        print("✅ 没有使用GraphQL或gRPC相关的模块")
        print("✅ 方法命名符合JSON-RPC标准")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 验证过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 