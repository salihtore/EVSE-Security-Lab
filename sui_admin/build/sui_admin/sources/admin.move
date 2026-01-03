module sui_admin::admin {
    use sui::transfer;
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};

    /// Admin yetkisini temsil eden struct.
    /// `key` yeteneği olduğu için bir Sui objesidir.
    /// `store` yeteneği olduğu için başka objelerin içinde saklanabilir veya transfer edilebilir.
    struct AdminCap has key, store {
        id: UID,
    }

    /// Modül init fonksiyonu, modül yayınlandığında bir kez çalışır.
    /// AdminCap objesini oluşturur ve yayınlayan kişiye (sender) gönderir.
    fun init(ctx: &mut TxContext) {
        let admin_cap = AdminCap {
            id: object::new(ctx),
        };
        
        transfer::transfer(admin_cap, tx_context::sender(ctx));
    }

    /// Yetkili bir admin'in yeni bir admin yetkisi oluşturup başka bir adrese vermesini sağlar.
    /// `_` parametresi, bu fonksiyonu çağırabilmek için çağıran kişinin bir AdminCap sahibi olması gerektiğini garanti eder.
    public entry fun create_admin(_: &AdminCap, recipient: address, ctx: &mut TxContext) {
        let new_admin_cap = AdminCap {
            id: object::new(ctx),
        };
        transfer::transfer(new_admin_cap, recipient);
    }

    /// Yeni bir AdminCap oluşturmak için test fonksiyonu.
    /// Sadece testlerde kullanılabilir.
    #[test_only]
    public fun create_admin_cap_for_testing(ctx: &mut TxContext): AdminCap {
        AdminCap {
            id: object::new(ctx),
        }
    }
}
