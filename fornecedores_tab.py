from PyQt5 import QtWidgets, QtCore
import shutil
import os
import requests
import json

class FornecedoresTab:
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.ui = main.ui
        self.db = main.db
        self.usuario = main.id_usuario
        self.funcao = main.funcao
        self.lista_setor = []
        self.lista_setor_edit = []
        self.lista_vendedor = []
        self.lista_documentos = []

#===============================FORNECEDORES=============================#  

    def carregar_tree_fornecedores(self):
        dados = self.db.get_all_fornecedores()

        self.ui.tree_forn_info.clear()

        fornecedor_atual = None
        setor_atual = None

        for row in dados:
            if fornecedor_atual != row["id_fornecedor"]:
                fornecedor_atual = row["id_fornecedor"]
                vendedores = self.db.vendedor_por_fornecedor(row["id_fornecedor"])

                fornecedor_item = QtWidgets.QTreeWidgetItem(self.ui.tree_forn_info)
                fornecedor_item.setText(0, row["nome_empresarial"])
                fornecedor_item.setData(0, QtCore.Qt.UserRole, row["id_fornecedor"])

                dados_item = QtWidgets.QTreeWidgetItem(fornecedor_item, ["Dados Cadastrais"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"CNPJ: {row['cnpj']}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Categoria: {row['categoria']}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Número: {row['numero']}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Complemento: {row['complemento']}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Bairro: {row['bairro']}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Município: {row['municipio']}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"UF: {row['uf']}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"CEP: {row['cep']}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"E-mail: {row['email']}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Telefone: {row['telefone']}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Aptidão: {row['status_aptidao']}"])

                setores_root = QtWidgets.QTreeWidgetItem(fornecedor_item, ["Setores"])
                setor_atual = None
            
                vendedores_root = QtWidgets.QTreeWidgetItem(fornecedor_item, ["Vendedores"])
                for v in vendedores:
                    vendedores_item = QtWidgets.QTreeWidgetItem(
                        vendedores_root, [v["nome"]]
                    )
                    vendedores_item.setData(0, QtCore.Qt.UserRole, v)
                    
                    QtWidgets.QTreeWidgetItem(vendedores_item, [v["contato"]])
                    QtWidgets.QTreeWidgetItem(vendedores_item, [v["status_vendedor"]])

            if setor_atual != row["id_setor"]:
                setor_atual = row["id_setor"]

                setor_item = QtWidgets.QTreeWidgetItem(
                    setores_root,
                    [f"{row['atividade']} ({row['criticidade']})"]
                )
                setor_item.setData(0, QtCore.Qt.UserRole, row["id_setor"])

            if row["id_documento"] is not None:
                doc_item = QtWidgets.QTreeWidgetItem(
                    setor_item,
                    [row["nome"]]
                )
                doc_item.setData(0, QtCore.Qt.UserRole, row["id_documento"])
                
    def filtro_fornecedores(self):
        termo = self.ui.edit_forn_pesquisar.text()
        
        dados = self.db.filtro_fornecedores(termo)
        
        if not dados:
            self.carregar_tree_fornecedores()
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Não foram encontrados resultados para: {termo}")
        
        else:
            self.ui.tree_forn_info.clear()

            fornecedor_atual = None
            setor_atual = None

            for row in dados:
                if fornecedor_atual != row["id_fornecedor"]:
                    fornecedor_atual = row["id_fornecedor"]

                    fornecedor_item = QtWidgets.QTreeWidgetItem(self.ui.tree_forn_info)
                    fornecedor_item.setText(0, row["nome_empresarial"])
                    fornecedor_item.setData(0, QtCore.Qt.UserRole, row["id_fornecedor"])

                    dados_item = QtWidgets.QTreeWidgetItem(fornecedor_item, ["Dados Cadastrais"])
                    QtWidgets.QTreeWidgetItem(dados_item, [f"CNPJ: {row['cnpj']}"])
                    QtWidgets.QTreeWidgetItem(dados_item, [f"Categoria: {row['categoria']}"])
                    QtWidgets.QTreeWidgetItem(dados_item, [f"Número: {row['numero']}"])
                    QtWidgets.QTreeWidgetItem(dados_item, [f"Complemento: {row['complemento']}"])
                    QtWidgets.QTreeWidgetItem(dados_item, [f"Bairro: {row['bairro']}"])
                    QtWidgets.QTreeWidgetItem(dados_item, [f"Município: {row['municipio']}"])
                    QtWidgets.QTreeWidgetItem(dados_item, [f"UF: {row['uf']}"])
                    QtWidgets.QTreeWidgetItem(dados_item, [f"CEP: {row['cep']}"])
                    QtWidgets.QTreeWidgetItem(dados_item, [f"E-mail: {row['email']}"])
                    QtWidgets.QTreeWidgetItem(dados_item, [f"Telefone: {row['telefone']}"])
                    QtWidgets.QTreeWidgetItem(dados_item, [f"Aptidão: {row['status_aptidao']}"])

                    setores_root = QtWidgets.QTreeWidgetItem(fornecedor_item, ["Setores"])
                    setor_atual = None

                if setor_atual != row["id_setor"]:
                    setor_atual = row["id_setor"]

                    setor_item = QtWidgets.QTreeWidgetItem(
                        setores_root,
                        [f"{row['atividade']} ({row['criticidade']})"]
                    )
                    setor_item.setData(0, QtCore.Qt.UserRole, row["id_setor"])

                if row["id_documento"] is not None:
                    doc_item = QtWidgets.QTreeWidgetItem(
                        setor_item,
                        [row["nome"]]
                    )
                    doc_item.setData(0, QtCore.Qt.UserRole, row["id_documento"])

    def carregar_tab_forn(self):
        self.ui.tabs.setCurrentIndex(0)
        self.listar_fornecedor_vinculo()
        self.listar_setores_vinculo()
        self.carregar_tree_fornecedores()
        
#===============================CADASTRO FORNECEDORES===============================#

    def carregar_tab_cadastro_forn(self):
        if self.funcao != "ADMINISTRADOR" and self.funcao != "GERENTE" and self.funcao != "ALMOXARIFADO":
            QtWidgets.QMessageBox.information(self.main, "Aviso", "Você não tem permissão para acessar essa aba.")
            return
        
        self.ui.tabs.setCurrentIndex(1)
        self.carregar_lista_setores_cadastro()
        self.limpar_campos_cadastro()

    def carregar_lista_setores_cadastro(self):
        self.ui.box_cadastro_forn_setor.clear()
        
        try:
            setores = self.db.listar_setores()
            self.ui.box_cadastro_forn_setor.addItem("Selecione um setor:")
            
            for s in setores:
                self.ui.box_cadastro_forn_setor.addItem(s['atividade'], s['id_setor'])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao carregar setores: {e}")

    def buscar_por_cnpj(self, cnpj):
        url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
        
        querystring = {"token": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX", "cnpj":"06990590000123", "plugin": "RF"}
        
        try:
            resposta = requests.request("GET", url, params=querystring)
            
            resp = json.loads(resposta.text)
            
            return resp['fantasia'], resp['logradouro'], resp['numero'], resp['complemento'], resp['bairro'], resp['municipio'], resp['uf'], resp['cep'], resp['telefone'], resp['email']
        
        except requests.exceptions.ConnectionError:
            QtWidgets.QMessageBox.warning(self.main, "Sem conexão", "Não foi possível conectar à internet.")
            return None
        
        except requests.exceptions.Timeout:
            QtWidgets.QMessageBox.warning(self.main, "Tempo esgotado", "A consulta demorou muito para responder.")
            return None
            
        except requests.exceptions.HTTPError:
            QtWidgets.QMessageBox.warning(self.main, "Erro na consulta", "CNPJ não encontrado ou serviço indisponível.")
            return None
        
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro inesperado", str(e))
            return None

    def cadastrar_fornecedor(self):
        info = (self.ui.edit_cadastro_forn_cnpj.text(), self.ui.edit_cadastro_forn_nome.text(), self.ui.box_cadastro_forn_categoria.currentText(),
                self.ui.edit_cadastro_forn_logradouro.text(), self.ui.edit_cadastro_forn_municipio.text(), self.ui.edit_cadastro_forn_bairro.text(),
                self.ui.edit_cadastro_forn_uf.text(), self.ui.edit_cadastro_forn_num.text(), self.ui.edit_cadastro_forn_complemento.text(),
                self.ui.edit_cadastro_forn_cep.text(), self.ui.edit_cadastro_forn_email.text(), self.ui.edit_cadastro_forn_tel.text(), "NAO_APTO", self.usuario)
        
        id_fornecedor = self.db.cadastrar_fornecedor(info)
        
        for s in self.lista_setor:
            id_setor = s["id_setor"]
            self.db.vincular_setor_fornecedor(id_fornecedor, id_setor)
        
        for item in self.lista_vendedor:
            info_vendedor = (
                id_fornecedor,
                item['nome'],
                item['telefone'],
                item['status']
            )
        
            self.db.cadastrar_vendedor(info_vendedor)
        
        self.limpar_campos_cadastro()
        self.carregar_tree_fornecedores()

    def cadastro_vendedores(self):
        
        nome = self.ui.edit_forn_cadastro_vendedores_nome.text()
        telefone = self.ui.edit_forn_cadastro_vendedores_telefone.text()
        status = self.ui.box_forn_cadastro_vendedores_status.currentText()
        
        info = {
            "nome": nome,
            "telefone": telefone,
            "status": status
        }
        
        self.lista_vendedor.append(info)
        self.carregar_vendedores()
    
    def carregar_vendedores(self):
        tabela = self.ui.table_forn_cadastro_vendedores
        tabela.setRowCount(0)
        
        for item in self.lista_vendedor:
            row = tabela.rowCount()
            tabela.insertRow(row)
            
            tabela.setItem(row, 0, QtWidgets.QTableWidgetItem(item["nome"]))
            tabela.setItem(row, 1, QtWidgets.QTableWidgetItem(item["telefone"]))
            tabela.setItem(row, 2, QtWidgets.QTableWidgetItem(item["status"]))

    def limpar_campos_cadastro(self):
        self.ui.box_cadastro_forn_setor.setCurrentIndex(0)
        self.ui.edit_cadastro_forn_cnpj.clear()
        self.ui.edit_cadastro_forn_nome.clear()
        self.ui.box_cadastro_forn_categoria.setCurrentIndex(0)
        self.ui.edit_cadastro_forn_logradouro.clear()
        self.ui.edit_cadastro_forn_municipio.clear()
        self.ui.edit_cadastro_forn_bairro.clear(),
        self.ui.edit_cadastro_forn_uf.clear()
        self.ui.edit_cadastro_forn_num.clear()
        self.ui.edit_cadastro_forn_complemento.clear()
        self.ui.edit_cadastro_forn_cep.clear()
        self.ui.edit_cadastro_forn_email.clear()
        self.ui.edit_cadastro_forn_tel.clear()
        self.lista_vendedor.clear()
        self.lista_setor.clear()
        self.ui.edit_forn_cadastro_vendedores_nome.clear()
        self.ui.edit_forn_cadastro_vendedores_telefone.clear()
        self.ui.box_forn_cadastro_vendedores_status.setCurrentIndex(0)
        self.carregar_vendedores()
        self.carregar_tabela_setores()

    def listar_setor_cadastro(self):
        info_setor = {
            "id_setor": self.ui.box_cadastro_forn_setor.currentData(),
            "setor": self.ui.box_cadastro_forn_setor.currentText()
        }
        
        self.lista_setor.append(info_setor)
        self.carregar_tabela_setores()

    def carregar_tabela_setores(self):
        tabela = self.ui.table_cadastro_forn_setor
        tabela.setRowCount(0)
        
        for item in self.lista_setor:
            row = tabela.rowCount()
            tabela.insertRow(row)
            
            tabela.setItem(row, 0, QtWidgets.QTableWidgetItem(item["setor"]))

#===============================EDITAR FORNECEDORES===============================#

    def carregar_tab_edit_forn(self):
        if self.funcao != "ADMINISTRADOR" and self.funcao != "GERENTE" and self.funcao != "ALMOXARIFADO":
            QtWidgets.QMessageBox.information(self.main, "Aviso", "Você não tem permissão para acessar essa aba.")
            return
        
        self.ui.tabs.setCurrentIndex(2)
        self.listar_fornecedores_edit()
        self.carregar_lista_setores_edit()

    def carregar_info_forn(self):
        self.carregar_lista_setores_fornecedor()
        self.carregar_campos_fornecedor()

    def listar_fornecedores_edit(self):
        self.ui.box_edit_forn_forn.clear()
        
        try:
            fornecedores = self.db.listar_fornecedores()
            self.ui.box_edit_forn_forn.addItem("Selecione um fornecedor:")
            
            for f in fornecedores:
                self.ui.box_edit_forn_forn.addItem(f["nome_empresarial"], f["id_fornecedor"])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao listar fornecedores: {e}")

    def carregar_lista_setores_edit(self):
        self.ui.box_edit_forn_novo_setor.clear()
        
        try:
            setores = self.db.listar_setores()
            self.ui.box_edit_forn_novo_setor.addItem("Selecione um setor:")
            
            for s in setores:
                self.ui.box_edit_forn_novo_setor.addItem(s['atividade'], s['id_setor'])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao carregar setores: {e}")   
    
    def carregar_lista_setores_fornecedor(self):
        id_fornecedor = self.ui.box_edit_forn_forn.currentData()
        
        if not id_fornecedor:
            return
        
        self.ui.box_edit_forn_setor.clear()
        
        setor_fornecedor = self.db.setor_fornecedor(id_fornecedor)
        
        try:
            self.ui.box_edit_forn_setor.addItem("Selecione um setor:")
            for f in setor_fornecedor:
                self.ui.box_edit_forn_setor.addItem(f["atividade"], f["id_setor"])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao carregar setores cadastrados: {e}")
    
    def remover_setor(self):
        id_fornecedor = self.ui.box_edit_forn_forn.currentData()
        id_setor = self.ui.box_edit_forn_setor.currentData()
        
        if not id_setor or not id_fornecedor:
            return
        
        self.db.remover_setor(id_fornecedor, id_setor)       

    def carregar_campos_fornecedor(self):
        id_fornecedor = self.ui.box_edit_forn_forn.currentData()
        
        if not id_fornecedor:
            return
        
        fornecedor = self.db.get_fornecedor(id_fornecedor)
        
        self.ui.edit_edit_forn_cnpj.setText(fornecedor["cnpj"])
        self.ui.box_edit_forn_categoria.setCurrentText(fornecedor["categoria"])
        self.ui.edit_edit_forn_municipio.setText(fornecedor["municipio"])
        self.ui.edit_edit_forn_uf.setText(fornecedor["uf"])
        self.ui.edit_edit_forn_complemento.setText(fornecedor["complemento"])
        self.ui.edit_edit_forn_email.setText(fornecedor["email"])
        self.ui.edit_edit_forn_nome.setText(fornecedor["nome_empresarial"])
        self.ui.edit_edit_forn_logradouro.setText(fornecedor["logradouro"])
        self.ui.edit_edit_forn_bairro.setText(fornecedor["bairro"])
        self.ui.edit_edit_forn_num.setText(fornecedor["numero"])
        self.ui.edit_edit_forn_cep.setText(fornecedor["cep"])
        self.ui.edit_edit_forn_tel.setText(fornecedor["telefone"])
        self.ui.box_edit_forn_status.setCurrentText(fornecedor["status_aptidao"])
        
    def manter_alteracoes_edit_forn(self):
        id_fornecedor = self.ui.box_edit_forn_forn.currentData()
        
        if not id_fornecedor:
            return
        
        info = {
        "cnpj": self.ui.edit_edit_forn_cnpj.text(),
        "categoria": self.ui.box_edit_forn_categoria.currentText(),
        "municipio": self.ui.edit_edit_forn_municipio.text(),
        "uf": self.ui.edit_edit_forn_uf.text(),
        "complemento": self.ui.edit_edit_forn_complemento.text(),
        "email": self.ui.edit_edit_forn_email.text(),
        "nome_empresarial": self.ui.edit_edit_forn_nome.text(),
        "logradouro": self.ui.edit_edit_forn_logradouro.text(),
        "bairro": self.ui.edit_edit_forn_bairro.text(),
        "numero": self.ui.edit_edit_forn_num.text(),
        "cep": self.ui.edit_edit_forn_cep.text(),
        "telefone": self.ui.edit_edit_forn_tel.text(),
        "status_aptidao": self.ui.box_edit_forn_status.currentText()
        }
        
        try:
            self.db.edit_fornecedor(info, id_fornecedor)
            QtWidgets.QMessageBox.information(self.main, "Informação", f"Sucesso ao editar fornecedor!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao editar fornecedor: {e}")
            return
        try: 
            for s in self.lista_setor_edit:
                id_setor = s["id_setor"]
                self.db.vincular_setor_fornecedor(id_fornecedor, id_setor)
            QtWidgets.QMessageBox.information(self.main, "Sucesso", "Setores editados com sucesso!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao editar os setores, tente novamente: {e}")
            return

            
        self.carregar_tree_fornecedores()
        self.limpar_campos_edit()

    def limpar_campos_edit(self):
        
        self.ui.edit_edit_forn_cnpj.clear()
        self.ui.box_edit_forn_categoria.setCurrentIndex(0)
        self.ui.edit_edit_forn_municipio.clear()
        self.ui.edit_edit_forn_uf.clear()
        self.ui.edit_edit_forn_complemento.clear()
        self.ui.edit_edit_forn_email.clear()
        self.ui.edit_edit_forn_nome.clear()
        self.ui.edit_edit_forn_logradouro.clear()
        self.ui.edit_edit_forn_bairro.clear()
        self.ui.edit_edit_forn_num.clear()
        self.ui.edit_edit_forn_cep.clear()
        self.ui.edit_edit_forn_tel.clear()
        self.ui.box_edit_forn_status.setCurrentIndex(0)
        self.ui.box_edit_forn_forn.setCurrentIndex(0)
        self.lista_setor_edit.clear()
        self.carregar_tab_setores_edit()

    def carregar_tab_setores_edit(self):
        tabela = self.ui.table_edit_forn_novo_setor
        tabela.setRowCount(0)
        
        for s in self.lista_setor_edit:
            row = tabela.rowCount()
            tabela.insertRow(row)
            
            tabela.setItem(row, 0, QtWidgets.QTableWidgetItem(s["setor"]))
    
    def listar_setor_edit(self):
        info_setor = {
            "id_setor": self.ui.box_edit_forn_novo_setor.currentData(),
            "setor": self.ui.box_edit_forn_novo_setor.currentText()
        }
        
        self.lista_setor_edit.append(info_setor)
        self.carregar_tab_setores_edit()
        
#===============================SETORES===============================#

    def carregar_tree_setores(self):
        dados = self.db.get_all_setores()
        
        self.ui.tree_setor_info.clear()
        
        setor_atual = None
        
        for row in dados:
            if setor_atual != row["id_setor"]:
                setor_atual = row["id_setor"]
                
                setor_item = QtWidgets.QTreeWidgetItem(self.ui.tree_setor_info)
                setor_item.setText(0, row["atividade"])
                setor_item.setData(0, QtCore.Qt.UserRole, row["id_setor"])
                
                documentos_root = QtWidgets.QTreeWidgetItem(setor_item, ["Documentos Necessários"])
            if row["id_doc_necessario"] is not None:
                    documento_item = QtWidgets.QTreeWidgetItem(documentos_root, [f"Documento: {row["nome"]}\nTipo do documento: {row["tipo"]}"])
                    documento_item.setData(0, QtCore.Qt.UserRole, row["id_doc_necessario"])

    def filtro_setores(self):
        termo = self.ui.edit_setor_pesquisar.text()
        
        dados = self.db.filtro_setores(termo)
        
        if not dados:
            self.carregar_tree_setores()
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Não foram encontrados resultados para: {termo}")
        
        else:
            self.ui.tree_setor_info.clear()
            
            setor_atual = None
            documento_atual = None
            
            for row in dados:
                if setor_atual != row["id_setor"]:
                    setor_atual = row["id_setor"]
                    documento_atual = None
                    
                    setor_item = QtWidgets.QTreeWidgetItem(self.ui.tree_setor_info)
                    setor_item.setText(0, row["atividade"])
                    setor_item.setData(0, QtCore.Qt.UserRole, row["id_setor"])
                    
                    documentos_root = QtWidgets.QTreeWidgetItem(setor_item, ["Documentos Necessários"])
                if row["id_doc_necessario"] is not None:
                    if documento_atual != row["id_doc_necessario"]:
                        documento_atual = row["id_doc_necessario"]
                        
                        documento_item = QtWidgets.QTreeWidgetItem(documentos_root, [f"Documento: {row["nome"]}\nTipo do documento: {row["tipo"]}"])
                        documento_item.setData(0, QtCore.Qt.UserRole, row["id_doc_necessario"])
            
    def carregar_tab_setores(self):
        self.ui.tabs.setCurrentIndex(3)
        self.carregar_tree_setores()
    
#===============================CADASTRO SETOR===============================#
    
    def carregar_tab_setor_cadastro(self):
        if self.funcao != "ADMINISTRADOR" and self.funcao != "GERENTE" and self.funcao != "ALMOXARIFADO":
            QtWidgets.QMessageBox.information(self.main, "Aviso", "Você não tem permissão para acessar essa aba.")
            return
        
        self.ui.tabs.setCurrentIndex(4)
        self.limpar_campos_setor_cadastro()
    
    def carregar_tabela_doc_nec(self):
        tabela = self.ui.table_cadastro_setor_doc_nec
        tabela.setRowCount(0)
        
        for item in self.lista_documentos:
            row = tabela.rowCount()
            tabela.insertRow(row)
            
            tabela.setItem(row, 0, QtWidgets.QTableWidgetItem(item["nome"]))
            tabela.setItem(row, 1, QtWidgets.QTableWidgetItem(item["tipo"]))
            
    def limpar_campos_setor_cadastro(self):
        self.ui.edit_cadastro_setor_atividade.clear()
        self.ui.box_cadastro_setor_criticidade.setCurrentIndex(0)
        self.lista_documentos.clear()
        self.ui.edit_cadastro_setor_doc_nec_nome.clear()
        self.ui.box_cadastro_setor_doc_nec_tipo.setCurrentIndex(0)
        self.carregar_tabela_doc_nec()
        
    def cadastrar_setor(self):
        info = (self.ui.edit_cadastro_setor_atividade.text(), self.ui.box_cadastro_setor_criticidade.currentText(), self.usuario)
        
        try:
            id_setor = self.db.cadastrar_setor(info)
            QtWidgets.QMessageBox.information(self.main, "Cadastro realizado!", "Cadastro do setor realizado com sucesso!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao cadastrar setor: {e}")
            return
        
        try:
            for d in self.lista_documentos:
                info_doc = (id_setor, d["nome"], d["tipo"], self.usuario)
                self.db.registrar_documento_necessario(info_doc)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao listar documentos necessários ajuste o setor: {e}")
            return
        QtWidgets.QMessageBox.information(self.main, "Sucesso!", "Documentos listados com sucesso!")
        self.limpar_campos_setor_cadastro()
        
    def listar_doc_necessarios(self):
        info_doc = {
            "nome": self.ui.edit_cadastro_setor_doc_nec_nome.text(),
            "tipo": self.ui.box_cadastro_setor_doc_nec_tipo.currentText()
        }
        
        self.lista_documentos.append(info_doc)
        self.carregar_tabela_doc_nec()

#===============================EDITAR SETORES===============================#

    def carregar_tab_edit_setor(self):
        if self.funcao != "ADMINISTRADOR" and self.funcao != "GERENTE" and self.funcao != "ALMOXARIFADO":
            QtWidgets.QMessageBox.information(self.main, "Aviso", "Você não tem permissão para acessar essa aba.")
            return
        
        self.ui.tabs.setCurrentIndex(5)
        self.listar_setores_edit()
        self.limpar_campos_setor_cadastro()
        
    def listar_setores_edit(self):
        self.ui.box_edit_setor_pesquisa.clear()
        
        try:
            setores = self.db.listar_setores()
            self.ui.box_edit_setor_pesquisa.addItem("Selecione um setor:")
            
            for s in setores:
                self.ui.box_edit_setor_pesquisa.addItem(s["atividade"], s["id_setor"])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao listar setores: {e}")
    
    def listar_novo_doc_edit_setor(self):
        info = {
            "nome": self.ui.edit_edit_setor_novo_doc_nome.text(),
            "tipo": self.ui.edit_edit_setor_novo_doc_tipo.text()
        }
        
        self.lista_documentos.append(info)
        self.carregar_tabela_novo_doc_edit()
    
    def carregar_tabela_novo_doc_edit(self):
        tabela = self.ui.table_edit_setor_novo_doc
        tabela.setRowCount(0)
        
        for item in self.lista_documentos:
            row = tabela.rowCount()
            tabela.insertRow(row)
            
            tabela.setItem(row, 0, QtWidgets.QTableWidgetItem(item["nome"]))
            tabela.setItem(row, 1, QtWidgets.QTableWidgetItem(item["tipo"]))
    
    def buscar_setor(self):
        id_setor = self.ui.box_edit_setor_pesquisa.currentData()
        
        if not id_setor:
            return
        
        try:
            documentos = self.db.buscar_doc_setor(id_setor)
            self.ui.box_edit_setor_doc.clear()
            self.ui.edit_edit_setor_atividade.setText(documentos[0]["atividade"])
            self.ui.edit_edit_setor_criticidade.setText(documentos[0]["criticidade"])
            
            if not documentos:
                return
            
            for d in documentos:
                self.ui.box_edit_setor_doc.addItem(d["nome"], d["id_doc_necessario"])
        
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao carregar informações do setor: {e}")
    
    def remover_doc(self):
        id_documento = self.ui.box_edit_setor_doc.currentData()
        
        if not id_documento:
            return
        
        try:
            self.db.remover_documento(id_documento)
            QtWidgets.QMessageBox.information(self.main, "Sucesso!", "Documento removido com sucesso!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao remover documento: {e}")
    
    def manter_alteracoes_edit_setor(self):
        id_setor = self.ui.box_edit_setor_pesquisa.currentData()
        
        if not id_setor:
            return 
        
        info = (self.ui.edit_edit_setor_atividade.text(), self.ui.edit_edit_setor_criticidade.text(), self.usuario, id_setor)
        
        try:
            self.db.edit_setor(info)
            QtWidgets.QMessageBox.information(self.main, "Informação", "Setor alterado com sucesso!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", "Erro ao editar setor.")
            return
        try:
            for item in self.lista_documentos:
                info_doc = (id_setor, item["nome"], item["tipo"], self.usuario)
                self.db.registrar_documento_necessario(info_doc)
            QtWidgets.QMessageBox.information(self.main, "Sucesso!", "Documentos alterados com sucesso!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao alterar informações do setor: {e}")
            return
        
        self.limpar_campos_edit_setor()
            
    def limpar_campos_edit_setor(self):
        self.ui.box_edit_setor_pesquisa.setCurrentIndex(0)
        self.ui.edit_edit_setor_novo_doc_nome.clear()
        self.ui.edit_edit_setor_novo_doc_tipo.clear()
        self.ui.box_edit_setor_doc.setCurrentIndex(0)
        self.ui.edit_edit_setor_atividade.clear()
        self.ui.edit_edit_setor_criticidade.clear()
        self.lista_documentos.clear()
        self.carregar_tabela_novo_doc_edit()
    
#===============================VINCULAR DOCUMENTO===============================#

    def vincular_documento(self):
        if self.funcao != "ADMINISTRADOR" and self.funcao != "GERENTE" and self.funcao != "ALMOXARIFADO":
            QtWidgets.QMessageBox.information(self.main, "Aviso", "Você não tem permissão para vincular documentos.")
            return
        
        id_fornecedor = self.ui.box_forn_vinculo_forn.currentData()
        id_setor = self.ui.box_forn_vinculo_setor.currentData()
        
        if not id_fornecedor:
            QtWidgets.QMessageBox.warning(self.main, "Atenção!", "Selecione um fornecedor.")
            return

        if not id_setor:
            QtWidgets.QMessageBox.warning(self.main, "Atenção!", "Selecione um setor.")
            return
        
        
        caminho_origem, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.main, "Selecionar documento", "", "Documentos (*.pdf *.jpg *.png *.docx);;Todos (*.*)"
        )
        
        if not caminho_origem:
            return
        
        nome = os.path.basename(caminho_origem)
        tipo = nome.split(".")[-1].upper()
        
        pasta_base = r"C:\Users\Junior.Erivaldo\Documents\dev\python_projects\sis\documentos\fornecedores"
        
        pasta_destino = os.path.join(pasta_base, self.ui.box_forn_vinculo_forn.currentText(), self.ui.box_forn_vinculo_setor.currentText())
        
        os.makedirs(pasta_destino, exist_ok=True)
        
        caminho_destino = os.path.join(pasta_destino, nome)
        
        shutil.copy2(caminho_origem, caminho_destino)
        
        info = (id_setor, id_fornecedor, nome, caminho_destino, tipo, self.usuario)
        try:
            self.db.vincular_documento_fornecedor(info)
            QtWidgets.QMessageBox.information(self.main, "Sucesso!", "Documento vinculado com sucesso!")
            self.carregar_tab_forn()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao vincular documento: {e}")
    
    def listar_fornecedor_vinculo(self):
        self.ui.box_forn_vinculo_forn.clear()
        
        try:
            fornecedores = self.db.listar_fornecedores()
            self.ui.box_forn_vinculo_forn.addItem("Selecione um fornecedor:")
            if not fornecedores:
                QtWidgets.QMessageBox.critical(self.main, "Erro", "Não foram encontrados fornecedores.")
                return
            
            for f in fornecedores:
                self.ui.box_forn_vinculo_forn.addItem(f["nome_empresarial"], f["id_fornecedor"])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao listar fornecedores: {e}")
    
    def listar_setores_vinculo(self):
        self.ui.box_forn_vinculo_setor.clear()
        id_fornecedor = self.ui.box_forn_vinculo_forn.currentData()
        
        try:
            setores = self.db.setor_fornecedor(id_fornecedor)
            self.ui.box_forn_vinculo_setor.addItem("Selecione um setor:")
            if not id_fornecedor:
                return
            if not setores:
                QtWidgets.QMessageBox.critical(self.main, "Erro", "Não foram encontrados setores.")
                return
            
            for f in setores:
                self.ui.box_forn_vinculo_setor.addItem(f["atividade"], f["id_setor"])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao listar setores: {e}")
    