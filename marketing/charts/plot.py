import json, datetime as dt
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.dates as md
rows=sorted(json.load(open("last10.json")),key=lambda r:r["sent"])
short={111:"Contratos automáticos",104:"Vistoria em tribunal",103:"Fotos e documentos",102:"Transfers",101:"Motorista por viatura",100:"Pagamentos semanas ant.",95:"Dia da Mobilidade (Bolt)",94:"Comunicado oficial*",93:"Programação Dia Mob.",92:"GalgoSheets no Dia Mob."}
for r in rows:
    r["d"]=dt.datetime.fromisoformat(r["sent"]); r["o"]=100*r["opens"]/r["delivered"]; r["c"]=100*r["clicks"]/r["delivered"]
TXT="#0b0b0b"; SEC="#52514e"; SURF="#fcfcfb"; GRID="#e6e5e1"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"text.color":TXT,"axes.labelcolor":SEC,"xtick.color":SEC,"ytick.color":SEC})
fig,axs=plt.subplots(2,1,figsize=(13,9),sharex=True,facecolor=SURF)
for ax,key,col,title in [(axs[0],"o","#2a78d6","Taxa de abertura (%)"),(axs[1],"c","#eb6834","Taxa de cliques (%)")]:
    ax.set_facecolor(SURF)
    big=[r for r in rows if r["id"]!=94]
    ax.plot([rows.index(r) for r in big],[r[key] for r in big],color=col,lw=2,zorder=2)
    for r in rows:
        small=r["id"]==94
        ax.scatter(rows.index(r),r[key],s=70,facecolor=SURF if small else col,edgecolor=col,linewidth=2,zorder=3)
    ax.set_title(title,loc="left",fontsize=14,fontweight="bold",color=TXT,pad=10)
    ax.grid(axis="y",color=GRID,lw=1); ax.set_axisbelow(True)
    for s in ["top","right","left"]: ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID); ax.tick_params(length=0)
    ax.set_ylim(0, max(r[key] for r in rows)*1.3)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,_: f"{v:.0f}%" if key=="o" else f"{v:.1f}%"))
    for i,r in enumerate(rows):
        ax.annotate(f'{r[key]:.1f}%' if key=="o" else f'{r[key]:.2f}%',(i,r[key]),textcoords="offset points",xytext=(0,11),ha="center",fontsize=10,color=TXT)
axs[1].set_xticks(range(len(rows))); axs[1].set_xticklabels([r["d"].strftime("%d %b")+"\n"+"\n".join(__import__("textwrap").wrap(short[r["id"]],13)) for r in rows],fontsize=9.5); axs[1].set_xlim(-0.6,len(rows)-0.4)
fig.suptitle("Últimos 10 emails enviados (Brevo): abertura e cliques por ordem de envio",x=0.06,ha="left",fontsize=16,fontweight="bold")
fig.text(0.06,0.015,"Taxas sobre emails entregues (~7.600–7.800 por envio). *Comunicado oficial foi um envio pequeno (632), marcador vazio, fora da linha.\nAberturas incluem aberturas automáticas do Apple Mail. Dados Brevo, 24 Nov 2026.",fontsize=9.5,color=SEC)
fig.tight_layout(rect=(0.02,0.07,1,0.96))
fig.savefig("/home/user/videos/../emails-abertura-cliques.png",dpi=150,facecolor=SURF)
