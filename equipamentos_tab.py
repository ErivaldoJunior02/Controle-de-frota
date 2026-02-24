from PyQt5 import QtWidgets, QtCore
import shutil
import os


class EquipamentosTab:
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.db = main.db
        self.usuario = main.id_usuario
        self.ui = main.ui
        self.funcao = main.funcao
        self.itens_abrir_os = []
        self.itens_manutencao = []
        
#===============================EQUIPAMENTOS=============================#

    def carregar_tab_equipamentos(self):
        self.ui.tabs.setCurrentIndex(10)
        self.carregar_tree_equipamentos()
        self.ui.frame_equipamento_edit.setFixedWidth(0)
        self.ui.frame_equipamento_doc.setFixedHeight(0)
        self.ui.date_equipamento_doc_emissao.setDate(QtCore.QDate.currentDate())
        self.ui.date_equipamento_doc_validade.setDate(QtCore.QDate.currentDate())
    
    def toggle_edit(self):
        if self.ui.frame_equipamento_edit.width() == 0:
            if self.ui.tree_equipamento_info.currentItem() is None:
                QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione um equipamento para editar.")
                return
            id_equipamento = self.ui.tree_equipamento_info.currentItem().data(0, QtCore.Qt.UserRole)
            equipamento = self.db.get_equipamento_by_id(id_equipamento)
            self.ui.frame_equipamento_edit.setFixedWidth(380)
            self.ui.edit_equipamento_edit_placa.setText(equipamento["placa"])
            self.ui.box_equipamento_edit_equipamento.setCurrentText(equipamento["equipamento"])
            self.ui.edit_equipamento_edit_modelo.setText(equipamento["modelo"])
            self.ui.edit_equipamento_edit_ano.setText(str(equipamento["ano"]))
            self.ui.edit_equipamento_edit_chassi.setText(equipamento["chassi"])
            self.ui.edit_equipamento_edit_renavam.setText(equipamento["renavam"])
            self.ui.edit_equipamento_edit_regime.setText(equipamento["regime"])
            self.ui.edit_equipamento_edit_km_atual.setText(str(equipamento["km_atual"]))
            self.ui.box_equipamento_edit_status.setCurrentText(equipamento["status_atividade"])
        else:
            self.ui.frame_equipamento_edit.setFixedWidth(0)
    
    def toggle_vinc_doc(self):
        if self.ui.frame_equipamento_doc.height() == 0:
            if self.ui.tree_equipamento_info.currentItem() is None:
                QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione um equipamento para vincular um documento.")
                return
            self.ui.frame_equipamento_doc.setFixedHeight(250)
            id_equipamento = self.ui.tree_equipamento_info.currentItem().data(0, QtCore.Qt.UserRole)
            equipamento = self.db.get_equipamento_by_id(id_equipamento)
            self.ui.edit_equipamento_doc_equipamento.setText(equipamento["placa"])
        else:
            self.ui.frame_equipamento_doc.setFixedHeight(0)
    
    def vincular_doc_equip(self):
        caminho_origem, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.main, "Selecionar documento", "", "Documentos (*.pdf *.jpg *.png *.docx);;Todos (*.*)"
        )
        
        if not caminho_origem:
            return
        
        nome = os.path.basename(caminho_origem)
        tipo = nome.split(".")[-1].upper()
        
        pasta_base = r"C:\Users\Junior.Erivaldo\Documents\dev\python_projects\sis\documentos\equipamentos"
        
        pasta_destino = os.path.join(pasta_base, self.ui.edit_equipamento_doc_equipamento.text())
        
        os.makedirs(pasta_destino, exist_ok=True)
        
        caminho_destino = os.path.join(pasta_destino, nome)
        
        shutil.copy2(caminho_origem, caminho_destino)
        
        id_equipamento = self.ui.tree_equipamento_info.currentItem().data(0, QtCore.Qt.UserRole)
        data_emissao = self.ui.date_equipamento_doc_emissao.date().toString("yyyy-MM-dd")
        data_validade = self.ui.date_equipamento_doc_validade.date().toString("yyyy-MM-dd")
        
        info = (id_equipamento, self.ui.edit_equipamento_doc_nome.text(), data_emissao, data_validade, caminho_destino, self.ui.box_equipamento_doc_tipo.currentText(), self.usuario)
        try:
            self.db.vincular_doc_equipamento(info)
            QtWidgets.QMessageBox.information(self.main, "Sucesso", "Documento vinculado com sucesso!")
            self.carregar_tab_equipamentos()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao vincular documento: {e}")
            return
    
    def carregar_tree_equipamentos(self):
        self.ui.tree_equipamento_info.clear()
        
        equipamentos = self.db.get_all_equipamentos()
        
        equipamento_atual = None
        
        for equip in equipamentos:
            if equipamento_atual != equip["id_veiculo"]:
                equipamento_atual = equip["id_veiculo"]
                
                documentos = self.db.documentos_equipamento(equipamento_atual)
                
                equipamento_item = QtWidgets.QTreeWidgetItem(self.ui.tree_equipamento_info)
                equipamento_item.setText(0, equip["placa"])
                equipamento_item.setData(0, QtCore.Qt.UserRole, equip["id_veiculo"])
                
                dados_item = QtWidgets.QTreeWidgetItem(equipamento_item, ["DADOS DO VEICULO"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Equipamento: {equip["equipamento"]}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Modelo: {equip["modelo"]}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Ano: {equip["ano"]}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Chassi: {equip["chassi"]}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Renavam: {equip["renavam"]}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Regime: {equip["regime"]}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"KM da última revisão: {equip["km_ultima_revisao"]}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"KM atual: {equip["km_atual"]}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Status do veículo: {equip["status_atividade"]}"])

                documentos_root = QtWidgets.QTreeWidgetItem(equipamento_item, ["DOCUMENTOS VINCULADOS"])
                
                for d in documentos:
                    QtWidgets.QTreeWidgetItem(documentos_root, [f"Documento: {d["nome"]} - Validade {d["validade"]}"])
     
    def editar_equipamento(self):
        info = (self.ui.edit_equipamento_edit_placa.text(), self.ui.box_equipamento_edit_equipamento.currentText(), 
                self.ui.edit_equipamento_edit_modelo.text(), self.ui.edit_equipamento_edit_ano.text(), 
                self.ui.edit_equipamento_edit_chassi.text(), self.ui.edit_equipamento_edit_renavam.text(), 
                self.ui.edit_equipamento_edit_regime.text(), self.ui.edit_equipamento_edit_km_atual.text().replace(",", "."), 
                self.ui.box_equipamento_edit_status.currentText(), self.ui.tree_equipamento_info.currentItem().data(0, QtCore.Qt.UserRole)
            )
        
        try:
            self.db.edit_equipamento(info)
            QtWidgets.QMessageBox.information(self.main, "Sucesso", "Alteração realizada com sucesso")
            self.toggle_edit()
            self.carregar_tree_equipamentos()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao alterar informações: {e}")
            return
    
    def filtrar_equipamento(self):
        termo = self.ui.edit_equipamento_filtro.text()
        
        if not termo:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Digite a informação que deseja buscar.")
            self.carregar_tree_equipamentos()
            return
        
        self.ui.tree_equipamento_info.clear()
        
        equipamentos = self.db.filtrar_equipamento(termo)
        
        equipamento_atual = None
        
        for equip in equipamentos:
            if equipamento_atual != equip["id_veiculo"]:
                equipamento_atual = equip["id_veiculo"]
                
                documentos = self.db.documentos_equipamento(equipamento_atual)
                
                equipamento_item = QtWidgets.QTreeWidgetItem(self.ui.tree_equipamento_info)
                equipamento_item.setText(0, equip["placa"])
                equipamento_item.setData(0, QtCore.Qt.UserRole, equip["id_veiculo"])
                
                dados_item = QtWidgets.QTreeWidgetItem(equipamento_item, ["DADOS DO VEICULO"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Equipamento: {equip["equipamento"]}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Modelo: {equip["modelo"]}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Ano: {equip["ano"]}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Chassi: {equip["chassi"]}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Renavam: {equip["renavam"]}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Regime: {equip["regime"]}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"KM da última revisão: {equip["km_ultima_revisao"]}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"KM atual: {equip["km_atual"]}"])
                QtWidgets.QTreeWidgetItem(dados_item, [f"Status do veículo: {equip["status_atividade"]}"])

                documentos_root = QtWidgets.QTreeWidgetItem(equipamento_item, ["DOCUMENTOS VINCULADOS"])
                
                for d in documentos:
                    QtWidgets.QTreeWidgetItem(documentos_root, [f"Documento: {d["nome"]} - Validade {d["validade"]}"])
    
    def limpar_campos_edit(self):
            self.ui.edit_equipamento_edit_placa.clear()
            self.ui.box_equipamento_edit_equipamento.setCurrentIndex(0)
            self.ui.edit_equipamento_edit_modelo.clear()
            self.ui.edit_equipamento_edit_ano.clear()
            self.ui.edit_equipamento_edit_chassi.clear()
            self.ui.edit_equipamento_edit_renavam.clear()
            self.ui.edit_equipamento_edit_regime.clear()
            self.ui.edit_equipamento_edit_km_atual.clear()
            self.ui.box_equipamento_edit_status.setCurrentIndex(0)
            self.ui.frame_equipamento_edit.setFixedWidth(0)
    
#===============================CADASTRO EQUIPAMENTOS=============================#

    def carregar_tab_cadastro_equipamento(self):
        self.ui.tabs.setCurrentIndex(11)
        self.limpar_campos_cadastro()
    
    def cadastrar_equipamento(self):
        info = (self.ui.edit_cadastro_equipamento_placa.text(), self.ui.box_cadastro_equipamento_equipamento.currentText(), self.ui.edit_cadastro_equipamento_modelo.text(),
                self.ui.edit_cadastro_equipamento_ano.text(), self.ui.edit_cadastro_equipamento_km_atual.text(), self.ui.edit_cadastro_equipamento_chassi.text(),
                self.ui.edit_cadastro_equipamento_renavam.text(), self.ui.edit_cadastro_equipamento_regime.text(), self.ui.box_cadastro_equipamento_status.currentText(),
                self.ui.edit_cadastro_equipamento_km_ultima_revisao.text(), self.usuario)
        
        try:
            self.db.cadastrar_equipamento(info)
            QtWidgets.QMessageBox.information(self.main, "Sucesso", "Veículo cadastrado com sucesso!")
            self.limpar_campos_cadastro()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao cadastrar equipamento: {e}")
            return
    
    def limpar_campos_cadastro(self):
        self.ui.edit_cadastro_equipamento_placa.clear()
        self.ui.box_cadastro_equipamento_equipamento.setCurrentIndex(0)
        self.ui.edit_cadastro_equipamento_modelo.clear()
        self.ui.edit_cadastro_equipamento_ano.clear()
        self.ui.edit_cadastro_equipamento_km_atual.clear()
        self.ui.edit_cadastro_equipamento_chassi.clear()
        self.ui.edit_cadastro_equipamento_renavam.clear()
        self.ui.edit_cadastro_equipamento_regime.clear()
        self.ui.box_cadastro_equipamento_status.setCurrentIndex(0)
        self.ui.edit_cadastro_equipamento_km_ultima_revisao.clear()
    
#===============================ORDENS DE SERVIÇO=============================#

    def carregar_tab_os(self):
        self.ui.tabs.setCurrentIndex(12)
        self.ui.frame_os_edit.setFixedHeight(0)
        self.ui.frame_itens_edit.setFixedWidth(0)
        self.ui.frame_os_status.setFixedHeight(0)
        self.carregar_tree_os()
    
    def toggle_edit_os(self):
        if self.ui.frame_os_edit.height() == 0:
            if self.ui.tree_os_info.currentItem() is None:
                QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione uma OS para editar.")
                return
            self.ui.frame_os_edit.setFixedHeight(350)
            id_os = self.ui.tree_os_info.currentItem().data(0, QtCore.Qt.UserRole)
            os = self.db.get_os_by_id(id_os)
            veiculos = self.db.get_all_equipamentos()
            self.ui.box_os_edit_equipamento.clear()
            self.ui.box_os_edit_equipamento.addItem("Selecione um veículo")
            for veiculo in veiculos:
                self.ui.box_os_edit_equipamento.addItem(veiculo["placa"], veiculo["id_veiculo"])
            self.ui.edit_os_edit_numero.setText(os["numero_os"])
            self.ui.box_os_edit_equipamento.setCurrentText(os["placa"])
            self.ui.edit_os_edit_inspetor.setText(os["responsavel"])
            self.ui.box_os_edit_tipo.setCurrentText(os["tipo"])
            self.ui.date_os_edit_data_inicio.setDate(os["data_saida"])
            self.ui.date_os_edit_data_termino.setDate(os["data_previsao"])
            self.ui.txt_os_edit_descricao.setText(os["descricao"])
            self.ui.edit_os_edit_local.setText(os["local_manutencao"])
            self.ui.edit_os_edit_km_atual.setText(str(os["km_atual"]))
            self.ui.box_os_edit_oficina.setCurrentText(os["oficina"])
            self.ui.edit_os_edit_custo.setText(str(os["custo"]))
            self.ui.box_os_edit_status.setCurrentText(os["status_os"])            
        else:
            self.ui.frame_os_edit.setFixedHeight(0)
    
    def toggle_itens_os_edit(self):
        if self.ui.frame_itens_edit.width() == 0:
            if self.ui.tree_os_info.currentItem() is None:
                QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione uma OS para editar itens.")
                return
            self.ui.frame_itens_edit.setFixedWidth(650)
            id_os = self.ui.tree_os_info.currentItem().data(0, QtCore.Qt.UserRole)
            itens = self.db.busca_itens_os(id_os)
            itens_os = []
            for item in itens:
                info = {
                    "item_id": item["id_item"],
                    "item": item["nome"],
                    "codigo": item["codigo_interno"],
                    "medida": item["unidade_medida"],
                    "quantidade": item["quantidade"],
                    "status": item["status_item"]
                }
                
                itens_os.append(info)
            
            tabela = self.ui.table_itens_os
            tabela.setRowCount(0)
            
            for item in itens_os:
                row = tabela.rowCount()
                tabela.insertRow(row)
                
                tabela.setItem(row, 0, QtWidgets.QTableWidgetItem(str(item["item_id"])))
                tabela.setItem(row, 1, QtWidgets.QTableWidgetItem(item["item"]))
                tabela.setItem(row, 2, QtWidgets.QTableWidgetItem(item["codigo"]))
                tabela.setItem(row, 3, QtWidgets.QTableWidgetItem(item["medida"]))
                tabela.setItem(row, 4, QtWidgets.QTableWidgetItem(str(item["quantidade"])))
                tabela.setItem(row, 5, QtWidgets.QTableWidgetItem(item["status"]))
            
            novos_itens = self.db.listar_itens()
            
            self.ui.box_itens_edit_novo_item.clear()
            self.ui.box_itens_edit_novo_item.addItem("Selecione um item:")
            
            for item in novos_itens:
                self.ui.box_itens_edit_novo_item.addItem(item["nome"], item["id_item"])
        else:
            self.ui.frame_itens_edit.setFixedWidth(0)
    
    def carregar_tree_os(self):
        self.ui.tree_os_info.clear()
        
        ordens = self.db.get_all_ordens()
        
        ordem_atual = None
        
        for ordem in ordens:
            if ordem_atual != ordem["id_os"]:
                ordem_atual = ordem["id_os"]
                
                itens = self.db.busca_itens_os(ordem["id_os"])
                manutencoes = self.db.get_manutencoes_os(ordem["id_os"])
                
                os_item = QtWidgets.QTreeWidgetItem(self.ui.tree_os_info)
                os_item.setText(0, f"OS: {ordem["numero_os"]} - Status: {ordem["status_os"]}")
                os_item.setData(0, QtCore.Qt.UserRole, ordem["id_os"])
                
                dados_os = QtWidgets.QTreeWidgetItem(os_item, ["DADOS DA ORDEM DE SERVIÇO"])
                QtWidgets.QTreeWidgetItem(dados_os, [f"Equipamento: {ordem["placa"]}"])
                QtWidgets.QTreeWidgetItem(dados_os, [f"Local da manutenção: {ordem["local_manutencao"]}"])
                QtWidgets.QTreeWidgetItem(dados_os, [f"KM registrado: {str(ordem["km_atual"])}"])
                QtWidgets.QTreeWidgetItem(dados_os, [f"Tipo de mantuenção: {ordem["tipo"]}"])
                QtWidgets.QTreeWidgetItem(dados_os, [f"Oficina: {ordem["oficina"]}"])
                QtWidgets.QTreeWidgetItem(dados_os, [f"Inspetor: {ordem["responsavel"]}"])
                QtWidgets.QTreeWidgetItem(dados_os, [f"Data de saída da Op.: {str(ordem["data_saida"])}"])
                QtWidgets.QTreeWidgetItem(dados_os, [f"Data prevista para finalizar: {str(ordem["data_previsao"])}"])
                QtWidgets.QTreeWidgetItem(dados_os, [f"Data de finalização definitiva: {str(ordem["data_retorno"])}"])
                QtWidgets.QTreeWidgetItem(dados_os, [f"Custo total previsto: R${str(ordem["custo"])}"])
                QtWidgets.QTreeWidgetItem(dados_os, [f"Status da ordem: {ordem["status_os"]}"])
                QtWidgets.QTreeWidgetItem(dados_os, [f"Descrição: {ordem["descricao"]}"])
                
                itens_os = QtWidgets.QTreeWidgetItem(os_item, ["ITENS NECESSÁRIOS"])
                
                for item in itens:
                    QtWidgets.QTreeWidgetItem(itens_os, [f"Item: {item["nome"]} - Quantidade: {item["quantidade"]} - Status: {item["status_item"]}"])
                
                manutencao_os = QtWidgets.QTreeWidgetItem(os_item, ["MANUTENÇÕES REALIZADAS"])
                
                for manutencao in manutencoes:
                    manutencoes_info = QtWidgets.QTreeWidgetItem(manutencao_os, [f"Serviço: {manutencao["servico"]}"])
                    QtWidgets.QTreeWidgetItem(manutencoes_info, [f"Data de início: {manutencao["data_inicio"]}"])
                    QtWidgets.QTreeWidgetItem(manutencoes_info, [f"Data de finalização: {manutencao["data_fim"]}"])
                    QtWidgets.QTreeWidgetItem(manutencoes_info, [f"Custo total: {manutencao["custo_total"]}"])
                    
                    
                    itens = self.db.itens_manutencao(manutencao["id_manutencao"])
                    
                    itens_manutencao = QtWidgets.QTreeWidgetItem(manutencoes_info, ["ITENS UTILIZADOS"])
                    
                    for item in itens:
                        QtWidgets.QTreeWidgetItem(itens_manutencao, [f"Item: {item["nome"]}"])
                        QtWidgets.QTreeWidgetItem(itens_manutencao, [f"Quantidade utilizada: {item["quantidade"]}"])
                        QtWidgets.QTreeWidgetItem(itens_manutencao, [f"Valor do item: {item["valor_unitario"]}"])
                        QtWidgets.QTreeWidgetItem(itens_manutencao, [f"Valor total: {item["valor_total"]}"])
                
    def editar_os(self):
        info = (self.ui.edit_os_edit_numero.text(), self.ui.box_os_edit_equipamento.currentData(), self.ui.edit_os_edit_inspetor.text(),
            self.ui.box_os_edit_tipo.currentText(), self.ui.date_os_edit_data_inicio.dateTime().toString("yyyy-MM-dd HH:mm:ss"), self.ui.date_os_edit_data_termino.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            self.ui.txt_os_edit_descricao.toPlainText(), self.ui.edit_os_edit_local.text(), self.ui.edit_os_edit_km_atual.text().replace(",", "."),
            self.ui.box_os_edit_oficina.currentText(), self.ui.edit_os_edit_custo.text().replace(",", "."), self.ui.box_os_edit_status.currentText(), self.usuario, self.ui.tree_os_info.currentItem().data(0, QtCore.Qt.UserRole)
        )
        try:
            self.db.editar_os(info)
            QtWidgets.QMessageBox.information(self.main, "Sucesso", "OS alterada com sucesso!")
            self.carregar_tree_os()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao alterar OS: {e}")
            return

    def nova_qntd_itens_edit(self):
        row = self.ui.table_itens_os.currentRow()
        
        if row >= 0:
            id_item = self.ui.table_itens_os.item(row, 0).text()
            id_item = int(id_item)
            
            info = (self.ui.edit_itens_edit_nova_qntd.text(), id_item)
            try:
                self.db.edit_qntd_itens_os(info)
                QtWidgets.QMessageBox.information(self.main, "Sucesso", "Quantidade alterada com sucesso!")
                self.toggle_itens_os_edit()
                self.toggle_itens_os_edit()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao alterar quantidade: {e}")
                return
        else:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione um item para alterar quantidade.")
            return

    def novo_item_os(self):
        id_item = self.ui.box_itens_edit_novo_item.currentData()
        item = self.db.get_item_by_id(id_item)
        if item:
            quantidade = float(self.ui.edit_itens_edit_quantidade.text() or 0)
            valor_total = float(item["ultimo_preco"]) * quantidade
        else:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Item não encontrado")
            return
        info = (self.ui.tree_os_info.currentItem().data(0, QtCore.Qt.UserRole), self.ui.box_itens_edit_novo_item.currentData(), self.ui.edit_itens_edit_quantidade.text(),
                item["ultimo_preco"], valor_total, "NAO_UTILIZADO")
        
        try:
            self.db.add_novo_item_os(info)
            QtWidgets.QMessageBox.information(self.main, "Sucesso", "Sucesso ao adicionar novo item.")
            custo = (valor_total, self.ui.tree_os_info.currentItem().data(0, QtCore.Qt.UserRole))
            self.db.update_custo_os(custo)
            self.toggle_itens_os_edit()
            self.toggle_itens_os_edit()
            self.carregar_tree_os()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao registrar novo item a OS: {e}")
            return
    
    def remover_item_os(self):
        row = self.ui.table_itens_os.currentRow()
        
        if row >= 0:
            id_item = self.ui.table_itens_os.item(row, 0).text()
            id_item = int(id_item)
            
            item = self.db.get_item_by_id(id_item)
            
            if item:
                quantidade = float(self.ui.table_itens_os.item(row, 4).text() or 0)
                valor_total = float(item["ultimo_preco"]) * quantidade
            else:
                QtWidgets.QMessageBox.warning(self.main, "Atenção", "Item não encontrado")
                return
            
            try:
                custo = (valor_total, self.ui.tree_os_info.currentItem().data(0, QtCore.Qt.UserRole))
                self.db.update_custo_remover_os(custo)
                self.db.remover_item_os(id_item)
                QtWidgets.QMessageBox.information(self.main, "Sucesso", "Item removido com sucesso")
                self.toggle_itens_os_edit()
                self.toggle_itens_os_edit()
                self.carregar_tree_os()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao remover item: {e}")
                return
    
    def limpar_campos_edit_os(self):
        self.ui.edit_os_edit_numero.clear()
        self.ui.box_os_edit_equipamento.setCurrentIndex(0) 
        self.ui.edit_os_edit_inspetor.clear()
        self.ui.box_os_edit_tipo.setCurrentIndex(0)
        self.ui.date_os_edit_data_inicio.setDate(QtCore.QDate.currentDate())
        self.ui.date_os_edit_data_termino.setDate(QtCore.QDate.currentDate())
        self.ui.txt_os_edit_descricao.clear()
        self.ui.edit_os_edit_local.clear()
        self.ui.edit_os_edit_km_atual.clear()
        self.ui.box_os_edit_oficina.setCurrentIndex(0)
        self.ui.edit_os_edit_custo.clear() 
        self.ui.box_os_edit_status.setCurrentIndex(0)
        self.ui.frame_os_edit.setFixedHeigth(0)

    def toggle_os_status(self):
        if self.ui.frame_os_status.height() == 0:
            self.ui.frame_os_status.setFixedHeight(40)

    def set_ordem_aberta(self):
        id_os = self.ui.tree_os_info.currentItem().data(0, QtCore.Qt.UserRole)
        self.db.set_os_aberta(id_os)
        self.carregar_tree_os()

    def set_ordem_em_execucao(self):
        id_os = self.ui.tree_os_info.currentItem().data(0, QtCore.Qt.UserRole)
        self.db.set_os_em_execucao(id_os)
        self.carregar_tree_os()
        
    def set_ordem_finalizada(self):
        id_os = self.ui.tree_os_info.currentItem().data(0, QtCore.Qt.UserRole)
        self.db.set_os_finalizada(id_os)
        self.carregar_tree_os()
        
    def set_ordem_cancelada(self):
        id_os = self.ui.tree_os_info.currentItem().data(0, QtCore.Qt.UserRole)
        self.db.set_os_cancelada(id_os)
        self.carregar_tree_os()
        
#===============================ABRIR ORDENS DE SERVIÇO=============================#
    
    def carregar_tab_abrir_os(self):
        self.ui.tabs.setCurrentIndex(13)
        self.ui.date_abrir_os_data_saida.setDate(QtCore.QDate.currentDate())
        self.ui.date_abrir_os_data_previsao.setDate(QtCore.QDate.currentDate())
        
        veiculos = self.db.listar_veiculos()
        self.ui.box_abrir_os_equipamento.clear()
        self.ui.box_abrir_os_equipamento.addItem("Selecione um equipamento:")
        
        for veiculo in veiculos:
            self.ui.box_abrir_os_equipamento.addItem(veiculo["placa"], veiculo["id_veiculo"])
        
        itens = self.db.listar_itens()
        
        self.ui.box_abrir_os_itens_item.clear()
        self.ui.box_abrir_os_itens_item.addItem("Selecione um item:")
        
        for item in itens:
            self.ui.box_abrir_os_itens_item.addItem(item["nome"], item["id_item"])
        
    def carregar_table_abrir_os_itens(self):
        tabela = self.ui.table_abrir_os_itens
        tabela.setRowCount(0)
        
        for item in self.itens_abrir_os:
            row = tabela.rowCount()
            tabela.insertRow(row)
            
            tabela.setItem(row, 0, QtWidgets.QTableWidgetItem(str(item["id_item"])))
            tabela.setItem(row, 1, QtWidgets.QTableWidgetItem(item["item"]))
            tabela.setItem(row, 2, QtWidgets.QTableWidgetItem(item["codigo"]))
            tabela.setItem(row, 3, QtWidgets.QTableWidgetItem(item["medida"]))
            tabela.setItem(row, 4, QtWidgets.QTableWidgetItem(item["quantidade"]))
            tabela.setItem(row, 5, QtWidgets.QTableWidgetItem(item["status"]))
    
    def listar_itens_abrir_os(self):
        id_item = self.ui.box_abrir_os_itens_item.currentData()
        item = self.db.get_item_by_id(id_item)
        
        info = {
            "id_item": self.ui.box_abrir_os_itens_item.currentData(),
            "item": self.ui.box_abrir_os_itens_item.currentText(),
            "codigo": item["codigo_interno"],
            "medida": item["unidade_medida"],
            "quantidade": self.ui.edit_abrir_os_itens_qntd.text(),
            "valor_unitario": self.ui.edit_abrir_os_itens_valor_unitario.text().replace(",", "."),
            "status": "NAO_UTILIZADO"
        }
        
        self.itens_abrir_os.append(info)
        custo_total = 0
        for item in self.itens_abrir_os:
            custo_total += float(item["quantidade"]) * float(item["valor_unitario"])
        self.ui.edit_abrir_os_custo.setText(str(custo_total))
        self.carregar_table_abrir_os_itens()

    def registrar_os(self):
        info_os = (self.ui.edit_abrir_os_numero.text(), self.ui.box_abrir_os_equipamento.currentData(), self.ui.edit_abrir_os_local.text(),
                   self.ui.edit_abrir_os_km_atual.text(), self.ui.box_abrir_os_tipo.currentText(), self.ui.box_abrir_os_oficina.currentText(),
                   self.ui.edit_abrir_os_inspetor.text(), self.ui.date_abrir_os_data_saida.dateTime().toString("yyyy-MM-dd HH:mm:ss"), self.ui.date_abrir_os_data_previsao.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
                   self.ui.edit_abrir_os_custo.text(), self.ui.box_abrir_os_status.currentText(), self.ui.txt_abrir_os_descricao.toPlainText(), self.usuario)
        
        try:
            id_os = self.db.registrar_os(info_os)
            try:
                for item in self.itens_abrir_os:
                    self.db.registrar_itens_os(id_os, item)
                QtWidgets.QMessageBox.information(self.main, "Sucesso", "Itens cadastrados com sucesso!")
                self.limpar_campos_abrir_os()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao cadastrar itens: {e}")
                return
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao registrar OS: {e}")
            return
    
    def limpar_campos_abrir_os_itens(self):
        self.itens_abrir_os.clear()
        self.ui.box_abrir_os_itens_item.setCurrentIndex(0)
        self.ui.edit_abrir_os_itens_qntd.clear()
        self.ui.edit_abrir_os_itens_valor_unitario.clear()
        self.carregar_table_abrir_os_itens()
    
    def limpar_campos_abrir_os(self):
        self.ui.edit_abrir_os_numero.clear()
        self.ui.box_abrir_os_equipamento.setCurrentIndex(0)
        self.ui.edit_abrir_os_local.clear()
        self.ui.edit_abrir_os_km_atual.clear()
        self.ui.box_abrir_os_tipo.setCurrentIndex(0)
        self.ui.box_abrir_os_oficina.setCurrentIndex(0)
        self.ui.edit_abrir_os_inspetor.clear()
        self.ui.date_abrir_os_data_saida.setDate(QtCore.QDate.currentDate())
        self.ui.date_abrir_os_data_previsao.setDate(QtCore.QDate.currentDate())
        self.ui.edit_abrir_os_custo.clear()
        self.ui.box_abrir_os_status.setCurrentIndex(0)
        self.ui.txt_abrir_os_descricao.clear()
        self.limpar_campos_abrir_os_itens()
    
    def buscar_preco_item(self):
        if self.ui.box_abrir_os_itens_item.currentData() == None:
            return
        
        item = self.db.get_item_by_id(self.ui.box_abrir_os_itens_item.currentData())
        
        self.ui.edit_abrir_os_itens_valor_unitario.setText(str(item["ultimo_preco"]))
        
#===============================REGISTRO MANUTENÇÃO=============================#        

    def carregar_tab_registro_manutencao(self):
        self.ui.tabs.setCurrentIndex(14)
        self.ui.date_registro_manutencao_data_inicio.setDate(QtCore.QDate.currentDate())
        self.ui.date_registro_manutencao_data_fim.setDate(QtCore.QDate.currentDate())
        
        os = self.db.listar_os()
        self.ui.box_registro_manutencao_os.clear()
        self.ui.box_registro_manutencao_os.addItem("Selecione a OS de referência:")
        
        for item in os:
            self.ui.box_registro_manutencao_os.addItem(item["numero_os"], item["id_os"])
            
        self.carregar_box_itens_manutencao()
        
    def carregar_box_itens_manutencao(self):
        id_os = self.ui.box_registro_manutencao_os.currentData()
        
        if not id_os:
            return
        
        itens = self.db.listar_itens_os(id_os)
        self.ui.box_registro_manutencao_itens_item.clear()
        self.ui.box_registro_manutencao_itens_item.addItem("Selecione um item:")
        
        for item in itens:
            self.ui.box_registro_manutencao_itens_item.addItem(item["nome"], item["id_item"])
    
    def detalhes_itens_manutencao(self):
        id_item = self.ui.box_registro_manutencao_itens_item.currentData()
        
        if not id_item:
            return
        
        item = self.db.item_os(id_item)
        
        self.ui.edit_registro_manutencao_itens_qntd.setText(str(item["quantidade_previsao"]))
        self.ui.edit_registro_manutencao_itens_valor_unitario.setText(str(item["valor_unitario_previsto"]))
    
    def listar_itens_manutencao(self):
        info_itens = {
            "id_item": self.ui.box_registro_manutencao_itens_item.currentData(),
            "item": self.ui.box_registro_manutencao_itens_item.currentText(),
            "quantidade": self.ui.edit_registro_manutencao_itens_qntd.text(),
            "valor_unitario": self.ui.edit_registro_manutencao_itens_valor_unitario.text(),
            "status_item": "UTILIZADO"
        }
        
        self.itens_manutencao.append(info_itens)
        self.carregar_table_itens_manutencao()
    
    def carregar_table_itens_manutencao(self):
        valor_total = float(0)
        self.ui.table_registro_manutencao_itens.setRowCount(0)
        
        for item in self.itens_manutencao:
            row = self.ui.table_registro_manutencao_itens.rowCount()
            self.ui.table_registro_manutencao_itens.insertRow(row)
            
            self.ui.table_registro_manutencao_itens.setItem(row, 0, QtWidgets.QTableWidgetItem(str(item["id_item"])))
            self.ui.table_registro_manutencao_itens.setItem(row, 1, QtWidgets.QTableWidgetItem(str(item["item"])))
            self.ui.table_registro_manutencao_itens.setItem(row, 2, QtWidgets.QTableWidgetItem(str(item["quantidade"])))
            self.ui.table_registro_manutencao_itens.setItem(row, 3, QtWidgets.QTableWidgetItem(str(item["valor_unitario"])))
            self.ui.table_registro_manutencao_itens.setItem(row, 4, QtWidgets.QTableWidgetItem(str(float(item["quantidade"]) * float(item["valor_unitario"]))))
            valor_total += float(item["quantidade"]) * float(item["valor_unitario"])
        
        self.ui.edit_registro_manutencao_custo_total.setText(str(valor_total))
        
    def registrar_manutencao(self):
        info_manutencao = (self.ui.edit_registro_manutencao_servico.text(), self.ui.box_registro_manutencao_os.currentData(), self.ui.date_registro_manutencao_data_inicio.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
                           self.ui.date_registro_manutencao_data_fim.dateTime().toString("yyyy-MM-dd HH:mm:ss"), self.ui.edit_registro_manutencao_custo_total.text())
        try:
            id_manutencao = self.db.registrar_manutencao(info_manutencao)
            try:
                for item in self.itens_manutencao:
                    self.db.registrar_itens_manutencao(id_manutencao, item)
                QtWidgets.QMessageBox.information(self.main, "Sucesso", "Itens adicionados com sucesso!")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao adicionar itens da manutenção: {e}")
                return
            QtWidgets.QMessageBox.information(self.main, "Sucesso", "Manutenção registrada com sucesso!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao registrar manutenção: {e}")
            return
    
    def limpar_campos_itens_manutencao(self):
        self.itens_manutencao.clear()
        self.ui.box_registro_manutencao_itens_item.setCurrentIndex(0)
        self.ui.edit_registro_manutencao_itens_qntd.clear()
        self.ui.edit_registro_manutencao_itens_valor_unitario.clear()
        self.carregar_table_itens_manutencao()
    
    def limpar_campos_manutencao(self):
        self.limpar_campos_itens_manutencao()
        self.ui.edit_registro_manutencao_servico.clear()
        self.ui.box_registro_manutencao_os.setCurrentIndex(0)
        self.ui.date_registro_manutencao_data_inicio.setDate(QtCore.QDate.currentDate())
        self.ui.date_registro_manutencao_data_fim.setDate(QtCore.QDate.currentDate())
        
                           