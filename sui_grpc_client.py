#!/usr/bin/env python3
"""
Sui 区块链 gRPC 客户端程序
基于 pysui 提供的 gRPC 支持（Beta），实现与 Full Node 的 gRPC 通信：
- 账户余额查询
- 部署 Move 包
- 调用合约函数（Programmable Transaction）
- 查询对象信息
- 查询交易信息

实现目标：
- 尽可能与 `sui_client.SuiContractClient` 的方法签名与返回结构保持一致，便于替换/并存。
- 若本地 pysui 版本不具备 gRPC 能力，或 Full Node 未开启 gRPC 索引，提供明确的报错与指引。

注意：
- gRPC 为 Beta 能力，Full Node 需在配置中启用 `rpc.enable-indexing: true` 才能完整服务。
- 需在 requirements 中安装 `grpcio`（多数情况下 pysui 已处理 protobuf 依赖）。
"""

import logging
import sys
import json
from typing import Any, Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GrpcUnavailableError(RuntimeError):
    pass


class SuiGrpcClient:
    """
    Sui gRPC 客户端

    依赖 pysui 的 gRPC 支持。
    """

    def __init__(self, config_path: Optional[str] = None):
        try:
            # 延迟导入，便于给出更可读的错误
            try:
                from pysui import SuiConfig
            except Exception as e:
                raise GrpcUnavailableError(
                    f"未找到 pysui，请安装或升级 pysui>=0.88.0。原始错误: {e}"
                )

            # 载入配置
            if config_path:
                self.config = SuiConfig.user_config(config_path)
            else:
                self.config = SuiConfig.default_config()

            # 检测/创建 gRPC 客户端
            self._client = self._construct_grpc_client(self.config)

            # 活跃地址
            self.active_address = self.config.active_address

            # 记录连接信息
            grpc_url = getattr(self.config, 'grpc_url', None) or '<未在配置中发现 grpc_url>'
            logger.info(f"已准备使用 Sui gRPC 节点: {grpc_url}")
            logger.info(f"当前活跃地址: {self.active_address}")

            # 健康检查
            self._check_connection()
        except Exception as e:
            logger.error(f"初始化 Sui gRPC 客户端失败: {e}")
            raise

    def _construct_grpc_client(self, config: Any) -> Any:
        """构造 pysui gRPC 客户端，兼容不同版本命名。"""
        # 候选路径（根据 pysui 项目演进梳理，按顺序尝试）
        candidate_imports = [
            # 新版可能导出专用 gRPC 同步客户端
            ("pysui.sui.sui_clients", "GrpcClient"),
            # 也可能在 grpc_client 模块中
            ("pysui.sui.sui_clients.grpc_client", "GrpcClient"),
            # 某些版本可能提供统一 SyncClient，但要求传参指明后端
            ("pysui", "SyncClient"),
        ]

        last_err: Optional[Exception] = None
        for module_path, class_name in candidate_imports:
            try:
                mod = __import__(module_path, fromlist=[class_name])
                cls = getattr(mod, class_name)
                # 尝试不同的构造方式
                try:
                    # 优先直接使用 GrpcClient(config)
                    client = cls(config)
                    logger.debug(f"使用 {module_path}.{class_name} 作为 gRPC 客户端")
                    return client
                except TypeError:
                    # 可能是 SyncClient(config, transport='grpc') 这类签名
                    try:
                        client = cls(config, transport='grpc')
                        logger.debug(f"使用 {module_path}.{class_name}(transport='grpc') 作为 gRPC 客户端")
                        return client
                    except Exception as e2:
                        last_err = e2
                        continue
            except Exception as e:
                last_err = e
                continue

        hint = (
            "未能构造 pysui gRPC 客户端。请确保:\n"
            "- 安装 pysui>=0.88.0（建议 0.89.0 或以上）\n"
            "- 已安装 grpcio（requirements 已包含）\n"
            "- Full Node 已启用 gRPC 索引 (fullnode.yaml: rpc.enable-indexing: true)\n"
            "- 参考 pysui 仓库文档 PYSUI_GRPC.md 获取用法与版本要求\n"
        )
        raise GrpcUnavailableError(hint + (f"\n最后错误: {last_err}" if last_err else ""))

    def _handle_result(self, result: Any, operation: str) -> Dict[str, Any]:
        """兼容处理 pysui 的返回类型，统一为 dict。"""
        # JSON-RPC 路径使用 SuiRpcResult；gRPC 可能返回不同类型
        try:
            # 尝试 JSON-RPC 风格（带 is_ok/result_data）
            if hasattr(result, 'is_ok') and callable(result.is_ok):
                if result.is_ok():
                    data = getattr(result, 'result_data', None)
                    if hasattr(data, 'to_json'):
                        return json.loads(data.to_json())
                    return data if isinstance(data, dict) else json.loads(json.dumps(data, default=str))
                raise RuntimeError(getattr(result, 'result_string', f"{operation} 失败"))

            # gRPC：若已有 protobuf/模型对象，尝试 to_json 或转字典
            if hasattr(result, 'to_json'):
                return json.loads(result.to_json())

            # 退化为通用序列化
            return json.loads(json.dumps(result, default=str))
        except Exception as e:
            raise RuntimeError(f"{operation} 结果处理失败: {e}") from e

    def _check_connection(self):
        """以查询参考 Gas 价格/系统状态等方式做连通性验证。"""
        try:
            # 尝试在 pysui 中寻找 gRPC LiveData/系统状态读取能力
            check_ok = False

            # 方案1：使用 client.current_gas_price（若 pysui 统一暴露）
            try:
                gas_price = getattr(self._client, 'current_gas_price', None)
                if callable(gas_price):
                    _ = gas_price()
                    check_ok = True
                elif gas_price is not None:
                    _ = gas_price
                    check_ok = True
            except Exception:
                pass

            # 方案2：尝试通过 builder 执行简单只读请求
            if not check_ok:
                try:
                    import pysui.sui.sui_builders.get_builders as get_builders
                    if hasattr(get_builders, 'GetReferenceGasPrice'):
                        builder = get_builders.GetReferenceGasPrice()
                        res = self._client.execute(builder)
                        _ = self._handle_result(res, "gRPC 参考 Gas 价格查询")
                        check_ok = True
                except Exception:
                    pass

            if not check_ok:
                raise RuntimeError("无法通过 gRPC 进行健康检查。")

            logger.info("gRPC 连接健康检查通过")
        except Exception as e:
            raise GrpcUnavailableError(
                f"无法通过 gRPC 连接到 Sui 节点，请确认 fullnode 已开启 gRPC，或网络/证书可用。详情: {e}"
            )

    def get_account_balance(self) -> Dict[str, Any]:
        """获取账户 SUI 余额（gRPC）。"""
        try:
            import pysui.sui.sui_builders.get_builders as get_builders

            # 优先使用 suix 等价查询（如果 pysui 将其映射到 gRPC LiveDataService）
            builder = None
            if hasattr(get_builders, 'GetAllCoinBalances'):
                builder = get_builders.GetAllCoinBalances(owner=self.active_address)
            elif hasattr(get_builders, 'GetCoins'):
                builder = get_builders.GetCoins(owner=self.active_address, coin_type="0x2::sui::SUI")

            if not builder:
                raise RuntimeError("当前 pysui 版本不支持通过 builder 查询余额（gRPC）。")

            result = self._client.execute(builder)

            # 与 JSON-RPC 版本對齊：直接從 result.result_data (對象屬性) 解析，避免轉字典丟失信息
            if hasattr(result, 'is_ok') and callable(result.is_ok) and result.is_ok():
                balance_data = getattr(result, 'result_data', None)
                total_balance = 0
                sui_objects: List[Dict[str, Any]] = []

                # 情況A：GetAllCoinBalances 對象，具備 items 屬性
                if hasattr(balance_data, 'items') and balance_data.items:
                    for balance_item in balance_data.items:
                        if getattr(balance_item, 'coin_type', None) == '0x2::sui::SUI':
                            total_balance = int(getattr(balance_item, 'total_balance', 0))
                            coin_count = int(getattr(balance_item, 'coin_object_count', 0))
                            sui_objects.append({
                                'coin_count': coin_count,
                                'total_balance': total_balance,
                                'coin_type': balance_item.coin_type,
                            })
                            break

                # 情況B：GetCoins 對象，具備 data 屬性
                elif hasattr(balance_data, 'data') and balance_data.data:
                    for coin in balance_data.data:
                        bal = int(getattr(coin, 'balance', 0))
                        total_balance += bal
                        sui_objects.append({
                            'object_id': getattr(coin, 'coin_object_id', ''),
                            'balance': bal,
                            'version': getattr(coin, 'version', ''),
                            'digest': getattr(coin, 'digest', ''),
                            'coin_type': getattr(coin, 'coin_type', '0x2::sui::SUI'),
                        })

                # 若上述均未獲取到，回退到字典路徑解析
                else:
                    data = self._handle_result(result, "账户余额查询(gRPC)")
                    if isinstance(data, dict) and 'items' in data:
                        for item in data.get('items', []):
                            if item.get('coin_type') == '0x2::sui::SUI':
                                total_balance = int(item.get('total_balance', 0))
                                sui_objects.append({
                                    'coin_count': int(item.get('coin_object_count', 0)),
                                    'total_balance': total_balance,
                                    'coin_type': item.get('coin_type'),
                                })
                                break
                    elif isinstance(data, dict) and 'data' in data:
                        for coin in data.get('data', []):
                            bal = int(coin.get('balance', 0))
                            total_balance += bal
                            sui_objects.append({
                                'object_id': coin.get('coin_object_id') or coin.get('objectId') or '',
                                'balance': bal,
                                'version': coin.get('version', ''),
                                'digest': coin.get('digest', ''),
                                'coin_type': coin.get('coin_type', '0x2::sui::SUI'),
                            })

                return {
                    'total_balance_mists': total_balance,
                    'total_balance_sui': total_balance / 1_000_000_000,
                    'sui_objects': sui_objects,
                    'active_address': str(self.active_address),
                }

            # 非標準返回，走通用處理
            data = self._handle_result(result, "账户余额查询(gRPC)")
            total_balance = 0
            sui_objects: List[Dict[str, Any]] = []
            if isinstance(data, dict) and 'items' in data:
                for item in data.get('items', []):
                    if item.get('coin_type') == '0x2::sui::SUI':
                        total_balance = int(item.get('total_balance', 0))
                        sui_objects.append({
                            'coin_count': int(item.get('coin_object_count', 0)),
                            'total_balance': total_balance,
                            'coin_type': item.get('coin_type'),
                        })
                        break
            elif isinstance(data, dict) and 'data' in data:
                for coin in data.get('data', []):
                    bal = int(coin.get('balance', 0))
                    total_balance += bal
                    sui_objects.append({
                        'object_id': coin.get('coin_object_id') or coin.get('objectId') or '',
                        'balance': bal,
                        'version': coin.get('version', ''),
                        'digest': coin.get('digest', ''),
                        'coin_type': coin.get('coin_type', '0x2::sui::SUI'),
                    })

            return {
                'total_balance_mists': total_balance,
                'total_balance_sui': total_balance / 1_000_000_000,
                'sui_objects': sui_objects,
                'active_address': str(self.active_address),
            }
        except Exception as e:
            logger.error(f"gRPC 获取账户余额失败: {e}")
            return {
                'total_balance_mists': 0,
                'total_balance_sui': 0.0,
                'sui_objects': [],
                'active_address': str(self.active_address),
                'error': str(e)
            }

    def deploy_contract(self, package_path: str, gas_budget: Optional[int] = None,
                        build_args: Optional[List[str]] = None) -> Dict[str, Any]:
        """通过 gRPC 部署 Move 包。"""
        try:
            from pathlib import Path
            pkg = Path(package_path)
            if not pkg.exists():
                raise FileNotFoundError(f"包路径不存在: {package_path}")
            if not (pkg / 'Move.toml').exists():
                raise FileNotFoundError(f"在 {package_path} 中未找到 Move.toml")

            # 使用 SuiTransaction（pysui 统一抽象，gRPC 后端执行）
            from pysui.sui.sui_txn.sync_transaction import SuiTransaction
            txn = SuiTransaction(client=self._client, initial_sender=self.active_address)

            upgrade_cap = txn.publish(project_path=str(pkg), args_list=build_args or [])
            txn.transfer_objects(transfers=[upgrade_cap], recipient=self.active_address)

            # 可选：检查成本
            try:
                _ = txn.inspect_for_cost()
            except Exception:
                pass

            res = txn.execute()
            deploy_data = self._handle_result(res, "合约部署(gRPC)")

            package_id = None
            upgrade_cap_id = None
            for ch in deploy_data.get('objectChanges', []) if isinstance(deploy_data, dict) else []:
                if ch.get('type') == 'published':
                    package_id = ch.get('packageId')
                elif ch.get('type') == 'created' and '::package::UpgradeCap' in ch.get('objectType', ''):
                    upgrade_cap_id = ch.get('objectId')

            return {
                'package_id': package_id,
                'upgrade_cap_id': upgrade_cap_id,
                'transaction_hash': deploy_data.get('digest') if isinstance(deploy_data, dict) else None,
                'gas_used': (deploy_data.get('effects', {}) if isinstance(deploy_data, dict) else {}).get('gasUsed'),
                'status': (deploy_data.get('effects', {}) if isinstance(deploy_data, dict) else {}).get('status'),
                'full_result': deploy_data,
            }
        except Exception as e:
            logger.error(f"gRPC 合约部署失败: {e}")
            raise

    def call_contract_function(self, package_id: str, module_name: str, function_name: str,
                               arguments: Optional[List[Any]] = None,
                               type_arguments: Optional[List[str]] = None,
                               gas_budget: Optional[int] = None) -> Dict[str, Any]:
        """通过 gRPC 调用合约函数。"""
        try:
            from pysui.sui.sui_txn.sync_transaction import SuiTransaction
            from pysui import ObjectID
            from pysui.sui.sui_types.scalars import SuiU64, SuiString

            txn = SuiTransaction(client=self._client, initial_sender=self.active_address)
            target = f"{package_id}::{module_name}::{function_name}"

            processed_args: List[Any] = []
            if arguments:
                for arg in arguments:
                    if isinstance(arg, str) and arg.startswith('0x') and len(arg) >= 3:
                        # 尝试作为 ObjectID
                        try:
                            processed_args.append(ObjectID(arg))
                            continue
                        except Exception:
                            pass
                        processed_args.append(SuiString(arg))
                    elif isinstance(arg, bytes):
                        processed_args.append(list(arg))
                    elif isinstance(arg, int):
                        processed_args.append(SuiU64(arg))
                    elif isinstance(arg, bool):
                        processed_args.append(arg)
                    else:
                        processed_args.append(arg)

            _ = txn.move_call(target=target, arguments=processed_args, type_arguments=type_arguments or [])

            try:
                _ = txn.inspect_for_cost()
            except Exception:
                pass

            res = txn.execute()
            call_data = self._handle_result(res, "合约函数调用(gRPC)")

            return {
                'transaction_hash': call_data.get('digest') if isinstance(call_data, dict) else None,
                'gas_used': (call_data.get('effects', {}) if isinstance(call_data, dict) else {}).get('gasUsed'),
                'status': (call_data.get('effects', {}) if isinstance(call_data, dict) else {}).get('status'),
                'events': call_data.get('events', []) if isinstance(call_data, dict) else [],
                'object_changes': call_data.get('objectChanges', []) if isinstance(call_data, dict) else [],
                'full_result': call_data,
            }
        except Exception as e:
            logger.error(f"gRPC 合约函数调用失败: {e}")
            raise

    def get_object_info(self, object_id: str) -> Dict[str, Any]:
        """通过 gRPC 查询对象信息。"""
        try:
            import pysui.sui.sui_builders.get_builders as get_builders
            from pysui import ObjectID

            if hasattr(get_builders, 'GetObject'):
                builder = get_builders.GetObject(
                    object_id=ObjectID(object_id),
                    options={"showType": True, "showContent": True, "showOwner": True},
                )
                res = self._client.execute(builder)
                return self._handle_result(res, f"获取对象信息(gRPC) {object_id}")

            raise RuntimeError("pysui 不支持 GetObject builder (gRPC)")
        except Exception as e:
            logger.error(f"gRPC 获取对象信息失败: {e}")
            return {'object_id': object_id, 'error': str(e)}

    def get_transaction_info(self, tx_hash: str) -> Dict[str, Any]:
        """通过 gRPC 查询交易信息。"""
        try:
            import pysui.sui.sui_builders.get_builders as get_builders

            if hasattr(get_builders, 'GetTx'):
                builder = get_builders.GetTx(
                    digest=tx_hash,
                    options={
                        "showInput": True,
                        "showEffects": True,
                        "showEvents": True,
                        "showObjectChanges": True,
                    },
                )
                res = self._client.execute(builder)
                return self._handle_result(res, f"获取交易信息(gRPC) {tx_hash}")

            if hasattr(get_builders, 'GetMultipleTx'):
                builder = get_builders.GetMultipleTx(
                    digests=[tx_hash],
                    options={
                        "showInput": True,
                        "showEffects": True,
                        "showEvents": True,
                        "showObjectChanges": True,
                    },
                )
                res = self._client.execute(builder)
                data = self._handle_result(res, f"获取交易信息(gRPC) {tx_hash}")
                if isinstance(data, list) and data:
                    return data[0]
                return data

            raise RuntimeError("pysui 不支持交易查询 builder (gRPC)")
        except Exception as e:
            logger.error(f"gRPC 获取交易信息失败: {e}")
            return {'transaction_hash': tx_hash, 'error': str(e)}


def main():
    try:
        logger.info("=== Sui gRPC 客户端演示 ===")
        client = SuiGrpcClient()

        logger.info("\n=== 查询账户余额 (gRPC) ===")
        balance = client.get_account_balance()
        print(f"活跃地址: {balance['active_address']}")
        print(f"总余额: {balance['total_balance_sui']:.6f} SUI")
        print(f"SUI对象数量: {len(balance['sui_objects'])}")

        logger.info("\n=== 演示完成 ===")
    except Exception as e:
        logger.error(f"gRPC 演示过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 