import json, sys
OUT = sys.argv[1]
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1920px;height:1080px;font-family:'Noto Sans','DejaVu Sans',sans-serif;background:#eef3f8;color:#0b2545}
.brand{position:absolute;top:36px;right:48px;font-weight:800;font-size:34px;color:#0b2545;background:#fff;padding:12px 22px;border-radius:14px;box-shadow:0 4px 16px rgba(0,0,0,.08)}
.brand span{color:#1db954}
.tag{position:absolute;bottom:28px;right:48px;font-size:18px;color:#7a8ca5}
.win{position:absolute;left:120px;top:120px;width:1680px;height:840px;background:#fff;border-radius:18px;overflow:hidden;box-shadow:0 20px 60px rgba(11,37,69,.18);display:flex}
.side{width:560px;background:linear-gradient(160deg,#0a74c9,#0b8fe0);color:#fff;padding:70px 56px}
.side h1{font-weight:300;font-size:48px;line-height:1.15}.side h1 b{font-weight:800;display:block}
.side p{margin-top:36px;font-size:24px;opacity:.9}
.main{flex:1;padding:0}
.steps{display:flex;gap:0;padding:40px 60px;background:#f6f9fc;border-bottom:1px solid #e3ebf3}
.st{flex:1;text-align:center;color:#b8c7d8;font-size:22px}
.st i{display:inline-block;width:44px;height:44px;line-height:44px;border-radius:50%;background:#dbe6f1;color:#fff;font-style:normal;font-weight:700;margin-bottom:10px}
.st.on{color:#0a74c9}.st.on i{background:#0a74c9}
.q{padding:56px 60px 0;font-size:38px;font-weight:800}
.opts{padding:36px 60px;display:grid;grid-template-columns:1fr 1fr;gap:22px}
.o{border:2px solid #e3ebf3;background:#fafcfe;border-radius:12px;padding:28px 26px;font-size:26px;font-weight:600;display:flex;align-items:center;gap:18px}
.o i{width:28px;height:28px;border-radius:50%;border:2px solid #9fb2c8;flex:none}
.o.sel{border-color:#0a74c9;background:#eaf4fd}.o.sel i{border:9px solid #0a74c9}
.f{padding:10px 60px}.f label{display:block;font-size:20px;color:#5b6f87;margin:18px 0 8px}
.f div{border:2px solid #e3ebf3;border-radius:10px;padding:18px 20px;font-size:26px;min-height:66px}
.f div.fill{border-color:#0a74c9}
.btn{margin:30px 60px;display:inline-block;background:#0a74c9;color:#fff;font-size:26px;padding:20px 48px;border-radius:10px;font-weight:600}
.btn.hl{box-shadow:0 0 0 8px rgba(10,116,201,.25)}
.ok{padding:120px 60px;text-align:center}.ok b{display:inline-block;width:150px;height:150px;border-radius:50%;background:#1db954;color:#fff;font-size:96px;line-height:150px}
.ok h2{margin-top:36px;font-size:44px}.ok p{margin-top:16px;font-size:26px;color:#5b6f87}
.title{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(160deg,#0b2545,#0a74c9);color:#fff;text-align:center}
.title .logo{font-size:84px;font-weight:800}.title .logo span{color:#38e07b}
.title h1{margin-top:40px;font-size:64px;font-weight:800;max-width:1400px}.title p{margin-top:24px;font-size:34px;opacity:.85}
"""
STEPS = ["Início","Caracterização","Atividade","Validação"]
def steps(n): return '<div class="steps">'+''.join(f'<div class="st {"on" if i<n else ""}"><i>{i+1}</i><br>{s}</div>' for i,s in enumerate(STEPS))+'</div>'
def win(n, body): return f'''<div class="win"><div class="side"><h1>Declaração de<b>Início de Atividade</b></h1><p>Exemplo ilustrativo dos passos no Portal das Finanças.</p></div><div class="main">{steps(n)}{body}</div></div>'''
def page(inner, brand=True):
    b = '<div class="brand">Galgo<span>Sheets</span></div><div class="tag">Ilustração. Não é o portal oficial.</div>' if brand else ''
    return f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{inner}{b}</body></html>'
def opts(sel): 
    L=["Início de Atividade","Alteração de Atividade","Cessação de Atividade"]
    return '<div class="q">Qual o tipo de declaração que pretende entregar?</div><div class="opts">'+''.join(f'<div class="o {"sel" if x==sel else ""}"><i></i>{x}</div>' for x in L)+'</div>'
def fields(fill):
    F=[("NIF","123 456 789"),("Data de início","01/12/2026"),("Regime de IVA","Isenção (art. 53.º) ou regime normal")]
    return '<div class="q">Caracterização</div><div class="f">'+''.join(f'<label>{l}</label><div class="{"fill" if fill else ""}">{v if fill else ""}</div>' for l,v in F)+'</div>'
def act(sel):
    L=["Transporte de passageiros (TVDE)","Outra atividade"]
    return '<div class="q">Qual a atividade que vai exercer?</div><div class="opts">'+''.join(f'<div class="o {"sel" if (sel and i==0) else ""}"><i></i>{x}</div>' for i,x in enumerate(L))+'</div>'
frames = {
 "s1": page('<div class="title"><div class="logo">Galgo<span>Sheets</span></div><h1>Abrir atividade como motorista TVDE</h1><p>Passo a passo, em menos de um minuto</p></div>', brand=False),
 "s2a": page(win(1, opts(None))), "s2b": page(win(1, opts("Início de Atividade")+'<div class="btn hl">Avançar</div>')),
 "s3a": page(win(2, fields(False))), "s3b": page(win(2, fields(True))),
 "s4a": page(win(3, act(False))), "s4b": page(win(3, act(True)+'<div class="btn hl">Avançar</div>')),
 "s5a": page(win(4, '<div class="q">Validação</div><div class="f"><label>Resumo</label><div class="fill">Início de Atividade · TVDE · 01/12/2026</div></div><div class="btn hl">Submeter</div>')),
 "s5b": page(win(4, '<div class="ok"><b>✓</b><h2>Declaração submetida</h2><p>Já podes passar recibos verdes.</p></div>')),
 "s6": page('<div class="title"><div class="logo">Galgo<span>Sheets</span></div><h1>Dúvidas? Um contabilista ajuda-te na app.</h1><p>galgosheets.com</p></div>', brand=False),
}
for k,v in frames.items(): open(f"{OUT}/{k}.html","w").write(v)
print(len(frames))
