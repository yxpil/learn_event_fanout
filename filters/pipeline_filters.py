"""Filters for the four radiating pipelines. Each pipeline is independent."""


# --- Pipeline: notification ---
def email_send(ctx):
    ctx["email_sent"] = f"mail to {ctx.get('user_id')} about order {ctx.get('order_id')}"
email_send.name = "email_send"


def push_send(ctx):
    ctx["push_sent"] = f"push to {ctx.get('user_id')}"
push_send.name = "push_send"


# --- Pipeline: search index ---
def index_build(ctx):
    ctx["indexed"] = f"search doc for order {ctx.get('order_id')}"
index_build.name = "index_build"


def index_refresh(ctx):
    ctx["refreshed"] = True
index_refresh.name = "index_refresh"


# --- Pipeline: loyalty points ---
def points_add(ctx):
    ctx["points"] = int(ctx.get("amount", 0) * 1)
points_add.name = "points_add"


def level_check(ctx):
    ctx["level_up_checked"] = True
level_check.name = "level_check"


# --- Pipeline: inventory ---
def stock_deduct(ctx):
    qty = ctx.get("qty", 0)
    if qty <= 0:
        from framework.eventbus import StopPipeline
        raise StopPipeline("zero qty")
    ctx["stock_deducted"] = qty
stock_deduct.name = "stock_deduct"


def low_stock_alert(ctx):
    ctx["alert_sent"] = ctx.get("stock_deducted", 0) <= 1
low_stock_alert.name = "low_stock_alert"
