# Pegasus Collection Editor
# Copyright (C) 2025 luis0henrique
# Version 0.50

import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem,
                             QFileDialog, QLineEdit, QCheckBox, QMessageBox, QSplitter, QSizePolicy)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class PegasusCustomCollectionEditor(QWidget):

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: #f0f0f0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QLineEdit {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 5px;
            }
            QListWidget::item {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border-bottom: 1px solid #555;
            }
            QListWidget::item:hover {
                background-color: #4a4a4a;
            }
            QLabel {
                color: #f0f0f0;
            }
            QCheckBox {
                color: #f0f0f0;
            }
            QMessageBox {
                background-color: #2d2d2d;
                color: #f0f0f0;
            }
            QMessageBox QPushButton {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 5px;
            }
            QMessageBox QPushButton:hover {
                background-color: #4a4a4a;
            }
            QMessageBox QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.apply_dark_theme
        self.collection_file = None
        self.source_file = None
        self.absolute_path = ""
        self.games = []
        self.existing_games = set()
        self.games_to_add = []
        self.games_to_remove = set()
        self.launch_command = "none"
        self.header = ""
        self.source_collection_name = ""
        self.source_games = set()  # Stores games from the source file
        self.source_loaded = False  # Indicates whether the source file has been loaded.
        self.setWindowTitle("Pegasus Custom Collection Editor")

    def extrair_info_arquivo(self, caminho_arquivo, caminho_base):
        """ Returns the absolute path and file extension. """
        caminho_absoluto = os.path.join(caminho_base, caminho_arquivo.lstrip("./"))
        extensao = os.path.splitext(caminho_arquivo)[1]
        placeholder = ""  # Add a placeholder value to return three values
        return caminho_absoluto, extensao, placeholder

    def initUI(self):
        main_layout = QHBoxLayout()

        # List of games in the custom collection
        self.existing_games_list = QListWidget()
        self.existing_games_list_label = QLabel("Games in the custom collection:")

        # List of games in the source collection
        self.source_games_list = QListWidget()
        self.source_games_list_label = QLabel("Games in the source collection:")

        left_layout = QVBoxLayout()

        # Open collection and create new collection buttons, name and shortname fields
        top_layout = QHBoxLayout()
        self.create_collection_button = QPushButton("📝")
        self.create_collection_button.setToolTip("Create new")
        self.create_collection_button.setStyleSheet("QPushButton { font-size: 40px; }")

        self.open_collection_button = QPushButton("📂")
        self.open_collection_button.setToolTip("Open")
        self.open_collection_button.setStyleSheet("QPushButton { font-size: 40px; }")

        # Adjust button size
        button_size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        button_font = QFont()

        name_layout = QVBoxLayout()
        self.collection_name_input = QLineEdit()
        self.collection_name_input.setPlaceholderText("Collection name")
        self.collection_name_input.setToolTip("Name of the custom collection")

        self.shortname_input = QLineEdit()
        self.shortname_input.setPlaceholderText("Shortname")
        self.shortname_input.setToolTip("An optional short name for the collection, in lowercase. Often an abbreviation, like MAME, NES, etc. By default, matches the name of the collection.")

        name_layout.addWidget(self.collection_name_input)
        name_layout.addWidget(self.shortname_input)

        top_layout.addWidget(self.create_collection_button)
        top_layout.addWidget(self.open_collection_button)
        top_layout.addLayout(name_layout)

        # Adds top layout to left layout
        left_layout.addLayout(top_layout)
        left_layout.addWidget(self.existing_games_list_label)
        left_layout.addWidget(self.existing_games_list)

        # Main Layout with Splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left widget for existing games
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        # Right widget for editing functions
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        # Label to show collection path (hidden in interface)
        self.collection_path_label = QLabel("")
        self.collection_path_label.setVisible(False)  # Hide the label
        right_layout.addWidget(self.collection_path_label)

        # Search fields
        self.search_label = QLabel("Choose the field to search:")
        right_layout.addWidget(self.search_label)

        self.field_checkboxes = {}
        fields = ["game", "file", "description", "developer", "publisher", "genre", "release", "players"]
        field_checkbox_layout = QHBoxLayout()
        for field in fields:
            checkbox = QCheckBox(field)
            checkbox.setEnabled(False)  # Inicialmente desativados
            self.field_checkboxes[field] = checkbox
            field_checkbox_layout.addWidget(checkbox)
        right_layout.addLayout(field_checkbox_layout)

        # Campo de palavra-chave
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Enter the keyword...")
        self.keyword_input.setEnabled(False)
        right_layout.addWidget(self.keyword_input)

        # Botão para filtrar jogos
        self.filter_button = QPushButton("Search")
        right_layout.addWidget(self.filter_button)
        self.filter_button.setEnabled(False)

        # Lista de jogos adicionados
        self.selected_games_label = QLabel("Filtered games:")
        self.selected_games_list = QListWidget()
        right_layout.addWidget(self.selected_games_label)
        right_layout.addWidget(self.selected_games_list)

        # Botão para limpar a lista de jogos adicionados
        self.clear_list_button = QPushButton("Clear Search")
        right_layout.addWidget(self.clear_list_button)
        self.clear_list_button.clicked.connect(self.clear_game_list)

        # Campo para definir caminho absoluto (oculto na interface)
        self.absolute_path_label = QLabel("Absolute path:")
        self.absolute_path_input = QLineEdit()
        self.absolute_path_label.setVisible(False)
        self.absolute_path_input.setVisible(False)
        right_layout.addWidget(self.absolute_path_label)
        right_layout.addWidget(self.absolute_path_input)

        # Botão para salvar
        self.save_button = QPushButton("Save Custom Collection")
        right_layout.addWidget(self.save_button)
        self.save_button.setEnabled(False)

        right_widget.setLayout(right_layout)

        # Widget para a lista de jogos da fonte
        source_games_layout = QVBoxLayout()

        # Criar layout horizontal para o botão e nome da coleção fonte
        source_header_layout = QHBoxLayout()
        source_header_layout.setSpacing(5)  # Reduz o espaçamento entre os widgets
        source_header_layout.setContentsMargins(0, 0, 0, 0)  # Remove as margens

        # Criar o botão com o mesmo estilo do "Abrir Custom Collection"
        self.open_source_button = QPushButton("📂")
        self.open_source_button.setToolTip("Open Source Collection")
        self.open_source_button.setStyleSheet("QPushButton { font-size: 40px; }")

        # Criar o campo de texto somente leitura para o nome da coleção fonte
        self.source_collection_name_display = QLineEdit()
        self.source_collection_name_display.setReadOnly(True)
        self.source_collection_name_display.setPlaceholderText("Source collection name")
        self.source_collection_name_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        source_header_layout.addWidget(self.open_source_button)
        source_header_layout.addWidget(self.source_collection_name_display, 1)

        source_games_layout.addLayout(source_header_layout)
        source_games_layout.addWidget(self.source_games_list_label)
        source_games_layout.addWidget(self.source_games_list)

        source_games_widget = QWidget()
        source_games_widget.setLayout(source_games_layout)

        # Adicionar widgets ao splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.addWidget(source_games_widget)

        # Configurar larguras e proporções
        right_widget.setFixedWidth(600)  # Largura fixa maior para o painel central
        left_widget.setMinimumWidth(300)
        source_games_widget.setMinimumWidth(300)

        # Configurar os fatores de alongamento
        splitter.setStretchFactor(0, 1)  # Lista de jogos existentes
        splitter.setStretchFactor(1, 0)  # Painel central - não estica
        splitter.setStretchFactor(2, 1)  # Lista de jogos da fonte

        # Aumentar a altura mínima das listas
        self.existing_games_list.setMinimumHeight(500)
        self.selected_games_list.setMinimumHeight(500)
        self.source_games_list.setMinimumHeight(500)

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # Conectar botões às funções
        self.open_collection_button.clicked.connect(self.open_collection)
        self.create_collection_button.clicked.connect(self.create_new_collection)
        self.open_source_button.clicked.connect(self.open_source)
        self.save_button.clicked.connect(self.save_collection)
        self.filter_button.clicked.connect(self.filter_games)

        for checkbox in self.field_checkboxes.values():
            checkbox.stateChanged.connect(self.toggle_keyword_input)

        self.apply_dark_theme()

    def toggle_keyword_input(self):
        self.keyword_input.setEnabled(any(cb.isChecked() for cb in self.field_checkboxes.values()))
        self.filter_button.setEnabled(self.keyword_input.isEnabled())

    def open_collection(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Custom Collection", "", "Pegasus Metadata (*.txt)")
        if file_name:
            self.collection_file = file_name
            self.save_button.setEnabled(True)
            self.load_collection_metadata(file_name)
            self.collection_path_label.setText(file_name)
            self.load_existing_games(file_name)
            self.clear_game_list()
            self.update_existing_games_list()
            self.update_source_games_list()  # Atualizar a lista de jogos da coleção fonte

    def load_existing_games(self, file_name):
        """ Carrega os jogos existentes na custom collection. """
        self.existing_games.clear()
        self.games_to_remove.clear()

        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            collecting_games = False
            current_game = {}

            for line in lines:
                if not collecting_games and line.startswith("collection:"):
                    collecting_games = True  # Começamos a coletar os jogos

                if collecting_games:
                    if line.startswith("# "):
                        # Adiciona o jogo coletado anteriormente
                        if current_game and 'game' in current_game and 'file' in current_game:
                            launch_cmd = current_game.get('launch', 'none')  # Pega o launch original ou define 'none'
                            abs_path, ext, _ = self.extrair_info_arquivo(current_game['file'], self.absolute_path)  # Ignore the placeholder value
                            self.existing_games.add((current_game['game'], abs_path, ext, launch_cmd))  # Mantém o comando original

                        # Inicia novo jogo
                        current_game = {'game': line.strip("# ").strip()}
                    elif line.strip() == "":
                        # Finaliza a adição do jogo anterior
                        if current_game and 'game' in current_game and 'file' in current_game:
                            launch_cmd = current_game.get('launch', 'none')  # Pega o launch original ou define 'none'
                            abs_path, ext, _ = self.extrair_info_arquivo(current_game['file'], self.absolute_path)  # Ignore the placeholder value
                            self.existing_games.add((current_game['game'], abs_path, ext, launch_cmd))  # Mantém o comando original

                        current_game = {}
                    else:
                        key, value = line.split(":", 1)
                        current_game[key.strip()] = value.strip()

            # Último jogo
            if current_game and 'game' in current_game and 'file' in current_game:
                launch_cmd = current_game.get('launch', 'none')  # Pega o launch original ou define 'none'
                abs_path, ext, _ = self.extrair_info_arquivo(current_game['file'], self.absolute_path)  # Ignore the placeholder value
                self.existing_games.add((current_game['game'], abs_path, ext, launch_cmd))  # Mantém o comando original

    def update_existing_games_list(self):
        self.existing_games_list.clear()
        for game_name, file_path, ext, launch in sorted(self.existing_games):
            item = QListWidgetItem()
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(10)  # Espaçamento entre o botão e o texto

            # Primeiro adiciona o botão
            button = QPushButton("x")
            button.setFixedSize(30, 30)
            button.clicked.connect(lambda _, item=item, game_name=game_name: self.toggle_game_removal(item, game_name))
            item_layout.addWidget(button)

            # Depois adiciona o label
            label = QLabel(game_name)
            item_layout.addWidget(label)

            # Adiciona espaço flexível no final
            item_layout.addStretch()

            item_widget.setLayout(item_layout)
            item.setSizeHint(item_widget.sizeHint())
            self.existing_games_list.addItem(item)
            self.existing_games_list.setItemWidget(item, item_widget)

    def toggle_game_removal(self, item, game_name):
        row = self.existing_games_list.row(item)
        label = self.existing_games_list.itemWidget(item).findChild(QLabel)
        button = self.existing_games_list.itemWidget(item).findChild(QPushButton)

        if game_name in self.games_to_remove:
            self.games_to_remove.remove(game_name)
            font = label.font()
            font.setStrikeOut(False)
            label.setFont(font)
            label.setStyleSheet('color: black')
            button.setText("x")
        else:
            self.games_to_remove.add(game_name)
            font = label.font()
            font.setStrikeOut(True)
            label.setFont(font)
            label.setStyleSheet('color: gray')
            button.setText("+")

    def create_new_collection(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Create new custom collection", "metadata.pegasus.txt", "Pegasus Metadata (*.txt)")
        if file_name:
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write("collection:\nshortname:\ncommand: none\nextensions: none\nlaunch: none\n\n")
            self.collection_file = file_name
            self.save_button.setEnabled(True)
            self.collection_path_label.setText(file_name)
            self.clear_game_list()
            self.load_collection_metadata(file_name)  # Carregar metadata da nova coleção
            self.load_existing_games(file_name)  # Carregar jogos existentes da nova coleção
            self.update_existing_games_list()  # Atualizar a lista de jogos existentes
            self.update_source_games_list()  # Atualizar a lista de jogos da coleção fonte

    def open_source(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Source File", "", "Pegasus Metadata (*.txt)")
        if file_name:
            self.source_file = file_name
            self.absolute_path = os.path.dirname(file_name)
            self.absolute_path_input.setText(self.absolute_path)
            self.source_loaded = True  # Marca que o arquivo fonte foi carregado
            self.load_launch_command(file_name)
            self.load_source_collection_name(file_name)
            self.load_source_games(file_name)

            # Atualizar o display do nome da coleção fonte
            self.source_collection_name_display.setText(self.source_collection_name)

            # Habilitar os checkboxes de filtro após carregar o arquivo fonte
            for checkbox in self.field_checkboxes.values():
                checkbox.setEnabled(True)

            # Atualizar a lista de jogos da coleção fonte
            self.update_source_games_list()

    def update_source_games_list(self):
        self.source_games_list.clear()
        for game_name, file_path in sorted(self.source_games):
            item = QListWidgetItem()
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(10)  # Espaçamento entre o texto e o botão

            label = QLabel(game_name)
            item_layout.addWidget(label)

            abs_path, file_extension, _ = self.extrair_info_arquivo(file_path, self.absolute_path)
            is_duplicate = any(
                existing_game[1] == abs_path and existing_game[2] == file_extension
                for existing_game in self.existing_games
            )

            if is_duplicate:
                label.setFont(QFont('Arial'))
                label.setStyleSheet('color: gray')
                label.setToolTip("Already exists in the custom collection")
            else:
                button = QPushButton("+")
                button.setFixedSize(30, 30)
                button.clicked.connect(lambda _, item=item, game={"game": game_name, "file": file_path}:
                                    self.toggle_source_game_addition(item, game))
                item_layout.addWidget(button)

            item_widget.setLayout(item_layout)
            item.setSizeHint(item_widget.sizeHint())
            self.source_games_list.addItem(item)
            self.source_games_list.setItemWidget(item, item_widget)

    def load_launch_command(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith("launch:"):
                    self.launch_command = line.replace("launch: ", "").strip()
                    break

    def load_source_collection_name(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith("collection:"):
                    self.source_collection_name = line.replace("collection:", "").strip()
                    break

    def load_source_games(self, file_name):
        self.source_games.clear()
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            current_game = {}
            for line in lines:
                if line.startswith("# "):
                    if current_game and 'game' in current_game and 'file' in current_game:
                        self.source_games.add((current_game['game'], current_game['file']))
                    current_game = {'game': line.strip("# ").strip()}
                elif line.strip() == "":
                    if current_game and 'game' in current_game and 'file' in current_game:
                        self.source_games.add((current_game['game'], current_game['file']))
                        current_game = {}
                else:
                    if ":" in line:  # Ensure the line contains ':' before splitting
                        key, value = line.split(":", 1)
                        current_game[key.strip()] = value.strip()
            if current_game and 'game' in current_game and 'file' in current_game:
                self.source_games.add((current_game['game'], current_game['file']))

        # Atualizar a lista de jogos da coleção fonte
        self.update_source_games_list()

    def load_collection_metadata(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            collection_name = ""
            shortname = ""
            header_lines = []
            for line in file:
                header_lines.append(line)
                if line.startswith("collection:"):
                    collection_name = line.replace("collection:", "").strip()
                elif line.startswith("shortname:"):
                    shortname = line.replace("shortname:", "").strip()
                if line.strip() == "":
                    header_lines.append("\n")
                    break
            self.collection_name_input.setText(collection_name)
            self.shortname_input.setText(shortname)
            self.header = "".join(header_lines)
            self.clear_game_list()  # Limpar a lista de jogos ao carregar a metadata

    def filter_games(self):
        """ Filtra os jogos da coleção fonte e destaca duplicatas. """
        if not self.source_file or not self.keyword_input.text():
            return

        selected_fields = [field for field, checkbox in self.field_checkboxes.items() if checkbox.isChecked()]
        keyword = self.keyword_input.text().lower()
        new_games = []

        with open(self.source_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_game = {}
        description_lines = []
        description_active = False

        for line in lines:
            line = line.strip()

            if line.startswith("game:"):
                if current_game:
                    if any(keyword in current_game.get(field, "").lower() for field in selected_fields):
                        new_games.append(current_game)
                current_game = {"game": line[5:].strip(), "launch": self.launch_command, "file": None, "genre": ""}
                description_lines = []
                description_active = False
            elif line.startswith("description:"):
                description_active = True
                description_lines.append(line.replace("description:", "").strip())
                current_game["description"] = " ".join(description_lines)
            elif line.startswith("developer:"):
                current_game["developer"] = line.replace("developer:", "").strip()
            elif line.startswith("publisher:"):
                current_game["publisher"] = line.replace("publisher:", "").strip()
            elif line.startswith("file:"):
                current_game["file"] = line.replace("file:", "").strip()
            elif line.startswith("genre:"):
                current_game["genre"] = line.replace("genre:", "").strip().lower()  # Captura o campo "genre"
            elif description_active and (line.startswith("publisher:") or line.startswith("genre:") or line.startswith("release:") or line.startswith("players:") or line.startswith("rating:") or line.startswith("assets.") or line.startswith("x-")):
                description_active = False
            elif description_active:
                description_lines.append(line)
                current_game["description"] = " ".join(description_lines)
            elif line and ":" in line:
                key, value = line.split(":", 1)
                current_game[key.strip()] = value.strip()

        if current_game and any(keyword in current_game.get(field, "").lower() for field in selected_fields):
            new_games.append(current_game)

        # Atualiza a lista de jogos filtrados na interface
        self.selected_games_list.clear()

        for game in new_games:
            game_name = game["game"]
            item = QListWidgetItem()
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(10)  # Espaçamento entre o texto e o botão

            # Primeiro adiciona o label
            label = QLabel(game_name)
            item_layout.addWidget(label)

            # Verificar duplicação
            if game["file"]:
                abs_path, file_extension, _ = self.extrair_info_arquivo(game["file"], self.absolute_path)
                is_duplicate = any(
                    existing_game[1] == abs_path and existing_game[2] == file_extension
                    for existing_game in self.existing_games
                )
            else:
                is_duplicate = False

            # Adiciona espaço flexível antes do botão
            item_layout.addStretch()

            # Adiciona o botão ou espaçador no final
            if not is_duplicate:
                button = QPushButton("+")
                button.setFixedSize(30, 30)
                button.clicked.connect(lambda _, item=item, game=game: self.toggle_game_addition(item, game))
                item_layout.addWidget(button)
            elif is_duplicate:
                label.setFont(QFont('Arial'))
                label.setStyleSheet('color: gray')
                label.setToolTip("Already exists in the custom collection")

            item_widget.setLayout(item_layout)
            item.setSizeHint(item_widget.sizeHint())
            self.selected_games_list.addItem(item)
            self.selected_games_list.setItemWidget(item, item_widget)

    def toggle_game_addition(self, item, game):
        row = self.selected_games_list.row(item)
        label = self.selected_games_list.itemWidget(item).findChild(QLabel)
        button = self.selected_games_list.itemWidget(item).findChild(QPushButton)

        game_name = game["game"]
        abs_path = os.path.join(self.absolute_path, game["file"].lstrip("./"))

        if (game_name, abs_path, self.source_collection_name) in [(g['game'], g['file'], g['console']) for g in self.games_to_add]:
            self.games_to_add = [g for g in self.games_to_add if (g['game'], g['file'], g['console']) != (game_name, abs_path, self.source_collection_name)]
            label.setFont(QFont('Arial', italic=False))
            label.setStyleSheet('color: #f0f0f0')
            button.setText("+")
        else:
            game["console"] = self.source_collection_name
            game["file"] = abs_path
            if 'launch' not in game:
                game['launch'] = self.launch_command  # Define um valor padrão para 'launch'
            self.games_to_add.append(game)
            label.setFont(QFont('Arial', italic=False))
            label.setStyleSheet('color: #62c471') # light green
            button.setText("-")

        self.update_source_games_list()

    def toggle_source_game_addition(self, item, game):
        row = self.source_games_list.row(item)
        label = self.source_games_list.itemWidget(item).findChild(QLabel)
        button = self.source_games_list.itemWidget(item).findChild(QPushButton)

        game_name = game["game"]
        abs_path = os.path.join(self.absolute_path, game["file"].lstrip("./"))

        if (game_name, abs_path, self.source_collection_name) in [(g['game'], g['file'], g['console']) for g in self.games_to_add]:
            self.games_to_add = [g for g in self.games_to_add if (g['game'], g['file'], g['console']) != (game_name, abs_path, self.source_collection_name)]
            label.setFont(QFont('Arial', italic=False))
            label.setStyleSheet('color: #f0f0f0')
            button.setText("+")
        else:
            game["console"] = self.source_collection_name
            game["file"] = abs_path
            if 'launch' not in game:
                game['launch'] = self.launch_command  # Define um valor padrão para 'launch'
            self.games_to_add.append(game)
            label.setFont(QFont('Arial', italic=False))
            label.setStyleSheet('color: #62c471') # light green
            button.setText("-")

    def add_game_to_list(self, game_name):
        item = QListWidgetItem()
        item_widget = QWidget()
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(game_name)
        button = QPushButton("+")
        button.setFixedSize(30, 30)
        button.clicked.connect(lambda: self.toggle_game_addition(item, game_name))

        item_layout.addWidget(label)
        item_layout.addWidget(button)
        item_widget.setLayout(item_layout)

        item.setSizeHint(item_widget.sizeHint())
        self.selected_games_list.addItem(item)
        self.selected_games_list.setItemWidget(item, item_widget)

    def remove_game_from_list(self, item, game_name):
        row = self.selected_games_list.row(item)
        self.selected_games_list.takeItem(row)
        self.games = [game for game in self.games if not game.startswith(f"# {game_name}")]

    def clear_game_list(self):
        self.games = []
        self.selected_games_list.clear()

    def update_source_games_list(self):
        self.source_games_list.clear()
        for game_name, file_path in sorted(self.source_games):
            item = QListWidgetItem()
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(10)  # Espaçamento entre o botão e o texto

            abs_path, file_extension, _ = self.extrair_info_arquivo(file_path, self.absolute_path)
            is_duplicate = any(
                existing_game[1] == abs_path and existing_game[2] == file_extension
                for existing_game in self.existing_games
            )

            # Primeiro adiciona o botão ou espaçador
            if not is_duplicate:
                button = QPushButton("+")
                button.setFixedSize(30, 30)
                button.clicked.connect(lambda _, item=item, game={"game": game_name, "file": file_path}:
                                    self.toggle_source_game_addition(item, game))
                item_layout.addWidget(button)
            else:
                # Adiciona um espaçador do tamanho do botão para manter o alinhamento
                spacer = QWidget()
                spacer.setFixedSize(20, 20)
                item_layout.addWidget(spacer)

            # Depois adiciona o label
            label = QLabel(game_name)
            if is_duplicate:
                label.setFont(QFont('Arial'))
                label.setStyleSheet('color: gray')
                label.setToolTip("Already exists in the custom collection")
            item_layout.addWidget(label)

            # Adiciona espaço flexível no final
            item_layout.addStretch()

            item_widget.setLayout(item_layout)
            item.setSizeHint(item_widget.sizeHint())
            self.source_games_list.addItem(item)
            self.source_games_list.setItemWidget(item, item_widget)

    def toggle_game_removal(self, item, game_name):
        row = self.existing_games_list.row(item)
        label = self.existing_games_list.itemWidget(item).findChild(QLabel)
        button = self.existing_games_list.itemWidget(item).findChild(QPushButton)

        if game_name in self.games_to_remove:
            self.games_to_remove.remove(game_name)
            font = label.font()
            font.setStrikeOut(False)
            label.setFont(font)
            label.setStyleSheet('color: #f0f0f0')
            button.setText("x")
        else:
            self.games_to_remove.add(game_name)
            font = label.font()
            font.setStrikeOut(True)
            label.setFont(font)
            label.setStyleSheet('color: gray')
            button.setText("+")

    def save_collection(self):
        if not self.collection_file:
            return

        # Criar cabeçalho atualizado
        collection_name = self.collection_name_input.text().strip()
        shortname = self.shortname_input.text().strip()

        updated_header = f"collection: {collection_name}\nshortname: {shortname}\n"
        updated_header += "command: none\nextensions: none\nlaunch: none\n\n"

        # Atualizar a lista de jogos existentes com base nos jogos a serem removidos
        self.existing_games = {
            (game_name, file_path, ext, game_launch)
            for game_name, file_path, ext, game_launch in self.existing_games
            if game_name not in self.games_to_remove
        }

        # Combinar jogos existentes com novos jogos a serem adicionados
        all_games = sorted(
            self.existing_games.union(
                {(game['game'], game['file'], game.get('ext', ''), game['launch']) for game in self.games_to_add}
            ),
            key=lambda x: x[0].lower()  # Ordenação case insensitive pelo nome do jogo
        )

        # Escrever no arquivo
        with open(self.collection_file, 'w', encoding='utf-8') as file:
            file.write(updated_header)
            for game_name, file_path, ext, game_launch in all_games:
                file.write(f"# {game_name}\nfile: {file_path}\nlaunch: {game_launch}\n\n")

        QMessageBox.information(self, "Saved", "Custom Collection saved successfully!")

        # Recarregar o arquivo salvo para atualizar a interface
        self.load_existing_games(self.collection_file)
        self.update_existing_games_list()
        self.games_to_add = []  # Limpar a lista de jogos a serem adicionados após salvar
        self.filter_games()
        self.update_source_games_list()  # Atualizar a lista de jogos da coleção fonte

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = PegasusCustomCollectionEditor()
    window.show()
    sys.exit(app.exec_())
