<!DOCTYPE html>
<html>
  <head>
    <!--Import Google Icon Font-->
    <link href="http://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <!--Import materialize.css-->
    <link type="text/css" rel="stylesheet" href="static/css/materialize.min.css"  media="screen,projection"/>
    <link type="text/css" rel="stylesheet" href="static/css/chat.css"/>
    <!--Let browser know website is optimized for mobile-->
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Banco de dados distribuído</title>
  </head>

  <body>
    <div class="row">
      <form class="col s12 m6" action="send" method="post">
	<div class="row">
	  <div class="input-field col s12">
	    <select name="select" id="select" required>
	      <option value="" disabled selected>Escolha opção</option>
	      <option value="c">Criar/editar variável</option>
	      <option value="r">Remover variável</option>
	      <option value="a">Soma variável com variável</option>
	      <option value="ai">Soma variável com inteiro</option>
	    </select>
	    <label>Ação</label>
	  </div>
	</div>
        <div class="row">
	  <div class="input-field col s12 m6">
            <input name="par1" placeholder="Parâmetro 1" id="par1" type="text" class="validate" required>
            <label for="par1">Parâmetro 1</label>
          </div>
	  <div class="input-field col s12 m6">
            <input name="par2" placeholder="Parâmetro 2" id="par2" type="text">
            <label for="par2">Parâmetro 2</label>
          </div>
        </div>
        <div class="row">
          <div class="col offset-s5">
            <button class="btn waves-effect waves-light" type="submit" name="action" style="margin-top: 2em">Submit</button>
          </div>
        </div>
      </form>
      <div id="chat" class="col s12 m6">
        <div id="inchat">
          <h5> Computação Distribuída - Trabalho 3 </h5>
          <ul>
           %for k in dados.keys():
          <li><b>{{k}}</b>: {{dados[k]}}</li>
          %end
          </ul>
        </div>
      </div>
    </div>
    <script type="text/javascript" src="https://code.jquery.com/jquery-2.1.1.min.js"></script>
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
    <script type="text/javascript" src="static/js/materialize.min.js"></script>
    <script type="text/javascript">
      /*var auto_refresh = setInterval(function (){ $("#chat").load("/chat #inchat"); }, 1000);*/
    </script>
    <script>
      $(document).ready(function() {
      $('select').material_select();
      });
    </script>
  </body>
</html>

