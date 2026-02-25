from PyQt5 import QtWidgets
from gui.login_dialog import Ui_LoginDialog
from gui.new_main_window import Ui_MainWindow
from config.database import DbConect
from gui.tabs.fornecedores_tab import FornecedoresTab
from gui.tabs.estoque_tab import EstoqueTab
from gui.tabs.equipamentos_tab import EquipamentosTab

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, db, id_usuario, funcao):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.db = db
        self.id_usuario = id_usuario
        self.funcao = funcao
        
        self.fornecedores = FornecedoresTab(self)
        self.estoque = EstoqueTab(self)
        self.equipamentos = EquipamentosTab(self)
        
        self.ui.btn_menu.clicked.connect(self.toggle_menu)

#======================TABS======================#
        self.ui.btn_select_forn_tab.clicked.connect(self.fornecedores.carregar_tab_forn)
        self.ui.btn_select_estoque_tab.clicked.connect(self.estoque.carregar_tab_estoque)
        self.ui.btn_select_veic_tab.clicked.connect(self.equipamentos.carregar_tab_equipamentos)

#======================FORNECEDORES======================#
        self.fornecedores.carregar_tab_forn()
        self.ui.btn_forn_pesquisar.clicked.connect(self.fornecedores.filtro_fornecedores)
        self.ui.btn_forn_add.clicked.connect(self.fornecedores.carregar_tab_cadastro_forn)
        self.ui.btn_forn_edit_forn.clicked.connect(self.fornecedores.carregar_tab_edit_forn)
        self.ui.btn_forn_atualizar.clicked.connect(self.fornecedores.carregar_tree_fornecedores)
        self.ui.btn_forn_setores.clicked.connect(self.fornecedores.carregar_tab_setores)
        self.ui.btn_forn_vinculo.clicked.connect(self.fornecedores.vincular_documento)
        self.ui.box_forn_vinculo_forn.currentTextChanged.connect(self.fornecedores.listar_setores_vinculo)
        
#======================FORNECEDORES CADASTRO======================#
        self.ui.btn_forn_cadastro_vendedores_add_vendedor.clicked.connect(self.fornecedores.cadastro_vendedores)
        self.ui.btn_cadastro_forn_add_setor.clicked.connect(self.fornecedores.listar_setor_cadastro)
        self.ui.btn_cadastro_forn_add.clicked.connect(self.fornecedores.cadastrar_fornecedor)
        self.ui.btn_cadastro_forn_limpar.clicked.connect(self.fornecedores.limpar_campos_cadastro)
        self.ui.btn_forn_cadastro_pg_inicial.clicked.connect(self.fornecedores.carregar_tab_forn)
        self.ui.btn_forn_cadastro_consulta.clicked.connect(self.consulta_api)
        
#======================EDITAR FORNECEDOR======================#
        self.ui.btn_edit_forn_busca.clicked.connect(self.fornecedores.carregar_info_forn)
        self.ui.btn_edit_forn_pg_inicial.clicked.connect(self.fornecedores.carregar_tab_forn)
        self.ui.btn_edit_forn_novo_setor.clicked.connect(self.fornecedores.listar_setor_edit)
        self.ui.btn_edit_forn_remove_setor.clicked.connect(self.fornecedores.remover_setor)
        self.ui.btn_edit_forn_salvar.clicked.connect(self.fornecedores.manter_alteracoes_edit_forn)
        self.ui.btn_edit_forn_limpar.clicked.connect(self.fornecedores.limpar_campos_edit)

#======================SETORES======================#

        self.ui.btn_setor_pesquisar.clicked.connect(self.fornecedores.filtro_setores)
        self.ui.btn_setor_pg_forn.clicked.connect(self.fornecedores.carregar_tab_forn)
        self.ui.btn_setor_atualizar.clicked.connect(self.fornecedores.carregar_tree_setores)
        self.ui.btn_setor_add.clicked.connect(self.fornecedores.carregar_tab_setor_cadastro)
        self.ui.btn_setor_edit.clicked.connect(self.fornecedores.carregar_tab_edit_setor)
        

#======================SETOR CADASTRO======================#

        self.ui.btn_cadastro_setor_pg_inicial.clicked.connect(self.fornecedores.carregar_tab_setores)
        self.ui.btn_cadastro_setor_doc_nec_add.clicked.connect(self.fornecedores.listar_doc_necessarios)
        self.ui.btn_cadastro_setor_add.clicked.connect(self.fornecedores.cadastrar_setor)
        self.ui.btn_cadastro_setor_limpar.clicked.connect(self.fornecedores.limpar_campos_setor_cadastro)

#======================EDITAR SETOR======================#

        self.ui.btn_edit_setor_pg_inicial.clicked.connect(self.fornecedores.carregar_tab_setores)
        self.ui.btn_edit_setor_pesquisa.clicked.connect(self.fornecedores.buscar_setor)
        self.ui.btn_edit_setor_novo_doc.clicked.connect(self.fornecedores.listar_novo_doc_edit_setor)
        self.ui.btn_edit_setor_remover_doc.clicked.connect(self.fornecedores.remover_doc)
        self.ui.btn_edit_setor_salvar.clicked.connect(self.fornecedores.manter_alteracoes_edit_setor)
        self.ui.btn_edit_setor_limpar.clicked.connect(self.fornecedores.limpar_campos_edit_setor)
        
#======================ESTOQUE======================#

        self.ui.btn_estoque_itens_filtro.clicked.connect(self.estoque.filtrar_estoque)
        self.ui.btn_estoque_movimentacoes_filtro.clicked.connect(self.estoque.filtro_movimentacoes)
        self.ui.btn_estoque_movimentacoes_periodo.clicked.connect(self.estoque.filtro_movimentacoes_periodo)
        self.ui.btn_estoque_atualizar.clicked.connect(self.estoque.carregar_tab_estoque)
        self.ui.btn_estoque_itens.clicked.connect(self.estoque.carregar_tab_itens)
        self.ui.btn_estoque_ajuste.clicked.connect(self.estoque.toggle_editar_estoque)
        self.ui.btn_estoque_registro_movimentacao.clicked.connect(self.estoque.carregar_tab_movimentacoes)
        
#======================ITENS======================#

        self.ui.btn_itens_cadastro_salvar.clicked.connect(self.estoque.cadastrar_itens)
        self.ui.btn_itens_cadastro_limpar.clicked.connect(self.estoque.limpar_campos_itens)
        self.ui.btn_itens_pg_inicial.clicked.connect(self.estoque.carregar_tab_estoque)
        self.ui.box_edit_itens_nome.currentTextChanged.connect(self.estoque.carregar_itens_edit)
        self.ui.btn_edit_itens_salvar.clicked.connect(self.estoque.editar_item)
        self.ui.btn_edit_itens_limpar.clicked.connect(self.estoque.limpar_campos_edit)
        self.ui.btn_estoque_compras.clicked.connect(self.estoque.carregar_tab_compras)
        self.ui.btn_add_estoque_add.clicked.connect(self.estoque.adicionar_ao_estoque)
        self.ui.btn_add_estoque_limpar.clicked.connect(self.estoque.limpar_campos_add_estoque)

#======================COMPRAS======================#

        self.ui.btn_compras_pg_inicial.clicked.connect(self.estoque.carregar_tab_estoque)
        self.ui.btn_compras_itens_add.clicked.connect(self.estoque.listar_itens_compra)
        self.ui.btn_compras_cadastro_solicitar.clicked.connect(self.estoque.cadastrar_compra)
        self.ui.btn_compras_cadastro_limpar.clicked.connect(self.estoque.limpar_campos_compras)
        self.ui.box_compras_cadastro_forn.currentTextChanged.connect(self.estoque.carregar_lista_vendedores_compras)
        self.ui.btn_compras_set_recebida.clicked.connect(self.estoque.itens_recebidos)
        self.ui.btn_compras_set_aprovada.clicked.connect(self.estoque.set_compra_aprovada)
        self.ui.btn_compras_set_negada.clicked.connect(self.estoque.set_compra_negada)
        self.ui.btn_compras_set_analise.clicked.connect(self.estoque.set_compra_analise)
        self.ui.btn_compras_set_cancelada.clicked.connect(self.estoque.set_compra_cancelada)
        self.ui.btn_compras_cadastro_vinc_nf.clicked.connect(self.estoque.vincular_nf)
        self.ui.btn_compras_itens_remover.clicked.connect(self.estoque.remover_item_lista_compra)
        self.ui.btn_compras_nova_compra.clicked.connect(self.estoque.toggle_compras)
        self.ui.btn_compras_itens_incluir_criticos.clicked.connect(self.estoque.incluir_itens_criticos)

#======================EDITAR ESTOQUE======================#

        self.ui.btn_estoque_edit_busca.clicked.connect(self.estoque.buscar_item_edit)
        self.ui.btn_estoque_edit_salvar.clicked.connect(self.estoque.manter_alteracoes_edit)
        self.ui.btn_estoque_edit_limpar.clicked.connect(self.estoque.limpar_campos_edit)

#======================REGISTRAR MOVIMENTAÇÃO======================#

        self.ui.btn_movimentacao_itens_add.clicked.connect(self.estoque.adicionar_item_movimentacao)
        self.ui.btn_movimentacao_pg_inicial.clicked.connect(self.estoque.carregar_tab_estoque)
        self.ui.btn_movimentacao_registrar.clicked.connect(self.estoque.registrar_movimentacao)
        self.ui.btn_movimentacao_limpar.clicked.connect(self.estoque.limpar_campos_movimentacao)

#======================EQUIPAMENTOS======================#

        self.ui.btn_equipamento_edit.clicked.connect(self.equipamentos.toggle_edit)
        self.ui.btn_equipamento_vincular.clicked.connect(self.equipamentos.toggle_vinc_doc)
        self.ui.btn_equipamento_doc_vincular.clicked.connect(self.equipamentos.vincular_doc_equip)
        self.ui.btn_equipamento_edit_salvar.clicked.connect(self.equipamentos.editar_equipamento)
        self.ui.btn_equipamento_filtro.clicked.connect(self.equipamentos.filtrar_equipamento)
        self.ui.btn_equipamento_novo_equipamento.clicked.connect(self.equipamentos.carregar_tab_cadastro_equipamento)
        self.ui.btn_equipamento_edit_limpar.clicked.connect(self.equipamentos.limpar_campos_edit)
        self.ui.btn_equipamento_os.clicked.connect(self.equipamentos.carregar_tab_os)
        self.ui.btn_equipamento_manutencoes.clicked.connect(self.equipamentos.carregar_tab_registro_manutencao)
        self.ui.btn_equipamento_recarregar.clicked.connect(self.equipamentos.carregar_tab_equipamentos)
        
#======================CADASTRO EQUIPAMENTOS======================#

        self.ui.btn_cadastro_equipamento_pg_inicial.clicked.connect(self.equipamentos.carregar_tab_equipamentos)
        self.ui.btn_cadastro_equipamento_salvar.clicked.connect(self.equipamentos.cadastrar_equipamento)
        self.ui.btn_cadastro_equipamento_limpar.clicked.connect(self.equipamentos.limpar_campos_cadastro)
        
#======================ORDENS DE SERVIÇO======================#
        
        self.ui.btn_os_equipamentos.clicked.connect(self.equipamentos.carregar_tab_equipamentos)
        self.ui.btn_os_edit_os.clicked.connect(self.equipamentos.toggle_edit_os)
        self.ui.btn_os_edit_itens_os.clicked.connect(self.equipamentos.toggle_itens_os_edit)
        self.ui.btn_os_edit_salvar.clicked.connect(self.equipamentos.editar_os)
        self.ui.btn_itens_edit_alterar.clicked.connect(self.equipamentos.nova_qntd_itens_edit)
        self.ui.btn_itens_edit_adicionar.clicked.connect(self.equipamentos.novo_item_os)
        self.ui.btn_itens_edit_remover_item.clicked.connect(self.equipamentos.remover_item_os)
        self.ui.btn_os_edit_limpar.clicked.connect(self.equipamentos.limpar_campos_edit_os)
        self.ui.btn_os_nova_os.clicked.connect(self.equipamentos.carregar_tab_abrir_os)
        self.ui.tree_os_info.currentItemChanged.connect(self.equipamentos.toggle_os_status)
        self.ui.btn_os_set_aberta.clicked.connect(self.equipamentos.set_ordem_aberta)
        self.ui.btn_os_set_em_execucao.clicked.connect(self.equipamentos.set_ordem_em_execucao)
        self.ui.btn_os_set_finalizada.clicked.connect(self.equipamentos.set_ordem_finalizada)
        self.ui.btn_os_set_cancelada.clicked.connect(self.equipamentos.set_ordem_cancelada)
        self.ui.btn_os_registro_manutencao.clicked.connect(self.equipamentos.carregar_tab_registro_manutencao)
        self.ui.btn_os_recarregar.clicked.connect(self.equipamentos.carregar_tab_os)
        
#======================ABRIR ORDENS DE SERVIÇO======================#

        self.ui.box_abrir_os_itens_item.currentTextChanged.connect(self.equipamentos.buscar_preco_item)
        self.ui.btn_abrir_os_itens_add.clicked.connect(self.equipamentos.listar_itens_abrir_os)
        self.ui.btn_abrir_os_itens_limpar.clicked.connect(self.equipamentos.limpar_campos_abrir_os_itens)
        self.ui.btn_abrir_os_salvar.clicked.connect(self.equipamentos.registrar_os)
        self.ui.btn_abrir_os_limpar.clicked.connect(self.equipamentos.limpar_campos_abrir_os)
        self.ui.btn_abrir_os_pg_inicial.clicked.connect(self.equipamentos.carregar_tab_os)
        
#===============================REGISTRO MANUTENÇÃO=============================#

        self.ui.btn_registro_manutencao_pg_inicial.clicked.connect(self.equipamentos.carregar_tab_os)
        self.ui.box_registro_manutencao_os.currentIndexChanged.connect(self.equipamentos.carregar_box_itens_manutencao)
        self.ui.box_registro_manutencao_itens_item.currentIndexChanged.connect(self.equipamentos.detalhes_itens_manutencao)
        self.ui.btn_registro_manutencao_itens_add.clicked.connect(self.equipamentos.listar_itens_manutencao)
        self.ui.btn_registro_manutencao_salvar.clicked.connect(self.equipamentos.registrar_manutencao)
        self.ui.btn_registro_manutencao_itens_limpar.clicked.connect(self.equipamentos.limpar_campos_itens_manutencao)
        self.ui.btn_registro_manutencao_limpar.clicked.connect(self.equipamentos.limpar_campos_manutencao)

    def consulta_api(self):
        if not self.ui.edit_cadastro_forn_cnpj.text():
            return
        
        campos = self.fornecedores.buscar_por_cnpj(self.ui.edit_cadastro_forn_cnpj.text())
        
        if campos == None:
            return
        
        self.ui.edit_cadastro_forn_nome.setText(campos[0])
        self.ui.edit_cadastro_forn_logradouro.setText(campos[1])
        self.ui.edit_cadastro_forn_num.setText(campos[2])
        self.ui.edit_cadastro_forn_complemento.setText(campos[3])
        self.ui.edit_cadastro_forn_bairro.setText(campos[4])
        self.ui.edit_cadastro_forn_municipio.setText(campos[5])
        self.ui.edit_cadastro_forn_uf.setText(campos[6])
        self.ui.edit_cadastro_forn_cep.setText(campos[7].replace('.', '').replace('-',''))
        self.ui.edit_cadastro_forn_tel.setText(campos[8].replace('(','').replace(')', '').replace('-',''))
        self.ui.edit_cadastro_forn_email.setText(campos[9])
    
    def toggle_menu(self):
        if self.ui.pages.width() == 0:
            self.ui.pages.setFixedWidth(150)
        else:
            self.ui.pages.setFixedWidth(0)
        
class Login(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.login = Ui_LoginDialog()
        self.login.setupUi(self)
        self.login.btn_login_entrar.clicked.connect(self.logar)
        
        self.login.edit_login_email.setText("erivaldosantosjunior81@gmail.com")
        self.login.edit_login_senha.setText("123456")
        
        self.id_usuario = 0
        self.funcao = ""
    
    def abrir_main_window(self, db):
        self.main_window = MainWindow(db, self.id_usuario, self.funcao)
        self.main_window.showMaximized()
        self.close()  
    
    def logar(self):
        email = self.login.edit_login_email.text()
        senha = self.login.edit_login_senha.text()

        try:
            db = DbConect()
            db.conectar()
            usuario = db.login(email)

            if usuario is None:
                QtWidgets.QMessageBox.warning(self, "Erro", "Usuário não encontrado")
                return

            if senha != usuario["senha_hash"]:
                QtWidgets.QMessageBox.warning(self, "Erro", "Senha incorreta")
                return

            # Login OK
            self.id_usuario = usuario["id_usuario"]
            self.funcao = usuario["perfil"]
            QtWidgets.QMessageBox.information(self, "Ok", "Login efetuado com sucesso!")

            self.abrir_main_window(db)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", str(e))    
        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("QMessageBox QLabel {color: white !important;font-size: 12px;font-weight: bold;}")
    window = Login()
    window.show()
    app.exec_()