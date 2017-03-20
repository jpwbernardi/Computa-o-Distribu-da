<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Title of the document</title>
</head>

<body>
  <form action="perguntas" method="post">
    <div class="row">
      <div class="input-field col s12">
        <textarea id="idPergunta" name = "perg" class="materialize-textarea" required="validate"></textarea>
        <label for="idPergunta">Digite aqui sua pergunta:</label>
      </div>
    </div>
    <div class="row">
      <center>
        <button class="btn waves-effect waves-light blue-grey darken-3 grey-text text-lighten-5" type="submit" name="action">Perguntar
          <i class="material-icons right">send</i>
        </button>
      </center>
    </div>
  </form>
</body>

</html>
