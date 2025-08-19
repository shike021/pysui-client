/// 一个简单的Hello World智能合约示例
/// 演示Sui Move的基本功能
module hello_world::hello_world {
    use sui::object::{Self, UID};
    use sui::transfer;
    use sui::tx_context::{Self, TxContext};
    use std::string::{Self, String};
    use sui::event;

    /// 错误代码
    const EInvalidMessage: u64 = 1;

    /// 问候消息对象
    struct GreetingMessage has key, store {
        id: UID,
        message: String,
        sender: address,
    }

    /// 计数器对象
    struct Counter has key {
        id: UID,
        value: u64,
    }

    /// 问候事件
    struct GreetingEvent has copy, drop {
        message: String,
        sender: address,
    }

    /// 计数事件
    struct CountEvent has copy, drop {
        old_value: u64,
        new_value: u64,
    }

    /// 创建一个新的问候消息
    public entry fun create_greeting(message: vector<u8>, ctx: &mut TxContext) {
        let message_str = string::utf8(message);
        
        // 验证消息不为空
        assert!(!string::is_empty(&message_str), EInvalidMessage);
        
        let sender = tx_context::sender(ctx);
        
        let greeting = GreetingMessage {
            id: object::new(ctx),
            message: message_str,
            sender,
        };

        // 发出事件
        event::emit(GreetingEvent {
            message: message_str,
            sender,
        });

        // 转移给发送者
        transfer::public_transfer(greeting, sender);
    }

    /// 更新问候消息
    public entry fun update_greeting(greeting: &mut GreetingMessage, new_message: vector<u8>, ctx: &mut TxContext) {
        let new_message_str = string::utf8(new_message);
        assert!(!string::is_empty(&new_message_str), EInvalidMessage);
        
        greeting.message = new_message_str;
        
        event::emit(GreetingEvent {
            message: new_message_str,
            sender: tx_context::sender(ctx),
        });
    }

    /// 创建一个新的计数器
    public entry fun create_counter(ctx: &mut TxContext) {
        let counter = Counter {
            id: object::new(ctx),
            value: 0,
        };

        transfer::share_object(counter);
    }

    /// 增加计数器
    public entry fun increment_counter(counter: &mut Counter, _ctx: &mut TxContext) {
        let old_value = counter.value;
        counter.value = old_value + 1;
        
        event::emit(CountEvent {
            old_value,
            new_value: counter.value,
        });
    }

    /// 设置计数器值
    public entry fun set_counter(counter: &mut Counter, new_value: u64, _ctx: &mut TxContext) {
        let old_value = counter.value;
        counter.value = new_value;
        
        event::emit(CountEvent {
            old_value,
            new_value,
        });
    }

    /// 获取问候消息内容（只读函数）
    public fun get_greeting_message(greeting: &GreetingMessage): String {
        greeting.message
    }

    /// 获取问候消息发送者（只读函数）
    public fun get_greeting_sender(greeting: &GreetingMessage): address {
        greeting.sender
    }

    /// 获取计数器值（只读函数）
    public fun get_counter_value(counter: &Counter): u64 {
        counter.value
    }

    /// 销毁问候消息
    public entry fun destroy_greeting(greeting: GreetingMessage, _ctx: &mut TxContext) {
        let GreetingMessage { id, message: _, sender: _ } = greeting;
        object::delete(id);
    }
} 