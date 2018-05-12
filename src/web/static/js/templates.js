

var schemaHomeTemplate = _.template(
    '<a href="<%= url %>" class="list-group-item list-group-item-action flex-column align-items-start">' +
        '<div class="d-flex w-100 justify-content-between">' +
            '<h5 class="mb-1"><%= name %></h5>' +
            '<small>updated <%= last_update %></small>' +
        '</div>' +
        '<p class="mb-1"><%= description %> by <%= organization %></p>' +
    '</a>');


var jsonObjectHomeTemplate = _.template(
    '<a href="<%= url %>" class="list-group-item list-group-item-action flex-column align-items-start">' +
        '<div class="d-flex w-100 justify-content-between">' +
            '<h5 class="mb-1"><%= name %></h5>' +
            '<small>updated <%= last_update %></small>' +
        '</div>' +
        '<p class="mb-1"><%= description %> by <%= organization %></p>' +
    '</a>');
