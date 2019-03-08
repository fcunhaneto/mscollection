#MSCollection

##O Que É

O aplicativo foi criado por uma necessidade minha de manter base dados dos meus DVD e Blu-ray, o que era para ser uma simples lista de títulos acabou se tornando maior do que o imaginado foram incluídos na base de dados diretores, categorias, elencos, listas de episódios por temporada e mais, isso tudo sendo muito fácil de incluir pois o MSCollection pode fazer scraping de paginas do site [IMDB](https://www.imdb.com/) para quem fala a língua inglesa ou dos sites [Adoro Cinema](http://www.adorocinema.com/) e [Minha Série](https://www.minhaserie.com.br/) para língua portuguesa.

Atualmente o MSCollection possui uma versão só para Linux na língua portuguesa, mas ele pode ser facilmente traduzido editando um único arquivo o _texts.py_.

Assim que dispuser de mais tempo pretendo fazer melhorias lançar uma versão em inglês e também uma versão compatível com o Windows.

Para instalar ele siga os passos abaixo, para usá-lo no diretório _doc_ existe o manual de instrução com versões em html e pdf.

##Instalação

Para instalar o MSCollection na maioria das distribuições Linux basta pelo terminal entrar no diretório no MSCollection e digitar:
```bash
$ ./install.sh
```

Após a instalação o aplicativo abre automaticamente, para abri-lo novamente  basta pelo terminal entrar no diretório no MSCollection e digitar:
```bash
$ ./mscollection.py
```

##Instalação Manual

Para uma instalação manual você deve conhecer o seguinte:

* Uso do virtualenv
* _SQLalchemy_

Antes de começar a instalação propriamente dita crie com o virtualenv uma instalação virtual do Python dentro do diretório onde se encontra o MSCollection ative ela e digite:
```bash
pip install -r requirements.txt
```

Para configurar o banco de dados você deve editar os método get_engine no arquivo _db/db_settings.py_ e no mesmo arquivo alterar a variável install = True para install = False.
Feito isso basta rodar o arquivo mscollection.py através do virtualenv que você criou.