def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()

    def txt(t):
        return t.encode('latin-1', 'replace').decode('latin-1')

    # Fundo
    pdf.set_fill_color(230,255,230)
    pdf.rect(0,0,210,297,'F')

    # Cabeçalho
    pdf.set_fill_color(34,139,34)
    pdf.rect(0,0,210,35,'F')

    pdf.set_text_color(255,255,255)
    pdf.set_font("Arial","B",18)
    pdf.cell(210,15, txt("CONSULTORIA AGRONÔMICA"), align="C")

    pdf.ln(10)
    pdf.set_font("Arial","B",12)
    pdf.cell(210,10, txt("Consultor: Felipe Amorim"), align="C")

    pdf.ln(25)
    pdf.set_text_color(0,0,0)

    # DADOS
    pdf.set_fill_color(220,220,220)
    pdf.set_font("Arial","B",12)
    pdf.cell(190,8, txt("DADOS DA ÁREA"), ln=True, fill=True)

    pdf.set_font("Arial","",11)
    pdf.cell(190,8, txt(f"Produtor: {cliente}"), ln=True)
    pdf.cell(190,8, txt(f"Área: {area} ha"), ln=True)
    pdf.cell(190,8, txt(f"Cultura: {cultura}"), ln=True)

    pdf.ln(5)

    # ANÁLISE
    pdf.set_font("Arial","B",12)
    pdf.cell(190,8, txt("ANÁLISE DO SOLO"), ln=True, fill=True)

    pdf.set_font("Arial","",11)
    pdf.cell(190,8, txt(f"Fósforo: {p} mg/dm³"), ln=True)
    pdf.cell(190,8, txt(f"Potássio: {k} cmolc/dm³"), ln=True)
    pdf.cell(190,8, txt(f"Argila: {argila}"), ln=True)
    pdf.cell(190,8, txt(f"V%: {v_atual}"), ln=True)

    pdf.ln(5)

    # CALAGEM
    pdf.set_font("Arial","B",12)
    pdf.cell(190,8, txt("CALAGEM"), ln=True, fill=True)

    pdf.set_font("Arial","",11)

    if nc == 0:
        pdf.multi_cell(190,8, txt(obs_calagem))
    else:
        pdf.cell(190,8, txt(f"Necessidade: {nc:.2f} t/ha"), ln=True)
        pdf.cell(190,8, txt(f"Total: {total_calc:.2f} t"), ln=True)

    pdf.ln(5)

    # ADUBAÇÃO
    pdf.set_font("Arial","B",12)
    pdf.cell(190,8, txt("ADUBAÇÃO"), ln=True, fill=True)

    pdf.set_font("Arial","",11)
    pdf.cell(190,8, txt(f"N: {req_n} kg/ha"), ln=True)
    pdf.cell(190,8, txt(f"P₂O₅: {req_p} kg/ha"), ln=True)
    pdf.cell(190,8, txt(f"K₂O: {req_k} kg/ha"), ln=True)

    pdf.cell(190,8, txt(obs_n), ln=True)

    # 👉 ADUBO FORMULADO (AGORA VAI APARECER)
    if dose > 0:
        pdf.ln(5)
        pdf.set_font("Arial","B",12)
        pdf.cell(190,8, txt("ADUBO FORMULADO"), ln=True, fill=True)

        pdf.set_font("Arial","",11)
        pdf.cell(190,8, txt(f"Fórmula: {f_n}-{f_p}-{f_k}"), ln=True)
        pdf.cell(190,8, txt(f"Dose: {dose:.0f} kg/ha"), ln=True)
        pdf.cell(190,8, txt(f"Total: {sacos} sacos"), ln=True)

    return bytes(pdf.output(dest='S'))
