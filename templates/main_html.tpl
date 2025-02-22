<!DOCTYPE html>
<HTML lang = {{:lang}}>
<HEAD>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
  {{#:title}}<title>{{:title}}</title>{{/:title}}
  {{{ :header_script }}}

  <script type="text/x-mathjax-config">
    MathJax.Hub.Config({
      tex2jax: {inlineMath: [['$','$'], ['\\(','\\)']]}
    });
  </script>

  <script src='https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'></script>

  <style type="text/css">
  {{{ :themecss }}}
  </style>

  {{{ :highlightcss }}}

</HEAD>
  <BODY>
    <div class ="container">
      <div class = "row">
        <div class = "col-md-12 twelve columns">

          <div class="title">
            {{#:title}}<h1 class="title">{{:title}}</h1>{{/:title}}
            <h5>{{:wtime}}</h5>
          </div>

          {{{ :body }}}


          <HR/>
          <div class="footer"><p>
          Created on {{:wtime}}.
          <p></div>


        </div>
      </div>
    </div>
  </BODY>
</HTML>
