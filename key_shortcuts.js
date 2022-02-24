hotkeys('t, r', function (event, handler){
  switch (handler.key) {
    case 't': scroll(0,0); 
      break;
    case 'r': alert('you pressed r!');
      break;
    default: alert(event);
  }
});
