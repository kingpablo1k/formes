import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import json
import os

# Caminho para o arquivo de armazenamento
DATA_FILE = "data.json"

def load_data():
    """Carrega os dados do arquivo JSON, se existir."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_data(data):
    """Salva os dados no arquivo JSON."""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def main():
    st.set_page_config(page_title="Estudos para Concurso", page_icon="📝")
    
    # Carregar dados persistidos
    if "data" not in st.session_state:
        st.session_state.data = load_data()
    
    if "logged_in" not in st.session_state.data:
        st.session_state.data["logged_in"] = False
    
    if "subjects" not in st.session_state.data:
        st.session_state.data["subjects"] = {}
    
    if "notes" not in st.session_state.data:
        st.session_state.data["notes"] = ""
    
    if "revisao" not in st.session_state.data:
        st.session_state.data["revisao"] = []  # Lista para armazenar os resultados com acertos abaixo de 80%

    if not st.session_state.data["logged_in"]:
        login_page()
    else:
        notes_page()

def login_page():
    st.title("Login para Estudos")
    st.write("Digite a senha de 6 dígitos para acessar suas anotações.")
    
    password = st.text_input("Senha:", type="password", max_chars=6)
    
    if st.button("Entrar") or (password and len(password) == 6 and password == "181920"):
        if password == "181920":
            st.session_state.data["logged_in"] = True
            save_data(st.session_state.data)  # Salvar os dados após login
            st.rerun()
        else:
            st.error("Senha incorreta. Tente novamente.")

def notes_page():
    st.write("### Desempenho de Questões")
    
    materias_existentes = list(st.session_state.data["subjects"].keys())
    if materias_existentes:
        materia_selecionada = st.selectbox("Selecione a matéria:", materias_existentes)
        
        if materia_selecionada not in st.session_state.data["subjects"]:
            st.session_state.data["subjects"][materia_selecionada] = {}

        assuntos_existentes = list(st.session_state.data["subjects"][materia_selecionada].keys())
        if assuntos_existentes:
            assunto_selecionado = st.selectbox("Selecione um assunto:", assuntos_existentes)
            
            if assunto_selecionado not in st.session_state.data["subjects"][materia_selecionada]:
                st.session_state.data["subjects"][materia_selecionada][assunto_selecionado] = []
                
            acertos = st.number_input("Número de questões corretas:", min_value=0, step=1)
            total_questoes = st.number_input("Número total de questões:", min_value=1, step=1)

            if acertos and total_questoes:
                if st.button("Registrar Resultado"):
                    # Adicionando a data ao registro
                    data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    prova = {"acertos": acertos, "total": total_questoes, "data": data_atual}
                    st.session_state.data["subjects"][materia_selecionada][assunto_selecionado].append(prova)
                    save_data(st.session_state.data)  # Salvar os dados após registrar resultado
                    st.success(f"Resultado para o assunto '{assunto_selecionado}' registrado!")
                    
                    # Verifique se o percentual é menor que 80% e registre na parte de Revisar Conteúdo
                    percentual = (acertos / total_questoes) * 100
                    if percentual < 80:
                        revisao = {"materia": materia_selecionada, "assunto": assunto_selecionado, "acertos": acertos, "total": total_questoes, "% Acerto": f"{percentual:.2f}%", "data": data_atual}

                        if "revisao" not in st.session_state.data:
                            st.session_state.data["revisao"] = []

                        st.session_state.data["revisao"].append(revisao)
                        save_data(st.session_state.data)  # Salvar os dados após atualizar revisão
    
    show_revisar_conteudo = st.checkbox("Mostrar Revisar Conteúdo")
    
    if show_revisar_conteudo:
        if "revisao" in st.session_state.data and st.session_state.data["revisao"]:
            revisao_df = pd.DataFrame(st.session_state.data["revisao"])
            st.write("### Resultados para Revisar (Acerto < 80%)")
            st.dataframe(revisao_df)
            
            # Botão para remover teste revisado
            revisao_para_remover = st.selectbox("Escolha um teste para remover:", ["Selecione um teste"] + [f"{r['materia']} - {r['assunto']} ({r['data']})" for r in st.session_state.data["revisao"]])
            
            if revisao_para_remover != "Selecione um teste":
                if st.button("Remover Teste"):
                    # Ajuste para separar corretamente os dados
                    try:
                        # Extrair matéria, assunto e data
                        materia, assunto_data = revisao_para_remover.split(" - ")
                        assunto, data = assunto_data.split(" (")
                        data = data.rstrip(')')  # Remover parênteses de fechamento

                        # Remover o teste de revisão
                        st.session_state.data["revisao"] = [r for r in st.session_state.data["revisao"] if not (r['materia'] == materia and r['assunto'] == assunto and r['data'] == data)]
                        save_data(st.session_state.data)  # Salvar os dados após remover teste
                        st.success(f"Teste '{materia} - {assunto}' removido dos testes revisados.")
                    except ValueError:
                        st.error("Erro ao tentar remover o teste. Verifique se o formato está correto.")
        else:
            st.warning("Nenhum resultado com acertos abaixo de 80% ainda registrado.")
    
    # Opções para adicionar ou remover matéria
    show_materia_options = st.checkbox("Mostrar opções para adicionar ou remover matéria")
    
    if show_materia_options:
        materia = st.text_input("Digite o nome da matéria:")
        
        if materia.strip() and st.button("Adicionar Matéria"):
            if materia not in st.session_state.data["subjects"]:
                st.session_state.data["subjects"][materia] = {}
                save_data(st.session_state.data)  # Salvar os dados após adicionar matéria
                st.success(f"Matéria '{materia}' adicionada!")
            else:
                st.warning(f"A matéria '{materia}' já existe.")
        
        if st.session_state.data["subjects"]:
            materia_para_remover = st.selectbox("Escolha uma matéria para remover:", ["Selecione uma matéria"] + list(st.session_state.data["subjects"].keys()))
            
            if materia_para_remover != "Selecione uma matéria" and st.button(f"Remover Matéria '{materia_para_remover}'"):
                del st.session_state.data["subjects"][materia_para_remover]
                save_data(st.session_state.data)  # Salvar os dados após remover matéria
                st.success(f"Matéria '{materia_para_remover}' removida.")
    
    # Opções para adicionar ou remover assunto
    show_assunto_options = st.checkbox("Mostrar opções para adicionar ou remover assunto")
    
    if show_assunto_options and materias_existentes:
        assunto = st.text_input("Digite um assunto:")
        
        if assunto.strip() and st.button("Adicionar Assunto"):
            if assunto and assunto not in st.session_state.data["subjects"][materia_selecionada]:
                st.session_state.data["subjects"][materia_selecionada][assunto] = []
                save_data(st.session_state.data)  # Salvar os dados após adicionar assunto
                st.success(f"Assunto '{assunto}' adicionado!")
            else:
                st.warning(f"O assunto '{assunto}' já existe nesta matéria.")
        
        if st.session_state.data["subjects"][materia_selecionada]:
            assunto_para_remover = st.selectbox("Escolha um assunto para remover:", ["Selecione um assunto"] + list(st.session_state.data["subjects"][materia_selecionada].keys()))
            
            if assunto_para_remover != "Selecione um assunto" and st.button(f"Remover Assunto '{assunto_para_remover}'"):
                del st.session_state.data["subjects"][materia_selecionada][assunto_para_remover]
                save_data(st.session_state.data)  # Salvar os dados após remover assunto
                st.success(f"Assunto '{assunto_para_remover}' removido da matéria {materia_selecionada}.")
    
    # Exibir desempenho geral
    show_desempenho_geral = st.checkbox("Mostrar Desempenho Geral")
    
    if show_desempenho_geral:
        data = []
        for materia, assuntos in st.session_state.data["subjects"].items():
            for assunto, provas in assuntos.items():
                for prova in provas:
                    percentual = (prova["acertos"] / prova["total"]) * 100
                    data.append([materia, assunto, prova["acertos"], prova["total"], f"{percentual:.2f}%", prova["data"]])
        
        if data:
            df = pd.DataFrame(data, columns=["Matéria", "Assunto", "Acertos", "Total de Questões", "% Acerto", "Data"])
            st.write("### Desempenho por Matéria e Assunto")
            st.dataframe(df)
            
            fig, ax = plt.subplots()
            df.groupby("Matéria")["Acertos"].sum().plot(kind="bar", ax=ax)
            ax.set_ylabel("Total de Acertos")
            ax.set_title("Desempenho por Matéria")
            st.pyplot(fig)
        else:
            st.warning("Nenhum dado salvo ainda.")
    
    # Botão para sair e deslogar
    if st.button("Sair"):
        st.session_state.data["logged_in"] = False
        save_data(st.session_state.data)  # Salvar os dados após deslogar
        st.rerun()


if __name__ == "__main__":
    main()
