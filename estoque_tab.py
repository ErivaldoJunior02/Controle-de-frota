from PyQt5 import QtWidgets, QtCore

class EstoqueTab:
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.ui = main.ui
        self.db = main.db
        self.usuario = main.id_usuario
        self.funcao = main.funcao
        self.itens_compra = []
        self.itens_movimentacao = []
        self.itens_criticos = []
        self.item_verificado = 0
        
#===============================ESTOQUE=============================#

    def carregar_tab_estoque(self):
        self.ui.tabs.setCurrentIndex(6)
        self.ui.frame_estoque_edit.setFixedHeight(0)
        self.ui.date_estoque_movimentacoes_periodo_inicio.setDate(QtCore.QDate.currentDate())
        self.ui.date_estoque_movimentacoes_periodo_fim.setDate(QtCore.QDate.currentDate())
        self.carregar_table_estoque()
        self.carregar_tree_movimentacoes()
        self.verificar_estoque()

    def carregar_table_estoque(self):
        itens = self.db.get_itens_estoque()
        tabela = self.ui.table_estoque_itens
        tabela.setRowCount(0)

        for item in itens:
            row = tabela.rowCount()
            tabela.insertRow(row)

            tabela.setItem(row, 0, QtWidgets.QTableWidgetItem(str(item["id_item"])))
            tabela.setItem(row, 1, QtWidgets.QTableWidgetItem(item["nome"]))
            tabela.setItem(row, 2, QtWidgets.QTableWidgetItem(item["codigo_interno"]))
            tabela.setItem(row, 3, QtWidgets.QTableWidgetItem(item["unidade_medida"]))
            tabela.setItem(row, 4, QtWidgets.QTableWidgetItem(str(item["quantidade_atual"])))
            tabela.setItem(row, 5, QtWidgets.QTableWidgetItem(str(item["quantidade_minima"])))

    def filtrar_estoque(self):
        if self.ui.edit_estoque_itens_filtro.text() == "":
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Digite o item que deseja filtrar.")
            self.carregar_table_estoque()
            return
        
        termo = self.ui.edit_estoque_itens_filtro.text()
        tabela = self.ui.table_estoque_itens
        tabela.setRowCount(0)
        
        itens = self.db.filtrar_estoque(termo)
        
        for item in itens:
            row = tabela.rowCount()
            tabela.insertRow(row)
            
            tabela.setItem(row, 0, QtWidgets.QTableWidgetItem(str(item["id_item"])))
            tabela.setItem(row, 1, QtWidgets.QTableWidgetItem(item["nome"]))
            tabela.setItem(row, 2, QtWidgets.QTableWidgetItem(item["codigo_interno"]))
            tabela.setItem(row, 3, QtWidgets.QTableWidgetItem(item["unidade_medida"]))
            tabela.setItem(row, 4, QtWidgets.QTableWidgetItem(str(item["quantidade_atual"])))
            tabela.setItem(row, 5, QtWidgets.QTableWidgetItem(str(item["quantidade_minima"])))
            
    def carregar_tree_movimentacoes(self):
        dados = self.db.get_all_movimentacoes()
        
        self.ui.tree_estoque_movimentacoes.clear()
        
        mov_atual = None
        
        for row in dados:
            if mov_atual != row["id_movimentacao"]:
                mov_atual = row["id_movimentacao"]
                
                movimentacao = QtWidgets.QTreeWidgetItem(self.ui.tree_estoque_movimentacoes, [f"{row["tipo"]} - Data: {row["register_at"]}"])
                movimentacao.setData(0, QtCore.Qt.UserRole, mov_atual)
                
                QtWidgets.QTreeWidgetItem(movimentacao, [f"Origem: {row["origem"]}"])
                QtWidgets.QTreeWidgetItem(movimentacao, [f"Destino: {row["destino"]}"])
                QtWidgets.QTreeWidgetItem(movimentacao, [f"Solicitante: {row["solicitante"]}"])
                
                itens_usados = QtWidgets.QTreeWidgetItem(movimentacao, ["ITENS MOVIMENTADOS"])
            QtWidgets.QTreeWidgetItem(itens_usados, [f"Item: {row["nome"]} - Quantidade: {row["quantidade"]}"])
            
    def filtro_movimentacoes(self):
        if self.ui.edit_movimentacoes_filtro.text() == "":
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Digite o tipo de movimentação que deseja filtrar.")
            self.carregar_tree_movimentacoes()
            return
        
        termo = self.ui.edit_movimentacoes_filtro.text()
        
        dados = self.db.filtrar_movimentacoes(termo)
        
        mov_atual = None
        self.ui.tree_estoque_movimentacoes.clear()
        
        for row in dados:
            if mov_atual != row["id_movimentacao"]:
                mov_atual = row["id_movimentacao"]
                
                movimentacao = QtWidgets.QTreeWidgetItem(self.ui.tree_estoque_movimentacoes, [f"{row["tipo"]} - {row["register_at"]}"])
                movimentacao.setData(0, QtCore.Qt.UserRole, mov_atual)
                
                QtWidgets.QTreeWidgetItem(movimentacao, [f"Origem: {row["origem"]}"])
                QtWidgets.QTreeWidgetItem(movimentacao, [f"Destino: {row["destino"]}"])
                QtWidgets.QTreeWidgetItem(movimentacao, [f"Solicitante: {row["solicitante"]}"])
                QtWidgets.QTreeWidgetItem(movimentacao, [f"Data da movimentação: {row["register_at"]}"])
                
                itens_usados = QtWidgets.QTreeWidgetItem(movimentacao, ["ITENS MOVIMENTADOS"])
            QtWidgets.QTreeWidgetItem(itens_usados, [f"Item: {row["nome"]} - Quantidade: {row["quantidade"]}"])
    
    def filtro_movimentacoes_periodo(self):
        data_1 = self.ui.date_estoque_movimentacoes_periodo_inicio.date().toString("yyyy-MM-dd")
        data_2 = self.ui.date_estoque_movimentacoes_periodo_fim.date().toString("yyyy-MM-dd")
        
        if data_1 > data_2:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione um período válido.")
            return
        
        dados = self.db.filtrar_movimentacoes_periodo(data_1, data_2)
        
        self.ui.tree_estoque_movimentacoes.clear()
        
        mov_atual = None
        
        for row in dados:
            if mov_atual != row["id_movimentacao"]:
                mov_atual = row["id_movimentacao"]
                
                movimentacao = QtWidgets.QTreeWidgetItem(self.ui.tree_estoque_movimentacoes, [f"{row["tipo"]} - {row["register_at"]}"])
                movimentacao.setData(0, QtCore.Qt.UserRole, mov_atual)
                
                QtWidgets.QTreeWidgetItem(movimentacao, [f"Origem: {row["origem"]}"])
                QtWidgets.QTreeWidgetItem(movimentacao, [f"Destino: {row["destino"]}"])
                QtWidgets.QTreeWidgetItem(movimentacao, [f"Solicitante: {row["solicitante"]}"])
                QtWidgets.QTreeWidgetItem(movimentacao, [f"Data da movimentação: {row["register_at"]}"])
                
                itens_usados = QtWidgets.QTreeWidgetItem(movimentacao, ["ITENS MOVIMENTADOS"])
            QtWidgets.QTreeWidgetItem(itens_usados, [f"Item: {row["nome"]} - Quantidade: {row["quantidade"]}"])    
    
    def verificar_estoque(self):
        itens_criticos = self.db.verificar_itens_criticos()
        
        if self.item_verificado != 0:
            return
        
        for item in itens_criticos:
            info = {
                "id_item": item["id_item"],
                "item": item["nome"],
                "quantidade_atual": item["quantidade_atual"],
                "quantidade_minima": item["quantidade_minima"],
                "quantidade": item["quantidade_minima"] - item["quantidade_atual"],
                "valor_unitario": item["ultimo_preco"]
            }
            
            self.itens_criticos.append(info)
            self.itens_compra.append(info)
        
        if not self.itens_criticos:
            return
        
        mensagem = "Os seguintes itens estão em estado de alerta:\n\n"
        
        for item in self.itens_criticos:
            mensagem += f"Item: {item["item"]} - Quantidade atual: {item["quantidade"]} Quantidade mínima: {item["quantidade_minima"]}\n"
        
        QtWidgets.QMessageBox.warning(self.main, "Itens críticos", mensagem)
        
        self.carregar_tab_compras()

        tabela = self.ui.table_compras_itens
        tabela.setRowCount(0)
        
        for item in self.itens_criticos:
            row = tabela.rowCount()
            tabela.insertRow(row)
            
            tabela.setItem(row, 0, QtWidgets.QTableWidgetItem(item["item"]))
            tabela.setItem(row, 1, QtWidgets.QTableWidgetItem(str(item["quantidade_minima"] - item["quantidade_atual"])))
            tabela.setItem(row, 2, QtWidgets.QTableWidgetItem(f"R${item["valor_unitario"]:.2f}"))
            tabela.setItem(row, 3, QtWidgets.QTableWidgetItem(f"R${float((item["quantidade_minima"] - item["quantidade_atual"])) * float(item["valor_unitario"]):.2f}"))
        
        if self.ui.frame_compras_cadastro.width() == 0:
            self.ui.frame_compras_cadastro.setFixedWidth(850)
        self.item_verificado += 1 
    
#===============================ITENS=============================#        
    
    def carregar_tree_itens(self):
        dados = self.db.get_all_itens()
        
        self.ui.tree_itens_cadastrados.clear()
        
        for row in dados:
            itens = QtWidgets.QTreeWidgetItem(self.ui.tree_itens_cadastrados)
            itens.setText(0, row["nome"])
            itens.setData(0,QtCore.Qt.UserRole, row["id_item"])
            
            QtWidgets.QTreeWidgetItem(itens, [f"Código interno: {row["codigo_interno"]}"])
            QtWidgets.QTreeWidgetItem(itens, [f"Unidade de medida: {row["unidade_medida"]}"])
        
    def carregar_tab_itens(self):
        self.ui.tabs.setCurrentIndex(7)
        self.carregar_tree_itens()
        self.carregar_lista_itens_edit()
        self.carregar_lista_itens_add()
        self.limpar_campos_itens()
        self.limpar_campos_edit()
        self.limpar_campos_add_estoque()
    
    def cadastrar_itens(self):
        info = (self.ui.edit_itens_cadastro_nome.text(), self.ui.edit_itens_cadastro_codigo.text(), self.ui.edit_itens_cadastro_medida.text(), self.usuario)
        
        nome = self.ui.edit_itens_cadastro_nome.text()
        item = self.db.buscar_item_nome(nome)
        
        if item:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", f"Um item com o nome {nome} já existe.")
            return
        
        try:
            self.db.cadastrar_itens(info)
            QtWidgets.QMessageBox.information(self.main, "Sucesso!", "Item cadastrado com sucesso!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao cadastrar item: {e}")
            return
        
        self.carregar_tab_itens()
    
    def limpar_campos_itens(self):
        self.ui.edit_itens_cadastro_nome.clear()
        self.ui.edit_itens_cadastro_codigo.clear()
        self.ui.edit_itens_cadastro_medida.clear()
    
    def adicionar_ao_estoque(self):
        info = (self.ui.box_add_estoque_item.currentData(), self.ui.edit_add_estoque_qntd_atual.text(), self.ui.edit_add_estoque_qntd_minima.text(), self.usuario)
        
        id_item = self.ui.box_add_estoque_item.currentData()
        item = self.db.verificar_estoque(id_item)
        
        if item:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Item já cadastrado no estoque.")
            return
        
        try:
            self.db.adicionar_ao_estoque(info)
            QtWidgets.QMessageBox.information(self.main, "Sucesso", "Item adicionado ao estoque com sucesso!")
            self.limpar_campos_add_estoque()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao adicionar item ao estoque: {e}")
            return
    
    def limpar_campos_add_estoque(self):
        self.ui.box_add_estoque_item.setCurrentIndex(0)
        self.ui.edit_add_estoque_qntd_atual.clear()
        self.ui.edit_add_estoque_qntd_minima.clear()
          
    def carregar_lista_itens_edit(self):
        self.ui.box_edit_itens_nome.clear()

        try:
            self.ui.box_edit_itens_nome.addItem("Selecione um item:")
            itens = self.db.get_all_itens()
            
            for i in itens:
                self.ui.box_edit_itens_nome.addItem(i["nome"], i["id_item"])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao carregar lista de itens: {e}")
            return
    
    def carregar_lista_itens_add(self):
        self.ui.box_add_estoque_item.clear()

        try:
            self.ui.box_add_estoque_item.addItem("Selecione um item:")
            itens = self.db.get_all_itens()
            
            for i in itens:
                self.ui.box_add_estoque_item.addItem(i["nome"], i["id_item"])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao carregar lista de itens: {e}")
            return
    
    def carregar_itens_edit(self):
        if self.ui.box_edit_itens_nome.currentData() is None:
            return
        
        id_item = self.ui.box_edit_itens_nome.currentData()
        
        item = self.db.buscar_item_por_id(id_item)
        
        self.ui.edit_edit_itens_codigo.setText(item["codigo_interno"])
        self.ui.edit_edit_itens_medida.setText(item["unidade_medida"])
    
    def editar_item(self):
        info = {"nome": self.ui.box_edit_itens_nome.currentText(),
                "codigo": self.ui.edit_edit_itens_codigo.text(), 
                "medida": self.ui.edit_edit_itens_medida.text(), 
                "usuario": self.usuario,
                "id_item": self.ui.box_edit_itens_nome.currentData()}
        
        
        item = self.db.buscar_item_nome(info["nome"])
        if item:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", f"Um item com o nome {info["nome"]} já existe.")
            return
        
        try:
            self.db.edit_item(info)
            QtWidgets.QMessageBox.information(self.main, "Sucesso", "Item alterado com sucesso!")
            self.carregar_tree_itens()
            self.limpar_campos_edit()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao alterar item: {e}")
            return
    
    def limpar_campos_edit(self):
        self.ui.box_edit_itens_nome.setCurrentIndex(0)
        self.ui.edit_edit_itens_codigo.clear()
        self.ui.edit_edit_itens_medida.clear()
    
#===============================COMPRAS=============================#

    def carregar_tree_compras(self):
        dados = self.db.get_all_compras()
        
        self.ui.tree_compras_cadastradas.clear()
        compra_atual = None
        
        for row in dados:
            if compra_atual != row["id_compra"]:
                compra_atual = row["id_compra"]
                
                compras = QtWidgets.QTreeWidgetItem(self.ui.tree_compras_cadastradas)
                compras.setText(0, f"Data: {row["data_solicitacao"]} - Status: {row["validacao"]}")
                compras.setData(0, QtCore.Qt.UserRole, row["id_compra"])
                
                QtWidgets.QTreeWidgetItem(compras, [f"Nota fiscal: {row["n_danfe"]}"])
                QtWidgets.QTreeWidgetItem(compras, [f"Chave de acesso: {row["chave_acesso"]}"])
                QtWidgets.QTreeWidgetItem(compras, [f"Fornecedor: {row["fornecedor"]}"])
                QtWidgets.QTreeWidgetItem(compras, [f"Vendedor: {row["vendedor"]}"])
                QtWidgets.QTreeWidgetItem(compras, [f"Solicitante: {row["usuario"]}"])
                QtWidgets.QTreeWidgetItem(compras, [f"Motivo: {row["motivo"]}"])
                QtWidgets.QTreeWidgetItem(compras, [f"Valor total: {row["valor_total"]}"])
                QtWidgets.QTreeWidgetItem(compras, [f"Atualizado por: {row["approved_by"]}"])
                QtWidgets.QTreeWidgetItem(compras, [f"Atualizado em: {row["data_validacao"]}"])
                
                itens_comprados = QtWidgets.QTreeWidgetItem(compras, ["ITENS DA COMPRA"])
            QtWidgets.QTreeWidgetItem(itens_comprados, [f"Item: {row["item"]} - Quantidade: {row["quantidade"]} - Valor unitário: {row["valor_unitario"]}"])
    
    def carregar_tab_compras(self):
        self.ui.tabs.setCurrentIndex(8)
        self.ui.frame_compras_cadastro.setFixedWidth(0)
        self.carregar_tree_compras()
        self.carregar_tabela_itens()
        self.carregar_lista_fornecedores_compras()
        self.carregar_lista_vendedores_compras()
        self.carregar_lista_itens_compras()
   
    def toggle_compras(self):
        if self.ui.frame_compras_cadastro.width() == 0:
            self.ui.frame_compras_cadastro.setFixedWidth(850)
            self.limpar_campos_compras()
        else:
            self.ui.frame_compras_cadastro.setFixedWidth(0)
    
    def cadastrar_compra(self):
        info_compra = (self.ui.box_compras_cadastro_forn.currentData(), self.ui.box_compras_cadastro_vendedor.currentData(), self.ui.txt_compras_cadastro_motivo.toPlainText(),
                       self.ui.edit_compras_cadastro_valor_total.text(), self.usuario)
        
        id_fornecedor = self.ui.box_compras_cadastro_forn.currentData()
        id_vendedor = self.ui.box_compras_cadastro_vendedor.currentData()
        
        if not id_fornecedor:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione um fornecedor.")
            return
        
        if not id_vendedor:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione um vendedor")
            return
        
        if not self.itens_compra:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Adicione pelo menos um item a compra.")
            return
        
        try:
            id_compra = self.db.cadastrar_compra(info_compra)
            try:
                for item in self.itens_compra:
                    self.db.registrar_itens_compra(id_compra, item)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao registrar item {item["item"]}: {e}")
                return
            QtWidgets.QMessageBox.information(self.main, "Informação", "Compra cadastrada com sucesso!")
            self.carregar_tree_compras()
            self.limpar_campos_compras()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao registrar compra: {e}")
            return
    
    def listar_itens_compra(self):
        if not self.ui.edit_compras_itens_valor.text():
            QtWidgets.QMessageBox.warning(self.main, "Aviso", "Por favor insira o valor da peça.")
            return
        
        info_itens = {"id_item": self.ui.box_compras_itens_item.currentData(),
                      "item": self.ui.box_compras_itens_item.currentText(),
                      "quantidade": float(self.ui.edit_compras_itens_qntd.text().replace(",",".")),
                      "valor_unitario": float(self.ui.edit_compras_itens_valor.text().replace(",", "."))}
        
        self.itens_compra.append(info_itens)
        
        self.carregar_tabela_itens()
    
    def incluir_itens_criticos(self):
        for item in self.itens_criticos:
            self.itens_compra.append(item)
            self.carregar_tabela_itens()
    
    def carregar_tabela_itens(self):
        tabela = self.ui.table_compras_itens
        tabela.setRowCount(0)
        
        valor_total = 0.0
        
        for item in self.itens_compra:
            row = tabela.rowCount()
            tabela.insertRow(row)
            
            tabela.setItem(row, 0, QtWidgets.QTableWidgetItem(item["item"]))
            tabela.setItem(row, 1, QtWidgets.QTableWidgetItem(str(item["quantidade"])))
            tabela.setItem(row, 2, QtWidgets.QTableWidgetItem(f"R${item["valor_unitario"]:.2f}"))
            tabela.setItem(row, 3, QtWidgets.QTableWidgetItem(f"R${float(item["quantidade"]) * float(item["valor_unitario"]):.2f}"))
            
            valor_total += float(item["quantidade"]) * float(item["valor_unitario"])
        self.ui.edit_compras_cadastro_valor_total.setText(f"R$ {valor_total:.2f}")
    
    def limpar_campos_compras(self):
        self.ui.box_compras_cadastro_forn.setCurrentIndex(0)
        self.ui.box_compras_cadastro_vendedor.setCurrentIndex(0)
        self.ui.edit_compras_cadastro_valor_total.clear()
        self.ui.txt_compras_cadastro_motivo.clear()
        self.ui.box_compras_itens_item.setCurrentIndex(0)
        self.ui.edit_compras_itens_valor.clear()
        self.ui.edit_compras_cadastro_nf.clear()
        self.itens_compra.clear()
        self.carregar_tabela_itens()
    
    def carregar_lista_fornecedores_compras(self):
        self.ui.box_compras_cadastro_forn.clear()
        
        fornecedores = self.db.listar_fornecedores()
        
        self.ui.box_compras_cadastro_forn.addItem("Selecione um fornecedor")
        
        for f in fornecedores:
            self.ui.box_compras_cadastro_forn.addItem(f["nome_empresarial"], f["id_fornecedor"])
        
    def carregar_lista_vendedores_compras(self):
        self.ui.box_compras_cadastro_vendedor.clear()
        
        id_fornecedor = self.ui.box_compras_cadastro_forn.currentData()
        
        vendedores = self.db.vendedor_por_fornecedor(id_fornecedor)
        
        self.ui.box_compras_cadastro_vendedor.addItem("Selecione um vendedor")
        
        for v in vendedores:
            self.ui.box_compras_cadastro_vendedor.addItem(v["nome"], v["id_vendedor"])
    
    def carregar_lista_itens_compras(self):
        self.ui.box_compras_itens_item.clear()
        
        itens = self.db.get_all_itens()
        
        self.ui.box_compras_itens_item.addItem("Selecione um item:")
        
        for i in itens:
            self.ui.box_compras_itens_item.addItem(i["nome"], i["id_item"])
    
    def itens_recebidos(self):
        compra = self.ui.tree_compras_cadastradas.currentItem()
        
        if not compra:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione uma compra para alterar o status.")
            return
        
        id_compra = compra.data(0, QtCore.Qt.UserRole)
        
        if id_compra is None:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione um item, não um grupo.")
            return
        
        item = self.db.get_itens_compra(id_compra)
        for i in item:
            existe = self.db.verificar_existe_estoque(i["id_item"])
            if existe:
                self.db.entrada_estoque(i, id_compra)
                self.carregar_tree_compras()
            else:
                info = {
                    "id_item": i["id_item"],
                    "quantidade": i["quantidade"],
                    "usuario": self.usuario
                }
                
                self.db.registrar_estoque_compra(info, id_compra)
                self.carregar_tree_compras()
        
    def set_compra_aprovada(self):
        if self.funcao != "GERENTE" and self.funcao != "ADMINISTRADOR":
            QtWidgets.QMessageBox.warning(self.main, "Aviso", "Você não tem permissão para aprovar uma compra.")
            return
        
        compra = self.ui.tree_compras_cadastradas.currentItem()
        
        if not compra:
            return
        
        id_compra = compra.data(0, QtCore.Qt.UserRole)
        
        if id_compra is None:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione um item, não um grupo.")
            return
        
        self.db.set_compra_aprovada(id_compra)
        self.carregar_tree_compras()
    
    def set_compra_negada(self):
        if self.funcao != "GERENTE" and self.funcao != "ADMINISTRADOR":
            QtWidgets.QMessageBox.warning(self.main, "Aviso", "Você não tem permissão para negar uma compra.")
            return
        
        compra = self.ui.tree_compras_cadastradas.currentItem()
        
        if not compra:
            return
        
        id_compra = compra.data(0, QtCore.Qt.UserRole)
        
        if id_compra is None:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione um item, não um grupo.")
            return
        
        self.db.set_compra_negada(id_compra)
        self.carregar_tree_compras()

    def set_compra_cancelada(self):
        compra = self.ui.tree_compras_cadastradas.currentItem()
        
        if not compra:
            return
        
        id_compra = compra.data(0, QtCore.Qt.UserRole)
        
        if id_compra is None:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione um item, não um grupo.")
            return
        
        self.db.set_compra_cancelada(id_compra)
        self.carregar_tree_compras()

    def set_compra_analise(self):
        if self.funcao != "GERENTE" and self.funcao != "ADMINISTRADOR":
            QtWidgets.QMessageBox.warning(self.main, "Aviso", "Você não tem permissão para alterar a compra.")
            return
        
        compra = self.ui.tree_compras_cadastradas.currentItem()
        
        if not compra:
            return
        
        id_compra = compra.data(0, QtCore.Qt.UserRole)
        
        if id_compra is None:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione um item, não um grupo.")
            return
        
        self.db.set_compra_analise(id_compra)
        self.carregar_tree_compras()
        
    def vincular_nf(self):
        compra = self.ui.tree_compras_cadastradas.currentItem()
        
        if not compra:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione uma compra para vincular NF.")
            return
        
        numero_nota = self.ui.edit_compras_cadastro_nf.text()
        
        if not numero_nota:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Digite o número da nota.")
            return
        
        chave_acesso = self.ui.edit_compras_cadastro_nf_chave.text()
        
        if not chave_acesso:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Digite a chave de acesso (encontra-se embaixo do código de barras da nota).")
            return
        
        id_compra = compra.data(0, QtCore.Qt.UserRole)
        
        if id_compra is None:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione um item, não um grupo.")
            return
        
        info_nf = (self.ui.edit_compras_cadastro_nf.text(), id_compra)
        
        try:
            self.db.vincular_nf(info_nf)
            QtWidgets.QMessageBox.information(self.main, "Sucesso", "NF vinculada com sucesso!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao vincular NF: {e}")
            return
        
        self.carregar_tree_compras()
        self.limpar_campos_compras()

    def remover_item_lista_compra(self):
        row = self.ui.table_compras_itens.currentRow()
        
        if row >= 0:
            id_item = self.ui.table_compras_itens.item(row, 0).text()
            
            for item in self.itens_compra:
                if item["item"] == id_item:
                    self.itens_compra.remove(item)
                    QtWidgets.QMessageBox.information(self.main, "Sucesso", "Item removido com sucesso!")
                    self.carregar_tabela_itens()
                    return

#===============================EDITAR ESTOQUE=============================#

    def buscar_item_edit(self):
        row = self.ui.table_estoque_itens.currentRow()
        
        if row >= 0:
            id_item = self.ui.table_estoque_itens.item(row, 0).text()
            id_item = int(id_item)
            
            item = self.db.get_info_itens_estoque(id_item)
            
            self.ui.edit_estoque_edit_qntd.setText(str(item["quantidade_atual"]))
            self.ui.edit_estoque_edit_nova_qntd.setText(str(item["quantidade_minima"]))
        else:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione um item para editar.")
            return 
    
    def toggle_editar_estoque(self):
        if self.ui.frame_estoque_edit.height() == 0:
            self.ui.frame_estoque_edit.setFixedHeight(200)
            self.limpar_campos_edit()
        else:
            self.ui.frame_estoque_edit.setFixedHeight(0)
            self.limpar_campos_edit()
    
    def manter_alteracoes_edit(self):
        row = self.ui.table_estoque_itens.currentRow()
        
        texto = self.ui.edit_estoque_edit_qntd.text()

        try:
            valor = float(texto)
            if valor < 0:
                raise ValueError
        except ValueError:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Digite um valor válido.")
        
        texto_2 = self.ui.edit_estoque_edit_nova_qntd.text()

        try:
            valor = float(texto_2)
            if valor < 0:
                raise ValueError
        except ValueError:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Digite um valor válido.")
        
        if row >= 0:
            id_item = self.ui.table_estoque_itens.item(row, 0).text()
            id_item = int(id_item)
            
            info = {"quantidade": self.ui.edit_estoque_edit_qntd.text().replace(",", "."),
                    "nova_quantidade": self.ui.edit_estoque_edit_nova_qntd.text().replace(",", "."), 
                    "id_item": id_item}
            try:
                self.db.ajustar_estoque(info, self.usuario)
                QtWidgets.QMessageBox.information(self.main, "Sucesso!", "Estoque ajustado com sucesso")
                self.carregar_table_estoque()
                self.carregar_tree_movimentacoes()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao ajustar o estoque: {e}")
                return    
        else:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione um item para editar.")
            return  
    
    def limpar_campos_edit(self):
        self.ui.edit_estoque_edit_qntd.clear()
        self.ui.edit_estoque_edit_nova_qntd.clear()
    
#===============================REGISTRO MOVIMENTAÇÃO=============================#

    def carregar_tab_movimentacoes(self):
        self.ui.tabs.setCurrentIndex(9)
        self.listar_itens_os()
        self.listar_os_movimentacao()

    def listar_os_movimentacao(self):
        self.ui.box_movimentacao_os.clear()
        
        self.ui.box_movimentacao_os.addItem("Selecione uma OS:")
        
        try:
            os = self.db.listar_os()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao listar OS: {e}")
            return
        
        for item in os:
            self.ui.box_movimentacao_os.addItem(item["numero_os"], item["id_os"])
    
    def listar_itens_os(self):
        self.ui.box_movimentacao_itens_item.clear()
        
        self.ui.box_movimentacao_itens_item.addItem("Selecione um item:")
        
        try:
            itens = self.db.get_all_itens()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro ao listar itens para os: {e}")
            return
        
        for item in itens:
            self.ui.box_movimentacao_itens_item.addItem(item["nome"], item["id_item"])
    
    def adicionar_item_movimentacao(self):
        id_item = self.ui.box_movimentacao_itens_item.currentData()
        
        if not id_item:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione um item para adicionar.")
            return
        
        quantidade = self.ui.edit_movimentacao_itens_qntd.text()
        
        if not quantidade:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Digite a quantidade de itens a ser movimentado.")
            return
        
        try:
            valor = float(quantidade)
            if valor < 0:
                raise ValueError
        except ValueError:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Digite um valor válido.")
            return
                
        item = self.db.get_itens_movimentacao(id_item)
        
        info_item_movimentacao = {
            "id_item": id_item,
            "nome": item["nome"],
            "codigo_interno": item["codigo_interno"],
            "unidade_medida": item["unidade_medida"],
            "quantidade": self.ui.edit_movimentacao_itens_qntd.text(),
            "estoque": item["quantidade_atual"]
        }
        
        self.itens_movimentacao.append(info_item_movimentacao)
        self.carregar_table_itens_movimentacao()
    
    def carregar_table_itens_movimentacao(self):
        tabela = self.ui.table_movimentacao_itens
        tabela.setRowCount(0)
        
        for item in self.itens_movimentacao:
            row = tabela.rowCount()
            tabela.insertRow(row)
            
            tabela.setItem(row, 0, QtWidgets.QTableWidgetItem(item["nome"]))
            tabela.setItem(row, 1, QtWidgets.QTableWidgetItem(item["codigo_interno"]))
            tabela.setItem(row, 2, QtWidgets.QTableWidgetItem(item["unidade_medida"]))
            tabela.setItem(row, 3, QtWidgets.QTableWidgetItem(str(item["quantidade"])))
            tabela.setItem(row, 4, QtWidgets.QTableWidgetItem(str(item["estoque"])))          
    
    def registrar_movimentacao(self):

        if self.ui.box_movimentacao_tipo.currentText() == "SAIDA" and self.ui.box_movimentacao_destino.currentText() == "MECANICA" and not self.ui.box_movimentacao_os.currentData():
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione uma OS")
            return
        
        if self.ui.box_movimentacao_tipo.currentText() not in ("ENTRADA", "SAIDA"):
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione o tipo de movimentação.")
            return
        
        if self.ui.box_movimentacao_origem.currentText() not in ("MECANICA", "FUNCIONARIO", "ESTOQUE"):
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione a origem da movimentação.")
            return
        
        if self.ui.box_movimentacao_destino.currentText() not in ("MECANICA", "FUNCIONARIO", "ESTOQUE"):
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Selecione o destino da movimentação.")
            return
        
        if self.ui.box_movimentacao_tipo.currentText() == "ENTRADA" and self.ui.box_movimentacao_origem.currentText() == "ESTOQUE":
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "O estoque não pode dar entrada para ele mesmo")
            return
        
        if self.ui.box_movimentacao_tipo.currentText() == "ENTRADA" and self.ui.box_movimentacao_destino.currentText() != "ESTOQUE":
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Entrada é apenas destinada ao estoque.")
            return
        
        if self.ui.box_movimentacao_tipo.currentText() == "SAIDA" and self.ui.box_movimentacao_origem.currentText() != "ESTOQUE":
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Não é possível realizar a retirada de itens que não sejam do estoque.")
            return
        
        if self.ui.box_movimentacao_tipo.currentText() == "SAIDA" and self.ui.box_movimentacao_destino.currentText() == "ESTOQUE":
            QtWidgets.QMessageBox.information(self.main, "Atenção", "Não é possível realizar uma saída para o próprio estoque")
            return
        
        responsavel = self.ui.edit_movimentacao_responsavel.text()
        
        if not responsavel:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "Informe o responsável pela solicitacao do item.")
            return
        
        if not self.itens_movimentacao:
            QtWidgets.QMessageBox.warning(self.main, "Atenção", "É necessário ter pelo menos um item para realizar a movimentação.")
            return
            
        info_mov = (self.ui.box_movimentacao_tipo.currentText(), self.ui.box_movimentacao_os.currentData(), self.ui.box_movimentacao_origem.currentText(), self.ui.edit_movimentacao_responsavel.text(), self.ui.box_movimentacao_destino.currentText(),
                    self.ui.txt_movimentacao_descricao.toPlainText(), self.usuario)
        
        try:
            id_mov = self.db.registrar_movimentacao(info_mov)
            try:
                for item in self.itens_movimentacao:
                    self.db.registrar_itens_movimentacao(item, id_mov)
                    if self.ui.box_movimentacao_tipo.currentText() == "SAIDA":
                        self.db.saida_estoque_movimentacao(item)
                    else:
                        self.db.entrada_estoque_movimentacao(item)
                QtWidgets.QMessageBox.information(self.main, "Sucesso", "Movimentação registrada com sucesso!")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self.main, "Erro", f"Os itens da movimentação não foram cadastrados: {e}")
                return
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main, "Erro", f"Erro, a movimentação não foi registrada: {e}")
            return
        
        self.limpar_campos_movimentacao()
    
    def limpar_campos_movimentacao(self):
        self.ui.box_movimentacao_tipo.setCurrentIndex(0)
        self.ui.edit_movimentacao_responsavel.clear()
        self.ui.box_movimentacao_destino.setCurrentIndex(0)
        self.ui.box_movimentacao_origem.setCurrentIndex(0)
        self.ui.txt_movimentacao_descricao.clear()
        self.itens_movimentacao.clear()
        self.ui.box_movimentacao_itens_item.setCurrentIndex(0)
        self.ui.edit_movimentacao_itens_qntd.clear()
        self.carregar_table_itens_movimentacao()