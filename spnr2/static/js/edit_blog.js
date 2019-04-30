function derivedSlugFromDate() {
    var date_input = $('#page-edit-form input[name=date]');
    var slug_input = $('#page-edit-form input[name=slug]');
    var titl_input = $('#page-edit-form input[name=title]');

    if (titl_input.length == 0) {
        // only run if title field is missing
        date_input.on('change', function() {
            slug_input.val(
                'year-in-photos-'
                + date_input.val().split('-').splice(0, 2).join('-')
            );
        });
    }
}

$(function() {
    if (!$('body').hasClass('page-is-live')) {
        derivedSlugFromDate()
    }
});
