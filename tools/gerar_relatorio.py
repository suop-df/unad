import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, PageBreak, HRFlowable, KeepTogether)
from reportlab.lib.colors import HexColor
import os

# ── DADOS ─────────────────────────────────────────────
df_all = pd.read_excel(r'E:\empenho\exportar.xlsx', engine='openpyxl')
for col in ['NOUG', 'NUNE', 'NOEVENTO', 'DALANCAMENTO']:
    df_all[col] = df_all[col].str.strip()
df_all['VADOCUMENTO'] = df_all['VADOCUMENTO'].round(2)
df_all['FONTE_GRUPO'] = df_all['COFONTE'].apply(lambda x: str(x)[:4])
df_all['MES'] = pd.to_datetime(df_all['DALANCAMENTO'], dayfirst=True).dt.month.astype(int)
df = df_all[df_all['MES'] == 4].copy()

GND_NOME = {
    1: 'Pessoal e Encargos Sociais',
    2: 'Juros e Encargos da Dívida',
    3: 'Outras Despesas Correntes',
    4: 'Investimentos',
    5: 'Inversões Financeiras',
    6: 'Amortização da Dívida',
}

ORGAO = 'Subsecretaria de Orçamento Público SUOP/SEFIN/SEEC'

# ── CORES ─────────────────────────────────────────────
AZUL_ESCURO   = HexColor('#1a3a5c')
AZUL_MEDIO    = HexColor('#2563a8')
AZUL_CLARO    = HexColor('#dbeafe')
VERDE         = HexColor('#16a34a')
CINZA_CLARO   = HexColor('#f1f5f9')
CINZA_BORDA   = HexColor('#cbd5e1')
BRANCO        = colors.white
TEXTO_ESC     = HexColor('#1e293b')

W, H = A4
CONTENT_W = W - 4*cm   # 17 cm

# ── FORMATADORES ──────────────────────────────────────
def fv(v):
    """Valor abreviado para cards (nunca quebra linha)."""
    if v >= 1e9:
        return f"R$ {v/1e9:.2f} Bi".replace('.', ',')
    if v >= 1e6:
        return f"R$ {v/1e6:.2f} Mi".replace('.', ',')
    if v >= 1e3:
        return f"R$ {v/1e3:.2f} Mil".replace('.', ',')
    return f"R$ {v:.2f}".replace('.', ',')

def fmt_val(v):
    return f"R$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def fmt_n(n):
    return f"{n:,}".replace(',', '.')

# ── ESTILOS ───────────────────────────────────────────
def estilos():
    titulo_capa = ParagraphStyle('TituloCapa',
        fontName='Helvetica-Bold', fontSize=22, leading=28,
        alignment=TA_CENTER, textColor=BRANCO)
    subtit_capa = ParagraphStyle('SubtitCapa',
        fontName='Helvetica', fontSize=13, leading=18,
        alignment=TA_CENTER, textColor=HexColor('#bfdbfe'))
    meta_capa = ParagraphStyle('MetaCapa',
        fontName='Helvetica', fontSize=10, leading=14,
        alignment=TA_CENTER, textColor=HexColor('#93c5fd'))
    cap_sec = ParagraphStyle('CapSec',
        fontName='Helvetica-Bold', fontSize=13, leading=16,
        textColor=BRANCO, alignment=TA_LEFT)
    titulo_sec = ParagraphStyle('TituloSec',
        fontName='Helvetica-Bold', fontSize=14, leading=18,
        textColor=AZUL_ESCURO, spaceBefore=10, spaceAfter=4)
    subtitulo = ParagraphStyle('Subtitulo',
        fontName='Helvetica-Bold', fontSize=11, leading=14,
        textColor=AZUL_MEDIO, spaceBefore=8, spaceAfter=4)
    corpo = ParagraphStyle('Corpo',
        fontName='Helvetica', fontSize=9.5, leading=14,
        alignment=TA_JUSTIFY, spaceAfter=6, textColor=TEXTO_ESC)
    numero_card = ParagraphStyle('NumCard',
        fontName='Helvetica-Bold', fontSize=15, leading=18,
        alignment=TA_CENTER, textColor=AZUL_ESCURO)
    label_card = ParagraphStyle('LabelCard',
        fontName='Helvetica', fontSize=7.5, leading=10,
        alignment=TA_CENTER, textColor=HexColor('#64748b'))
    nota = ParagraphStyle('Nota',
        fontName='Helvetica', fontSize=8.5, leading=12,
        textColor=HexColor('#475569'), alignment=TA_JUSTIFY)

    return dict(titulo_capa=titulo_capa, subtit_capa=subtit_capa,
                meta_capa=meta_capa, cap_sec=cap_sec,
                titulo_sec=titulo_sec, subtitulo=subtitulo,
                corpo=corpo, numero_card=numero_card,
                label_card=label_card, nota=nota)

ST = estilos()

# ── HELPERS ───────────────────────────────────────────
def hr(color=AZUL_MEDIO, thickness=0.8, spaceBefore=4, spaceAfter=6):
    return HRFlowable(width='100%', thickness=thickness, color=color,
                      spaceBefore=spaceBefore, spaceAfter=spaceAfter)

def header_secao(texto, cor=AZUL_ESCURO):
    t = Table([[Paragraph(texto, ST['cap_sec'])]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), cor),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING',   (0,0), (-1,-1), 14),
        ('RIGHTPADDING',  (0,0), (-1,-1), 14),
    ]))
    return t

def tabela_dados(cabecalho, linhas, col_widths, alt_color=CINZA_CLARO):
    t = Table([cabecalho] + linhas, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),  (-1,0),  AZUL_MEDIO),
        ('TEXTCOLOR',     (0,0),  (-1,0),  BRANCO),
        ('FONTNAME',      (0,0),  (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0),  (-1,-1), 8),
        ('FONTNAME',      (0,1),  (-1,-1), 'Helvetica'),
        ('ROWBACKGROUNDS',(0,1),  (-1,-1), [BRANCO, alt_color]),
        ('GRID',          (0,0),  (-1,-1), 0.4, CINZA_BORDA),
        ('TOPPADDING',    (0,0),  (-1,-1), 4),
        ('BOTTOMPADDING', (0,0),  (-1,-1), 4),
        ('LEFTPADDING',   (0,0),  (-1,-1), 6),
        ('RIGHTPADDING',  (0,0),  (-1,-1), 6),
        ('VALIGN',        (0,0),  (-1,-1), 'MIDDLE'),
    ]))
    return t

def linha_total(vals, col_widths):
    cells = [Paragraph(f'<b>{v}</b>',
             ParagraphStyle('tt', fontSize=8, fontName='Helvetica-Bold',
                            alignment=TA_RIGHT if i > 0 else TA_LEFT))
             for i, v in enumerate(vals)]
    t = Table([cells], colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), AZUL_CLARO),
        ('GRID',          (0,0), (-1,-1), 0.4, CINZA_BORDA),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING',   (0,0), (-1,-1), 6),
        ('RIGHTPADDING',  (0,0), (-1,-1), 6),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t

def cards_resumo(items):
    """items = list of (label, valor_str, sublabel). Valores já devem vir abreviados."""
    n = len(items)
    cw = CONTENT_W / n
    cells = []
    for label, valor, sub in items:
        cell = [Paragraph(valor, ST['numero_card']),
                Paragraph(label, ST['label_card'])]
        if sub:
            cell.append(Paragraph(sub, ST['label_card']))
        cells.append(cell)
    t = Table([cells], colWidths=[cw]*n)
    t.setStyle(TableStyle([
        ('BOX',           (0,0), (-1,-1), 0.5, AZUL_MEDIO),
        ('INNERGRID',     (0,0), (-1,-1), 0.5, AZUL_MEDIO),
        ('BACKGROUND',    (0,0), (-1,-1), AZUL_CLARO),
        ('TOPPADDING',    (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t

def p(txt, style='corpo', **kw):
    s = ST[style]
    if kw:
        s = ParagraphStyle('_tmp', parent=s, **kw)
    return Paragraph(txt, s)

def ph(txt, cor=BRANCO, align=TA_CENTER):
    return Paragraph(f'<b>{txt}</b>',
        ParagraphStyle('_h', fontSize=8, leading=10,
                       fontName='Helvetica-Bold', textColor=cor, alignment=align))

def pd_(txt, align=TA_LEFT, bold=False):
    return Paragraph(f'<b>{txt}</b>' if bold else txt,
        ParagraphStyle('_d', fontSize=8, leading=10,
                       fontName='Helvetica-Bold' if bold else 'Helvetica',
                       alignment=align))

# ── SEÇÃO POR VINCULAÇÃO ──────────────────────────────
def build_secao(story, df_sub, titulo_header, cor, top_n=10):
    total_val = df_sub['VADOCUMENTO'].sum()
    total_qtd = len(df_sub)

    story.append(Spacer(1, 0.3*cm))
    story.append(header_secao(titulo_header, cor))
    story.append(Spacer(1, 0.3*cm))

    story.append(cards_resumo([
        ('EMPENHOS CADASTRADOS', fmt_n(total_qtd),                          'Abril/2026'),
        ('VALOR TOTAL EMPENHADO', fv(total_val),                             ''),
        ('TICKET MÉDIO',          fv(total_val/total_qtd if total_qtd else 0),'por empenho'),
        ('UNIDADES GESTORAS',     fmt_n(df_sub['COUG'].nunique()),           'UGs envolvidas'),
    ]))
    story.append(Spacer(1, 0.5*cm))

    # ── 1. FONTES (ordem crescente, só 4 dígitos) ─────
    story.append(p('1. Distribuição por Fonte de Recurso', 'subtitulo'))

    CW_F = [2.2*cm, 2.0*cm, 1.8*cm, 8.2*cm, 1.8*cm]   # total = 16.0 cm (≤17)
    fg = (df_sub.groupby('FONTE_GRUPO')
          .agg(QTD=('NUNE','count'), VALOR=('VADOCUMENTO','sum'))
          .sort_values('FONTE_GRUPO', ascending=True).reset_index())

    cab_f = [ph('Fonte'), ph('Qtd.'), ph('% Qtd.'), ph('Valor (R$)'), ph('% Valor')]
    linhas_f = [
        [pd_(row['FONTE_GRUPO'], bold=True),
         pd_(fmt_n(int(row['QTD'])),                   TA_CENTER),
         pd_(f"{row['QTD']/total_qtd*100:.1f}%",       TA_CENTER),
         pd_(fmt_val(row['VALOR']),                     TA_RIGHT),
         pd_(f"{row['VALOR']/total_val*100:.1f}%",      TA_CENTER)]
        for _, row in fg.iterrows()
    ]
    story.append(KeepTogether([
        tabela_dados(cab_f, linhas_f, CW_F),
        linha_total(['TOTAL', fmt_n(total_qtd), '100,0%',
                     fmt_val(total_val), '100,0%'], CW_F),
    ]))
    story.append(Spacer(1, 0.5*cm))

    # ── 2. GND ────────────────────────────────────────
    story.append(p('2. Distribuição por Grupo de Natureza da Despesa (GND)', 'subtitulo'))

    CW_G = [1.4*cm, 5.2*cm, 2.0*cm, 1.6*cm, 5.0*cm, 1.8*cm]  # 17.0 cm
    gg = (df_sub.groupby('GND')
          .agg(QTD=('NUNE','count'), VALOR=('VADOCUMENTO','sum'))
          .sort_values('VALOR', ascending=False).reset_index())

    cab_g = [ph('GND'), ph('Descrição', align=TA_LEFT),
             ph('Qtd.'), ph('% Qtd.'), ph('Valor (R$)'), ph('% Valor')]
    linhas_g = [
        [pd_(f"GND {int(row['GND'])}", bold=True),
         pd_(GND_NOME.get(int(row['GND']), '')),
         pd_(fmt_n(int(row['QTD'])),               TA_CENTER),
         pd_(f"{row['QTD']/total_qtd*100:.1f}%",   TA_CENTER),
         pd_(fmt_val(row['VALOR']),                 TA_RIGHT),
         pd_(f"{row['VALOR']/total_val*100:.1f}%",  TA_CENTER)]
        for _, row in gg.iterrows()
    ]
    story.append(KeepTogether([
        tabela_dados(cab_g, linhas_g, CW_G),
        linha_total(['', 'TOTAL', fmt_n(total_qtd), '100,0%',
                     fmt_val(total_val), '100,0%'], CW_G),
    ]))
    story.append(Spacer(1, 0.5*cm))

    # ── 3. TOP UGs ────────────────────────────────────
    story.append(p(f'3. Principais Unidades Gestoras — Top {top_n} por Valor', 'subtitulo'))

    CW_U = [0.7*cm, 1.8*cm, 6.5*cm, 1.5*cm, 4.7*cm, 1.8*cm]  # 17.0 cm
    ug_g = (df_sub.groupby(['COUG','NOUG'])
            .agg(QTD=('NUNE','count'), VALOR=('VADOCUMENTO','sum'))
            .sort_values('VALOR', ascending=False).head(top_n).reset_index())

    cab_u = [ph('#'), ph('Código'), ph('Unidade Gestora', align=TA_LEFT),
             ph('Qtd.'), ph('Valor (R$)'), ph('% Valor')]
    linhas_u = []
    for idx, row in enumerate(ug_g.itertuples()):
        linhas_u.append([
            pd_(str(idx+1),            TA_CENTER, bold=True),
            pd_(str(int(row.COUG)),    TA_CENTER),
            pd_(row.NOUG),
            pd_(fmt_n(int(row.QTD)),   TA_CENTER),
            pd_(fmt_val(row.VALOR),    TA_RIGHT),
            pd_(f"{row.VALOR/total_val*100:.1f}%", TA_CENTER),
        ])
    story.append(tabela_dados(cab_u, linhas_u, CW_U))
    story.append(Spacer(1, 0.3*cm))


# ════════════════════════════════════════════════════════
# SCRIPT PRINCIPAL
# ════════════════════════════════════════════════════════
def gerar_pdf():
    OUTPUT = r'E:\empenho\Relatorio_Empenhos_Abril2026.pdf'

    total_val  = df['VADOCUMENTO'].sum()
    total_qtd  = len(df)
    total_ugs  = df['COUG'].nunique()
    df_vinc    = df[df['INDESTINACAO'] == 2]
    df_nvinc   = df[df['INDESTINACAO'] == 1]
    vinc_val   = df_vinc['VADOCUMENTO'].sum()
    vinc_qtd   = len(df_vinc)
    nvinc_val  = df_nvinc['VADOCUMENTO'].sum()
    nvinc_qtd  = len(df_nvinc)

    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title='Relatório de Empenhos - Abril/2026',
        author=ORGAO,
    )
    story = []

    # ── CAPA ──────────────────────────────────────────
    capa_topo = Table([[Paragraph('GOVERNO DO DISTRITO FEDERAL', ST['meta_capa'])]],
                      colWidths=[CONTENT_W])
    capa_topo.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), AZUL_ESCURO),
        ('TOPPADDING',    (0,0), (-1,-1), 30),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 20),
        ('RIGHTPADDING',  (0,0), (-1,-1), 20),
    ]))

    capa_corpo_rows = [
        [Paragraph('RELATÓRIO DE EMPENHOS', ST['titulo_capa'])],
        [Paragraph('Sistema Integrado de Gestão Governamental — SIGGO', ST['subtit_capa'])],
        [Spacer(1, 0.2*cm)],
        [Paragraph('Competência: ABRIL / 2026', ST['meta_capa'])],
        [Paragraph('Distribuição por Vinculação de Fonte, Fonte de Recurso e GND', ST['meta_capa'])],
        [Spacer(1, 0.5*cm)],
        [Paragraph(ORGAO, ST['meta_capa'])],
        [Spacer(1, 0.4*cm)],
    ]
    capa_corpo = Table(capa_corpo_rows, colWidths=[CONTENT_W])
    capa_corpo.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), AZUL_MEDIO),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING',   (0,0), (-1,-1), 20),
        ('RIGHTPADDING',  (0,0), (-1,-1), 20),
    ]))

    story.append(capa_topo)
    story.append(capa_corpo)
    story.append(Spacer(1, 0.8*cm))

    # ── CARDS GERAIS ──────────────────────────────────
    story.append(cards_resumo([
        ('TOTAL DE EMPENHOS',    fmt_n(total_qtd),              'Abril/2026 — SIGGO'),
        ('VALOR TOTAL',          fv(total_val),                 ''),
        ('UNIDADES GESTORAS',    fmt_n(total_ugs),              'UGs com empenhos'),
        ('FONTES DE RECURSO',    fmt_n(df['COFONTE'].nunique()),'distintas'),
    ]))
    story.append(Spacer(1, 0.6*cm))

    # ── SUMÁRIO EXECUTIVO ─────────────────────────────
    story.append(hr(AZUL_ESCURO, 1.2))
    story.append(p('SUMÁRIO EXECUTIVO', 'titulo_sec'))
    story.append(hr())

    story.append(p(
        f'No mês de <b>abril de 2026</b>, foram cadastrados no SIGGO <b>{fmt_n(total_qtd)} empenhos</b>, '
        f'totalizando <b>{fmt_val(total_val)}</b> em compromissos orçamentários assumidos '
        f'por <b>{fmt_n(total_ugs)} unidades gestoras</b> do Governo do Distrito Federal, '
        f'distribuídos em <b>{df["COFONTE"].nunique()} fontes de recurso distintas</b>.'))

    story.append(p(
        f'Do total de empenhos, <b>{fmt_n(nvinc_qtd)} ({nvinc_qtd/total_qtd*100:.1f}%)</b> foram '
        f'realizados com <b>fontes não vinculadas</b>, correspondendo a '
        f'<b>{fmt_val(nvinc_val)} ({nvinc_val/total_val*100:.1f}%)</b> do volume financeiro. '
        f'Os empenhos com <b>fontes vinculadas</b> totalizam '
        f'<b>{fmt_n(vinc_qtd)} empenhos ({vinc_qtd/total_qtd*100:.1f}%)</b>, '
        f'no valor de <b>{fmt_val(vinc_val)} ({vinc_val/total_val*100:.1f}%)</b>.'))

    story.append(Spacer(1, 0.3*cm))

    # Tabela resumo vinculação
    CW_R = [4.5*cm, 2.8*cm, 1.6*cm, 5.2*cm, 1.6*cm, 1.3*cm]
    cab_r = [ph('Vinculação', align=TA_LEFT), ph('Qtd. Empenhos'),
             ph('% Qtd.'), ph('Valor Total (R$)'), ph('% Valor'), ph('UGs')]
    linhas_r = [
        [pd_('Não Vinculada'),
         pd_(fmt_n(nvinc_qtd),                    TA_CENTER),
         pd_(f'{nvinc_qtd/total_qtd*100:.1f}%',   TA_CENTER),
         pd_(fmt_val(nvinc_val),                   TA_RIGHT),
         pd_(f'{nvinc_val/total_val*100:.1f}%',    TA_CENTER),
         pd_(fmt_n(df_nvinc['COUG'].nunique()),    TA_CENTER)],
        [pd_('Vinculada'),
         pd_(fmt_n(vinc_qtd),                     TA_CENTER),
         pd_(f'{vinc_qtd/total_qtd*100:.1f}%',    TA_CENTER),
         pd_(fmt_val(vinc_val),                    TA_RIGHT),
         pd_(f'{vinc_val/total_val*100:.1f}%',     TA_CENTER),
         pd_(fmt_n(df_vinc['COUG'].nunique()),     TA_CENTER)],
    ]
    story.append(tabela_dados(cab_r, linhas_r, CW_R))
    story.append(Spacer(1, 0.6*cm))

    # ── SEÇÃO I — FONTES NÃO VINCULADAS ───────────────
    story.append(PageBreak())
    story.append(hr(AZUL_ESCURO, 1.2))
    story.append(p('SEÇÃO I — FONTES NÃO VINCULADAS', 'titulo_sec'))
    story.append(hr())
    build_secao(story, df_nvinc, 'FONTES NÃO VINCULADAS', VERDE)

    # ── SEÇÃO II — FONTES VINCULADAS ──────────────────
    story.append(PageBreak())
    story.append(hr(AZUL_ESCURO, 1.2))
    story.append(p('SEÇÃO II — FONTES VINCULADAS', 'titulo_sec'))
    story.append(hr())
    build_secao(story, df_vinc, 'FONTES VINCULADAS', AZUL_MEDIO)

    # ── RODAPÉ ────────────────────────────────────────
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 7.5)
        canvas.setFillColor(HexColor('#94a3b8'))
        canvas.drawString(2*cm, 1.2*cm,
            f'GDF — {ORGAO} | Relatório de Empenhos SIGGO — Abril/2026 | CONFIDENCIAL')
        canvas.drawRightString(W - 2*cm, 1.2*cm, f'Página {doc.page}')
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f'PDF gerado: {OUTPUT}')
    print(f'Tamanho: {os.path.getsize(OUTPUT)/1024:.0f} KB')
    from pypdf import PdfReader
    print(f'Páginas: {len(PdfReader(OUTPUT).pages)}')

gerar_pdf()
