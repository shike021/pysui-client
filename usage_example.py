#!/usr/bin/env python3
"""
Sui客户端使用示例
演示如何使用SuiContractClient进行合约部署和调用
"""

import json
import time
from sui_client import SuiContractClient

try:
    from sui_grpc_client import SuiGrpcClient
except Exception:
    SuiGrpcClient = None


def main():
    """完整的使用示例"""
    try:
        print("=== Sui智能合约客户端使用示例 ===\n")
        
        # 1. 初始化客户端 (JSON-RPC)
        print("1. 初始化 JSON-RPC 客户端...")
        client = SuiContractClient()
        print("✓ JSON-RPC 客户端初始化成功\n")
        
        # 2. 查询账户余额
        print("2. 查询账户余额 (JSON-RPC)...")
        balance_info = client.get_account_balance()
        print(f"   活跃地址: {balance_info['active_address']}")
        print(f"   总余额: {balance_info['total_balance_sui']:.6f} SUI")
        print(f"   SUI对象数量: {len(balance_info['sui_objects'])}")
        
        # 检查是否有足够的余额
        if balance_info['total_balance_sui'] < 1.0:
            print("   ⚠️  警告: 余额不足1 SUI，可能无法完成合约部署")
        print("✓ 余额查询完成\n")

        # 3. 可选：初始化 gRPC 客户端并查询余额
        if SuiGrpcClient is not None:
            try:
                print("3. 初始化 gRPC 客户端并查询余额...")
                gclient = SuiGrpcClient()
                gbalance = gclient.get_account_balance()
                print(f"   (gRPC) 活跃地址: {gbalance['active_address']}")
                print(f"   (gRPC) 总余额: {gbalance['total_balance_sui']:.6f} SUI")
                print(f"   (gRPC) SUI对象数量: {len(gbalance['sui_objects'])}")
                print("✓ gRPC 查询完成\n")
            except Exception as e:
                print(f"   ⚠️ gRPC 客户端不可用或节点未开启 gRPC：{e}\n")
        else:
            print("3. 跳过 gRPC 演示（未找到 gRPC 客户端类）\n")
        
        print("=== 示例执行完成 ===")
        print("\n📖 使用说明:")
        print("1. 确保您的Sui配置正确且账户有足够的SUI余额")
        print("2. gRPC 需要 Full Node 启用 gRPC 索引 (fullnode.yaml: rpc.enable-indexing: true)")
        print("3. 如需体验 gRPC，请安装 pysui>=0.88.0 且 grpcio，并运行 `SuiGrpcClient` 示例")
        
    except Exception as e:
        print(f"❌ 示例执行过程中发生错误: {e}")


if __name__ == "__main__":
    main() 