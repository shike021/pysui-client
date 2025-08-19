#!/usr/bin/env python3
"""
Pysui Client Launcher (Unified Menu)

- 移除位置參數，僅暴露 --protocol {jsonrpc,grpc,auto}
- 不管選擇 grpc 還是 json-rpc，都會進入統一的菜單選擇
- auto: 優先嘗試 gRPC，失敗回退 JSON-RPC
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Any, Optional

# 將當前目錄加入模塊路徑
sys.path.insert(0, str(Path(__file__).parent))


def build_client(protocol: str) -> tuple[str, Any]:
    """根據協議構造客戶端。

    Returns: (effective_protocol, client_instance)
    """
    # 延遲導入，避免未安裝時阻塞其他協議
    from sui_client import SuiContractClient

    if protocol == 'jsonrpc':
        return 'jsonrpc', SuiContractClient()

    if protocol == 'grpc':
        try:
            from sui_grpc_client import SuiGrpcClient
        except Exception as e:
            raise RuntimeError(f"gRPC 客戶端不可用：{e}")
        return 'grpc', SuiGrpcClient()

    # auto: 先試 gRPC，失敗回退 JSON-RPC
    try:
        from sui_grpc_client import SuiGrpcClient
        eff = 'grpc'
        cli = SuiGrpcClient()
        return eff, cli
    except Exception as e:
        print(f"⚠️ gRPC 無法使用，回退到 JSON-RPC。原因: {e}")
        return 'jsonrpc', SuiContractClient()


def read_line(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        return ''


def read_int(prompt: str) -> Optional[int]:
    raw = read_line(prompt)
    if not raw:
        return None
    try:
        return int(raw.replace('_', '').replace(',', ''))
    except ValueError:
        print("輸入的數字無效，跳過。")
        return None


def read_json_list(prompt: str) -> list[Any]:
    raw = read_line(prompt)
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        print("請輸入 JSON 陣列，例如: [\"0xabc...\", 123, true]")
        return []
    except Exception as e:
        print(f"JSON 解析失敗: {e}")
        return []


def show_menu(effective_protocol: str, active_address: str) -> None:
    print("\n============== Pysui 統一菜單 ==============")
    print(f"協議: {effective_protocol.upper()}    活躍地址: {active_address}")
    print("1) 查詢賬戶餘額")
    print("2) 部署合約 (Move 包)")
    print("3) 調用合約函數")
    print("4) 查詢對象信息")
    print("5) 查詢交易信息")
    print("0) 退出")
    print("=========================================")


def main():
    parser = argparse.ArgumentParser(description='Pysui Client Launcher (Unified Menu)')
    parser.add_argument('--protocol', dest='protocol', default='auto',
                        choices=['jsonrpc', 'grpc', 'auto'],
                        help='選擇協議: jsonrpc | grpc | auto (默認: auto)')
    args = parser.parse_args()

    try:
        effective_protocol, client = build_client(args.protocol)
        # 嘗試拿到活躍地址
        active_address = getattr(client, 'active_address', '')

        while True:
            show_menu(effective_protocol, str(active_address))
            choice = read_line('請選擇操作: ')

            if choice == '0':
                print('再見!')
                return

            elif choice == '1':
                try:
                    info = client.get_account_balance()
                    print(json.dumps(info, indent=2, ensure_ascii=False))
                except Exception as e:
                    print(f"❌ 查詢餘額失敗: {e}")

            elif choice == '2':
                pkg = read_line('Move 包路徑 (例如 ./example_contract): ')
                gas = read_int('Gas 預算 (mists，可空): ')
                build_args = read_json_list('構建參數 JSON 陣列 (可空): ')
                try:
                    res = client.deploy_contract(package_path=pkg, gas_budget=gas, build_args=build_args or None)
                    print(json.dumps(res, indent=2, ensure_ascii=False))
                except Exception as e:
                    print(f"❌ 部署失敗: {e}")

            elif choice == '3':
                package_id = read_line('package_id: ')
                module_name = read_line('module_name: ')
                function_name = read_line('function_name: ')
                args_list = read_json_list('arguments (JSON 陣列，可空): ')
                type_args = read_json_list('type_arguments (JSON 陣列，可空): ')
                gas = read_int('Gas 預算 (mists，可空): ')
                try:
                    res = client.call_contract_function(
                        package_id=package_id,
                        module_name=module_name,
                        function_name=function_name,
                        arguments=args_list or None,
                        type_arguments=type_args or None,
                        gas_budget=gas,
                    )
                    print(json.dumps(res, indent=2, ensure_ascii=False))
                except Exception as e:
                    print(f"❌ 調用失敗: {e}")

            elif choice == '4':
                object_id = read_line('object_id: ')
                try:
                    res = client.get_object_info(object_id)
                    print(json.dumps(res, indent=2, ensure_ascii=False))
                except Exception as e:
                    print(f"❌ 查詢對象失敗: {e}")

            elif choice == '5':
                tx = read_line('交易哈希 (digest): ')
                try:
                    res = client.get_transaction_info(tx)
                    print(json.dumps(res, indent=2, ensure_ascii=False))
                except Exception as e:
                    print(f"❌ 查詢交易失敗: {e}")

            else:
                print('無效選擇，請重試。')

    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
