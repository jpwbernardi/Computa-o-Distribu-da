<!DOCTYPE html>
<html>
  <head>
    <!--Import Google Icon Font-->
    <link href="http://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <!--Import materialize.css-->
    <link type="text/css" rel="stylesheet" href="static/materialize.min.css"  media="screen,projection"/>
    <!--Let browser know website is optimized for mobile-->
    <meta name="viewport" content="width=device-width,
                                   initial-scale=1.0"/>
    <title>Client</title>
  </head>

  <body>
    <div class="row">
    <form class="col s12" action="" method="post">
      <div class="row">
        <div class="input-field col s12 m9 l5">
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
        <div class="input-field col s12 m9 l5">
          <i class="material-icons prefix">mode_edit</i>
          <textarea name="msg" id="msg" class="materialize-textarea"></textarea>
          <label for="msg">Message</label>
        </div>
      </div>
      <div class="row">
        <div class="col offset-m4 offset-s5 offset-l2">
          <button class="btn waves-effect waves-light" type="submit"
                  name="action" style="margin-top: 2em">Submit</button>
        </div>
      </div>
    </form>
    <script type="text/javascript" src="https://code.jquery.com/jquery-2.1.1.min.js"></script>
    <script type="text/javascript"
            src="static/materialize.min.js"></script>
    <script>
      $(document).ready(function() {
      %if error == True:
      Materialize.toast('Some field is blank', 4000);
      %end
      });
    </script>
  </body>
</html>

