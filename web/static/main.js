function stop_sim(cb) {
  $.ajax({
      url: '/api/stop',
      method: 'GET',
      success: cb
  });
}

function get_status(cb) {
    $.ajax({
        url: '/api/status',
        method: 'GET',
        success: cb
    });
}

function poll_status(cb, interval) {
  get_status(cb);
  setInterval(() => get_status(cb), interval);
}
