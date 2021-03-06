var coords = new Array();
var curcrd;
var canvas;
var context;

onload = function(){
  draw();
  $('#reset').click(function(){
    resetstatus();
  });
  $('#skip').on('click', function(){
    var $btn = $(this).button('loading');
    setTimeout(function() {
      nextajax(skip=1, imgdir=imgdir);
      $btn.button('reset')
    }, 1000);
  });
  $('#next').live('click', function(){
    var $btn = $(this).button('loading');
    setTimeout(function(){
      nextajax(skip=0, imgdir=imgdir);
      $btn.button('reset')
    }, 1000);
  });
  $('.bar').css({'width': count*100/imgnum + '%'});
  if (count >= imgnum) {
    $('.btn').addClass('disabled');
  }
};

function draw(){
  var image = new Image();
  image.src = imgsrc;
  image.onload = function(){
    var wid = image.naturalWidth;
    var hei = image.naturalHeight;
    $('.main-wrapper').css({'width': wid, 'minWidth': wid});
    var wrapper = $('#canvas-wrapper');
    $(wrapper).empty();
    var c = $('<canvas/>').attr('id', 'cnvs');
    $(wrapper).append(c);
    canvas = $('#cnvs').get(0);
    context = canvas.getContext('2d');
    $('#cnvs').css({'width': wid + 'px', 'height': hei + 'px'}).attr({'width': wid + 'px', 'height': hei + 'px'});
    context.drawImage(image, 0, 0);
    $(function(){
      $('#cnvs').Jcrop({
        onSelect: selected,
        onRelease: released,
      });
    });
  }
}

function selected(c){
  curcrd = [c.x, c.y, c.w, c.h];
}

function released(c){
  coords.push(curcrd);
  context.beginPath();
  context.lineWidth = 3;
  context.strokeStyle = 'rgba(238, 26, 26, 1)';
  context.strokeRect(curcrd[0], curcrd[1], curcrd[2], curcrd[3]);
}

function resetstatus(){
  coords = new Array();
  draw();
}

function nextajax(skip, imgdir){
  console.log('座標:'+coords);
  coords = JSON.stringify(coords);
  $.ajax({
    type: 'GET',
    dataType: "json",
    data: {'coords': coords, 'skip': skip, 'imgdir': imgdir},
    url: "/_next",
    success: function (data) {
      imgsrc = data.imgsrc;
      var numboxes = data.numboxes;
      var count = data.count;
      console.log(count)
      var finished = data.finished;
      $('.bar').css({'width': count*100/imgnum + '%'});
      console.log(count + '/' + imgnum);

      console.log(numboxes);
      if (finished){
        w = $('.head-wrapper').width()
        $('.main-wrapper').css({'width': w, 'minWidth': w});
        $('#canvas-wrapper').empty().append('<div class="messages"><div class="message">' + imgnum + ' Images were</div><div class="message">Successfuly Processed!</div></div>');
        $('.btn').addClass('disabled');
        $('.count').html(imgnum + ' files, ' + numboxes + ' boxes');
      } else{
        $('.count').html(count + '/' + imgnum + ' (' + numboxes + ')');
        resetstatus();
      }
    }
  });
}
