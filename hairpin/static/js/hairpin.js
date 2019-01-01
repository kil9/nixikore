$('.message .close')
  .on('click', function() {
      $(this)
        .closest('.message')
        .transition('fade');
    });

$('.hairpin-delete')
  .on('click', function() {
    $('#hairpin-action').text(
      '[' + $(this).data('category') + '] ' + $(this).data('content')
    );
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
