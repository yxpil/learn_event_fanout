"""Demo: one OrderCreated event fans out to 4 independent pipelines."""
from framework.eventbus import EventBus, Pipeline
from filters import pipeline_filters as F


def build_bus():
    bus = EventBus()

    notif = Pipeline("notification")
    notif.use(F.email_send).use(F.push_send)

    search = Pipeline("search_index")
    search.use(F.index_build).use(F.index_refresh)

    loyalty = Pipeline("loyalty")
    loyalty.use(F.points_add).use(F.level_check)

    inv = Pipeline("inventory")
    inv.use(F.stock_deduct).use(F.low_stock_alert)

    for p in (notif, search, loyalty, inv):
        bus.subscribe("OrderCreated", p)
    return bus


def show(title, results):
    print(f"\n--- {title} ---")
    for name, status, logs in results:
        print(f"  [{name}] {status}")
        for line in logs:
            print(f"      {line}")


def main():
    bus = build_bus()

    # Case 1: one event fans out to all 4 pipelines
    show("Case 1: publish OrderCreated -> 4 pipelines run independently",
         bus.publish("OrderCreated", {
             "order_id": "o_001", "user_id": "u_1", "amount": 200.0, "qty": 2,
         }))

    # Case 2: one pipeline fails (zero qty in inventory) -> others unaffected
    show("Case 2: inventory pipeline stops (zero qty), others still run",
         bus.publish("OrderCreated", {
             "order_id": "o_002", "user_id": "u_2", "amount": 50.0, "qty": 0,
         }))

    # Case 3: dynamically add a new subscriber (audit log) without touching others
    audit = Pipeline("audit_log")
    audit.use(lambda ctx: ctx.update(audited=f"order {ctx.get('order_id')} logged"))
    audit.filters[0].name = "write_audit"
    bus.subscribe("OrderCreated", audit)
    show("Case 3: new audit pipeline plugged in, now 5 pipelines fan out",
         bus.publish("OrderCreated", {
             "order_id": "o_003", "user_id": "u_3", "amount": 10.0, "qty": 1,
         }))

    print("\n== all cases done ==")


if __name__ == "__main__":
    main()
