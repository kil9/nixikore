$('.message .close')
  .on('click', function() {
      $(this)
        .closest('.message')
        .transition('fade');
    });

$('.hairpin-test-script')
  .on('click', function() {
    $('.hairpin-test-content')
      .text($(this).data('content'));

    $.ajax({
      url: $(this).data('url'),
      type: 'GET',
      success: function(result) {
        $('#hairpin-test-result').html(result)
        $('.hairpin-test-modal')
          .modal({
            centered: false
          }).modal('show');
      }
    });

  });

$('.hairpin-delete')
  .on('click', function() {
    $('#hairpin-action').text(
      ($(this).data('category') ? '[' + $(this).data('category') + '] ' : '') +
      $(this).data('content'));
    $('.hairpin-confirm')
      .data('url', $(this).data('url'))
      .data('type', 'delete');
    $('.hairpin-confirm-modal')
      .modal({
        centered: false
      }).modal('show');
  });

$('.actions .hairpin-cancel')
  .on('click', function() {
    $('hairpin-confirm-modal').modal('hide');
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

$('#hairpin-do-tweet')
  .on('click', function() {
    $.ajax({
      url: '/tweet',
      type: 'POST',
      success: function(result) {
        location.reload();
      }
    });
  });
