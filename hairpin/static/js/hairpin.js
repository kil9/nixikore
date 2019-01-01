$('.message .close')
  .on('click', function() {
      $(this)
        .closest('.message')
        .transition('fade');
    });

$('.hairpin-delete')
  .on('click', function() {
    $('#hairpin-action').text(
      ($(this).data('category') ? '[' + $(this).data('category') + '] ' : '') +
      $(this).data('content'));
    $('.hairpin-confirm')
      .data('url', $(this).data('url'))
      .data('type', 'delete');
    $('.ui.modal')
      .modal({
        centered: false
      }).modal('show');
  });

$('.actions .hairpin-cancel')
  .on('click', function() {
    $('.ui.modal').modal('hide');
  });

$('.actions .hairpin-confirm')
  .on('click', function() {
    $.ajax({
      url: $(this).data('url'),
      type: $(this).data('type'),
      success: function(result) {
        location.reload();
      }
    });
  });

$('.hairpin-generate-tweet')
  .on('click', function() {
    $.ajax({
      url: '/pending_tweets/' + $(this).data('tweet-count'),
      type: 'POST',
      success: function(result) {
        location.reload();
      }
    });
  });

$('#hairpin-remove-all-tweets')
  .on('click', function() {
    $.ajax({
      url: '/pending_tweets/all',
      type: 'DELETE',
      success: function(result) {
        location.reload();
      }
    });
  });
