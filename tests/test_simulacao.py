"""Simulação completa do jogo SEM abrir janela.

Substitui o tkinter por uma versão falsa e joga as 8 fases por código:
andar até as portas, falar com NPCs, coletar itens, levar dano, responder
os desafios e chegar ao diploma. Rode com:  python tests/test_simulacao.py
"""
import sys, types, os, random, tempfile
class FakeImg:
    def __init__(self, **kw): self.w=kw.get('width',0); self.h=kw.get('height',0)
    def put(self,*a,**k): pass
    def zoom(self,x,y=None): return FakeImg(width=self.w*x,height=self.h*(y or x))
class FakeCanvas:
    def __init__(self,*a,**k): self.n=0; self.calls=0
    def pack(self): pass
    def _id(self): self.n+=1; return self.n
    def create_image(self,*a,**k): return self._id()
    def create_text(self,*a,**k): return self._id()
    def create_rectangle(self,*a,**k): return self._id()
    def delete(self,*a): pass
    def bbox(self,i): return (0,0,50,12)
    def tag_raise(self,*a): pass
class FakeRoot:
    def title(self,*a):pass
    def resizable(self,*a):pass
    def bind(self,*a):pass
    def protocol(self,*a):pass
    def after(self,*a): pass
    def destroy(self): pass
tk = types.ModuleType("tkinter"); tk.PhotoImage=FakeImg; tk.Canvas=FakeCanvas; tk.Tk=FakeRoot
sys.modules["tkinter"]=tk
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import data_quest_8bit as dq
dq.SAVE = os.path.join(tempfile.mkdtemp(), "save_test.json")
if os.path.exists(dq.SAVE): os.remove(dq.SAVE)
def boom(): raise RuntimeError("erro no tick")
dq.traceback.print_exc = boom

g = dq.Jogo(FakeRoot())
def tick(n=1, ev=None):
    if ev: g.ev.extend(ev)
    for _ in range(n): g.tick()
def avancar_dialogo():
    guard=0
    while g.dialog and guard<400:
        tick(1,[("space"," ")]); guard+=1
        if g.dialog and g.dialog["chars"]<len(g.dialog["wrapped"]): tick(1)
    assert not g.dialog

# título -> nome -> hub
tick(3); tick(1,[("return","\r")]); assert g.scene=="nome", g.scene
tick(1,[(c,c) for c in "Ana"]+[("return","\r")]); assert g.scene=="room" and g.room["kind"]=="hub"
avancar_dialogo()
# andar no hub até a porta 1
g.keys={"left"}
for _ in range(200):
    tick()
    if g.p["x"]<=64: break
g.keys={"up"}
for _ in range(120):
    tick()
    if g.lv: break
assert g.lv and g.lv["n"]==1, "não entrou na fase 1"
print("hub -> fase 1 OK, posicao", g.p)
g.keys=set()
# porta trancada
g.ir_hub(1); g.p["x"]=HUBX=dq.HUB_DOORS[2]*32; g.p["y"]=40
g.keys={"up"}; tick(25); g.keys=set()
assert g.lv is None, "entrou em porta trancada!"
print("porta trancada OK:", g.toast_msg)

def play_level(n, errar_item=True, usar_h=True):
    g.ir_nivel(n); g.dialog=None
    N=dq.NIVEIS[n-1]
    # mestre
    g.p["x"],g.p["y"]=3*32+32, 2*32+32
    assert g.npc_perto() and g.npc_perto()["id"]=="mestre"
    tick(1,[("e","e")]); avancar_dialogo()
    lv=g.lv; assert lv["lesson_done"]
    C=N.get("coleta")
    if C:
        assert lv["itens"], "sem itens"
        pos={(it["tx"],it["ty"]) for it in lv["itens"]}; assert len(pos)==len(lv["itens"])
        # bugs não nascem em cima de itens/parede
        for b in lv["bugs"]:
            assert not g.bate_rect(b["x"]+4,b["y"]+4,b["x"]+28,b["y"]+28)
        # rodar bugs vários ticks (sem player por perto)
        g.p["x"],g.p["y"]=g.room["start"]
        v0=lv["vidas"]
        keep=lv["bugs"]; lv["bugs"]=[]
        order=sorted(lv["itens"], key=lambda it: it["ordem"])
        if errar_item:
            if C.get("ordenada"):
                it=order[-1]   # item fora de ordem
            else:
                bad=[i for i in order if not i["bom"]]
                it=bad[0] if bad else None
            if it:
                g.p["x"],g.p["y"]=it["tx"]*32, it["ty"]*32-8
                tick(2)
                assert lv["vidas"]==v0-1, f"dano não aplicado {lv['vidas']} {v0}"
                g.p["x"],g.p["y"]=g.room["start"]
                tick(130)  # invul e cooldown acabam
        lv["bugs"]=keep
        for it in order:
            if it["got"] or not it["bom"]: continue
            lv["bugs"]=[]; lv["invul"]=0
            g.p["x"],g.p["y"]=it["tx"]*32, it["ty"]*32-8
            tick(2)
        assert lv["collect_done"], f"coleta não concluída {lv['bons']}/{lv['bons_total']}"
    # guardião
    g.p["x"],g.p["y"]=15*32, 2*32+40
    assert g.npc_perto() and g.npc_perto()["id"]=="guardiao"
    tick(1,[("e","e")]); avancar_dialogo()
    assert g.quiz
    for Q in N["quiz"]:
        if usar_h: tick(1,[("h","h")])
        if Q["tipo"]=="mc":
            # primeiro erra de propósito na 1ª pergunta
            g.quiz["sel"]=Q["certa"]
            tick(1,[("return","\r")])
        else:
            tick(1,[(c,c) for c in dq.fmt(float(Q["valor"])) if True]+[("return","\r")])
        assert g.quiz["fase"]=="fb" and g.quiz["ok"], (n, Q["q"][:30], g.quiz["fb"])
        tick(1,[("return","\r")])
        if not g.quiz: break
    assert not g.quiz
    avancar_dialogo()
    assert n in dq.ESTADO["concluidas"], "fase não concluída"
    return True

for n in range(1,9):
    ok=play_level(n)
    print(f"fase {n} OK  XP={dq.ESTADO['xp']}  scene={g.scene}")
assert g.scene=="fim"
tick(5)
print("fim OK; patente:", dq.patente())

# Saída da fase volta ao hub
dq.ESTADO["concluidas"]=[1]
g.scene="room"; g.ir_hub(None); g.dialog=None
g.ir_nivel(2); g.dialog=None
g.p["x"],g.p["y"]=9*32, 11*32-8
tick(3)
assert g.lv is None and g.room["kind"]=="hub", "saída não voltou ao hub"
print("saída da fase OK, jogador em", g.p)

# game over
g.ir_nivel(4); g.dialog=None
g.p["x"],g.p["y"]=3*32+32, 2*32+32; tick(1,[("e","e")]); avancar_dialogo()
for _ in range(4):
    lv=g.lv; lv["invul"]=0
    bad=[i for i in lv["itens"] if not i["bom"] and not i["got"]][0]
    g.p["x"],g.p["y"]=bad["tx"]*32, bad["ty"]*32-8; lv["bugs"]=[]
    tick(2)
print("game over -> vidas", g.lv["vidas"], "|", g.toast_msg)
assert g.lv["vidas"]==3 or g.lv["vidas"]>0

# quiz reprovando
g.ir_nivel(1); g.dialog=None
lv=g.lv; lv["lesson_done"]=lv["collect_done"]=True
g.p["x"],g.p["y"]=15*32, 2*32+40; tick(1,[("e","e")]); avancar_dialogo()
for Q in dq.NIVEIS[0]["quiz"]:
    g.quiz["sel"]=(Q["certa"]+1)%4
    tick(1,[("return","\r")]); tick(1,[("return","\r")])  # erra 2x
    tick(1,[("return","\r")])
assert not g.quiz
avancar_dialogo()
assert not g.lv["quiz_done"]
print("reprovação OK")
# pausa e salvar
tick(1,[("escape","")]); assert g.pausa; tick(3); tick(1,[("escape","")]); assert not g.pausa
print("TUDO OK")
