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
    <title>Chat</title>
  </head>

  <body>
    <div class="row">
      <form class="col s12 m6" action="send" method="post">
        <div class="row">
          <div class="input-field col s12">
            <i class="material-icons prefix">account_circle</i>
            %if name != None:
            <input value="{{name}}"name="name" id="name" type="text" class="validate">
            %else:
            <input name="name" id="name" type="text" class="validate">
            %end
            <label for="name">Name</label>
          </div>
        </div>
        <div class="row">
          <div class="input-field col s12">
            <i class="material-icons prefix">mode_edit</i>
            <textarea name="msg" id="msg" class="materialize-textarea"></textarea>
            <label for="msg">Message</label>
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
          <h5> Computação Distribuída - Trabalho 1 </h5>
          <ul>
            %for (n, m) in reversed(msg):
          <li><b>{{n}}</b>: {{m}}</li>
          %end
          </ul>
        </div>
      </div>
    </div>
    <script type="text/javascript" src="https://code.jquery.com/jquery-2.1.1.min.js"></script>
    <script type="text/javascript" src="static/js/materialize.min.js"></script>
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
    <script type="text/javascript">
      var auto_refresh = setInterval(function (){ $("#chat").load("/chat #inchat"); }, 1000);
    </script>
  </body>
</html>

