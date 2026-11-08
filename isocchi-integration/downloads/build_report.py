from pathlib import Path
import csv, html
from decimal import Decimal, InvalidOperation
from datetime import date

ROOT = Path(__file__).resolve().parent

def aggregate(path):
    products, days, count, quantity = {}, {}, 0, 0
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ['date', 'product', 'quantity', 'unit_price']:
            raise ValueError('CSVの列は date,product,quantity,unit_price の順にしてください。')
        for line, row in enumerate(reader, 2):
            try:
                q = int(row['quantity'])
                p = Decimal(row['unit_price'])
                if q < 0 or not p.is_finite() or p < 0:
                    raise ValueError()
                product, day = row['product'].strip(), row['date'].strip()
                if not product or not day:
                    raise ValueError()
                day = date.fromisoformat(day).isoformat()
            except (ValueError, TypeError, InvalidOperation):
                raise ValueError(f'{line}行目の数値・商品名・日付を確認してください。') from None
            amount = q * p
            if product not in products:
                products[product] = [0, Decimal(0)]
            products[product][0] += q
            products[product][1] += amount
            days[day] = days.get(day, Decimal(0)) + amount
            quantity += q
            count += 1
    return products, days, count, quantity

def money(value):
    return f'¥{value:,.0f}' if value == value.to_integral_value() else f'¥{value:,.2f}'

def build():
    products, days, count, quantity = aggregate(ROOT / 'sales.csv')
    total = sum((v[1] for v in products.values()), Decimal(0))
    if days:
        first, last = date.fromisoformat(min(days)), date.fromisoformat(max(days))
        start = f'{first.year}年{first.month}月{first.day}日'
        end = f'{last.day}日' if (first.year,first.month)==(last.year,last.month) else f'{last.year}年{last.month}月{last.day}日'
        period = f'{start}〜{end}'
    else:
        period = '対象データなし'
    product_rows = ''.join(f'<tr><th scope="row">{html.escape(k)}</th><td>{v[0]}</td><td>{money(v[1])}</td></tr>' for k,v in sorted(products.items(), key=lambda x:(-x[1][1],x[0])))
    day_rows = ''.join(f'<tr><th scope="row">{html.escape(k)}</th><td>{money(v)}</td></tr>' for k,v in sorted(days.items()))
    bars = ''.join(f'<div class="bar-row"><b>{html.escape(k)}</b><div class="track"><i style="width:{float(v[1]/total*100) if total else 0:.2f}%"></i></div><span>{money(v[1])}</span></div>' for k,v in sorted(products.items(),key=lambda x:(-x[1][1],x[0])))
    page = f'''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>売上レポート｜練習CSV</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#071626;color:#edf4f7;font:16px/1.65 system-ui,'Yu Gothic',sans-serif}}main{{max-width:900px;margin:auto;padding:32px 22px}}h1{{font-size:clamp(26px,5vw,38px);margin:0 0 6px}}p{{margin:8px 0}}.eyebrow{{color:#f7be66;font-size:14px;letter-spacing:.06em}}.caption{{color:#b6c9d9;font-size:14px}}.metrics{{display:grid;grid-template-columns:2fr 1fr 1fr;gap:12px;margin:26px 0}}.metric{{background:#132b40;border-top:3px solid #4acbde;padding:16px;border-radius:4px}}.metric:first-child{{border-color:#ffb653}}.metric span{{color:#c6d5e0;font-size:14px}}.metric strong{{display:block;font-size:clamp(22px,4vw,36px);line-height:1.35;margin-top:7px}}section{{background:#102536;border:1px solid #274052;padding:22px;margin:20px 0;border-radius:8px}}h2{{margin:0 0 18px;font-size:21px}}table{{width:100%;border-collapse:collapse}}td,th{{padding:13px 8px;border-bottom:1px solid #314455;text-align:right}}th:first-child{{text-align:left}}thead{{color:#a7c4d6;font-size:14px}}tfoot{{color:#ffd18a;font-weight:bold}}.bar-row{{display:grid;grid-template-columns:80px 1fr 95px;gap:12px;align-items:center;margin:16px 0;font-size:15px}}.bar-row span{{text-align:right}}.track{{height:16px;background:#253b4d;border-radius:3px;overflow:hidden}}.track i{{display:block;height:100%;background:linear-gradient(90deg,#21a8c8,#70e3e9)}}.note{{border-left:3px solid #ffb653;padding-left:15px;color:#d1dee6;font-size:14px}}footer{{color:#93acbe;font-size:13px;margin-top:25px}}@media(max-width:480px){{main{{padding:22px 14px}}section{{padding:18px 14px}}.metrics{{gap:8px}}.metric{{padding:12px 9px}}.metric span{{font-size:12px}}.bar-row{{grid-template-columns:64px 1fr 83px;gap:7px;font-size:14px}}td,th{{padding:12px 5px}}}}
</style><main><p class="eyebrow">いそっち式 AI連携 実践スタートブック</p><h1>売上レポート</h1><p class="caption">元データ：sales.csv｜{period}</p><p class="caption">架空の練習CSVを独立集計した照合用見本。</p><div class="metrics"><div class="metric"><span>総売上</span><strong>{money(total)}</strong></div><div class="metric"><span>総数量</span><strong>{quantity}</strong></div><div class="metric"><span>入力行</span><strong>{count}</strong></div></div><section id="products"><h2>商品別売上</h2>{bars}<table><thead><tr><th>商品</th><th>数量</th><th>売上</th></tr></thead><tbody>{product_rows}</tbody><tfoot><tr><th>合計</th><td>{quantity}</td><td>{money(total)}</td></tr></tfoot></table></section><section id="daily"><h2>日別売上</h2><table><thead><tr><th>日付</th><th>売上</th></tr></thead><tbody>{day_rows}</tbody></table></section><p class="note">計算方法：各行の quantity × unit_price を足し合わせています。商品別は売上の降順、日別は日付の昇順です。</p><footer>この見本は今回の教材用に制作。本人の売上・過去の成果を示すものではありません。入力を変えたら同じフォルダで build_report.py を実行して再生成します。</footer></main></html>'''
    (ROOT / 'report.html').write_text(page,encoding='utf-8')
    print(f'report.html saved: total={total} JPY, quantity={quantity}, rows={count}')

if __name__ == '__main__':
    build()

