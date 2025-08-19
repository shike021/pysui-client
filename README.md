# 🌊 Sui区块链客户端程序

基于pysui库开发的Sui智能合约客户端，**专门使用JSON-RPC接口**进行区块链交互。

## 🎯 **项目特性**

✅ **100% JSON-RPC接口** - 完全基于JSON-RPC，不使用GraphQL  
✅ **智能合约部署** - 支持Move合约编译和部署到Sui网络  
✅ **合约函数调用** - 支持所有类型的合约函数调用  
✅ **账户管理** - 余额查询、对象查询、交易查询  
✅ **生产级代码** - 企业级错误处理和日志记录  
✅ **友好界面** - 交互式菜单和详细帮助信息  

## 📋 **文件结构**

```
sui-client/
├── sui_client.py              # 核心客户端类
├── quick_start.py            # 交互式菜单程序
├── test_client.py           # 基础功能测试
├── usage_example.py         # 使用示例
├── 功能演示.py              # 功能演示脚本
├── example_contract/        # 示例Move智能合约
│   ├── Move.toml           # 合约配置文件
│   └── sources/
│       └── hello_world.move # Hello World合约源码
└── README.md               # 项目文档
```

## 🚀 **快速开始**

### 1️⃣ **环境要求**

- Python 3.8+
- 已安装pysui库: `pip install pysui`
- 已配置Sui CLI (可选，用于密钥管理)
- 网络连接到Sui testnet

### 2️⃣ **安装使用**

```bash
# 进入项目目录
cd /home/ars/Eric/code/code/pysui-client

# 运行交互式程序
python quick_start.py

# 或运行基础测试
python test_client.py

# 或查看完整示例
python usage_example.py
```

### 3️⃣ **程序化使用**

```python
from sui_client import SuiContractClient

# 初始化客户端
client = SuiContractClient()

# 查询账户余额
balance = client.get_account_balance()
print(f"余额: {balance['total_balance_sui']:.6f} SUI")

# 部署智能合约
result = client.deploy_contract('./example_contract')
package_id = result['package_id']
print(f"合约已部署: {package_id}")

# 调用合约函数
result = client.call_contract_function(
    package_id=package_id,
    module_name='hello_world',
    function_name='create_greeting',
    arguments=[b'Hello from pysui!']
)
print(f"调用成功: {result['transaction_hash']}")
```

## 📚 **API参考**

### **SuiContractClient 类**

#### **初始化**
```python
client = SuiContractClient()
```

#### **余额查询**
```python
balance_info = client.get_account_balance()
# 返回: {'total_balance_sui': float, 'total_balance_mists': int, ...}
```

#### **合约部署**
```python
result = client.deploy_contract(
    package_path="./contract_directory",
    gas_budget=None,  # 可选，自动估算
    build_args=None   # 可选，构建参数
)
# 返回: {'package_id': str, 'upgrade_cap_id': str, 'transaction_hash': str, ...}
```

#### **合约调用**
```python
result = client.call_contract_function(
    package_id="0x...",
    module_name="contract_module",
    function_name="function_name",
    arguments=[arg1, arg2, ...],      # 可选
    type_arguments=["Type1", ...],    # 可选，泛型参数
    gas_budget=None                   # 可选，自动估算
)
# 返回: {'transaction_hash': str, 'status': dict, 'gas_used': dict, ...}
```

#### **对象查询**
```python
object_info = client.get_object_info("0x...")
# 返回: 对象的详细信息
```

#### **交易查询**
```python
tx_info = client.get_transaction_info("transaction_hash")
# 返回: 交易的详细信息
```

## 🧪 **示例智能合约**

项目包含一个完整的Hello World智能合约示例：

### **合约功能**
- `create_greeting(message)` - 创建问候消息
- `update_greeting(greeting, new_message)` - 更新问候消息
- `create_counter()` - 创建计数器
- `increment_counter(counter)` - 增加计数器
- `set_counter(counter, value)` - 设置计数器值
- `get_greeting_message(greeting)` - 获取问候消息内容
- `get_counter_value(counter)` - 获取计数器值
- `destroy_greeting(greeting)` - 销毁问候消息

### **合约结构**
```move
module hello_world::hello_world {
    // 问候消息对象
    struct GreetingMessage has key, store {
        id: UID,
        message: String,
        sender: address,
    }

    // 计数器对象
    struct Counter has key {
        id: UID,
        value: u64,
    }

    // 问候和计数事件
    struct GreetingEvent has copy, drop { ... }
    struct CountEvent has copy, drop { ... }
}
```

## 🔧 **技术实现细节**

### **JSON-RPC确认**

本项目**100%使用JSON-RPC接口**，技术证明：

1. **导入模块**: 使用`pysui.sui.sui_clients.sync_client.SuiClient`
2. **事务创建**: 使用`pysui.sui.sui_txn.sync_transaction.SuiTransaction`
3. **Builders**: 使用`pysui.sui.sui_builders.get_builders`中的JSON-RPC builders
4. **网络请求**: 所有请求发送到`https://fullnode.testnet.sui.io` (JSON-RPC端点)

### **Deprecation警告处理**

虽然pysui官方推荐GraphQL，但我们故意选择JSON-RPC因为：
- JSON-RPC是更通用和标准化的API调用方式
- 更容易与其他系统集成
- 调试和理解更简单
- 符合项目的技术需求

代码中已添加警告抑制：
```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pysui.*")
```

### **参数类型处理**

智能合约函数调用支持多种参数类型：

```python
# 字符串参数
arguments=["hello"]

# 字节数组参数 (vector<u8>)
arguments=[b"hello"]

# 整数参数
arguments=[42]

# 对象ID参数
arguments=["0x1234..."]

# 混合参数
arguments=[b"message", 123, "0x1234..."]
```

## ⚡ **已解决的技术问题**

### **余额查询修复**

**问题**: `sui client gas`显示2.00 SUI，但程序查询显示0 SUI

**解决方案**: 
- 修复了数据解析逻辑，直接使用`result.result_data`
- 正确访问pysui对象属性（`balance_data.items`而不是`balance_info['items']`）
- 添加了多个builder的兼容性支持

### **合约部署修复**

**问题**: `AttributeError: 'SuiClient' object has no attribute 'transaction'`

**解决方案**:
- 使用正确的`SuiTransaction`类而不是`client.transaction()`
- 修复Move合约语法（移除`public struct`）
- 修复Move.toml配置文件
- 修复参数编码（bytes转换为list[int]）

### **技术修复详情**

```python
# 修复前（错误）
txn = self.client.transaction(initial_sender=self.active_address)

# 修复后（正确）
from pysui.sui.sui_txn.sync_transaction import SuiTransaction
txn = SuiTransaction(client=self.client, initial_sender=self.active_address)
```

## 🎯 **测试验证**

### **功能测试结果**

| 功能         | 状态   | 详情                       |
| ------------ | ------ | -------------------------- |
| 客户端初始化 | ✅ 成功 | 连接testnet成功            |
| 余额查询     | ✅ 成功 | 与`sui client gas`结果一致 |
| 合约编译     | ✅ 成功 | Move语法错误已修复         |
| 合约部署     | ✅ 成功 | 成功部署到testnet          |
| 合约调用     | ✅ 成功 | 所有函数调用正常           |
| 对象查询     | ✅ 成功 | 获取详细信息成功           |
| 交易查询     | ✅ 成功 | 获取交易详细信息           |

### **成功案例**

最近的成功部署：
- **Package ID**: `0xdd7e410845f1a3a4adfbafe30c4b52d93c603336a3b94e149df950f065c28729`
- **部署Transaction**: `B1QzJYk9mrKwvP2tUeQtfZxCf3e5PsXdEvNxJVcuAijY`
- **Gas消耗**: ~0.014 SUI

成功的合约调用：
- **create_greeting**: `9gE5QqA2EWEk9LDWcHg1RqwjvDEUdZ1wwWrKpTWM1WT3`
- **create_counter**: `C8Uudhc9jY2vzQTaqSNuqMtkuf3iyoz5Tji77vbs6PwJ`
- **increment_counter**: `2Bcbfswwta5ki2zEH7THy5A7veGaFfnjmm6mpqp2JdyL`

## 🔍 **故障排除**

### **常见问题**

1. **余额不足**
   ```bash
   # 获取测试币
   sui client faucet
   ```

2. **网络连接问题**
   ```bash
   # 检查网络配置
   sui client envs
   sui client switch --env testnet
   ```

3. **依赖问题**
   ```bash
   # 重新安装pysui
   pip uninstall pysui
   pip install pysui
   ```

### **调试模式**

启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 **贡献指南**

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 **许可证**

本项目使用与pysui相同的许可证。

## 🙏 **致谢**

- [pysui](https://github.com/FrankC01/pysui) - Sui Python SDK
- [Sui](https://sui.io/) - Sui区块链平台
- Move语言和Sui生态系统

---

**🎯 项目目标完成**: 创建了一个完全基于JSON-RPC的生产级Sui智能合约客户端，支持合约部署、调用和所有基础区块链操作。 